"""
ASGI config for pgoops project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from channels.routing import URLRouter, ProtocolTypeRouter
from django.core.asgi import get_asgi_application
from django.utils.module_loading import import_string

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pgoops.settings')

# application = get_asgi_application()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(
        import_string('pgoops.routing.websocket_urlpatterns')
    ),
})
