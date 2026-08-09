import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

django_asgi_app = get_asgi_application()

from apps.chat.routing import urlpatterns as chat_urlpatterns
from apps.notification.routing import urlpatterns as notification_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": URLRouter(
        notification_urlpatterns +
        chat_urlpatterns
    ),
})