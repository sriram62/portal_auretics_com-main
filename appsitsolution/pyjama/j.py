from django.shortcuts import render
from django.utils import timezone
from datetime import datetime, date, timedelta
from django.shortcuts import render, HttpResponse, get_object_or_404
from shop.models import Product, Batch, Material_center
from distributor.models import Distributor_Inventry
from mlm_admin.models import Inventry
from django.contrib.auth.models import User
from django.db.models import Sum

# Create your views here.
'''
We are incorporating all common codes here.
'''

def pyjama(request):
    return HttpResponse('<h1>pyjama is live</h1>')

# Create your views here.
def previous_month(month,year):
    prev_year = year
    prev_month = month - 1
    if prev_month <= 0:
        prev_month = 12
        prev_year = year - 1
    return prev_month,prev_year


def month_name(month_number):
    month_number = int(month_number)
    return calendar.month_name[month_number]


def time_def():
    time_now = datetime.now()
    today = time_now.date()
    month = today.month
    year = today.year
    day_before_today = today - timedelta(days=1)
    last_month = int(month) - 1
    last_year = year
    if last_month <= 0:
        last_month = 12
        last_year = year - 1
    last_month_date = str(last_year) + "-" + str(last_month) + "-" + "01"
    last_month_date = datetime.strptime(last_month_date, "%Y-%m-%d").date()

    return_dict = {'time_now':time_now,
                   'month':month,
                   'year':year,
                   'last_month':last_month,
                   'last_year':last_year,
                   'last_month_date':last_month_date,
                   'today':today,
                   'day_before_today':day_before_today,
                   }
    return return_dict

def time_now_fn():
    return time_def()['time_now']

def month_fn():
    return time_def()['month']

def year_fn():
    return time_def()['year']

def last_month_fn():
    return time_def()['last_month']

def last_year_fn():
    return time_def()['last_year']

def last_month_date_fn():
    return time_def()['last_month_date']

def today_fn():
    return time_def()['today']

def day_before_today_fn():
    return time_def()['day_before_today']


time_now = time_now_fn()
month = month_fn()
year = year_fn()
last_month = last_month_fn()
last_year = last_year_fn()
last_month_date = last_month_date_fn()
today = today_fn()
day_before_today = day_before_today_fn()


class Objectify(object):
    pass

def qs_sum(qs,column):
    column = str(column) + '__sum'

    response = qs.aggregate(Sum('column'))[column]
    if response:
        response = float(response)
    else:
        response = 0.0
    return response



def usable_batches(product,material=False,distributor_checkout=False,user_id=False):
    """
        We will take product and find whether it is expiring product or not. (i.e. perishable or not)
        if expiring:
            We have to take the batch that has not expired
            We will further find whether the current material center has that batch in stock or not
            We will take the batch which is expiring first.
        else:
            We will filter the batches that has quantity in the current material.
            We will take the first batch.
        """
    batchs = Batch.objects.filter(product=product, delete=False)

    if product.expiration_dated_product == 'YES':
        batchs = batchs.filter(date_of_expiry__gte=today_fn()).order_by('date_of_expiry')
    else:
        batchs = batchs.order_by('pk')

    material = Material_center.objects.filter(frontend=True).first()
    if distributor_checkout:
        material = Material_center.objects.filter(id=distributor_checkout)
    else:
        if user_id:
            try:
                material = User.objects.get(user__pk=user_id).profile.get_related_mc()
            except:
                pass

    final_batches = []
    for batch in batchs:
        try:
            if not distributor_checkout:
                inventory = Inventry.objects.filter(product=product,
                                                    batch=batch,
                                                    material_center=material,
                                                    created_on__gte=day_before_today_fn(),
                                                    current_quantity__gte=1).latest('created_on')
            else:
                inventory = Distributor_Inventry.objects.filter(product=product,
                                                                batch=batch,
                                                                material_center=material,
                                                                created_on__gte=day_before_today_fn(),
                                                                current_quantity__gte=1).latest('created_on')

            if inventory.current_quantity > 0:
                final_batches.append(batch)

        except:
            pass

    if len(final_batches) > 0:
        batch = final_batches[0]
    else:
        batch = False
    return batch

def mrp_according_batch(product):
    data = usable_batches(product)
    if data:
        mrp = data.mrp
        mrp = "{:.2f}".format(mrp)
    else:
        mrp = 0.0
    return mrp

def get_mc(request=False):
    mc = Material_center.objects.filter(frontend=True).first()
    if request:
        if request.user.is_authenticated:
            try:
                # get the material center if distributor is selected if not then c&f state wise
                if "distributor_checkout" in request.session:
                    mc = Material_center.objects.get(id=request.session['distributor_checkout'])
                else:
                    mc = request.user.profile.get_related_mc()
                    if not mc:
                        mc = Material_center.objects.filter(frontend=True).first()
            except:
                pass
    return mc