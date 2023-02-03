# from django.conf.urls import url
from django.contrib import admin
from payments.views import payment, response


app_name = "wallet"
urlpatterns = [

	path('response/',response, name="response")

]
