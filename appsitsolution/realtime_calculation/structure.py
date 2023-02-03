import django
django.setup()

from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from accounts.models import ReferralCode
from shop.models import Material_center, Order
from realtime_calculation.models import RealTimeDetail, RealTimeOrder, RealTimeUser, generation, organisation, InstantDetail, execution_time
from realtime_calculation.views import power_centers_ids, low_power_pv, stock_variance_ids
from mlm_calculation.models import title_qualification_calculation_model, configurations, super_model, infinity_model, team_building_bonus_super_plan_model
from mlm_calculation.check_permit import check_permission
from business.views import last_month, last_year
from pyjama import j

from datetime import datetime, timedelta
from decimal import Decimal

from django.http import HttpResponse
import multiprocessing
from multiprocessing import Lock, Process, Queue, current_process
import pytz
import math


multiprocessing.set_start_method('spawn', force=True)


def delete_structure():
    generation.objects.all().delete()
    organisation.objects.all().delete()

def tag_upline(user, upline=None):
    if upline:
        upline = ReferralCode.objects.filter(user_id=upline)
        if upline:
            upline = upline[0].referal_by
        else:
            return True
    else:
        upline = ReferralCode.objects.filter(user_id=user)
        if upline:
            upline = upline[0].referal_by
        else:
            return True
    # upline = ReferralCode.objects.get(user_id=upline).referal_by
    if upline:
        qs = generation(user=user, upline=upline)
        qs.save()
        tag_upline(user, upline)
    else:
        return True


# pk = [107,109,123,124,]

def tag_parent(user, parent=None):
    if parent:
        try:
            position = parent.referralcode.position
        except:
            position = ""
        parent = ReferralCode.objects.filter(user_id=parent)
        if parent:
            parent = parent[0].parent_id
        else:
            return True
    else:
        parent = ReferralCode.objects.filter(user_id=user)
        if parent:
            parent = parent[0].parent_id
            try:
                position = user.referralcode.position
            except:
                position = ""
        else:
            return True
    # upline = ReferralCode.objects.get(user_id=upline).referal_by
    if parent:
        qs = organisation(user=user, parent=parent, position=position)
        qs.save()
        tag_parent(user, parent)
    else:
        return True


