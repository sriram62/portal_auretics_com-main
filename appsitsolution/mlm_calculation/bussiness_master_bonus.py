from .models import *
from django.shortcuts import render,redirect,HttpResponse
from django.contrib import messages
import json
import xlwt
from datetime import datetime
from .check_permit import check_permission

list_levels = ['Associate Director', 'Bronze Director', 'Silver Director', 'Gold Director',
                  'Platinum Director', 'Titanium Director', 'Sapphire Director','Emerald Director',
                  'Jade Director', 'Crown Director',  'Diamond Director',
                  'Black Diamond Director']

def calculate_business_master_bonus(request):
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
            results = business_master_bonus.objects.filter(input_date__month=month,
                                                                           input_date__year=year).delete()
            infinity_qs = infinity_model.objects.last()
            level_dic_self = {
                'Associate Director': infinity_qs.associate_direct_self,
                'Bronze Director': infinity_qs.bronze_direct_self,
                'Silver Director': infinity_qs.silver_direct_self,
                'Gold Director': infinity_qs.gold_direct_self,
                'Platinum Director': infinity_qs.platinum_direct_self,
                'Titanium Director': infinity_qs.titanium_direct_self,
                'Sapphire Director': infinity_qs.sapphire_direct_self,
                'Jade Director': infinity_qs.jade_direct_self,
                'Crown Director': infinity_qs.crown_direct_self,
                'Emerald Director': infinity_qs.emerald_direct_self,
                'Diamond Director': infinity_qs.diamond_direct_self,
                'Black Diamond Director': infinity_qs.black_diamond_direct_self
            }
            level_dic_1 = {
                'Associate Director': infinity_qs.associate_direct_1,
                'Bronze Director': infinity_qs.bronze_direct_1,
                'Silver Director': infinity_qs.silver_direct_1,
                'Gold Director': infinity_qs.gold_direct_1,
                'Platinum Director': infinity_qs.platinum_direct_1,
                'Titanium Director': infinity_qs.titanium_direct_1,
                'Sapphire Director': infinity_qs.sapphire_direct_1,
                'Jade Director': infinity_qs.jade_direct_1,
                'Crown Director': infinity_qs.crown_direct_1,
                'Emerald Director': infinity_qs.emerald_direct_1,
                'Diamond Director': infinity_qs.diamond_direct_1,
                'Black Diamond Director': infinity_qs.black_diamond_direct_1
            }
            level_dic_2 = {
                'Associate Director': infinity_qs.associate_direct_2,
                'Bronze Director': infinity_qs.bronze_direct_2,
                'Silver Director': infinity_qs.silver_direct_2,
                'Gold Director': infinity_qs.gold_direct_2,
                'Platinum Director': infinity_qs.platinum_direct_2,
                'Titanium Director': infinity_qs.titanium_direct_2,
                'Sapphire Director': infinity_qs.sapphire_direct_2,
                'Jade Director': infinity_qs.jade_direct_2,
                'Crown Director': infinity_qs.crown_direct_2,
                'Emerald Director': infinity_qs.emerald_direct_2,
                'Diamond Director': infinity_qs.diamond_direct_2,
                'Black Diamond Director': infinity_qs.black_diamond_direct_2
            }
            level_dic_3 = {
                'Associate Director': infinity_qs.associate_direct_3,
                'Bronze Director': infinity_qs.bronze_direct_3,
                'Silver Director': infinity_qs.silver_direct_3,
                'Gold Director': infinity_qs.gold_direct_3,
                'Platinum Director': infinity_qs.platinum_direct_3,
                'Titanium Director': infinity_qs.titanium_direct_3,
                'Sapphire Director': infinity_qs.sapphire_direct_3,
                'Jade Director': infinity_qs.jade_direct_3,
                'Crown Director': infinity_qs.crown_direct_3,
                'Emerald Director': infinity_qs.emerald_direct_3,
                'Diamond Director': infinity_qs.diamond_direct_3,
                'Black Diamond Director': infinity_qs.black_diamond_direct_3
            }
            level_dic_4 = {
                'Associate Director': infinity_qs.associate_direct_4,
                'Bronze Director': infinity_qs.bronze_direct_4,
                'Silver Director': infinity_qs.silver_direct_4,
                'Gold Director': infinity_qs.gold_direct_4,
                'Platinum Director': infinity_qs.platinum_direct_4,
                'Titanium Director': infinity_qs.titanium_direct_4,
                'Sapphire Director': infinity_qs.sapphire_direct_4,
                'Jade Director': infinity_qs.jade_direct_4,
                'Crown Director': infinity_qs.crown_direct_4,
                'Emerald Director': infinity_qs.emerald_direct_4,
                'Diamond Director': infinity_qs.diamond_direct_4,
                'Black Diamond Director': infinity_qs.black_diamond_direct_4
            }
            level_dic_5 = {
                'Associate Director': infinity_qs.associate_direct_5,
                'Bronze Director': infinity_qs.bronze_direct_5,
                'Silver Director': infinity_qs.silver_direct_5,
                'Gold Director': infinity_qs.gold_direct_5,
                'Platinum Director': infinity_qs.platinum_direct_5,
                'Titanium Director': infinity_qs.titanium_direct_5,
                'Sapphire Director': infinity_qs.sapphire_direct_5,
                'Jade Director': infinity_qs.jade_direct_5,
                'Crown Director': infinity_qs.crown_direct_5,
                'Emerald Director': infinity_qs.emerald_direct_5,
                'Diamond Director': infinity_qs.diamond_direct_5,
                'Black Diamond Director': infinity_qs.black_diamond_direct_5
            }
            level_dic_6 = {
                'Associate Director': infinity_qs.associate_direct_6,
                'Bronze Director': infinity_qs.bronze_direct_6,
                'Silver Director': infinity_qs.silver_direct_6,
                'Gold Director': infinity_qs.gold_direct_6,
                'Platinum Director': infinity_qs.platinum_direct_6,
                'Titanium Director': infinity_qs.titanium_direct_6,
                'Sapphire Director': infinity_qs.sapphire_direct_6,
                'Jade Director': infinity_qs.jade_direct_6,
                'Crown Director': infinity_qs.crown_direct_6,
                'Emerald Director': infinity_qs.emerald_direct_6,
                'Diamond Director': infinity_qs.diamond_direct_6,
                'Black Diamond Director': infinity_qs.black_diamond_direct_6
            }
            level_dic_7 = {
                'Associate Director': infinity_qs.associate_direct_7,
                'Bronze Director': infinity_qs.bronze_direct_7,
                'Silver Director': infinity_qs.silver_direct_7,
                'Gold Director': infinity_qs.gold_direct_7,
                'Platinum Director': infinity_qs.platinum_direct_7,
                'Titanium Director': infinity_qs.titanium_direct_7,
                'Sapphire Director': infinity_qs.sapphire_direct_7,
                'Jade Director': infinity_qs.jade_direct_7,
                'Crown Director': infinity_qs.crown_direct_7,
                'Emerald Director': infinity_qs.emerald_direct_7,
                'Diamond Director': infinity_qs.diamond_direct_7,
                'Black Diamond Director': infinity_qs.black_diamond_direct_7
            }
            level_dic_8 = {
                'Associate Director': infinity_qs.associate_direct_8,
                'Bronze Director': infinity_qs.bronze_direct_8,
                'Silver Director': infinity_qs.silver_direct_8,
                'Gold Director': infinity_qs.gold_direct_8,
                'Platinum Director': infinity_qs.platinum_direct_8,
                'Titanium Director': infinity_qs.titanium_direct_8,
                'Sapphire Director': infinity_qs.sapphire_direct_8,
                'Jade Director': infinity_qs.jade_direct_8,
                'Crown Director': infinity_qs.crown_direct_8,
                'Emerald Director': infinity_qs.emerald_direct_8,
                'Diamond Director': infinity_qs.diamond_direct_8,
                'Black Diamond Director': infinity_qs.black_diamond_direct_8
            }
            level_dic_9 = {
                'Associate Director': infinity_qs.associate_direct_9,
                'Bronze Director': infinity_qs.bronze_direct_9,
                'Silver Director': infinity_qs.silver_direct_9,
                'Gold Director': infinity_qs.gold_direct_9,
                'Platinum Director': infinity_qs.platinum_direct_9,
                'Titanium Director': infinity_qs.titanium_direct_9,
                'Sapphire Director': infinity_qs.sapphire_direct_9,
                'Jade Director': infinity_qs.jade_direct_9,
                'Crown Director': infinity_qs.crown_direct_9,
                'Emerald Director': infinity_qs.emerald_direct_9,
                'Diamond Director': infinity_qs.diamond_direct_9,
                'Black Diamond Director': infinity_qs.black_diamond_direct_9
            }
            level_dic_10 = {
                'Associate Director': infinity_qs.associate_direct_10,
                'Bronze Director': infinity_qs.bronze_direct_10,
                'Silver Director': infinity_qs.silver_direct_10,
                'Gold Director': infinity_qs.gold_direct_10,
                'Platinum Director': infinity_qs.platinum_direct_10,
                'Titanium Director': infinity_qs.titanium_direct_10,
                'Sapphire Director': infinity_qs.sapphire_direct_10,
                'Jade Director': infinity_qs.jade_direct_10,
                'Crown Director': infinity_qs.crown_direct_10,
                'Emerald Director': infinity_qs.emerald_direct_10,
                'Diamond Director': infinity_qs.diamond_direct_10,
                'Black Diamond Director': infinity_qs.black_diamond_direct_10
            }
            con_qs = configurations.objects.last()
            minimum_ppv_to_active = con_qs.minimum_monthly_purchase_to_become_active

            title_users = title_qualification_calculation_model.objects.filter(date_model__month=month,
                                                                 date_model__year=year)
            for title in title_users:
                current_qualification = title.current_month_qualification
                levelself_bmb_points = level_dic_self.get(current_qualification,None)
                if levelself_bmb_points == None:
                    levelself_bmb_points = 0
                dynamic_direct_qs = dynamic_compression_director.objects.filter(user = title.user,input_date__month = month,input_date__year = year)
                dynamic_direct_qs = dynamic_direct_qs.latest('pk')
                level1 = dynamic_direct_qs.directors_in_depth_level_1
                level1 = level_in_list(level1)
                level1_bmb_points = circle_bmb(level1,month,year,level_dic_1,minimum_ppv_to_active)
                level2 =dynamic_direct_qs.directors_in_depth_level_2
                level2 = level_in_list(level2)
                level2_bmb_points = circle_bmb(level2,month,year,level_dic_2,minimum_ppv_to_active)
                level3 = dynamic_direct_qs.directors_in_depth_level_3
                level3 = level_in_list(level3)
                level3_bmb_points = circle_bmb(level3,month,year,level_dic_3,minimum_ppv_to_active)
                level4 = dynamic_direct_qs.directors_in_depth_level_4
                level4 = level_in_list(level4)
                level4_bmb_points = circle_bmb(level4,month,year,level_dic_4,minimum_ppv_to_active)
                level5 = dynamic_direct_qs.directors_in_depth_level_5
                level5 = level_in_list(level5)
                level5_bmb_points = circle_bmb(level5,month,year,level_dic_5,minimum_ppv_to_active)
                level6 = dynamic_direct_qs.directors_in_depth_level_6
                level6 = level_in_list(level6)
                level6_bmb_points = circle_bmb(level6,month,year,level_dic_6,minimum_ppv_to_active)
                level7 = dynamic_direct_qs.directors_in_depth_level_7
                level7 = level_in_list(level7)
                level7_bmb_points = circle_bmb(level7,month,year,level_dic_7,minimum_ppv_to_active)
                level8 = dynamic_direct_qs.directors_in_depth_level_8
                level8 = level_in_list(level8)
                level8_bmb_points = circle_bmb(level8,month,year,level_dic_8,minimum_ppv_to_active)
                level9 = dynamic_direct_qs.directors_in_depth_level_9
                level9 = level_in_list(level9)
                level9_bmb_points = circle_bmb(level9,month,year,level_dic_9,minimum_ppv_to_active)
                level10 = dynamic_direct_qs.directors_in_depth_level_10
                level10 = level_in_list(level10)
                level10_bmb_points = circle_bmb(level10,month,year,level_dic_10,minimum_ppv_to_active)
                total_bmb_points = float(levelself_bmb_points) + float(level1_bmb_points) + float(level2_bmb_points) + float(level3_bmb_points)
                + float(level4_bmb_points) + float(level5_bmb_points) + float(level6_bmb_points) + float(level7_bmb_points)
                + float(level8_bmb_points) + float(level9_bmb_points) + float(level10_bmb_points)
                bmb_qs = business_master_bonus(user = title.user,input_date = month_cal,qualified_director_level = title.current_month_qualification,
                                      total_bmb_points_from_1st_generation_down = level1_bmb_points,
                                      total_bmb_points_from_2nd_generation_down = level2_bmb_points,
                                      total_bmb_points_from_3rd_generation_down = level3_bmb_points,
                                      total_bmb_points_from_4th_generation_down = level4_bmb_points,
                                      total_bmb_points_from_5th_generation_down = level5_bmb_points,
                                      total_bmb_points_from_6th_generation_down = level6_bmb_points,
                                      total_bmb_points_from_7th_generation_down = level7_bmb_points,
                                      total_bmb_points_from_8th_generation_down = level8_bmb_points,
                                      total_bmb_points_from_9th_generation_down = level9_bmb_points,
                                      total_bmb_points_from_10th_generation_down = level10_bmb_points,
                                      total_bmb_points = total_bmb_points,draft_date = today_date)
                bmb_qs.save()
                request.session['month'] = month
                request.session['year'] = year
                return redirect('mlm_calculation_after_sum_bmb')

    try:
        public_data = business_master_bonus.objects.filter(calculation_stage='Public')
        public_data = public_data.latest('pk')
        public_date = public_data.public_date
        public_month = public_data.input_date
    except:
        public_date = 'There is no data publish yet!'
        public_month = False
    try:
        draft_data = business_master_bonus.objects.filter(calculation_stage='Draft')
        draft_data = draft_data.latest('pk')
        draft_date = draft_data.draft_date
        draft_month = draft_data.input_date
    except:
        draft_date = 'There is no data draft yet!'
        draft_month = False
    params = {'public_date':public_date,'draft_date':draft_date,
              'public_month':public_month,'draft_month':draft_month}

    return render(request,'mlm_calculation/bmb_bonus.html',params)


