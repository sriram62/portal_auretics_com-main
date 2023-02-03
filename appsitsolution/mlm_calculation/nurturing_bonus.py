from .models import *
from django.shortcuts import render,redirect,HttpResponse
from django.contrib import messages
import json
import xlwt
from datetime import datetime
from realtime_calculation.models import RealTimeDetail
from .check_permit import check_permission
from business.views import Objectify

list_levels = ['Associate Director','Bronze Director', 'Silver Director', 'Gold Director',
               'Platinum Director', 'Titanium Director', 'Sapphire Director', 'Emerald Director',
               'Jade Director', 'Crown Director', 'Diamond Director',
               'Black Diamond Director']
                  
try:
    configurations_qs = configurations.objects.last() if configurations.objects.all().exists() else configurations.objects.create()
except:
    configurations_qs = Objectify()
    configurations_qs.associate_advisor_percent = []
    configurations_qs.advisor_percent = []
    configurations_qs.associate_manager_percent = []
    configurations_qs.manager_percent = []
    configurations_qs.associate_director_percent = []


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
                          


def calculation_nurturing_bonus(request):
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
            today_date = datetime.now().date()
            results = nuturing_bonus.objects.filter(input_date__month=month,
                                                                           input_date__year=year).delete()
                                                                           
            infinity_qs = infinity_model.objects.last()
            director_circle_levels =    { 'Associate Director':infinity_qs.associate_direct_circle,
                                    'Bronze Director':infinity_qs.bronze_direct_circle, 
                                    'Silver Director':infinity_qs.silver_direct_circle,
                                    'Gold Director':infinity_qs.gold_direct_circle,
                                    'Platinum Director':infinity_qs.platinum_direct_circle,
                                    'Titanium Director':infinity_qs.titanium_direct_circle, 
                                    'Sapphire Director':infinity_qs.sapphire_direct_circle,
                                    'Emerald Director':infinity_qs.emerald_direct_circle,
                                    'Jade Director':infinity_qs.jade_direct_circle, 
                                    'Crown Director':infinity_qs.crown_direct_circle,
                                    'Diamond Director':infinity_qs.diamond_direct_circle,
                                    'Black Diamond Director':infinity_qs.black_diamond_direct_circle
                                }

            director_bonus_paid_levels =    {'Associate Director':infinity_qs.associate_percentage_personal_bonus_downline_on_which_nurturing_bonus_paid,
                                    'Bronze Director':infinity_qs.bronze_percentage_personal_bonus_downline_on_which_nurturing_bonus_paid,
                                    'Silver Director':infinity_qs.silver_percentage_personal_bonus_downline_on_which_nurturing_bonus_paid,
                                    'Gold Director':infinity_qs.gold_percentage_personal_bonus_downline_on_which_nurturing_bonus_paid,
                                    'Platinum Director':infinity_qs.platinum_percentage_personal_bonus_downline_on_which_nurturing_bonus_paid,
                                    'Titanium Director':infinity_qs.titanium_percentage_personal_bonus_downline_on_which_nurturing_bonus_paid,
                                    'Sapphire Director':infinity_qs.sapphire_percentage_personal_bonus_downline_on_which_nurturing_bonus_paid,
                                    'Emerald Director':infinity_qs.emerald_percentage_personal_bonus_downline_on_which_nurturing_bonus_paid,
                                    'Jade Director':infinity_qs.jade_percentage_personal_bonus_downline_on_which_nurturing_bonus_paid,
                                    'Crown Director':infinity_qs.crown_percentage_personal_bonus_downline_on_which_nurturing_bonus_paid,
                                    'Diamond Director':infinity_qs.diamond_percentage_personal_bonus_downline_on_which_nurturing_bonus_paid,
                                    'Black Diamond Director':infinity_qs.black_diamond_percentage_personal_bonus_downline_on_which_nurturing_bonus_paid
                                }
            
            # [Flow] selecting only qualified directors
            title_users = title_qualification_calculation_model.objects.filter(date_model__month=month,
                                                                                date_model__year=year, 
                                                                                current_month_qualification__contains='Director'
                                                                                ).exclude(current_month_qualification='Non Qualified Director')
                                                                                
            for i in title_users:
                current_qualification = i.current_month_qualification
                if current_qualification in list_levels:
                    user_personal_bonus_percent = float(personal_bonus_percent[current_qualification]) / 100
                    print("i")
                    print(i)
                    print(current_qualification)
                    dic_circle = director_circle_levels[current_qualification]
                    print(dic_circle)
                    # [Flow] Dynamic Compression or Referral Code
                    all_directors = ReferralCode.objects.filter(user_id = i.user)
                    # dynamic_user = dynamic_compression_active.objects.filter(user = i.user,input_date__month=month,
                    #                                                           input_date__year=year)
                    
                    # For the time being actual calculation is deferred and we will calculate on GBV
                    realtime_detail = RealTimeDetail.objects.filter(user_id = i.user,
                                                                    date__month = month,
                                                                    date__year  = year)[0]
                    print(realtime_detail)
                    gbv = realtime_detail.rt_gbv_month
                    print(gbv)
                    
                    director_perc = director_bonus_paid_levels[current_qualification]
                    
                    # Warning !!!!! this part is hard coded
                    nurturing_bonus_income = float(gbv) *  float(director_perc) / 100 * user_personal_bonus_percent
                    
                    print(director_perc)
                    print(nurturing_bonus_income)
                    
                    nurtur_qs = nuturing_bonus.objects.create(user = i.user,input_date = month_cal,qualified_director_level = current_qualification,
                                   circle_to_consider = dic_circle, percentage = director_perc, nurturing_bonus_earned = nurturing_bonus_income,
                                   draft_date = today_date)
                    
                    print("nurtur_qs")
                    print(nurtur_qs)
                    nurtur_qs.save()
                    
                    
                    '''
                    
                    if dynamic_user.user_active:
                        if dic_circle == 'Lead Circle':
                            # [Flow] Find users till 10 levels down and calculate their Personal Bonus
                            
                            pass
                            
                            
                        elif dic_circle == 'Influence Circle':
                            # [Flow] Find users till 5 levels down and calculate their Personal Bonus
                            pass
                            
                        else:
                            # [Flow] Personal Bonus of the Circle will be 0
                            circle_total = 0

                        dic_paid = director_bonus_paid_levels[current_qualification]
                        nurturing_bonus_income = float(circle_total) *  float(dic_paid) / 100
                        nurtur_qs = nuturing_bonus(user = i.user,input_date = month_cal,qualified_director_level = current_qualification,
                                       circle_to_consider = dic_circle,percentage = dic_paid,nurturing_bonus_earned = nurturing_bonus_income,
                                       draft_date = today_date)
                        nurtur_qs.save()
                        '''

    try:
        public_data = nuturing_bonus.objects.filter(calculation_stage='Public')
        public_data = public_data.latest('pk')
        public_date = public_data.public_date
        public_month = public_data.input_date
    except:
        public_date = 'There is no data publish yet!'
        public_month = False
    try:
        draft_data = nuturing_bonus.objects.filter(calculation_stage='Draft')
        draft_data = draft_data.latest('pk')
        draft_date = draft_data.draft_date
        draft_month = draft_data.input_date
    except:
        draft_date = 'There is no data draft yet!'
        draft_month = False
    params = {'public_date':public_date,'draft_date':draft_date,
              'public_month':public_month,'draft_month':draft_month}
    return render(request,'mlm_calculation/nurturing_bonus.html',params)