def create_detail_down(tasks_to_accomplish): # users, month, year):
    try:
        task = tasks_to_accomplish.get_nowait()
    except:
        return

    users = task[0]
    month = task[1]
    year = task[2]

    for user in users:
        # user = User.objects.filter(id=user.user_id).first()
        group_users = generation.objects.filter(upline=user)
        left_users = organisation.objects.filter(parent=user, position='LEFT')
        right_users = organisation.objects.filter(parent=user, position='RIGHT')

        # group_instant_detail_users = generation.objects.filter(upline=user).values_list('id')
        # group_instant_detail_users = group_users.values_list('user_id')
        group_instant_detail = InstantDetail.objects.filter(user__id__in=group_users.values_list('user_id'),
                                                            date__month=month,
                                                            date__year=year,)
        left_instant_detail = InstantDetail.objects.filter(user__id__in = left_users.values_list('user_id'),
                                                           date__month=month,
                                                           date__year=year,)
        right_instant_detail = InstantDetail.objects.filter(user__id__in=right_users.values_list('user_id'),
                                                            date__month=month,
                                                            date__year=year,)

        left_pv = j.qs_sum(left_instant_detail,'rt_user_super_ppv')
        left_bv = j.qs_sum(left_instant_detail,'rt_user_super_pbv')
        left_dp = 0.0
        right_pv = j.qs_sum(right_instant_detail,'rt_user_super_ppv')
        right_bv = j.qs_sum(right_instant_detail,'rt_user_super_pbv')
        right_dp = 0.0
        gpv = j.qs_sum(group_instant_detail,'rt_user_infinity_ppv')
        gbv = j.qs_sum(group_instant_detail,'rt_user_infinity_pbv')
        gdp = 0.0
        tpv = j.qs_sum(group_instant_detail,'rt_ppv')
        tbv = j.qs_sum(group_instant_detail,'rt_pbv')
        tdp = 0.0

        left_new_users = organisation.objects.filter(parent=user,
                                                     position='LEFT',
                                                     user__profile__created_on__month = month,
                                                     user__profile__created_on__year = year,).count()
        right_new_users = organisation.objects.filter(parent=user,
                                                     position='RIGHT',
                                                     user__profile__created_on__month = month,
                                                     user__profile__created_on__year = year,).count()
        new_direct_sponsors = generation.objects.filter(upline=user,
                                                     user__profile__created_on__month = month,
                                                     user__profile__created_on__year = year,).count()

        new_group_instant_detail = InstantDetail.objects.filter(user__id__in=group_users.values_list('user_id'),
                                                                date__month=month,
                                                                date__year=year, )
        new_left_instant_detail = InstantDetail.objects.filter(user__id__in=left_users.values_list('user_id'),
                                                               date__month=month,
                                                               date__year=year, )
        new_right_instant_detail = InstantDetail.objects.filter(user__id__in=right_users.values_list('user_id'),
                                                                date__month=month,
                                                                date__year=year, )

        left_new_users_pv = j.qs_sum(new_left_instant_detail,'rt_user_super_ppv')
        right_new_users_pv = j.qs_sum(new_right_instant_detail,'rt_user_super_ppv')
        new_direct_sponsors_pv = j.qs_sum(new_group_instant_detail,'rt_user_infinity_ppv')
        left_new_users_bv = j.qs_sum(new_left_instant_detail,'rt_user_super_pbv')
        right_new_users_bv = j.qs_sum(new_right_instant_detail,'rt_user_super_pbv')
        new_direct_sponsors_bv = j.qs_sum(new_group_instant_detail,'rt_user_infinity_pbv')
        left_new_users_dp = 0.0
        right_new_users_dp = 0.0
        new_direct_sponsors_dp = new_group_instant_detail.count()
        group_users = group_users.count()

        qs = InstantDetail.objects.filter(user_id=user,
                                          date__month=month,
                                          date__year=year,
                                          ).update(
            rt_left_pv_month=left_pv,
            rt_left_bv_month=left_bv,
            rt_left_dp_month=left_dp,
            rt_right_pv_month=right_pv,
            rt_right_bv_month=right_bv,
            rt_right_dp_month=right_dp,
            rt_gpv_month=gpv,
            rt_gbv_month=gbv,
            # gdp=gdp,
            rt_tpv_month=tpv,
            rt_tbv_month=tbv,
            rt_tdp_month=tdp,
            rt_left_new_users_month=left_new_users,
            rt_right_new_users_month=right_new_users,
            rt_new_direct_sponsors_month=new_direct_sponsors,
            left_new_users_pv=left_new_users_pv,
            right_new_users_pv=right_new_users_pv,
            new_direct_sponsors_pv=new_direct_sponsors_pv,
            left_new_users_bv=left_new_users_bv,
            right_new_users_bv=right_new_users_bv,
            new_direct_sponsors_bv=new_direct_sponsors_bv,
            left_new_users_dp=left_new_users_dp,
            right_new_users_dp=right_new_users_dp,
            new_direct_sponsors_dp=new_direct_sponsors_dp,
            rt_group_users=group_users,
            status=True,
        )

    # Not required as we are performing this task for all users.
    # qs_false_delete = InstantDetail.objects.filter(date__month=month, date__year=year, status=False).delete()