def bmb_bonus_excel(request):
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
            response['content-Disposition'] = 'attachment; filename = Business Master Bonus' + str(datetime.now()) + '.xls'
            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('Expenses')
            row_num = 0
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            columns = ['pk', 'user', 'created_on','input_date', 'calculation_stage','is_user_qualified_director','qualified_director_level',
                       'circle_to_consider','percentage','business_master_bonus_earned','business_master_bonus_paid','business_master_bonus_balance_payable',
                'total_bmb_points_from_1st_generation_down','total_bmb_points_from_2nd_generation_down',
                'total_bmb_points_from_3rd_generation_down','total_bmb_points_from_4th_generation_down','total_bmb_points_from_5th_generation_down',
                'total_bmb_points_from_6th_generation_down','total_bmb_points_from_7th_generation_down',
                'total_bmb_points_from_8th_generation_down','total_bmb_points_from_9th_generation_down',
                'total_bmb_points_from_10th_generation_down','total_bmb_points',
                       'draft_date', 'public_date']
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)
            font_style = xlwt.XFStyle()
            # print(to_date)
            # print(from_date)
            rows = business_master_bonus.objects.filter(input_date__month = month,input_date__year = year).values_list(
                'pk',
                'user__username','created_on','input_date', 'calculation_stage','is_user_qualified_director','qualified_director_level',
                       'circle_to_consider','percentage','business_master_bonus_earned','business_master_bonus_paid','business_master_bonus_balance_payable',
                'total_bmb_points_from_1st_generation_down','total_bmb_points_from_2nd_generation_down',
                'total_bmb_points_from_3rd_generation_down','total_bmb_points_from_4th_generation_down','total_bmb_points_from_5th_generation_down',
                'total_bmb_points_from_6th_generation_down','total_bmb_points_from_7th_generation_down',
                'total_bmb_points_from_8th_generation_down','total_bmb_points_from_9th_generation_down',
                'total_bmb_points_from_10th_generation_down','total_bmb_points',
                       'draft_date', 'public_date')
            if len(rows)< 1:
                messages.success(request, 'This month Business Master Bonus is not Calculated!')
                return redirect('mlm_calculation_bmb_cal')
            print(rows, 'here we are geting the data that is going to print in excel sheet')
            print(len(rows), 'here we are geting the length of data')
            for row in rows:
                row_num += 1
                counting_sale_type = 0
                for col_num in range(len(row)):
                    ws.write(row_num, col_num, str(row[col_num]), font_style)
            wb.save(response)
            return response

    messages.success(request, 'This month Business Master Bonus is not Calculated!')
    return redirect('mlm_calculation_bmb_cal')

