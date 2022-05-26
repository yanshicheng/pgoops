import os
from collections import OrderedDict

import simplejson

# import yaml
from django.conf import settings
from rest_framework.decorators import action
from ruamel import yaml

from common.file import File
from common.monitor_api import PrometheusApi
from common.paramiko_handle import ParamikoHandle
from common.response import api_error_response, api_ok_response
from common.viewsets import StandardModelViewSet

from ..models import Group, Node
from ..serializers import GroupModelMixinSerializer


class GroupModelViewSet(StandardModelViewSet):
    queryset = Group.objects.filter().order_by("id")
    serializer_class = GroupModelMixinSerializer
    ordering_fields = ("-id",)
    filter_fields = ("name",)
    search_fields = ("name",)

    @action(methods=["get"], detail=True, url_path="group-rules")
    def group_rules(self, request, *args, **kwargs):
        data = OrderedDict([("groups", [])])
        instance: Group = self.get_object()
        group_rules = instance.get_group_rules()
        if not group_rules:
            return api_error_response(f"{instance.name} 分组为找到规则信息")
        data["groups"].append(group_rules)
        return api_ok_response(
            data=str(
                yaml.dump(simplejson.loads(simplejson.dumps(data)), allow_unicode=True)
            )
        )

    @action(methods=["get"], detail=False, url_path="group-rules")
    def group_all_rules(self, request, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset().order_by("id"))
        data = OrderedDict([("groups", [])])
        for query in queryset:
            group_rules = query.get_group_rules()
            if group_rules:
                data["groups"].append(group_rules)
                # rules_str +=  yaml.dump(simplejson.loads(simplejson.dumps(rules)), allow_unicode=True)
        if not data:
            return api_error_response(f"所有 分组为找到规则信息")
        return api_ok_response(
            data=yaml.dump(simplejson.loads(simplejson.dumps(data)), allow_unicode=True)
        )

    @action(methods=["post"], detail=False, url_path="distribute-config")
    def distribute_config(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().order_by("id"))
        data = OrderedDict([("groups", [])])
        for query in queryset:
            group_rules = query.get_group_rules()
            if group_rules:
                data["groups"].append(group_rules)
                # rules_str +=  yaml.dump(simplejson.loads(simplejson.dumps(rules)), allow_unicode=True)
        if not data:
            return api_error_response(f"所有 分组为找到规则信息")
        config_path = os.path.join(settings.BASE_DIR, "tmp", "rules.yml")
        if File.if_file_exists(config_path):
            File.rm_file(config_path)
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(
                simplejson.loads(simplejson.dumps(data)), stream=f, allow_unicode=True
            )
            f.flush()
            f.close()
        node_queryset = Node.objects.filter(master=False, status=True)
        for node in node_queryset:
            unique_name = node.host.get_unique_data()
            client = ParamikoHandle(unique_name)
            desc_path = node.get_rules_path()
            client.file_upload(config_path, desc_path)
            try:
                PrometheusApi.reload(
                    scheme=node.get_scheme_display(), addr=unique_name, port=node.port
                )
            except Exception as e:
                return api_error_response(f"prometheus 重启失败:{str(e)}")
        return api_ok_response("ok")
