from django.shortcuts import render, redirect
from django.db.models import Sum
from mlm_calculation.models import *
from realtime_calculation.models import RealTimeDetail
from django.contrib.auth.decorators import login_required
# from tkinter import *
from datetime import datetime, date, timedelta
from decimal import Decimal
from django.contrib.auth.models import User
import calendar
from django.http import HttpResponse
from PIL import Image, ImageDraw, ImageFont
import os
from mlm_calculation.bussiness_master_bonus import list_levels
from accounts.common_code import check_registration_form_fn
import calendar
import os
# from tkinter import *
from datetime import datetime, date, timedelta
from decimal import Decimal

from PIL import Image, ImageDraw, ImageFont
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render, redirect

from accounts.common_code import check_registration_form_fn
from mlm_calculation.bussiness_master_bonus import list_levels
from mlm_calculation.models import *
from realtime_calculation.models import RealTimeDetail


# Create your views here.
def previous_month(month, year):
    prev_year = year
    prev_month = month - 1
    if prev_month <= 0:
        prev_month = 12
        prev_year = year - 1
    return prev_month, prev_year


def month_name(month_number):
    month_number = int(month_number)
    return calendar.month_name[month_number]

def time_def():
    time_now = datetime.now()
    today_date = time_now.date()
    month = today_date.month
    year = today_date.year
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


time_now = time_def()['time_now']
month = time_def()['month']
year = time_def()['year']
last_month = time_def()['last_month']
last_year = time_def()['last_year']
last_month_date = time_def()['last_month_date']


class Objectify(object):
    pass

@login_required(login_url='home')
def download_certificate(request):
    today_date = datetime.now().date()
    template = Image.open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "static/images/Certificate Final.jpg"))
    draw = ImageDraw.Draw(template)
    font = ImageFont.truetype(os.path.join(os.path.dirname(os.path.dirname(__file__)), "static/fonts/arial.ttf"), 70)
    font_bigger = ImageFont.truetype(os.path.join(os.path.dirname(os.path.dirname(__file__)), "static/fonts/arial.ttf"), 150)
    ttf = ImageFont.truetype(os.path.join(os.path.dirname(os.path.dirname(__file__)), "static/fonts/courbi.ttf"), 150)
    try:
        title_qs = title_qualification_calculation_model.objects.filter(user=request.user,
                                                                        calculation_stage='Public').latest('pk').highest_qualification_ever
    except:
        title_qs = "Blue Advisor"
    # ARN  co ordiates 2301,2395,2861,2498
    draw.text((2320, 2395), request.user.referralcode.referral_code,font=font, fill='black')
    #  username co ordiates 976,1491,2847,1696
    draw.text((1400, 1030), request.user.profile.first_name.title()+' '+request.user.profile.last_name.title(),font=font_bigger,
              stroke_width=3, fill='black')
    # 1083, 1433, 2622, 1682
    draw.text((1300, 1530), title_qs, font=font_bigger, stroke_width=3, fill='black')
    # for date  3145,2484,3523,2404
    draw.text((3140, 2390), str(today_date), font=font, fill='black')
    response = HttpResponse(content_type='image/jpg')
    template.save(response, "JPEG")
    return response


@login_required(login_url='home')
def download_ID_card(request):
    template = Image.open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "static/images/ID_card.jpg"))
    draw = ImageDraw.Draw(template)
    # ARN  co ordiates 278,269,461,298
    font = ImageFont.truetype(os.path.join(os.path.dirname(os.path.dirname(__file__)), "static/fonts/arial.ttf"), 40)
    draw.text((450,260),request.user.referralcode.referral_code, font=font, fill='black')
    #  username co-ordiates 229,368,494,336
    draw.text((450,330), request.user.profile.first_name.upper() + '  ' + request.user.profile.last_name.upper(),stroke_width=1,font=font,fill='black')
    # pixcel co-ordinates 448,435,671,404
    draw.text((450,390), request.user.profile.co_applicant.title(), font=font, fill='black')
    # pixcel co-ordinates 238,503,433,471
    draw.text((450, 460), request.user.profile.phone_number, font=font, fill='black')
    # for date  379,537,543,568
    draw.text((450, 530), str(request.user.profile.created_on.date()), font=font, fill='black')
    response = HttpResponse(content_type='image/jpg')
    template.save(response, "JPEG")
    return response

def get_title(user_id):
    try:
        highest_qualification = title_qualification_calculation_model.objects.filter(
            user=user_id
        ).latest('pk').highest_qualification_ever
        return highest_qualification
    except title_qualification_calculation_model.DoesNotExist:
        try:
            user_exist = ReferralCode.objects.get(user_id=user_id)
            if user_exist != '':
                return "Blue Advisor"
            else:
                return ''
        except:
            return ''


def get_parent_and_title(user, position):
    parent = ''
    title = ''
    obj_type = ''
    referral_code = ''
    first_name = ''
    last_name = ''
    pk = ''
    try:
        obj_type = str(type(user.user_id))
        if user:
            try:
                parent_is = ReferralCode.objects.filter(parent_id=user.user_id, position=position)
            except:
                parent_is = ''
            if parent_is:
                parent = parent_is[0]
                title = get_title(parent.user_id)
                referral_code = parent.referral_code
                first_name = parent.user_id.profile.first_name
                last_name = parent.user_id.profile.last_name
                pk = parent.user_id.pk
            else:
                try:
                    parent_is = ReferralCode.objects.filter(parent_id=user, position=position)
                except:
                    pass


    except:
        pass
    return parent, title, obj_type, referral_code, first_name, last_name, pk

def get_user_email(user):
    try:
        user_email = User.objects.get(pk=user.user_id).email
    except:
        try:
            user_email = user.user_id.email
        except:
            try:
                user_email = User.objects.get(pk=user).email
            except:
                try:
                    user_email = user.email
                except:
                    user_email = ''
    return user_email

# def grey_or_yellow(user):
#     user_colour = 'GREY'
#     if user:
#         user_email = get_user_email(user)
#         try:
#             o = Order.objects.filter(email=user_email, paid=True).exclude(status=8).aggregate(Sum('pv'))
#             # user_pv = sum([li.pv for li in o])
#             user_pv = o['pv__sum']
#             if user_pv >= green_pv:
#                 user_colour = 'YELLOW'
#         except:
#             pass
#     return user_colour


def green_or_not(user):
    # First we will change the colour of all green ids to yellow.
    user_colour, user_pv, user_bv = 'GREY', '', ''
    if user:
        user_email = get_user_email(user)
        o_green_pv = Order.objects.filter(email=user_email, paid=True, delete=False).exclude(status=8).aggregate(Sum('pv'))
        user_pv_total = o_green_pv['pv__sum']
        if user_pv_total:
            o_active_pv = Order.objects.filter(email=user_email, date__month=month_fn(), date__year=year_fn(), paid=True,
                                               delete=False).exclude(status=8).aggregate(Sum('pv'))
            user_pv = o_active_pv['pv__sum']
            if not user_pv:
                user_pv = 0

            o_active_bv = Order.objects.filter(email=user_email, date__month=month_fn(), date__year=year_fn(), paid=True,
                                               delete=False).exclude(status=8).aggregate(Sum('bv'))
            user_bv = o_active_bv['bv__sum']
            if not user_bv:
                user_bv = 0

            try:
                active_pv = configurations.objects.all()[0].minimum_monthly_purchase_to_become_active
                green_pv = super_model.objects.all()[0].purchase_pv
            except:
                active_pv = False
                green_pv = False

            # Hard Coded Details to Avoid Error.
            if not active_pv:
                active_pv = 30
            if not green_pv:
                green_pv = 100

            if user_pv_total >= green_pv:
                user_colour = 'YELLOW'
                if user_pv:
                    if user_pv >= active_pv:
                        user_colour = 'GREEN'

    # Note: keep user_colour in 2 position as it is used elsewhere also.
    return user, user_colour, user_pv, user_bv


