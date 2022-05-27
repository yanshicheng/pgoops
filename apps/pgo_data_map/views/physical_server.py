from rest_framework.decorators import action

from common.config_dispose import ConfigDispose
from common.grafana_url import explain_url
from common.viewsets import StandardModelViewSet
from common.response import api_ok_response, api_error_response
from common.verify_handle import ipv4_addr_check
from ..models import Asset
from ..serializers import AssetSerializer

from ..verify.operate import OperateInstance
from ..verify.record_log import record


class PhysicalServerViewSet(StandardModelViewSet):
    classify_id = 6
    queryset = Asset.objects.filter(classify_id=classify_id).order_by("id")
    serializer_class = AssetSerializer
    ordering_fields = ("id",)
    filter_fields = ("id", "ban_bind")
    search_fields = ("data",)

    def list(self, request, *args, **kwargs):

        classify_obj = OperateInstance.get_classify(self.classify_id)

        if not classify_obj:
            return api_error_response("找不到指定的模型表")

        classify_field_obj = OperateInstance.get_classify_field(self.classify_id)
        if not classify_field_obj:
            return api_error_response("找不到分类表的字段表")

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(
                {
                    "data": serializer.data,
                    "fields": classify_field_obj.fields,
                    "rules": classify_field_obj.rules,
                    "patent_classify_name": classify_field_obj.classify.pid.name,
                    "classify_name": classify_field_obj.classify.name,
                    "classify_id": classify_field_obj.classify.id,
                }
            )

        serializer = self.get_serializer(queryset, many=True)
        data = {
            "data": serializer.data,
            "fields": classify_field_obj.fields,
            "rules": classify_field_obj.rules,
            "patent_classify_name": classify_field_obj.classify.pid.name,
            "classify_name": classify_field_obj.classify.name,
            "classify_id": classify_field_obj.classify.id,
        }
        return api_ok_response(data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        try:
            record("delete_data", instance, None, request)
        except Exception as e:
            return api_error_response(f"日志记录出错: {str(e)}")

        instance.delete()
        return api_ok_response("删除成功")

    @action(methods=["get"], detail=True, url_path="monitor")
    def monitor(self, request, *args, **kwargs):
        """
        var-nodename
        var-instance
        """
        instance: Asset = self.get_object()
        s_d = instance.get_unique_data()
        grafana_url, ok = explain_url("physical_server")
        if not ok:
            return api_error_response({"url": grafana_url, "title": f"[{s_d}]  主机信息面板", 'status': ok})
        if ipv4_addr_check(s_d):
            s_d = f"{s_d}:9100"
            url = f"{grafana_url}&var-instance={s_d}"
        else:
            url = f"{grafana_url}&var-nodename={s_d}"

        return api_ok_response({"url": url, "title": f"[{s_d}]  主机信息面板", 'status': ok})
