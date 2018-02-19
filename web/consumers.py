from datetime import datetime

from channels.consumer import SyncConsumer
import json

from web.minesweeper import Minesweeper, MinesweeperRoom


class LobbyConsumer(SyncConsumer):
    def websocket_connect(self, event):
        self.user = self.scope["session"].session_key
        name = self.scope['path'][17:-1]
        if not name in MinesweeperRoom.all:
            self.send({
                "type": "websocket.disconnect",
            })
            self.game = None
            return
        self.game = MinesweeperRoom.all[name]
        if not self.game.started is None:
            self.send({
                "type": "websocket.disconnect",
            })
            self.game = None
            return
        self.game.names[self.user] = 'NotKnown'
        self.game.connections.add(self)
        self.send({
            "type": "websocket.accept",
        })

    def websocket_receive(self, event):
        if self.game is None or not self.game.started is None:
            return

        if event['text'] == 'START':
            self.game.started = (datetime.utcnow() - datetime(1970,1,1)).total_seconds()
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
        if not name in MinesweeperRoom.all:
            self.send({
                "type": "websocket.disconnect",
            })
            self.game = None
            return
        self.game = MinesweeperRoom.all[name]
        if self.game.started is None:
            self.send({
                "type": "websocket.disconnect",
            })
            self.game = None
            return
        self.send({
            "type": "websocket.accept",
        })
        self.game.add_player(self)

    def websocket_receive(self, event):
        if self.game is None:
            return
        if self.game.players_list[self.game.turn] == self.user:
            koord = json.loads(event['text'])
            self.game.open(koord['x'], koord['y'])
            self.game.broadcast_board()
            self.game.turn = (self.game.turn + 1) % len(self.game.players_list)

    def websocket_disconnect(self, event):
        if self.game is None:
            return
        self.game.connections.remove(self)


class GameExistsConsumer(SyncConsumer):
    def websocket_connect(self, event):
        self.send({
            "type": "websocket.accept",
        })

    def websocket_receive(self, event):
        global games
        self.send({
            "type": "websocket.send",
            "text": str(1 if event['text'] in games else 0)
        })

    def websocket_disconnect(self, event):
        pass
