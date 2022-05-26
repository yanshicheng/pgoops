from common.viewsets import StandardModelViewSet

from ..models import TaskEvent
from ..serializers import TaskEventSerializer


class TaskEventModelViewSet(StandardModelViewSet):
    queryset = TaskEvent.objects.filter().order_by("-id")
    serializer_class = TaskEventSerializer
    ordering_fields = ("id",)
    filter_fields = ("host", "task_record")
    search_fields = ("host",)
