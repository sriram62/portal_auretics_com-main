import json
import xlwt
from datetime import datetime, date

from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q

from realtime_calculation.models import RealTimeDetail
from .models import *
from accounts.models import ReferralCode
from .check_permit import check_permission

from django.db.models import Sum

import ast

from portal_auretics_com import settings

audit_mode = False

def check_advisor_qualification(accumulated_pgpv,pgpv,previous_month_title,directors,no_of_legs_with_qualified_director_in_group,cal_qs,infinity_config_qs):
    qualified = 'Blue Advisor'
    fasttrack_advisor_pv = infinity_config_qs.advisor_pv
    fasttrack_director_pv = infinity_config_qs.director_pv
    
    if no_of_legs_with_qualified_director_in_group > 0:
        leg_with_qualified_director_in_group = True
    else:
        leg_with_qualified_director_in_group = False

    if accumulated_pgpv >= cal_qs.associate_advisor_accumulated_pgpv:
        qualified = 'Associate Advisor'
    #Find Fast Track Advisor Qualification:
    if pgpv >= fasttrack_advisor_pv:
        qualified = 'Advisor'
    if accumulated_pgpv >= cal_qs.advisor_accumulated_pgpv:
        qualified = 'Advisor'
    if accumulated_pgpv >= cal_qs.associate_manager_accumulated_pgpv:
        qualified = 'Associate Manager'
    if accumulated_pgpv >= cal_qs.manager_accumulated_pgpv:
        qualified = 'Manager'
    if accumulated_pgpv >= cal_qs.associate_director_accumulated_pgpv:
        qualified = 'Non Qualified Director'

    # If there is a director below this user, then he will atleast become Non-Qualified director
    if directors > 0:
        qualified = 'Non Qualified Director'

    # If user has better Advisor qualification, we will not demote him
    if qualification_levels[previous_month_title] > qualification_levels[qualified]:
        qualified = previous_month_title

    # Find Fast Track Director Qualification:
    if pgpv >= fasttrack_director_pv:
        qualified = 'Associate Director'
        leg_with_qualified_director_in_group = True
        
    

    return qualified, leg_with_qualified_director_in_group


def check_director_qualification(ppv,pgpv,directors,no_of_legs_with_qualified_director_in_group,cal_qs):
    qualified = 'Non Qualified Director'
    
    # [Flow] We are calculating the number of Director legs who have directors anywhere
    directors = no_of_legs_with_qualified_director_in_group
    
    if ppv >= cal_qs.associate_director_ppv and pgpv >= cal_qs.associate_director_pgpv and directors >= cal_qs.associate_director_legs:
        qualified = 'Associate Director'
    if ppv >= cal_qs.bronze_director_ppv and pgpv >= cal_qs.bronze_director_pgpv and directors >= cal_qs.bronze_director_legs:
        qualified = 'Bronze Director'
    if ppv >= cal_qs.silver_director_ppv and pgpv >= cal_qs.silver_director_pgpv and directors >= cal_qs.silver_director_legs:
        qualified = 'Silver Director'
    if ppv >= cal_qs.gold_director_ppv and pgpv >= cal_qs.gold_director_pgpv and directors >= cal_qs.gold_director_legs:
        qualified = 'Gold Director'
    if ppv >= cal_qs.platinum_director_ppv and pgpv >= cal_qs.platinum_director_pgpv and directors >= cal_qs.platinum_director_legs:
        qualified = 'Platinum Director'
    if ppv >= cal_qs.titanium_director_ppv and pgpv >= cal_qs.titanium_director_pgpv and directors >= cal_qs.titanium_director_legs:
        qualified = 'Titanium Director'
    if ppv >= cal_qs.sapphire_director_ppv and pgpv >= cal_qs.sapphire_director_pgpv and directors >= cal_qs.sapphire_director_legs:
        qualified = 'Sapphire Director'
    if ppv >= cal_qs.emerald_director_ppv and pgpv >= cal_qs.emerald_director_pgpv and directors >= cal_qs.emerald_director_legs:
        qualified = 'Emerald Director'
    if ppv >= cal_qs.jade_director_ppv and pgpv >= cal_qs.jade_director_pgpv and directors >= cal_qs.jade_director_legs:
        qualified = 'Jade Director'
    if ppv >= cal_qs.crown_director_ppv and pgpv >= cal_qs.crown_director_pgpv and directors >= cal_qs.crown_director_legs:
        qualified = 'Crown Director'
    if ppv >= cal_qs.diamond_director_ppv and pgpv >= cal_qs.diamond_director_pgpv and directors >= cal_qs.diamond_director_legs:
        qualified = 'Diamond Director'
    if ppv >= cal_qs.black_diamond_director_ppv and pgpv >= cal_qs.black_diamond_director_pgpv and directors >= cal_qs.black_diamond_director_legs:
        qualified = 'Black Diamond Director'
    
    if no_of_legs_with_qualified_director_in_group > 0:
        leg_with_qualified_director_in_group = True
    else:
        leg_with_qualified_director_in_group = False
    
    if "Director" in qualified:
        if qualified != "Non Qualified Director":
            leg_with_qualified_director_in_group = True
        
    return qualified, leg_with_qualified_director_in_group


def check_qualification(accumulated_pgpv, myid, referal_by, pgpv, gpv, ppv, month, year, previous_month_title, cal_qs, infinity_config_qs):
    highest_qualification_ever = "Blue Advisor"
    check_list = ['Associate Manager', 'Manager', ]
    q_or_nq_directors = title_qualification_calculation_model.objects.filter(user__referralcode__referal_by=referal_by, date_model__month=month,
                                                        date_model__year=year, current_month_qualification__contains='Director').count()
    
    directors = title_qualification_calculation_model.objects.filter(user__referralcode__referal_by=referal_by, date_model__month=month,
                                                        date_model__year=year, current_month_qualification__contains='Director').exclude(current_month_qualification='Non Qualified Director').count()
    
    no_of_legs_with_qualified_director_in_group = title_qualification_calculation_model.objects.filter(user__referralcode__referal_by=referal_by, date_model__month=month,
                                                        date_model__year=year, current_month_qualification__contains='Director', is_there_a_qualified_director_in_the_group = True).count()
    
    # advisors  = title_qualification_calculation_model.objects.filter(user__referralcode__referal_by=referal_by, date_model__month=month,
    #                                                     date_model__year=year,current_month_qualification__contains__in = check_list).exclude(current_month_qualification='Blue Advisor').count()
    # cal_qs = configurations.objects.last()
    # infinity_config_qs = infinity_model.objects.last()
    if "Director" not in previous_month_title:
        qualified, leg_with_qualified_director_in_group = check_advisor_qualification(accumulated_pgpv,pgpv,previous_month_title,q_or_nq_directors,no_of_legs_with_qualified_director_in_group,cal_qs,infinity_config_qs)

        if "Director" in qualified:
            qualified, leg_with_qualified_director_in_group = check_director_qualification(ppv,pgpv,directors,no_of_legs_with_qualified_director_in_group,cal_qs)

    else:
        qualified, leg_with_qualified_director_in_group = check_director_qualification(ppv,pgpv,directors,no_of_legs_with_qualified_director_in_group,cal_qs)

    if qualification_levels[previous_month_title] > qualification_levels[qualified]:
        highest_qualification_ever = previous_month_title
    elif qualification_levels[previous_month_title] < qualification_levels[qualified]:
        highest_qualification_ever = qualified
    else:
        highest_qualification_ever = qualified

    # [Commented and Scrapped *1]
    # [Commented and Scrapped *2]
    return qualified, highest_qualification_ever, directors, leg_with_qualified_director_in_group, no_of_legs_with_qualified_director_in_group

