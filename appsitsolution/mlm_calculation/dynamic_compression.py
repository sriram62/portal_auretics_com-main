from django.utils.timezone import activate
from .models import *
from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from django.contrib import messages
import json
import xlwt
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from realtime_calculation.models import RealTimeDetail
import time
from datetime import datetime, date
from asgiref.sync import sync_to_async
from .check_permit import check_permission

qualified_director_title = [
    'Associate Director',
    'Bronze Director',
    'Silver Director',
    'Gold Director',
    'Platinum Director',
    'Titanium Director',
    'Sapphire Director',
    'Emerald Director',
    'Jade Director',
    'Crown Director',
    'Diamond Director',
    'Black Diamond Director',
]


def check_top_user(dynamic_comp_active, dynamic_user):
    # print(F"\ndynamic_user {dynamic_user.user}\n")
    # [Flow] Getting referral of current user
    dynamic_user_ref = dynamic_user.referral
    isFound = False
    while(not isFound):
        # [Flow] Checking if user have referral
        if dynamic_user_ref:
            try:
                referral_user = dynamic_comp_active.get(user=dynamic_user_ref)
                # [Flow] Getting referral status if it is True than assigning to current user
                if(referral_user.user_active):
                    isFound = True
                    dynamic_user.referral = referral_user.user
                    dynamic_user.save()
                    break
                else:
                    # [Flow] If current user referral is inactive than changing current referral
                    # to referral's referral
                    dynamic_user_ref = referral_user.referral
                    # [Flow] If referral don't have referral than passing flow to next user
                    if not dynamic_user_ref:
                        dynamic_user.referral = referral_user.user
                        dynamic_user.save()
                        break
            except Exception as err:
                print(F"\nError : {err}\n")
                pass
        else:
            # [Flow] If user don't have referral than it's first user
            dynamic_user_ref = None
            break


def get_active_user(dynamic_comp_active, month, year, cm_ppv):
    print("Dynamic Compression Active User")
    rt_detail = RealTimeDetail.objects.filter(
        date__month=month, date__year=year).values('user_id', 'rt_ppv')
    # [Flow] Changing active status based on rt_ppv value
    for i in range(rt_detail.count()):
        user = rt_detail[i]['user_id']
        if cm_ppv <= rt_detail[i]['rt_ppv']:
            try:
                active_user = dynamic_comp_active.get(user__id=user)
                active_user.user_active = True
                active_user.save()
            except:
                pass

    for item in dynamic_comp_active.reverse():
        # [Flow] Calling function to change referrals
        check_top_user(dynamic_comp_active, item)

def get_qualified_directors(dynamic_comp_director, month, year):
    print("Dynamic Compression Director")
    for dynamic_user in dynamic_comp_director:
        if dynamic_user.referral:
            try:
                dynamic_user_title_qualification = title_qualification_calculation_model.objects.get(
                    user=dynamic_user.user,
                    date_model__month=month,
                    date_model__year=year)
                dynamic_user_title_qualification_qualification = dynamic_user_title_qualification.current_month_qualification
            except ObjectDoesNotExist:
                dynamic_user_title_qualification_qualification = 'Blue Advisor'

            # [Flow] Changing active status based on current_month_qualification value
            if dynamic_user_title_qualification_qualification in qualified_director_title:
                dynamic_user.user_active = True
                dynamic_user.save()
    
    # [Flow] Calling function to change referrals
    for item in dynamic_comp_director.reverse():
        check_top_user(dynamic_comp_director, item)

def get_users_tbb(dynamic_comp_tbb, month, year):
    print("Dynamic Compression TBB")
    for dynamic_user in dynamic_comp_tbb:
        if dynamic_user.referral:
            try:
                dynamic_user_tbb_earned = team_building_bonus_super_plan_model.objects.get(user=dynamic_user.user,
                                                                                           input_date__month=month,
                                                                                           input_date__year=year,).team_building_bonus_earned
            except ObjectDoesNotExist:
                dynamic_user_tbb_earned = 0

            # [Flow] Changing active status based on team_building_bonus_earned value
            if dynamic_user_tbb_earned > 0:
                dynamic_user.user_active = True
                dynamic_user.save()

    # [Flow] Calling function to change referrals
    for item in dynamic_comp_tbb.reverse():
        check_top_user(dynamic_comp_tbb, item)


