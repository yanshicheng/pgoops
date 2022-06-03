from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.pgo_openapi.views.test import WebHookPromeOpenApiView
from apps.pgo_openapi.views.cmdb import CmdbOpenApiView

router = DefaultRouter()
# router.register(r"v1/iac/repository", RepositoryModelViewSet)


urlpatterns = [
    path("v1/openapi/test/", WebHookPromeOpenApiView.as_view()),
    path("v1/openapi/cmdb/", CmdbOpenApiView.as_view()),
]
urlpatterns += router.urls
