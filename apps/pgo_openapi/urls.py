from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.pgo_openapi.views.test import WebHookPromeOpenApiView

router = DefaultRouter()
# router.register(r"v1/iac/repository", RepositoryModelViewSet)


urlpatterns = [
    path("v1/openapi/test/", WebHookPromeOpenApiView.as_view()),
]
urlpatterns += router.urls
