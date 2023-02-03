from django.urls import path

from . import views, ivr

urlpatterns = [
    path('crm-list', views.crm_list, name="crm-list"),
    path('crm-list/test', views.crm_list_test, name="crm-list_test"),
    path('ivr/register', ivr.ivr_register, name="ivr_register"),
    path('ivr/register/', ivr.ivr_register, name="ivr_register"),
    path('ivr/register/check_user_success', ivr.check_user_success, name="check_user_success"),
    path('ivr/register/check_user_success/', ivr.check_user_success, name="check_user_success"),
    path('ivr/register/check_user_exist', ivr.check_user_exist, name="check_user_exist"),
    path('ivr/register/check_user_exist/', ivr.check_user_exist, name="check_user_exist"),
    path('ivr/register/check_upline_exist', ivr.check_upline_exist, name="check_upline_exist"),
    path('ivr/register/check_upline_exist/', ivr.check_upline_exist, name="check_upline_exist"),
]

