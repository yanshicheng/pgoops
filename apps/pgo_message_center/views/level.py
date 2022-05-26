from common.viewsets import StandardModelViewSet

from ..models import Level
from ..serializers import LevelSerializers


class LevelModelViewSet(StandardModelViewSet):
    queryset = Level.objects.filter().order_by("-id")
    serializer_class = LevelSerializers
    ordering_fields = ("-id",)
    filter_fields = ("name", "cname")
    search_fields = ("name", "cname")
