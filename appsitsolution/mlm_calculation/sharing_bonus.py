from .models import *
from django.shortcuts import render,HttpResponse,redirect
from django.contrib import messages
import json
import xlwt
from datetime import datetime
from mlm_calculation.bussiness_master_bonus import list_levels
from .check_permit import check_permission

def calcaltion_sharing_bonus(request):
    # checking if user has permission to view this page
    if not check_permission(request):
        return HttpResponse('<h1>You don\'t have permission to view this page</h1>')

    try:
        public_data = sharing_bonus.objects.filter(calculation_stage='Public')
        public_data = public_data.latest('pk')
        public_date = public_data.public_date
        public_month = public_data.input_date
    except:
        public_date = 'There is no data publish yet!'
        public_month = False
    try:
        draft_data = sharing_bonus.objects.filter(calculation_stage='Draft')
        draft_data = draft_data.latest('pk')
        draft_date = draft_data.draft_date
        draft_month = draft_data.input_date
    except:
        draft_date = 'There is no data draft yet!'
        draft_month = False
    params = {'public_date':public_date,'draft_date':draft_date,
              'public_month':public_month,'draft_month':draft_month}

    if request.method == 'POST':
        month_cal = request.POST.get('month', None)
        print(month_cal, '<----------------------------')
        if month_cal != '':
            data = month_cal.split('-')
            year = data[0]
            month = data[1]
            month_cal += '-01'
            request.session['month'] = month
            request.session['year'] = year
            today_date = datetime.now().date()

            results = sharing_bonus.objects.filter(input_date__month=month,
                                                                           input_date__year=year).delete()
            all_titles = title_qualification_calculation_model.objects.filter(date_model__month = month,date_model__year = year)
            sharing_bonus_how_many_point_per_self_pgbv_allocate = float(infinity_model.objects.latest('pk').how_many_point_per_self_pgbv_allocate)
            sb_index = float(infinity_model.objects.latest('pk').sb_bonus_pool) / 100

            for i in all_titles:
                if i.current_month_qualification in list_levels:
                    sharing_bonus_point = float(i.pgbv) * sharing_bonus_how_many_point_per_self_pgbv_allocate
                    sharing_bonus_value = sharing_bonus_point * sb_index
                    query_qs = sharing_bonus(user=i.user, input_date=month_cal, pgbv=i.pgbv, sharing_bonus_point=sharing_bonus_point,
                                             sharing_bonus_earned=sharing_bonus_value,
                                             draft_date=today_date)
                    query_qs.save()

            return render(request,'mlm_calculation/sharing_bonus.html',params)

    return render(request,'mlm_calculation/sharing_bonus.html',params)

'''
def calcaltion_sharing_bonus(request):
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
            request.session['month'] = month
            request.session['year'] = year
            today_date = datetime.now().date()

            results = sharing_bonus.objects.filter(input_date__month=month,
                                                                           input_date__year=year).delete()
            all_titles = title_qualification_calculation_model.objects.filter(date_model__month = month,date_model__year = year)
            all_pgpv = 0
            list_levels = ['Associate Director', 'Bronze Director', 'Silver Director', 'Gold Director',
                          'Platinum Director', 'Titanium Director', 'Sapphire Director',
                          'Jade Director', 'Crown Director', 'Emerald Director', 'Diamond Director',
                          'Black Diamond Director']
            for i in all_titles:
                if i.current_month_qualification in list_levels:
                    all_pgpv += i.pgpv
            return render(request,'mlm_calculation/sharing_bonus_front.html',{'sum_sharing_point' : all_pgpv})

    try:
        public_data = sharing_bonus.objects.filter(calculation_stage='Public')
        public_data = public_data.latest('pk')
        public_date = public_data.public_date
        public_month = public_data.input_date
    except:
        public_date = 'There is no data publish yet!'
        public_month = False
    try:
        draft_data = sharing_bonus.objects.filter(calculation_stage='Draft')
        draft_data = draft_data.latest('pk')
        draft_date = draft_data.draft_date
        draft_month = draft_data.input_date
    except:
        draft_date = 'There is no data draft yet!'
        draft_month = False
    params = {'public_date':public_date,'draft_date':draft_date,
              'public_month':public_month,'draft_month':draft_month}
    return render(request,'mlm_calculation/sharing_bonus.html',params)
'''


