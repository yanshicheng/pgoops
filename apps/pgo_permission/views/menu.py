import json

from rest_framework.decorators import action

from common.viewsets import StandardModelViewSet
from common.response import api_ok_response, api_error_response
from ..models import Menu
from ..serializers import MenuSerializer


class MenuViewSet(StandardModelViewSet):
    queryset = Menu.objects.filter().order_by("-id")
    serializer_class = MenuSerializer
    ordering_fields = ("id", "order")
    filter_fields = ("id", "pid")
    search_fields = ("name", "pid")

    @action(
        methods=["GET"],
        detail=False,
    )
    def parent(self, request, *args, **kwargs):
        parent_queryset = self.get_queryset().filter(pid=None).order_by("order")
        serializer = self.get_serializer(parent_queryset, many=True)

        return api_ok_response(serializer.data)

    @action(
        methods=["GET"],
        detail=False,
    )
    def tree(self, request, *args, **kwargs):
        t_l = []
        parent_queryset = self.get_queryset().filter(pid=None)
        for p_queryset in parent_queryset:
            menu = self.__format_res(
                self.get_serializer(p_queryset, many=False).data, many=False
            )
            children_queryset = self.get_queryset().filter(pid=p_queryset)
            menu["children"] = self.__format_res(
                self.get_serializer(children_queryset, many=True).data, many=True
            )
            t_l.append(menu)

        return api_ok_response(self.__sorted(t_l))

    def __format_res(self, data, many):
        if not many:
            if data["name"]:
                res_dic = {
                    "order": data["order"],
                    "path": data["path"],
                    "component": data["component"],
                    "name": data["name"],
                    "redirect": data["redirect"],
                    "hidden": data["hidden"],
                    "alwaysShow": data["always_show"],
                    "meta": {
                        "title": data["title"],
                        "roles": data["roles"],
                        "icon": data["icon"],
                        "noCache": data["no_cache"],
                        "breadcrumb": data["breadcrumb"],
                        "affix": data["affix"],
                    },
                }
            else:
                res_dic = {
                    "order": data["order"],
                    "path": data["path"],
                    "component": data["component"],
                }
            return res_dic
        else:
            res_list = []
            for item in json.loads(json.dumps(data)):
                res_dic = {
                    "order": item["order"],
                    "path": item["path"],
                    "component": item["component"],
                    "name": item["name"],
                    "redirect": item["redirect"],
                    "hidden": item["hidden"],
                    "meta": {
                        "title": item["title"],
                        "roles": item["roles"],
                        "icon": item["icon"],
                        "noCache": item["no_cache"],
                        "breadcrumb": item["breadcrumb"],
                        "affix": item["affix"],
                        "activeMenu": item["active_menu"],
                    },
                }
                if item["active_menu"]:
                    res_dic["meta"] = item["active_menu"]
                res_list.append(res_dic)
            return res_list

    def __sorted(self, data):

        new_data = sorted(data, key=lambda x: x["order"])

        for item_dic in new_data:
            item_dic["children"] = (
                []
                if not item_dic.get("children")
                else sorted(item_dic["children"], key=lambda x: x["order"])
            )
        return new_data
