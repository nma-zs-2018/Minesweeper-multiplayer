import random
import string
from datetime import datetime

from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect

# Create your views here.
from minesweeper import MinesweeperRoom

from threading import Timer


class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


def clean_minesweeper_rooms():
    now = (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()
    remove = [k for k in MinesweeperRoom.all if MinesweeperRoom.all[k].ended > 10 and now - MinesweeperRoom.all[k].ended > 60*60*24]
    for k in remove: del MinesweeperRoom.all[k]


timer = None


def random_string_up_letters(n):
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(n))


def random_string_letters_digits(n):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(n))


def game(request, game_name):
    global timer

    if timer is None:
        timer = RepeatTimer(60*60*24, clean_minesweeper_rooms)
        timer.start()

    if game_name not in MinesweeperRoom.all:
        return HttpResponseBadRequest()

    room = MinesweeperRoom.all[game_name]

    if room.started is None:
        return HttpResponseBadRequest()

    username = None
    if request.session.session_key in room.names:
        username = room.names[request.session.session_key]

    return render(request, "game.html", {'game_name': game_name, 'username': username})


def game_create(request):
    if not request.POST:
        return HttpResponseBadRequest()

    width = int(request.POST['width'])
    height = int(request.POST['height'])
    name = request.POST['name']
    mines = int(request.POST['mines'])

    if name in MinesweeperRoom.all:
        name += random_string_letters_digits(10)

    MinesweeperRoom.all[name] = MinesweeperRoom(height, width, mines)

    return redirect('/lobby/' + name)


def lobby(request, game_name):
    if game_name not in MinesweeperRoom.all:
        return HttpResponseBadRequest()

    game = MinesweeperRoom.all[game_name].game
    if game.won or game.fail is not None:
        return redirect('/game/' + game_name)

    return render(request, "lobby.html", {'game_name': game_name,
                                          'your_name': 'player ' + random_string_up_letters(2)})


def index(request):
    if not request.session.session_key:
        request.session.save()

    game_name = random_string_letters_digits(10)
    return render(request, "index.html", {'game_name': game_name})


def clone(request, game_name):
    if game_name not in MinesweeperRoom.all:
        return HttpResponseBadRequest()

    old = MinesweeperRoom.all[game_name]

    name = random_string_letters_digits(10)
    height = old.game.n
    width = old.game.m
    mines = old.game.minesCount
    MinesweeperRoom.all[name] = MinesweeperRoom(height, width, mines)

    return redirect('/lobby/' + name)


def logout(request):
    request.session.flush()
    return redirect('/')
