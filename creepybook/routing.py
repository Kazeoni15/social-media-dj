from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from .consumers import *

app = ProtocolTypeRouter({
    "websocket": URLRouter([
        path("ws/chat/<str:room_id>/", ChatConsumer.as_asgi()),
    ]),
})