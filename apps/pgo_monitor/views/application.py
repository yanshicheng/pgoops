import simplejson
import yaml
from rest_framework.decorators import action

from common.config_dispose import ConfigDispose
from common.grafana_url import application_explain_url, explain_url
from common.monitor_targets import MonitorTargets
from common.viewsets import StandardModelViewSet

from ..models import Application
from ..prome_config_node import PromeConfig
from ..serializers import ApplicationModelMixinSerializer
from apps.pgo_data_map.models import Classify
from apps.pgo_data_map.serializers import ClassifySerializer
from common.response import api_ok_response, api_error_response


class ApplicationModelViewSet(StandardModelViewSet):
    data_map_classify = [
        6,
    ]
    queryset = Application.objects.filter().order_by("id")
    serializer_class = ApplicationModelMixinSerializer
    ordering_fields = ("-id",)
    filter_fields = ("asset", "group")
    search_fields = ("asset__data",)

    @action(methods=["get"], detail=False, url_path="data-map-classify")
    def data_map_classify(self, request, *args, **kwargs):
        data_map_classify = [
            6,
        ]
        classify_query = Classify.objects.filter(id__in=data_map_classify)
        return api_ok_response(data=ClassifySerializer(classify_query, many=True).data)

    @action(methods=["get"], detail=True, url_path="monitor")
    def monitor(self, request, *args, **kwargs):
        instance: Application = self.get_object()
        s_d = instance.asset.get_unique_data()
        grafana_url, ok = application_explain_url(
            instance.group.grafana_path, f"{s_d}:{instance.port}"
        )
        return api_ok_response(
            {"url": grafana_url, "title": f"[{s_d}]  {instance.group.name}信息面板"}
        )

    @action(methods=["post"], detail=False, url_path="consul")
    def consul(self, request, *args, **kwargs):
        try:
            MonitorTargets.application_targets()
            return api_ok_response("下发成功")
        except Exception as e:
            return api_error_response(str(e))

    @action(methods=["get"], detail=False, url_path="service-monitor")
    def service_monitor(self, request, *args, **kwargs):
        grafana_url, ok = explain_url("server")
        return api_ok_response(
            {
                "url": grafana_url,
            }
        )