def nurturing_bonus_excel(request):
    # checking if user has permission to view this page
    if not check_permission(request):
        return HttpResponse('<h1>You don\'t have permission to view this page</h1>')

    if request.method == 'POST':
        month_cal = request.POST.get('excel_date',None)
        print(month_cal,'<----------------------------')
        if month_cal != '':
            data = month_cal.split('-')
            year = data[0]
            month = data[1]
            month_cal +='-01'
            today_date = datetime.now().date()
            response = HttpResponse(content_type='application/ms-excel')
            response['content-Disposition'] = 'attachment; filename = Nurturing Bonus' + str(datetime.now()) + '.xls'
            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('Expenses')
            row_num = 0
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            columns = ['pk', 'user', 'created_on','input_date', 'calculation_stage','is_user_qualified_director','qualified_director_level',
                       'circle_to_consider','percentage','nurturing_bonus_earned','nurturing_bonus_paid','nurturing_bonus_balance_payable',
                'total_personal_bonus_of_1st_generation_down','total_personal_bonus_of_2nd_generation_down',
                'total_personal_bonus_of_3rd_generation_down','total_personal_bonus_of_4th_generation_down','total_personal_bonus_of_5th_generation_down',
                'total_personal_bonus_of_6th_generation_down','total_personal_bonus_of_7th_generation_down',
                'total_personal_bonus_of_8th_generation_down','total_personal_bonus_of_9th_generation_down',
                'total_personal_bonus_of_10th_generation_down',
                       'draft_date', 'public_date']
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)
            font_style = xlwt.XFStyle()
            # print(to_date)
            # print(from_date)
            rows = nuturing_bonus.objects.filter(input_date__month = month,input_date__year = year).values_list(
                'pk',
                'user__username', 'created_on','input_date', 'calculation_stage','is_user_qualified_director','qualified_director_level',
                       'circle_to_consider','percentage','nurturing_bonus_earned','nurturing_bonus_paid','nurturing_bonus_balance_payable',
                'total_personal_bonus_of_1st_generation_down','total_personal_bonus_of_2nd_generation_down',
                'total_personal_bonus_of_3rd_generation_down','total_personal_bonus_of_4th_generation_down','total_personal_bonus_of_5th_generation_down',
                'total_personal_bonus_of_6th_generation_down','total_personal_bonus_of_7th_generation_down',
                'total_personal_bonus_of_8th_generation_down','total_personal_bonus_of_9th_generation_down',
                'total_personal_bonus_of_10th_generation_down',
                       'draft_date', 'public_date')
            if len(rows)< 1:
                messages.success(request, 'This month Nurturing Bonus is not Calculated!')
                return redirect('nurturing_bonus')
            print(rows, 'here we are geting the data that is going to print in excel sheet')
            print(len(rows), 'here we are geting the length of data')
            for row in rows:
                row_num += 1
                counting_sale_type = 0
                for col_num in range(len(row)):
                    ws.write(row_num, col_num, str(row[col_num]), font_style)
            wb.save(response)
            return response

    messages.success(request, 'This month Nurturing Bonus is not Calculated!')
    return redirect('nurturing_bonus')


