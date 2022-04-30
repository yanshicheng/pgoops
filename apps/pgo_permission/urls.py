from django.urls import path, include
from rest_framework import routers

from apps.pgo_permission.views.menu import MenuViewSet
from apps.pgo_permission.views.role import RoleViewSet
from apps.pgo_permission.views.rule import RoleRuleViewSet

router = routers.DefaultRouter()
router.register(r"v1/prem/role", RoleViewSet)
router.register(r"v1/prem/rule", RoleRuleViewSet)
router.register(r"v1/prem/menu", MenuViewSet)
urlpatterns = []

urlpatterns += router.urls
