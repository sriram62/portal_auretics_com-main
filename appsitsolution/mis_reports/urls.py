
from django.urls import path
# from django.conf.urls import url
from . import views
 

# from .order_id import update_order_id
# app_name = "shop"

urlpatterns = [


    path('path-to-report', views.TotalProductSales.as_view(), name='path-to-report'),
    
    path('reports-of-payments', views.PaymentDetails.as_view(), name='report-of-payments'),
    path('reports-of-orders', views.OrderReports.as_view(), name='report-of-orders'),
    path('reports-of-products', views.ProductReports.as_view(), name='report-of-products'),
    path('perday-users-logins', views.LogIns.as_view(), name='perday-users-logins'),




]