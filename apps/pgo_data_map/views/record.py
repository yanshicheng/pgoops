from rest_framework.decorators import action

from common.viewsets import StandardModelViewSet

from ..models import ChangeRecord
from ..serializers import ChangeRecordSerializer


class ChangeRecordViewSet(StandardModelViewSet):
    queryset = ChangeRecord.objects.filter().order_by("-id")
    serializer_class = ChangeRecordSerializer
    ordering_fields = (
        "id",
        "title",
    )
    filter_fields = ("id", "title", "asset_id")
    search_fields = ("title", "title")
