from django.shortcuts import render, HttpResponse, get_object_or_404,redirect
from django.contrib import messages
import json
import xlwt
from datetime import datetime, date, timedelta
from shop.models import *
from accounts.models import *
from .forms import *
from .models import *
from realtime_calculation.models import RealTimeDetail
from .check_permit import check_permission
import ast


# Create your views here.
def calculation(request):
    # checking if user has permission to view this page
    if not check_permission(request):
        return HttpResponse('<h1>You don\'t have permission to view this page</h1>')

    # qs = get_object_or_404(pk = 1)
    query_qs = configurations.objects.last()
    form = ConfigurationForm(instance=query_qs)
    if request.method == 'POST':
        form = ConfigurationForm(request.POST)
        if form.is_valid():
            form = ConfigurationForm(instance=query_qs, data=request.POST, files=(request.FILES or None), )
            form.save()
        else:
            print(form.errors)
    distributors = Profile.objects.filter(distributor=True)
    return render(request, 'mlm_calculation/index.html', {'distributors': distributors, 'form': form})


def configurations_super(request):
    # checking if user has permission to view this page
    if not check_permission(request):
        return HttpResponse('<h1>You don\'t have permission to view this page</h1>')

    query_qs = super_model.objects.last()
    form = super_modelForm(instance=query_qs)
    if request.method == 'POST':
        form = super_modelForm(request.POST)
        if form.is_valid():
            form = super_modelForm(instance=query_qs, data=request.POST, files=(request.FILES or None), )
            form.save()
        else:
            print(form.errors)
    return render(request, 'mlm_calculation/test.html', {'form': form})


def configurations_infinity(request):
    # checking if user has permission to view this page
    if not check_permission(request):
        return HttpResponse('<h1>You don\'t have permission to view this page</h1>')

    query_qs = infinity_model.objects.last()
    form = infinity_modelForm(instance=query_qs)
    # form = infinity_modelForm()
    if request.method == 'POST':
        form = infinity_modelForm(request.POST)
        if form.is_valid():
            form = infinity_modelForm(instance=query_qs, data=request.POST, files=(request.FILES or None), )
            # form = infinity_modelForm( data=request.POST, files=(request.FILES or None), )
            form.save()
        else:
            print(form.errors)
    return render(request, 'mlm_calculation/test1.html', {'form': form})


from datetime import datetime

