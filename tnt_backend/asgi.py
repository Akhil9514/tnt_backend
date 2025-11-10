import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
# import your_websocket_routing  # If using WebSockets; otherwise, skip

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tnt_backend.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    # "websocket": AuthMiddlewareStack(URLRouter(your_websocket_routing.websocket_urlpatterns)),  # If needed
})