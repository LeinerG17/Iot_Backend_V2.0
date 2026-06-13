from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/ubicaciones/', consumers.UbicacionConsumer.as_asgi()),
]