from .models import *
from accounts.models import *
from django.shortcuts import render,redirect,HttpResponse
from django.db import transaction
from django.db.models import Sum
from django.contrib import messages
import json
import xlwt
from datetime import datetime
from .check_permit import check_permission
from shop.models import Order


level_dic_self = {
                'Blue Advisor': 0,
                'Associate Advisor': 0,
                'Advisor': 0,
                'Associate Manager': 0,
                'Manager': 0,
                'Non Qualified Director': 0,
                'Associate Director': 1,
                'Bronze Director': 2,
                'Silver Director': 3,
                'Gold Director': 4,
                'Platinum Director': 5,
                'Titanium Director': 6,
                'Sapphire Director': 7,
                'Emerald Director': 8,
                'Jade Director': 9,
                'Crown Director': 10,
                'Diamond Director': 11,
                'Black Diamond Director': 12
            }
month_name = {
    '01':'Jan',
    '02':'Feb',
    '03':'Mar',
    '04':'Apr',
    '05':'May',
    '06':'Jun',
    '07':'Jul',
    '08':'Aug',
    '09':'Sep',
    '10':'Oct',
    '11':'Nov',
    '12':'Dec'
}

def vas_code(request):
    # checking if user has permission to view this page
    if not check_permission(request):
        return HttpResponse('<h1>You don\'t have permission to view this page</h1>')

    """
    Vacation Fund, Automobile Fund and Shelter Fund are given to users as a percentage of what they earn as
    Personal Bonus, Sharing Bonus, Nurturing Bonus & Business Master Bonus.
    VAS Funds are subject to qualification by each user.
    """
    if request.method == 'POST':
        month_cal = request.POST.get('month', None)
        # print(month_cal, '<----------------------------')
        if month_cal != '':
            data = month_cal.split('-')
            year = data[0]
            month = data[1]
            month_cal += '-01'
            request.session['month'] = month
            request.session['year'] = year
            today_date = datetime.now().date()

            last_month = int(month) - 1
            last_year = int(year)
            if last_month <= 0:
                last_month = 12
                last_year = int(year) - 1
            
            # [Flow] Remove data if already exists in the table for the current month
            results = vacation_fund.objects.filter(input_date__month=month, input_date__year=year).delete()
            results = automobile_fund.objects.filter(input_date__month=month, input_date__year=year).delete()
            results = shelter_fund.objects.filter(input_date__month=month, input_date__year=year).delete()
            
            # [Flow] Get all configuration data
            infinity_qs     = infinity_model.objects.last()
            vacation_level  = infinity_qs.vacation_fund_qualified_direct_level
            vacation_level  = level_dic_self[vacation_level]
            vacation_index  = infinity_qs.vacation_fund_percentage_pb_sb_nb_bmb
            vehicle_level   = infinity_qs.vehicle_fund_qualified_direct_level
            vehicle_level   = level_dic_self[vehicle_level]
            vehicle_index   = infinity_qs.vehicle_fund_percentage_pb_sb_nb_bmb
            shelter_level   = infinity_qs.shelter_fund_qualified_direct_level
            shelter_level   = level_dic_self[shelter_level]
            shelter_index   = infinity_qs.shelter_fund_percentage_pb_sb_nb_bmb

            # [Flow] Get all user data and iterate users one by one
            all_titles      = title_qualification_calculation_model.objects.filter(date_model__month = month,date_model__year = year)

            for title in all_titles:
                current_qualification = title.current_month_qualification
                ever_eligible_for_vas = False

                # [Flow] Checking if user has ever got a VAS
                vacation_fund_count = vacation_fund.objects.filter(user = title.user).count()
                automobile_fund_count = automobile_fund.objects.filter(user = title.user).count()
                shelter_fund_count = shelter_fund.objects.filter(user = title.user).count()

                if (vacation_fund_count + automobile_fund_count + shelter_fund_count) > 0:
                    ever_eligible_for_vas = True
                
                # [Flow] Note: In case we increase the title requirement for any VAS, then user might not get previously earned VAS.
                highest_qualification_ever = title.highest_qualification_ever
                
                if level_dic_self[highest_qualification_ever] >= vacation_level:
                    ever_eligible_for_vas = True
                if level_dic_self[highest_qualification_ever] >= vehicle_level:
                    ever_eligible_for_vas = True
                if level_dic_self[highest_qualification_ever] >= shelter_level:
                    ever_eligible_for_vas = True

                if ever_eligible_for_vas:
                    try:
                        vacation_fund_qs = vacation_fund.objects.get(input_date__month = last_month,input_date__year = last_year,user = title.user)
                        opening_vacation_fund = vacation_fund_qs.closing_vacation_fund
                    except:
                        opening_vacation_fund = 0

                    try:
                        automobile_fund_qs = automobile_fund.objects.get(input_date__month = last_month,input_date__year = last_year,user = title.user)
                        opening_automobile_fund = automobile_fund_qs.closing_automobile_fund
                    except:
                        opening_automobile_fund = 0

                    try:
                        shelter_fund_qs = shelter_fund.objects.get(input_date__month = last_month,input_date__year = last_year,user = title.user)
                        opening_shelter_fund = shelter_fund_qs.closing_shelter_fund
                    except:
                        opening_shelter_fund = 0

                    self_level = level_dic_self[current_qualification]
                    
                    personal_qs = personal_bonus.objects.filter(input_date__month = month, input_date__year = year, user = title.user)
                    try:
                        personal_qs = personal_qs.latest('pk').personal_bonus_earned
                    except:
                        personal_qs = 0
                        
                    sharing_qs = sharing_bonus.objects.filter(input_date__month = month, input_date__year = year, user = title.user)
                    try:
                        sharing_qs = sharing_qs.latest('pk').sharing_bonus_earned
                    except:
                        sharing_qs = 0
                        
                    nuturing_qs = nuturing_bonus.objects.filter(input_date__month = month, input_date__year = year, user = title.user)
                    try:
                        nuturing_qs = nuturing_qs.latest('pk').nurturing_bonus_earned
                    except:
                        nuturing_qs = 0
                        
                    bmb_qs = business_master_bonus.objects.filter(input_date__month = month, input_date__year = year, user = title.user)
                    try:
                        bmb_qs = bmb_qs.latest('pk').business_master_bonus_earned
                    except:
                        bmb_qs = 0
                        
                    total_points = personal_qs  + sharing_qs + nuturing_qs + bmb_qs
                    if self_level >= vacation_level:
                        total_vacation = float(total_points) * float(vacation_index)/ 100
                    else:
                        total_vacation = 0
                            
                    closing_vacation_fund = float(opening_vacation_fund) + float(total_vacation)
                    vacation_fund_earned_heading  = 'Vacation Fund of ' + str(month_name[str(month)]) + str(year)
                    vacation_qs = vacation_fund(user = title.user,input_date = month_cal,qualified_director_level = title.current_month_qualification,
                                          is_user_qualified_vacation_fund = True,
                                          draft_date = today_date,closing_vacation_fund = closing_vacation_fund,
                                          sum_of_all_bonus_earned = total_points,vacation_fund_earned = total_vacation,
                                          vacation_fund_earned_heading = vacation_fund_earned_heading,
                                          opening_vacation_fund = opening_vacation_fund,)
                    vacation_qs.save()
                        
                    if self_level >= vehicle_level:
                        total_automobile = float(total_points) * float(vehicle_index)/ 100
                    else:
                        total_automobile = 0
                            
                    closing_automobile_fund = float(opening_automobile_fund) + float(total_automobile)
                    automobile_fund_earned_heading  = 'Automobile Fund of ' + str(month_name[str(month)]) + str(year)
                    automobile_qs = automobile_fund(user = title.user,input_date = month_cal,qualified_director_level = title.current_month_qualification,
                                      is_user_qualified_automobile_fund = True,
                                      draft_date = today_date,closing_automobile_fund = closing_automobile_fund,
                                      sum_of_all_bonus_earned = total_points,automobile_fund_earned = total_automobile,
                                      automobile_fund_earned_heading = automobile_fund_earned_heading,
                                      opening_automobile_fund = opening_automobile_fund)
                    # print(total_automobile)
                    automobile_qs.save()

                    if self_level >= shelter_level:
                        total_shelter = float(total_points) * float(shelter_index)/ 100
                    else:
                        total_shelter = 0
                            
                    closing_shelter_fund = float(opening_shelter_fund) + float(total_shelter)
                    shelter_fund_earned_heading  = 'Shelter Fund of ' + str(month_name[str(month)]) + str(year)
                    shelter_qs = shelter_fund(user = title.user,input_date = month_cal,qualified_director_level = title.current_month_qualification,
                                  is_user_qualified_shelter_fund = True,draft_date = today_date,closing_shelter_fund = closing_shelter_fund,
                                  sum_of_all_bonus_earned = total_points,shelter_fund_earned = total_shelter,
                                  shelter_fund_earned_heading = shelter_fund_earned_heading,
                                  opening_shelter_fund = opening_shelter_fund)
                    # print(total_shelter)
                    shelter_qs.save()

            return HttpResponse('<h1>Welcome to Auretics! IF you are at this page it means Vacation Fund, Automobile Fund and Shelter Fund is calculated Successfully!!!</h1>')

    try:
        public_data = vacation_fund.objects.filter(calculation_stage='Public')
        public_data = public_data.latest('pk')
        public_date = public_data.public_date
        public_month = public_data.input_date
    except:
        public_date = 'There is no data publish yet!'
        public_month = False
    try:
        draft_data = vacation_fund.objects.filter(calculation_stage='Draft')
        draft_data = draft_data.latest('pk')
        draft_date = draft_data.draft_date
        draft_month = draft_data.input_date
    except:
        draft_date = 'There is no data draft yet!'
        draft_month = False
    params = {'public_date':public_date,'draft_date':draft_date,
              'public_month':public_month,'draft_month':draft_month}
    return render(request,'mlm_calculation/vas_bonus.html',params)


