from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Sum

from accounts.models import ReferralCode
from shop.models import Material_center, Order
from realtime_calculation.models import RealTimeDetail, RealTimeOrder, RealTimeUser, RealTimeOrderAudit
from mlm_calculation.models import title_qualification_calculation_model, configurations, super_model, infinity_model, team_building_bonus_super_plan_model
from mlm_calculation.check_permit import check_permission

from datetime import datetime, timedelta
from decimal import Decimal

from django.http import HttpResponse


power_centers_ids = [3, 6, ]
low_power_pv = 10000
stock_variance_ids = [592, 9384]


def get_child_from_userid(userid):
    child = ReferralCode.objects.filter(parent_id_id=userid).first()
    # print("child")
    if child is not None:
        childId = child.user_id_id
        # print(childId)
        return ReferralCode.objects.filter(user_id=childId).first()
    # print("none")
    return None


def build_tree():
    activeUsers = []
    try:

        activeUsers = User.objects.filter(is_active=True)
        # print(len(activeUsers))
        for activeUser in activeUsers:
            left_users = 0
            right_users = 0
            print("user")
            print(activeUser.id)
            chhildUser = get_child_from_userid(activeUser.id)

            while chhildUser is not None:
                pid = chhildUser.user_id_id
                if chhildUser.position == 'LEFT':
                    left_users += 1
                if chhildUser.position == 'RIGHT':
                    right_users += 1
                chhildUser = get_child_from_userid(pid)
            print("left_users")
            print(left_users)
            print("right_users")
            print(right_users)
            activeUser.rt_left_new_users = left_users
            activeUser.rt_right_new_users = right_users
            activeUser.save()
            print("saved to db")
            break
    except Exception as e:
        print(e)


def get_sum(orders):
    total_bv = 0.0
    total_pv = 0.0
    for order in orders:
        total_pv = total_pv + order.pv
        total_bv = total_bv + order.bv

    return total_pv, total_bv


def get_orders(child, time_span):
    if time_span == "day":
        orders = Order.objects.filter(
            email=child.user_id.email,
            date__day=datetime.now().day,
            date__year=year,
            paid=True,
            delete=False,
            loyalty_order=False,
        ).exclude(status=8)
    elif time_span == "month":
        orders = Order.objects.filter(
            email=child.user_id.email,
            date__month=month,
            date__year=year,
            paid=True,
            delete=False,
            loyalty_order=False,
        ).exclude(status=8)
    return orders


def get_new_users(request, time_span, user_position):
    new_user = 0
    if time_span == "day":
        new_user = ReferralCode.objects.filter(
            referal_by=request.user,
            position=user_position,
            created_on__day=datetime.now().day,
            created_on__year=year
        )
    elif time_span == "month":
        new_user = ReferralCode.objects.filter(
            referal_by=request.user,
            position=user_position,
            created_on__month=month,
            created_on__year=year
        )
    return new_user


@login_required(login_url='home')
def calculate(request):
    left_child = ReferralCode.objects.filter(
        parent_id=request.user,
        position='LEFT'
    ).latest('pk')
    right_child = ReferralCode.objects.filter(
        parent_id=request.user,
        position='RIGHT'
    ).latest('pk')
    if left_child:
        orders = get_orders(left_child, "day")
        rt_left_pv_today, rt_left_bv_today = get_sum(orders)
        orders = get_orders(left_child, "month")
        rt_left_pv_month, rt_left_bv_month = get_sum(orders)
    if right_child:
        orders = get_orders(right_child, "day")
        rt_right_pv_today, rt_right_bv_today = get_sum(orders)
        orders = get_orders(right_child, "month")
        rt_right_pv_month, rt_right_bv_month = get_sum(orders)

    rt_left_new_users_today = get_new_users(request, "day", "LEFT")
    rt_right_new_users_today = get_new_users(request, "day", "RIGHT")
    rt_new_direct_sponsors_today = rt_left_new_users_today + rt_right_new_users_today

    rt_left_new_users_month = get_new_users(request, "month", "LEFT")
    rt_right_new_users_month = get_new_users(request, "month", "RIGHT")
    rt_new_direct_sponsors_month = rt_left_new_users_month + rt_right_new_users_month


