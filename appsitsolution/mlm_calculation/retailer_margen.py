from .models import *
from django.shortcuts import render,HttpResponse,redirect
from django.contrib import messages
import json
import xlwt

from datetime import datetime
from .check_permit import check_permission


def retailer_margin_fn(request):
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
            results = retail_margin.objects.filter(input_date__month=month,
                                                                           input_date__year=year).delete()
            all_titles = title_qualification_calculation_model.objects.filter(date_model__month = month,date_model__year = year)
            infinity_qs = infinity_model.objects.last()
            percentage_loyalty_given = infinity_qs.percentage_loyalty_given
            for title in all_titles:
                user_total_margen = 0
                orders = Order.objects.filter(name = title.user.username,date__month = month,date__year = year)
                lineitems = LineItem.objects.filter(order__in = orders)
                for item  in lineitems:
                    try:
                        mrp = item.batch.mrp
                        mrp = float(mrp)
                    except:
                        mrp = 0
                    price = float(item.price)
                    margin = (mrp - price)
                    user_total_margen += margin
                retail_qs = retail_margin(user = title.user,input_date = month_cal,retail_margin = user_total_margen,draft_date = today_date)
                retail_qs.save()
            return HttpResponse('<h1>Wellcome auteticser! IF you are at this page it means Retailer Bonus is calculated Successfully!!!</h1>')


    try:
        public_data = retail_margin.objects.filter(calculation_stage='Public')
        public_data = public_data.latest('pk')
        public_date = public_data.public_date
        public_month = public_data.input_date
    except:
        public_date = 'There is no data publish yet!'
        public_month = False
    try:
        draft_data = retail_margin.objects.filter(calculation_stage='Draft')
        draft_data = draft_data.latest('pk')
        draft_date = draft_data.draft_date
        draft_month = draft_data.input_date

    except:
        draft_date = 'There is no data draft yet!'
        draft_month = False
    params = {'public_date':public_date,'draft_date':draft_date,
              'draft_month':draft_month,'public_month':public_month}
    return render(request,'mlm_calculation/retailer_bonus.html',params)


def retailer_margin_excel(request):
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
            response['content-Disposition'] = 'attachment; filename = Retailer Margin' + str(datetime.now()) + '.xls'
            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('Expenses')
            row_num = 0
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            columns = ['pk', 'user', 'created_on','input_date', 'calculation_stage','retail_margin','draft_date', 'public_date']
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)
            font_style = xlwt.XFStyle()
            # print(to_date)
            # print(from_date)
            rows = retail_margin.objects.filter(input_date__month = month,input_date__year = year).values_list(
                'pk',
                'user__username','created_on','input_date', 'calculation_stage','retail_margin','draft_date', 'public_date'
            )
            if len(rows)< 1:
                messages.success(request, 'This month Leader Ship Bonus is not Calculated!')
                return redirect('mlm_calculation_retail_margin')
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
    return redirect('mlm_calculation_retail_margin')


def retailer_margin_publish(request):
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
            value = retail_margin.objects.filter(input_date__month=month, input_date__year=year,calculation_stage = 'Draft').exists()
            if value == True:
                data_qs = retail_margin.objects.filter(input_date__month = month,input_date__year = year ).update(public_date = today_date,
                                                                                                                            calculation_stage = 'Public')
                messages.success(request, str(month_cal) +' ' + 'Data Published Successfully!')
            else:
                messages.success(request, str(month_cal) + ' ' + 'Data Allready Published!')

    return redirect('mlm_calculation_retail_margin')