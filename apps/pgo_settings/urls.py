from django.urls import path
from rest_framework.routers import DefaultRouter

from .views.config import ConfigApiView

router = DefaultRouter()
# router.register(r"v1/iac/repository", RepositoryModelViewSet)


urlpatterns = [
    path("v1/settings/config/", ConfigApiView.as_view()),
]
urlpatterns += router.urls