qualification_levels =  {
                        'Blue Advisor':1,
                        'Associate Advisor':2,
                        'Advisor':3,
                        'Associate Manager':4,
                        'Manager':5,
                        'Non Qualified Director':6,
                        'Associate Director':7,
                        'Bronze Director':8,
                        'Silver Director':9,
                        'Gold Director':10,
                        'Platinum Director':11,
                        'Titanium Director':12,
                        'Sapphire Director':13,
                        'Emerald Director':14,
                        'Jade Director':15,
                        'Crown Director':16,
                        'Diamond Director':17,
                        'Black Diamond Director':18,
                        }


def pgpv_pgbv(request):
    # checking if user has permission to view this page
    if not check_permission(request):
        return HttpResponse('<h1>You don\'t have permission to view this page</h1>')

    """
    We have to calculate PGBV from PBV & GBV of each user.
    PGBV is the total business done by a user by himself, by his non-director and non qualified director legs.
    We will calculate PGPV, PGBV, Title Qualification and Personal Bonus together in this function.
    Todos are mentioned with the tag [Flow]
    """
    # params = {}
    if request.method == 'POST':
        month_cal = request.POST.get('month', None)
        params_not_passing = do_pgpv_pgbv_calculation(month_cal)
    try:
        public_data = personal_bonus.objects.filter(calculation_stage='Public')
        public_data = public_data.latest('pk')
        public_date = public_data.public_date
        public_month = public_data.input_date
    except:
        public_date = 'There is no data published yet!'
        public_month = False
    try:
        draft_data = personal_bonus.objects.filter(calculation_stage='Draft')
        draft_data = draft_data.latest('pk')
        draft_date = draft_data.draft_date
        draft_month = draft_data.input_date
    except:
        draft_date = 'There is no data draft yet!'
        draft_month = False

    params = {'public_date': public_date,
              'draft_date': draft_date,
              'public_month': public_month,
              'draft_month': draft_month,
              }
    return render(request, 'mlm_calculation/gpv_gbv.html',params)

# [AG]
def get_non_director_downline_pgpv_pgbv(user, downlines, today_date_month, today_date_year,previous_month_title):
    non_director_downline_pgpv = 0
    non_director_downline_pgbv = 0
    
    # [Commented and Scrapped *3]
    # [AG] Alternate Working
    for downline in downlines:
        title_qs = title_qualification_calculation_model.objects.filter(date_model__month=today_date_month,
                                                                     date_model__year=today_date_year,
                                                                     user_id=downline.user_id)[0]

        if "Director" in title_qs.current_month_qualification:
            # if downline_title.current_month_qualification != "Non Qualified Director":
            if "Non" not in title_qs.current_month_qualification:
                continue
            else:
                non_director_downline_pgpv = non_director_downline_pgpv + title_qs.pgpv
                non_director_downline_pgbv = non_director_downline_pgbv + title_qs.pgbv
        else:
            # non_director_downline_pgpv = non_director_downline_pgpv + downline_title.pgpv
            # non_director_downline_pgbv = non_director_downline_pgbv + downline_title.pgbv
            non_director_downline_pgpv = non_director_downline_pgpv + title_qs.pgpv
            non_director_downline_pgbv = non_director_downline_pgbv + title_qs.pgbv

    return non_director_downline_pgpv, non_director_downline_pgbv


def check_downline_exist_leg_count(current_qualification_level, downlines, today_date_month, today_date_year,previous_month_title, cal_qs, infinity_config_qs):
    downline_directors = 0
    downline_title_exist_count = 0
    downline_directors_in_group = 0
    for downline in downlines:

        check_downline_user_title_exist = title_qualification_calculation_model.objects.filter(user=downline.user_id,
                                                                                               date_model__month=today_date_month,
                                                                                               date_model__year=today_date_year)
        if check_downline_user_title_exist.exists():
            check_downline_user_title_exist = check_downline_user_title_exist[0]
            if check_downline_user_title_exist.pgpv_pgbv_calculation_done:
                downline_title_exist_count += 1
                qualify, highest_qualification_ever, director_legs, leg_with_qualified_director_in_group, no_of_legs_with_qualified_director_in_group = check_qualification(check_downline_user_title_exist.accumulated_pgpv,
                                              check_downline_user_title_exist.id,
                                              downline.user_id,
                                              check_downline_user_title_exist.pgpv,
                                              check_downline_user_title_exist.gpv,
                                              check_downline_user_title_exist.ppv,
                                              today_date_month,
                                              today_date_year,
                                              check_downline_user_title_exist.current_month_qualification,
                                              cal_qs,
                                              infinity_config_qs)

                # calculation_obj.current_month_qualification = current_qualification_level
                # calculation_obj.highest_qualification_ever = highest_qualification_ever

                if qualify.find('Director') > 0 and current_qualification_level != 'Non Qualified Director':
                    downline_directors += 1
                if leg_with_qualified_director_in_group == True:
                    downline_directors_in_group += 1
                    
    return downline_directors, downline_directors_in_group, downline_title_exist_count


