from .models import *
from django.shortcuts import render,HttpResponse,get_object_or_404,redirect
from django.contrib import messages
import json
import xlwt

from datetime import datetime
from .check_permit import check_permission


list_levels = ['Associate Director', 'Bronze Director', 'Silver Director', 'Gold Director',
                  'Platinum Director', 'Titanium Director', 'Sapphire Director','Emerald Director',
                  'Jade Director', 'Crown Director',  'Diamond Director',
                  'Black Diamond Director']

def dynamic_compression_director_f(request):
    # checking if user has permission to view this page
    if not check_permission(request):
        return HttpResponse('<h1>You don\'t have permission to view this page</h1>')

    if request.method == 'POST':
        month_cal = request.POST.get('month',None)
        print(month_cal,'<----------------------------')
        if month_cal != '':
            data = month_cal.split('-')
            year = data[0]
            month = data[1]
            month_cal +='-01'
            today_date = datetime.now().date()
            results = dynamic_compression_director.objects.filter(input_date__month=month,
                                                                           input_date__year=year).delete()
            super_qs = super_model.objects.last()
            # configure_qs = configurations.objects.last()
            tbl_users_r = ReferralCode.objects.filter().order_by('pk')
            for user in tbl_users_r:
                qlf_qs = title_qualification_calculation_model.objects.filter(user = user.user_id,date_model__month = month,date_model__year = year)
                qlf_qs = qlf_qs.latest('pk')
                if qlf_qs.current_month_qualification in list_levels:
                    user_direct = True
                else:
                    user_direct = False
                upline_refereds = user.referal_by
                dynamic_qs = dynamic_compression_director.objects.filter(user = upline_refereds,input_date = month_cal)
                try:
                    dynamic_qs = dynamic_qs.latest('pk')
                    if dynamic_qs.user_active:
                        referral = user
                    else:
                        referral = dynamic_qs.referral
                except:
                    referral = user

                user_enabled = user.status
                dynamic_comprsn_qs = dynamic_compression_director( user = user.user_id,input_date = month_cal,
                user_enabled = user_enabled,draft_date = today_date,user_active = user_direct,referral = referral)
                dynamic_comprsn_qs.save()



            all_dynamic_users = dynamic_compression_director.objects.filter(input_date = month_cal)
            for user in all_dynamic_users:
                try:
                    check_referall = user.user.referralcode.referal_by.referralcode
                    testing_referall = user.user.referralcode
                    if user.referral == testing_referall:
                        for_user_dynamic_compression = dynamic_compression_director.objects.get(user = check_referall,input_date = month_cal)
                        if for_user_dynamic_compression.user_active == False:
                            user.update(referral = for_user_dynamic_compression.referral)
                except:
                    pass

                if user.user_active:
                    level1  = dynamic_compression_director.objects.filter(input_date = month_cal,referral = user.user.referralcode).values_list('referral__user_id__username', flat=True)
                    level2  = dynamic_compression_director.objects.filter(input_date = month_cal,referral__referal_by__username__in = level1).values_list('referral__user_id__username', flat=True).exclude(referral__user_id__username__in = level1)
                    level3  = dynamic_compression_director.objects.filter(input_date = month_cal,referral__referal_by__username__in = level2).values_list('referral__user_id__username', flat=True).exclude(referral__user_id__username__in = level2)
                    level4  = dynamic_compression_director.objects.filter(input_date = month_cal,referral__referal_by__username__in = level3).values_list('referral__user_id__username', flat=True).exclude(referral__user_id__username__in = level3)
                    level5  = dynamic_compression_director.objects.filter(input_date = month_cal,referral__referal_by__username__in = level4).values_list('referral__user_id__username', flat=True).exclude(referral__user_id__username__in = level4)
                    level6  = dynamic_compression_director.objects.filter(input_date = month_cal,referral__referal_by__username__in = level5).values_list('referral__user_id__username', flat=True).exclude(referral__user_id__username__in = level5)
                    level7  = dynamic_compression_director.objects.filter(input_date = month_cal,referral__referal_by__username__in = level6).values_list('referral__user_id__username', flat=True).exclude(referral__user_id__username__in = level6)
                    level8  = dynamic_compression_director.objects.filter(input_date = month_cal,referral__referal_by__username__in = level7).values_list('referral__user_id__username', flat=True).exclude(referral__user_id__username__in = level7)
                    level9  = dynamic_compression_director.objects.filter(input_date = month_cal,referral__referal_by__username__in = level8).values_list('referral__user_id__username', flat=True).exclude(referral__user_id__username__in = level8)
                    level10  = dynamic_compression_director.objects.filter(input_date = month_cal,referral__referal_by__username__in = level9).values_list('referral__user_id__username', flat=True).exclude(referral__user_id__username__in = level9)
                    try:
                        level1 = removing_brkt(level1)
                    except:
                        level1 = ''
                    try:
                        level2 = removing_brkt(level2)
                    except:
                        level2 = ''
                    try:
                        level3 = removing_brkt(level3)
                    except:
                        level3 = ''
                    try:
                        level4 = removing_brkt(level4)
                    except:
                        level4 = ''
                    try:
                        level5 = removing_brkt(level5)
                    except:
                        level5 = ''
                    try:
                        level6 = removing_brkt(level6)
                    except:
                        level6 = ''
                    try:
                        level7 = removing_brkt(level7)
                    except:
                        level7 = ''
                    try:
                        level8 = removing_brkt(level8)
                    except:
                        level8 = ''
                    try:
                        level9 = removing_brkt(level9)
                    except:
                        level9 = ''
                    try:
                        level10 = removing_brkt(level10)
                    except:
                        level10 = ''
                    print(level1,'<-------------------------------------level1')
                    print(level2,'<-------------------------------------level2')
                    print(level3,'<-------------------------------------level3')
                    print(level4,'<-------------------------------------level4')
                    print(level5,'<-------------------------------------level5')
                    print(level6,'<-------------------------------------level6')
                    print(level7,'<-------------------------------------level7')
                    print(level8,'<-------------------------------------level8')
                    print(level9,'<-------------------------------------level9')
                    print(level10,'<-------------------------------------level10')
                    dynamic_compression_director. objects.filter(user = user.user,input_date = month_cal,draft_date = today_date).update(users_in_depth_level_1 = level1,
                                                users_in_depth_level_2 = level2,users_in_depth_level_3 = level3,users_in_depth_level_4 = level4,
                                                users_in_depth_level_5 = level5,users_in_depth_level_6 = level6,users_in_depth_level_7 = level7,
                                                users_in_depth_level_8 = level8,users_in_depth_level_9 = level9,users_in_depth_level_10 = level10)
    try:
        public_data = dynamic_compression_active.objects.filter(calculation_stage='Public')
        public_data = public_data.latest('pk')
        public_date = public_data.public_date
        public_month = public_data.input_date
    except:
        public_date = 'There is no data publish yet!'
        public_month = False
    try:
        draft_data = dynamic_compression_active.objects.filter(calculation_stage='Draft')
        draft_data = draft_data.latest('pk')
        draft_date = draft_data.draft_date
        draft_month = draft_data.input_date
    except:
        draft_date = 'There is no data draft yet!'
        draft_month = False

    params = {'public_date' : public_date,
              'draft_date':draft_date,
              'public_month' : public_month,
              'draft_month' : draft_month
              }

    return render(request,'mlm_calculation/dynamic_compression_director.html',params)
