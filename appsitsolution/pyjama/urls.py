from django.urls import path
from . import j

urlpatterns = [
    path('pyjama', j.pyjama, name="pyjama"),
]