def personal_data_save(user, calculation_obj, personal_bonus_percent, current_qualification_level,
                       month_cal, today_date, downlines):
    try:
        previous_title_qualification = title_qualification_calculation_model.objects.filter(
            user=user.user_id).exclude(pk=user.user_id.pk).latest('pk')
        previous_accumulated_pgbv = previous_title_qualification.accumulated_pgbv
        previous_accumulated_pgpv = previous_title_qualification.accumulated_pgpv
    except:
        previous_accumulated_pgbv = 0
        previous_accumulated_pgpv = 0

    cal_percent = personal_bonus_percent[current_qualification_level]
    cal_percent = float(cal_percent)
    config_qs = configurations.objects.last()
    
    if (float(config_qs.minimum_monthly_purchase_to_become_active) <= float(calculation_obj.ppv)):
        user_active = True
    else:
        user_active = False
        
    # [Flow] Using Differential Method
    my_personal_bonus = float(calculation_obj.infinity_pbv) * float(cal_percent) / 100
    total_differential_personal_bonus = 0.0
    
    personal_bonus_diff_list = {}
    
    for downline in downlines:
        downline_title_qs = title_qualification_calculation_model.objects.filter(
                                user=downline.user_id, date_model__month = today_date.month, date_model__year = today_date.year).latest('pk')
        personal_bonus_perc_diff = float(cal_percent) - float(personal_bonus_percent[downline_title_qs.highest_qualification_ever])
        if personal_bonus_perc_diff < 0:
            personal_bonus_perc_diff = 0.0
        
        personal_bonus_diff = float(downline_title_qs.pgbv) * personal_bonus_perc_diff / 100
        if audit_mode:
            personal_bonus_diff_list[downline] = str([downline,personal_bonus_perc_diff,personal_bonus_diff])
        
        total_differential_personal_bonus = total_differential_personal_bonus + personal_bonus_diff
        
    personal_bonus_earned = my_personal_bonus + total_differential_personal_bonus
    
    personal_Data = personal_bonus(user=user.user_id, input_date=month_cal, user_active=user_active,
                                   advisor_level=current_qualification_level,
                                   previous_accumulated_pgbv=previous_accumulated_pgbv,
                                   current_month_pgbv=calculation_obj.pgbv, 
                                   my_personal_bonus = my_personal_bonus,
                                   personal_bonus_from_my_personal_group = total_differential_personal_bonus,
                                   personal_bonus_earned = personal_bonus_earned,
                                   audit_personal_bonus_self_perc = cal_percent,
                                   audit_down_personal_bonus_diff = total_differential_personal_bonus,
                                   audit_down_personal_bonus_diff_list = personal_bonus_diff_list
                                   )
    personal_Data.save()


def set_downline_upline_users(user, calculation_obj, personal_bonus_percent,
                              current_qualification_level, month_cal, today_date,
                              previous_month_calculation, uplines, downlines):
    if not previous_month_calculation:
        previous_month_calculation.accumulated_pgpv = 0
        previous_month_calculation.accumulated_pgbv = 0
    upline_title_exist_count = 0
    do_continue = False
    # [Flow] Save PGPV & PGBV for this user
    # calculation_obj.pgpv = calculation_obj.ppv
    # calculation_obj.pgbv = calculation_obj.pbv

    # [Flow] Claculate Personal Bonus and Add details to the database

    personal_data_save(user, calculation_obj, personal_bonus_percent,
                       current_qualification_level,
                       month_cal, today_date, downlines)

    # [Flow] and find out wheather the user is a director

    # [Flow] If the User is a director change pgpv_pgbv_calculation_done as True
    # find his last month accumulated_pgpv & accumulated_pgbv and add it to current month accumulated_pgpv & bv
    # and continue the loop
    if current_qualification_level.find('Director') > 0 and current_qualification_level != 'Non Qualified Director':
        calculation_obj.pgpv_pgbv_calculation_done = True
        calculation_obj.accumulated_pgpv = float(previous_month_calculation.accumulated_pgpv) + float(calculation_obj.accumulated_pgpv)
        calculation_obj.accumulated_pgbv = float(previous_month_calculation.accumulated_pgbv) + float(calculation_obj.accumulated_pgbv)
        calculation_obj.date_model = today_date
        calculation_obj.save()
        do_continue = True

    # [Flow] Else add PGBV of this user to the PGBV of his upline
    elif uplines.exists():
        topline_user = uplines[0].referal_by
        upline_calculaiton_obj = title_qualification_calculation_model.objects.filter(user=topline_user,
                                                                                      date_model__month=today_date.month,
                                                                                      date_model__year=today_date.year)
        if upline_calculaiton_obj.exists():
            upline_title_exist_count += 1
            upline_calculaiton_obj = upline_calculaiton_obj[0]
            upline_calculaiton_obj.pgbv = float(upline_calculaiton_obj.pgbv) + float(calculation_obj.pgbv)
            upline_calculaiton_obj.save()
            # calculation_obj.pgpv_pgbv_calculation_done = True
        calculation_obj.pgpv_pgbv_calculation_done = True
        calculation_obj.accumulated_pgpv = float(previous_month_calculation.accumulated_pgpv) + float(calculation_obj.accumulated_pgpv)
        calculation_obj.accumulated_pgbv = float(previous_month_calculation.accumulated_pgbv) + float(calculation_obj.accumulated_pgbv)
        calculation_obj.date_model = today_date
        calculation_obj.save()
    # [Flow] change pgpv_pgbv_calculation_done as True
    calculation_obj.pgpv_pgbv_calculation_done = True
    return do_continue, calculation_obj


def make_upline_calculation_not_done(uplines, today_date_month, today_date_year):
    upline_users = uplines.values_list('user_id', flat=True)
    title_qualification_calculation_model.objects.filter(user__id__in=upline_users,
                                                         date_model__month=today_date_month,
                                                         date_model__year=today_date_year).update(pgpv_pgbv_calculation_done=False)


list_percent = ['Blue Advisor', 'Associate Advisor',
               'Advisor',
               'Associate Manager',
               'Manager',
               'Associate Director',
               'Non Qualified Director']


