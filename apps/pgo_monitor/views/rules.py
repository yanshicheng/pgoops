from django.conf import settings
from rest_framework.decorators import action
from ruamel import yaml

from common.file import File
from common.response import api_ok_response, api_error_response
from common.viewsets import StandardModelViewSet
from common.monitor_api import PrometheusApi
from ..models import Rules
from ..serializers import RulesModelMixinSerializer


class RulesModelViewSet(StandardModelViewSet):
    queryset = Rules.objects.filter().order_by("id")
    serializer_class = RulesModelMixinSerializer
    ordering_fields = ("-id",)
    filter_fields = (
        "name",
        "group",
    )
    search_fields = ("name", "promeql")

    @action(methods=["post"], detail=False, url_path="execute")
    def execute(self, request, *args, **kwargs):
        query = request.data.get("query")
        result, ok = PrometheusApi.execute(query=query)
        if not ok:
            return api_error_response(f'Prometheus连接查询失败，错误信息:{result}')
        return api_ok_response(data=result)
