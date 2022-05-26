from django.urls import path
from rest_framework import routers

from apps.pgo_data_map.views.asset import AssetViewSet
from apps.pgo_data_map.views.classify import ClassifyViewSet
from apps.pgo_data_map.views.field import FieldsViewSet
from apps.pgo_data_map.views.record import ChangeRecordViewSet
from apps.pgo_data_map.views.physical_server import PhysicalServerViewSet

router = routers.DefaultRouter()
router.register(r"v1/data-map/classify", ClassifyViewSet)
router.register(r"v1/data-map/field", FieldsViewSet)
router.register(r"v1/data-map/asset", AssetViewSet)
router.register(r"v1/data-map/record", ChangeRecordViewSet)
router.register(r"v1/data-map/physical-server", PhysicalServerViewSet)

urlpatterns = []

urlpatterns += router.urls
