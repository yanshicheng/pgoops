from rest_framework.decorators import action

from common.viewsets import StandardModelViewSet
from common.response import api_ok_response, api_error_response
from ..models import Rule
from ..serializers import RuleSerializer


class RoleRuleViewSet(StandardModelViewSet):
    queryset = Rule.objects.filter().order_by("id")
    serializer_class = RuleSerializer
    ordering_fields = ("id",)
    filter_fields = ("id", "name", "pid")
    search_fields = ("name", "pid")

    @action(
        methods=["GET"],
        detail=False,
    )
    def tree(self, request, *args, **kwargs):
        t_l = []
        parent_queryset = self.get_queryset().filter(pid=None)
        for inc in parent_queryset:
            parent_ser = self.get_serializer(inc, many=False)
            children_inc = Rule.objects.filter(pid=inc)
            parent_dic = parent_ser.data
            parent_dic["children"] = RuleSerializer(children_inc, many=True).data
            t_l.append(parent_dic)
        return api_ok_response(t_l)

    @action(
        methods=["GET"],
        detail=False,
    )
    def parent(self, request, *args, **kwargs):
        all_queryset = self.get_queryset().filter(pid=None)
        serializer = self.get_serializer(all_queryset, many=True)
        return api_ok_response(serializer.data)