def after_sum_sharing_bonus(request):
    # checking if user has permission to view this page
    if not check_permission(request):
        return HttpResponse('<h1>You don\'t have permission to view this page</h1>')

    month = request.session['month']
    year = request.session['year']
    input_date = '01-' + month + '-' + year
    # sharing_bonus_point = request.get('sharing_bonus_point')
    index = request.POST.get('index',None)
    if index == None:
        index = 1
    try:
        index = float(index)
    except:
        index = 1
    today_date = datetime.now().date()
    all_titles = title_qualification_calculation_model.objects.filter(date_model__month = month,date_model__year = year)
    list_levels = ['Associate Director', 'Bronze Director', 'Silver Director', 'Gold Director',
                  'Platinum Director', 'Titanium Director', 'Sapphire Director',
                  'Jade Director', 'Crown Director', 'Emerald Director', 'Diamond Director',
                  'Black Diamond Director']

    for i in all_titles:
        if i.current_month_qualification in list_levels:
            sharing_bonus_value = float(i.pbv) * float(index)
            query_qs = sharing_bonus(user = i.user,input_date = input_date,pgbv = i.pgpv,sharing_bonus_point = i.pbv,sharing_bonus_earned = sharing_bonus_value,
                                     draft_date = today_date)
            query_qs.save()

    print('pass')
    return HttpResponse('<h1>Welcome to this window. It means your sharing bonus is calculated</h1>')


def sharing_bonus_excel(request):
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
            response['content-Disposition'] = 'attachment; filename = Sharing Bonus' + str(datetime.now()) + '.xls'
            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('Expenses')
            row_num = 0
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            columns = ['pk', 'user', 'created_on','input_date', 'calculation_stage','is_user_qualified_director','pgbv',
                       'sharing_bonus_point','sharing_bonus_earned','sharing_bonus_paid','sharing_bonus_balance_payable',
                       'draft_date', 'public_date']
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)
            font_style = xlwt.XFStyle()
            # print(to_date)
            # print(from_date)
            rows = sharing_bonus.objects.filter(input_date__month = month,input_date__year = year).values_list(
                'pk',
                'user__username', 'created_on','input_date', 'calculation_stage','is_user_qualified_director','pgbv',
                       'sharing_bonus_point','sharing_bonus_earned','sharing_bonus_paid','sharing_bonus_balance_payable',
                       'draft_date', 'public_date')
            if len(rows)< 1:
                messages.success(request, 'This month Sharing Bonus is not Calculated!')
                return redirect('mlm_calculation_sharig_bonus')
            print(rows, 'here we are geting the data that is going to print in excel sheet')
            print(len(rows), 'here we are geting the length of data')
            for row in rows:
                row_num += 1
                counting_sale_type = 0
                for col_num in range(len(row)):
                    ws.write(row_num, col_num, str(row[col_num]), font_style)
            wb.save(response)
            return response

    messages.success(request, 'This month Sharing Bonus is not Calculated!')
    return redirect('mlm_calculation_sharig_bonus')


def sharing_bonus_publish(request):
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
            value = sharing_bonus.objects.filter(input_date__month=month, input_date__year=year,calculation_stage = 'Draft').exists()
            if value == True:
                data_qs = sharing_bonus.objects.filter(input_date__month = month,input_date__year = year ).update(public_date = today_date,
                                                                                                                            calculation_stage = 'Public')
                messages.success(request, str(month_cal) +' ' + 'Data Published Successfully!')
            else:
                messages.success(request, str(month_cal) + ' ' + 'Data Allready Published!')

    return redirect('mlm_calculation_sharig_bonus')