def vacation_excel(request):
    # checking if user has permission to view this page
    if not check_permission(request):
        return HttpResponse('<h1>You don\'t have permission to view this page</h1>')

    if request.method == 'POST':
        month_cal = request.POST.get('excel_date',None)
        # print(month_cal,'<----------------------------')
        if month_cal != '':
            data = month_cal.split('-')
            year = data[0]
            month = data[1]
            month_cal +='-01'
            today_date = datetime.now().date()
            response = HttpResponse(content_type='application/ms-excel')
            response['content-Disposition'] = 'attachment; filename = Vacation Fund' + str(datetime.now()) + '.xls'
            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('Expenses')
            row_num = 0
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            columns = ['pk', 'user', 'created_on','input_date', 'calculation_stage','is_user_qualified_director','qualified_director_level',
                       'is_user_qualified_vacation_fund','closing_vacation_fund','sum_of_all_bonus_earned','vacation_fund_earned',
                       'vacation_fund_earned_heading','vacation_fund_earned_remarks','opening_vacation_fund',
                'vacation_fund_used','vacation_fund_used_heading','vacation_fund_used_remarks',
                       'draft_date', 'public_date']
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)
            font_style = xlwt.XFStyle()
            rows = vacation_fund.objects.filter(input_date__month = month,input_date__year = year).values_list(
                'pk',
                'user__username', 'created_on','input_date', 'calculation_stage','is_user_qualified_director','qualified_director_level',
                       'is_user_qualified_vacation_fund','closing_vacation_fund','sum_of_all_bonus_earned','vacation_fund_earned',
                       'vacation_fund_earned_heading','vacation_fund_earned_remarks','opening_vacation_fund',
                'vacation_fund_used','vacation_fund_used_heading','vacation_fund_used_remarks',
                       'draft_date', 'public_date')
            if len(rows)< 1:
                messages.success(request, 'This month Vacation Fund is not Calculated!')
                return redirect('mlm_calculation_vacation_excel')
            # print(rows, 'here we are geting the data that is going to print in excel sheet')
            # print(len(rows), 'here we are geting the length of data')
            for row in rows:
                row_num += 1
                counting_sale_type = 0
                for col_num in range(len(row)):
                    ws.write(row_num, col_num, str(row[col_num]), font_style)
            wb.save(response)
            return response

    messages.success(request, 'This month Vacation Fund is not Calculated!')
    return redirect('mlm_calculation_vacation_excel')

