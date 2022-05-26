from django.utils import timezone

from common.response import api_ok_response, api_error_response
from common.request_info import get_user
from rest_framework.viewsets import ModelViewSet


class StandardModelViewSet(ModelViewSet):
    """
    视图集合基类
    """

    def create(self, request, *args, **kwargs):
        # 校验字段
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer, request)
        return api_ok_response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer, request)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return api_ok_response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if hasattr(self, "is_system"):
            if self.is_system:
                return api_error_response("Built-in data cannot be deleted")
        instance.delete()
        return api_ok_response()

    def list(self, request, *args, **kwargs):
        try:
            ordering = request.query_params.get("ordering", "")
            ordering = ordering.replace("+", "").strip()
            if ordering:
                if self.serializer_class is None:
                    queryset = self.filter_queryset(
                        self.get_serializer_class().Meta.model.objects.order_by(
                            ordering
                        )
                    )
                else:
                    queryset = self.filter_queryset(
                        self.serializer_class.Meta.model.objects.order_by(ordering)
                    )
            else:
                queryset = self.filter_queryset(self.get_queryset())
            page = request.query_params.get("page", "")
            size = request.query_params.get("size", "")
            if page or size:
                page_queryset = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = self.get_serializer(page_queryset, many=True)
                    return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(queryset, many=True)
            return api_ok_response(data=serializer.data)
        except Exception as e:
            return api_error_response(message=str(e))

    def retrieve(self, request, *args, **kwargs):
        response = super(StandardModelViewSet, self).retrieve(request, *args, **kwargs)
        return api_ok_response(response.data)

    def perform_update(self, serializer, request=None):
        serializer.save(request=request)

    def perform_create(self, serializer, request=None):
        serializer.save(request=request)


class StandardOpenModelViewSet(ModelViewSet):
    """
    视图集合基类
    """

    authentication_classes = []
    permission_classes = []

    def create(self, request, *args, **kwargs):
        response = super(StandardOpenModelViewSet, self).create(
            request, *args, **kwargs
        )
        return api_ok_response(response.data)

    def update(self, request, *args, **kwargs):
        response = super(StandardOpenModelViewSet, self).update(
            request, *args, **kwargs
        )
        return api_ok_response(response.data)

    def destroy(self, request, *args, **kwargs):
        response = super(StandardOpenModelViewSet, self).destroy(
            request, *args, **kwargs
        )
        return api_ok_response(response.data)

    def list(self, request, *args, **kwargs):
        try:
            ordering = request.query_params.get("ordering", "")
            ordering = ordering.replace("+", "").strip()
            if ordering:
                if self.serializer_class is None:
                    queryset = self.filter_queryset(
                        self.get_serializer_class().Meta.model.objects.order_by(
                            ordering
                        )
                    )
                else:
                    queryset = self.filter_queryset(
                        self.serializer_class.Meta.model.objects.order_by(ordering)
                    )
            else:
                queryset = self.filter_queryset(self.get_queryset())
            page = request.query_params.get("page", "")
            size = request.query_params.get("size", "")
            if page or size:
                page_queryset = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = self.get_serializer(page_queryset, many=True)
                    return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(queryset, many=True)
            return api_ok_response(data=serializer.data)
        except Exception as e:
            return api_error_response(message=str(e))

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_ok_response(serializer.data)
