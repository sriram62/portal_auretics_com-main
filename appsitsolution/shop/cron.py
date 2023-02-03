from mlm_admin.models import Inventry
from django.core.exceptions import ObjectDoesNotExist,MultipleObjectsReturned
from django.shortcuts import HttpResponse
from datetime import date,timedelta

def cron_run():
    today = date.today()
    yesterday = today - timedelta(days = 1)
    inventries = Inventry.objects.filter(created_on = yesterday)
    for inventry in inventries:
        try:
            query = Inventry.objects.get(product = inventry.product,batch = inventry.batch,material_center = inventry.material_center,
            created_on = today)
        except ObjectDoesNotExist:
            query = Inventry(product = inventry.product,batch = inventry.batch,material_center = inventry.material_center,purchase_price = inventry.purchase_price,
                     opening_quantity = inventry.current_quantity,current_quantity = inventry.current_quantity,
                     )
            query.save()


def cron_runtest():
    today = date.today()
    yesterday = today - timedelta(days = 1)
    inventries = Inventry.objects.filter(created_on = yesterday)
    for inventry in inventries:
        try:
            query_set = Inventry.objects.get(product = inventry.product,batch = inventry.batch,material_center = inventry.material_center,created_on = today)
        except MultipleObjectsReturned:
            pass
        except ObjectDoesNotExist:
            pass

def cron_manu(request):
    cron_runtest()
    return HttpResponse('<h1>evvery thing is fine</h1>')


def cron_sort_sold_products(request):
    today = date.today()
    yesterday = today - timedelta(days = 1)
# cron_run()
