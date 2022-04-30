from common.viewsets import StandardModelViewSet

from ..models import TaskStats
from ..serializers import TaskStatsSerializer


class TaskStatsModelViewSet(StandardModelViewSet):
    queryset = TaskStats.objects.filter()
    serializer_class = TaskStatsSerializer
    ordering_fields = ("-id",)
    filter_fields = ("host", "task_record",)
    search_fields = ("host", "task_record",)