def automobile_excel(request):
    # checking if user has permission to view this page
    if not check_permission(request):
        return HttpResponse('<h1>You don\'t have permission to view this page</h1>')

    if request.method == 'POST':
        month_cal = request.POST.get('excel_date',None)
        # print(month_cal,'<----------------------------')
        if month_cal != '':
            data = month_cal.split('-')
            year = data[0]
            month = data[1]
            month_cal +='-01'
            today_date = datetime.now().date()
            response = HttpResponse(content_type='application/ms-excel')
            response['content-Disposition'] = 'attachment; filename = Automobile Fund' + str(datetime.now()) + '.xls'
            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('Expenses')
            row_num = 0
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            columns = ['pk', 'user', 'created_on','input_date', 'calculation_stage','is_user_qualified_director','qualified_director_level',
                       'is_user_qualified_automobile_fund','closing_automobile_fund','sum_of_all_bonus_earned','automobile_fund_earned',
                       'automobile_fund_earned_heading','automobile_fund_earned_remarks','opening_automobile_fund',
                'automobile_fund_used','automobile_fund_used_heading','automobile_fund_used_remarks','closing_automobile_fund_used',
                       'draft_date', 'public_date']
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)
            font_style = xlwt.XFStyle()
            rows = automobile_fund.objects.filter(input_date__month = month,input_date__year = year).values_list(
                'pk',
                'user__username', 'created_on','input_date', 'calculation_stage','is_user_qualified_director','qualified_director_level',
                       'is_user_qualified_automobile_fund','closing_automobile_fund','sum_of_all_bonus_earned','automobile_fund_earned',
                       'automobile_fund_earned_heading','automobile_fund_earned_remarks','opening_automobile_fund',
                'automobile_fund_used','automobile_fund_used_heading','automobile_fund_used_remarks','closing_automobile_fund_used',
                       'draft_date', 'public_date')
            if len(rows)< 1:
                messages.success(request, 'This month Automobile Fund is not Calculated!')
                return redirect('mlm_calculation_automobile_excel')
            # print(rows, 'here we are geting the data that is going to print in excel sheet')
            # print(len(rows), 'here we are geting the length of data')
            for row in rows:
                row_num += 1
                counting_sale_type = 0
                for col_num in range(len(row)):
                    ws.write(row_num, col_num, str(row[col_num]), font_style)
            wb.save(response)
            return response

    messages.success(request, 'This month Automobile Fund is not Calculated!')
    return redirect('mlm_calculation_automobile_excel')