def create_detail(month, year):
    '''
    Note: You need to run create_detail function month-wise. i.e from first month till now
    '''
    exec_time = execution_time.objects.create(create_detail=True)

    date = datetime(year, month, 1)

    # AG :: Mark status of all entries as False now, we will mark each entry as True one by one.
    # Entries with status still as False will be deleted. (There should be no entry marked as False as we are working on each entry).
    # This is just a sanity check.
    # Not required as we are performing this task for all users.
    # qs_status = InstantDetail.objects.filter(date__month=month,
    #                                          date__year=year).update(status=False)

    active_pv = float(configurations.objects.all()[0].minimum_monthly_purchase_to_become_active)
    green_pv = float(super_model.objects.all()[0].purchase_pv)

    users = User.objects.all()

    exec_time = execution_time.objects.filter(pk=exec_time.pk)
    exec_time.update(create_detail_self=True ,start_time_details_self=datetime.now())

    for user in users:
        # Break the loop if you are testing.
        break
        # To avoid pycharm highlights
        a == 1

        # AG :: This month details
        user_order_this_month = Order.objects.filter(email=user.email,
                                                     date__month=month,
                                                     date__year=year,
                                                     paid=True,
                                                     delete=False,
                                                     ).exclude(status=8).exclude(
            loyalty_order=True,
            is_partial_loyalty_order=False).exclude(
            material_center__id__in=power_centers_ids)

        ppv = j.qs_sum(user_order_this_month, 'pv')
        pbv = j.qs_sum(user_order_this_month, 'bv')

        # AG :: Calculating all information required as per model
        # AG :: All orders till now
        user_order_till_now = Order.objects.filter(email=user.email,
                                                   paid=True,
                                                   delete=False,
                                                   date__month__lte = month,
                                                   date__year__lte=year,
                                                   ).exclude(status=8).exclude(
            loyalty_order=True,
            is_partial_loyalty_order=False).exclude(
            material_center__id__in=power_centers_ids)

        total_ppv = j.qs_sum(user_order_till_now,'pv')

        user_infinity_ppv, user_infinity_pbv, user_super_ppv, user_super_pbv = 0.0, 0.0, 0.0, 0.0

        # We are checking each month details independently. i.e. we will not take past moth details for our calculation.
        # AG :: All orders till now
        user_order_before_this_month = Order.objects.filter(email=user.email,
                                                            paid=True,
                                                            delete=False,
                                                            date__month__lt=month,
                                                            date__year__lt=year,
                                                           ).exclude(status=8).exclude(
            loyalty_order=True,
            is_partial_loyalty_order=False).exclude(
            material_center__id__in=power_centers_ids)

        ppv_before_this_month = j.qs_sum(user_order_before_this_month,'pv')

        if ppv_before_this_month >= green_pv:
            rt_is_user_green = True
        else:
            rt_is_user_green = False

        # AG :: Checking User for Power
        user_order_this_month_power = Order.objects.filter(email=user.email,
                                                           date__month=month,
                                                           date__year=year,
                                                           paid=True,
                                                           delete=False,
                                                           material_center__id__in=power_centers_ids,
                                                           ).exclude(status=8).exclude(
            loyalty_order=True,
            is_partial_loyalty_order=False)

        power_ppv = j.qs_sum(user_order_this_month_power, 'pv')

        # AG :: We will first check if we have given a small power (for activation) to this user or not.
        # If yes then we will only mark this user as green and will not do anything else.
        if power_ppv > green_pv:
            rt_is_user_green = True

        if power_ppv >= low_power_pv:
            user_super_ppv = power_ppv

        if ppv > 0:
            # For each order, super pv/bv is calculated only if the new user has placed the ordered (New user are those who have PPV less than 100PV).
            # Here we will have three cases:
            # Case 1: User's was already green last month (i.e. he has purchased products > 100PV). (All Infinity)
            # Case 2: User was not green last month but is green now. (Partial PV/BV for Super & Partial for Infinity). (This is mix of Case 2 & 3 of Realtime calculation)
            # Case 3: User was not green, neither he is green now. (All Super)

            # We will use audit cases as per old realtime model.
            audit_case_1_pv, audit_case_1_bv, \
            audit_case_2_pv, audit_case_2_bv, \
            audit_case_3_infinity_pv,audit_case_3_infinity_bv, \
            audit_case_3_super_pv, audit_case_3_super_bv, \
            audit_case_4_pv, audit_case_4_bv = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

            # Case 1: When user is already green, we will allocate complete pv/bv to infinity.
            if rt_is_user_green:
                user_infinity_ppv = ppv
                user_infinity_pbv = pbv
                audit_case_1_pv = ppv
                audit_case_1_bv = pbv

            # Otherwise, we will allocate to super and infinity
            else:
                # This is tricky and the most crucial part of Super/Infinity Division.
                # Case 2: Partial PV/BV for Super & Partial for Infinity.
                if total_ppv > green_pv:                                        # eg: total_ppv = 150, till_last_month = 80, this_month = 150 - 80 = 70.
                    user_infinity_ppv = total_ppv - green_pv                    # Allocation to Infinity = 150 - 100 = 50.
                    user_infinity_pbv = pbv * (user_infinity_ppv / ppv)         # BV allocation = 700 * 50/70 = 500.
                    user_super_ppv = ppv - user_infinity_ppv                    # Super PV = 70 - 50 = 20.
                    user_super_pbv = pbv - user_infinity_pbv                    # Super BV = 700 - 500 = 200.
                    audit_case_3_infinity_pv = user_infinity_ppv
                    audit_case_3_infinity_bv = user_infinity_pbv
                    audit_case_3_super_pv = user_super_ppv
                    audit_case_3_super_bv = user_super_pbv


                # Case 3: User was not green & is not green now also (All allocation to Super)
                else:
                    user_super_ppv = ppv
                    user_super_pbv = pbv
                    audit_case_4_pv = ppv
                    audit_case_4_bv = pbv

                if total_ppv >= green_pv:
                    rt_is_user_green = True

                # AG :: Note: In all cases PV is allocated to Infinity also.
                user_infinity_ppv = ppv

        qs = InstantDetail.objects.update_or_create(user=user,
                                                    date=date,
                                                    defaults={
                                                        'rt_ppv':ppv,
                                                        'rt_pbv':pbv,
                                                        'rt_user_super_ppv':user_super_ppv,
                                                        'rt_user_super_pbv':user_super_pbv,
                                                        'rt_user_infinity_ppv':user_infinity_ppv,
                                                        'rt_user_infinity_pbv':user_infinity_pbv,
                                                        'rt_is_user_green':rt_is_user_green,
                                                        'rt_audit_case_1_pv': audit_case_1_pv,
                                                        'rt_audit_case_1_bv': audit_case_1_bv,
                                                        'rt_audit_case_2_pv': audit_case_2_pv,
                                                        'rt_audit_case_2_bv': audit_case_2_bv,
                                                        'rt_audit_case_3_infinity_pv': audit_case_3_infinity_pv,
                                                        'rt_audit_case_3_infinity_bv': audit_case_3_infinity_bv,
                                                        'rt_audit_case_3_super_pv': audit_case_3_super_pv,
                                                        'rt_audit_case_3_super_bv': audit_case_3_super_bv,
                                                        'rt_audit_case_4_pv': audit_case_4_pv,
                                                        'rt_audit_case_4_bv': audit_case_4_bv,
                                                    })

    exec_time.update(end_time_details_self=datetime.now(),
                     create_detail_down=True,
                     start_time_details_down=datetime.now())


    # AG :: We might run this function parallelly.
    # AG Code::
    threads_to_run = int((multiprocessing.cpu_count()/2))
    # Find number of instances to run
    number_of_processes = threads_to_run

    # Divide the users in that number of chunks
    no_of_users_in_a_chunk = float(len(users)) / float(number_of_processes)
    no_of_users_in_a_chunk = int(math.floor(no_of_users_in_a_chunk))
    # We will process balance chunks at the end
    no_of_users_in_last_chunk = len(users) - (no_of_users_in_a_chunk * number_of_processes)
    latest_users_start = 0
    latest_users_end = 0
    tasks_to_accomplish = Queue()
    tasks_that_are_done = Queue()
    processes = []
    for i in range(number_of_processes):
        # time.sleep(10)
        if no_of_users_in_last_chunk > 0:
            if i == range(number_of_processes)[-1]:
                no_of_users_in_a_chunk = no_of_users_in_last_chunk
        latest_users_start = latest_users_end
        latest_users_end = latest_users_start + no_of_users_in_a_chunk
        users_to_process = users[latest_users_start:latest_users_end]
        data = [users_to_process, month, year]
        tasks_to_accomplish.put(data)
        p = Process(target=create_detail_down, args=(tasks_to_accomplish,))
        processes.append(p)
        p.start()
        # completing process
        for p in processes:
            p.join()
        # print the output
        while not tasks_that_are_done.empty():
            print(tasks_that_are_done.get())

    # create_detail_down(users, month, year)

    exec_time.update(end_time_details_down=datetime.now())


