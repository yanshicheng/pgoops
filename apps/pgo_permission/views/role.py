from rest_framework.decorators import action

from common.viewsets import StandardModelViewSet
from common.response import api_ok_response, api_error_response
from ..models import Role
from ..serializers import RoleSerializer


class RoleViewSet(StandardModelViewSet):
    queryset = Role.objects.filter().order_by("-id")
    serializer_class = RoleSerializer
    ordering_fields = ("id",)
    filter_fields = ("id",)
    search_fields = ("name",)