def shelter_excel(request):
    # checking if user has permission to view this page
    if not check_permission(request):
        return HttpResponse('<h1>You don\'t have permission to view this page</h1>')

    if request.method == 'POST':
        month_cal = request.POST.get('excel_date',None)
        # print(month_cal,'<----------------------------')
        if month_cal != '':
            data = month_cal.split('-')
            year = data[0]
            month = data[1]
            month_cal +='-01'
            today_date = datetime.now().date()
            response = HttpResponse(content_type='application/ms-excel')
            response['content-Disposition'] = 'attachment; filename = Shelter Fund' + str(datetime.now()) + '.xls'
            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('Expenses')
            row_num = 0
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            columns = ['pk', 'user', 'created_on','input_date', 'calculation_stage','is_user_qualified_director','qualified_director_level',
                       'is_user_qualified_shelter_fund','closing_shelter_fund','sum_of_all_bonus_earned','shelter_fund_earned',
                       'shelter_fund_earned_heading','shelter_fund_earned_remarks','opening_shelter_fund',
                'shelter_fund_used','shelter_fund_used_heading','shelter_fund_used_remarks','closing_shelter_fund_used',
                       'draft_date', 'public_date']
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)
            font_style = xlwt.XFStyle()
            rows = shelter_fund.objects.filter(input_date__month = month,input_date__year = year).values_list(
                'pk',
                'user__username',  'created_on','input_date', 'calculation_stage','is_user_qualified_director','qualified_director_level',
                       'is_user_qualified_shelter_fund','closing_shelter_fund','sum_of_all_bonus_earned','shelter_fund_earned',
                       'shelter_fund_earned_heading','shelter_fund_earned_remarks','opening_shelter_fund',
                'shelter_fund_used','shelter_fund_used_heading','shelter_fund_used_remarks','closing_shelter_fund_used',
                       'draft_date', 'public_date')
            if len(rows)< 1:
                messages.success(request, 'This month Shelter Fund is not Calculated!')
                return redirect('mlm_calculation_shelter_excel')
            # print(rows, 'here we are geting the data that is going to print in excel sheet')
            # print(len(rows), 'here we are geting the length of data')
            for row in rows:
                row_num += 1
                counting_sale_type = 0
                for col_num in range(len(row)):
                    ws.write(row_num, col_num, str(row[col_num]), font_style)
            wb.save(response)
            return response

    messages.success(request, 'This month Shelter Fund is not Calculated!')
    return redirect('mlm_calculation_shelter_excel')


