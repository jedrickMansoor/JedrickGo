from django.urls import path

from .consumers import NotificationConsumer


urlpatterns = [

    path(
        "ws/",
        NotificationConsumer.as_asgi(),
    ),

]