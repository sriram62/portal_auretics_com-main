from django.urls import path
from .views import total_pv_bv

urlpatterns = [
    path('calculate/', total_pv_bv, name='total_pv_bv_v2'),
]