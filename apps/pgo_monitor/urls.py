from django.urls import path
from rest_framework.routers import DefaultRouter
from .views.rules import RulesModelViewSet
from .views.node import NodeModelViewSet
from .views.group import GroupModelViewSet
from .views.application import ApplicationModelViewSet
from apps.pgo_openapi.views.test import WebHookPromeOpenApiView

router = DefaultRouter()
router.register(r"v1/monitor/rules", RulesModelViewSet)
router.register(r"v1/monitor/application", ApplicationModelViewSet)
router.register(r"v1/monitor/group", GroupModelViewSet)
router.register(r"v1/monitor/node", NodeModelViewSet)


urlpatterns = [
    # path("v1/monitor/rules-group/", WebHookPromeOpenApiView.as_view()),
]
urlpatterns += router.urls