def organisation_structure_params(user):
    userify = Objectify()
    userify.user_id = user

    user_1_l, user_1_l_title, user_1_l_obj, user_1_l_referral_code, user_1_l_first_name, user_1_l_last_name, user_1_l_pk = get_parent_and_title(userify, 'LEFT')
    user_1_r, user_1_r_title, user_1_r_obj, user_1_r_referral_code, user_1_r_first_name, user_1_r_last_name, user_1_r_pk = get_parent_and_title(userify, 'RIGHT')
    user_2_l_l, user_2_l_l_title, user_2_l_l_obj, user_2_l_l_referral_code, user_2_l_l_first_name, user_2_l_l_last_name, user_2_l_l_pk = get_parent_and_title(user_1_l, 'LEFT')
    user_2_l_r, user_2_l_r_title, user_2_l_r_obj, user_2_l_r_referral_code, user_2_l_r_first_name, user_2_l_r_last_name, user_2_l_r_pk = get_parent_and_title(user_1_l, 'RIGHT')
    user_2_r_l, user_2_r_l_title, user_2_r_l_obj, user_2_r_l_referral_code, user_2_r_l_first_name, user_2_r_l_last_name, user_2_r_l_pk = get_parent_and_title(user_1_r, 'LEFT')
    user_2_r_r, user_2_r_r_title, user_2_r_r_obj, user_2_r_r_referral_code, user_2_r_r_first_name, user_2_r_r_last_name, user_2_r_r_pk = get_parent_and_title(user_1_r, 'RIGHT')
    user_3_l_l_l, user_3_l_l_l_title, user_3_l_l_l_obj, user_3_l_l_l_referral_code, user_3_l_l_l_first_name, user_3_l_l_l_last_name, user_3_l_l_l_pk = get_parent_and_title(user_2_l_l, 'LEFT')
    user_3_l_l_r, user_3_l_l_r_title, user_3_l_l_r_obj, user_3_l_l_r_referral_code, user_3_l_l_r_first_name, user_3_l_l_r_last_name, user_3_l_l_r_pk = get_parent_and_title(user_2_l_l, 'RIGHT')
    user_3_l_r_l, user_3_l_r_l_title, user_3_l_r_l_obj, user_3_l_r_l_referral_code, user_3_l_r_l_first_name, user_3_l_r_l_last_name, user_3_l_r_l_pk = get_parent_and_title(user_2_l_r, 'LEFT')
    user_3_l_r_r, user_3_l_r_r_title, user_3_l_r_r_obj, user_3_l_r_r_referral_code, user_3_l_r_r_first_name, user_3_l_r_r_last_name, user_3_l_r_r_pk = get_parent_and_title(user_2_l_r, 'RIGHT')
    user_3_r_l_l, user_3_r_l_l_title, user_3_r_l_l_obj, user_3_r_l_l_referral_code, user_3_r_l_l_first_name, user_3_r_l_l_last_name, user_3_r_l_l_pk = get_parent_and_title(user_2_r_l, 'LEFT')
    user_3_r_l_r, user_3_r_l_r_title, user_3_r_l_r_obj, user_3_r_l_r_referral_code, user_3_r_l_r_first_name, user_3_r_l_r_last_name, user_3_r_l_r_pk = get_parent_and_title(user_2_r_l, 'RIGHT')
    user_3_r_r_l, user_3_r_r_l_title, user_3_r_r_l_obj, user_3_r_r_l_referral_code, user_3_r_r_l_first_name, user_3_r_r_l_last_name, user_3_r_r_l_pk = get_parent_and_title(user_2_r_r, 'LEFT')
    user_3_r_r_r, user_3_r_r_r_title, user_3_r_r_r_obj, user_3_r_r_r_referral_code, user_3_r_r_r_first_name, user_3_r_r_r_last_name, user_3_r_r_r_pk = get_parent_and_title(user_2_r_r, 'RIGHT')

    # Get further user details
    user_1_l, user_1_l_colour,user_1_l_ppv, user_1_l_pbv = green_or_not(user_1_l)
    user_1_r, user_1_r_colour,user_1_r_ppv, user_1_r_pbv = green_or_not(user_1_r)
    user_2_l_l, user_2_l_l_colour,user_2_l_l_ppv, user_2_l_l_pbv = green_or_not(user_2_l_l)
    user_2_l_r, user_2_l_r_colour,user_2_l_r_ppv, user_2_l_r_pbv = green_or_not(user_2_l_r)
    user_2_r_l, user_2_r_l_colour,user_2_r_l_ppv, user_2_r_l_pbv = green_or_not(user_2_r_l)
    user_2_r_r, user_2_r_r_colour,user_2_r_r_ppv, user_2_r_r_pbv = green_or_not(user_2_r_r)
    user_3_l_l_l, user_3_l_l_l_colour,user_3_l_l_l_ppv, user_3_l_l_l_pbv = green_or_not(user_3_l_l_l)
    user_3_l_l_r, user_3_l_l_r_colour,user_3_l_l_r_ppv, user_3_l_l_r_pbv = green_or_not(user_3_l_l_r)
    user_3_l_r_l, user_3_l_r_l_colour,user_3_l_r_l_ppv, user_3_l_r_l_pbv = green_or_not(user_3_l_r_l)
    user_3_l_r_r, user_3_l_r_r_colour,user_3_l_r_r_ppv, user_3_l_r_r_pbv = green_or_not(user_3_l_r_r)
    user_3_r_l_l, user_3_r_l_l_colour,user_3_r_l_l_ppv, user_3_r_l_l_pbv = green_or_not(user_3_r_l_l)
    user_3_r_l_r, user_3_r_l_r_colour,user_3_r_l_r_ppv, user_3_r_l_r_pbv = green_or_not(user_3_r_l_r)
    user_3_r_r_l, user_3_r_r_l_colour,user_3_r_r_l_ppv, user_3_r_r_l_pbv = green_or_not(user_3_r_r_l)
    user_3_r_r_r, user_3_r_r_r_colour,user_3_r_r_r_ppv, user_3_r_r_r_pbv = green_or_not(user_3_r_r_r)

    params_dict = {
        'user_1_l': user_1_l,
        'user_1_r': user_1_r,
        'user_2_l_l': user_2_l_l,
        'user_2_l_r': user_2_l_r,
        'user_2_r_l': user_2_r_l,
        'user_2_r_r': user_2_r_r,
        'user_3_l_l_l': user_3_l_l_l,
        'user_3_l_l_r': user_3_l_l_r,
        'user_3_l_r_l': user_3_l_r_l,
        'user_3_l_r_r': user_3_l_r_r,
        'user_3_r_l_l': user_3_r_l_l,
        'user_3_r_l_r': user_3_r_l_r,
        'user_3_r_r_l': user_3_r_r_l,
        'user_3_r_r_r': user_3_r_r_r,
        'user_1_l_ppv': user_1_l_ppv,
        'user_1_r_ppv': user_1_r_ppv,
        'user_2_l_l_ppv': user_2_l_l_ppv,
        'user_2_l_r_ppv': user_2_l_r_ppv,
        'user_2_r_l_ppv': user_2_r_l_ppv,
        'user_2_r_r_ppv': user_2_r_r_ppv,
        'user_3_l_l_l_ppv': user_3_l_l_l_ppv,
        'user_3_l_l_r_ppv': user_3_l_l_r_ppv,
        'user_3_l_r_l_ppv': user_3_l_r_l_ppv,
        'user_3_l_r_r_ppv': user_3_l_r_r_ppv,
        'user_3_r_l_l_ppv': user_3_r_l_l_ppv,
        'user_3_r_l_r_ppv': user_3_r_l_r_ppv,
        'user_3_r_r_l_ppv': user_3_r_r_l_ppv,
        'user_3_r_r_r_ppv': user_3_r_r_r_ppv,
        'user_1_l_pbv': user_1_l_pbv,
        'user_1_r_pbv': user_1_r_pbv,
        'user_2_l_l_pbv': user_2_l_l_pbv,
        'user_2_l_r_pbv': user_2_l_r_pbv,
        'user_2_r_l_pbv': user_2_r_l_pbv,
        'user_2_r_r_pbv': user_2_r_r_pbv,
        'user_3_l_l_l_pbv': user_3_l_l_l_pbv,
        'user_3_l_l_r_pbv': user_3_l_l_r_pbv,
        'user_3_l_r_l_pbv': user_3_l_r_l_pbv,
        'user_3_l_r_r_pbv': user_3_l_r_r_pbv,
        'user_3_r_l_l_pbv': user_3_r_l_l_pbv,
        'user_3_r_l_r_pbv': user_3_r_l_r_pbv,
        'user_3_r_r_l_pbv': user_3_r_r_l_pbv,
        'user_3_r_r_r_pbv': user_3_r_r_r_pbv,
        'user_1_l_title': user_1_l_title,
        'user_1_r_title': user_1_r_title,
        'user_2_l_l_title': user_2_l_l_title,
        'user_2_l_r_title': user_2_l_r_title,
        'user_2_r_l_title': user_2_r_l_title,
        'user_2_r_r_title': user_2_r_r_title,
        'user_3_l_l_l_title': user_3_l_l_l_title,
        'user_3_l_l_r_title': user_3_l_l_r_title,
        'user_3_l_r_l_title': user_3_l_r_l_title,
        'user_3_l_r_r_title': user_3_l_r_r_title,
        'user_3_r_l_l_title': user_3_r_l_l_title,
        'user_3_r_l_r_title': user_3_r_l_r_title,
        'user_3_r_r_l_title': user_3_r_r_l_title,
        'user_3_r_r_r_title': user_3_r_r_r_title,
        'user_1_l_colour': user_1_l_colour,
        'user_1_r_colour': user_1_r_colour,
        'user_2_l_l_colour': user_2_l_l_colour,
        'user_2_l_r_colour': user_2_l_r_colour,
        'user_2_r_l_colour': user_2_r_l_colour,
        'user_2_r_r_colour': user_2_r_r_colour,
        'user_3_l_l_l_colour': user_3_l_l_l_colour,
        'user_3_l_l_r_colour': user_3_l_l_r_colour,
        'user_3_l_r_l_colour': user_3_l_r_l_colour,
        'user_3_l_r_r_colour': user_3_l_r_r_colour,
        'user_3_r_l_l_colour': user_3_r_l_l_colour,
        'user_3_r_l_r_colour': user_3_r_l_r_colour,
        'user_3_r_r_l_colour': user_3_r_r_l_colour,
        'user_3_r_r_r_colour': user_3_r_r_r_colour,
        'user_1_l_obj':user_1_l_obj,
        'user_1_r_obj':user_1_r_obj,
        'user_2_l_l_obj':user_2_l_l_obj,
        'user_2_l_r_obj':user_2_l_r_obj,
        'user_2_r_l_obj':user_2_r_l_obj,
        'user_2_r_r_obj':user_2_r_r_obj,
        'user_3_l_l_l_obj':user_3_l_l_l_obj,
        'user_3_l_l_r_obj':user_3_l_l_r_obj,
        'user_3_l_r_l_obj':user_3_l_r_l_obj,
        'user_3_l_r_r_obj':user_3_l_r_r_obj,
        'user_3_r_l_l_obj':user_3_r_l_l_obj,
        'user_3_r_l_r_obj':user_3_r_l_r_obj,
        'user_3_r_r_l_obj':user_3_r_r_l_obj,
        'user_3_r_r_r_obj':user_3_r_r_r_obj,
        'user_1_l_referral_code': user_1_l_referral_code,
        'user_1_r_referral_code': user_1_r_referral_code,
        'user_2_l_l_referral_code': user_2_l_l_referral_code,
        'user_2_l_r_referral_code': user_2_l_r_referral_code,
        'user_2_r_l_referral_code': user_2_r_l_referral_code,
        'user_2_r_r_referral_code': user_2_r_r_referral_code,
        'user_3_l_l_l_referral_code': user_3_l_l_l_referral_code,
        'user_3_l_l_r_referral_code': user_3_l_l_r_referral_code,
        'user_3_l_r_l_referral_code': user_3_l_r_l_referral_code,
        'user_3_l_r_r_referral_code': user_3_l_r_r_referral_code,
        'user_3_r_l_l_referral_code': user_3_r_l_l_referral_code,
        'user_3_r_l_r_referral_code': user_3_r_l_r_referral_code,
        'user_3_r_r_l_referral_code': user_3_r_r_l_referral_code,
        'user_3_r_r_r_referral_code': user_3_r_r_r_referral_code,
        'user_1_l_first_name': user_1_l_first_name,
        'user_1_r_first_name': user_1_r_first_name,
        'user_2_l_l_first_name': user_2_l_l_first_name,
        'user_2_l_r_first_name': user_2_l_r_first_name,
        'user_2_r_l_first_name': user_2_r_l_first_name,
        'user_2_r_r_first_name': user_2_r_r_first_name,
        'user_3_l_l_l_first_name': user_3_l_l_l_first_name,
        'user_3_l_l_r_first_name': user_3_l_l_r_first_name,
        'user_3_l_r_l_first_name': user_3_l_r_l_first_name,
        'user_3_l_r_r_first_name': user_3_l_r_r_first_name,
        'user_3_r_l_l_first_name': user_3_r_l_l_first_name,
        'user_3_r_l_r_first_name': user_3_r_l_r_first_name,
        'user_3_r_r_l_first_name': user_3_r_r_l_first_name,
        'user_3_r_r_r_first_name': user_3_r_r_r_first_name,
        'user_1_l_last_name': user_1_l_last_name,
        'user_1_r_last_name': user_1_r_last_name,
        'user_2_l_l_last_name': user_2_l_l_last_name,
        'user_2_l_r_last_name': user_2_l_r_last_name,
        'user_2_r_l_last_name': user_2_r_l_last_name,
        'user_2_r_r_last_name': user_2_r_r_last_name,
        'user_3_l_l_l_last_name': user_3_l_l_l_last_name,
        'user_3_l_l_r_last_name': user_3_l_l_r_last_name,
        'user_3_l_r_l_last_name': user_3_l_r_l_last_name,
        'user_3_l_r_r_last_name': user_3_l_r_r_last_name,
        'user_3_r_l_l_last_name': user_3_r_l_l_last_name,
        'user_3_r_l_r_last_name': user_3_r_l_r_last_name,
        'user_3_r_r_l_last_name': user_3_r_r_l_last_name,
        'user_3_r_r_r_last_name': user_3_r_r_r_last_name,
        'user_1_l_pk': user_1_l_pk,
        'user_1_r_pk': user_1_r_pk,
        'user_2_l_l_pk': user_2_l_l_pk,
        'user_2_l_r_pk': user_2_l_r_pk,
        'user_2_r_l_pk': user_2_r_l_pk,
        'user_2_r_r_pk': user_2_r_r_pk,
        'user_3_l_l_l_pk': user_3_l_l_l_pk,
        'user_3_l_l_r_pk': user_3_l_l_r_pk,
        'user_3_l_r_l_pk': user_3_l_r_l_pk,
        'user_3_l_r_r_pk': user_3_l_r_r_pk,
        'user_3_r_l_l_pk': user_3_r_l_l_pk,
        'user_3_r_l_r_pk': user_3_r_l_r_pk,
        'user_3_r_r_l_pk': user_3_r_r_l_pk,
        'user_3_r_r_r_pk': user_3_r_r_r_pk,
    }
    return params_dict

