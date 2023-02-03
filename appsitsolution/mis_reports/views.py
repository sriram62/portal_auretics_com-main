from django.db.models.aggregates import Count
from django.shortcuts import render

from activitylog.models import UserLoginActivity
from django.db.models import Sum
from slick_reporting.views import SlickReportView
from slick_reporting.fields import SlickReportField

from django.utils.translation import gettext as _

from shop.models import *

# Create your views here.
 
class TotalProductSales(SlickReportView):
     
    report_model = LineItem
    date_field = 'date_added'
    group_by = 'product'
    columns = ['product_name',
                SlickReportField.create(Sum, 'quantity') ,
                SlickReportField.create(Sum, 'price', name='sum__price') ]

    chart_settings = [{
        'type': 'column',
        'data_source': ['sum__price'],
        'plot_total': False,
        'title_source': 'title',
        'title': _('Detailed Columns'),

    }, ]

class PaymentDetails(SlickReportView):
     
    report_model = Payment
    date_field = 'created_on'
    group_by = 'order'
    columns = ['order_id1',
                
                SlickReportField.create(Sum, 'amount', name='sum__amount')
    ]

    chart_settings = [{
        'type': 'column',
        'data_source': ['sum__amount'],
        'plot_total': False,
        'title_source': 'title',
        'title': _('Detailed Columns'),

    }, ]



class OrderReports(SlickReportView):
    report_model = Order
    date_field = 'date'
    
    group_by = 'shipping_address'
    columns = ['shipping_address',
                
                
                SlickReportField.create(Sum, 'grand_total', name='sum__grand_total'),
                SlickReportField.create(Sum, 'pv', name='sum__pv'),
                SlickReportField.create(Sum, 'bv', name='sum__bv'),
 
    ]


    chart_settings = [{
        'type': 'column',
        'data_source': ['sum__grand_total'],
        'plot_total': False,
        'title_source': 'title',
        'title': _('Order Detailed Coulmns'),

    }, ]



class ProductReports(SlickReportView):
    report_model = Product
    date_field = 'launch_date' 
    group_by = 'category'
    columns = ['cat_name',
                 
                SlickReportField.create(Sum, 'quantity', name='sum__quantity'),


                SlickReportField.create(Sum, 'purchase_price', name='sum__purchase_price'),
               
                 
    ]


    chart_settings = [{
        'type': 'column',
        'data_source': ['sum__purchase_price'],
        'plot_total': False,
        'title_source': 'title',
        'title': _('Product Detailed Coulmns'),

    }, ]


class LogIns(SlickReportView):
    

    report_model = UserLoginActivity
     
    date_field = 'login_datetime'
    group_by = 'login_username'
    columns = ['login_username']
    time_series_pattern = 'monthly'
    
    time_series_columns = [
        SlickReportField.create(method=Count, field='login_datetime', name='Weekly count of logins')
        # we can have multiple ReportField in the time series columns too !
    ]


 
