from common.viewsets import StandardModelViewSet
from ..models import Department
from ..serializers import DepartmentSerializer


class DepartmentViewSet(StandardModelViewSet):
    queryset = Department.objects.filter().order_by("-id")
    serializer_class = DepartmentSerializer
    ordering_fields = ("id",)
    filter_fields = ("id",)
    search_fields = ("name",)