def super_team_building_bonus(request):
    # checking if user has permission to view this page
    if not check_permission(request):
        return HttpResponse('<h1>You don\'t have permission to view this page</h1>')

    if request.method == 'POST':
        month_cal = request.POST['month']
        TBBDistribution = request.POST.get('TBBDistribution')
        month_cal += '-01'
        data = month_cal.split('-')
        year = int(data[0])
        month = int(data[1])
        if month == 1:
            previous_year = int(year) - 1
            previous_month = 12
        else:
            previous_year = year
            previous_month = int(month) - 1
        tbbusers = ReferralCode.objects.filter()

        # allusers = User.objects.filter()
        today_date = datetime.now().date()
        prev_month_cal = date(int(previous_year), int(previous_month), 1)
        # In case of date mismatch.
        if prev_month_cal.month != previous_month or prev_month_cal.year != previous_year:
            prev_month_cal = prev_month_cal - timedelta(days=7)

        delete = team_building_bonus_super_plan_model.objects.filter(input_date__month=month,
                                                               input_date__year=year).delete()
        config_qs = configurations.objects.last()
        super_qs = super_model.objects.last()
        tbb_min_pv = super_qs.team_building_bonus_minimum_ppv
        tbb_capping = super_qs.team_building_bonus_capping
        
        total_tbb_points = 0
        
        for user in tbbusers:
            # u = user.filter(parent_id=user)
            qs = team_building_bonus_super_plan_model(user=user.user_id, input_date=month_cal, calculation_stage='Draft',
                                                      draft_date=today_date)
            try:
                prev_qs = team_building_bonus_super_plan_model.objects.get(user=user.user_id, input_date__month = previous_month, input_date__year = previous_year)
                remark1 = "1) TBB details found. "
            except:
                remark1 = "1) Previous Month TBB details not found. "
                prev_qs = team_building_bonus_super_plan_model(user=user.user_id, input_date = prev_month_cal)
                prev_qs.input_date = prev_month_cal
                prev_qs.cm_no_of_new_advisor_pv_in_left_position_referred_carry_forward = 0
                prev_qs.cm_no_of_new_advisor_pv_in_right_position_referred_carry_forward = 0
            
            # [Flow] Find value of left PPV & right PPV from realtime calculation of the user and continue the calculation
            rt_qs = RealTimeDetail.objects.filter(user_id__id=user.user_id.id, date__month=month, date__year=year)
            if rt_qs:
                rt_qs = rt_qs[0]
                remark2 = "2) Realtime Details found. "
                # print("Inside if rt_qs 1")
                userinleft_ppv = rt_qs.rt_left_pv_month
                userinright_ppv = rt_qs.rt_right_pv_month
            else:
                remark2 = "2) Realtime Details not found. "
                # print("Inside else rt_qs 1")
                userinleft_ppv = 0
                userinright_ppv = 0
                
            qs.cm_left_pv = userinleft_ppv
            qs.cm_right_pv = userinright_ppv
            
            tbb_points_left_bf = prev_qs.cm_no_of_new_advisor_pv_in_left_position_referred_carry_forward
            tbb_points_right_bf = prev_qs.cm_no_of_new_advisor_pv_in_right_position_referred_carry_forward
            
            userinleft_ppv = userinleft_ppv + tbb_points_left_bf
            userinright_ppv = userinright_ppv + tbb_points_right_bf
            
            # [Flow] Find TBB points (i.e. minimum of the two)
            if userinleft_ppv > userinright_ppv:
                remark3 = "3) Left PPV is more. "
                tbb_points = userinright_ppv
                tbb_points_left_cf = userinleft_ppv - userinright_ppv
                tbb_points_right_cf = 0
            elif userinleft_ppv < userinright_ppv:
                remark3 = "3) Right PPV is more. "
                tbb_points = userinleft_ppv
                tbb_points_left_cf = 0
                tbb_points_right_cf = userinright_ppv - userinleft_ppv
            elif userinleft_ppv == userinright_ppv:
                remark3 = "3) Both Side PPVs are equal. "
                tbb_points = userinright_ppv
                tbb_points_left_cf = 0
                tbb_points_right_cf = 0
            else:
                remark3 = "3) Neither Side PPV taken. "
                tbb_points = 0
                tbb_points_left_cf = 0
                tbb_points_right_cf = 0
            
            qs.bf_no_of_new_advisor_pv_in_left_position_referred = tbb_points_left_bf
            qs.bf_no_of_new_advisor_pv_in_right_position_referred = tbb_points_right_bf
            qs.cm_no_of_new_advisor_pv_in_left_position_referred_carry_forward = tbb_points_left_cf
            qs.cm_no_of_new_advisor_pv_in_right_position_referred_carry_forward = tbb_points_right_cf

            if rt_qs:
                # print("Inside if rt_qs 2")
                if rt_qs.rt_ppv < tbb_min_pv:
                    remark4 = "4) User Inactive. "
                    # AG :: To provide or not to provide tbb_points to inactive users
                    # Currently we will not provide tbb to inactive users
                    tbb_points = 0
                    qs.user_active = False
                else:
                    remark4 = "4) User Active. "
                    qs.user_active = True
            else:
                # print("Inside else rt_qs 2")
                remark4 = "4) Active Status not found. "
                # AG :: To provide or not to provide tbb_points to inactive users
                # Currently we will not provide tbb to inactive users
                tbb_points = 0
                qs.user_active = False
            
            qs.team_building_bonus_points = tbb_points
            qs.remarks = remark1 + remark2 + remark3 + remark4
            
            # qs.cm_no_of_new_advisor_in_left_position_referred = qs.total_no_of_new_advisor_in_left_position - pre_team_total_no_of_new_advisor_in_left_position
            # qs.cm_no_of_new_advisor_in_right_position_referred = qs.total_no_of_new_advisor_in_right_position - pre_team_total_no_of_new_advisor_in_right_position
            
            total_tbb_points = total_tbb_points + tbb_points
            qs.save()
            
        capping = float(tbb_capping)

        # tbb_active_users = team_building_bonus_super_plan_model.objects.filter(input_date__month=month,
        #                                                        input_date__year=year, user_active = True)
        tbb_active_users = team_building_bonus_super_plan_model.objects.filter(input_date__month=month,
                                                               input_date__year=year)

        run_capping_loop = True
        excess_tbb = 0.0
        while run_capping_loop:
            run_capping_loop = False
            TBBDistribution = float(TBBDistribution)
            total_tbb_points = float(total_tbb_points)
            if TBBDistribution > 0 and total_tbb_points > 0:
                tbbindex = TBBDistribution / total_tbb_points
            else:
                tbbindex = 0
            for user in tbb_active_users:
                tbb_till_now = float(user.team_building_bonus_earned)
                tbb = float(user.team_building_bonus_points) * float(tbbindex)
                total_tbb = tbb_till_now + tbb
                if total_tbb > capping:
                    excess_tbb = excess_tbb + (total_tbb - capping)
                    total_tbb = capping
                    total_tbb_points = total_tbb_points - float(user.team_building_bonus_points)
                    run_capping_loop = True
                    total_tbb_points = 0.0
                    user.team_building_bonus_capping = True
                
                user.team_building_bonus_earned = total_tbb
                user.save()
                
            if run_capping_loop:
                # tbb_active_users = team_building_bonus_super_plan_model.objects.filter(input_date__month=month,
                #                                                        input_date__year=year, user_active = True, team_building_bonus_capping = False)
                tbb_active_users = team_building_bonus_super_plan_model.objects.filter(input_date__month=month,
                                                                       input_date__year=year, team_building_bonus_capping = False)
                TBBDistribution = excess_tbb
        

    try:
        public_data = team_building_bonus_super_plan_model.objects.filter(calculation_stage='Public')
        public_data = public_data.latest('pk')
        public_date = public_data.public_date
        public_month = public_data.input_date

    except:
        public_date = 'There is no data publish yet!'
        public_month = False
    try:
        draft_data = team_building_bonus_super_plan_model.objects.filter(calculation_stage='Draft')
        draft_data = draft_data.latest('pk')
        draft_date = draft_data.draft_date
        draft_month = draft_data.input_date
    except:
        draft_date = 'There is no data draft yet!'
        draft_month = False
    params = {'public_date':public_date,'draft_date':draft_date,
              'public_month':public_month,'draft_month':draft_month}
    return render(request, 'mlm_calculation/team_building.html',params)