def bmb_bonus_publish(request):
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
            value = business_master_bonus.objects.filter(input_date__month=month, input_date__year=year,calculation_stage = 'Draft').exists()
            if value == True:
                data_qs = business_master_bonus.objects.filter(input_date__month = month,input_date__year = year ).update(public_date = today_date,
                                                                                                                            calculation_stage = 'Public')
                messages.success(request, str(month_cal) +' ' + 'Data Published Successfully!')
            else:
                messages.success(request, str(month_cal) + ' ' + 'Data Allready Published!')

    return redirect('mlm_calculation_bmb_cal')

def level_in_list(li):
    data  = []
    if li != None:
        data = li.split(',')
    return data
def circle_bmb(data,month,year,dic_level,minmun_purchase_to_active):
    circle_bmb_value = 0
    for i in data:
        title = title_qualification_calculation_model.objects.filter(user__username = i,input_date__month = month,input_date__year = year)
        title = title.latest('pk')
        if title.ppv >= minmun_purchase_to_active:
            current_qualification = title.current_month_qualification
            index_bmb = dic_level[current_qualification]
            index_bmb = float(index_bmb)
            circle_bmb_value += index_bmb
    return circle_bmb_value

def after_sum_business_master(request):
    # checking if user has permission to view this page
    if not check_permission(request):
        return HttpResponse('<h1>You don\'t have permission to view this page</h1>')

    month = request.session['month']
    year = request.session['year']
    data = business_master_bonus.objects.filter(input_date__month = month,input_date__year = year)
    total_bmb_points = sum([bm.total_bmb_points for bm in data])
    if request.method == 'POST':
        index = request.POST.get('index',None)
        if index == None:
            index = 0
        try:
            index = float(index)
        except:
            index = 0
        for user in data:
            business_master_bonus_earned = float(user.total_bmb_points) * index
            business_master_bonus.objects.filter(user = user.user,input_date = user.input_date).update(business_master_bonus_earned = business_master_bonus_earned)
    return render(request,'mlm_calculation/bmb_bonus_cal.html',{'sum_bmb_point' : total_bmb_points})