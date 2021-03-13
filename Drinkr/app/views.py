"""
Definition of views.
"""

from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpRequest
from .forms import GameHostDetailsForm, GameJoinDetailsForm
from TCP.client import Client, current_client
from TCP.Message import Message
from TCP.constants import server_command_types

def home(request):
    assert isinstance(request, HttpRequest)

    if request.method == 'POST':
        if 'host_form' in request.POST:
            request.session['is_host'] = True
            request.session['host_data'] = request.POST

        elif 'join_form' in request.POST:
            request.session['is_host'] = False
            request.session['join_data'] = request.POST

        return redirect('lobby')

    else:
        host_form = GameHostDetailsForm()
        join_form = GameJoinDetailsForm()

    return render(
        request,
        'app/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
            'host_form': host_form,
            'join_form': join_form,
        }
    )


def lobby(request):
    assert isinstance(request, HttpRequest)
    
    if request.method == 'POST':
        # To do:  validate post

        # To do:  connect to tcp server
        try:
            if 'enter' in request.POST:
                current_client.connect("127.0.0.1", 5555)
                current_client.send(Message(server_command_types.Welcome, current_client.client_data.to_bytes()))

                current_client.send(Message(server_command_types.Log_Users))
                return redirect('game')
        except:
            print("Could not connect to server")

    else:
        is_host = bool(request.session['is_host'])
        if is_host:
            form = GameHostDetailsForm(request.session['host_data'])
        else:
            form = GameJoinDetailsForm(request.session['join_data'])
    
        username = form.data['displayName']
        current_client.set_data(is_host, username)


    return render(
        request,
        'app/lobby.html',
        {
            'title':'Lobby Page',
            'username': username,
            'year':datetime.now().year,
        }
    )


def game(request):
    assert isinstance(request, HttpRequest)


    return render(
        request,
        'app/game.html',
        {
            'title':'Game Page',
            'year':datetime.now().year,
        }
    )