def team_building_bonus_excel(request):
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
            response['content-Disposition'] = 'attachment; filename = Team Building Bonus' + str(datetime.now()) + '.xls'
            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('Expenses')
            row_num = 0
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            columns = ['pk', 'user', 'ARN', 'Mobile', 'First Name', 'Last Name', 'created_on','input_date', 'calculation_stage','cm_left_pv', 'cm_right_pv',
                       'cm_left_bv','cm_right_bv','cm_no_of_new_advisor_in_left_position_referred','cm_no_of_new_advisor_in_right_position_referred',
                       'bf_no_of_new_advisor_pv_in_left_position_referred','bf_no_of_new_advisor_pv_in_right_position_referred',
                       'cm_no_of_new_advisor_pv_in_left_position_referred_carry_forward',
                        'cm_no_of_new_advisor_pv_in_right_position_referred_carry_forward','total_no_of_new_advisor_in_left_position',
                       'total_no_of_new_advisor_in_right_position','total_no_of_new_advisor_pv_in_left_position',
                        'total_no_of_new_advisor_pv_in_right_position','max_no_of_new_advisor_to_be_considered_in_left_position',
                        'max_no_of_new_advisor_to_be_considered_in_right_position','team_building_bonus_points','team_building_bonus_earned',
                        'team_building_bonus_paid','team_building_balance_payable','draft_date', 'public_date']
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)
            font_style = xlwt.XFStyle()
            # print(to_date)
            # print(from_date)
            rows = team_building_bonus_super_plan_model.objects.filter(input_date__month = month,input_date__year = year).values_list(
                        'pk',
                        'user__username', 'user__referralcode__referral_code', 'user_id__profile__phone_number',  'user_id__profile__first_name',
                        'user_id__profile__last_name','created_on','input_date', 'calculation_stage','cm_left_pv', 'cm_right_pv',
                       'cm_left_bv','cm_right_bv','cm_no_of_new_advisor_in_left_position_referred','cm_no_of_new_advisor_in_right_position_referred',
                       'bf_no_of_new_advisor_pv_in_left_position_referred','bf_no_of_new_advisor_pv_in_right_position_referred',
                       'cm_no_of_new_advisor_pv_in_left_position_referred_carry_forward',
                        'cm_no_of_new_advisor_pv_in_right_position_referred_carry_forward','total_no_of_new_advisor_in_left_position',
                       'total_no_of_new_advisor_in_right_position','total_no_of_new_advisor_pv_in_left_position',
                        'total_no_of_new_advisor_pv_in_right_position','max_no_of_new_advisor_to_be_considered_in_left_position',
                        'max_no_of_new_advisor_to_be_considered_in_right_position','team_building_bonus_points','team_building_bonus_earned',
                        'team_building_bonus_paid','team_building_balance_payable','draft_date', 'public_date')
            if len(rows)< 1:
                messages.success(request, 'This month Title Qualification is not Calculated!')
                return redirect('team_bonus')
            print(rows, 'here we are geting the data that is going to print in excel sheet')
            print(len(rows), 'here we are geting the length of data')
            for row in rows:
                row_num += 1
                counting_sale_type = 0
                for col_num in range(len(row)):
                    ws.write(row_num, col_num, str(row[col_num]), font_style)
            wb.save(response)
            return response

    messages.success(request, 'This month Title Qualification is not Calculated!')
    return redirect('team_bonus')

def team_building_bonus_publish(request):
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
            value = team_building_bonus_super_plan_model.objects.filter(input_date__month=month, input_date__year=year,calculation_stage = 'Draft').exists()
            if value == True:
                data_qs = team_building_bonus_super_plan_model.objects.filter(input_date__month = month,input_date__year = year ).update(public_date = today_date,
                                                                                                                            calculation_stage = 'Public')
                messages.success(request, str(month_cal) +' ' + 'Data Published Successfully!')
            else:
                messages.success(request, str(month_cal) + ' ' + 'Data Allready Published!')

    return redirect('team_bonus')

def calculate_ppv(ppv, referal_user, month, year, referred):
    r_user = referal_user.user_id.parent.filter(parent_id=referal_user.user_id)
    if len(r_user) > 0:
        for i in r_user:
            referred += 1
            pv = 0
            order = Order.objects.filter(email=i.user_id.email, date__month=month, date__year=year, paid=True)
            pv = sum([o.pv for o in order])
            ppv = ppv + pv
            value = calculate_ppv(ppv, i, month, year, referred)
            ppv = value[0]
            referred = value[1]
        return ppv, referred
    else:
        return ppv, referred