def delete_rt_calculation(month, year):
    delete_existing_data_RealTimeDetail = RealTimeDetail.objects.filter(date__month=month, date__year=year).delete()
    delete_existing_data_RealTimeOrder = RealTimeOrder.objects.filter(date__month=month, date__year=year).delete()
    delete_existing_data_RealTimeUser = RealTimeUser.objects.filter(date__month=month, date__year=year).delete()
    delete_existing_data_RealTimeOrderAudit = RealTimeOrderAudit.objects.filter(date__month=month,
                                                                                date__year=year).delete()


def create_rt_detail(parent, position, pv, bv, dp, month, year, date):
    # print("running super")
    order_detail_qs = RealTimeDetail.objects.update_or_create(user_id=parent, date__month=month, date__year=year,
                                                              defaults={'user_id': parent, 'date': date})[0]
    order_detail_qs.date = date

    if position == "LEFT":
        order_detail_qs.rt_left_pv_month = float(order_detail_qs.rt_left_pv_month) + pv
        order_detail_qs.rt_left_bv_month = float(order_detail_qs.rt_left_bv_month) + bv
        order_detail_qs.rt_left_dp_month = float(order_detail_qs.rt_left_dp_month) + dp
    elif position == "RIGHT":
        order_detail_qs.rt_right_pv_month = float(order_detail_qs.rt_right_pv_month) + pv
        order_detail_qs.rt_right_bv_month = float(order_detail_qs.rt_right_bv_month) + bv
        order_detail_qs.rt_right_dp_month = float(order_detail_qs.rt_right_dp_month) + dp

    order_detail_qs.save()


def get_user_id_from_referral_id(username_of_referral):
    obj = ReferralCode.objects.get(referal_by=username_of_referral)
    # if username_of_referral != obj.user_id:
    # print("user mismatch")
    # print(username_of_referral, obj.user_id)
    return username_of_referral

def if_none_than_zero(value):
    if not value:
        value = 0.0
    return value

def add_pv_bv(current_user, pv, bv, dp, attribute, month, year, date):
    if not current_user:
        return False

    pv = if_none_than_zero(pv)
    bv = if_none_than_zero(bv)
    dp = if_none_than_zero(dp)

    qs = RealTimeDetail.objects.update_or_create(user_id=current_user, date__month=month, date__year=year, defaults=
    {'user_id': current_user, 'date': date})[0]
    qs.date = date

    if "rt_gv_month" in attribute:
        qs.rt_gpv_month = float(qs.rt_gpv_month) + pv
        qs.rt_gbv_month = float(qs.rt_gbv_month) + bv
        add_pv_bv(current_user, pv, bv, dp, ["rt_tv_month", ], month, year, date)
    if "rt_p" in attribute:
        qs.rt_ppv = float(qs.rt_ppv) + pv
        qs.rt_pbv = float(qs.rt_pbv) + bv
    if "rt_user_infinity" in attribute:
        qs.rt_user_infinity_ppv = float(qs.rt_user_infinity_ppv) + pv
        qs.rt_user_infinity_pbv = float(qs.rt_user_infinity_pbv) + bv
    if "rt_user_super" in attribute:
        qs.rt_user_super_ppv = float(qs.rt_user_super_ppv) + pv
        qs.rt_user_super_pbv = float(qs.rt_user_super_pbv) + bv
    if "rt_tv_month" in attribute:
        qs.rt_tpv_month = float(qs.rt_tpv_month) + pv
        qs.rt_tbv_month = float(qs.rt_tbv_month) + bv
        qs.rt_tdp_month = float(qs.rt_tdp_month) + dp
    if "case_1" in attribute:
        qs.rt_audit_case_1_pv = float(qs.rt_audit_case_1_pv) + pv
        qs.rt_audit_case_1_bv = float(qs.rt_audit_case_1_bv) + bv
        qs.rt_is_user_green = True
    if "case_2" in attribute:
        qs.rt_audit_case_2_pv = float(qs.rt_audit_case_2_pv) + pv
        qs.rt_audit_case_2_bv = float(qs.rt_audit_case_2_bv) + bv
        qs.rt_is_user_green = True
    if "case_3_infinity" in attribute:
        qs.rt_audit_case_3_infinity_pv = float(qs.rt_audit_case_3_infinity_pv) + pv
        qs.rt_audit_case_3_infinity_bv = float(qs.rt_audit_case_3_infinity_bv) + bv
        qs.rt_is_user_green = True
    if "case_3_super" in attribute:
        qs.rt_audit_case_3_super_pv = float(qs.rt_audit_case_3_super_pv) + pv
        qs.rt_audit_case_3_super_bv = float(qs.rt_audit_case_3_super_pv) + bv
        qs.rt_is_user_green = True
    if "case_4" in attribute:
        qs.rt_audit_case_4_pv = float(qs.rt_audit_case_4_pv) + pv
        qs.rt_audit_case_4_bv = float(qs.rt_audit_case_4_bv) + bv

    qs.save()


