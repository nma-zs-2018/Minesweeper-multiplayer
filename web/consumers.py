from datetime import datetime

from channels.consumer import SyncConsumer
import json

from minesweeper import MinesweeperRoom

WEBSOCKET_DISCONNECT = {"type": "websocket.disconnect", }
WEBSOCKET_ACCEPT = {"type": "websocket.accept", }


class LobbyConsumer(SyncConsumer):
    def websocket_connect(self, event):
        self.user = self.scope["session"].session_key
        name = self.scope['path'][17:-1]
        if name not in MinesweeperRoom.all:
            self.send(WEBSOCKET_DISCONNECT)
            self.game = None
            return
        self.game = MinesweeperRoom.all[name]
        if self.game.started is not None:
            self.send(WEBSOCKET_DISCONNECT)
            self.game = None
            return
        self.game.names[self.user] = 'NotKnown'
        self.game.connections.add(self)
        self.send(WEBSOCKET_ACCEPT)

    def websocket_receive(self, event):
        if self.game is None or self.game.started is not None:
            return

        if event['text'] == 'START':
            self.game.started = (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()
            self.game.players_list = list(self.game.names.keys())
            self.game.broadcast('REDIRECT')
        else:
            self.game.names[self.user] = event['text']
            self.game.broadcast_players()

    def websocket_disconnect(self, event):
        if self.game is None:
            return
        self.game.connections.remove(self)


class GameConsumer(SyncConsumer):
    def websocket_connect(self, event):
        self.user = self.scope["session"].session_key
        name = self.scope['path'][16:-1]
        if name not in MinesweeperRoom.all:
            self.send(WEBSOCKET_DISCONNECT)
            self.game = None
            return
        self.game = MinesweeperRoom.all[name]
        if self.game.started is None:
            self.send(WEBSOCKET_DISCONNECT)
            self.game = None
            return
        self.send(WEBSOCKET_ACCEPT)
        self.game.add_player(self)

    def websocket_receive(self, event):
        if self.game is None:
            return
        if self.game.players_list[self.game.turn] == self.user:
            point = json.loads(event['text'])
            self.game.open(point['x'], point['y'])
            self.game.turn = (self.game.turn + 1) % len(self.game.players_list)
            self.game.broadcast_board()

    def websocket_disconnect(self, event):
        if self.game is None:
            return
        self.game.connections.remove(self)
