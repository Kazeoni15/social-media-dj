import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from .consumers import ChatConsumer
from .routing import *


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SNS.settings')





# Get the default Django ASGI application
django_application = get_asgi_application()

# Use the URLRouter to route WebSocket requests to your consumer
application = ProtocolTypeRouter({
    "http": django_application,  # For HTTP requests
    "websocket": app,  # For WebSocket requests
})


