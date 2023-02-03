from django.contrib import admin
from .models import *
# Register your models here.


class TemplateAdmin(admin.ModelAdmin):
    list_display = ['template_name']

admin.site.register(NoticeTemplate, TemplateAdmin)