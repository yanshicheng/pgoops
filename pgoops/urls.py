"""pgoops URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.views import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    re_path(r"media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    re_path(
        r"^static/(?P<path>.*)$",
        static.serve,
        {"document_root": settings.STATIC_ROOT},
        name="static",
    ),
    path("admin/", admin.site.urls),
    path("api/v1/user/login/", obtain_jwt_token),
    path("api/", include("apps.pgo_user.urls")),
    path("api/", include("apps.pgo_permission.urls")),
    path("api/", include("apps.pgo_data_map.urls")),
    path("api/", include("apps.pgo_service_tree.urls")),
    path("api/", include("apps.pgo_iac.urls")),
    path("api/", include("apps.pgo_message_center.urls")),
    path("api/", include("apps.pgo_openapi.urls")),
    path("api/", include("apps.pgo_settings.urls")),
    path("api/", include("apps.pgo_monitor.urls")),
]
