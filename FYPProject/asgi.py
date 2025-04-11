"""
ASGI config for FYPProject project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from accounts.consumers import ChatConsumer  # Import your WebSocket consumer

# Set the default settings module for the 'asgi' application.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FYPProject.settings')

# Define the ASGI application protocol router.
application = ProtocolTypeRouter({
    # The HTTP protocol is handled by the default ASGI application.
    "http": get_asgi_application(),  # Default HTTP handling
    
    # The WebSocket protocol is handled by a custom consumer defined in accounts/consumers.py.
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/chat/", ChatConsumer.as_asgi()),  # WebSocket route for chat (adjust path as needed)
        ])
    ),
})
