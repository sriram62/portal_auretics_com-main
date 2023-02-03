from django.urls import path
from .views import *

urlpatterns = [
    path('audit_order_pv_bv/', audit_order_pv_bv, name='audit_order_pv_bv'),
]