def search_redirect(type,request):
    # If person has searched for a user
    referral_code_in_url = True
    if type == "SUPER":
        url = '/business/organisation_structure'
    elif type == "INFINITY":
        url = '/business/generational_structure'
    elif type == "downline_details":
        url = '/business/downline_details'
        referral_code_in_url = False
    elif type == "pgxv_details":
        url = '/business/pgxv'
        referral_code_in_url = False
    elif type == "active":
        url = '/business/dyn_active_details'
        referral_code_in_url = False
    elif type == "director":
        url = '/business/dyn_director_details'
        referral_code_in_url = False
    elif type == "tbb":
        url = '/business/dyn_tbb_details'
        referral_code_in_url = False
    elif type == "order_summary":
        url = '/business/order_summary'
        referral_code_in_url = False
    elif type == "income_statement":
        url = '/business/income_statement'
        referral_code_in_url = False
    elif type == "payout_statement":
        url = '/business/payout_statement'
        referral_code_in_url = False
    elif type == "loyalty_purchase":
        url = '/business/loyalty_purchase'
        referral_code_in_url = False
    elif type == "fund_statement":
        url = '/business/fund_statement'
        referral_code_in_url = False
    else:
        url ='/business/business'

    redirect_bool = False
    response = redirect(url + '?msg="User not Found"')
    if request.method == 'POST':
        q = request.POST.get('q', False)
        if q:
            q=q.upper()
            redirect_bool = True
            try:
                referal = ReferralCode.objects.get(referral_code=q)
                user_id = referal.user_id.pk
                referal = referal.referral_code
                url = url + '/' + str(user_id)
                if referral_code_in_url:
                    url = url + '/' + str(referal)
                response = redirect(url)
            except:
                user_id = None
                referal = None

    # If person has searched for a user but got no results:
    msg = ""
    try:
        if request.method == 'GET':
            msg = request.GET['msg']
    except:
        pass
    return msg, redirect_bool, response

def get_super_details(user):
    rt_left_pv_month, rt_left_bv_month, rt_right_pv_month, rt_right_bv_month, left_consumed, right_consumed, total_pv_as_on_date_left,total_pv_as_on_date_right, t_user = Decimal("0.00"), Decimal(
        "0.00"), Decimal("0.00"), Decimal("0.00"), Decimal("0.00"), Decimal("0.00"), Decimal("0.00"), Decimal("0.00"), ''
    try:
        rt_detail = RealTimeDetail.objects.get(user_id=user, date__month=datetime.now().month,
                                               date__year=datetime.now().year)
        rt_left_pv_month = rt_detail.rt_left_pv_month
        rt_left_bv_month = rt_detail.rt_left_bv_month
        rt_right_pv_month = rt_detail.rt_right_pv_month
        rt_right_bv_month = rt_detail.rt_right_bv_month
    except:
        pass

    try:
        o = Order.objects.filter(email=user.email, date__month=month_fn(), date__year=year_fn(), paid=True, delete=False).exclude(
            status=8)
        main_user = sum([li. pv for li in o])
        current_bv = sum([li.bv for li in o])
        o = Order.objects.filter(email=user.email, date__month=last_month_fn(), date__year=last_year_fn(), paid=True,
                                 delete=False).exclude(status=8)
        last_pv = sum([li.pv for li in o])
        last_bv = sum([li.bv for li in o])
        t_user = team_building_bonus_super_plan_model.objects.filter(user=user,
                                                                     calculation_stage='Public').latest('pk')
        left_consumed = float(t_user.bf_no_of_new_advisor_pv_in_left_position_referred) + float(
            t_user.cm_left_pv) - float(t_user.cm_no_of_new_advisor_pv_in_left_position_referred_carry_forward)
        right_consumed = float(t_user.bf_no_of_new_advisor_pv_in_right_position_referred) + float(
            t_user.cm_right_pv) - float(t_user.cm_no_of_new_advisor_pv_in_right_position_referred_carry_forward)
        total_pv_as_on_date_left = float(
            t_user.cm_no_of_new_advisor_pv_in_left_position_referred_carry_forward) + float(rt_left_pv_month)
        total_pv_as_on_date_right = float(
            t_user.cm_no_of_new_advisor_pv_in_right_position_referred_carry_forward) + float(rt_right_pv_month)
    except:
        pass

    details_dict = {
        'main_user': main_user,
        'rt_left_pv_month': rt_left_pv_month,
        'rt_left_bv_month': rt_left_bv_month,
        'rt_right_pv_month': rt_right_pv_month,
        'rt_right_bv_month': rt_right_bv_month,
        'current_bv':current_bv,
        'last_pv':last_pv,
        'last_bv':last_bv,
        't_user': t_user,
        'left_consumed': left_consumed,
        'right_consumed': right_consumed,
        'total_pv_as_on_date_left': total_pv_as_on_date_left,
        'total_pv_as_on_date_right': total_pv_as_on_date_right,
    }
    return details_dict

@login_required(login_url='home')
def organisation_structure(request):
    msg, redirect_bool, response = search_redirect("SUPER", request)
    if redirect_bool:
        return response

    user = request.user
    top_user_title = get_title(user)
    con_qs = configurations.objects.last()
    super_con_qs = super_model.objects.last()

    params_dict = organisation_structure_params(user)

    details_dict = get_super_details(user)

    super_rt_details_dict = super_rt_details(user, con_qs)

    left_users = 0
    right_users = 0
    left_green_users = 0
    right_green_users = 0
    for k, v in params_dict.items():
        if k.startswith('refl') and k.endswith("_l") and v != '':
            left_users += 1

        if k.startswith('refl') and k.endswith("_r") and v != '':
            right_users += 1

        if k.endswith("l_colour") and v == 'GREEN':
            left_green_users += 1

        if k.endswith("r_colour") and v == 'GREEN':
            right_green_users += 1


    params_func_dict = {
        'user': user,
        'con_qs': con_qs,
        'super_con_qs': super_con_qs,
        'msg':msg,
        'left_users': left_users,
        'right_users': right_users,
        'right_green_users': right_green_users,
        'left_green_users': left_green_users,
        'title': "Organisation Structure"
    }

    # params = params_dict | details_dict | super_rt_details_dict | params_func_dict
    params = {**params_dict, **details_dict, **super_rt_details_dict, **params_func_dict}
    return render(request, 'business/user_dashboard_11.html', params)

