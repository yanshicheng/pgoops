import os.path

import simplejson

# import yaml
from ruamel import yaml
from rest_framework.decorators import action
from django.conf import settings

from common.monitor_api import PrometheusApi
from common.response import api_ok_response, api_error_response
from common.viewsets import StandardModelViewSet

from ..models import Node
from ..prome_config_node import PromeConfig
from ..serializers import NodeModelMixinSerializer
from ...pgo_data_map.models import Classify
from ...pgo_data_map.serializers import ClassifySerializer
from common.file import File
from common.paramiko_handle import ParamikoHandle


class NodeModelViewSet(StandardModelViewSet):
    queryset = Node.objects.filter().order_by("id")
    serializer_class = NodeModelMixinSerializer
    ordering_fields = ("-id",)

    filter_fields = ("master",)
    search_fields = ("host__data",)

    @action(methods=["get"], detail=False, url_path="data-map-classify")
    def data_map_classify(self, request, *args, **kwargs):
        data_map_classify = [
            6,
        ]
        classify_query = Classify.objects.filter(id__in=data_map_classify)
        return api_ok_response(data=ClassifySerializer(classify_query, many=True).data)

    @action(methods=["post"], detail=True, url_path="download-config")
    def download_config(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            config = PromeConfig.parse(instance)
            return api_ok_response(
                yaml.dump(
                    config,
                    Dumper=yaml.RoundTripDumper,
                    default_flow_style=False,
                    allow_unicode=False,
                )
            )
        except Exception as e:
            return api_error_response(str(e))

    @action(methods=["post"], detail=False, url_path="distribute-config")
    def distribute_config(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().filter(master=False))
        for query in queryset:
            unique_name = query.host.get_unique_data()
            config_path = os.path.join(settings.BASE_DIR, "tmp", "prometheus.yml")
            if File.if_file_exists(config_path):
                File.rm_file(config_path)
            with open(config_path, "w", encoding="utf-8") as f:
                config = PromeConfig.parse(query)
                yaml.dump(
                    config,
                    stream=f,
                    Dumper=yaml.RoundTripDumper,
                    default_flow_style=False,
                    allow_unicode=False,
                )
                f.flush()
                f.close()
            client = ParamikoHandle(unique_name)
            desc_path = query.get_config_path()
            client.file_upload(config_path, desc_path)
            try:
                PrometheusApi.reload(
                    scheme=query.get_scheme_display(), addr=unique_name, port=query.port
                )
            except Exception as e:
                return api_error_response(f"prometheus 重启失败:{str(e)}")
        return api_ok_response("ok")
