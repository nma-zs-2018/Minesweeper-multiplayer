import json
import random
from datetime import datetime


class MinesweeperBoardException(Exception):
    pass


class Minesweeper:
    def __init__(self, n, m, mines):
        self.n = n
        self.m = m
        self.minesCount = mines
        self.fail = None
        self.won = False
        self.unknown = n * m
        if mines * 1.2 >= n * m or mines < 3:
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
        if self.won:
            this = Minesweeper(n, m, mines)

    def show_mines(self):
        for ii in range(0, self.n):
            for jj in range(0, self.m):
                if self.mines[ii][jj]:
                    self.board[ii][jj] = 99

    def open(self, i, j):
        if self.fail is not None or self.won or self.board[i][j] != 100:
            return

        self.unknown -= 1

        if self.mines[i][j]:
            self.fail = True
            self.show_mines()
            self.board[i][j] = 98
        else:
            self.board[i][j] = 0

            def check(x, y):
                if 0 <= x < self.n and 0 <= y < self.m and self.mines[x][y]:
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
                    if 0 <= x < self.n and 0 <= y < self.m and self.board[x][y] == 100:
                        self.open(x, y)

                run(i, j + 1)
                run(i, j - 1)
                run(i + 1, j + 1)
                run(i - 1, j + 1)
                run(i + 1, j - 1)
                run(i - 1, j - 1)
                run(i + 1, j)
                run(i - 1, j)

            if self.unknown == 0:
                self.won = True

    def open_mine(self, i, j):
        if self.fail is not None or self.won or self.board[i][j] != 100:
            return

        self.unknown -= 1

        if self.mines[i][j]:
            self.board[i][j] = 99
            if self.unknown == 0:
                self.won = True
        else:
            self.fail = True
            self.show_mines()

    def dictionary(self):
        return {'n': self.n, 'm': self.m,
                'fail': str(self.fail), 'won': 1 if self.won else 0,
                'mines': self.minesCount,
                'board': self.board, 'unknown': self.unknown}


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

    def open(self, i, j, mine):
        if self.game.fail or self.game.won:
            return
        name = self.names[self.players_list[self.turn]]
        if mine:
            self.game.open_mine(i,j)
        else:
            self.game.open(i, j)
        if self.game.fail:
            self.game.fail = name
        if self.game.fail or self.game.won:
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
        self.connections.add(player)
        player.send({
            "type": "websocket.send",
            "text": self.json()
        })

    def broadcast_players(self):
        self.broadcast(json.dumps(list(self.names.values())))