def removing_brkt(level):
    level = list(level)
    level = str(level)
    level = level.replace('[', '')
    level = level.replace(']', '')
    return level


def dynamic_compression_director_excel(request):
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
            response['content-Disposition'] = 'attachment; filename = dynamic compression director' + str(datetime.now()) + '.xls'
            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('Expenses')
            row_num = 0
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            columns = ['pk', 'user', 'created_on',
                'input_date', 'calculation_stage','is_user_director', 'referral', 'directors_in_depth_level_1',
                'directors_in_depth_level_2', 'directors_in_depth_level_3', 'directors_in_depth_level_4', 'directors_in_depth_level_5',
                'directors_in_depth_level_6', 'directors_in_depth_level_7',
                'directors_in_depth_level_8', 'directors_in_depth_level_9',
                'directors_in_depth_level_10', 'draft_date', 'public_date']
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)
            font_style = xlwt.XFStyle()
            # print(to_date)
            # print(from_date)
            rows = dynamic_compression_director.objects.filter(input_date__month = month,input_date__year = year).values_list(
                'pk',
                'user__username', 'created_on',
                'input_date', 'calculation_stage','is_user_director', 'referral', 'directors_in_depth_level_1',
                'directors_in_depth_level_2', 'directors_in_depth_level_3', 'directors_in_depth_level_4', 'directors_in_depth_level_5',
                'directors_in_depth_level_6', 'directors_in_depth_level_7',
                'directors_in_depth_level_8', 'directors_in_depth_level_9',
                'directors_in_depth_level_10', 'draft_date', 'public_date')
            if len(rows)< 1:
                messages.success(request, 'This month dynamic Compression Director is not done!')
                return redirect('dynamic_compression_director')
            print(rows, 'here we are geting the data that is going to print in excel sheet')
            print(len(rows), 'here we are geting the length of data')
            for row in rows:
                row_num += 1
                counting_sale_type = 0
                for col_num in range(len(row)):
                    ws.write(row_num, col_num, str(row[col_num]), font_style)
            wb.save(response)
            return response

    messages.success(request, 'This month dynamic Compression Director is not done!')
    return redirect('dynamic_compression_director')