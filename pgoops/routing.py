from django.urls import re_path

from apps.pgo_iac.consumers import AsyncTaskEventConsumer

websocket_urlpatterns = [
    re_path(r'ws/iac/task/(?P<pk>\d+)/$', AsyncTaskEventConsumer.as_asgi()),
]