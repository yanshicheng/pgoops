from django.utils import timezone
from rest_framework.decorators import action

from common.request_info import get_user
from common.response import api_ok_response, api_error_response
from common.viewsets import StandardModelViewSet
from ..filters import TaskPeriodicFilter

from ..models import TaskPeriodic
from ..serializers import TaskPeriodicSerializer


class TaskPeriodicModelViewSet(StandardModelViewSet):
    queryset = TaskPeriodic.objects.filter().order_by("-id")
    serializer_class = TaskPeriodicSerializer
    ordering_fields = ("id",)
    filter_class = TaskPeriodicFilter
    search_fields = ("name")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            instance = serializer.save(created_by=get_user(request), updated_by=get_user(request))
            return api_ok_response(self.serializer_class(instance).data)
        except Exception as e:
            return api_error_response(str(e))

    @action(methods=["post"], detail=True)
    def pause(self, request, *args, **kwargs):
        instance: TaskPeriodic = self.get_object()
        instance.enabled = False
        instance.updated_by = get_user(request)
        instance.save()
        return api_ok_response(self.serializer_class(instance).data)

    @action(methods=["post"], detail=True)
    def enable(self, request, *args, **kwargs):
        instance: TaskPeriodic = self.get_object()
        instance.enabled = True
        instance.updated_by = get_user(request)
        instance.save()
        return api_ok_response(self.serializer_class(instance).data)


