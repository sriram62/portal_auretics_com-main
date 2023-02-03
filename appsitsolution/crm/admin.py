from django.contrib import admin
from django.apps import apps

# Register your models here.
from .models import *

admin.site.register(ivr_user_created)
admin.site.register(ivr_logs)
admin.site.register(ivr_check_logs)