def gpv_gbv_pb_excel(request):
    # checking if user has permission to view this page
    if not check_permission(request):
        return HttpResponse('<h1>You don\'t have permission to view this page</h1>')

    if request.method == 'POST':
        month_cal = request.POST.get('excel_date',None)
        if month_cal != '':
            data = month_cal.split('-')
            year = data[0]
            month = data[1]
            month_cal +='-01'
            today_date = datetime.now().date()
            response = HttpResponse(content_type='application/ms-excel')
            response['content-Disposition'] = 'attachment; filename = Personal Bonus' + str(today_date) + '.xls'
            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('Expenses')
            row_num = 0
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            columns = ['pk', 'user', 'ARN', 'Mobile',  'First Name',  'Last Name', 'created_on', 'input_date','calculation_stage','advisory_level', 'previous_accumulated_pgbv',
                       'current_month_pgbv','personal_bonus_level', 'my_personal_bonus', 'personal_bonus_from_my_personal_group',
                       'personal_bonus_earned','personal_bonus_paid', 'personal_bonus_balance_payable',
                       'audit_personal_bonus_self_perc','audit_down_personal_bonus_diff',
                       'draft_date', 'public_date']
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)
            font_style = xlwt.XFStyle()
            rows = personal_bonus.objects.filter(input_date__month = month,input_date__year = year).values_list('pk',
                        'user__username', 'user__referralcode__referral_code', 'user_id__profile__phone_number',  'user_id__profile__first_name',  'user_id__profile__last_name',
                        'created_on', 'input_date','calculation_stage','advisor_level', 'previous_accumulated_pgbv',
                       'current_month_pgbv','personal_bonus_level', 'my_personal_bonus', 'personal_bonus_from_my_personal_group',
                       'personal_bonus_earned','personal_bonus_paid', 'personal_bonus_balance_payable',
                       'audit_personal_bonus_self_perc','audit_down_personal_bonus_diff',
                       'draft_date', 'public_date')
            if len(rows)< 1:
                messages.success(request, 'This month Personal Bonus is not Calculated!')
                return redirect('mlm_calculation_gpb_gbv_pb')
            for row in rows:
                row_num += 1
                counting_sale_type = 0
                for col_num in range(len(row)):
                    ws.write(row_num, col_num, str(row[col_num]), font_style)
            wb.save(response)
            return response
    messages.success(request, 'This month Personal Bonus is not Calculated!')
    return redirect('mlm_calculation_gpb_gbv_pb')

def personal_bonus_publish(request):
    # checking if user has permission to view this page
    if not check_permission(request):
        return HttpResponse('<h1>You don\'t have permission to view this page</h1>')

    if request.method == 'POST':
        month_cal = request.POST.get('publish_date', None)
        if month_cal != '':
            data = month_cal.split('-')
            year = data[0]
            month = data[1]
            month_cal += '-01'
            today_date = datetime.now().date()
            value = personal_bonus.objects.filter(input_date__month=month, input_date__year=year,calculation_stage = 'Draft').exists()
            if value == True:
                data_qs = personal_bonus.objects.filter(input_date__month = month,input_date__year = year ).update(public_date = today_date,
                                                                                                                            calculation_stage = 'Public')
                messages.success(request, str(month_cal) +' ' + 'Data Published Successfully!')
            else:
                messages.success(request, str(month_cal) + ' ' + 'Data Already Published!')

        return redirect('mlm_calculation_gpb_gbv_pb')


