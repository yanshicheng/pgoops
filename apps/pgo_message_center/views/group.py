from common.response import api_ok_response
from common.viewsets import StandardModelViewSet

from ..models import Group
from ..serializers import GroupSerializers


class GroupModelViewSet(StandardModelViewSet):
    queryset = Group.objects.filter().order_by("-id")
    serializer_class = GroupSerializers
    ordering_fields = ("-id",)
    filter_fields = ("name",)
    search_fields = ("host",)
