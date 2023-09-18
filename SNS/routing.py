# # your_project/routing.py
# from channels.routing import ProtocolTypeRouter, URLRouter
# from django.urls import path
# from SNS.creepybook import consumers
#
# application = ProtocolTypeRouter({
#     "websocket": URLRouter([
#         path("ws/chat/<str:room_name>/", consumers.ChatConsumer.as_asgi()),
#     ]),
# })
