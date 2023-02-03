from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Sum

from .models import *
from accounts.models import ReferralCode
from shop.models import *
from distributor.models import *

from datetime import datetime, timedelta
from decimal import Decimal

from mlm_admin.templatetags.template_tag import *


def delete_existing_data(month, year):
    delete_existing_data_AuditOrderDistributor = AuditOrderDistributor.objects.filter(date__month = month, date__year = year).delete()


# Create your views here.
def audit_order_pv_bv(request):
    '''
    We are auditing and finding out that all the order are okay or not.
    This function will check orders for the following cases:
    (1) Whether PV & BV has been allocated to online orders.
    (2) Whether line wise item details and overall order details have been correctly added to Order from Distributor Table.
    (3) Whether PV & BV has been allocated to orders created at distributor's end.
    (4) What PV & BV should have been allocated.
    (5) How much PV & BV should have been allocated.
    (6) Is there a difference in PV & BV.
    '''
    latest_orders = []
    distributor_orders = []
    date_now = datetime.datetime.now()
    if request.GET.get('inputbtn'):
        print("Rebuilding")
        year = int(request.GET.get('year'))
        month = int(request.GET.get('month'))
        delete_existing_data(month, year)

        distributor_orders = Distributor_Sale.objects.filter(date__month=month, date__year=year)

    if request.GET.get('compute'):
        print("Starting computing")
        month = date_now.month
        year = date_now.year
        # Pick order number till last function run
        try:
            latest_orders = AuditOrderNo.objects.latest('pk')
        except AuditOrderNo.DoesNotExist:
            latest_orders = None

        # If we are running this function for the first time in the month.
        if not latest_orders:
            print("=============> inside if")
            distributor_orders = Distributor_Sale.objects.filter(date__month=month, date__year=year)

        # If we are running this function for the subsequent time in the month.
        else:
            print("=============> inside else")
            distributor_orders = Distributor_Sale.objects.filter(date__gt=latest_orders.last_order.date,
                                                               date__month=month,
                                                               date__year=year)

    ecommerce_mc = Material_center.objects.filter(frontend=True)
    non_ecommerce_mc = Material_center.objects.filter(frontend=False)

    date = datetime.datetime(int(year), int(month), 1) - timedelta(days=1)

    variance_allowed = 0.01
    variance_allowed_lower = 1 - variance_allowed
    variance_allowed_upper = 1 + variance_allowed

    # [Flow] Checking on distributors first:
    for distributor_order in distributor_orders:
        expected_pv, actual_pv, expected_bv, actual_bv, expected_dp, actual_dp = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        found_in_order, is_pv_allocated, is_bv_allocated, is_pv_same, is_bv_same, is_there_line_item = \
            False, False, False, False, False, False
        line_item_wise_details = {}

        # Distributor Line Item to Distributor Order & # Distributor Order Item to Order
        distributor_line_items = Distributor_Sale_itemDetails.objects.filter(sale = distributor_order.id)

        if distributor_line_items:
            is_there_line_item = True
            order_id_order = distributor_line_items.first().sale.order

            for distributor_line_item in distributor_line_items:
                mrp, distributor_margin, igst, business_value, line_item_dp, line_item_pv, line_item_bv, quantity = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

                batch = Batch.objects.get(id = distributor_line_item.batch.id)
                mrp = round(float(batch.mrp),2)
                product = Product.objects.get(id = distributor_line_item.item.id)
                distributor_margin = round(float(product.distributor_price),2)
                quantity = float(distributor_line_item.quantity)
                igst = float(product.igst)
                product_business_volume = float(product.business_value)
                product_point_value = float(product.point_value)

                li_ex_dp = round(float(dis_price_include_tax(mrp, distributor_margin)),2) * quantity
                li_ex_pv = round(float(point_value(mrp, distributor_margin, igst, product_point_value)),2) * quantity
                li_ex_bv = round(float(bussiness_value(mrp,distributor_margin,igst,product_business_volume)),2) * quantity

                try:
                    line_item_dp = round(float(LineItem.objects.filter(order=order_id_order, product=distributor_line_item.item)[0].price), 2)
                    line_item_pv = round(float(LineItem.objects.filter(order=order_id_order, product = distributor_line_item.item)[0].pv),2)
                    line_item_bv = round(float(LineItem.objects.filter(order=order_id_order, product = distributor_line_item.item)[0].bv),2)
                except:
                    pass

                expected_dp += li_ex_dp
                actual_dp   += line_item_dp
                expected_pv += li_ex_pv
                actual_pv   += line_item_pv
                expected_bv += li_ex_bv
                actual_bv   += line_item_bv

                if (line_item_bv * variance_allowed_lower) <= li_ex_bv <= (line_item_bv * variance_allowed_upper):
                    okay_status = "OKAY"
                else:
                    okay_status = "ISSUE"

                line_item_wise_details[product] = str([batch,
                                                       ('MRP: ' + str(mrp)),
                                                       ('GST: ' + str(igst)),
                                                       ('DP%: ' + str(distributor_margin)),
                                                       ('EDP: ' + str(li_ex_dp)),
                                                       ('ADP: ' + str(li_ex_dp)),
                                                       ('EPV: ' + str(li_ex_pv)),
                                                       ('APV: ' + str(line_item_pv)),
                                                       ('EBV: ' + str(li_ex_bv)),
                                                       ('ABV: ' + str(line_item_bv)),
                                                       ('QTY: ' + str(quantity)),
                                                       ('STATUS: ' + str(okay_status)),])

            if order_id_order:
                found_in_order = True
            if actual_pv:
                is_pv_allocated = True
            if actual_bv:
                is_bv_allocated = True
            if (actual_pv * variance_allowed_lower) <= expected_pv <= (actual_pv * variance_allowed_upper):
                is_pv_same = True
            if (actual_bv * variance_allowed_lower) <= expected_bv <= (actual_bv * variance_allowed_upper):
                is_bv_same = True

            OrderDistributor = AuditOrderDistributor(date = date,
                                                     date_added = date_now,
                                                     order_id_dist = order_id_order,
                                                     order_no_dist = distributor_order.id,
                                                     material_center = distributor_order.material_center,
                                                     found_in_order = found_in_order,
                                                     order_id_order = order_id_order,
                                                     order_no_order = order_id_order.id,
                                                     order_by_user = distributor_order.advisor_distributor_name,
                                                     user_referral_code = distributor_order.advisor_distributor_name.referralcode.referral_code,
                                                     user_email = distributor_order.advisor_distributor_name.email,
                                                     expected_dp = expected_dp,
                                                     expected_pv = expected_pv,
                                                     expected_bv = expected_bv,
                                                     actual_dp = actual_dp,
                                                     actual_pv = actual_pv,
                                                     actual_bv = actual_bv,
                                                     is_pv_allocated = is_pv_allocated,
                                                     is_bv_allocated = is_bv_allocated,
                                                     is_pv_same = is_pv_same,
                                                     is_bv_same = is_bv_same,
                                                     is_there_line_item = is_there_line_item,
                                                     line_item_wise_details = line_item_wise_details,
                                                     )
        else:
            OrderDistributor = AuditOrderDistributor(date=date,
                                                     date_added=date_now,
                                                     order_no_dist=distributor_order.id,
                                                     material_center=distributor_order.material_center,
                                                     order_by_user=distributor_order.advisor_distributor_name,
                                                     user_referral_code=distributor_order.advisor_distributor_name.referralcode.referral_code,
                                                     user_email=distributor_order.advisor_distributor_name.email,
                                                     )

        latest_orders, latest_orders_created = AuditOrderNo.objects.update_or_create(date__month=month,
                                                                                     date__year=year,
                                                                                     defaults={
                                                                                         'date': date,
                                                                                         'date_added': date_now,
                                                                                         'last_order': distributor_order.order
                                                                                     })
        print(OrderDistributor)
        latest_orders.save()
        OrderDistributor.save()


        # Order Line Item to Order




    return(render(request, 'realtime_calculation/base.html',))