def upline(user_id, myid):
    try:
        upline_id = ReferralCode.objects.get(user_id=myid).referal_by.pk
        if upline_id == user_id:
            return True
        else:
            return upline(user_id, upline_id)
    except:
        return False

def upline_parent(user_id, myid):
    try:
        parent = ReferralCode.objects.get(user_id=myid).parent_id.pk
        if parent == user_id:
            return True
        else:
            return upline_parent(user_id, parent)
    except:
        return False

def check_downline(type, request, myid):
    user_id = request.user.pk
    is_downline = False
    if user_id == myid:
        is_downline = True
    if not is_downline:
        if type == "SUPER":
            is_downline = upline_parent(user_id, myid)
        elif type == "INFINITY":
            is_downline = upline(user_id, myid)
        else:
            pass
    return is_downline

def super_rt_details(user,con_qs):
    refer_by_pk = ReferralCode.objects.get(user_id=user.pk).referal_by
    try:
        refer_by_arn = ReferralCode.objects.get(user_id=refer_by_pk).referral_code
    except:
        refer_by_arn = []
    arn = ReferralCode.objects.get(user_id=user.pk)
    userify = Objectify()
    userify.user_id = user.pk

    try:
        rt_detail = RealTimeDetail.objects.get(user_id=user.pk, date__month=datetime.now().month,
                                               date__year=datetime.now().year)
        rt_detail_user_id = rt_detail.user_id
        rt_detail_date = rt_detail.date

    except RealTimeDetail.DoesNotExist:
        rt_detail = None
        rt_detail_user_id = arn.user_id
        rt_detail_date = None

    rt_detail_colour = green_or_not(user)[1]

    super_rt_details_dict = {
        'refer_by_pk':refer_by_pk,
        'refer_by_arn':refer_by_arn,
        'arn':arn,
        'rt_detail_colour':rt_detail_colour,
        'rt_detail':rt_detail,
        'rt_detail_user_id':rt_detail_user_id,
        'rt_detail_date':rt_detail_date
    }

    return super_rt_details_dict

@login_required(login_url='home')
def more_binary(request, myid, referal):
    msg, redirect_bool, response = search_redirect("SUPER", request)
    if redirect_bool:
        return response
    is_downline = check_downline("SUPER", request, myid)
    if not is_downline:
        return redirect('/business/organisation_structure?msg="This user is not in your downline"')

    top_user_title = get_title(myid)
    con_qs = configurations.objects.last()
    super_con_qs = super_model.objects.last()
    user = User.objects.get(pk=myid)

    if request.user.id == myid:
        allow_one_level_above = False
    else:
        allow_one_level_above = True

    super_rt_details_dict = super_rt_details(user, con_qs)
    params_dict = organisation_structure_params(myid)

    left_users = 0
    right_users = 0
    left_green_users = 0
    right_green_users = 0

    for k, v in params_dict.items():
        if k.startswith('refl') and k.endswith("_l") and v != '':
            print(k, v, "dat-------")
            left_users += 1

        if k.startswith('refl') and k.endswith("_r") and v != '':
            right_users += 1

        if k.endswith("l_colour") and v == 'GREEN':
            left_green_users += 1

        if k.endswith("r_colour") and v == 'GREEN':
            right_green_users += 1

    details_dict = get_super_details(user)

    params_func_dict = {
        'user': user,
        'con_qs': con_qs,
        'allow_one_level_above': allow_one_level_above,
        'top_user_title': top_user_title,
        'left_users': left_users,
        'right_users': right_users,
        'left_green_users': left_green_users,
        'right_green_users': right_green_users,
        'title': "Organisation Structure"
    }

    # params = params_dict | details_dict | super_rt_details_dict | params_func_dict
    params = {**params_dict, **details_dict, **super_rt_details_dict, **params_func_dict}

    return render(request, 'business/user_dashboard_11.html', params)

# Generational Functions
def get_users(request, myid, msg):
    activated_users, cm_active_users, cm_inactive_users = {}, {}, {}
    activated_users_list, cm_active_users_list, cm_inactive_users_list = [], [], []

    if myid:
        user = User.objects.get(pk=myid)
    else:
        user = request.user

    refer_by_pk = ReferralCode.objects.get(user_id=user.pk).referal_by
    try:
        refer_by_arn = ReferralCode.objects.get(user_id=refer_by_pk.pk).referral_code
    except:
        refer_by_arn = ''

    arn = ReferralCode.objects.get(user_id=user.pk)

    params = {}
    active_users = {}

    show_all = False
    if request.method == 'GET':
        get_show_all = request.GET.get('show_all', None)
        if get_show_all == "Y":
            show_all = True

    if request.user.id == myid:
        allow_one_level_above = False
    else:
        allow_one_level_above = True

    users = ReferralCode.objects.filter(referal_by=user)


    users_list_proc = users.values_list('user_id')
    users_list = [id[0] for id in users_list_proc]
    try:
        activated_users = RealTimeDetail.objects.filter(user_id__in=users_list, rt_is_user_green=True).values_list(
            'user_id').distinct()
        activated_users_list = [id[0] for id in activated_users]
        activated_users = ReferralCode.objects.filter(user_id__in=activated_users_list)
    except:
        pass
    try:
        cm_active_users = RealTimeDetail.objects.filter(user_id__in=activated_users_list,
                                                        rt_is_user_green=True,
                                                        rt_user_infinity_ppv__gt=0,
                                                        date__month=month_fn(),
                                                        date__year=year_fn()).values_list(
            'user_id').distinct()
        cm_active_users_list = [id[0] for id in cm_active_users]
        cm_active_users = ReferralCode.objects.filter(user_id__in=cm_active_users_list)
    except:
        pass
    try:
        cm_inactive_users_list = list(set(activated_users_list) - set(cm_active_users_list))
        cm_inactive_users = ReferralCode.objects.filter(user_id__in=cm_inactive_users_list)
    except:
        pass

    users = users.exclude(id__in=cm_active_users).exclude(id__in=cm_inactive_users)

    con_qs = configurations.objects.last()

    try:
        rt_detail = RealTimeDetail.objects.get(user_id=user,
                                               date__month=datetime.now().month,
                                               date__year=datetime.now().year)
        rt_detail_user_id = rt_detail.user_id
        rt_detail_date = rt_detail.date

    except RealTimeDetail.DoesNotExist:
        rt_detail = None
        rt_detail_user_id = arn.user_id
        rt_detail_date = None

    rt_detail_colour = green_or_not(user)[1]

    try:
        user = request.user
        o = Order.objects.filter(email=user.email,
                                 date__month=month_fn(),
                                 date__year=year_fn(),
                                 paid=True, delete=False).exclude(
                                status=8)
        current_pv = sum([li.pv for li in o])
        current_bv = sum([li.bv for li in o])
        o = Order.objects.filter(email=user.email, date__month=last_month_fn(), date__year=last_year_fn(), paid=True,
                                 delete=False).exclude(status=8)
        last_pv = sum([li.pv for li in o])
        last_bv = sum([li.bv for li in o])
        t_user = team_building_bonus_super_plan_model.objects.filter(user=request.user,
                                                                     calculation_stage='Public').latest('pk')
    except:
        t_user = ''

    rt_params = {
        'show_all': show_all,
    }

    other_params = {
        'show_all_rt': show_all,
        'arn': arn,
        'users': users,
        'user': user,
        'user_id': rt_detail_user_id,
        'date': rt_detail_date,
        'rt_detail': rt_detail,
        'rt_detail_colour': rt_detail_colour,
        'activated_users': activated_users,
        'cm_active_users': cm_active_users,
        'cm_inactive_users': cm_inactive_users,
        'current_pv': current_pv,
        'current_bv': current_bv,
        'last_pv': last_pv,
        'last_bv': last_bv,
        't_user': t_user,
        'refer_by_pk': refer_by_pk,
        'refer_by_arn': refer_by_arn,
        'msg': msg,
        'allow_one_level_above': allow_one_level_above,
        'title': "Generational Structure",
    }

    if rt_detail:
        params = {**rt_params, **other_params}
    else:
        params = other_params

    return render(request, 'business/user_dashboard_12.html', params)
    # else:
    #     return render(request, 'business/user_dashboard_12.html', {'users': users})


@login_required(login_url='home')
def generational_structure(request):
    msg, redirect_bool, response = search_redirect("INFINITY", request)
    if redirect_bool:
        return response
    return get_users(request, None, msg)


@login_required(login_url='home')
def more_generational_structure(request, myid, referal):
    msg, redirect_bool, response = search_redirect("INFINITY", request)
    if redirect_bool:
        return response
    is_downline = check_downline("INFINITY", request, myid)
    if not is_downline:
        return redirect('/business/generational_structure?msg="This user is not in your downline"')
    return get_users(request, myid, msg)


@login_required(login_url='home')
def business(request):
    # today_date = datetime.now().date()
    # month = today_date.month
    orders = Order.objects.filter(email=request.user.email,
                                  date__month=month_fn(),
                                  date__year=year_fn(),
                                  paid=True)
    pv = orders.aggregate(Sum('pv'))['pv__sum']     # sum([li.pv for li in orders])
    bv = orders.aggregate(Sum('bv'))['bv__sum']     # sum([li.bv for li in orders])
    tbv_cm = RealTimeDetail.objects.filter(user_id=request.user,
                                           date__month=month_fn(),
                                           date__year=year_fn()).aggregate(
        Sum('rt_tbv_month'))['rt_tbv_month__sum']
    tbv_pm = RealTimeDetail.objects.filter(user_id=request.user,
                                           date__month=last_month_fn(),
                                           date__year=last_year_fn(),).aggregate(
                                        Sum('rt_tbv_month'))['rt_tbv_month__sum']
    tbv_acc = RealTimeDetail.objects.filter(user_id=request.user, ).aggregate(Sum('rt_tbv_month'))['rt_tbv_month__sum']
    try:
        title_qs = title_qualification_calculation_model.objects.filter(user=request.user,
                                                                        calculation_stage='Public').latest('pk')
    except:
        title_qs = False

    query_qs = configurations.objects.last()

    check_user_qs = User_Check.objects.filter(user_check=request.user)
    registration_status = False
    if check_user_qs:
        check_user_qs = check_user_qs.first()
        registration_status = check_registration_form_fn(check_user_qs)
        if registration_status == 'Registration  is Complete':
            registration_status = True
        else:
            registration_status = False

    return render(request, 'business/user_dashboard_1.html', {'pv': pv,
                                                              'bv': bv,
                                                              'title_qs': title_qs,
                                                              'query_qs': query_qs,
                                                              'tbv_cm': tbv_cm,
                                                              'tbv_pm': tbv_pm,
                                                              'tbv_acc': tbv_acc,
                                                              'registration_status':registration_status,
                                                              'title': "Business Dashboard",})