def differentiate_super_infinity(request):
    # checking if user has permission to view this page
    if not check_permission(request):
        return HttpResponse('<h1>You don\'t have permission to view this page</h1>')

    # This function is no longer required

    '''
    if request.method == 'POST':
        month_cal = request.POST.get('month', None)
        print(month_cal, '<----------------------------')
        if month_cal != '':
            data = month_cal.split('-')
            year = data[0]
            month = data[1]
            month_cal += '-01'
            today_date = datetime.now().date()
            tblusers = User.objects.filter()
            all_users = User.objects.filter()
            super_qs = super_model.objects.last()
            results = title_qualification_calculation_model.objects.filter(date_model__month=month,
                                                                           date_model__year=year).delete()
            # qlf_configurations = configurations.objects.last()
            # advisors = ['Associate Advisor','Advisor','Associate Manager','Manager']
            # director = ['Bronze Director','Silver Director','Gold Director','Platinum Director','Titanium Director','Sapphire Director','Jade Director','Crown Director','Emerald Director','Diamond Director','Black Diamond Director']
            for user in tblusers:
                print(results, '<---result')
                results = title_qualification_calculation_model.objects.filter(user=user)
                try:
                    pre_title_qlf = results.latest('pk')
                    pre_accumulated_ppv = pre_title_qlf.accumulated_ppv
                    pre_current_month_qualification = pre_title_qlf.current_month_qualification
                    print(type(pre_current_month_qualification), '<---------------------------------------')
                    pre_highest_qualification_ever = pre_title_qlf.highest_qualification_ever
                    print(type(pre_highest_qualification_ever), '<-----------------------high')
                except:
                    pre_accumulated_ppv = 0
                    pre_current_month_qualification = 'Blue Advisor'
                    pre_highest_qualification_ever = 'Blue Advisor'

                orders = Order.objects.filter(email=user.email, date__month=month, date__year=year, paid=True)
                pv = sum([li.pv for li in orders])
                bv = sum([li.bv for li in orders])
                if pre_current_month_qualification != 'Blue Advisor':
                    super_ppv = 0
                    super_pbv = 0
                    infinity_ppv = pv
                    infinity_pbv = bv


                else:
                    qualification_ppv = pre_accumulated_ppv + pv
                    if qualification_ppv < super_qs.purchase_pv:
                        super_ppv = pv
                        super_pbv = bv
                        infinity_ppv = 0
                        infinity_pbv = 0
                    else:
                        super_ppv = super_qs.purchase_pv - pre_accumulated_ppv
                        infinity_ppv = float(pv) - float(super_ppv)
                        if pv == 0:
                            pv = 1
                        super_pbv = (float(bv) * float(super_ppv)) / float(pv)
                        infinity_pbv = float(bv) - float(super_pbv)

                if super_ppv < 0:
                    super_ppv = 0
                elif super_pbv < 0:
                    super_pbv = 0
                elif infinity_ppv < 0:
                    infinity_ppv = 0
                elif infinity_pbv < 0:
                    infinity_pbv = 0
                accumulated_ppv = float(pre_accumulated_ppv) + float(pv)
                accumulated_pbv = float(pre_accumulated_ppv) + float(bv)
                qs = title_qualification_calculation_model(user=user, date_model=month_cal,
                                                           current_month_qualification=pre_current_month_qualification,
                                                           highest_qualification_ever=pre_highest_qualification_ever,
                                                           super_ppv=super_ppv, super_pbv=super_pbv,
                                                           infinity_ppv=infinity_ppv, infinity_pbv=infinity_pbv,
                                                           ppv=infinity_ppv, accumulated_ppv=accumulated_ppv, pbv=infinity_pbv,
                                                           accumulated_pbv=accumulated_pbv,draft_date = today_date)
                qs.save()
    '''
    try:
        public_data = title_qualification_calculation_model.objects.filter(calculation_stage='Public')
        public_data = public_data.latest('pk')
        public_date = public_data.public_date
        public_month = public_data.date_model
    except:
        public_date = 'There is no data publish yet!'
        public_month = False
    try:
        draft_data = title_qualification_calculation_model.objects.filter(calculation_stage='Draft')
        draft_data = draft_data.latest('pk')
        draft_date = draft_data.draft_date
        draft_month = draft_data.date_model
    except:
        draft_date = 'There is no data draft yet!'
        draft_month = False
    params = {'public_date' : public_date,
              'draft_date':draft_date,
              'public_month' : public_month,
              'draft_month' : draft_month
              }
    return render(request, 'mlm_calculation/differentiater_super_infinity.html',params)


def differentiate_super_infinity_excel(request):
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
            response['content-Disposition'] = 'attachment; filename = Title Qualification' + str(datetime.now()) + '.xls'
            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('Expenses')
            row_num = 0
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            columns = ['pk', 'user', 'ARN', 'Mobile',  'First Name',  'Last Name', 'date_model', 'calculation_stage', 'pgpv_pgbv_calculation_done', 'no_of_director_legs',
                       'is_there_a_qualified_director_in_the_group','pgpv', 'accumulated_pgpv',
                       'ppv', 'accumulated_ppv', 'pgbv', 'accumulated_pgbv','pbv', 'accumulated_pbv','gpv', 'accumulated_gpv',
                       'gbv','accumulated_gbv', 'tbv','accumulated_tbv', 'current_month_qualification' , 'tpv','accumulated_tpv',
                       'is_user_green', 'current_month_qualification', 'highest_qualification_ever','super_ppv','super_pbv',
                               'infinity_ppv', 'infinity_pbv','calculation']
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)
            font_style = xlwt.XFStyle()
            # print(to_date)
            # print(from_date)
            rows = title_qualification_calculation_model.objects.filter(date_model__month = month,date_model__year = year).values_list(
                    'pk',
                    'user__username', 'user__referralcode__referral_code', 'user_id__profile__phone_number',  'user_id__profile__first_name',  'user_id__profile__last_name',
                    'date_model', 'calculation_stage', 'pgpv_pgbv_calculation_done', 'no_of_director_legs',
                       'is_there_a_qualified_director_in_the_group','pgpv', 'accumulated_pgpv',
                       'ppv', 'accumulated_ppv', 'pgbv', 'accumulated_pgbv','pbv', 'accumulated_pbv','gpv', 'accumulated_gpv',
                       'gbv','accumulated_gbv', 'tbv','accumulated_tbv', 'current_month_qualification' , 'tpv','accumulated_tpv',
                       'is_user_green', 'current_month_qualification', 'highest_qualification_ever','super_ppv','super_pbv',
                               'infinity_ppv', 'infinity_pbv','calculation')
            if len(rows)< 1:
                messages.success(request, 'This month Title Qualification is not Calculated!')
                return redirect('differentiate_super_infinity')
            print(rows, 'here we are geting the data that is going to print in excel sheet')
            print(len(rows), 'here we are geting the length of data')
            for row in rows:
                row_num += 1
                counting_sale_type = 0
                for col_num in range(len(row)):
                    ws.write(row_num, col_num, str(row[col_num]), font_style)
            wb.save(response)
            return response

    messages.success(request, 'This month Title Qualification is not Calculated!')
    return redirect('differentiate_super_infinity')
    
