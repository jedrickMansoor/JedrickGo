from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from apps.chat.routing import urlpatterns as chat_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": URLRouter(chat_urlpatterns),
})