@login_required(login_url='home')
def business_summary(request):
    # today_date = datetime.now().date()
    # month = today_date.month
    # year = today_date.year
    user = request.user
    month_cal = datetime.now().date()
    year = month_cal.year
    month = month_cal.month

    if request.method == 'POST':
        month_cal = request.POST.get('month', None)
        if month_cal != '':
            input_date = month_cal.split('-')
            year = input_date[0]
            month = input_date[1]
            month_cal += '-01'

    try:
        data = title_qualification_calculation_model.objects.filter(user=user,
                                                                    date_model__month=month,
                                                                    date_model__year=year)
        data = data.latest('pk')
    except:
        data = []

    try:
        rt_data = RealTimeDetail.objects.filter(user_id=user,
                                                date__month=month,
                                                date__year=year).latest('pk')
    except:
        rt_data = []

    try:
        month = month_name(month_cal.month)
        year = month_cal.year
    except:
        try:
            month = month_name(month)
            year = year
        except:
            month = "Please Select a Date"
            year = ""

    return render(request, 'business/user_dashboard_2.html',{'data': data,
                                                             'input_date': month_cal,
                                                             'rt_data': rt_data,
                                                             'month': month,
                                                             'year': year,
                                                             'title': "Business Details",})


def income_statement_fn(request,month_cal,user):
    if request.method == 'POST':
        month_cal = request.POST.get('month', None)
        if month_cal != '' and month_cal != None:
            input_date = month_cal.split('-')
            year = input_date[0]
            month = input_date[1]
            month_cal += '-01'
            month_cal = datetime.strptime(month_cal, "%Y-%m-%d").date()
    try:
        direct_qs = direct_bonus_super_plan_model.objects.filter(user=user, calculation_stage='Public',
                                                                 input_date__month=month_cal.month,
                                                                 input_date__year=month_cal.year)
        direct_qs = direct_qs.latest('pk')
        direct_bonus_amount = direct_qs.direct_bonus_earned
    except:
        direct_bonus_amount = 0
    try:
        tbb_qs = team_building_bonus_super_plan_model.objects.filter(user=user, calculation_stage='Public',
                                                                     input_date__month=month_cal.month,
                                                                     input_date__year=month_cal.year)
        tbb_qs = tbb_qs.latest('pk')
        tbb_amount = tbb_qs.team_building_bonus_earned
    except:
        tbb_amount = 0
    try:
        lbb_qs = leadership_building_bonus_super_plan_model.objects.filter(user=user, calculation_stage='Public',
                                                                           input_date__month=month_cal.month,
                                                                           input_date__year=month_cal.year)
        lbb_qs = lbb_qs.latest('pk')
        lbb_amount = lbb_qs.leadership_building_bonus_earned
    except:
        lbb_amount = 0
    try:
        lifestyle_qs = life_style_fund_super_plan_model.objects.filter(user=user, calculation_stage='Public',
                                                                       input_date__month=month_cal.month,
                                                                       input_date__year=month_cal.year)
        lifestyle_qs = lifestyle_qs.latest('pk')
        lifestyle_amount = lifestyle_qs.life_style_fund_earned
    except:
        lifestyle_amount = 0
    try:
        retail_qs = retail_margin.objects.filter(user=user, calculation_stage='Public',
                                                 input_date__month=month_cal.month, input_date__year=month_cal.year)
        retail_qs = retail_qs.latest('pk')
        retail_amount = retail_qs.retail_margin
    except:
        retail_amount = 0
    try:
        pb_qs = personal_bonus.objects.filter(user=user, calculation_stage='Public', input_date__month=month_cal.month,
                                              input_date__year=month_cal.year)
        pb_qs = pb_qs.latest('pk')
        pb_amount = pb_qs.personal_bonus_earned
    except:
        pb_amount = 0
    try:
        fb_qs = fortune_bonus.objects.filter(user=user, calculation_stage='Public', input_date__month=month_cal.month,
                                             input_date__year=month_cal.year)
        fb_qs = fb_qs.latest('pk')
        fb_amount = fb_qs.fortune_bonus_earned
    except:
        fb_amount = 0
    try:
        sb_qs = sharing_bonus.objects.filter(user=user, calculation_stage='Public', input_date__month=month_cal.month,
                                             input_date__year=month_cal.year)
        sb_qs = sb_qs.latest('pk')
        sb_amount = sb_qs.sharing_bonus_earned
    except:
        sb_amount = 0
    try:
        nb_qs = nuturing_bonus.objects.filter(user=user, calculation_stage='Public', input_date__month=month_cal.month,
                                              input_date__year=month_cal.year)
        nb_qs = nb_qs.latest('pk')
        nb_amount = nb_qs.nurturing_bonus_earned
    except:
        nb_amount = 0
    try:
        bmb_qs = business_master_bonus.objects.filter(user=user, calculation_stage='Public',
                                                      input_date__month=month_cal.month,
                                                      input_date__year=month_cal.year)
        bmb_qs = bmb_qs.latest('pk')
        bmb_amount = bmb_qs.business_master_bonus_earned
    except:
        bmb_amount = 0
    try:
        vacation_qs = vacation_fund.objects.filter(user=user, calculation_stage='Public',
                                                   input_date__month=month_cal.month, input_date__year=month_cal.year)
        vacation_qs = vacation_qs.latest('pk')
        vacation_amount = vacation_qs.vacation_fund_earned
    except:
        vacation_amount = 0
    try:
        automobile_qs = automobile_fund.objects.filter(user=user, calculation_stage='Public',
                                                       input_date__month=month_cal.month,
                                                       input_date__year=month_cal.year)
        automobile_qs = automobile_qs.latest('pk')
        automobile_amount = automobile_qs.automobile_fund_earned
    except:
        automobile_amount = 0
    try:
        shelter_qs = shelter_fund.objects.filter(user=user, calculation_stage='Public',
                                                 input_date__month=month_cal.month, input_date__year=month_cal.year)
        shelter_qs = shelter_qs.latest('pk')
        shelter_amount = shelter_qs.shelter_fund_earned
    except:
        shelter_amount = 0
    try:
        cri_qs = consistent_retailers_income.objects.filter(user=user, calculation_stage='Public',
                                                            input_date__month=month_cal.month,
                                                            input_date__year=month_cal.year)
        cri_qs = cri_qs.latest('pk')
        cri_amount = cri_qs.cri_earned
    except:
        cri_amount = 0

    half_total = float(direct_bonus_amount) + float(tbb_amount) + float(lbb_amount) + float(lifestyle_amount)
    full_total = float(retail_amount) + float(pb_amount) + float(fb_amount) + float(sb_amount) + float(
        nb_amount) + float(bmb_amount) + float(vacation_amount) + float(automobile_amount) + float(
        shelter_amount) + float(cri_amount)
    grand_total = half_total + full_total

    try:
        month = month_name(month_cal.month)
        year = month_cal.year
    except:
        try:
            month = month_name(month)
            year = year
        except:
            month = "Please Select a Date"
            year = ""

    common_params = {
        'input_date': month_cal,
        'grand_total': grand_total,
        'half_total': half_total,
        'full_total': full_total,
        'direct_bonus_amount': direct_bonus_amount,
        'tbb_amount': tbb_amount,
        'lbb_amount': lbb_amount,
        'lifestyle_amount': lifestyle_amount,
        'retail_amount': retail_amount,
        'pb_amount': pb_amount,
        'fb_amount': fb_amount,
        'sb_amount': sb_amount,
        'nb_amount': nb_amount,
        'bmb_amount': bmb_amount,
        'vacation_amount': vacation_amount,
        'automobile_amount': automobile_amount,
        'shelter_amount': shelter_amount,
        'cri_amount': cri_amount,
        'month': month,
        'year': year,
        'title': "Income Statement",
    }

    return common_params


@login_required(login_url='home')
def income_statement(request):
    month_cal = datetime.now().date()
    month_cal = last_month_date
    user = request.user

    msg, redirect_bool, response = search_redirect("income_statement", request)
    if redirect_bool:
        return response

    pid = request.user.pk
    common_params = downline_details_common_fn(request, pid, msg)
    referall_code = request.user.referralcode.referral_code
    user_name = request.user.profile.first_name + ' ' + request.user.profile.last_name

    income_statement_params = income_statement_fn(request,month_cal,user)

    other_params = {
        'referall_code': referall_code,
        'user_name': user_name,
        'report_type': 'income_statement',
        'add': False,
    }

    params = {**income_statement_params, **common_params, **other_params}

    return render(request, 'business/income_statement.html', params)

@login_required(login_url='home')
def income_statement_add(request, pid):
    month_cal = datetime.now().date()
    month_cal = last_month_date
    try:
        user = User.objects.get(id=pid)
    except:
        user = request.user

    msg, redirect_bool, response = search_redirect("income_statement", request)
    if redirect_bool:
        return response
    is_downline = check_downline("INFINITY", request, pid)
    if not is_downline:
        return redirect('/business/income_statement?msg="This user is not in your downline"')

    common_params = downline_details_common_fn(request, pid, msg)

    income_statement_params = income_statement_fn(request, month_cal, user)

    other_params = {
        'report_type': 'income_statement',
        'add': False,
    }

    params = {**income_statement_params, **common_params, **other_params}

    return render(request, 'business/income_statement.html', params)


