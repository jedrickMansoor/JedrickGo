from django.urls import path
from .consumers import ChatConsumer

urlpatterns = [
    path("ws/chat/<int:conversation_id>/", ChatConsumer.as_asgi()),
]