from django.contrib import admin

# Register your models here.
from .models import *


admin.site.register(Gateway)
admin.site.register(PaymentMode)