@login_required(login_url='home')
def income_statement_details(request, detail):
    print("detail:", detail)
    month_cal = datetime.now().date()
    month_cal = last_month_date
    user = request.user

    msg, redirect_bool, response = search_redirect("income_statement", request)
    if redirect_bool:
        return response

    pid = request.user.pk
    common_params = downline_details_common_fn(request, pid, msg)
    referall_code = request.user.referralcode.referral_code
    user_name = request.user.profile.first_name + ' ' + request.user.profile.last_name

    income_statement_params = income_statement_fn(request, month_cal, user)

    if detail == 'Direct Bonus':
        detail = detail
    if detail == 'Team Building Bonus':
        detail = detail
    if detail == 'Leadership Building Bonus':
        detail = detail
    if detail == 'Lifestyle Fund':
        detail = detail
    if detail == 'Personal Bonus':
        detail = detail
    if detail == 'Fortune Bonus':
        detail = detail
    if detail == 'Sharing Bonus':
        detail = detail
    if detail == 'Nurturing Bonus':
        detail = detail
    if detail == 'Business Master Bonus':
        detail = detail
    if detail == 'Vacation Fund':
        detail = detail
    if detail == 'Automobile Fund':
        detail = detail
    if detail == 'Shelter Fund':
        detail = detail
    if detail == 'Consistent Retailer’s Income':
        detail = detail

    other_params = {
        'referall_code': referall_code,
        'user_name': user_name,
        'report_type': 'income_statement',
        'add': False,
        'detail': detail
    }
    params = {**income_statement_params, **common_params, **other_params}
    return render(request, 'business/income_statement_details.html', params)


def payout_statement_fn(request, user):
    month_cal = datetime.now().date()
    month_cal = last_month_date
    year = month_cal.year
    month = month_cal.month
    if request.method == 'POST':
        month_cal = request.POST.get('month', None)
        if month_cal != '' and month_cal != None:
            input_date = month_cal.split('-')
            year = input_date[0]
            month = input_date[1]
            month_cal += '-01'
    try:
        direct_qs = direct_bonus_super_plan_model.objects.filter(user=user,
                                                                 calculation_stage='Public',
                                                                 input_date__month=month,
                                                                 input_date__year=year)
        direct_qs = direct_qs.latest('pk')
        direct_bonus_amount = direct_qs.direct_bonus_earned #direct_bonus_paid
    except:
        direct_bonus_amount = 0
    try:
        tbb_qs = team_building_bonus_super_plan_model.objects.filter(user=user, calculation_stage='Public',
                                                                     input_date__month=month, input_date__year=year)
        tbb_qs = tbb_qs.latest('pk')
        tbb_amount = tbb_qs.team_building_bonus_earned #team_building_bonus_paid
    except:
        tbb_amount = 0
    try:
        lbb_qs = leadership_building_bonus_super_plan_model.objects.filter(user=user,
                                                                           calculation_stage='Public',
                                                                           input_date__month=month,
                                                                           input_date__year=year)
        lbb_qs = lbb_qs.latest('pk')
        lbb_amount = lbb_qs.leadership_building_bonus_earned #leadership_building_bonus_paid
    except:
        lbb_amount = 0
    try:
        pb_qs = personal_bonus.objects.filter(user=user,
                                              calculation_stage='Public',
                                              input_date__month=month,
                                              input_date__year=year)
        pb_qs = pb_qs.latest('pk')
        pb_amount = pb_qs.personal_bonus_earned #personal_bonus_paid
    except:
        pb_amount = 0
    try:
        fb_qs = fortune_bonus.objects.filter(user=user,
                                             calculation_stage='Public',
                                             input_date__month=month,
                                             input_date__year=year)
        fb_qs = fb_qs.latest('pk')
        fb_amount = fb_qs.fortune_bonus_earned #fortune_bonus_paid
    except:
        fb_amount = 0
    try:
        sb_qs = sharing_bonus.objects.filter(user=user,
                                             calculation_stage='Public',
                                             input_date__month=month,
                                             input_date__year=year)
        sb_qs = sb_qs.latest('pk')
        sb_amount = sb_qs.sharing_bonus_earned #sharing_bonus_paid
    except:
        sb_amount = 0
    try:
        nb_qs = nuturing_bonus.objects.filter(user=user,
                                              calculation_stage='Public',
                                              input_date__month=month,
                                              input_date__year=year)
        nb_qs = nb_qs.latest('pk')
        nb_amount = nb_qs.nurturing_bonus_earned #nurturing_bonus_paid
    except:
        nb_amount = 0
    try:
        bmb_qs = business_master_bonus.objects.filter(user=user,
                                                      calculation_stage='Public',
                                                      input_date__month=month,
                                                      input_date__year=year)
        bmb_qs = bmb_qs.latest('pk')
        bmb_amount = bmb_qs.business_master_bonus_earned #business_master_bonus_paid
    except:
        bmb_amount = 0

    payment_status = "UNPAID"
    try:
        commission_wallet = commission_wallet_amount_out_detail_model.objects.filter(input_date__month=month,
                                                                                     input_date__year=year,
                                                                                     instrument_amount_without_comma_style__gt=0)
        if commission_wallet:
            payment_status = "PAID"
    except:
        pass

    half_total = float(direct_bonus_amount) + float(tbb_amount) + float(lbb_amount)
    full_total = float(pb_amount) + float(fb_amount) + float(sb_amount) + float(
        nb_amount) + float(bmb_amount)
    grand_total = half_total + full_total
    try:
        month = month_name(month_cal.month)
        year = month_cal.year
    except:
        try:
            month = month_name(month)
            year = year
        except:
            month = "Please Select a Date"
            year = ""

    # Checking if user has entered PAN details and if they are corret or not.
    pan = False
    try:
        pan = Kyc.objects.get(kyc_user=user).pan_number
        if pan:
            # To check if PAN is correct, we will use two methods
            # 1) PAN details if of 10 digits
            # 2) PAN details has been manually marked as checked by the user.
            if len(pan) == 10:
                pan = True
            if not pan:
                pan_check = False
                try:
                    pan_check = User_Check.objects.get(user_check=user).check_pan_number
                    pan = True
                except:
                    pass
    except:
        pass

    payout_statement_params = {
        'input_date': month_cal,
        'grand_total': grand_total,
        'half_total': half_total,
        'full_total': full_total,
        'direct_bonus_amount': direct_bonus_amount,
        'tbb_amount': tbb_amount,
        'lbb_amount': lbb_amount,
        'pb_amount': pb_amount,
        'fb_amount': fb_amount,
        'sb_amount': sb_amount,
        'nb_amount': nb_amount,
        'bmb_amount': bmb_amount,
        'month': month,
        'year': year,
        'payment_status':payment_status,
        'pan':pan,
        'title':"Payout Statement"
    }

    return payout_statement_params

@login_required(login_url='home')
def payout_statement(request):
    user = request.user

    msg, redirect_bool, response = search_redirect("payout_statement", request)
    if redirect_bool:
        return response

    pid = request.user.pk
    common_params = downline_details_common_fn(request, pid, msg)
    referall_code = request.user.referralcode.referral_code
    user_name = request.user.profile.first_name + ' ' + request.user.profile.last_name

    payout_statement_params = payout_statement_fn(request,user)

    other_params = {
        'referall_code': referall_code,
        'user_name': user_name,
        'report_type': 'payout_statement',
        'add': False,
    }

    params = {**payout_statement_params, **common_params, **other_params}

    return render(request, 'business/payout_statement.html', params)

@login_required(login_url='home')
def payout_statement_add(request,pid):
    try:
        user = User.objects.get(id=pid)
    except:
        user = request.user

    msg, redirect_bool, response = search_redirect("payout_statement", request)
    if redirect_bool:
        return response

    is_downline = check_downline("INFINITY", request, pid)
    if not is_downline:
        return redirect('/business/payout_statement?msg="This user is not in your downline"')

    common_params = downline_details_common_fn(request, pid, msg)

    payout_statement_params = payout_statement_fn(request, user)

    other_params = {
        'report_type': 'payout_statement',
        'add': False,
    }

    params = {**payout_statement_params, **common_params, **other_params}

    return render(request, 'business/payout_statement.html', params)


def loyalty_purchase_fn(request, user):
    cri_qs = consistent_retailers_income.objects.filter(user=user, calculation_stage='Public')
    try:
        cri_qs = cri_qs.latest('pk')
        loyalty_purchase_earned = cri_qs.cri_earned
        loyalty_purchase_used = cri_qs.cri_consumed
    except:
        loyalty_purchase_earned = 0.00
        loyalty_purchase_used = 0.00
    # if loyalty_purchase_earned >= loyalty_purchase_used:
    balance = loyalty_purchase_earned - loyalty_purchase_used

    loyalty_purchase_params = {'loyalty_purchase_earned': loyalty_purchase_earned,
                               'loyalty_purchase_used': loyalty_purchase_used,
                               'balance': balance,
                               'title': "Consistent Retailer's Income Balance",}

    return loyalty_purchase_params

@login_required(login_url='home')
def loyalty_purchase(request):
    user = request.user

    msg, redirect_bool, response = search_redirect("loyalty_purchase", request)
    if redirect_bool:
        return response

    pid = request.user.pk
    common_params = downline_details_common_fn(request, pid, msg)
    referall_code = request.user.referralcode.referral_code
    user_name = request.user.profile.first_name + ' ' + request.user.profile.last_name

    loyalty_purchase_params = loyalty_purchase_fn(request, user)

    other_params = {
        'referall_code': referall_code,
        'user_name': user_name,
        'report_type': 'loyalty_purchase',
        'add': False,
    }

    params = {**loyalty_purchase_params, **common_params, **other_params}

    return render(request, 'business/loyalty_purchase.html', params)

