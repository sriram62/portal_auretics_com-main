from django.contrib import messages
from django.shortcuts import render, redirect
from django.db.models import Sum
from mlm_admin.models import *
from shop.calculation import calculated_business_value, calculated_point_value, calculated_partial_loyalty_details
from shop.models import Order, Material_center
from .new_inventory_calculation import *
from mlm_calculation.models import consistent_retailers_income
from business.views import previous_month

def recalculate_everything(request, myid=None, post_bill=False, check=False, mlm_admin=False, loop=0, dist_order=True, excess_cri=0):
    '''
    This function recalculates the Grand Total, PV, BV of a given invoice:
    :param request: is request.
    :param myid: is the pk of distributor_sale.
    :param check: for checking whether the recalculation is done properly or not.
    :param mlm_admin: mlm_admin can perform rechecking whenever they want.
    :return: we will return error or success message.
    '''
    if myid:
        # First we will pick the row from distributor sale & order table.
        try:
            distributor_sale_obj = Distributor_Sale.objects.get(pk=myid)
            order_obj = Order.objects.get(pk=distributor_sale_obj.order.id)
            is_loyalty = distributor_sale_obj.is_loyalty_sale
            is_partial_loyalty_sale = distributor_sale_obj.is_partial_loyalty_sale
            if is_partial_loyalty_sale:
                is_loyalty = False
        except:
            messages.warning(request, 'Distributor Sale ID not found. Please contact Admin')
            return redirect('distributor_sale_list')

        # Distributors are allowed to perform Recalculation in the same month only.
        if not mlm_admin:
            allowed = Order.objects.filter(pk=distributor_sale_obj.order.id, date__month=datetime.now().month, date__year=datetime.now().year,)
            if not allowed:
                messages.warning(request, 'Recalculation is allowed in the same month. Please contact Admin')
                return redirect('distributor_view_sale', myid=myid)
                # return redirect('distributor_sale_list')

        # Now we will recalculate the pv, bv and total, linetime wise from order table.
        was_there_calculation_issue_in_li = False
        was_there_calculation_issue_in_grand_total = False
        was_there_calculation_issue_in_pv = False
        was_there_calculation_issue_in_bv = False
        o_pv, o_bv, li_pv, li_bv, grand_total_amount, consumed_cri = 0, 0, 0, 0, 0,0
        dist_li = Distributor_Sale_itemDetails.objects.filter(sale=distributor_sale_obj)
        for item in dist_li:
            quantity = item.quantity
            mrp = item.batch.mrp
            distributor_price = item.item.distributor_price
            igst = item.item.igst
            if is_loyalty:
                distributor_price_with_tax = round(mrp ,2)
                distributor_price = round(mrp / ((100 + igst) / 100), 2)
                consumed_cri += (distributor_price_with_tax * quantity)
                distributor_price_with_tax = 0
                distributor_price = 0
            else:
                distributor_price_with_tax = round(mrp / ((100 + distributor_price) / 100), 2)
                distributor_price = round(mrp / ((100 + igst) / 100) / ((100 + distributor_price) / 100), 2)
            igst = 0
            cgst = 0
            sgst = 0

            # if item.sale.sale_type == '1':
            #     distributor_price = round(mrp / ((100 + igst) / 100) / ((100 + distributor_price) / 100),2)
            #     igst = round(distributor_price * (igst / 100),2)
            #     igst = round(igst, 2)
            #     cgst = 0
            #     sgst = 0
            # else:
            #     distributor_price = mrp / ((100 + igst) / 100) / ((100 + distributor_price) / 100)
            #     cgst = round(distributor_price * ((igst / 2) / 100),2)
            #     cgst = round(cgst / 2, 2)
            #     sgst = round(distributor_price * ((igst / 2) / 100),2)
            #     sgst = round(sgst / 2, 2)
            #     igst = 0
            total_amount = round((distributor_price_with_tax * quantity),2)
            grand_total_amount += total_amount

            if not is_loyalty:
                li_pv = calculated_point_value(item.item, distributor_price, quantity)
                li_bv = calculated_business_value(item.item, distributor_price, quantity)
                o_pv += li_pv
                o_bv += li_bv

                if is_partial_loyalty_sale:
                    # AG :: We will find total consumption of CRI without this order and then find excess cri.
                    user = User.objects.get(email=order_obj.email)
                    month_to_be_taken = order_obj.date.month
                    year_to_be_taken = order_obj.date.year
                    previous_month_to_be_taken = month_to_be_taken - 1
                    previous_year_to_be_taken = year_to_be_taken
                    if previous_month_to_be_taken <= 0:
                        previous_month_to_be_taken = 12
                        previous_year_to_be_taken = previous_year_to_be_taken - 1

                    order_total_consumed = Order.objects.filter(email = order_obj.email,
                                                                date__month = month_to_be_taken,
                                                                date__year = year_to_be_taken,
                                                                paid = True,
                                                                delete = False,
                                                                loyalty_order = True).exclude(
                        status = 8).exclude(
                        pk = order_obj.pk).aggregate(Sum('consumed_cri'))['consumed_cri__sum']
                    if order_total_consumed:
                        order_total_consumed = float(order_total_consumed)
                    else:
                        order_total_consumed = 0.0
                    cri_earned = float(consistent_retailers_income.objects.get(user=user,
                                                                                input_date__month=previous_month_to_be_taken,
                                                                                input_date__year=previous_year_to_be_taken,
                                                                                ).cri_earned)
                    excess_cri = float(mrp) - cri_earned + order_total_consumed
                    li_pv, li_bv, distributor_price_with_tax = calculated_partial_loyalty_details(item.item, excess_cri)
                    total_amount = distributor_price_with_tax
                    # total_amount = distributor_price_with_tax + mrp - excess_cri
                    grand_total_amount = total_amount
                    consumed_cri = mrp - excess_cri
                    o_pv = li_pv
                    o_bv = li_bv

                # Checking PV & BV Distributor Line Item wise
                if float(li_pv) != float(item.pv_total):
                    item.pv_total = li_pv
                    was_there_calculation_issue_in_pv = True
                if float(li_bv) != float(item.bv_total):
                    item.bv_total = li_bv
                    was_there_calculation_issue_in_bv = True


            # Checking if there is need to recalculate grand total line item wise
            # allowing error margin of Rs.1 or 0.5%
            # We will first check distributor line item details for single quantity
            item_total_amount_lower_single = min((float(item.distributor_price) - 1.00), float(item.distributor_price) * 0.9950)
            item_total_amount_higher_single = max((float(item.distributor_price) + 1.00), float(item.distributor_price) * 1.0050)
            if not item_total_amount_lower_single <= float(distributor_price_with_tax) <= item_total_amount_higher_single:
                item.distributor_price = distributor_price_with_tax
                # Distributor_Sale_itemDetails.objects.filter(sale=distributor_sale_obj, batch=item.batch).update(total_amount=total_amount).save()
                was_there_calculation_issue_in_li = True
                was_there_calculation_issue_in_grand_total = True

            # We will first check distributor line item details for all quantity
            item_total_amount_lower = min((float(item.total_amount) - 1.00), float(item.total_amount) * 0.9950)
            item_total_amount_higher = max((float(item.total_amount) + 1.00), float(item.total_amount) * 1.0050)
            if not item_total_amount_lower <= float(total_amount) <= item_total_amount_higher:
                item.total_amount = total_amount
                # Distributor_Sale_itemDetails.objects.filter(sale=distributor_sale_obj, batch=item.batch).update(total_amount=total_amount).save()
                was_there_calculation_issue_in_li = True
                was_there_calculation_issue_in_grand_total = True

            item.was_there_calculation_issue_in_li = was_there_calculation_issue_in_li
            item.was_there_calculation_issue_in_grand_total = was_there_calculation_issue_in_grand_total

            item.save()

            distributor_sale_obj.was_there_calculation_issue_in_li = was_there_calculation_issue_in_li
            distributor_sale_obj.save()

            # Checking if there is need to recalculate PV BV & Grand Total line item wise (in shop line item).
            if not check:
                if float(li_pv) != float(LineItem.objects.get(order=order_obj, batch= item.batch).pv):
                    LineItem.objects.filter(order=order_obj, batch= item.batch).update(pv = li_pv)
                    was_there_calculation_issue_in_pv = True
                if float(li_bv) != float(LineItem.objects.get(order=order_obj, batch=item.batch).bv):
                    LineItem.objects.filter(order=order_obj, batch=item.batch).update(bv=li_bv)
                    was_there_calculation_issue_in_bv = True
                if not item_total_amount_lower_single <= float(LineItem.objects.get(order=order_obj, batch=item.batch).price) <= item_total_amount_higher_single:
                    LineItem.objects.filter(order=order_obj, batch=item.batch).update(price=distributor_price_with_tax)
                    was_there_calculation_issue_in_li = True
                    was_there_calculation_issue_in_grand_total = True
                if not item_total_amount_lower <= float(LineItem.objects.get(order=order_obj, batch=item.batch).total_amount) <= item_total_amount_higher:
                    LineItem.objects.filter(order=order_obj, batch=item.batch).update(total_amount=total_amount)
                    was_there_calculation_issue_in_li = True
                    was_there_calculation_issue_in_grand_total = True

            if is_partial_loyalty_sale:
                break

        # Checking if there is need to recalculate grand total of the complete order (from order table)
        item_total_amount_lower_order_obj = min((float(order_obj.grand_total) - 1.00), float(order_obj.grand_total) * 0.9950)
        item_total_amount_higher_order_obj = max((float(order_obj.grand_total) + 1.00), float(order_obj.grand_total) * 1.0050)
        if not item_total_amount_lower_order_obj <= float(grand_total_amount) <= item_total_amount_higher_order_obj:
            was_there_calculation_issue_in_li = True
            was_there_calculation_issue_in_grand_total = True

        # Checking if there is need to recalculate grand total of the complete order (from distributor_sale table)
        item_total_amount_lower_distributor_sale_obj = min((float(distributor_sale_obj.grand_total) - 1.00),
                                                float(distributor_sale_obj.grand_total) * 0.9950)
        item_total_amount_higher_distributor_sale_obj = max((float(distributor_sale_obj.grand_total) + 1.00),
                                                 float(distributor_sale_obj.grand_total) * 1.0050)
        if not item_total_amount_lower_distributor_sale_obj <= float(grand_total_amount) <= item_total_amount_higher_distributor_sale_obj:
            was_there_calculation_issue_in_li = True
            was_there_calculation_issue_in_grand_total = True

        # Saving consumed_cri in case of it is a loyalty only order.
        if is_loyalty or is_partial_loyalty_sale:
            if order_obj.consumed_cri != consumed_cri:
                was_there_calculation_issue_in_grand_total = True
            order_obj.consumed_cri = consumed_cri

            user = User.objects.get(email=order_obj.email)
            user_total_cri_consumed = Order.objects.filter(date__month=order_obj.date.month,
                                                           date__year=order_obj.date.year,
                                                           loyalty_order=True)
            prev_month,prev_year = previous_month(order_obj.date.month, order_obj.date.year)
            cri = consistent_retailers_income.objects.get(user=user,
                                                          input_date__month=prev_month,
                                                          input_date__year=prev_year,
                                                          )
            cri.cri_consumed = consumed_cri
            cri.cri_balance = float(cri.cri_earned) - float(consumed_cri)
            cri.save()

        if float(o_pv) != float(order_obj.pv):
            was_there_calculation_issue_in_li = True
            was_there_calculation_issue_in_pv = True
        if float(o_bv) != float(order_obj.bv):
            was_there_calculation_issue_in_li = True
            was_there_calculation_issue_in_bv = True

        if float(o_pv) != float(distributor_sale_obj.grand_pv):
            was_there_calculation_issue_in_li = True
            was_there_calculation_issue_in_pv = True
        if float(o_bv) != float(distributor_sale_obj.grand_bv):
            was_there_calculation_issue_in_li = True
            was_there_calculation_issue_in_bv = True


        if not check:
            order_obj.was_there_calculation_issue_in_pv = was_there_calculation_issue_in_pv
            order_obj.was_there_calculation_issue_in_bv = was_there_calculation_issue_in_bv
            order_obj.was_there_calculation_issue_in_li = was_there_calculation_issue_in_li

            # Now we will check if all details of distributor_lineitem are correct or not.
            output = 'Recalculation done '
            if was_there_calculation_issue_in_li:
                output = output + 'with issues. '
            if was_there_calculation_issue_in_pv:
                output = output + 'Issue in PV. '
            if was_there_calculation_issue_in_bv:
                output = output + 'Issue in BV Found. '
            if was_there_calculation_issue_in_grand_total:
                output = output + 'Issue in Grand Total. '

            # At last we will update pv, bv and grand total from the line items.
            if was_there_calculation_issue_in_pv:
                order_obj.pv = o_pv
                distributor_sale_obj.grand_pv = o_pv
            if was_there_calculation_issue_in_bv:
                order_obj.bv = o_bv
                distributor_sale_obj.grand_bv = o_bv
            if was_there_calculation_issue_in_grand_total:
                order_obj.grand_total = grand_total_amount
                distributor_sale_obj.grand_total = grand_total_amount

            if is_loyalty or is_partial_loyalty_sale:
                order_obj.consumed_cri = consumed_cri

            try:
                order_obj.save()
                distributor_sale_obj.save()
            except:
                pass

        if check:
            if was_there_calculation_issue_in_li or was_there_calculation_issue_in_pv or was_there_calculation_issue_in_bv or was_there_calculation_issue_in_grand_total:
                return False
            else:
                return True

        if loop == 0:
            recalculate_everything(request, myid=myid, post_bill=post_bill, check=False, mlm_admin=mlm_admin, loop=(loop + 1))

        # If this rechecking function found any error, then we will test if the issues are still remaining.
        # just to avoid any chances of infinite loop.
        else:
            if was_there_calculation_issue_in_li or was_there_calculation_issue_in_pv or was_there_calculation_issue_in_bv or was_there_calculation_issue_in_grand_total:
                if recalculate_everything(request, myid=myid, post_bill=post_bill, check=True, mlm_admin=mlm_admin,  loop=(loop + 1)):
                    output = output + "All changes were done successfully"
                else:
                    output = output + "Changes were unsuccessful. Please contact admin."
            else:
                output = output + "No issues found."

        # o = order_obj
        # obj = distributor_sale_obj
        #
        # pv = sum([li.pv for li in obj.order.lineitem_set.all()])
        # bv = sum([li.bv for li in obj.order.lineitem_set.all()])
        # grand_total = sum([li.total_amount for li in obj.order.lineitem_set.all()])

        # Order.objects.filter(pk=obj.order.id).update(pv=pv, bv=bv, grand_total=grand_total)
        # Distributor_Sale.objects.filter(pk=myid).update(grand_pv=pv, grand_bv=bv, grand_total=grand_total)

        if not post_bill:
            messages.success(request, output)
    else:
        messages.warning(request, 'Please check for Distributor Sale ID or contact Admin')

    return redirect('distributor_view_sale', myid=myid)