def nurturing_bonus_publish(request):
    # checking if user has permission to view this page
    if not check_permission(request):
        return HttpResponse('<h1>You don\'t have permission to view this page</h1>')

    if request.method == 'POST':
        month_cal = request.POST.get('publish_date', None)
        print(month_cal, '<----------------------------')
        if month_cal != '':
            data = month_cal.split('-')
            year = data[0]
            month = data[1]
            month_cal += '-01'
            today_date = datetime.now().date()
            value = nuturing_bonus.objects.filter(input_date__month=month, input_date__year=year,calculation_stage = 'Draft').exists()
            if value == True:
                data_qs = nuturing_bonus.objects.filter(input_date__month = month,input_date__year = year ).update(public_date = today_date,
                                                                                                                            calculation_stage = 'Public')
                messages.success(request, str(month_cal) +' ' + 'Data Published Successfully!')
            else:
                messages.success(request, str(month_cal) + ' ' + 'Data Allready Published!')

    return redirect('nurturing_bonus')

def level_in_list(li):
    data = li.split(',')
    return data
def level_listing(levels,month,year):
    circle_personal_bonus = 0
    con_qs = configurations.objects.last()
    for li in levels:
        title = title_qualification_calculation_model.objects.filter(user__username = li,input_date__month = month,input_date__year = year)
        title = title.latest('pk')
        if title.ppv >= con_qs.minimum_monthly_purchase_to_become_active:
            personal_qs = personal_bonus.objects.filter(user__username = li,input_date__month = month,input_date__year = year)
            personal_qs = personal_qs.latest('pk')
            circle_personal_bonus += float(personal_qs.my_personal_bonus)
    return circle_personal_bonus