def differentiate_super_infinity_publish(request):
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
            value = title_qualification_calculation_model.objects.filter(date_model__month=month, date_model__year=year,calculation_stage = 'Draft').exists()
            if value == True:
                data_qs = title_qualification_calculation_model.objects.filter(date_model__month = month,date_model__year = year ).update(public_date = today_date,
                                                                                                                            calculation_stage = 'Public')
                messages.success(request, str(month_cal) +' ' + 'Data Published Successfully!')
            else:
                messages.success(request, str(month_cal) + ' ' + 'Data Allready Published!')
    return redirect('differentiate_super_infinity')

def direct_bonus(request):  # step 2-direct bonus
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

            results = direct_bonus_super_plan_model.objects.filter(input_date__month=month,
                                                                           input_date__year=year).delete()
            tblusers = RealTimeDetail.objects.filter(date__month=month, date__year=year)
            super_qs = super_model.objects.last()
            percent_of_bv = float(super_qs.direct_bonus_bv) / 100
            direct_bonus_capping_per_new_sponsor = super_qs.direct_bonus_capping
            total_super_pbv = 0
            
            for user in tblusers:
                print("user is:")
                print(user)
                # all_refered_users = ReferralCode.objects.filter(referal_by=user)
                # total_super_pbv = total_super_pbv + float(user.rt_user_super_pbv)
                bonus = 0
                direct_bonus_user_wise_details = []
                
                bonus = float(user.rt_user_super_pbv) * percent_of_bv
                upline = ReferralCode.objects.filter(user_id=user.user_id).latest('pk').referal_by
                upline_direct_bonus_qs = direct_bonus_super_plan_model.objects.update_or_create(user = upline, input_date__month=month, input_date__year=year, 
                                                                                                defaults = {'user' : upline, 'input_date' : month_cal})[0]
                
                existing_direct_bonus = float(upline_direct_bonus_qs.direct_bonus_earned)
                upline_direct_bonus_qs.direct_bonus_earned = existing_direct_bonus + bonus
                
                existing_no_of_users_referred = float(upline_direct_bonus_qs.no_of_user_referred)
                upline_direct_bonus_qs.no_of_user_referred = existing_no_of_users_referred + 1.0
                
                if bonus > 0:
                    existing_no_of_new_users_referred = float(upline_direct_bonus_qs.no_of_new_user_referred)
                    upline_direct_bonus_qs.no_of_new_user_referred = existing_no_of_new_users_referred + 1.0
                
                if bonus > direct_bonus_capping_per_new_sponsor:
                    upline_direct_bonus_qs.direct_bonus_for_any_sponsor_exceeded_capping = True
                
                # [Flow] Saving user wise details:
                if bonus > 0:
                    if upline_direct_bonus_qs.direct_bonus_user_wise_details:
                        direct_bonus_user_wise_details = ast.literal_eval(upline_direct_bonus_qs.direct_bonus_user_wise_details)
                    direct_bonus_user_wise_details[str(user.user_id)] = str([float(user.rt_user_super_pbv),bonus])
                    upline_direct_bonus_qs.direct_bonus_user_wise_details = str(direct_bonus_user_wise_details)
                    
                upline_direct_bonus_qs.save()
                
                print(upline_direct_bonus_qs.direct_bonus_earned)
                
                # print(total_super_pbv)


        else:
            pass

    try:
        public_data = direct_bonus_super_plan_model.objects.filter(calculation_stage='Public')
        public_data = public_data.latest('pk')
        public_date = public_data.input_date
        public_month = public_data.input_date
    except:
        public_date = 'There is no data publish yet!'
        public_month = False
    try:
        draft_data = direct_bonus_super_plan_model.objects.filter(calculation_stage='Draft')
        draft_data = draft_data.latest('pk')
        draft_date = draft_data.input_date
        draft_month = draft_data.input_date
    except:
        draft_date = 'There is no data draft yet!'
        draft_month = False
    params = {'public_date':public_date,'draft_date':draft_date,
              'public_month':public_month,'draft_month':draft_month}
    return render(request, 'mlm_calculation/direct_bonus.html',params)


def direct_bonus_excel(request):
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
            response['content-Disposition'] = 'attachment; filename = Direct Bonus' + str(datetime.now()) + '.xls'
            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('Expenses')
            row_num = 0
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            columns = ['pk', 'user', 'created_on','input_date', 'calculation_stage','no_of_user_referred','no_of_new_user_referred',
                        'direct_bonus_for_any_sponsor_exceeded_capping','direct_bonus_earned',
                        'direct_bonus_paid','direct_bonus_balance_payable','direct_bonus_user_wise_details','draft_date', 'public_date']
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)
            font_style = xlwt.XFStyle()
            # print(to_date)
            # print(from_date)
            rows = direct_bonus_super_plan_model.objects.filter(input_date__month = month,input_date__year = year).values_list(
                'pk',
                'user__username', 'created_on','input_date', 'calculation_stage','no_of_user_referred','no_of_new_user_referred',
                        'direct_bonus_for_any_sponsor_exceeded_capping','direct_bonus_earned',
                        'direct_bonus_paid','direct_bonus_balance_payable','direct_bonus_user_wise_details','draft_date', 'public_date')
            if len(rows)< 1:
                messages.success(request, 'This month Title Qualification is not Calculated!')
                return redirect('direct_bonus')
            print(rows, 'here we are geting the data that is going to print in excel sheet')
            print(len(rows), 'here we are geting the length of data')
            for row in rows:
                row_num += 1
                counting_sale_type = 0
                for col_num in range(len(row)):
                    ws.write(row_num, col_num, str(row[col_num]), font_style)
            wb.save(response)
            return response

    messages.success(request, 'This month Title Qualification is not Calculated!')
    return redirect('direct_bonus')