def do_pgpv_pgbv_calculation(month_cal=False):
    if not month_cal:
        today_date = date.today()
        month_cal = '{}-{}'.format(today_date.year, today_date.month)
    if month_cal != '':
        data = month_cal.split('-')
        year = data[0]
        month = data[1]
        month_cal += '-01'
        # today_date = date.today()
        # [Flow] making date to same as date calculated
        # today_date.replace(year=int(year), month=int(month)+1, day=1)
        today_date = date(int(year), int(month), 1)

        # [Flow] Delete data if it already exists for the current month.
        delete_personal_bonus = personal_bonus.objects.filter(
            input_date__month=month, input_date__year=year).delete()
        delete_title_qualification = title_qualification_calculation_model.objects.filter(
            date_model__month=month, date_model__year=year).delete()

        configurations_qs = configurations.objects.last()
        cal_qs = configurations.objects.last()
        infinity_config_qs = infinity_model.objects.last()

        # [Flow] Personal Bonus Percentages
        personal_bonus_percent = {'Blue Advisor': 0, 'Associate Advisor': configurations_qs.associate_advisor_percent,
                                  'Advisor': configurations_qs.advisor_percent,
                                  'Associate Manager': configurations_qs.associate_manager_percent,
                                  'Manager': configurations_qs.manager_percent,
                                  'Associate Director': configurations_qs.associate_director_percent,
                                  'Bronze Director': configurations_qs.associate_director_percent,
                                  'Silver Director': configurations_qs.associate_director_percent,
                                  'Gold Director': configurations_qs.associate_director_percent,
                                  'Platinum Director': configurations_qs.associate_director_percent,
                                  'Titanium Director': configurations_qs.associate_director_percent,
                                  'Sapphire Director': configurations_qs.associate_director_percent,
                                  'Emerald Director': configurations_qs.associate_director_percent,
                                  'Jade Director': configurations_qs.associate_director_percent,
                                  'Crown Director': configurations_qs.associate_director_percent,
                                  'Diamond Director': configurations_qs.associate_director_percent,
                                  'Black Diamond Director': configurations_qs.associate_director_percent,
                                  'Non Qualified Director': configurations_qs.associate_director_percent}

        # [Flow] Get all users and start from the bottom most user
        all_users = ReferralCode.objects.filter().order_by('-pk')
        # [Flow] Save this user list in the title qualification table for the current month and year

        run_pgpv_pgbv_loop = True
        today_date_month = today_date.month
        today_date_year = today_date.year
        run_count = 0

        while run_pgpv_pgbv_loop:
            run_pgpv_pgbv_loop = False
            if run_count:
                users = title_qualification_calculation_model.objects.filter(pgpv_pgbv_calculation_done=False,
                                                                             date_model__month=today_date_month,
                                                                             date_model__year=today_date_year).values_list(
                                                                                                                            'user__id',
                                                                                                                            flat=True)
                current_users = all_users.filter(
                    user_id__id__in=users).order_by('-pk')
            else:
                current_users = all_users
            run_count += 1
            for user in current_users:
                # current_qualification_level = "Blue Advisor"
                # highest_qualification_ever  = "Blue Advisor"
                previous_month_calculation = None
                calculation_obj = title_qualification_calculation_model.objects.filter(user=user.user_id,
                                                                                       date_model__month=today_date_month,
                                                                                       date_model__year=today_date_year)
                if calculation_obj.exists():
                    calculation_obj = calculation_obj[0]
                else:
                    calculation_obj = title_qualification_calculation_model(
                        user=user.user_id)
                    calculation_obj.date_model = today_date
                    calculation_obj.save()

                # [AG]
                previous_month_calculation = title_qualification_calculation_model.objects.filter(user=user.user_id). \
                    exclude(id=calculation_obj.id).order_by(
                    '-date_model')

                # [Flow] If value of accumulated_ppv, accumulated_pbv, accumulated_gpv, accumulated_gbv is 0.0 in user's current month row
                # Then value of add current month ppv, pbv, gpv & gbv to the accumulated value of last time. (Try except required)

                # '''
                #                     if (not calculation_obj.accumulated_ppv and not calculation_obj.accumulated_pbv and not
                #                         calculation_obj.accumulated_gpv and not calculation_obj.accumulated_gbv):
                #                         '''
                # previous_month_calculation = title_qualification_calculation_model.objects.filter(user=user.user_id).\
                #                                 exclude(id=calculation_obj.id).order_by('-date_model')

                # [Flow] If value of super_ppv, super_pbv, infinity_ppv, infinity_pbv is 0.0 in user's current month row
                # Then value of add current month super_ppv, super_pbv, infinity_ppv, infinity_pbv from realtime calculation. (Try except required)
                realtime_detail = RealTimeDetail.objects.filter(user_id__id=user.user_id.id,
                                                                date__month=today_date_month,
                                                                date__year=today_date_year)
                if (not calculation_obj.super_ppv or not calculation_obj.super_pbv or not
                calculation_obj.infinity_ppv or not calculation_obj.infinity_pbv):
                    # realtime_detail = RealTimeDetail.objects.filter(user_id__id=user.user_id.id,
                    #                                                 date__month=today_date_month,
                    #                                                 date__year=today_date_year)
                    # try:
                    if realtime_detail.exists():
                        realtime_detail = realtime_detail[0]
                        calculation_obj.super_ppv = realtime_detail.rt_user_super_ppv
                        calculation_obj.super_pbv = realtime_detail.rt_user_super_pbv
                        calculation_obj.infinity_ppv = realtime_detail.rt_user_infinity_ppv
                        calculation_obj.infinity_pbv = realtime_detail.rt_user_infinity_pbv
                        calculation_obj.gbv = realtime_detail.rt_gbv_month
                        calculation_obj.tbv = realtime_detail.rt_tbv_month
                        calculation_obj.tpv = realtime_detail.rt_tpv_month


                    # except:
                    #     try:
                    #         calculation_obj.super_ppv = realtime_detail.rt_user_super_ppv
                    #         calculation_obj.super_pbv = realtime_detail.rt_user_super_pbv
                    #         calculation_obj.infinity_ppv = realtime_detail.rt_user_infinity_ppv
                    #         calculation_obj.infinity_pbv = realtime_detail.rt_user_infinity_pbv
                    #         calculation_obj.tbv = realtime_detail.rt_tbv_month
                    #         calculation_obj.tpv = realtime_detail.rt_tpv_month
                    #     except:
                    #         pass
                    #         # calculation_obj.super_ppv = 0
                    #         # calculation_obj.super_pbv = 0
                    #         # calculation_obj.infinity_ppv = 0
                    #         # calculation_obj.infinity_pbv = 0

                try:
                    if realtime_detail.exists():
                        realtime_detail = realtime_detail[0]
                        calculation_obj.ppv = realtime_detail.rt_user_infinity_ppv
                        calculation_obj.pbv = realtime_detail.rt_user_infinity_pbv
                        if realtime_detail.rt_is_user_green == True:
                            calculation_obj.is_user_green = True
                except:
                    calculation_obj.ppv = realtime_detail.rt_user_infinity_ppv
                    calculation_obj.pbv = realtime_detail.rt_user_infinity_pbv

                if previous_month_calculation.exists():
                    previous_month_calculation = previous_month_calculation[0]
                    calculation_obj.accumulated_ppv = float(
                        previous_month_calculation.accumulated_ppv) + float(calculation_obj.ppv)
                    calculation_obj.accumulated_pbv = float(
                        previous_month_calculation.accumulated_pbv) + float(calculation_obj.pbv)
                    calculation_obj.accumulated_gpv = float(
                        previous_month_calculation.accumulated_gpv) + float(calculation_obj.gpv)
                    calculation_obj.accumulated_gbv = float(
                        previous_month_calculation.accumulated_gbv) + float(calculation_obj.gbv)
                    calculation_obj.accumulated_tbv = float(
                        previous_month_calculation.accumulated_tbv) + float(calculation_obj.tbv)
                    calculation_obj.accumulated_tpv = float(
                        previous_month_calculation.accumulated_tpv) + float(calculation_obj.tpv)
                    calculation_obj.accumulated_pgpv = float(
                        previous_month_calculation.accumulated_pgpv) + float(calculation_obj.ppv)
                    calculation_obj.accumulated_pgbv = float(
                        previous_month_calculation.accumulated_pgbv) + float(calculation_obj.pbv)
                    previous_month_title = previous_month_calculation.highest_qualification_ever
                    if previous_month_calculation.is_user_green == True:
                        calculation_obj.is_user_green = True
                else:
                    calculation_obj.accumulated_ppv = float(calculation_obj.ppv)
                    calculation_obj.accumulated_pbv = float(calculation_obj.pbv)
                    calculation_obj.accumulated_gpv = float(calculation_obj.gpv)
                    calculation_obj.accumulated_gbv = float(calculation_obj.gbv)
                    calculation_obj.accumulated_tbv = float(calculation_obj.tbv)
                    calculation_obj.accumulated_pgpv = float(calculation_obj.ppv)
                    calculation_obj.accumulated_pgbv = float(calculation_obj.pbv)
                    previous_month_title = "Blue Advisor"

                downlines = ReferralCode.objects.filter(
                    referal_by=user.user_id)
                uplines = ReferralCode.objects.filter(
                    user_id=user.user_id, referal_by__isnull=False).order_by('-created_on')[:1]

                # [Flow] If pgpv_pgbv_calculation_done is True then continue
                if calculation_obj.pgpv_pgbv_calculation_done:
                    calculation_obj.date_model = today_date
                    calculation_obj.save()
                    continue

                # [Flow] Else, we will calculate further
                else:
                    # [Flow] For All Users, Initially, Their PGPV = PPV, PGBV = PBV
                    calculation_obj.pgpv = calculation_obj.ppv
                    calculation_obj.pgbv = calculation_obj.pbv
                    calculation_obj.date_model = today_date
                    calculation_obj.save()

                    # [Flow] Find out the current month qualification of the user using the function check_qualification
                    current_qualification_level, highest_qualification_ever, director_legs, leg_with_qualified_director_in_group, no_of_legs_with_qualified_director_in_group = check_qualification(
                        calculation_obj.accumulated_pgpv,
                        calculation_obj.id,
                        user.user_id,
                        calculation_obj.pgpv,
                        calculation_obj.gpv,
                        calculation_obj.ppv,
                        today_date_month,
                        today_date_year,
                        previous_month_title,
                        cal_qs,
                        infinity_config_qs
                        )

                    calculation_obj.current_month_qualification = current_qualification_level
                    calculation_obj.highest_qualification_ever = highest_qualification_ever
                    calculation_obj.no_of_director_legs = no_of_legs_with_qualified_director_in_group
                    calculation_obj.is_there_a_qualified_director_in_the_group = leg_with_qualified_director_in_group
                    calculation_obj.date_model = today_date
                    calculation_obj.save()

                    # [Flow] If the user has no downline (i.e not referred anyone)
                    if not downlines.exists():
                        # [Flow] Find out the current month qualification of the user using the function check_qualification
                        current_qualification_level, highest_qualification_ever, director_legs, leg_with_qualified_director_in_group, no_of_legs_with_qualified_director_in_group = check_qualification(
                            calculation_obj.accumulated_pgpv,
                            calculation_obj.id,
                            user.user_id,
                            calculation_obj.pgpv,
                            calculation_obj.gpv,
                            calculation_obj.ppv,
                            today_date_month,
                            today_date_year,
                            previous_month_title,
                            cal_qs,
                            infinity_config_qs)

                        calculation_obj.current_month_qualification = current_qualification_level
                        calculation_obj.highest_qualification_ever = highest_qualification_ever
                        calculation_obj.no_of_director_legs = no_of_legs_with_qualified_director_in_group
                        calculation_obj.is_there_a_qualified_director_in_the_group = leg_with_qualified_director_in_group
                        calculation_obj.date_model = today_date
                        calculation_obj.save()
                        # [Flow] Save PGPV & PGBV for this user
                        # calculation_obj.pgpv = calculation_obj.ppv
                        # calculation_obj.pgbv = calculation_obj.pbv

                        do_continue, calculation_obj = set_downline_upline_users(user,
                                                                                 calculation_obj,
                                                                                 personal_bonus_percent,
                                                                                 current_qualification_level,
                                                                                 month_cal,
                                                                                 today_date,
                                                                                 previous_month_calculation,
                                                                                 uplines,
                                                                                 downlines)

                        if do_continue:
                            calculation_obj.date_model = today_date
                            calculation_obj.save()
                            continue

                        # [Commented and Scrapped *4]
                        
                    # [Flow] If the user has downline (i.e if he has referred anyone)
                    # [AG] Added else and indented to form it within if else of downlines.exists()
                    # if downlines.exists():
                    else:

                        # [Flow] Check if the calculation is done for the downline
                        downline_directors, downline_directors_in_group, downline_title_exist_count = check_downline_exist_leg_count(
                            current_qualification_level,
                            downlines,
                            today_date_month,
                            today_date_year,
                            previous_month_title,
                            cal_qs,
                            infinity_config_qs)
                            
                        # [Flow] If calculation is done for everyone in the downline
                        if downline_title_exist_count == len(downlines):
                            # [Flow] Save PGPV & PGBV for this user
                            calculation_obj.date_model = today_date
                            calculation_obj.no_of_director_legs = downline_directors_in_group
                            calculation_obj.save()
                            non_director_downline_pgpv, non_director_downline_pgbv = get_non_director_downline_pgpv_pgbv(
                                user,
                                downlines,
                                today_date_month,
                                today_date_year,
                                previous_month_title)

                            calculation_obj.pgpv = float(non_director_downline_pgpv) + float(calculation_obj.ppv)
                            calculation_obj.pgbv = float(non_director_downline_pgbv) + float(calculation_obj.pbv)
                            try:
                                if previous_month_calculation.exists():
                                    previous_month_calculation = previous_month_calculation[0]
                                    calculation_obj.accumulated_pgpv = float(
                                        previous_month_calculation.accumulated_pgpv) + float(calculation_obj.pgpv)
                                    calculation_obj.accumulated_pgbv = float(
                                        previous_month_calculation.accumulated_pgbv) + float(calculation_obj.pgbv)
                                else:
                                    calculation_obj.accumulated_pgpv = float(calculation_obj.ppv)
                                    calculation_obj.accumulated_pgbv = float(calculation_obj.pbv)
                            except:
                                calculation_obj.accumulated_pgpv = float(
                                    previous_month_calculation.accumulated_pgpv) + float(calculation_obj.pgpv)
                                calculation_obj.accumulated_pgbv = float(
                                    previous_month_calculation.accumulated_pgbv) + float(calculation_obj.pgbv)
                            calculation_obj.date_model = today_date
                            calculation_obj.save()

                            # [Flow] Find out the current month qualification of the user using the function check_qualification
                            current_qualification_level, highest_qualification_ever, director_legs, leg_with_qualified_director_in_group, no_of_legs_with_qualified_director_in_group = check_qualification(
                                calculation_obj.accumulated_pgpv,
                                calculation_obj.id,
                                user.user_id,
                                calculation_obj.pgpv,
                                calculation_obj.gpv,
                                calculation_obj.ppv,
                                today_date_month,
                                today_date_year,
                                previous_month_title,
                                cal_qs,
                                infinity_config_qs)

                            calculation_obj.current_month_qualification = current_qualification_level
                            calculation_obj.highest_qualification_ever = highest_qualification_ever
                            calculation_obj.no_of_director_legs = no_of_legs_with_qualified_director_in_group
                            calculation_obj.is_there_a_qualified_director_in_the_group = leg_with_qualified_director_in_group
                            calculation_obj.date_model = today_date
                            calculation_obj.save()

                            do_continue, calculation_obj = set_downline_upline_users(user,
                                                                                     calculation_obj,
                                                                                     personal_bonus_percent,
                                                                                     current_qualification_level,
                                                                                     month_cal,
                                                                                     today_date,
                                                                                     previous_month_calculation,
                                                                                     uplines, downlines)

                            # [Commented and Scrapped *5]
                            
                        # [Flow] Else if any of the downline calculation is pending.
                        # We will have re-perform pgbv & pgpv calculation after this lot.
                        # Mark pgpv_pgbv_calculation_done as False for this user and this upline as well.
                        if downline_title_exist_count != len(downlines):
                            calculation_obj.pgpv_pgbv_calculation_done = False

                            make_upline_calculation_not_done(uplines, today_date_month, today_date_year)

                            run_pgpv_pgbv_loop = True
                            calculation_obj.date_model = today_date
                            calculation_obj.save()

                            # [Flow] and We will continue the loop (i.e. we will not make a decision to find out director qualification or to roll-up or not for this user)
                            continue

                    # [Flow] find this user's last month accumulated_pgpv & accumulated_pgbv and add it to current month accumulated_pgpv & bv
                    # and continue the loop
                    if previous_month_calculation:
                        calculation_obj.accumulated_pgpv = float(
                            calculation_obj.pgpv) + float(previous_month_calculation.accumulated_pgpv)
                        calculation_obj.accumulated_pgbv = float(
                            calculation_obj.pgbv) + float(previous_month_calculation.accumulated_pgbv)
                        calculation_obj.date_model = today_date
                        calculation_obj.save()
                        continue
                    calculation_obj.date_model = today_date
                    calculation_obj.save()

                # [Commented and Scrapped *6]


    try:
        public_data = personal_bonus.objects.filter(calculation_stage='Public')
        public_data = public_data.latest('pk')
        public_date = public_data.public_date
        public_month = public_data.input_date
    except:
        public_date = 'There is no data published yet!'
        public_month = False
    try:
        draft_data = personal_bonus.objects.filter(calculation_stage='Draft')
        draft_data = draft_data.latest('pk')
        draft_date = draft_data.draft_date
        draft_month = draft_data.input_date
    except:
        draft_date = 'There is no data draft yet!'
        draft_month = False

    params = {'public_date': public_date,
              'draft_date': draft_date,
              'public_month': public_month,
              'draft_month': draft_month
              }
    return params
    










