from django.forms import ModelForm
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms


class orderForm(ModelForm):

    class Meta:
        model = Order
        fields = '__all__'
        exclude = ['tags']


class customerForm(ModelForm):

    class Meta:
        model = Customer
        fields = '__all__'
        exclude = ['user']


class createUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
