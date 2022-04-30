from django.urls import path
from rest_framework.routers import DefaultRouter
from .views.group import GroupModelViewSet
from .views.provider import ProviderModelViewSet
from .views.level import LevelModelViewSet
from .views.history import HistoryModelViewSet
from .views.webhook import WebHookPromeOpenApiView

router = DefaultRouter()
router.register(r"v1/message-center/group", GroupModelViewSet)
router.register(r"v1/message-center/provider", ProviderModelViewSet)
router.register(r"v1/message-center/level", LevelModelViewSet)
router.register(r"v1/message-center/history", HistoryModelViewSet)

urlpatterns = [
    path(r"v1/message-center/webhook/prome/send/", WebHookPromeOpenApiView.as_view()),
]
urlpatterns += router.urls
