import random
import string

from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect

# Create your views here.
from web.minesweeper import MinesweeperRoom


def game(request, id):
    if not id in MinesweeperRoom.all:
        return HttpResponseBadRequest()

    room = MinesweeperRoom.all[id]

    if room.started is None:
        return HttpResponseBadRequest()

    username = None
    if request.session.session_key in room.names:
        username = room.names[request.session.session_key]


    return render(request, "game.html", {'game_name': id, 'username': username})


def game_create(request):
    if not request.POST:
        return HttpResponseBadRequest()

    width = int(request.POST['width'])
    height = int(request.POST['height'])
    name = request.POST['name']
    mines = int(request.POST['mines'])

    MinesweeperRoom.all[name] = MinesweeperRoom(height, width, mines)

    return redirect('../lobby/' + name)


def lobby(request, id):
    if not id in MinesweeperRoom.all:
        return HttpResponseBadRequest()

    return render(request, "lobby.html", {'game_name': id,
                                          'your_name': 'player ' + ''.join(random.choice(string.ascii_uppercase) for _ in range(2))})


def index(request):
    game_name = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
    return render(request, "index.html", {'game_name': game_name})
