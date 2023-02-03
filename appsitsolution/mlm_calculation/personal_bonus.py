from django.shortcuts import render, HttpResponse, get_object_or_404
from datetime import datetime
from .models import *
from .check_permit import check_permission

def personla_bonus_calculation(request):
    # checking if user has permission to view this page
    if not check_permission(request):
        return HttpResponse('<h1>You don\'t have permission to view this page</h1>')

    if request.method == 'POST':
        month_cal = request.POST.get('month', None)
        print(month_cal, '<----------------------------')
        if month_cal != '':
            data = month_cal.split('-')
            year = data[0]
            month = data[1]
            month_cal += '-01'
            super_qs = super_model.objects.last()
            r_users = ReferralCode.objects.filter().order_by('-pk')
            for user in r_users:
                try:
                    bonus = personal_bonus.objects.filter(user = user.user_id,date_model__month=month,
                                                                             date_model__year=year).latest('pk')
                except:
                    repeat_bonus(user.user_id,month,year)

                return_values = repeat_pgpv_pgbv(title.user, pgpv, gpv, pgbv, gbv, month, year)


def repeat_bonus(member,month,year):
    try:
        title = title_qualification_calculation_model.objects.filter(user=member.user_id,
                                                                     date_model__month=month,
                                                                     date_model__year=year).latest('pk')
        bonus = personal_bonus.objects.filter(user = member.user_id,date_model__month=month,
                                                                 date_model__year=year).latest('pk')
    except:
        repeat_bonus(member.user_id,month,year)