from django import template
from shop import models
from mlm_calculation.models import *
from distributor.models import *
from datetime import datetime
register = template.Library()

@register.simple_tag()
def check_active(email):
    today_date = datetime.now().date()
    print(today_date)
    month = today_date.month
    year = today_date.year
    print(month)
    o = Order.objects.filter(email = email,date__month = month,date__year = year)
    print(email)
    total = sum([li.pv for li in o])
    super_qs = configurations.objects.last()
    if total >= super_qs.minimum_monthly_purchase_to_become_active:
        return True
    else:
        return False

@register.simple_tag()
def income(date_model,user):
    try:
        cwm_qs = commission_wallet_model.objects.filter(input_date = date_model,user = user,calculation_stage = 'Public').latest('pk')
        amount = cwm_qs.amount_in
    except:
        amount = 0.00
    return amount

@register.simple_tag()
def blance(amount_in,amount_out):
    try:
       blance_value =  amount_in - amount_out
    except:
        blance_value = 0
    return blance_value

@register.filter()
def downline(user):
    downlines = ReferralCode.objects.filter(referal_by = user)
    return downlines