def vas_publish(request):
    # checking if user has permission to view this page
    if not check_permission(request):
        return HttpResponse('<h1>You don\'t have permission to view this page</h1>')

    if request.method == 'POST':
        month_cal = request.POST.get('publish_date', None)
        # print(month_cal, '<----------------------------')
        if month_cal != '':
            data = month_cal.split('-')
            year = data[0]
            month = data[1]
            month_cal += '-01'
            today_date = datetime.now().date()
            value = vacation_fund.objects.filter(input_date__month=month, input_date__year=year,calculation_stage = 'Draft').exists()
            if value == True:
                with transaction.atomic():
                    data_qs = vacation_fund.objects.filter(input_date__month = month,input_date__year = year ).update(public_date = today_date,
                                                                                                                            calculation_stage = 'Public')
                    data_qs = automobile_fund.objects.filter(input_date__month=month,
                                                                   input_date__year=year).update(public_date=today_date,
                                                                                                 calculation_stage='Public')
                    data_qs = shelter_fund.objects.filter(input_date__month=month,
                                                                   input_date__year=year).update(public_date=today_date,
                                                                                                 calculation_stage='Public')
                messages.success(request, str(month_cal) +' ' + 'Data Published Successfully!')
            else:
                messages.success(request, str(month_cal) + ' ' + 'Data Allready Published!')

    return redirect('mlm_calculation_vas')

def conficonsistent_retailers_income_fn(request):
    # checking if user has permission to view this page
    if not check_permission(request):
        return HttpResponse('<h1>You don\'t have permission to view this page</h1>')

    if request.method == 'POST':
        month_cal = request.POST.get('month', None)
        # print(month_cal, '<----------------------------')
        if month_cal != '':
            data = month_cal.split('-')
            year = data[0]
            month = data[1]
            next_month = int(month) + 1
            next_year = int(year)
            if next_month > 12:
                next_month = 1
                next_year = next_year + 1
            month_cal += '-01'
            today_date = datetime.now().date()
            results = consistent_retailers_income.objects.filter(input_date__month=month,
                                                                           input_date__year=year).delete()
            all_titles = title_qualification_calculation_model.objects.filter(date_model__month = month,date_model__year = year)
            infinity_qs = infinity_model.objects.last()
            minimum_purchase_in_earning_month_ppv = infinity_qs.minimum_purchase_in_earning_month
            percentage_loyalty_given = float(infinity_qs.percentage_loyalty_given)/100
            for title in all_titles:
                loyal_pbv_points = 0
                
                if title.infinity_ppv >= minimum_purchase_in_earning_month_ppv:
                    loyal_pbv = float(title.infinity_pbv) * percentage_loyalty_given
                    is_user_qualified_consistent_retailers_income = True
                    print(title.user.username)
                    consumed_cri = Order.objects.filter(email = title.user.username,
                                                      date__month=next_month,
                                                      date__year=next_year,
                                                      paid=True,
                                                      delete = False).exclude(status=8).aggregate(Sum('consumed_cri'))['consumed_cri__sum']
                    if consumed_cri:
                        consumed_cri = float(consumed_cri)
                    else:
                        consumed_cri = 0.0
                    cri_balance = loyal_pbv - consumed_cri
                # else:
                #     loyal_pbv = 0
                #     is_user_qualified_consistent_retailers_income = False
                    
                    last_month_pbv = title.infinity_pbv
                    consistent_qs = consistent_retailers_income(user = title.user,input_date = month_cal,draft_date = today_date,
                                                is_user_qualified_consistent_retailers_income = is_user_qualified_consistent_retailers_income,
                                                last_month_pbv = last_month_pbv,this_month_pbv = title.infinity_pbv,
                                                cri_earned = loyal_pbv, cri_consumed = consumed_cri, cri_balance = cri_balance,
                                                )
                    consistent_qs.save()
            return HttpResponse('<h1>Welcome Auretics! If you are at this page it means Consistent Retailers Income is calculated Successfully!!!</h1>')


    try:
        public_data = consistent_retailers_income.objects.filter(calculation_stage='Public')
        public_data = public_data.latest('pk')
        public_date = public_data.input_date
        public_month = public_data.input_date

    except:
        public_date = 'There is no data publish yet!'
        public_month = False
    try:
        draft_data = consistent_retailers_income.objects.filter(calculation_stage='Draft')
        draft_data = draft_data.latest('pk')
        draft_date = draft_data.input_date
        draft_month = draft_data.input_date
    except:
        draft_date = 'There is no data draft yet!'
        draft_month = False
    params = {'public_date':public_date,'draft_date':draft_date,
              'public_month':public_month,'draft_month':draft_month}
    return render(request,'mlm_calculation/cri_bonus.html',params)