# [Commented and Scrapped *1]
    # print("qualification_levels[previous_month_title]")
    # print(qualification_levels[previous_month_title])
    # print("qualification_levels[qualified]")
    # print(qualification_levels[qualified])
    # print("previous_month_title")
    # print(previous_month_title)
    # print("highest_qualification_ever")
    # print(highest_qualification_ever)
    # print("qualified")
    # print(qualified)
    # # [AG]
    # print("Check Function Inputs are:")
    # print("accumulated_pgpv")
    # print(accumulated_pgpv)
    # print("myid")
    # print(myid)
    # print("referal_by")
    # print(referal_by)
    # print("pgpv")
    # print(pgpv)
    # print("gpv")
    # print(gpv)
    # print("ppv")
    # print(ppv)
    # print("month")
    # print(month)
    # print("year")
    # print(year)
    # print("no_of_legs_with_qualified_director_in_group")
    # print(no_of_legs_with_qualified_director_in_group)

# [Commented and Scrapped *2]
    # print("Check Qualification Variables are:")
    # print(configurations.objects.last())
    # print(cal_qs.associate_advisor_accumulated_pgpv)
    # print(cal_qs.advisor_accumulated_pgpv)
    # print(cal_qs.associate_manager_accumulated_pgpv)
    # print(cal_qs.manager_accumulated_pgpv)
    # print(cal_qs.associate_director_accumulated_pgpv)
    # print(cal_qs.associate_director_ppv)
    # print(cal_qs.associate_director_pgpv)
    # print(cal_qs.associate_director_legs)
    # print(cal_qs.bronze_director_ppv)
    # print(cal_qs.bronze_director_pgpv)
    # print(cal_qs.bronze_director_legs)
    # print(cal_qs.silver_director_ppv)
    # print(cal_qs.silver_director_pgpv)
    # print(cal_qs.silver_director_legs)
    # print(cal_qs.gold_director_ppv)
    # print(cal_qs.gold_director_pgpv)
    # print(cal_qs.gold_director_legs)
    # print(cal_qs.platinum_director_ppv)
    # print(cal_qs.platinum_director_pgpv)
    # print(cal_qs.platinum_director_legs)
    # print(cal_qs.titanium_director_ppv)
    # print(cal_qs.titanium_director_pgpv)
    # print(cal_qs.titanium_director_legs)
    # print(cal_qs.sapphire_director_ppv)
    # print(cal_qs.sapphire_director_pgpv)
    # print(cal_qs.sapphire_director_legs)
    # print(cal_qs.emerald_director_ppv)
    # print(cal_qs.emerald_director_pgpv)
    # print(cal_qs.emerald_director_legs)
    # print(cal_qs.jade_director_ppv)
    # print(cal_qs.jade_director_pgpv)
    # print(cal_qs.jade_director_legs)
    # print(cal_qs.crown_director_ppv)
    # print(cal_qs.crown_director_pgpv)
    # print(cal_qs.crown_director_legs)
    # print(cal_qs.diamond_director_ppv)
    # print(cal_qs.diamond_director_pgpv)
    # print(cal_qs.diamond_director_legs)
    # print(cal_qs.black_diamond_director_ppv)
    # print(cal_qs.black_diamond_director_pgpv)
    # print(cal_qs.black_diamond_director_legs)
    
