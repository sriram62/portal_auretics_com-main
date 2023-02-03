from business.views import time_def, time_now_fn, month_fn, year_fn, last_month_fn, last_year_fn
from mlm_admin.views import is_mlm_admin
from django.contrib.auth.decorators import user_passes_test
from mlm_admin.decorator import allowed_users
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from notify.models import NoticeTemplate

# Import required for CRM
from mlm_calculation.models import consistent_retailers_income, commission_wallet_model, commission_wallet_amount_out_detail_model
from realtime_calculation.models import RealTimeDetail

# Create your views here.

def crm_list_test(request=False):
    crm_list(request, test=True)

# @user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
# @allowed_users(allowed_roles=['crm_management', ['1', '2', '3', '4']])
def crm_list(request, test=False):
    command = request.POST.get('command',None)
    command_test = request.POST.get('command_test',None)

    if command:
        request.test = test
        result = eval(command)(request)
        messages.error(request, "<a style='color:green'><b>Success</b></a>")

    if command_test:
        test = True
        request.test = test
        result = eval(command_test)(request)
        messages.error(request, "<a style='color:green'><b>Test message sent successfully</b></a>")

    return render(request, 'mlm_admin/crm-list.html', {})


# AG :: Adding False to request so that we can call this function via cron as well.
def send_consistency_message(request=False):
    if request:
        test = request.test

    qs = consistent_retailers_income.objects.filter(input_date__month=last_month_fn(), input_date__year=last_year_fn(),
                                                is_user_qualified_consistent_retailers_income=True,
                                                cri_balance__gt=100, calculation_stage="Public"
                                                )

    if test:
        qs = [qs.first(),]

    for i in qs:
        try:
            params = {
                'var1': " " + str((i.user.profile.first_name + " " + i.user.profile.first_name)),
                'var2': int(i.cri_balance),
                      }
        except:
            messages.error(request,"NO USER MEETING THIS CRITERIA")
            return

        if test:
            email = 'arjun@auretics.com'
            phone_number = '+917840066888'
        else:
            email = i.user.email
            phone_number = "+91" + str(i.user.profile.phone_number)

        NoticeTemplate.send_notification('sms-22',
                                        email_data =params,
                                        sms_data = params,
                                        email = email,
                                        phone_number = phone_number,
                                        send_sms = True,
                                        send_email = False)


def send_business_details(request=False):
    if request:
        test = request.test
    qs = RealTimeDetail.objects.filter(date__month = month_fn(), date__year = year_fn(), rt_pbv__gt=300)

    for i in qs:
        NoticeTemplate.send_notification('on_account_created',
                                         email_data={'var1': 'Abhinav',
                                                     'var2': 'Hi!'},
                                         sms_data={'var1': 'Abhi',
                                                   'var2': 'Hello'},
                                         email='',
                                         phone_number='',
                                         send_sms=True,
                                         send_email=True)


def send_income_summary(request=False):
    if request:
        test = request.test
    qs = commission_wallet_model.objects.filter(input_date__month = month_fn(), input_date__year = year_fn(), amount_in__gt=0)

    for i in qs:
        NoticeTemplate.send_notification('on_account_created',
                                         email_data={'var1': 'Abhinav',
                                                     'var2': 'Hi!'},
                                         sms_data={'var1': 'Abhi',
                                                   'var2': 'Hello'},
                                         email='',
                                         phone_number='',
                                         send_sms=True,
                                         send_email=True)


def send_commission_transfer(request=False):
    if request:
        test = request.test
    qs = commission_wallet_amount_out_detail_model.objects.filter(input_date__month = month_fn(), input_date__year = year_fn(),
                                                                  instrument_amount_without_comma_style__gt=0)

    for i in qs:
        NoticeTemplate.send_notification('on_account_created',
                                         email_data={'var1': 'Abhinav',
                                                     'var2': 'Hi!'},
                                         sms_data={'var1': 'Abhi',
                                                   'var2': 'Hello'},
                                         email='',
                                         phone_number='',
                                         send_sms=True,
                                         send_email=True)


def send_profile_verification(request=False):
    if request:
        test = request.test
    pass


def send_company_message(request=False):
    if request:
        test = request.test
    pass