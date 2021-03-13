"""
Definition of forms.
"""

from django import forms
from django.utils.translation import ugettext_lazy as _

class GameHostDetailsForm(forms.Form):
    displayName = forms.CharField(max_length=254, 
                                  label=_("Display Name"),
                                  widget=forms.TextInput({
                                      'class': 'form-control',
                                      'placeholder': 'Display name'}))

    gamePassword = forms.CharField(label=_("Password"),
                                   widget=forms.TextInput({
                                       'class': 'form-control',
                                       'placeholder':'Password'}))

class GameJoinDetailsForm(forms.Form):
    gameCode = forms.CharField(max_length=8,
                               label=_("Room Code"),
                               widget=forms.TextInput({
                                      'class': 'form-control',
                                      'placeholder': 'ABC123YZ'}))

    displayName = forms.CharField(max_length=254,
                                  label=_("Display Name"),
                                  widget=forms.TextInput({
                                    'class': 'form-control',
                                    'placeholder': 'Display name'}))

    gamePassword = forms.CharField(label=_("Password"),
                                   widget=forms.TextInput({
                                       'class': 'form-control',
                                       'placeholder':'Password'}))