def rt_infinity_calculation(current_user, pv, bv, dp, parameter, month, year, date):
    # print("running infinity")
    # [Flow] We will run loop and add the PV & BV to each user's gpv & pbv
    referral_obj = ReferralCode.objects.get(user_id=current_user)  # User
    username_of_referral = referral_obj.referal_by  # His Upline
    add_pv_bv(current_user, pv, bv, dp, [parameter, ], month, year, date)

    if username_of_referral is not None:
        # [Flow] Check for both update and save function
        order_detail_qs = RealTimeDetail.objects.update_or_create(user_id=username_of_referral,
                                                                  date__month=month,
                                                                  date__year=year,
                                                                  defaults={'user_id': username_of_referral,
                                                                            'date': date})[0]
        order_detail_qs.date = date
        order_detail_qs.save()

        rt_infinity_calculation(username_of_referral, pv, bv, dp, parameter, month, year, date)
    else:
        pass


@login_required(login_url='home')
def total_pv_bv(request):
    '''
    Des:   Using this view we will calculate users left pv/bv, right pv/bv (Super) and gpv/gbv (Infinity).
    input: It is meant to run using cron and will pick orders from the order table from the last run and add up details.
    out:   Function will save relevant details directly to database.
    Todo(D): User Self PPV.
    Todo(d): Calculate this and save details on monthly basis.
    Todo(2): Find number of users (in left, in right and in total group). [This is to be maintained only once and not monthly].
    Todo(3): Rebuilding users option.
    Todo(*): Find Active Users below a person (i.e. user with PV > PV to become active).
    Todo(D): Run for order placed before 2 hour, i.e. skip orders placed within last 2 hour (during continue compute).
    Todo(D): Issues to be checked
    Todo(D): Configure it for Cron
    Todo(8): System saving last month details in date column (everywhere) instead of current month & year
    Todo(D): Calculate TBV for each user (adding BV to the user and his upline)
    Todo( ): Calculate DP sales turnover userwise.
    '''

    # checking if user has permission to view this page
    if not check_permission(request):
        return HttpResponse('<h1>You don\'t have permission to view this page</h1>')

    latest_orders = []
    month, year = 1, 1
    if (request.GET.get('inputbtn') or request.POST.get('inputbtn')):
        print("Starting rebuilding")
        if request.method == 'GET':
            year = int(request.GET.get('year'))
            month = int(request.GET.get('month'))
        if request.method == 'POST':
            year = int(request.POST.get('year'))
            month = int(request.POST.get('month'))
        delete_rt_calculation(month, year)
        latest_orders = Order.objects.filter(date__month=month,
                                             date__year=year,
                                             paid=True,
                                             delete=False,
                                             loyalty_order=False,
                                             ).exclude(status=8).order_by('-pk')
        total_pv_bv_calc(latest_orders, month, year)

    if (request.GET.get('compute') or request.POST.get('compute')):
        total_pv_bv_calc(latest_orders, month, year)

    return render(request, 'realtime_calculation/base.html', )

# Run cron from last order
def total_pv_bv_cron():
    total_pv_bv_calc([], 1, 1)

# Delete details of the current month and run cron from the first order of this month
def total_pv_bv_cron_fresh():
    total_pv_bv_calc([], 1, 1, True)

