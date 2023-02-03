from django.contrib import messages
from django.shortcuts import render, redirect
from django.db.models import Sum
from .models import *
from shop.calculation import calculated_business_value, calculated_point_value
from shop.models import Material_center
from .new_inventory_calculation import *
from pyjama import j

def recalculate_everything_mlm(request, myid=None, post_bill=False, check=False, mlm_admin=False, loop=0, cf=False):
    '''
    This function recalculates the Grand Total, PV, BV of a given invoice:
    :param request: is request.
    :param myid: is the pk of Sale.
    :param check: for checking whether the recalculation is done properly or not.
    :param mlm_admin: mlm_admin can perform rechecking whenever they want.
    :return: we will return error or success message.
    '''
    if myid:
        # First we will pick the row from mlm_admin sale & order table.
        try:
            sale_obj = Sale.objects.get(pk=myid)
        except:
            messages.warning(request, 'Sale ID not found. Please contact Admin')
            if cf:
                return redirect('cnf_view_sale', myid=myid)
            else:
                return redirect('view_sale', myid=myid)

        # Distributors are allowed to perform Recalculation in the same month only.
        if not mlm_admin:
            allowed = Sale.objects.filter(pk=myid, date__month=datetime.now().month, date__year=datetime.now().year,)
            if not allowed:
                messages.warning(request, 'Recalculation is allowed in the same month. Please contact Admin')
                if cf:
                    return redirect('cnf_view_sale', myid=myid)
                else:
                    return redirect('view_sale', myid=myid)
                # return redirect('Sale_list')

        # Now we will recalculate the pv, bv and total, linetime wise from order table.
        was_there_calculation_issue_in_li = False
        was_there_calculation_issue_in_grand_total = False
        was_there_calculation_issue_in_pv = False
        was_there_calculation_issue_in_bv = False
        o_pv, o_bv, li_pv, li_bv, grand_total_amount = 0, 0, 0, 0, 0
        dist_li = Sale_itemDetails.objects.filter(sale=sale_obj)
        for item in dist_li:
            quantity = item.quantity
            mrp = item.batch.mrp
            distributor_price = item.item.distributor_price
            igst = item.item.igst
            distributor_price_with_tax = round(mrp / ((100 + distributor_price) / 100), 2)
            distributor_price = round(mrp / ((100 + igst) / 100) / ((100 + distributor_price) / 100), 2)
            igst = 0
            cgst = 0
            sgst = 0

            total_amount = round((distributor_price_with_tax * quantity),2)
            grand_total_amount += total_amount

            li_pv = calculated_point_value(item.item, distributor_price, quantity)
            li_bv = calculated_business_value(item.item, distributor_price, quantity)
            o_pv += li_pv
            o_bv += li_bv

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
                # Sale_itemDetails.objects.filter(sale=sale_obj, batch=item.batch).update(total_amount=total_amount).save()
                was_there_calculation_issue_in_li = True
                was_there_calculation_issue_in_grand_total = True

            # We will first check distributor line item details for all quantity
            item_total_amount_lower = min((float(item.total_amount) - 1.00), float(item.total_amount) * 0.9950)
            item_total_amount_higher = max((float(item.total_amount) + 1.00), float(item.total_amount) * 1.0050)
            if not item_total_amount_lower <= float(total_amount) <= item_total_amount_higher:
                item.total_amount = total_amount
                # Sale_itemDetails.objects.filter(sale=sale_obj, batch=item.batch).update(total_amount=total_amount).save()
                was_there_calculation_issue_in_li = True
                was_there_calculation_issue_in_grand_total = True

            item.was_there_calculation_issue_in_li = was_there_calculation_issue_in_li
            item.was_there_calculation_issue_in_grand_total = was_there_calculation_issue_in_grand_total

            item.save()

            sale_obj.was_there_calculation_issue_in_li = was_there_calculation_issue_in_li
            sale_obj.save()

            # Checking if there is need to recalculate PV BV & Grand Total line item wise (in shop line item).
            if not check:
                if float(li_pv) != float(Sale_itemDetails.objects.get(order=sale_obj, batch= item.batch).pv):
                    LineItem.objects.filter(order=sale_obj, batch= item.batch).update(pv = li_pv)
                    was_there_calculation_issue_in_pv = True
                if float(li_bv) != float(LineItem.objects.get(order=sale_obj, batch=item.batch).bv):
                    LineItem.objects.filter(order=sale_obj, batch=item.batch).update(bv=li_bv)
                    was_there_calculation_issue_in_bv = True
                if not item_total_amount_lower_single <= float(LineItem.objects.get(order=sale_obj, batch=item.batch).price) <= item_total_amount_higher_single:
                    LineItem.objects.filter(order=sale_obj, batch=item.batch).update(price=distributor_price_with_tax)
                    was_there_calculation_issue_in_li = True
                    was_there_calculation_issue_in_grand_total = True
                if not item_total_amount_lower <= float(LineItem.objects.get(order=sale_obj, batch=item.batch).total_amount) <= item_total_amount_higher:
                    LineItem.objects.filter(order=sale_obj, batch=item.batch).update(total_amount=total_amount)
                    was_there_calculation_issue_in_li = True
                    was_there_calculation_issue_in_grand_total = True

        # Checking if there is need to recalculate grand total of the complete order (from order table)
        item_total_amount_lower_sale_obj = min((float(sale_obj.grand_total) - 1.00), float(sale_obj.grand_total) * 0.9950)
        item_total_amount_higher_sale_obj = max((float(sale_obj.grand_total) + 1.00), float(sale_obj.grand_total) * 1.0050)
        if not item_total_amount_lower_sale_obj <= float(grand_total_amount) <= item_total_amount_higher_sale_obj:
            was_there_calculation_issue_in_li = True
            was_there_calculation_issue_in_grand_total = True

        # Checking if there is need to recalculate grand total of the complete order (from Sale table)
        item_total_amount_lower_sale_obj = min((float(sale_obj.grand_total) - 1.00),
                                                float(sale_obj.grand_total) * 0.9950)
        item_total_amount_higher_sale_obj = max((float(sale_obj.grand_total) + 1.00),
                                                 float(sale_obj.grand_total) * 1.0050)
        if not item_total_amount_lower_sale_obj <= float(grand_total_amount) <= item_total_amount_higher_sale_obj:
            was_there_calculation_issue_in_li = True
            was_there_calculation_issue_in_grand_total = True


        if float(o_pv) != float(sale_obj.pv):
            was_there_calculation_issue_in_li = True
            was_there_calculation_issue_in_pv = True
        if float(o_bv) != float(sale_obj.bv):
            was_there_calculation_issue_in_li = True
            was_there_calculation_issue_in_bv = True

        if float(o_pv) != float(sale_obj.grand_pv):
            was_there_calculation_issue_in_li = True
            was_there_calculation_issue_in_pv = True
        if float(o_bv) != float(sale_obj.grand_bv):
            was_there_calculation_issue_in_li = True
            was_there_calculation_issue_in_bv = True


        if not check:
            sale_obj.was_there_calculation_issue_in_pv = was_there_calculation_issue_in_pv
            sale_obj.was_there_calculation_issue_in_bv = was_there_calculation_issue_in_bv
            sale_obj.was_there_calculation_issue_in_li = was_there_calculation_issue_in_li

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
                sale_obj.pv = o_pv
                sale_obj.grand_pv = o_pv
            if was_there_calculation_issue_in_bv:
                sale_obj.bv = o_bv
                sale_obj.grand_bv = o_bv
            if was_there_calculation_issue_in_grand_total:
                sale_obj.grand_total = grand_total_amount
                sale_obj.grand_total = grand_total_amount

            try:
                sale_obj.save()
                sale_obj.save()
            except:
                pass

        if check:
            if was_there_calculation_issue_in_li or was_there_calculation_issue_in_pv or was_there_calculation_issue_in_bv or was_there_calculation_issue_in_grand_total:
                return False
            else:
                return True

        if loop == 0:
            recalculate_everything_mlm(request, myid=myid, post_bill=post_bill, check=False, mlm_admin=mlm_admin, loop=(loop + 1), cf=cf)

        # If this rechecking function found any error, then we will test if the issues are still remaining.
        # just to avoid any chances of infinite loop.
        else:
            if was_there_calculation_issue_in_li or was_there_calculation_issue_in_pv or was_there_calculation_issue_in_bv or was_there_calculation_issue_in_grand_total:
                if recalculate_everything_mlm(request, myid=myid, post_bill=post_bill, check=True, mlm_admin=mlm_admin,  loop=(loop + 1), cf=cf):
                    output = output + "All changes were done successfully"
                else:
                    output = output + "Changes were unsuccessful. Please contact admin."
            else:
                output = output + "No issues found."

        # o = sale_obj
        # obj = sale_obj
        #
        # pv = sum([li.pv for li in obj.order.lineitem_set.all()])
        # bv = sum([li.bv for li in obj.order.lineitem_set.all()])
        # grand_total = sum([li.total_amount for li in obj.order.lineitem_set.all()])

        if not post_bill:
            messages.success(request, output)
    else:
        messages.warning(request, 'Please check for Sale ID or contact Admin')

    if cf:
        return redirect('cnf_view_sale', myid=myid)
    else:
        return redirect('view_sale', myid=myid)