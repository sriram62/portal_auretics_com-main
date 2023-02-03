from django.urls import path
from .views import total_pv_bv
from .structure import create_structure

urlpatterns = [
    path('calculate/', total_pv_bv, name='total_pv_bv'),
    path('create_structure/', create_structure, name='create_structure'),
]