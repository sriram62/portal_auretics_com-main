from .models import *
from django.shortcuts import render,HttpResponse,redirect
from django.contrib import messages
import json
import xlwt
from datetime import datetime
from .check_permit import check_permission

def calcaltion_fortune_bonus(request):
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
            results = fortune_bonus.objects.filter(input_date__month=month, input_date__year=year).delete()
            configurations_qs = configurations.objects.last()
            infinity_qs = infinity_model.objects.last()
            minimum_percetnage = infinity_qs.how_many_advisor_select
            given_pv = infinity_qs.how_much_pv_give
            personal_member = personal_bonus.objects.filter(input_date__month = month,user_active = True).count()
            members = personal_member * minimum_percetnage / 100
            cal_value = personal_member * given_pv / 100
            member = int(members)
            personal_bonuses = personal_bonus.objects.filter(input_date__month = month).order_by('?')[member:]
            for i in personal_bonuses:
                actual_personal_bonus = i.personal_bonus_earned * cal_value
                fortu_qs = fortune_bonus(user = i.user,input_date = month_cal,user_active = i.user_active,personal_bonus = i.personal_bonus_earned,
                              fortune_bonus_earned = actual_personal_bonus,draft_date = today_date)
                fortu_qs.save()
            print(personal_bonuses,'first 10 objects will get in this list')


    try:
        public_data = fortune_bonus.objects.filter(calculation_stage='Public')
        public_data = public_data.latest('pk')
        public_date = public_data.public_date
        public_month = public_data.input_date
    except:
        public_date = 'There is no data publish yet!'
        public_month = False
    try:
        draft_data = fortune_bonus.objects.filter(calculation_stage='Draft')
        draft_data = draft_data.latest('pk')
        draft_date = draft_data.draft_date
        draft_month = draft_data.input_date
    except:
        draft_date = 'There is no data draft yet!'
        draft_month = False
    params = {'public_date':public_date,'draft_date':draft_date,
              'public_month':public_month,'draft_month':draft_month}
    return render(request,'mlm_calculation/fortune_bonus.html',params)



def fortune_excel(request):
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
            response['content-Disposition'] = 'attachment; filename = Fortune Bonus' + str(datetime.now()) + '.xls'
            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('Expenses')
            row_num = 0
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            columns = ['pk', 'user', 'created_on','input_date', 'calculation_stage','wheather_Selected','personal_bonus',
                       'fortune_bonus_earned','fortune_bonus_paid','fortune_bonus_balance_payable',
                       'draft_date', 'public_date']
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)
            font_style = xlwt.XFStyle()
            # print(to_date)
            # print(from_date)
            rows = fortune_bonus.objects.filter(input_date__month = month,input_date__year = year).values_list(
                'pk',
                'user__username', 'created_on','input_date', 'calculation_stage','wheather_Selected','personal_bonus',
                       'fortune_bonus_earned','fortune_bonus_paid','fortune_bonus_balance_payable',
                       'draft_date', 'public_date')
            if len(rows)< 1:
                messages.success(request, 'This month Leader Ship Bonus is not Calculated!')
                return redirect('mlm_calculation_fortune_bonus')
            print(rows, 'here we are geting the data that is going to print in excel sheet')
            print(len(rows), 'here we are geting the length of data')
            for row in rows:
                row_num += 1
                counting_sale_type = 0
                for col_num in range(len(row)):
                    ws.write(row_num, col_num, str(row[col_num]), font_style)
            wb.save(response)
            return response

    messages.success(request, 'This month Leader Ship Bonus is not Calculated!')
    return redirect('mlm_calculation_fortune_bonus')


def fortune_publish(request):
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
            value = fortune_bonus.objects.filter(input_date__month=month, input_date__year=year,calculation_stage = 'Draft').exists()
            if value == True:
                data_qs = fortune_bonus.objects.filter(input_date__month = month,input_date__year = year ).update(public_date = today_date,
                                                                                                                            calculation_stage = 'Public')
                messages.success(request, str(month_cal) +' ' + 'Data Published Successfully!')
            else:
                messages.success(request, str(month_cal) + ' ' + 'Data Allready Published!')

    return redirect('mlm_calculation_fortune_bonus')