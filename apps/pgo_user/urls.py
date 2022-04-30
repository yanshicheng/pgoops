from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views.department import DepartmentViewSet
from .views.user_profile import UserInfoApiView, UserLogoutApiView, UserProfileViewSet

router = DefaultRouter()
router.register(r"v1/user/user-profile", UserProfileViewSet)
router.register(r"v1/user/department", DepartmentViewSet)

urlpatterns = [
    path("v1/user/info/", UserInfoApiView.as_view()),
    path("v1/user/logout/", UserLogoutApiView.as_view()),
]

urlpatterns += router.urls