@login_required(login_url='home')
def loyalty_purchase_add(request,pid):
    try:
        user = User.objects.get(id=pid)
    except:
        user = request.user

    msg, redirect_bool, response = search_redirect("loyalty_purchase", request)
    if redirect_bool:
        return response

    is_downline = check_downline("INFINITY", request, pid)
    if not is_downline:
        return redirect('/business/loyalty_purchase?msg="This user is not in your downline"')

    common_params = downline_details_common_fn(request, pid, msg)

    loyalty_purchase_params = loyalty_purchase_fn(request, user)

    other_params = {
        'report_type': 'loyalty_purchase',
        'add': False,
    }

    params = {**loyalty_purchase_params, **common_params, **other_params}

    return render(request, 'business/loyalty_purchase.html', params)

def fund_statement_fn(request, user):
    lsf_qs = life_style_fund_super_plan_model.objects.filter(user=user, calculation_stage='Public')
    vacation_qs = vacation_fund.objects.filter(user=user, calculation_stage='Public')
    automobile_qs = automobile_fund.objects.filter(user=user, calculation_stage='Public')
    shelter_qs = shelter_fund.objects.filter(user=user, calculation_stage='Public')

    try:
        lsf_qs = lsf_qs.latest('pk')
        lsf_close = lsf_qs.life_style_fund_closing
    except:
        lsf_close = 0.00
    try:
        vacation_qs = vacation_qs.latest('pk')
        vacation_close = vacation_qs.closing_vacation_fund
    except:
        vacation_close = 0.00
    try:
        automobile_qs = automobile_qs.latest('pk')
        automobile_close = automobile_qs.closing_automobile_fund
    except:
        automobile_close = 0.00
    try:
        shelter_qs = shelter_qs.latest('pk')
        shelter_close = shelter_qs.closing_shelter_fund
    except:
        shelter_close = 0.00
    total_fund = float(lsf_close) + float(vacation_close) + float(automobile_close) + float(shelter_close)
    fund_statement_params = {'lsf_close': lsf_close,
              'vacation_close': vacation_close,
              'automobile_close': automobile_close,
              'shelter_close': shelter_close,
              'total_fund': total_fund,
              'title': "Fund Statement",
              }
    return fund_statement_params

@login_required(login_url='home')
def fund_statement(request):
    user = request.user

    msg, redirect_bool, response = search_redirect("fund_statement", request)
    if redirect_bool:
        return response

    pid = request.user.pk
    common_params = downline_details_common_fn(request, pid, msg)
    referall_code = request.user.referralcode.referral_code
    user_name = request.user.profile.first_name + ' ' + request.user.profile.last_name

    fund_statement_params = fund_statement_fn(request, user)

    other_params = {
        'referall_code': referall_code,
        'user_name': user_name,
        'report_type': 'loyalty_purchase',
        'add': False,
    }

    params = {**fund_statement_params, **common_params, **other_params}

    return render(request, 'business/fund_statement.html', params)

@login_required(login_url='home')
def fund_statement_add(request,pid):
    try:
        user = User.objects.get(id=pid)
    except:
        user = request.user

    msg, redirect_bool, response = search_redirect("fund_statement", request)
    if redirect_bool:
        return response

    is_downline = check_downline("INFINITY", request, pid)
    if not is_downline:
        return redirect('/business/fund_statement?msg="This user is not in your downline"')

    common_params = downline_details_common_fn(request, pid, msg)

    fund_statement_params = fund_statement_fn(request, user)

    other_params = {
        'report_type': 'loyalty_purchase',
        'add': False,
    }

    params = {**fund_statement_params, **common_params, **other_params}

    return render(request, 'business/fund_statement.html', params)


@login_required(login_url='home')
def upline_details(request):
    users_details = ReferralCode.objects.get(user_id=request.user)
    try:
        upline_mobile_number = Profile.objects.get(user=users_details.referal_by)
    except:
        upline_mobile_number = ""
    params = {
        'users_details': users_details,
        'upline_mobile_number': upline_mobile_number,
        'title': "Upline Details",
    }
    return render(request, 'business/user_dashboard_7.html', params)

def downline_details_common_fn(request, pid, msg, dynamic=False):
    today_date = datetime.now().date()
    if not dynamic:
        month = today_date.month
        year = today_date.year
    else:
        month = last_month_fn()
        year =last_year_fn()
    pv = ''
    show_inactive_ids = False
    if request.method == 'GET':
        try:
            year = int(request.GET.get('year'))
            month = int(request.GET.get('month'))
            pv = request.GET.get('pv')
        except:
            pass
        try:
            show_inactive_ids = request.GET.get('show_inactive_ids')
        except:
            pass

    # Show Point Values of Business Volumes
    if (pv == 'Y' or pv =='y'):
        pv = True
    else:
        pv = False

    if request.method == 'POST':
        month_cal = request.POST.get('month', None)
        if month_cal != '':
            input_date = month_cal.split('-')
            year = input_date[0]
            month = input_date[1]
            month_cal += '-01'
    try:
        user = User.objects.get(id=pid)
    except:
        user = request.user
    referall_code = user.referralcode.referral_code
    user_name = user.profile.first_name + ' ' + user.profile.last_name

    try:
        self_user = RealTimeDetail.objects.get(user_id=user,
                                               date__month=month,
                                               date__year=year)
    except:
        self_user = []

    try:
        title = title_qualification_calculation_model.objects.filter(user=user,
                                                                     calculation_stage='Public').latest(
            'date_model')
    except:
        title = []

    try:
        self_title = title_qualification_calculation_model.objects.get(user=user,
                                                                       date_model__month=month,
                                                                       date_model__year=year)
    except:
        self_title = Objectify()
        self_title.user = Objectify()
        self_title.user.id = user.id

    try:
        # users = title_qualification_calculation_model.objects.filter(pk=myid)
        users_details = ReferralCode.objects.filter(referal_by=user)
    except:
        users_details = {}

    try:
        if dynamic=='active':
            dy_active_users = dynamic_compression_active.objects.filter(referral=user,
                                                                        input_date__month=month,
                                                                        input_date__year=year)
            # dy_active_users_list = [user[0] for user in dy_active_users]
            users = RealTimeDetail.objects.filter(user_id__dynamic_compression_active__in=dy_active_users,
                                                  date__month=month,
                                                  date__year=year)
        elif dynamic=='director':
            dy_director_users = dynamic_compression_director.objects.filter(referral=user,
                                                                            input_date__month=month,
                                                                            input_date__year=year)
            # dy_active_users_list = [user[0] for user in dy_active_users]
            users = RealTimeDetail.objects.filter(user_id__dynamic_compression_director__in=dy_director_users,
                                                  date__month=month,
                                                  date__year=year)
        elif dynamic=='tbb':
            dy_tbb_users = dynamic_compression_tbb.objects.filter(referral=user,
                                                                  input_date__month=month,
                                                                  input_date__year=year)
            # dy_active_users_list = [user[0] for user in dy_active_users]
            users = RealTimeDetail.objects.filter(user_id__dynamic_compression_tbb__in=dy_tbb_users,
                                                  date__month=month,
                                                  date__year=year)
        else:
            users = RealTimeDetail.objects.filter(user_id__referralcode__referal_by=user,
                                                  date__month=month,
                                                  date__year=year)
    except:
        users = []

    try:
        downline_title_director = title_qualification_calculation_model.objects.filter(
                                                                        user__referralcode__referal_by=user,
                                                                        date_model__month=month,
                                                                        date_model__year=year,
                                                                        current_month_qualification__in=list_levels)
    except:
        downline_title_director = []

    try:
        downline_title_with_director = title_qualification_calculation_model.objects.filter(
                                                                        user__referralcode__referal_by=user,
                                                                        date_model__month=month,
                                                                        date_model__year=year,
                                                                        is_there_a_qualified_director_in_the_group=True).exclude(
                                                current_month_qualification__in=list_levels)
    except:
        downline_title_with_director = []

    green_user_list = []
    try:
        green_users = RealTimeDetail.objects.filter(user_id__referralcode__referal_by=user,
                                                date__month=month, date__year=year, rt_is_user_green=True)
        for green_user in green_users:
            green_user_id = green_user.user_id.pk
            green_user_list.append(green_user_id)

        downline_title_non_director = title_qualification_calculation_model.objects.filter(
            user_id__in=green_user_list, date_model__month=month, date_model__year=year,
            is_there_a_qualified_director_in_the_group=False).exclude(current_month_qualification__in=list_levels)#)
    except:
        downline_title_non_director = []

    downline_title_inactive = []
    if show_inactive_ids:
        try:
            downline_title_inactive = title_qualification_calculation_model.objects.filter(
                user__referralcode__referal_by=user, date_model__month=month, date_model__year=year,
                is_there_a_qualified_director_in_the_group=False,
                is_user_green=False).exclude(current_month_qualification__in=list_levels).exclude(user_id__in=green_user_list)
        except:
            pass

    try:
        int_month = int(month)
    except:
        int_month = month

    month_num = month
    month = month_name(month)

    url_short = request.path
    url_full = request.get_full_path()

    if url_short == url_full:
        pv_path = url_full + '?month=' + str(month_num) + '&year=' + str(year) + '&pv=Y'
        bv_path = url_full + '?month=' + str(month_num) + '&year=' + str(year) + '&pv=N'
    else:
        pv_path = url_full + '&pv=Y'
        bv_path = url_full + '&pv=N'

    common_params = {
        'referall_code': referall_code,
        'user_name': user_name,
        'users': users,
        'users_details': users_details,
        'self_user': self_user,
        'int_month': int_month,
        'month': month,
        'year': year,
        'pv': pv,
        'msg': msg,
        'pv_path':pv_path,
        'bv_path':bv_path,
        'self_title':self_title,
        'downline_title_director':downline_title_director,
        'downline_title_with_director':downline_title_with_director,
        'downline_title_non_director': downline_title_non_director,
        'downline_title_inactive': downline_title_inactive,
        'show_inactive_ids':show_inactive_ids,
    }

    return common_params