# [Commented and Scrapped *3]
    # # users = title_qualification_calculation_model.objects.filter(pgpv_pgbv_calculation_done=False,
    # #                                                              date_model__month=today_date_month,
    # #                                                              date_model__year=today_date_year).values_list('user__id',
    # #                                                                                                        flat=True)
    # # current_users = all_users.filter(
    # #     user_id__id__in=users).order_by('-pk')
    # # [AG] Old Working
    # downlines_title = title_qualification_calculation_model.objects.filter(pgpv_pgbv_calculation_done=True,
    #                                                              date_model__month=today_date_month,
    #                                                              date_model__year=today_date_year,
    #                                                              user_id__id__in=downlines)
    # print(downlines_title)
    # # if downlines_title.exists():
    # for downline_title in downlines_title:
    #     print(downline_title.user)
    #     print(downline_title.current_month_qualification)
    #     print("Downlines")
    #     # if downline_title.current_month_qualification.find('Director') > 0:
    #     #     if downline_title.current_month_qualification != 'Non Qualified Director':
    #     #         print("Inside If")
    #     #         continue
    

# [Commented and Scrapped *4]
    # """# [Flow] Claculate Personal Bonus and Add details to the database
    # personal_data_save(user, calculation_obj, personal_bonus_percent,
    #                    current_qualification_level,
    #                    month_cal, today_date)
    # 
    # # [Flow] and find out wheather the user is a director
    # 
    # 
    # # [Flow] If the User is a director change pgpv_pgbv_calculation_done as True
    # # find his last month accumulated_pgpv & accumulated_pgbv and add it to current month accumulated_pgpv & bv
    # # and continue the loop
    # if current_qualification_level.find('Director') > 0 and current_qualification_level != 'Non Qualified Director':
    #      calculation_obj.pgpv_pgbv_calculation_done = True
    #      calculation_obj.accumulated_pgpv = previous_month_calculation.accumulated_pgpv + \
    #          calculation_obj.accumulated_pgpv
    #      calculation_obj.accumulated_pgbv = previous_month_calculation.accumulated_pgbv + \
    #          calculation_obj.accumulated_pgbv
    #      calculation_obj.save()
    #      continue
    # 
    # # [Flow] Else add PGBV of this user to the PGBV of his upline
    # elif uplines.exists():
    #     topline_user = uplines[0].referal_by
    #     upline_calculaiton_obj = title_qualification_calculation_model.objects.filter(user=topline_user,
    #                                                          date_model__month=today_date_month,
    #                                                          date_model__year=today_date_year)
    #     if upline_calculaiton_obj.exists():
    #         upline_title_exist_count += 1
    #         upline_calculaiton_obj = upline_calculaiton_obj[0]
    #         upline_calculaiton_obj.pgbv = upline_calculaiton_obj.pgbv + calculation_obj.pgbv
    #         upline_calculaiton_obj.save()
    #         #calculation_obj.pgpv_pgbv_calculation_done = True
    #     calculation_obj.pgpv_pgbv_calculation_done = True
    #     calculation_obj.accumulated_pgpv = previous_month_calculation.accumulated_pgpv + \
    #         calculation_obj.accumulated_pgpv
    #     calculation_obj.accumulated_pgbv = previous_month_calculation.accumulated_pgbv + \
    #         calculation_obj.accumulated_pgbv
    #     calculation_obj.save()
    # # [Flow] change pgpv_pgbv_calculation_done as True
    # calculation_obj.pgpv_pgbv_calculation_done = True
    # """
    
    
