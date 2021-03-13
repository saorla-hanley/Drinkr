"""
Definition of views.
"""

from datetime import datetime
from django.shortcuts import render
from django.http import HttpRequest, HttpResponseRedirect
from .forms import GameHostDetailsForm, GameJoinDetailsForm

def home(request):
    assert isinstance(request, HttpRequest)

    if request.method == 'POST':
        if 'host_form' in request.POST:
            request.session['is_host'] = True
            request.session['host_data'] = request.POST

        elif 'join_form' in request.POST:
            request.session['is_host'] = False
            request.session['join_data'] = request.POST

        # Need to validate
        return HttpResponseRedirect('lobby')

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

    username = "unknown"
    if bool(request.session['is_host']) == True:
        username = GameHostDetailsForm(request.session['host_data']).data['displayName']
    else:
        username = GameJoinDetailsForm(request.session['join_data']).data['displayName']

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