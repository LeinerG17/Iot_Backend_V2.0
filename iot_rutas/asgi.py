"""
ASGI config for iot_rutas project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iot_rutas.settings')

from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()  # ← debe inicializarse ANTES de importar consumers

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from api.routing import websocket_urlpatterns  # ← api.routing, no api

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})