def create_structure(request):
    '''
    This function creates a seperate table for each user where we will tag the upline of that user.
    Later we will filter from these uplines and calculation the business done by downlines.
    In this function we will create generational & organisation structures of all users
    '''
    # checking if user has permission to view this page
    if not check_permission(request):
        return HttpResponse('<h1>You don\'t have permission to view this page</h1>')

    # AG :: In case we are rebuilding, we will first remove everything
    if request.POST.get('inputbtn'):
        delete_structure()

    # AG :: Filtering user for whom structure is last made
    try:
        latest_gen_pk = generation.objects.all().latest('user').user.pk
    except:
        latest_gen_pk = 0

    try:
        latest_org_pk = organisation.objects.all().latest('user').user.pk
    except:
        latest_org_pk = 0

    common = True
    if request.POST.get('compute'):
        # AG :: If Generation User and Organisation Users are same,
        # then we will combine both in a single loop.
        # else we will run them separately.
        if latest_gen_pk != latest_org_pk:
            common = False

    if (request.POST.get('compute') or request.POST.get('inputbtn')):
        exec_time = execution_time(create_structure=True, start_time_structure=datetime.now())
        # AG :: Filter users for whom we will create the structure
        users_to_be_taken_gen = User.objects.filter(pk__gt = latest_gen_pk,).order_by('pk')

        if common:
            for user in users_to_be_taken_gen:
                # AG :: Creating Generational Structure
                # AG :: Tagging Uplines
                tag_upline(user)

                # AG :: Creating Organisational Structure
                # AG :: Tagging Parent
                tag_parent(user)
        else:
            users_to_be_taken_org = User.objects.filter(pk__gt=latest_org_pk).order_by('pk')
            for user in users_to_be_taken_gen:
                # AG :: Creating Generational Structure
                # AG :: Tagging Uplines
                tag_upline(user)
            for user in users_to_be_taken_org:
                # AG :: Creating Organisational Structure
                # AG :: Tagging Parent
                tag_parent(user)

        exec_time.update(end_time_structure=datetime.now())
        exec_time.save()

    if request.POST.get('create_detail'):
        year = int(request.POST.get('year', None))
        month = int(request.POST.get('month', None))
        create_detail(month, year)



    return render(request, 'realtime_calculation/base.html', {'page_type':'structure',
                                                              'latest_gen_pk':latest_gen_pk,
                                                              'latest_org_pk':latest_org_pk,})



