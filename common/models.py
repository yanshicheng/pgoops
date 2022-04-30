from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from django.contrib.contenttypes.models import ContentType
from django.db import models, router

from django.contrib.auth import get_user_model
from django.db.models.deletion import Collector
from rest_framework.mixins import CreateModelMixin

from common.response import api_ok_response
from django.core.exceptions import PermissionDenied


class DateTimeModelMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        abstract = True
        ordering = ["-update_at"]  # 默认排序


class StandardModelMixin(DateTimeModelMixin):
    def delete(self, using=None, keep_parents=False):
        if hasattr(self, 'is_system'):
            if self.is_system:
                raise Exception('Built-in deletion is prohibited')
        using = using or router.db_for_write(self.__class__, instance=self)
        assert self.pk is not None, (
                "%s object can't be deleted because its %s attribute is set to None." %
                (self._meta.object_name, self._meta.pk.attname)
        )

        collector = Collector(using=using)
        collector.collect([self], keep_parents=keep_parents)
        return collector.delete()

    class Meta:
        abstract = True


class BulkCreateModelMixin(CreateModelMixin):
    """
    Either create a single or many model instances in bulk by using the
    Serializers ``many=True`` ability from Django REST >= 2.2.5.
    .. note::
        This mixin uses the same method to create model instances
        as ``CreateModelMixin`` because both non-bulk and bulk
        requests will use ``POST`` request method.
    """

    # https://github.com/miki725/django-rest-framework-bulk/blob/master/rest_framework_bulk/drf3/mixins.py

    def create(self, request, *args, **kwargs):
        bulk = isinstance(request.data, list)

        if not bulk:
            return super(BulkCreateModelMixin, self).create(request, *args, **kwargs)

        else:
            serializer = self.get_serializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_bulk_create(serializer)
            return api_ok_response(serializer.data)

    def perform_bulk_create(self, serializer):
        return self.perform_create(serializer)


class BroadcastModelMixin:
    __group_name_prefix__ = None
    __group_name_field__ = 'pk'
    __handler_name__ = 'on_changed'

    @classmethod
    @database_sync_to_async
    def channel_layer_group_name(cls, pk):
        group_name_prefix = cls.__group_name_prefix__
        if not group_name_prefix:
            content_type = ContentType.objects.get_for_model(cls())
            group_name_prefix = f'{content_type.app_label}'
        if pk:
            return f'{group_name_prefix}_{pk}'
        return group_name_prefix

    @async_to_sync
    async def handle_changed(self):
        channel_layer = get_channel_layer()
        pk = getattr(self, self.__group_name_field__)
        group_name = await self.channel_layer_group_name(pk)
        await channel_layer.group_send(group_name, {"type": self.__handler_name__, "data": pk})


def model_changed(sender, **kwargs):
    if issubclass(sender, BroadcastModelMixin):
        kwargs['instance'].handle_changed()
