from common.response import api_ok_response
from common.viewsets import StandardModelViewSet

from ..models import Provider
from ..serializers import ProviderSerializers


class ProviderModelViewSet(StandardModelViewSet):
    queryset = Provider.objects.filter().order_by('-id')
    serializer_class = ProviderSerializers
    ordering_fields = ("-id",)
    filter_fields = ("name",)
    search_fields = ("host",)