def direct_bonus_publish(request):
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
            value = direct_bonus_super_plan_model.objects.filter(input_date__month=month, input_date__year=year,calculation_stage = 'Draft').exists()
            if value == True:
                data_qs = direct_bonus_super_plan_model.objects.filter(input_date__month = month,input_date__year = year ).update(public_date = today_date,
                                                                                                                            calculation_stage = 'Public')
                messages.success(request, str(month_cal) +' ' + 'Data Published Successfully!')
            else:
                messages.success(request, str(month_cal) + ' ' + 'Data Allready Published!')

    return redirect('direct_bonus')

def function_check_actual_field(direct_name):
    if direct_name == 'Blue Advisor':
        return 'blue_advisor'
    elif direct_name == 'Associate Advisor':
        return 'associate_advisor_accumulated_pgpv', 'associate_advisor_percent'
    elif direct_name == 'Advisor':
        return 'advisor_accumulated_pgpv', 'advisor_percent'
    elif direct_name == 'Associate Manager':
        return 'associate_manager_accumulated_pgpv', 'associate_manager_percent'
    elif direct_name == 'Manager':
        return 'manager_accumulated_pgpv', 'manager_percent'
    elif direct_name == 'Associate Director':
        return 'associate_director_accumulated_pgpv', 'associate_director_percent', 'associate_director_ppv', 'associate_director_pgpv', 'associate_director_legs'
    elif direct_name == 'Bronze Director':
        return 'bronze_director_ppv', 'bronze_director_pgpv', 'bronze_director_legs'
    elif direct_name == 'Silver Director':
        return 'silver_director_ppv', 'silver_director_pgpv', 'silver_director_legs'
    elif direct_name == 'Gold Director':
        return 'gold_director_ppv', 'gold_director_pgpv', 'gold_director_legs'
    elif direct_name == 'Platinum Director':
        return 'platinum_director_ppv', 'platinum_director_pgpv', 'platinum_director_legs'
    elif direct_name == 'Titanium Director':
        return 'titanium_director_ppv', 'titanium_director_pgpv', 'titanium_director_legs'
    elif direct_name == 'Sapphire Director':
        return 'sapphire_director_ppv', 'sapphire_director_pgpv', 'sapphire_director_legs'
    elif direct_name == 'Emerald Director':
        return 'emerald_director_ppv', 'emerald_director_pgpv', 'emerald_director_legs'
    elif direct_name == 'Jade Director':
        return 'jade_director_ppv', 'jade_director_pgpv', 'jade_director_legs'
    elif direct_name == 'Crown Director':
        return 'crown_director_ppv', 'crown_director_pgpv', 'crown_director_legs'
    elif direct_name == 'Diamond Director':
        return 'diamond_director_ppv', 'diamond_director_pgpv', 'diamond_director_legs'
    elif direct_name == 'Black Diamond Director':
        return 'black_diamond_director_ppv', 'black_diamond_director_pgpv', 'black_diamond_director_legs'


def test_my_skill(request):
    # checking if user has permission to view this page
    if not check_permission(request):
        return HttpResponse('<h1>You don\'t have permission to view this page</h1>')

    orders = Order.objects.filter(email=request.user.email).values_list('email', flat=True)
    # d_orders = []
    # for ord in orders:
    #     d_orders.append( ord['email'])
    orders = list(orders)
    print(type(orders))
    orders = str(orders)
    print(len(orders))
    orders = orders.replace('[', '')
    orders = orders.replace(']', '')
    print(len(orders))
    print(orders)
    return HttpResponse(orders)
    # user_names = list(Order.objects.all().values_list('email', flat=True))
    # print(user_names)
    # return HttpResponse(user_names)


def leadership_level_calculation(user, month, year):
    total_tbb_of_this_level = 0.0
    downlines = ReferralCode.objects.filter(referal_by=user)
    if downlines:
        print(downlines)
        for downline in downlines:
            print(downline)
            lbb_downline = team_building_bonus_super_plan_model.objects.get(user = downline.user_id, input_date__month=month, input_date__year=year).team_building_bonus_earned
            total_tbb_of_this_level = float(total_tbb_of_this_level) + float(lbb_downline)
            print("Inside Function")
            print(lbb_downline)
            print(total_tbb_of_this_level)
    return total_tbb_of_this_level

