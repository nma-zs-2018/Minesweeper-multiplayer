import random
import json
from datetime import datetime


class MinesweeperBoardException(Exception):
    pass


class Minesweeper:
    def __init__(self, n, m, mines):
        self.n = n
        self.m = m
        self.minesCount = mines
        self.fail = False
        if mines * 1.2 >= n * m:
            raise MinesweeperBoardException()

        self.mines = []
        self.board = []
        cells = []

        for i in range(0, n):
            self.mines.append([])
            self.board.append([])
            for j in range(0, m):
                self.mines[i].append(False)
                self.board[i].append(100)
                cells.append((i, j))

        random.shuffle(cells)

        for x in cells[0:mines]:
            self.mines[x[0]][x[1]] = True

        self.open(cells[mines][0], cells[mines][1])

    def open(self, i, j):
        if self.fail:
            return

        if self.mines[i][j]:
            self.fail = True

            for ii in range(0, self.n):
                for jj in range(0, self.m):
                    if self.mines[ii][jj]:
                        self.board[ii][jj] = 99

            self.board[i][j] = 98
        else:
            self.board[i][j] = 0

            def check(x, y):
                if x >= 0 and y >= 0 and x < self.n and y < self.m and self.mines[x][y]:
                    self.board[i][j] += 1

            check(i, j + 1)
            check(i, j - 1)
            check(i + 1, j + 1)
            check(i - 1, j + 1)
            check(i + 1, j - 1)
            check(i - 1, j - 1)
            check(i + 1, j)
            check(i - 1, j)

            if self.board[i][j] == 0:
                def run(x, y):
                    if x >= 0 and y >= 0 and x < self.n and y < self.m and self.board[x][y] == 100:
                        self.open(x, y)

                run(i, j + 1)
                run(i, j - 1)
                run(i + 1, j + 1)
                run(i - 1, j + 1)
                run(i + 1, j - 1)
                run(i - 1, j - 1)
                run(i + 1, j)
                run(i - 1, j)

    def dictionary(self):
        return {'n': self.n, 'm': self.m, 'fail': 1 if self.fail else 0, 'mines': self.minesCount,
                'board': self.board}


class MinesweeperRoom:
    all = {}

    def __init__(self, n, m, mines):
        self.turn = 0
        self.players_list = None
        self.connections = set()
        self.names = {}
        self.game = Minesweeper(n, m, mines)
        self.started = None
        self.ended = 0

    def open(self, i, j):
        if self.game.fail:
            return
        self.game.open(i, j)
        if self.game.fail:
            self.ended = (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()

    def broadcast(self, message):
        for x in self.connections:
            x.send({
                "type": "websocket.send",
                "text": message
            })

    def broadcast_board(self):
        self.broadcast(self.json())

    def json(self):
        return json.dumps({'game': self.game.dictionary(),
                           'turn': self.names[self.players_list[self.turn]],
                           'started': self.started,
                           'ended': self.ended})

    def add_player(self, player):
        print(self.json())
        self.connections.add(player)
        player.send({
            "type": "websocket.send",
            "text": self.json()
        })

    def broadcast_players(self):
        self.broadcast(json.dumps(list(self.names.values())))