@csrf_exempt
def dynamic_compression_user(request):
    # checking if user has permission to view this page
    if not check_permission(request):
        return HttpResponse('<h1>You don\'t have permission to view this page</h1>')

    start_time = time.time()
    """
    Dynamic Compression compresses inactive users / non-qualified directors / users who have not earned TBB.
    Note: Run Dynamic Compression only after calculating PGBV (Title Qualification) and TBB.
    Todo are mentioned with the tag [Flow]
    """
    params = {}
    if request.method == 'POST':
        month_cal = request.POST.get('month', None)
        print(month_cal, '<----------------------------')
        if month_cal != '':
            data = month_cal.split('-')
            year = data[0]
            month = data[1]
            month_cal += '-01'
            # today_date = datetime.now().date()
            today_date = date(int(year), int(month), 1)
            print(month)
            print(year)

            # [Flow] Delete data if it already exists for the current month.
            dynamic_compression_active.objects.filter(input_date__month=month,
                                                      input_date__year=year).delete()

            dynamic_compression_director.objects.filter(input_date__month=month,
                                                        input_date__year=year).delete()

            dynamic_compression_tbb.objects.filter(input_date__month=month,
                                                   input_date__year=year).delete()

            super_qs = super_model.objects.last()

            configure_qs = configurations.objects.last()

            # [Flow] Copy Referral Code Table.
            tbl_users = ReferralCode.objects.all().order_by('-pk')

            # [Flow] and paste to dynamic_compression_active table and dynamic_compression_director table for this month.
            # [Flow] Get Title Qualification Model.
            # qlf_qs = title_qualification.values(
            #     "user_id", "ppv", "current_month_qualification").order_by('-user_id')

            cm_ppv = configurations.objects.values_list(
                'minimum_monthly_purchase_to_become_active', flat=True)[0]

            for user in tbl_users:
                dynamic_compression_active.objects.create(
                    user=user.user_id,
                    referral=user.referal_by,
                    input_date=today_date,
                )

                dynamic_compression_director.objects.create(
                    user=user.user_id,
                    referral=user.referal_by,
                    input_date=today_date,
                )

                dynamic_compression_tbb.objects.create(
                    user=user.user_id,
                    referral=user.referal_by,
                    input_date=today_date,
                )

            dynamic_comp_active = dynamic_compression_active.objects.filter(
                input_date__month=month,
                input_date__year=year,
            ).order_by('-pk')

            dynamic_comp_director = dynamic_compression_director.objects.filter(
                input_date__month=month,
                input_date__year=year,
            ).order_by('-pk')

            dynamic_comp_tbb = dynamic_compression_tbb.objects.filter(
                input_date__month=month,
                input_date__year=year,
            ).order_by('-pk')

            # [Flow] Iterate user one by one

            # [Flow] Dynamic Compression Active
            get_active_user(dynamic_comp_active, month, year, cm_ppv)

            # [Flow] Checking Qualified Directors
            get_qualified_directors(dynamic_comp_director,
                                    month, year)

            # # [Flow] Checking TBB Earned
            get_users_tbb(dynamic_comp_tbb, month, year)

    try:
        public_data = dynamic_compression_active.objects.filter(
            calculation_stage='Public')
        public_data = public_data.latest('pk')
        public_date = public_data.public_date
        public_month = public_data.input_date
    except:
        public_date = 'There is no data publish yet!'
        public_month = False
    try:
        draft_data = dynamic_compression_active.objects.filter(
            calculation_stage='Draft')
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
    print(f'------{time.time() - start_time} seconds--------')

    return render(request, 'mlm_calculation/dynamic_compression_user.html', params)


def removing_brkt(level):
    level = list(level)
    level = str(level)
    level = level.replace('[', '')
    level = level.replace(']', '')
    return level


def dynamic_compression_user_excel(request):
    # checking if user has permission to view this page
    if not check_permission(request):
        return HttpResponse('<h1>You don\'t have permission to view this page</h1>')

    if request.method == 'POST':
        month_cal = request.POST.get('excel_date', None)
        print(month_cal, '<----------------------------')
        if month_cal != '':
            data = month_cal.split('-')
            year = data[0]
            month = data[1]
            month_cal += '-01'
            today_date = datetime.now().date()
            response = HttpResponse(content_type='application/ms-excel')
            response['content-Disposition'] = 'attachment; filename = dynamic compression user' + \
                str(datetime.now()) + '.xls'
            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('Expenses')
            row_num = 0
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            columns = ['pk', 'user', 'created_on', 'input_date',
                       'calculation_stage', 'referral', 'users_in_depth_level_1', 'users_in_depth_level_2', 'users_in_depth_level_3',
                       'users_in_depth_level_4', 'users_in_depth_level_5', 'users_in_depth_level_6', 'users_in_depth_level_7',
                       'users_in_depth_level_8', 'users_in_depth_level_9', 'users_in_depth_level_10', 'draft_date',
                       'public_date']
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)
            font_style = xlwt.XFStyle()
            # print(to_date)
            # print(from_date)
            rows = dynamic_compression_active.objects.filter(input_date__month=month, input_date__year=year).values_list(
                'pk',
                'user__username', 'created_on',
                'input_date', 'calculation_stage', 'referral', 'users_in_depth_level_1',
                'users_in_depth_level_2', 'users_in_depth_level_3', 'users_in_depth_level_4', 'users_in_depth_level_5',
                'users_in_depth_level_6', 'users_in_depth_level_7',
                'users_in_depth_level_8', 'users_in_depth_level_9',
                'users_in_depth_level_10', 'draft_date', 'public_date')
            if len(rows) < 1:
                messages.success(
                    request, 'This month dynamic Compression User is not done!')
                return redirect('dynamic_compression_user')
            print(
                rows, 'here we are geting the data that is going to print in excel sheet')
            print(len(rows), 'here we are geting the length of data')
            for row in rows:
                row_num += 1
                counting_sale_type = 0
                for col_num in range(len(row)):
                    ws.write(row_num, col_num, str(row[col_num]), font_style)
            wb.save(response)
            return response

    messages.success(
        request, 'This month dynamic Compression User is not done!')
    return redirect('dynamic_compression_user')