def leader_ship_bonus_super_plan(request):
    # checking if user has permission to view this page
    if not check_permission(request):
        return HttpResponse('<h1>You don\'t have permission to view this page</h1>')

    # user = request.user
    # r_users = ReferralCode.objects.all()
    if request.method == 'POST':
        month_cal = request.POST.get('month', None)
        print(month_cal, '<----------------------------')
        if month_cal != '':
            data = month_cal.split('-')
            year = data[0]
            month = data[1]
            month_cal += '-01'
            today_date = datetime.now().date()

            results = leadership_building_bonus_super_plan_model.objects.filter(input_date__month=month,
                                                                           input_date__year=year).delete()
            # [Flow] Dynamic Compression or Referral Code
            tbl_dynamic_active_users = ReferralCode.objects.filter()
            # tbl_dynamic_active_users = dynamic_compression_active.objects.filter(input_date__month=month,
            #                                                                      input_date__year=year)
            super_qs = super_model.objects.last()
            
            lifestyle_fund_as_a_perc_of_lbb = float(super_qs.life_style_fund_tbb) / 100
            
            cal_amnt_1st_downline = super_qs.level_1st_downline
            cal_amnt_2nd_downline = super_qs.level_2nd_downline
            cal_amnt_3rd_downline = super_qs.level_3rd_downline
            cal_amnt_4th_downline = super_qs.level_4th_downline
            cal_amnt_5th_downline = super_qs.level_5th_downline
            for tbl_active in tbl_dynamic_active_users:
                lbb_level_1_earned = 0.0
                lbb_level_2_earned = 0.0
                lbb_level_3_earned = 0.0
                lbb_level_4_earned = 0.0
                lbb_level_5_earned = 0.0
                
                lbb_level_1_earned = leadership_level_calculation(tbl_active.user_id, month, year)
                
                level_1 = ReferralCode.objects.filter(referal_by=tbl_active.user_id)
                for downline_2 in level_1:
                    lbb_downline_2_earned = leadership_level_calculation(downline_2.user_id, month, year)
                    lbb_level_2_earned = float(lbb_level_2_earned) + float(lbb_downline_2_earned)
                    
                    level_2 = ReferralCode.objects.filter(referal_by=tbl_active.user_id)
                    for downline_3 in level_2:
                        lbb_downline_3_earned = leadership_level_calculation(downline_3.user_id, month, year)
                        lbb_level_3_earned = float(lbb_level_3_earned) + float(lbb_downline_3_earned)
                        
                        level_3 = ReferralCode.objects.filter(referal_by=tbl_active.user_id)
                        for downline_4 in level_3:
                            lbb_downline_4_earned = leadership_level_calculation(downline_4.user_id, month, year)
                            lbb_level_4_earned = float(lbb_level_4_earned) + float(lbb_downline_4_earned)
                            
                            level_4 = ReferralCode.objects.filter(referal_by=tbl_active.user_id)
                            for downline_5 in level_4:
                                lbb_downline_5_earned = leadership_level_calculation(downline_5.user_id, month, year)
                                lbb_level_5_earned = float(lbb_level_5_earned) + float(lbb_downline_5_earned)
                
                total_1_bonus = lbb_level_1_earned * float(cal_amnt_1st_downline)/100
                total_2_bonus = lbb_level_2_earned * float(cal_amnt_2nd_downline)/100
                total_3_bonus = lbb_level_3_earned * float(cal_amnt_3rd_downline)/100
                total_4_bonus = lbb_level_4_earned * float(cal_amnt_4th_downline)/100
                total_5_bonus = lbb_level_5_earned * float(cal_amnt_5th_downline)/100
                
                leadership_building_bonus_earned = float(total_1_bonus) + float(total_2_bonus) + float(total_3_bonus) + float(total_4_bonus) + float(total_5_bonus)
                save_data_qs = leadership_building_bonus_super_plan_model(user = tbl_active.user_id,input_date = month_cal,
                            all_first_immediate_active_advisor_tbb = lbb_level_1_earned, all_second_immediate_active_advisor_tbb = lbb_level_2_earned,
                        all_third_immediate_active_advisor_tbb = lbb_level_3_earned, all_fourth_immediate_active_advisor_tbb = lbb_level_4_earned,
                        all_fifth_immediate_active_advisor_tbb = lbb_level_5_earned, draft_date = today_date,
                        bonus_from_all_first_immediate_active_advisor = total_1_bonus,bonus_from_all_second_immediate_active_advisor = total_2_bonus,
                        bonus_from_all_third_immediate_active_advisor = total_3_bonus,bonus_from_all_fourth_immediate_active_advisor = total_4_bonus,
                        bonus_from_all_fifth_immediate_active_advisor = total_5_bonus,leadership_building_bonus_earned = leadership_building_bonus_earned
                                                                          )
                
                # [Flow] Calculating Lifestyle Fund Simultaneously 
                lifestyle_fund_earned = leadership_building_bonus_earned * lifestyle_fund_as_a_perc_of_lbb
                
                lifestyle_qs = life_style_fund_super_plan_model(user = tbl_active.user_id,input_date = month_cal,leadership_building_bonus_earned = lifestyle_fund_earned,
                                                 life_style_fund_earned = lifestyle_fund_earned,draft_date = today_date)
                save_data_qs.save()
                lifestyle_qs.save()

        else:
            pass
    try:
        public_data = leadership_building_bonus_super_plan_model.objects.filter(calculation_stage='Public')
        public_data = public_data.latest('pk')
        public_date = public_data.public_date
        public_month = public_data.input_date

    except:
        public_date = 'There is no data publish yet!'
        public_month = False
    try:
        draft_data = leadership_building_bonus_super_plan_model.objects.filter(calculation_stage='Draft')
        draft_data = draft_data.latest('pk')
        draft_date = draft_data.draft_date
        draft_month = draft_data.input_date
    except:
        draft_date = 'There is no data draft yet!'
        draft_month = False
    params = {'public_date':public_date,'draft_date':draft_date,
              'public_month' : public_month,'draft_month' : draft_month}
    return render(request, 'mlm_calculation/leadership_building.html',params)


