from django.conf.urls import url

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from web.consumers import GameConsumer, LobbyConsumer

application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter([
            url("^game/websocket/(.*)/$", GameConsumer),
            url("^lobby/websocket/(.*)/$", LobbyConsumer),
        ])
    )
})