def total_pv_bv_calc(latest_orders, month, year, fresh=False):
    if not latest_orders:
        print("Starting computing")
        # build_tree()
        # return
        date = datetime.now()
        # Pick order excluding orders placed within 2 hours
        date_to_be_taken = date - timedelta(minutes=15)
        month = date.month
        year = date.year
        # Remove Current Data if we want to get fresh results (i.e. fresh = True)
        if fresh == True:
            delete_rt_calculation(month, year)
        # Pick order number till last function run
        try:
            latest_orders = RealTimeOrder.objects.filter(date__month=month, date__year=year).latest('date')
            print(latest_orders)
        except RealTimeOrder.DoesNotExist:
            latest_orders = None
        # If we are running this function for the first time in the month.
        if not latest_orders:
            print("=============> inside if")
            latest_orders = Order.objects.filter(date__lt=date_to_be_taken,
                                                 date__month=month,
                                                 date__year=year,
                                                 paid=True,
                                                 delete=False,
                                                 loyalty_order=False,
                                                 ).exclude(status=8).order_by('-pk')
            print(len(latest_orders))

        # If we are running this function for the subsequent time in the month.
        else:
            print("=============> inside else")
            latest_orders = Order.objects.filter(date__gt=latest_orders.last_order.date,
                                                 date__lt=date_to_be_taken,
                                                 date__month=month,
                                                 date__year=year,
                                                 paid=True,
                                                 delete=False,
                                                 loyalty_order=False,
                                                 ).exclude(status=8).order_by('-date')
            print(len(latest_orders))

    previous_month = month - 1
    previous_year = year
    if previous_month < 0:
        previous_month = month
        previous_year = year - 1

    date = datetime(int(year), int(month), 1) + timedelta(days=1)

    for latest_order in reversed(latest_orders):
        order_audit_qs = RealTimeOrderAudit.objects.update_or_create(order_id=latest_order,
                                                                     defaults={'order_id': latest_order,
                                                                               'date': date,
                                                                               'grand_total':latest_order.grand_total,
                                                                               'paid':latest_order.paid,
                                                                               'delete':latest_order.delete,
                                                                               'status':latest_order.status,
                                                                               'pv':latest_order.pv,
                                                                               'bv':latest_order.bv,
                                                                               })[0]
        order_audit_qs.date = date
        order_audit_qs.save()

    pv_factor = 1

    # We will first find the amount of PV required to become green. Note: User who is once green, will forever remain green.
    pv_to_become_active = float(super_model.objects.latest('pk').purchase_pv)

    # We will stop the function if we get no new order.
    print('latest order', latest_orders)
    print('lenth order..............', len(latest_orders))
    if not latest_orders:
        return

    latest_order_from_latest_orders = latest_orders.latest('date')
    print('..................',latest_order_from_latest_orders)

    order_number_qs = RealTimeOrder.objects.update_or_create(date__month=month,
                                                             date__year=year,
                                                             defaults={
                                                                 'last_order': latest_order_from_latest_orders,
                                                                 'date': date}, )[0]

    # Iterate each order to add up values (from oldest order to recent order)
    # Needs concurrency
    for latest_order in reversed(latest_orders):
        # [Flow] Added 1 day to the current date as date in production server was saving as last date of the previous month.
        need_to_run_infinity_calculation_inside_super = True

        # Find username of User who has placed this order
        try:
            current_user = User.objects.get(email=latest_order.email)
        except User.DoesNotExist:
            continue

        # [Flow] Creating RealTimeDetails
        # [Flow] Save Audit Details for the current order
        latest_order_audit_qs = RealTimeOrderAudit.objects.get(order_id=latest_order, date__month=month,
                                                               date__year=year)
        latest_order_audit_qs.rt_calculation_done = True
        latest_order_audit_qs.save()

        # [Flow] Save current Running Order
        order_number_qs = RealTimeOrder.objects.update_or_create(date__month=month,
                                                                 date__year=year, defaults={
                                                                        # 'last_order': latest_order,       # AG :: No need to add latest order now
                                                                        'date': date,
                                                                         'order_completed_till': latest_order,})[0]

        order_number_qs.date = date
        order_number_qs.save()

        # Benefit of Stock Variance will not be given.
        if current_user.id in stock_variance_ids:
            latest_order_audit_qs.is_stock_variance_order = True
            latest_order_audit_qs.save()
            continue

        try:
            rt_user = User.objects.get(email=latest_order.email)
        except User.DoesNotExist:
            print("User with email {} not present".format(latest_order.email))
            rt_user = None

        # Find PV, BV & DP of the order in hand
        current_pv, current_bv = float(latest_order.pv), float(latest_order.bv)
        current_dp = float(latest_order.grand_total) - float(latest_order.shiping_charge)

        # current_pv = current_pv * pv_factor

        # [Flow] Add pbv & ppv details for the current user
        add_pv_bv(current_user, current_pv, current_bv, current_dp, ["rt_p", ], month, year, date)

        # [Flow] Add tbv for the user and his upline (Team Building Bonus)
        rt_infinity_calculation(current_user, current_pv, current_bv, current_dp, "rt_tv_month", month, year, date)

        # if latest_order.material_center.id not in power_centers_ids:
        # For each order, super pv/bv is calculated only if the new user has placed the ordered (New user are those who have PPV less than 100PV).
        # Here we will have three cases:
        # Case 1: User's was already green last month (i.e. he has purchased products > 100PV). (All Infinity)
        # Case 2: User was not green last month but was green before placing this order. (All Infinity)
        # Case 3: User was not green, but is green after placing this order (Partial PV/BV for Super & Partial for Infinity).
        # Case 4: User was not green, neither he is green now. (All Super)

        # We will assume that super calculation is required in this case.
        # However, for Case 1 & 2 above, the system will not calculate user's PV / BV in Super.
        super_calculation_required = True

        try:
            # Details of all old users is saved in Title Qualification Table of mlm_calculation module.
            # We will pick user's Qualification.
            user_highest_qualification = title_qualification_calculation_model.objects.filter(user=current_user).latest(
                'date_model').highest_qualification_ever
            is_user_green = title_qualification_calculation_model.objects.filter(user=current_user).latest(
                'date_model').is_user_green

            # If user is not found in title qualification table (i.e. the user is a registered in this month), we will mark him as blue advisor.
            if not user_highest_qualification:
                user_highest_qualification = "Blue Advisor"
                is_user_green = False
        except:
            print("inside except")
            user_highest_qualification = "Blue Advisor"
            is_user_green = False

        order_detail_for_audit_qs = RealTimeDetail.objects.update_or_create(user_id=current_user,
                                                                            date__month=month, date__year=year,
                                                                            defaults={'user_id': current_user,
                                                                                      'date': date})[0]
        order_detail_for_audit_qs.user_highest_qualification = user_highest_qualification
        order_detail_for_audit_qs.save()

        if (latest_order.material_center.id not in power_centers_ids) or (
                (latest_order.material_center.id in power_centers_ids) and (current_pv <= low_power_pv)):
            print(
                "0) if latest_order.material_center.id not in power_centers_ids or if latest_order.material_center.id in power_centers_ids and current_pv <= low_power_pv:")
            # For old user who's ID is green (Case 1), we will move directly to Infinity Calculation and continue this loop.
            if (user_highest_qualification != "Blue Advisor" and is_user_green):
                print("1) if user_highest_qualification != \"Blue Advisor\":")

                # [Flow] Since rt_infinity_calculation adds PV/BV to GPV/GBV, we are adding PV/BV to user's infinity PPV/PBV seperately.
                add_pv_bv(current_user, current_pv, current_bv, current_dp, ["rt_user_infinity", "case_1", ], month, year, date)
                rt_infinity_calculation(current_user, current_pv, current_bv, current_dp, "rt_gv_month", month, year,
                                        date)

                super_calculation_required = False
                continue

            # In case the User is not green.
            # We will find the PV of the user till last order (before the current one)
            # try:
            a = Order.objects.filter(date__lt=latest_order.date,
                                     paid=True,
                                     email=current_user.email,
                                     delete=False,
                                     loyalty_order=False,
                                     ).exclude(status=8)
            print("========>" + str(len(a)))
            # current_user_pv_till_last_order = Order.objects.filter(date__lt = latest_order.date, paid = True, email = current_user.email,delete=False).exclude(status=8).latest('pk').pv
            try:
                current_user_pv_till_last_order = float(a.aggregate(Sum('pv'))['pv__sum'])
                print("current_user_pv_till_last_order: " + str(current_user_pv_till_last_order))

            except:
                current_user_pv_till_last_order = 0.0

            # If the user has previously became Green in the current month only, i.e. this order is placed after he has achieved min PV for Green.
            # Then this will become our Case 2 and we will carry this PV to infinity model and continue this loop.
            if current_user_pv_till_last_order >= pv_to_become_active:
                print(
                    "2) if current_user_pv_till_last_order != 0 and current_user_pv_till_last_order >= pv_to_become_active:")

                add_pv_bv(current_user, current_pv, current_bv, current_dp, ["rt_user_infinity", "case_2", ], month, year, date)
                rt_infinity_calculation(current_user, current_pv, current_bv, current_dp, "rt_gv_month", month, year,
                                        date)

                super_calculation_required = False
                continue

            # If the user is not green but after this order, his PV goes above min PV to green (Case 3)
            if (current_user_pv_till_last_order + current_pv) > pv_to_become_active:
                print("3) if (current_user_pv_till_last_order + current_pv) > pv_to_become_active:")
                # saving values of current_pv
                current_super_pv = float(current_pv)
                current_super_bv = float(current_bv)
                current_super_dp = float(current_dp)

                # Prorating pv and bv for infinity plan
                current_pv = current_user_pv_till_last_order + current_pv - pv_to_become_active
                current_bv = current_bv * current_pv / current_super_pv
                current_dp = current_dp * current_pv / current_super_pv

                # [Flow] We are giving new user PV benefit to their uplines
                # We will allocate complete PV to infinity and partial PV to super.
                add_pv_bv(current_user, current_super_pv, current_bv, current_dp, ["rt_user_infinity", "case_3_infinity", ], month,
                          year, date)
                rt_infinity_calculation(current_user, current_super_pv, current_bv, current_dp, "rt_gv_month", month,
                                        year, date)

                # Balance pv & bv will be for the super plan
                current_pv = current_super_pv - current_pv
                current_bv = current_super_bv - current_bv
                current_dp = current_super_dp - current_dp

                add_pv_bv(current_user, current_pv, current_bv, current_dp, ["case_3_super", ], month, year, date)

                need_to_run_infinity_calculation_inside_super = False

        # For Case 4 and Partial PV & BV of Case 3
        # We will run loop and add the PV & BV to each user's left or right position

        # We will check if Super Calculation is required
        if super_calculation_required:
            print("Running Super Calculation")
            referral_obj = ReferralCode.objects.get(user_id=current_user)
            parent_id, position = referral_obj.parent_id, referral_obj.position

            add_pv_bv(current_user, current_pv, current_bv, current_dp, ["rt_user_super", ], month, year, date)
            add_pv_bv(current_user, current_pv, current_bv, current_dp, ["case_4", ], month, year, date)

            if need_to_run_infinity_calculation_inside_super:
                add_pv_bv(current_user, current_pv, 0, current_dp, ["rt_user_infinity", ], month, year, date)
                rt_infinity_calculation(current_user, current_pv, 0, current_dp, "rt_gv_month", month, year, date)

            while parent_id is not None:
                # We will identify Power Orders and will behave differently with them.
                if latest_order.material_center in power_centers_ids:
                    # We will not add PVs to parents if PV is given for activation of ID and will break the loop.
                    # A way to find out this is when PV is given from Power Material Center and is less than low_power_pv.
                    if latest_order.pv < low_power_pv:
                        break
                    # We will not add PVs to parents if they already have received a very high PV in other position before.
                    if latest_order.pv >= low_power_pv:
                        try:
                            parent_rt = team_building_bonus_super_plan_model.objects.get(user=referral_obj,
                                                                                         date__month=month,
                                                                                         date__year=year)
                            if position == "LEFT":
                                if parent_rt.cm_no_of_new_advisor_pv_in_right_position_referred_carry_forward > low_power_pv:
                                    break
                            else:
                                if parent_rt.cm_no_of_new_advisor_pv_in_left_position_referred_carry_forward > low_power_pv:
                                    break
                        except:
                            pass
                parent = User.objects.get(email=parent_id.email)
                create_rt_detail(parent, position, current_pv, current_bv, current_dp, month, year, date)
                referral_obj = ReferralCode.objects.get(user_id=parent)
                parent_id, position = referral_obj.parent_id, referral_obj.position
        else:
            print("Super Calculation Skipped")
            continue