def leader_ship_building_bonus_excel(request):
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
            response['content-Disposition'] = 'attachment; filename = Leader Ship Building Bonus' + str(datetime.now()) + '.xls'
            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('Expenses')
            row_num = 0
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            columns = ['pk', 'user', 'created_on','input_date', 'calculation_stage','all_first_immediate_active_advisor_tbb',
                       'bonus_from_all_first_immediate_active_advisor','all_second_immediate_active_advisor_tbb',
                       'bonus_from_all_second_immediate_active_advisor','all_third_immediate_active_advisor_username',
                       'all_third_immediate_active_advisor_tbb',
                       'bonus_from_all_third_immediate_active_advisor','all_fourth_immediate_active_advisor_username',
                       'all_fourth_immediate_active_advisor_tbb',
            'bonus_from_all_fourth_immediate_active_advisor','all_fifth_immediate_active_advisor_username',
                       'all_fifth_immediate_active_advisor_tbb','bonus_from_all_fifth_immediate_active_advisor',
            'leadership_building_bonus_earned','leadership_building_bonus_paid',
            'leadership_building_bonus_balance_payable','draft_date', 'public_date']
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)
            font_style = xlwt.XFStyle()
            # print(to_date)
            # print(from_date)
            rows = leadership_building_bonus_super_plan_model.objects.filter(input_date__month = month,input_date__year = year).values_list(
                'pk',
                'user__username', 'created_on','input_date', 'calculation_stage','all_first_immediate_active_advisor_tbb',
                       'bonus_from_all_first_immediate_active_advisor','all_second_immediate_active_advisor_tbb',
                       'bonus_from_all_second_immediate_active_advisor','all_third_immediate_active_advisor_username',
                       'all_third_immediate_active_advisor_tbb',
                       'bonus_from_all_third_immediate_active_advisor','all_fourth_immediate_active_advisor_username',
                       'all_fourth_immediate_active_advisor_tbb',
            'bonus_from_all_fourth_immediate_active_advisor','all_fifth_immediate_active_advisor_username',
                       'all_fifth_immediate_active_advisor_tbb','bonus_from_all_fifth_immediate_active_advisor',
            'leadership_building_bonus_earned','leadership_building_bonus_paid',
            'leadership_building_bonus_balance_payable','draft_date', 'public_date')
            if len(rows)< 1:
                messages.success(request, 'This month Leader Ship Bonus is not Calculated!')
                return redirect('leadership_bonus')
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
    return redirect('leadership_bonus')


def leader_ship_building_bonus_publish(request):
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
            value = leadership_building_bonus_super_plan_model.objects.filter(input_date__month=month, input_date__year=year,calculation_stage = 'Draft').exists()
            if value == True:
                data_qs = leadership_building_bonus_super_plan_model.objects.filter(input_date__month = month,input_date__year = year ).update(public_date = today_date,
                                                                                                                            calculation_stage = 'Public')
                messages.success(request, str(month_cal) +' ' + 'Data Published Successfully!')
            else:
                messages.success(request, str(month_cal) + ' ' + 'Data Allready Published!')

    return redirect('leadership_bonus')

def life_style_fund_super_plan_fn(request):
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

            results = life_style_fund_super_plan_model.objects.filter(input_date__month=month,
                                                                           input_date__year=year).delete()
            tbl_leaders = leadership_building_bonus_super_plan_model.objects.filter(input_date__month=month,
                                                                                 input_date__year=year)
            super_qs = super_model.objects.last()
            cal_life_style_bonus = super_qs.life_style_fund_tbb
            for leader in tbl_leaders:
                query_delete = life_style_fund_super_plan_model.objects.filter(user= leader.user,
                                                                                         input_date__month=month,
                                                                                         input_date__year=year).delete()
                earned_bonus = leader.leadership_building_bonus_earned
                life_style_bonus = float(earned_bonus) * float(cal_life_style_bonus)/100
                query_qs = life_style_fund_super_plan_model(user = leader.user,input_date = month_cal,leadership_building_bonus_earned = earned_bonus,
                                                 life_style_fund_earned = life_style_bonus,draft_date = today_date)
                query_qs.save()

    try:
        public_data = life_style_fund_super_plan_model.objects.filter(calculation_stage='Public')
        public_data = public_data.latest('pk')
        public_date = public_data.public_date
        public_month = public_data.input_date
    except:
        public_date = 'There is no data publish yet!'
        public_month = False
    try:
        draft_data = life_style_fund_super_plan_model.objects.filter(calculation_stage='Draft')
        draft_data = draft_data.latest('pk')
        draft_date = draft_data.draft_date
        draft_month = draft_data.input_date
    except:
        draft_date = 'There is no data draft yet!'
        draft_month = False
    params = {'public_date':public_date,'draft_date':draft_date,'public_month':public_month,'draft_month':draft_month}
    return render(request, 'mlm_calculation/life_style_bonus.html',params)


def life_style_fund_super_plan_excel(request):
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
            response['content-Disposition'] = 'attachment; filename = Life Style Fund Bonus' + str(datetime.now()) + '.xls'
            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('Expenses')
            row_num = 0
            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            columns = ['pk', 'user', 'created_on','input_date', 'calculation_stage','leadership_building_bonus_earned',
                       'life_style_fund_earned','life_style_fund_paid',
                       'life_style_fund_payable','draft_date', 'public_date']
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)
            font_style = xlwt.XFStyle()
            # print(to_date)
            # print(from_date)
            rows = life_style_fund_super_plan_model.objects.filter(input_date__month = month,input_date__year = year).values_list(
                'pk',
                'user__username', 'created_on','input_date', 'calculation_stage','leadership_building_bonus_earned',
                       'life_style_fund_earned','life_style_fund_paid',
                       'life_style_fund_payable','draft_date', 'public_date')
            if len(rows)< 1:
                messages.success(request, 'This month Leader Ship Bonus is not Calculated!')
                return redirect('life_style')
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
    return redirect('life_style')


def life_style_fund_super_plan_publish(request):
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
            value = life_style_fund_super_plan_model.objects.filter(input_date__month=month, input_date__year=year,calculation_stage = 'Draft').exists()
            if value == True:
                data_qs = life_style_fund_super_plan_model.objects.filter(input_date__month = month,input_date__year = year ).update(public_date = today_date,
                                                                                                                            calculation_stage = 'Public')
                messages.success(request, str(month_cal) +' ' + 'Data Published Successfully!')
            else:
                messages.success(request, str(month_cal) + ' ' + 'Data Allready Published!')

    return redirect('life_style')


#def delete_Data(request):
#    data_qs = User.objects.filter(pk__gte = 251).delete()
#    return HttpResponse('<h1>Nipur data delteed succesfully</h1>')
