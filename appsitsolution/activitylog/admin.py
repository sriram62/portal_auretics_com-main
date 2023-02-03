from django.contrib import admin

from .models import UserLoginActivity
# Register your models here.
class UserLoginActivityAdmin(admin.ModelAdmin):
    list_display = ['id', 'login_username', 'login_IP', 'login_datetime','status','user_agent_info']
    search_fields=('id', 'login_username', 'login_IP', 'login_datetime', 'status','user_agent_info')


admin.site.register(UserLoginActivity,UserLoginActivityAdmin)


 