@login_required(login_url='home')
def downline_details(request):
    msg, redirect_bool, response = search_redirect("downline_details", request)
    if redirect_bool:
        return response
    pid = request.user.pk
    common_params = downline_details_common_fn(request, pid, msg)
    referall_code = request.user.referralcode.referral_code
    user_name = request.user.profile.first_name + ' ' + request.user.profile.last_name

    other_params = {
        'referall_code':referall_code,
        'user_name':user_name,
        'report_type':'downline_details',
        'title': "Downline Details",
    }

    params = {**common_params, **other_params}

    return render(request, 'business/downline_details.html', params)


@login_required(login_url='home')
def downline_details_add(request, pid):
    msg, redirect_bool, response = search_redirect("downline_details", request)
    if redirect_bool:
        return response
    is_downline = check_downline("INFINITY", request, pid)
    if not is_downline:
        return redirect('/business/downline_details?msg="This user is not in your downline"')

    common_params = downline_details_common_fn(request, pid, msg)

    other_params = {
        'report_type': 'downline_details',
        'title': "Downline Details",
    }

    params = {**common_params, **other_params}

    return render(request, 'business/downline_details_add.html', params)


@login_required(login_url='home')
def pgxv_details(request):
    msg, redirect_bool, response = search_redirect("pgxv_details", request)
    if redirect_bool:
        return response
    pid = request.user.pk
    common_params = downline_details_common_fn(request, pid, msg)
    referall_code = request.user.referralcode.referral_code
    user_name = request.user.profile.first_name + ' ' + request.user.profile.last_name

    other_params = {
        'referall_code':referall_code,
        'user_name':user_name,
        'report_type':'downline_details',
        'add':False,
        'title': "Personal Group Details",
    }

    params = {**common_params, **other_params}

    return render(request, 'business/pgxv.html', params)

@login_required(login_url='home')
def pgxv_details_add(request, pid):
    msg, redirect_bool, response = search_redirect("pgxv_details", request)
    if redirect_bool:
        return response
    is_downline = check_downline("INFINITY", request, pid)
    if not is_downline:
        return redirect('/business/downline_details?msg="This user is not in your downline"')

    common_params = downline_details_common_fn(request, pid, msg)

    other_params = {
        'report_type': 'downline_details',
        'add': True,
        'title': "Personal Group Details",
    }

    params = {**common_params, **other_params}

    return render(request, 'business/pgxv.html', params)


@login_required(login_url='home')
def group_summary(request):
    today_date = datetime.now().date()
    month = today_date.month
    year = today_date.year
    referall_code = request.user.referralcode.referral_code
    user_name = request.user.profile.first_name + ' ' + request.user.profile.last_name
    try:
        title = title_qualification_calculation_model.objects.filter(user=request.user,
                                                                     calculation_stage='Public').latest('date_model')
    except:
        title = []
    try:
        user = RealTimeDetail.objects.filter(user_id=request.user).latest("pk")
    except:
        user = []
    try:
        users_details = ReferralCode.objects.filter(referal_by=request.user)
    except:
        users_details = []
    try:
        users = RealTimeDetail.objects.filter(user_id__referralcode__referal_by=request.user, date__month=month,
                                              date__year=year)
    except:
        users = []
    try:
        downline_title = title_qualification_calculation_model.objects.filter(
            user__referralcode__referal_by=request.user).latest('date_model')
    except:
        downline_title = []

    month = month_name(month)
    params = {
        'referall_code': referall_code,
        'user_name': user_name,
        'users': users,
        'title': "Downline Details",
        'downline_title': downline_title,
        'users_details': users_details,
        'month': month,
        'year': year,
    }
    return render(request, 'business/user_dashboard_8_complete.html', params)


@login_required(login_url='home')
def group_summary_add(request, pid):
    today_date = datetime.now().date()
    month = today_date.month
    year = today_date.year
    try:
        try:
            user = User.objects.get(id=pid)
        except:
            user = request.user
        referall_code = user.referralcode.referral_code
        user_name = user.profile.first_name + ' ' + user.profile.last_name
    except:
        user = []
        referall_code = []
        user_name = []
    try:
        title = title_qualification_calculation_model.objects.filter(user=user, calculation_stage='Public').latest(
            'date_model')
    except:
        title = []
    try:
        users_details = ReferralCode.objects.filter(referal_by=user)
    except:
        users_details = []
    try:
        users = RealTimeDetail.objects.filter(user_id__referralcode__referal_by=user,
                                              date__month=month,
                                              date__year=year)
    except:
        users = []
    try:
        downline_title = title_qualification_calculation_model.objects.filter(
            user__referralcode__referal_by=user).latest('date_model')
    except:
        downline_title = []
    month = month_name(month)
    params = {
        'referall_code': referall_code,
        'user_name': user_name,
        'users': users,
        'title': title,
        'downline_title': downline_title,
        'users_details': users_details,
        'month': month,
        'year': year,
    }
    return render(request, 'business/user_dashboard_8_add_complete.html', params)


@login_required(login_url='home')
def dyn_active_details(request):
    msg, redirect_bool, response = search_redirect("active", request)
    if redirect_bool:
        return response
    pid = request.user.pk
    common_params = downline_details_common_fn(request, pid, msg, 'active')
    referall_code = request.user.referralcode.referral_code
    user_name = request.user.profile.first_name + ' ' + request.user.profile.last_name
    other_params = {'referall_code': referall_code,
                    'user_name': user_name,
                    'report_type': 'dyn_active',
                    'title': "Active Line of Sponsorship",}
    params = {**common_params, **other_params}
    return render(request, 'business/downline_details_add.html', params)

@login_required(login_url='home')
def dyn_active_details_add(request, pid):
    msg, redirect_bool, response = search_redirect("active", request)
    if redirect_bool:
        return response
    is_downline = check_downline("INFINITY", request, pid)
    if not is_downline:
        return redirect('/business/downline_details?msg="This user is not in your downline"')
    common_params = downline_details_common_fn(request, pid, msg, 'active')
    other_params = {'report_type': 'dyn_active',
                    'title': "Active Line of Sponsorship",}
    params = {**common_params, **other_params}
    return render(request, 'business/downline_details_add.html', params)

@login_required(login_url='home')
def dyn_director_details(request):
    msg, redirect_bool, response = search_redirect("director", request)
    if redirect_bool:
        return response
    pid = request.user.pk
    common_params = downline_details_common_fn(request, pid, msg, 'director')
    referall_code = request.user.referralcode.referral_code
    user_name = request.user.profile.first_name + ' ' + request.user.profile.last_name
    other_params = {'referall_code': referall_code,
                    'user_name': user_name,
                    'report_type': 'dyn_director',
                    'title': "Line of Sponsorship applicable for Directors",}
    params = {**common_params, **other_params}
    return render(request, 'business/downline_details_add.html', params)

@login_required(login_url='home')
def dyn_director_details_add(request, pid):
    msg, redirect_bool, response = search_redirect("director", request)
    if redirect_bool:
        return response
    is_downline = check_downline("INFINITY", request, pid)
    if not is_downline:
        return redirect('/business/downline_details?msg="This user is not in your downline"')
    common_params = downline_details_common_fn(request, pid, msg, 'director')
    other_params = {'report_type': 'dyn_director',
                    'title': "Line of Sponsorship applicable for Directors",}
    params = {**common_params, **other_params}
    return render(request, 'business/downline_details_add.html', params)

@login_required(login_url='home')
def dyn_tbb_details(request):
    msg, redirect_bool, response = search_redirect("tbb", request)
    if redirect_bool:
        return response
    pid = request.user.pk
    common_params = downline_details_common_fn(request, pid, msg, 'tbb')
    referall_code = request.user.referralcode.referral_code
    user_name = request.user.profile.first_name + ' ' + request.user.profile.last_name
    other_params = {'referall_code': referall_code,
                    'user_name': user_name,
                    'report_type': 'dyn_tbb',
                    'title': "Line of Sponsorship applicable for TBB",}
    params = {**common_params, **other_params}
    return render(request, 'business/downline_details_add.html', params)

@login_required(login_url='home')
def dyn_tbb_details_add(request, pid):
    msg, redirect_bool, response = search_redirect("tbb", request)
    if redirect_bool:
        return response
    is_downline = check_downline("INFINITY", request, pid)
    if not is_downline:
        return redirect('/business/downline_details?msg="This user is not in your downline"')
    common_params = downline_details_common_fn(request, pid, msg, 'tbb')
    other_params = {'report_type': 'dyn_tbb',
                    'title': "Line of Sponsorship applicable for TBB",}
    params = {**common_params, **other_params}
    return render(request, 'business/downline_details_add.html', params)

def level_in_list(li):
    data = []
    if li != None:
        data = li.split(',')
    return data


@login_required(login_url='home')
def commission_wallet(request):
    current_date = date.today().isoformat()
    days_before = (date.today() - timedelta(days=30)).isoformat()
    user = request.user
    commissions = commission_wallet_model.objects.filter(user=user, created_on__gte=days_before,
                                                         created_on__lte=current_date, calculation_stage='Public')
    if request.method == 'POST':
        days_before = request.POST.get('from_date', None)
        current_date = request.POST.get('to_date', None)
        try:
            commissions = commission_wallet_model.objects.filter(user=user, created_on__gte=days_before,
                                                                 created_on__lte=current_date,
                                                                 calculation_stage='Public')
        except:
            pass
    return render(request, 'business/user_dashboard_10.html', {'commissions': commissions})

@login_required(login_url='home')
def welcome_letter(request):
    return render(request, 'business/welcome_letter.html', {'title': "Welcome Letter",})
