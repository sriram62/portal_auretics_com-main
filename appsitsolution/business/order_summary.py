from django.db.models.fields import DateTimeField
from django.shortcuts import render,get_object_or_404,redirect
from django.db.models import Sum
from accounts.models import *
from mlm_calculation.models import *
from realtime_calculation.models import RealTimeDetail
from django.contrib.auth.decorators import login_required
# from tkinter import *
from datetime import datetime, date, timedelta
from dateutil.relativedelta import *
from decimal import Decimal
from django.contrib.auth.models import User
import calendar,os
import textwrap
from django.http import HttpResponse
from .views import search_redirect, check_downline, get_user_email
import calendar

def rt_detail(user,month,year):
    pass

def order_detail(user,date_now,date_show):
    year = date_now.year
    month = date_now.month
    user_email = get_user_email(user)
    o = Order.objects.filter(email=user_email, date__month=month, date__year=year, paid=True, delete=False).exclude(
        status=8)
    user_pv = sum([li.pv for li in o])
    user_bv = sum([li.bv for li in o])
    user_total = sum([li.grand_total for li in o])

    order_details = [date_show, user_total, user_bv, user_pv]

    return order_details

def order_detail_total(user):
    user_email = get_user_email(user)
    o = Order.objects.filter(email=user_email, paid=True, delete=False).exclude(status=8)
    user_pv = sum([li.pv for li in o])
    user_bv = sum([li.bv for li in o])
    user_total = sum([li.grand_total for li in o])

    order_details_total = [user_total, user_bv, user_pv]

    return order_details_total

def monthly_details(user):
    order_details = []
    total_order_detail_grand_total = 0.0
    total_order_detail_bv = 0.0
    total_order_detail_pv = 0.0
    date_now = date.today()
    for i in range(12):
        month_char = calendar.month_name[date_now.month][:3]
        date_show = str(month_char) + " - " + str(date_now.year)
        month_order_detail = order_detail(user, date_now, date_show)
        order_details.append(month_order_detail)
        total_order_detail_grand_total += float(month_order_detail[1])
        total_order_detail_bv += float(month_order_detail[2])
        total_order_detail_pv += float(month_order_detail[3])
        date_now = date_now + relativedelta(months=-1)

    return order_details, total_order_detail_grand_total, total_order_detail_bv, total_order_detail_pv

@login_required(login_url='home')
def order_summary(request):
    msg, redirect_bool, response = search_redirect("order_summary", request)
    if redirect_bool:
        return response

    user = request.user

    allow_one_level_above = False
    user_name = user.profile.first_name + ' ' + user.profile.last_name

    order_details, total_order_detail_grand_total, total_order_detail_bv, total_order_detail_pv = monthly_details(user)
    total_order_detail = order_detail_total(user)

    params = {
        'order_details': order_details,
        'allow_one_level_above': allow_one_level_above,
        'user_name': user_name,
        'msg': msg,
        'order_details': order_details,
        'total_order_detail_grand_total': total_order_detail_grand_total,
        'total_order_detail_bv': total_order_detail_bv,
        'total_order_detail_pv': total_order_detail_pv,
        'total_order_detail': total_order_detail,
        'title':"Order Summary"
    }

    return render(request, 'business/order_summary.html', params)


@login_required(login_url='home')
def order_summary_add(request, myid):
    msg, redirect_bool, response = search_redirect("order_summary", request)
    if redirect_bool:
        return response
    is_downline = check_downline("INFINITY", request, myid)
    if not is_downline:
        return redirect('/business/order_summary?msg="This user is not in your downline"')

    user = User.objects.get(pk=myid)

    if request.user.id == myid:
        allow_one_level_above = False
    else:
        allow_one_level_above = True
    try:
        user_name = user.profile.first_name + ' ' + user.profile.last_name
    except:
        try:
            user_name = user.profile.first_name
        except:
            user_name = ""

    order_details, total_order_detail_grand_total, total_order_detail_bv, total_order_detail_pv = monthly_details(user)
    total_order_detail = order_detail_total(user)

    params = {
        'order_details': order_details,
        'allow_one_level_above':allow_one_level_above,
        'user_name':user_name,
        'msg':msg,
        'order_details':order_details,
        'total_order_detail_grand_total':total_order_detail_grand_total,
        'total_order_detail_bv':total_order_detail_bv,
        'total_order_detail_pv':total_order_detail_pv,
        'total_order_detail':total_order_detail,
    }

    return render(request, 'business/order_summary.html', params)