def cri_excel(request):
    # checking if user has permission to view this page
    if not check_permission(request):
        return HttpResponse('<h1>You don\'t have permission to view this page</h1>')

    if request.method == 'POST':
        month_cal = request.POST.get('excel_date',None)
        # print(month_cal,'<----------------------------')
        if month_cal != '':
            data = month_cal.split('-')
            year = data[0]
            month = data[1]
            month_cal +='-01'
            today_date = datetime.now().date()
            response = HttpResponse(content_type='application/ms-excel')
            response['content-Disposition'] = 'attachment; filename = CRI' + str(datetime.now()) + '.xls'
            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('Expenses')
            row_num = 0
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            columns = ['pk', 'user', 'ARN', 'Mobile',  'First Name',  'Last Name', 'created_on','input_date', 'calculation_stage','is_user_qualified_consistent_retailers_income',
                       'last_month_pbv',
                       'this_month_pbv','cri_consumed','cri_earned','order_no_in_which_pbv_was_consumed',
                       'cri_balance',
                       'draft_date', 'public_date']
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)
            font_style = xlwt.XFStyle()
            rows = consistent_retailers_income.objects.filter(input_date__month = month,input_date__year = year).values_list(
                        'pk',
                        'user__username', 'user__referralcode__referral_code', 'user_id__profile__phone_number',  'user_id__profile__first_name',  'user_id__profile__last_name',
                        'created_on','input_date', 'calculation_stage','is_user_qualified_consistent_retailers_income',
                        'last_month_pbv',
                        'this_month_pbv','cri_consumed','cri_earned','order_no_in_which_pbv_was_consumed',
                        'cri_balance',
                        'draft_date', 'public_date')
            if len(rows)< 1:
                messages.success(request, 'This month Cri is not Calculated!')
                return redirect('mlm_calculation_consistent_retailers_income')
            # print(rows, 'here we are geting the data that is going to print in excel sheet')
            # print(len(rows), 'here we are geting the length of data')
            for row in rows:
                row_num += 1
                counting_sale_type = 0
                for col_num in range(len(row)):
                    ws.write(row_num, col_num, str(row[col_num]), font_style)
            wb.save(response)
            return response

    messages.success(request, 'This month Cri is not Calculated!')
    return redirect('mlm_calculation_consistent_retailers_income')


def cri_publish(request):
    # checking if user has permission to view this page
    if not check_permission(request):
        return HttpResponse('<h1>You don\'t have permission to view this page</h1>')

    if request.method == 'POST':
        month_cal = request.POST.get('publish_date', None)
        # print(month_cal, '<----------------------------')
        if month_cal != '':
            data = month_cal.split('-')
            year = data[0]
            month = data[1]
            month_cal += '-01'
            today_date = datetime.now().date()
            value = consistent_retailers_income.objects.filter(input_date__month=month, input_date__year=year,calculation_stage = 'Draft').exists()
            if value == True:
                data_qs = consistent_retailers_income.objects.filter(input_date__month = month,input_date__year = year ).update(public_date = today_date,
                                                                                                                        calculation_stage = 'Public')
                messages.success(request, str(month_cal) +' ' + 'Data Published Successfully!')
            else:
                messages.success(request, str(month_cal) + ' ' + 'Data Allready Published!')

    return redirect('mlm_calculation_consistent_retailers_income')