# [Commented and Scrapped *5]
    # """
    # # [Flow] Calculate Personal Bonus and Add details to the database
    # personal_data_save(user, calculation_obj, personal_bonus_percent,
    #                    current_qualification_level,
    #                    month_cal, today_date)
    # 
    # # [Flow] Find No. of directors in his downline and save it in no_of_director_legs
    # downline_directors, downline_title_exist_count = check_downline_exist_leg_count(user, current_qualification_level,
    #                                                                                 downlines, today_date_month, today_date_year)
    # calculation_obj.no_of_director_legs = downline_directors
    # # [Flow] and find out wheather the user is a director
    # if current_qualification_level.find('Director') > 0 and current_qualification_level != 'Non Qualified Director':
    #     # [Flow] If the User is a director change pgpv_pgbv_calculation_done as True
    #     # find his last month accumulated_pgpv & accumulated_pgbv and add it to current month accumulated_pgpv & bv
    #     # and continue the loop
    #     calculation_obj.pgpv_pgbv_calculation_done = True
    #     calculation_obj.accumulated_pgpv = previous_month_calculation.accumulated_pgpv + \
    #         calculation_obj.accumulated_pgpv
    #     calculation_obj.accumulated_pgbv = previous_month_calculation.accumulated_pgbv + \
    #         calculation_obj.accumulated_pgbv
    #     calculation_obj.save()
    #     continue
    # 
    # # [Flow] Else add PGBV of this user to the PGBV of his upline
    # elif uplines.exists():
    #     topline_user = uplines[0].referal_by
    #     upline_calculaiton_obj = title_qualification_calculation_model.objects.filter(
    #         user=topline_user,
    #         date_model__month=today_date_month,
    #         date_model__year=today_date_year)
    #     if upline_calculaiton_obj.exists():
    #         upline_title_exist_count += 1
    #         upline_calculaiton_obj = upline_calculaiton_obj[0]
    #         upline_calculaiton_obj.pgbv = upline_calculaiton_obj.pgbv + calculation_obj.pgbv
    #         upline_calculaiton_obj.save()
    #         calculation_obj.pgpv_pgbv_calculation_done = True
    #     calculation_obj.pgpv_pgbv_calculation_done = True
    #     calculation_obj.accumulated_pgpv = previous_month_calculation.accumulated_pgpv + \
    #         calculation_obj.accumulated_pgpv
    #     calculation_obj.accumulated_pgbv = previous_month_calculation.accumulated_pgbv + \
    #         calculation_obj.accumulated_pgbv
    #     calculation_obj.save()
    # # [Flow] change pgpv_pgbv_calculation_done as True
    # """
    

# [Commented and Scrapped *6]
# title = title_qualification_calculation_model.objects.filter(user=user.user_id,
#                                                          date_model__month=month,
#                                                          date_model__year=year).latest('pk')
# here if the  title qualifications calculation is done not done properly in that case we will perform the if(condiction) task
# if title.calculation  == False:
#     ppv = 0
#     pgpv = 0
#     gpv = 0
#     pbv = 0
#     pgbv = 0
#     gbv = 0
#     return_values = repeat_pgpv_pgbv(title.user,pgpv,gpv,pgbv,gbv,month,year,month_cal,dic_percent,today_date)
#     send_ppv = title.ppv
#     send_pgpv = return_values[1] + title.ppv
#     send_gpv = return_values[0] + title.ppv
#     send_pbv = title.pbv
#     send_pgbv = return_values[3] + title.pbv
#     send_gbv = return_values[2] +  title.pbv
#     accumulated_ppv = title.accumulated_ppv
#     myid = title.pk
#     referal_by = title.user
#     current_qualification = check_qualification(accumulated_ppv,myid,referal_by,send_pgpv,send_gpv, send_ppv, month, year)
#     try:
#         last_month_data = title_qualification_calculation_model.objects.filter(user = title.user).exclude(pk = title.pk).latest('pk')
#         last_current_qualification = last_month_data.current_month_qualification
#         last_highest_qualification = last_month_data.highest_qualification_ever
#     except:
#         last_current_qualification = 'Blue Advisor'
#         last_highest_qualification = 'Blue Advisor'
#     datas = check_actual_qualification(last_current_qualification,last_highest_qualification,current_qualification)
#     save_qs = title_qualification_calculation_model.objects.filter(pk=title.pk).update(pgpv=send_pgpv,gpv = send_gpv,pgbv = send_pgbv,
#                                                                                        gbv = send_gbv,
#                                                                                        calculation = True,
#                                                                                        current_month_qualification = datas[2],
#                                                                                        highest_qualification_ever = datas[1])
#     print(save_qs)
#     try:
#         previous_title_qualification = title_qualification_calculation_model.objects.filter(user=title.user).exclude(pk = title.pk).latest('pk')
#         previous_accumulated_pgbv = previous_title_qualification.accumulated_pbv
#     except:
#         previous_accumulated_pgbv = 0
#     current_qualification_level = title.current_month_qualification
#     cal_percent = dic_percent[current_qualification_level]
#     cal_percent = float(cal_percent)
#     # title.accumulated_pgbv - send_q
#     config_qs = configurations.objects.last()
#     if (float(config_qs.minimum_monthly_purchase_to_become_active) <=  float(title.ppv)):
#         user_active = True
#     else:
#         user_active = False
#     my_personal_bonus = float(send_pbv)*float(cal_percent)/100
#
#     personal_Data = personal_bonus(user = title.user,input_date = month_cal,user_active = user_active,draft_date = today_date,
#                    advisory_level = current_qualification_level,previous_accumulated_pgbv = previous_accumulated_pgbv,
#                    current_month_pgbv = send_pgbv,my_personal_bonus = my_personal_bonus,)
#     personal_Data.save()