import json
from datetime import timedelta

import requests
import xlwt
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from accounts.models import Profile, ReferralCode
from mlm_admin.models import *
from shop.calculation import calculated_business_value, calculated_point_value
from shop.order_id import order_id
from shop.models import Order, Material_center
from .models import *
from .common_code import *
from .new_inventory_calculation import *

from django.http import HttpResponse
from django.views.generic import View

# importing get_template from loader
from django.template.loader import get_template
from .utils import render_to_pdf

from business.views import month_fn, year_fn, last_month_fn, last_year_fn, previous_month
from .recalculate import recalculate_everything
from .new_inventory_calculation import calculate_distributor_inventory
from pyjama import j


# Create your views here.

def is_distributor(user):
    try:
        return user.is_authenticated and user.profile.distributor is not False
    except Profile.DoesNotExist:
        return False


def home(request):
    try:
        material = Material_center.objects.get(advisor_registration_number = request.user)
    except:
        material = []
        messages.warning(request, "Material Center is not assigned to you. Please contact Admin.")
        return redirect('home')

    sale_this_month = Order.objects.filter(date__month=month_fn(), date__year=year_fn(),
                                           paid=True, delete=False, material_center=material, ).exclude(status=8).exclude(
                                           email="stockvariance@auretics.com").exclude(
                                           email="loyalty@auretics.com", )
    sale_this_month_dp = sale_this_month.aggregate(Sum('grand_total'))['grand_total__sum']
    sale_this_month_bv = sale_this_month.aggregate(Sum('bv'))['bv__sum']
    sale_last_month = Order.objects.filter(date__month=last_month_fn(), date__year=last_year_fn(),
                                           paid=True, delete=False, material_center=material, ).exclude(status=8).exclude(
                                           email="stockvariance@auretics.com").exclude(
                                           email="loyalty@auretics.com", )
    sale_last_month_dp = sale_last_month.aggregate(Sum('grand_total'))['grand_total__sum']
    sale_last_month_bv = sale_last_month.aggregate(Sum('bv'))['bv__sum']
    sale_till_date = Order.objects.filter(date__year=year_fn(), paid=True, delete=False, material_center=material, ).exclude(
                                           status=8).exclude(
                                           email="stockvariance@auretics.com").exclude(
                                           email="loyalty@auretics.com", )
    sale_till_date_dp = sale_till_date.aggregate(Sum('grand_total'))['grand_total__sum']
    sale_till_date_bv = sale_till_date.aggregate(Sum('bv'))['bv__sum']

    monthly_bv = []
    monthly_grand_total = []
    monthly_bv_month = []
    monthly_order = []
    monthly_order_bv = 0
    monthly_grand_total_bv = 0
    prev_month, prev_year = month_fn(), year_fn()
    for x in range(12):
        monthly_order = Order.objects.filter(date__month=prev_month, date__year=prev_year,
                                             paid=True, delete=False, material_center=material, ).exclude(
                                             status=8).exclude(email="stockvariance@auretics.com").exclude(
                                             email="loyalty@auretics.com")
        monthly_order_bv = monthly_order.aggregate(Sum('bv'))['bv__sum']
        if monthly_order_bv:
            monthly_order_bv = monthly_order_bv/1000
        else:
            monthly_order_bv = 0.0

        monthly_bv.append(int(monthly_order_bv))

        monthly_grand_total_bv = monthly_order_bv
        monthly_grand_total.append(int(monthly_grand_total_bv))

        monthly_bv_month.append(int(prev_month))
        prev_month, prev_year = previous_month(prev_month, prev_year)

    daily_bv = []
    daily_grand_total = []
    daily_bv_date = []
    daily_order = []
    daily_order_bv = 0
    daily_order_grand_total = 0
    date_now = datetime.now()
    for x in range(30):
        daily_order = Order.objects.filter(date__day=date_now.day, date__month=date_now.month,
                                           date__year=date_now.year, paid=True,
                                           delete=False, material_center=material).exclude(
                                           status=8).exclude(email="stockvariance@auretics.com").exclude(
                                           email="loyalty@auretics.com")
        # daily_order_bv = sum([li.bv for li in daily_order])/1000
        daily_order_bv = daily_order.aggregate(Sum('bv'))['bv__sum']
        if daily_order_bv:
            daily_order_bv = daily_order_bv / 1000
        else:
            daily_order_bv = 0.0
        daily_bv.append(int(daily_order_bv))

        # daily_order_grand_total = sum([li.grand_total for li in daily_order]) / 1000
        daily_order_grand_total = daily_order.aggregate(Sum('grand_total'))['grand_total__sum']
        if daily_order_grand_total:
            daily_order_grand_total = daily_order_grand_total / 1000
        else:
            daily_order_grand_total = 0.0
        daily_grand_total.append(int(daily_order_grand_total))

        daily_bv_date.append(int(date_now.day))
        date_now = date_now - timedelta(days=1)

    monthly_bv.reverse()
    monthly_bv_month.reverse()
    monthly_grand_total.reverse()
    daily_grand_total.reverse()
    daily_bv.reverse()
    daily_bv_date.reverse()

    return render(request, 'distributor/base.html', {
                                                   'title': 'Auretics Dashboard',
                                                   'sale_this_month_dp':sale_this_month_dp,
                                                   'sale_this_month_bv':sale_this_month_bv,
                                                   'sale_last_month_dp':sale_last_month_dp,
                                                   'sale_last_month_bv':sale_last_month_bv,
                                                   'sale_till_date_dp':sale_till_date_dp,
                                                   'sale_till_date_bv':sale_till_date_bv,
                                                   'monthly_bv':monthly_bv,
                                                   'monthly_bv_month':monthly_bv_month,
                                                   'monthly_grand_total':monthly_grand_total,
                                                   'daily_bv':daily_bv,
                                                   'daily_bv_date':daily_bv_date,
                                                   'daily_grand_total':daily_grand_total,
                                                   })


@user_passes_test(is_distributor, login_url='D_login')
def distributor_purchase_pending(request):
    today = datetime.now().date()
    data = Sale.objects.filter(advisor_distributor_name=request.user, delete=False, accept=False).order_by('-date')
    return render(request, 'distributor/pending_purchase_list.html',
                  {'data': data, 'title': 'Pending Purchase List', 'today': today})


@user_passes_test(is_distributor, login_url='D_login')
def distributor_purchase(request):
    today = datetime.now().date()
    data = Sale.objects.filter(advisor_distributor_name=request.user, delete=False, accept=True).order_by('-date')
    return render(request, 'distributor/purchase_list.html', {'data': data, 'title': 'Purchase List', 'today': today})


# def distributor_sale(request):
#     today = datetime.now().date()
#     data = Sale.objects.filter(sale_user_id = request.user).order_by('-date')
#     return render(request, 'distributor/sale_list.html', {'data': data,'title':'Distributor Sale List','today':today})
# return HttpResponse('<h1>data has been coming here</h1>')
# return render(request,'distributor/purchase_list.html')

@user_passes_test(is_distributor, login_url='D_login')
def view_distributor_pending_purchase(request, myid):
    today = datetime.now().date()
    if request.method == 'POST':
        distributor_purchase = Sale.objects.get(pk=myid)
        Sale.objects.filter(pk=myid).update(accept= True, accepted_date= today)
        purchase_item_list = Sale_itemDetails.objects.filter(sale=distributor_purchase)
        for i in purchase_item_list:
            product = i.item
            batch1 = i.batch
            material = distributor_purchase.material_center_to
            try:
                # data_check = Distributor_Batch.objects.get(distributor_material_center=material, batch=i.batch)
                data_check = Distributor_Inventry.objects.get(created_on=today, material_center=material, batch=i.batch)
                updated_quantity = int(data_check.current_quantity) + int(i.quantity)
                update_data = Distributor_Inventry.objects.filter(created_on=today, material_center=material,
                                                               batch=i.batch).update(current_quantity=updated_quantity)
            except:
                new_batch = Distributor_Inventry(material_center=material, batch=i.batch, current_quantity=i.quantity)
                new_batch.save()
            # <----------------------------------------------------------------------------here we are creating inventory start code------------------------------------------------------------------------------------------------------>
            distributor_pending_purchase_inventry(
                product= product,
                batch= batch1,
                material_center= material,
                quantity= i.quantity,
                batch_mrp= batch1.mrp
            )
        return redirect('distributor_purchase')
    sale_data = Sale.objects.get(pk=myid, accept=False)
    data = Sale_itemDetails.objects.filter(sale=sale_data)
    if sale_data.advisor_distributor_name != request.user:
        messages.warning(request, 'Sorry you are not authorize to check these records!')
        return redirect('distributor_pending_purchase')
    params = {
        'sale_data': sale_data,
        'data': data,
        'title': 'Distributor  purchase View'
    }
    return render(request, 'distributor/view_pending_purchase.html', params)


@user_passes_test(is_distributor, login_url='D_login')
def view_distributor_purchase(request, myid):
    sale_data = Sale.objects.get(pk=myid, accept=True)
    data = Sale_itemDetails.objects.filter(sale=sale_data)
    if sale_data.advisor_distributor_name != request.user:
        messages.warning(request, 'Sorry you are not authorize to check these records!')
        return redirect('distributor_purchase')
    params = {
        'sale_data': sale_data,
        'data': data,
        'title': 'Distributor  purchase View'
    }
    return render(request, 'distributor/view_purchase.html', params)


def testing(request):
    today = datetime.now().date()
    product = Product.objects.get(pk=1)
    batch1 = Batch.objects.get(pk=3)
    material = Material_center.objects.get(pk=14)
    D_inventory_update = Inventry.objects.filter(product=product, batch=batch1,
                                                 material_center=material).latest('created_on')

    update_time_inventry = Distributor_Inventry.objects.get(created_on=today, product=product,
                                                            batch=batch1, material_center=material)
    return HttpResponse(D_inventory_update)


@user_passes_test(is_distributor, login_url='D_login')
def distributor_add_sale(request, distributor_sale_id=None):
    today = datetime.now().date()
    if request.method == "POST":
        date_data = datetime.now().date()
        # mc_center = request.POST['material_center']
        mc_center = Material_center.objects.get(advisor_registration_number=request.user).pk
        advisor_user = request.POST['advisor_user']
        sale_type = request.POST['sale_type']
        narration = request.POST['narration']
        grand_total = 0 #request.POST['grand_total']
        payment_mode = request.POST['payment_mode']
        quaantity_item = request.POST.getlist('quaantity_item')
        check_quantity = request.POST.getlist('check_quantity')
        result = quantity_validate(check_quantity, quaantity_item)
        if result == False:
            messages.success(request, "Bad Request (Quantity entered is greater than maximum allowed quantity).")
            return redirect('distributor_add_sale')
        # vat_item = request.POST.getlist('vat_item')
        item = request.POST.getlist('item')
        batch = request.POST.getlist('batch')

        # AG :: Validation to find if duplicate batch items exists
        if not len(batch) == len(set(batch)):
            messages.success(request, "Order Validation Error: Duplicate Batch Found. Please Try Again or Contact Admin")
            return redirect('distributor_sale_list')

        totalamount_item = request.POST.getlist('totalamount_item')

        # AG :: Error will raise if user's email id is not passed.
        if not advisor_user:
            messages.success(request,
                             "Error: User not selected. Please select user from the drop down list under Advisor/Distributor.")
            return redirect('distributor_sale_list')
        user = User.objects.get(email=advisor_user)
        material_center = Material_center.objects.get(pk=mc_center)
        order_id1 = order_id(material_center)
        try:
            postal_code = user.profile.shipping_address.pin
            shipping_address = user.profile.shipping_address
        except:
            postal_code = 0
            shipping_address = []
            # Shipping address is shipping address
        o = Order(
            name=user.username,
            email=user.email,
            user_id = request.user,
            postal_code=postal_code,
            shipping_address=shipping_address,
            order_id1=order_id1,
            grand_total=grand_total,
            delivered_date=date_data,
            status=4,
            paid=True,
            material_center=material_center
        )
        o.save()
        if 'distributor_sale_id' in request.POST:
            data = Distributor_Sale.objects.get(pk=request.POST['distributor_sale_id'])
            data.sale_user_id = request.user
            data.material_center = material_center
            data.date = date_data
            data.narration = narration
            data.advisor_distributor_name = user
            data.payment_mode = payment_mode
            data.sale_type = sale_type
            data.grand_total = grand_total
            data.order = o
            data.is_pending = False
        else:
            data = Distributor_Sale(sale_user_id=request.user, material_center=material_center, date=date_data,
                                    narration=narration, advisor_distributor_name=user, payment_mode=payment_mode,
                                    sale_type=sale_type, grand_total=grand_total, order=o, is_pending=False)
        data.save()

        try:
            for i, k in enumerate(totalamount_item):
                sale = data
                quantity = quaantity_item[i]
                total_amount = totalamount_item[i]
                product = item[i]
                product = Product.objects.get(pk=product)
                batch1 = batch[i]
                batch1 = Batch.objects.get(pk=batch1)

                mrp = batch1.mrp
                cgst = product.cgst
                sgst = product.sgst
                igst = product.igst
                distributor_price = product.distributor_price
                if cgst == None:
                    cgst = 0
                if sgst == None:
                    sgst = 0
                if igst == None:
                    igst = 0
                if distributor_price == None:
                    distributor_price = 0

                distributor_price = mrp / ((100 + distributor_price) / 100)
                igst = 0
                cgst = 0
                sgst = 0

                # if sale_type == '1':
                #     distributor_price = mrp / ((100 + igst) / 100) / ((100 + distributor_price) / 100)
                #     igst = distributor_price * (igst / 100)
                #     igst = round(igst, 2)
                #     cgst = 0
                #     sgst = 0
                # else:
                #     distributor_price = mrp / ((100 + igst) / 100) / ((100 + distributor_price) / 100)
                #     cgst = distributor_price * ((igst/2) / 100)
                #     cgst = round(igst/2, 2)
                #     sgst = distributor_price * ((igst/2) / 100)
                #     sgst = cgst
                #     igst = 0

                distributor_price = round(distributor_price, 2)
                total_amount = int(quantity) * distributor_price
                total_amount = round(total_amount, 2)            

                try:
                    batch_qty = Distributor_Inventry.objects.get(created_on=today, batch=batch1, material_center=material_center)
                except ObjectDoesNotExist:
                    raise Exception(
                        f'Distributor_Batch does not exist for batch <b> {batch1} </b>, and for material_center <b> {material_center} </b> please contact to the administrator.')
                # inventory code start
                batch_quantity = batch_qty.current_quantity
                update_batch_quantity = int(batch_quantity) - int(quantity)
                Distributor_Inventry.objects.filter(batch=batch1, material_center=material_center).update(current_quantity=update_batch_quantity)

                # AG :: Re-calculating Distributor's Quantity First
                calculate_distributor_inventory(product=product,
                                                batch=batch1,
                                                material_center=material_center,
                                                quantity=0
                                                )

                # AG :: Checking whether stock of this item exist in our system.
                available_quantity = Distributor_Inventry.objects.filter(batch=batch1,
                                                                         material_center=material_center).latest('pk').current_quantity
                if not int(available_quantity) >= int(quantity):
                    messages.success(request,
                                     "Order Validation Error. Insufficient Quantity. Please Try Again or Contact Admin")
                    return redirect('distributor_sale_list')

                # AG :: Now deducting the quantity from Distributor's Inventory and recalulation inventory again.
                calculate_distributor_inventory(product= product,
                    batch= batch1,
                    material_center= material_center,
                    quantity= quantity
                )

                saledata = Distributor_Sale_itemDetails(item=product, sale=sale, batch=batch1, quantity=quantity,
                                                        distributor_price=distributor_price, cgst=cgst, sgst=sgst, igst=igst, vat=0,
                                                        total_amount=total_amount)
                li = LineItem(
                    order_by=user.email,
                    product_id=product.id,
                    price=distributor_price,
                    # price = cart_item.price,
                    quantity=quantity,
                    order_id=o.id,
                    batch=batch1,
                    cgst=product.cgst,
                    sgst=product.sgst,
                    igst=product.igst,
                    total_amount=total_amount,
                    pv=calculated_point_value(product, distributor_price, quantity),
                    bv=calculated_business_value(product, distributor_price, quantity)
                )
                li.save()
                saledata.save()

            messages.success(request, "Record added successfully!")

        except Exception as e:
            # messages.warning(request, str(error))
            messages.error(request, str(e))

        # updating pv, bv and grand total from the backend
        # o = Order.objects.get(pk=o.id)
        # pv = sum([li.pv for li in o.lineitem_set.all()])
        # bv = sum([li.bv for li in o.lineitem_set.all()])
        # grand_total = sum([li.total_amount for li in o.lineitem_set.all()])
        # Order.objects.filter(pk=o.id).update(pv=pv, bv=bv, grand_total=grand_total)
        # Distributor_Sale.objects.filter(pk=sale.id).update(grand_pv=pv, grand_bv=bv, grand_total=grand_total)

        # order_data = Order.objects.get(pk=o.pk)
        # user = User.objects.get(email=order_data.email)
        # updaate_super_bv(order_data.bv, user)

        recalculate_everything(request, myid=sale.id, post_bill=True, check=False, mlm_admin=False)
        return redirect('distributor_view_sale', myid=sale.id)

    referral_code = request.user.pk
    # try:
    #     material = Material_center.get_center_for_user(request.user, advisory_owned='YES')
    # except ObjectDoesNotExist:
    #     material = None
    batches = Batch.objects.all().exclude(delete=True)
    material = Material_center.objects.get(advisor_registration_number=request.user)
    if material:
        products = Distributor_Inventry.objects.filter(created_on=today, current_quantity__gt=0, material_center=material).values_list('product')
    else:
        products = Distributor_Inventry.objects.filter(created_on=today, current_quantity__gt=0).values_list('product')
    # products = Distributor_Inventry.objects.filter(current_quantity__gte = 0).values_list('product')
    products = set(products)
    product = []
    for i in products:
        for j in i:
            product.append(j)

    items = Product.objects.filter(pk__in=product).exclude(delete=True)
    myDate = datetime.now()
    formatedDate = myDate.strftime("%Y-%m-%d")
    params = {
        'date': formatedDate,
        'batches': batches,
        'items': items,
        'material': material,
    }
    if request.method == 'GET' and distributor_sale_id:
        pending_sale = Distributor_Sale.objects.get(pk=distributor_sale_id)
        order = pending_sale.order
        line_items = order.lineitem_set.all()
        params.update(line_items=line_items)
        params.update(sale_data=pending_sale)

    return render(request, 'distributor/add_sale.html', params)


'''
@user_passes_test(is_distributor, login_url='D_login')
def distributor_add_loyalty_sale(request, distributor_sale_id=None):
    if request.method == "POST":
        # try:
        date_data = request.POST['date']
        mc_center = request.POST['material_center']
        # TBD
        # user = request.POST['user']
        advisor_user = request.POST['advisor_user']
        sale_type = request.POST['sale_type']
        narration = request.POST['narration']
        grand_total = request.POST['grand_total']
        payment_mode = request.POST['payment_mode']
        quaantity_item = request.POST.getlist('quaantity_item')
        check_quantity = request.POST.getlist('check_quantity')
        result = quantity_validate(check_quantity, quaantity_item)
        if result == False:
            messages.success(request, "Bad Request (Quantity entered is greater than maximum allowed quantity).")
            return redirect('distributor_add_sale')
        distributor_price = request.POST.getlist('distributor_price')
        cgst_item = request.POST.getlist('cgst_item')
        sgst_item = request.POST.getlist('sgst_item')
        igst_item = request.POST.getlist('igst_item')
        # vat_item = request.POST.getlist('vat_item')
        item = request.POST.getlist('item')
        batch = request.POST.getlist('batch')
        totalamount_item = request.POST.getlist('totalamount_item')
        user = User.objects.get(email=advisor_user)
        material_center = Material_center.objects.get(pk=mc_center)
        order_id1 = order_id(material_center)
        try:
            # Shipping address is shipping address
            o = Order(
                name=user.username,
                email=user.email,
                postal_code=user.profile.shipping_address.pin,
                shipping_address=user.profile.shipping_address,
                order_id1=order_id1,
                grand_total=grand_total,
                delivered_date=date_data,
                status=4,
                paid=True,
                material_center=material_center
            )
        except:
            # shipping address is billing address here
            o = Order(
                name=user.username,
                email=user.email,
                postal_code=user.profile.billing_address.pin,
                shipping_address=user.profile.billing_address,
                order_id1=order_id1,
                grand_total=grand_total,
                delivered_date=date_data,
                status=4,
                paid=True,
                material_center=material_center
            )
        o.save()
        if 'distributor_sale_id' in request.POST:
            data = Distributor_Sale.objects.get(pk=request.POST['distributor_sale_id'])
            data.sale_user_id = request.user
            data.material_center = material_center
            data.date = date_data
            data.narration = narration
            data.advisor_distributor_name = user
            data.payment_mode = payment_mode
            data.sale_type = sale_type
            data.grand_total = grand_total
            data.order = o
            data.is_pending = False
        else:
            data = Distributor_Sale(sale_user_id=request.user, material_center=material_center, date=date_data,
                                    narration=narration, advisor_distributor_name=user, payment_mode=payment_mode,
                                    sale_type=sale_type, grand_total=grand_total, order=o, is_pending=False)
        data.save()

        try:
            for i, k in enumerate(totalamount_item):
                sale = data
                quantity = quaantity_item[i]
                price = distributor_price[i]
                # total_price = totalamount_item[i]
                cgst = cgst_item[i]
                sgst = sgst_item[i]
                igst = igst_item[i]
                # vat = vat_item[i]
                total_amount = totalamount_item[i]
                product = item[i]
                product = Product.objects.get(pk=product)
                batch1 = batch[i]
                batch1 = Batch.objects.get(pk=batch1)
                try:
                    batch_qty = Distributor_Batch.objects.get(batch=batch1, distributor_material_center=material_center)
                except ObjectDoesNotExist:
                    raise Exception(
                        f'Distributor_Batch does not exist for batch <b> {batch1} </b>, and for material_center <b> {material_center} </b> please contact to the administrator.')
                # inventory code start
                batch_quantity = batch_qty.quantity
                update_batch_quantity = int(batch_quantity) - int(quantity)
                Distributor_Batch.objects.filter(pk=batch_qty.pk).update(quantity=update_batch_quantity)
                try:
                    today = datetime.now().date()
                    D_inventory_update = Distributor_Inventry.objects.get(product=product, batch=batch1,
                                                                          material_center=material_center,
                                                                          created_on=today)
                    D_inventory_update_current_quantity = int(D_inventory_update.current_quantity) - int(quantity)
                    D_inventory_update_quantity_out = int(D_inventory_update.quantity_out) + int(quantity)
                    Distributor_Inventry.objects.filter(product=product, batch=batch1, material_center=material_center,
                                                        created_on=today).update(
                        current_quantity=D_inventory_update_current_quantity,
                        quantity_out=D_inventory_update_quantity_out)
                except:
                    # here add code for inventry start here 20-03-2021
                    try:
                        D_inventory_update = Distributor_Inventry.objects.filter(product=product, batch=batch1,
                                                                                 material_center=material_center).latest(
                            'created_on')
                        current_quantity = int(D_inventory_update.current_quantity) + int(quantity)
                        D_inventory = Distributor_Inventry(product=product, batch=batch1,
                                                           material_center=material_center,
                                                           opening_quantity=D_inventory_update.opening_quantity,
                                                           current_quantity=current_quantity,
                                                           quantity_out=quantity)
                        D_inventory.save()
                    except:
                        D_inventory = Distributor_Inventry(product=product, batch=batch1,
                                                           material_center=material_center,
                                                           opening_quantity=0, current_quantity=quantity,
                                                           quantity_out=quantity)
                        D_inventory.save()

                saledata = Distributor_Sale_itemDetails(item=product, sale=sale, batch=batch1, quantity=quantity,
                                                        distributor_price=price, cgst=cgst, sgst=sgst, igst=igst, vat=0,
                                                        total_amount=total_amount)
                li = LineItem(
                    order_by=user.email,
                    product_id=product.id,
                    price=price,
                    # price = cart_item.price,
                    quantity=quantity,
                    order_id=o.id,
                    batch=batch1,
                    cgst=product.cgst,
                    sgst=product.sgst,
                    igst=product.igst,
                    total_amount=total_amount,
                    pv=calculated_point_value(product, price, quantity),
                    bv=calculated_business_value(product, price, quantity)
                )
                li.save()
                saledata.save()

            o = Order.objects.get(pk=o.id)
            pv = sum([li.pv for li in o.lineitem_set.all()])
            bv = sum([li.bv for li in o.lineitem_set.all()])
            grand_total = sum([li.total_amount for li in o.lineitem_set.all()])
            Order.objects.filter(pk=o.id).update(pv=pv, bv=bv, grand_total=grand_total)

            order_data = Order.objects.get(pk=o.pk)
            user = User.objects.get(email=order_data.email)
            # updaate_super_bv(order_data.bv, user)
            messages.success(request, "Record added successfully!")
            return redirect('distributor_sale_list')
        except Exception as error:
            messages.error(request, str(error))
            return redirect('distributor_add_sale')
    referral_code = request.user.pk
    try:
        material = Material_center.get_center_for_user(request.user, advisory_owned='YES')
    except ObjectDoesNotExist:
        material = None
    batches = Batch.objects.all().exclude(delete=True)
    today = datetime.now().date()
    products = Distributor_Inventry.objects.filter(created_on=today, current_quantity__gte=0).values_list('product')
    # products = Distributor_Inventry.objects.filter(current_quantity__gte = 0).values_list('product')
    products = set(products)
    product = []
    for i in products:
        for j in i:
            product.append(j)

    items = Product.objects.filter(pk__in=product).exclude(delete=True)
    myDate = datetime.now()
    formatedDate = myDate.strftime("%Y-%m-%d")
    params = {
        'date': formatedDate,
        'batches': batches,
        'items': items,
        'material': material,
        'users': User.objects.all()
    }
    if request.method == 'GET' and distributor_sale_id:
        pending_sale = Distributor_Sale.objects.get(pk=distributor_sale_id)
        order = pending_sale.order
        line_items = order.lineitem_set.all()
        params.update(line_items=line_items)
        params.update(sale_data=pending_sale)

    return render(request, 'distributor/add_loyalty_sale.html', params)
'''




@csrf_exempt
def add_saleField(request):
    cnt_multiple_product = request.POST['cnt_multiple_product']
    today = datetime.now().date()
    products = Distributor_Inventry.objects.filter(created_on=today, current_quantity__gt=0).values_list('product')
    products = set(products)
    product = []
    for i in products:
        for j in i:
            product.append(j)
    items = Product.objects.filter(pk__in=product).exclude(delete=True)
    batches = Batch.objects.all().exclude(delete=True)
    params = {
        'items': items,
        'batches': batches,
        'cnt_multiple_product': cnt_multiple_product
    }
    return render(request, 'distributor/add_more_sale_fields.html', params)

@user_passes_test(is_distributor, login_url='D_login')
def distributor_sale_deleted_list(request):
    response = distributor_sale_list(request, deleted=True)
    return response

@user_passes_test(is_distributor, login_url='D_login')
def distributor_sale_list(request, deleted=False):
    pending_sales_view = request.GET.get('pending_sales', '')
    today = datetime.now().date()
    data = Distributor_Sale.objects.filter(delete=deleted, sale_user_id=request.user,
                                           is_pending=False, is_loyalty_sale=False)
    return render(request, 'distributor/sale_list.html', {'data': data, 'title': 'Sale List',
                                                          'today': today, 'pending_sales_view': pending_sales_view,
                                                          'data_from_pending_sale': False,
                                                          'deleted':deleted})


@user_passes_test(is_distributor, login_url='D_login')
def distributor_sale_list_pending(request):
    today = datetime.now().date()
    data = Distributor_Sale.objects.filter(delete = False, order__paid=False,
                                            is_pending= True, material_center__advisor_registration_number= request.user)
    return render(request, 'distributor/sale_list.html', {'data': data, 'title':'Sale List',
                                                          'today':today, 'pending_sales_view': True,
                                                          'data_from_pending_sale': True})


@user_passes_test(is_distributor, login_url='D_login')
def distributor_view_sale(request, myid):
    sale = Distributor_Sale.objects.get(pk=myid)
    shopLineObj = LineItem.objects.filter(order=sale.order)
    # <------------------------------------------------------------------------------------------------------------------------------------------------------------------------>
    batches = Batch.objects.all().exclude(delete=True)
    items = Product.objects.all().exclude(delete=True)
    users = User.objects.all()
    # sale_data = Distributor_Sale.objects.get(pk=myid)
    # data = Distributor_Sale_itemDetails.objects.filter(sale=sale)
    if sale.sale_user_id != request.user:
        messages.warning(request, 'You are not allowed to update these records')
        return redirect('distributor_sale_list')
    pending_sales_view = request.GET.get('pending_sales', '')
    params = {
        'batches': batches,
        'items': items,
        'users': users,
        'sale_data': sale,
        'data': shopLineObj,
        'title': 'View Sale',
        'myid':myid,
    }
    return render(request, 'distributor/view_sale.html', params)

    # <------------------------------------------------------------------------------------------------------------


@user_passes_test(is_distributor, login_url='D_login')
def distributor_edit_sale(request, myid):
    today = datetime.now().date()
    # check that myid belongs to the current logged in user, required.
    # <--------------------------------------------------Dealing with post request Start here---------------------------------------------------------------------------------------------------------------------->
    if request.method == "POST":
        date = request.POST['date']
        mc_center = request.POST['material_center']
        # mc_center_from = request.POST['material_center_from']
        narration = request.POST['narration']
        user = request.POST['advisor_user']
        # party_name = request.POST['party_name']
        sale_type = request.POST['sale_type']
        grand_total = 0 #request.POST['grand_total']
        # grand_pv = request.POST['grand_pv']
        # grand_bv = request.POST['grand_bv']
        payment_mode = request.POST['payment_mode']
        item = request.POST.getlist('item')
        batch = request.POST.getlist('batch')

        # AG :: Validation to find if duplicate batch items exists
        if not len(batch) == len(set(batch)):
            messages.success(request,
                             "Order Validation Error. Duplicate Batch Found. Please Try Again or Contact Admin")
            return redirect('distributor_sale_list')

        quaantity_item = request.POST.getlist('quaantity_item')
        check_quantity = request.POST.getlist('check_quantity')
        result = quantity_validate(check_quantity, quaantity_item)
        if result == False:
            messages.success(request, "Bad Request (Quantity entered is greater than maximum allowed quantity).")
            return redirect('distributor_sale_list')
        distributor_price = request.POST.getlist('distributor_price')
        cgst_item = request.POST.getlist('cgst_item')
        sgst_item = request.POST.getlist('sgst_item')
        igst_item = request.POST.getlist('igst_item')
        # pv_item = request.POST.getlist('pv_item')
        # bv_item = request.POST.getlist('bv_item')
        # vat_item = request.POST.getlist('vat_item')
        totalamount_item = request.POST.getlist('totalamount_item')
        user = User.objects.get(email=user)
        # try:
        material_center = Material_center.objects.get(pk=mc_center)
        # material_center_from = Material_center.objects.get(pk=mc_center_from)
        # user = User.objects.get(pk=user)
        data = Distributor_Sale.objects.filter(pk=myid).update(
                                                               # sale_user_id=request.user,      # AG: removed as we dont want to update user in any case.
                                                               material_center=material_center,
                                                               # advisor_distributor_name=user,  # AG: removed as we dont want to update user in any case.
                                                               date=date,
                                                               narration=narration, sale_type=sale_type,
                                                               grand_total=grand_total, payment_mode=payment_mode,
                                                               is_edited=True)
        obj = Distributor_Sale.objects.get(pk=myid)
        try:
            postal_code = user.profile.shipping_address.pin
            shipping_address = user.profile.shipping_address
        except:
            postal_code = ""
            shipping_address = ""

        Order.objects.filter(pk=obj.order.pk).update(grand_total=grand_total,
                                                     # name=user.username,          # AG: removed as we dont want to update user in any case.
                                                     # email=user.email,            # AG: removed as we dont want to update user in any case.
                                                     paid=True,
                                                     postal_code=postal_code,
                                                     shipping_address=shipping_address,
                                                     # material_center=material_center  # AG: removed as we dont want to update MC in any case.
                                                     )

        if Order.objects.filter(pk=obj.order.pk).delete:
            messages.success(request, "Bad Request (You are not allowed to edit deleted Orders). ID: " + str(obj.order.pk))
            return redirect('distributor_sale_list')

        sale_items = Distributor_Sale_itemDetails.objects.filter(sale=obj)

        for i in sale_items:
            # distributor_batch = Distributor_Inventry.objects.get(created_on=today, batch=i.batch,
            #                                                   material_center=obj.material_center)
            # update_time_batch_quantity = int(distributor_batch.current_quantity) + int(i.quantity)
            # Distributor_Inventry.objects.filter(pk=distributor_batch.pk).update(created_on=today, current_quantity=update_time_batch_quantity)
            # today = datetime.now().date()
            update_time_inventry = Distributor_Inventry.objects.get(created_on=today, product=i.item,
                                                                    batch=i.batch, material_center=obj.material_center)
            update_time_inventry_current_quantity = int(update_time_inventry.current_quantity) + int(i.quantity)
            update_time_inventry_quantity_out = int(update_time_inventry.quantity_out) - int(i.quantity)
            Distributor_Inventry.objects.filter(pk=update_time_inventry.pk).update(
                current_quantity=update_time_inventry_current_quantity,
                quantity_out=update_time_inventry_quantity_out)
        Distributor_Sale_itemDetails.objects.filter(sale=obj).delete()
        LineItem.objects.filter(order_id=obj.order.pk).delete()

        try:
            for i, k in enumerate(totalamount_item):
                sale = obj
                quantity = quaantity_item[i]
                price = distributor_price[i]
                cgst = cgst_item[i]
                sgst = sgst_item[i]
                igst = igst_item[i]
                # pv_total = pv_item[i]
                # bv_total = bv_item[i]
                # vat = vat_item[i]
                total_amount = totalamount_item[i]
                product = item[i]
                product = Product.objects.get(pk=product)
                batch1 = batch[i]
                batch1 = Batch.objects.get(pk=batch1)
                batch_qty = Distributor_Inventry.objects.get(created_on=today, batch=batch1, material_center=material_center)
                # inventory code start
                batch_quantity = batch_qty.current_quantity
                update_batch_quantity = int(batch_quantity) - int(quantity)
                Distributor_Inventry.objects.filter(pk=batch_qty.pk).update(current_quantity=update_batch_quantity)

                # AG :: Re-calculating Distributor's Quantity First
                calculate_distributor_inventory(product=product,
                                                batch=batch1,
                                                material_center=material_center,
                                                quantity=0
                                                )

                # AG :: Checking whether stock of this item exist in our system.
                available_quantity = Distributor_Inventry.objects.filter(batch=batch1,
                                                                         material_center=material_center).latest('pk').current_quantity
                if not int(available_quantity) >= int(quantity):
                    messages.success(request,
                                     "Order Validation Error. Insufficient Quantity. Please Try Again or Contact Admin")
                    return redirect('distributor_sale_list')

                # AG :: Now deducting the quantity from Distributor's Inventory and recalulation inventory again.
                calculate_distributor_inventory(product= product,
                    batch= batch1,
                    material_center= material_center,
                    quantity= quantity
                )

                saledata = Distributor_Sale_itemDetails(item=product, sale=sale, batch=batch1, quantity=quantity,
                                                        distributor_price=price, cgst=cgst, sgst=sgst, igst=igst, vat=0,
                                                        total_amount=total_amount)
                li = LineItem(
                    order_by=user.email,
                    product_id=product.id,
                    price=price,
                    # price = cart_item.price,
                    quantity=quantity,
                    order_id=obj.order.id,
                    batch=batch1,
                    cgst=product.cgst,
                    sgst=product.sgst,
                    igst=product.igst,
                    total_amount=total_amount,
                    pv=calculated_point_value(product, price, quantity),
                    bv=calculated_business_value(product, price, quantity)
                )
                li.save()
                saledata.save()

            messages.success(request, "Record added successfully!")
        except Exception as e:
            # print(e)
            messages.error(request, "something went wrong " + str(e))

        # Saving BV & PV of edited item on Database.
        recalculate_everything(request, myid=myid, post_bill=True, check=False, mlm_admin=False)

        # o = Order.objects.get(pk=obj.order.id)
        # pv = sum([li.pv for li in obj.order.lineitem_set.all()])
        # bv = sum([li.bv for li in obj.order.lineitem_set.all()])
        # grand_total = sum([li.total_amount for li in obj.order.lineitem_set.all()])
        # Order.objects.filter(pk=obj.order.id).update(pv=pv, bv=bv, grand_total=grand_total, modified=True)
        # Distributor_Sale.objects.filter(pk=myid).update(grand_pv=pv, grand_bv=bv, grand_total=grand_total)

        # order_data = Order.objects.get(pk=o.pk)
        # user = User.objects.get(email=order_data.email)
        return redirect('distributor_view_sale', myid=myid)

    # <--------------------------------------------------Dealing with post request End here--------------------------------------------------------------------------------------------------------------------->

    today = datetime.now().date()
    products = Distributor_Inventry.objects.filter(created_on=today).values_list('product')
    products = set(products)
    product = []
    for i in products:
        for j in i:
            product.append(j)
    batches = Batch.objects.all().exclude(delete=True)
    items = Product.objects.filter(pk__in=product).exclude(delete=True)
    sale_data = Distributor_Sale.objects.get(pk=myid)
    shopLineObj = LineItem.objects.filter(order=sale_data.order)
    # data = Distributor_Sale_itemDetails.objects.filter(sale=sale_data)
    today = datetime.now().date()
    if sale_data.created_on != today:
        messages.warning(request, 'You are not able to update these records')
        return redirect('distributor_sale_list')
    elif sale_data.sale_user_id != request.user:
        messages.warning(request, 'You are not able to update these records')
        return redirect('distributor_sale_list')
    params = {
        'batches': batches,
        'items': items,
        'sale_data': sale_data,
        'data': shopLineObj,
        'title': 'Edit Sale',
        'myid': myid,
    }
    return render(request, 'distributor/edit_sale.html', params)

    # <------------------------------------------------------------------------------------------------------------------------------------------------------------------------>


@user_passes_test(is_distributor, login_url='D_login')
def distributor_delete_sale(request, myid):
    sale = Distributor_Sale.objects.get(pk=myid)
    today = datetime.now().date()
    if sale.created_on != today:
        messages.warning(request, 'You are not able to delete this records')
        return redirect('distributor_sale_list')
    if sale.sale_user_id != request.user:
        messages.warning(request, 'You are not able to delete this records')
        return redirect('distributor_sale_list')
    sale_items = Distributor_Sale_itemDetails.objects.filter(sale=sale)

    # Updating Distributor Quantity
    for i in sale_items:
        distributor_batch = Distributor_Inventry.objects.get(created_on=today, batch=i.batch,
                                                          material_center=sale.material_center)
        update_time_batch_quantity = int(distributor_batch.current_quantity) + int(i.quantity)
        Distributor_Inventry.objects.filter(pk=distributor_batch.pk).update(current_quantity=update_time_batch_quantity)
        # today = datetime.now().date()
        # update_time_inventry = Distributor_Inventry.objects.get(created_on=today, product=i.item,
        #                                                         batch=i.batch, material_center=sale.material_center)
        # update_time_inventry_current_quantity = int(update_time_inventry.current_quantity) + int(i.quantity)
        # update_time_inventry_quantity_out = int(update_time_inventry.quantity_out) - int(i.quantity)
        # Distributor_Inventry.objects.filter(pk=update_time_inventry.pk).update(
        #     current_quantity=update_time_inventry_current_quantity,
        #     quantity_out=update_time_inventry_quantity_out)
        distributor_delete_sale_inventry(
            product=i.item,
            batch= i.batch,
            material_center=sale.material_center,
            quantity= i.quantity
        )

    # Marking Distributor Sale as Delete
    sale_delete = Distributor_Sale.objects.filter(pk=myid).update(delete=True)

    # Marking Shop Order Sale as Delete & zeroing bv & pv.
    shop_sale_delete = Order.objects.filter(pk=sale.order.id).update(delete=True, modified=True, bv=0, pv=0)

    messages.success(request, "Record deleted successfully!")
    return redirect('distributor_sale_list')


def product_detail(request):
    product_id = request.GET.get('product_id', False)
    batch_id = request.GET.get('batch_id', False)
    material_center = request.GET.get('material_center', False)
    material = Material_center.objects.get(pk=material_center)
    # sale_type= 0 for with in state(cgst+sgst) and sale_type = 1 for inter_state(igst)
    sale_type = request.GET.get('sale_type', False)
    product = Product.objects.get(pk=product_id)
    try:
        batch = Batch.objects.get(pk=batch_id)
    except:
        batch = Batch.objects.filter(pk=product)[0]
    # <-- here we are geting quantity from the inventry code start here -->
    # try:
    #     today = datetime.now().date()
    #     D_inventory_update = Distributor_Inventry.objects.get(product=product, batch=batch, material_center=material,
    #                                                           created_on=today, current_quantity__gt=0)
    #     D_inventory_update_current_quantity = int(D_inventory_update.current_quantity)
    #     batch_quantity = D_inventory_update_current_quantity
    # except:
    #     try:
    #         D_inventory_update = Distributor_Inventry.objects.filter(product=product, batch=batch,
    #                                                                  material_center=material, current_quantity__gt=0).latest('created_on')
    #         D_inventory = Distributor_Inventry(product=product, batch=batch, material_center=material,
    #                                            opening_quantity=D_inventory_update.opening_quantity,
    #                                            current_quantity=D_inventory_update.current_quantity,
    #                                            quantity_in=0, purchase_price=0)
    #         batch_quantity = D_inventory_update.current_quantity
    #         D_inventory.save()
    #     except:
    #         D_inventory = Distributor_Inventry(product=product, batch=batch, material_center=material,
    #                                            opening_quantity=0, current_quantity=0,
    #                                            quantity_in=0, purchase_price=0)
    #         batch_quantity = 0
    #         D_inventory.save()
    try:
        batch_quantity = Distributor_Inventry.objects.get(product=product, batch=batch, material_center=material,
                                                              created_on=datetime.now().date()).current_quantity
    except:
        batch_quantity = 0

    mrp = batch.mrp
    # cgst = product.cgst
    # sgst = product.sgst
    # igst = product.igst
    distributor_price = product.distributor_price
    # vat = product.vat
    # if cgst == None:
    #     cgst = 0
    # if sgst == None:
    #     sgst = 0
    # if igst == None:
    #     igst = 0
    if distributor_price == None:
        distributor_price = 0
    # if vat == None:
    #     vat = 0

    # distributor_price = (mrp / ((100 + igst) / 100)) / ((100 + distributor_price) / 100)
    distributor_price = round((mrp / ((100 + distributor_price) / 100)),2)

    # AG :: We have removed all the tax components from the order.
    # if sale_type == '1':
    #     igst = distributor_price * (igst / 100)
    #     cgst = 0
    #     sgst = 0
    #     vat = 0
    # else:
    #     cgst = distributor_price * ((igst / 2) / 100)
    #     cgst = round(igst / 2, 2)
    #     sgst = distributor_price * ((igst / 2) / 100)
    #     sgst = cgst
    #     igst = 0
    #
    # distributor_price = round(distributor_price, 2)
    # cgst = round(cgst, 2)
    # sgst = round(sgst, 2)
    # vat = round(vat, 2)
    # igst = round(igst, 2)
    igst = 0
    cgst = 0
    sgst = 0
    vat = 0
    params = {
        'distributor_price': distributor_price,
        'mrp': mrp,
        'cgst': cgst,
        'sgst': sgst,
        'igst': igst,
        'vat': vat,
        'pv': batch.pv,
        'bv': batch.bv,
        'batch_quantity': batch_quantity
    }
    return JsonResponse(status=200, data=params)


@user_passes_test(is_distributor, login_url='D_login')
def D_inventory_details(request):
    if request.method == 'POST':
        stock_details = request.POST['stock_details']
        # type = request.POST['m_center']
        select_all = request.POST.getlist('select_all')
        purchase_price = request.POST.getlist('purchase_price')
        distributor_price_with_tax = request.POST.getlist('distributor_price_with_tax')
        distributor_price_without_tax = request.POST.getlist('distributor_price_without_tax')
        mrp = request.POST.getlist('mrp')
        bussiness_volume = request.POST.getlist('bussiness_volume')
        point_value = request.POST.getlist('point_value')
        tax_percentage = request.POST.getlist('tax_percentage')
        tax_amount = request.POST.getlist('tax_amount')
        if len(select_all) == 1:
            purchase_price = True
            distributor_price_with_tax = True
            distributor_price_without_tax = True
            mrp = True
            bussiness_volume = True
            point_value = True
            tax_amount = True
            tax_percentage = True
        else:
            if len(purchase_price) == 1:
                purchase_price = True
            if len(distributor_price_with_tax) == 1:
                distributor_price_with_tax = True
            if len(distributor_price_without_tax) == 1:
                distributor_price_without_tax = True
            if len(mrp) == 1:
                mrp = True
            if len(bussiness_volume) == 1:
                bussiness_volume = True
            if len(point_value) == 1:
                point_value = True
            if len(tax_amount) == 1:
                tax_amount = True
            if len(tax_percentage) == 1:
                tax_percentage = True

        if stock_details == 'balance':
            blance_date = request.POST['blance_date']
            o_material_center = request.POST['material_center']
            material_pk = o_material_center
            if not blance_date:
                messages.warning(request, "Please enter Balance Date")
                return redirect('D_inventory_details')
            if not o_material_center:
                messages.warning(request, "Please select a Material center")
                return redirect('D_inventory_details')
            inventry = Distributor_Inventry.objects.filter(created_on=blance_date, material_center__pk=material_pk)
            product = []

            for i in inventry:
                if i.product not in product:
                    for_quantity = inventry.filter(product=i.product)
                    qty = 0
                    batch_quantity = 0
                    for k in for_quantity:
                        qty = qty + k.current_quantity
                        i.product.quantity = qty
                        if k.batch.quantity > batch_quantity:
                            batch_quantity = k.batch.quantity
                            i.product.mrp = k.batch.mrp
                    product.append(i.product)
            params = {
                'purchase_price': purchase_price,
                'distributor_price_with_tax': distributor_price_with_tax,
                'distributor_price_without_tax': distributor_price_without_tax,
                'mrp': mrp,
                'bussiness_volume': bussiness_volume,
                'point_value': point_value,
                'tax_percentage': tax_percentage,
                'inventory': inventry,
                'product': product,
                'title': 'Inventory Details'
            }
            if request.POST['batch'] == 'yes':
                return render(request, 'distributor/blanceDetails-list.html', params)
            if request.POST['batch'] == 'no':
                return render(request, 'distributor/No_blanceDetails-list.html', params)
        elif stock_details == 'detail':
            detail_end_date = request.POST['detail_end_date']
            detail_start_date = request.POST['detail_start_date']
            o_material_center = request.POST['material_center']
            material_pk = o_material_center
            inventry_data = Distributor_Inventry.objects.filter(created_on__range=[detail_start_date, detail_end_date],
                                                                material_center__pk=material_pk)
            inventry = []
            for i in inventry_data:
                if len(inventry) == 0:
                    inventry.append(i)
                else:
                    check = 0
                    for count, j in enumerate(inventry):
                        if i.material_center == j.material_center and i.batch == j.batch:
                            if i not in inventry:
                                if int(j.purchase_price) == 0:
                                    j.purchase_price = i.purchase_price
                                j.current_quantity = i.current_quantity
                                j.quantity_in = int(i.quantity_in) + int(j.quantity_in)
                                j.quantity_out = int(i.quantity_out) + int(j.quantity_out)
                                check = check + 1
                        elif (len(inventry) == (count + 1) and check == 0):
                            inventry.append(i)
            # Purchase.objects.filter()
            product = Product.objects.all().exclude(delete=True)
            product = []
            # if request.POST['batch'] == 'yes':
            for i in inventry:
                if i.product not in product:
                    current_qty = 0
                    batch_quantity = 0
                    opening_qty = 0
                    in_qty = 0
                    out_qty = 0
                    for k in inventry:
                        if k.product == i.product:
                            current_qty = current_qty + k.current_quantity
                            # opening_qty = opening_qty + k.opening_quantity
                            opening_qty = k.opening_quantity
                            in_qty = in_qty + k.quantity_in
                            out_qty = out_qty + k.quantity_out
                            if k.batch.quantity > batch_quantity:
                                batch_quantity = k.batch.quantity
                                i.product.mrp = k.batch.mrp
                    i.product.quantity = current_qty
                    i.product.minimum_purchase_quantity = opening_qty
                    i.product.item_package_quantity = in_qty
                    i.product.weight = out_qty
                    product.append(i.product)
            params = {
                'purchase_price': purchase_price,
                'distributor_price_with_tax': distributor_price_with_tax,
                'distributor_price_without_tax': distributor_price_without_tax,
                'mrp': mrp,
                'bussiness_volume': bussiness_volume,
                'point_value': point_value,
                'tax_amount': tax_amount,
                'tax_percentage': tax_percentage,
                'inventory': inventry,
                'product': product,
                'title': 'Inventory Detail'
            }
            if request.POST['batch'] == 'no':
                return render(request, 'distributor/no_batch_details-list.html', params)
            if request.POST['batch'] == 'yes':
                return render(request, 'distributor/details-list.html', params)
    material = Material_center.get_center_for_user(request.user, advisory_owned='YES')
    today = datetime.now().date()
    today = today.strftime("%Y-%m-%d")
    return render(request, 'distributor/D_inventory_details.html',
                  {'material': material, 'today': today, 'title': 'Inventory Detail'})


def D_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        email = request.POST.get('username')
        try:
            referal = ReferralCode.objects.get(referral_code=email)
            email = referal.user_id.username
        except:
            pass
        try:
            prof = Profile.objects.get(phone_number=email)
            email = prof.user.username
        except:
            pass
        email = email.lower()
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        valuenext = request.POST.get('next')
        # here we are writing code for recaptchar
        clientkey = request.POST['g-recaptcha-response']
        serverkey = '6LeVCKgaAAAAADsn51OcTxu6-wZ_THxWCT7b_GoA'
        captchaData = {
            'secret': serverkey,
            'response': clientkey
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=captchaData)
        response = json.loads(r.text)
        verify = response['success']
        if verify:
            # here we are writing code for recaptchar
            if user is not None and valuenext == '':
                login(request, user)
                if request.session['cart_id']:
                    cart_id = request.session['cart_id']
                    cart_session_item = CartItem.objects.filter(cart_id=cart_id)
                    cart_session_item = recalculate_cart(cart_session_item)
                    # <--!-------------------------------------------nipur code start 9-02-2021--------------------------------------------------------!-->
                    if len(cart_session_item) > 0:
                        cart_user_item = CartItem.objects.filter(user=user).first()
                        cart_user_item = recalculate_cart(cart_user_item)
                        if cart_user_item != None:
                            user_database_cart_id = cart_user_item.cart_id
                        cart_user_item_delete = CartItem.objects.filter(user=user).delete()
                        CartItem.objects.filter(cart_id=cart_id).update(user=user)
                        if cart_user_item != None:
                            CartItem.objects.filter(user=user).update(cart_id=user_database_cart_id)
                            request.session['cart_id'] = user_database_cart_id
                    else:
                        cart_user_item = CartItem.objects.filter(user=user).first()
                        cart_user_item = recalculate_cart(cart_user_item)
                        if cart_user_item != None:
                            request.session['cart_id'] = cart_user_item.cart_id
                else:
                    cart_id = CartItem.objects.filter(user=request.user).first()
                    cart_id = recalculate_cart(cart_id)
                    for i in cart_id:
                        request.session['i.cart_id'] = i.cart_id
                context = {'valuenext': valuenext}
                if request.user.profile.distributor:
                    messages.success(
                        request, "Welcome! You've been signed in"
                    )
                else:
                    messages.warning(
                        request, "You are not a Distributor"
                    )
                # return render(request, 'base.html', context)
                return redirect('distributor_pending_purchase')
            elif user is not None and valuenext != '':
                login(request, user)
                if request.session['cart_id']:
                    cart_id = request.session['cart_id']
                    cart_session_item = CartItem.objects.filter(cart_id=cart_id)
                    cart_session_item = recalculate_cart(cart_session_item)
                    # <--!-------------------------------------------nipur code start 9-02-2021--------------------------------------------------------!-->
                    if len(cart_session_item) > 0:
                        # < ------------------------------------------ this is my new code 20 feb -------------------------------->

                        cart_user_item = CartItem.objects.filter(user=user).first()
                        cart_user_item = recalculate_cart(cart_user_item)
                        if cart_user_item != None:
                            user_database_cart_id = cart_user_item.cart_id
                        cart_user_item_delete = CartItem.objects.filter(user=user).delete()
                        CartItem.objects.filter(cart_id=cart_id).update(user=user)

                        if cart_user_item != None:
                            CartItem.objects.filter(user=user).update(cart_id=user_database_cart_id)
                            request.session['cart_id'] = user_database_cart_id
                    else:
                        cart_user_item = CartItem.objects.filter(user=user).first()
                        if cart_user_item != None:
                            request.session['cart_id'] = cart_user_item.cart_id
                else:
                    cart_id = CartItem.objects.filter(user=request.user).first()
                    for i in cart_id:
                        request.session['i.cart_id'] = i.cart_id

                messages.success(request, "You have successfully logged in")
                valuenext = valuenext.strip('/')
                context = {'valuenext': valuenext}
                return redirect('checkout')
            else:
                messages.warning(request, "Wrong Credentials")
                return redirect('mlm_admin_login')
        else:
            pass
    else:
        return render(request, 'distributor/login.html')


@csrf_exempt
def edit_saleField(request):
    cnt_multiple_product = request.POST['cnt_multiple_product']
    # <----------------------------------------------------------------------------------------------------------start code for product ------------------------------------>

    today = datetime.now().date()
    products = Distributor_Inventry.objects.filter(created_on=today, current_quantity__gt=0).values_list('product')
    products = set(products)
    product = []
    for i in products:
        for j in i:
            product.append(j)

    # <----------------------------------------------------------------------------------------------------------end code for product ------------------------------------>

    items = Product.objects.filter(pk__in=product).exclude(delete=True)
    batches = Batch.objects.all().exclude(delete=True)
    params = {
        'items': items,
        'batches': batches,
        'cnt_multiple_product': cnt_multiple_product
    }
    return render(request, 'distributor/edit_saleField.html', params)


@user_passes_test(is_distributor, login_url='D_login')
def D_purchase_downlaod(request):
    if request.method == 'POST':
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        response = HttpResponse(content_type='application/ms-excel')
        response['content-Disposition'] = 'attachment; filename = User Purchase' + str(datetime.now()) + '.xls'
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Expenses')
        row_num = 0
        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        columns = ['Bill Number', 'material_center_to', 'material_center_from', 'advisor_distributor_name',
                   'party_name',
                   'grand_total', 'Billing Date', 'Created On', 'Narration', 'Product ID', 'item', 'Category',
                   'Variant', 'DV', 'BV', 'PV', 'batch', 'Batch Manufacture Date',
                   'Batch date_of_expiry', 'quantity', 'distributor_price', 'cgst', 'sgst', 'igst', 'vat',
                   'total_amount', 'Sale Type']
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        font_style = xlwt.XFStyle()
        rows = Sale_itemDetails.objects.filter(sale__created_on__gte=from_date, sale__created_on__lte=to_date,
                                               sale__delete=False, sale__advisor_distributor_name=request.user,
                                               sale__accept=True).values_list('sale__pk',
                                                                              'sale__material_center_to__mc_name',
                                                                              'sale__material_center_from__mc_name',
                                                                              'sale__advisor_distributor_name__email',
                                                                              'sale__party_name', 'sale__grand_total',
                                                                              'sale__date', 'sale__created_on',
                                                                              'sale__narration', 'item__pk',
                                                                              'item__product_name',
                                                                              'item__category__cat_name',
                                                                              'item__product_variant__variant_tag__product_name',
                                                                              'item__distributor_price',
                                                                              'item__business_value',
                                                                              'item__point_value',
                                                                              'batch__batch_name',
                                                                              'batch__date_of_manufacture',
                                                                              'batch__date_of_expiry', 'quantity',
                                                                              'distributor_price', 'cgst', 'sgst',
                                                                              'igst', 'vat', 'total_amount',
                                                                              'sale__sale_type')
        for row in rows:
            row_num += 1
            counting_sale_type = 0
            for col_num in range(len(row)):
                colmn = str(row[col_num])
                counting_sale_type += 1
                if counting_sale_type == 27:
                    if colmn == '0':
                        colmn = 'With in State'
                    elif colmn == '1':
                        colmn = 'Inter State'
                ws.write(row_num, col_num, colmn, font_style)
        wb.save(response)
        return response
    return render(request, 'distributor/download_purchase.html')


@user_passes_test(is_distributor, login_url='D_login')
def D_loyalty_sale_download(request):
    if request.method == 'POST':
        response = D_sale_downlaod(request, loyalty=True)
        return response
    return render(request, 'distributor/download_sale.html', {'loyalty':True})


@user_passes_test(is_distributor, login_url='D_login')
def D_sale_downlaod(request, loyalty=False):
    if request.method == 'POST':
        to_date = request.POST.get('to_date')
        from_date = request.POST.get('from_date')
        response = HttpResponse(content_type='application/ms-excel')
        response['content-Disposition'] = 'attachment; filename = Sale' + str(datetime.now()) + '.xls'
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Expenses')
        row_num = 0
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        columns = ['Bill Number', 'material_center', 'advisor_distributor_name', 'party_name',
                   'grand_total', 'Billing Date', 'Created On', 'Narration', 'Product ID', 'item', 'Category',
                   'Variant', 'DV', 'BV', 'PV', 'batch', 'Batch Manufacture Date',
                   'Batch date_of_expiry', 'quantity', 'distributor_price', 'cgst', 'sgst', 'igst', 'vat',
                   'total_amount', 'Sale Type', 'Is Loyalty']
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)
        font_style = xlwt.XFStyle()
        rows = Distributor_Sale_itemDetails.objects.filter(sale__created_on__gte=from_date,
                                                           sale__created_on__lte=to_date,
                                                           sale__delete=False,
                                                           sale__order__loyalty_order = loyalty,
                                                           sale__sale_user_id=request.user).values_list('sale__pk',
                                                                                                        'sale__material_center__mc_name',
                                                                                                        'sale__advisor_distributor_name__email',
                                                                                                        'sale__party_name',
                                                                                                        'sale__grand_total',
                                                                                                        'sale__date',
                                                                                                        'sale__created_on',
                                                                                                        'sale__narration',
                                                                                                        'item__pk',
                                                                                                        'item__product_name',
                                                                                                        'item__category__cat_name',
                                                                                                        'item__product_variant__variant_tag__product_name',
                                                                                                        'item__distributor_price',
                                                                                                        'item__business_value',
                                                                                                        'item__point_value',
                                                                                                        'batch__batch_name',
                                                                                                        'batch__date_of_manufacture',
                                                                                                        'batch__date_of_expiry',
                                                                                                        'quantity',
                                                                                                        'distributor_price',
                                                                                                        'cgst', 'sgst',
                                                                                                        'igst', 'vat',
                                                                                                        'total_amount',
                                                                                                        'sale__sale_type',
                                                                                                        'sale__order__loyalty_order')
        for row in rows:
            row_num += 1
            counting_sale_type = 0
            for col_num in range(len(row)):
                colmn = str(row[col_num])
                counting_sale_type += 1
                if counting_sale_type == 26:
                    if colmn == '0':
                        colmn = 'With in State'
                    elif colmn == '1':
                        colmn = 'Inter State'
                ws.write(row_num, col_num, colmn, font_style)
        wb.save(response)
        return response
    return render(request, 'distributor/download_sale.html')


def download_invoice(request):
    return render(request, 'distributor/download_sale.html')


# Creating our view, it is a class based view
class GeneratePDF(View):
    def get(self, request, *args, **kwargs):
        template = get_template('distributor/invoice1.html')
        datas = Distributor_Sale.objects.filter(pk=17)
        for i in datas:
            context = {
                'datas': datas,
            }
        html = template.render(context)
        pdf = render_to_pdf('distributor/invoice1.html')
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "Invoice_%s.pdf" % ("12341231")
            content = "inline; filename='%s'" % (filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename='%s'" % (filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")


def quantity_validate(max_quantity, ac_quantity):
    for sn, i in enumerate(ac_quantity):
        m_quantity = int(max_quantity[sn])
        try:
            quanitty = int(i)
        except:
            quanitty = 0
        if quanitty > m_quantity:
            return False


def users_autocomplete(request):
    userKey = request.POST['user_keys']
    ProfileModels = Profile.objects.filter(
        Q(phone_number__icontains=userKey) |
        Q(user__username__icontains=userKey) |
        Q(user__referralcode__referral_code__icontains=userKey)) \
        .values('user__username', 'email', 'phone_number', 'user__referralcode__referral_code', 'first_name',
                'last_name')
    listCompress = [{'key': item['email'],
                     'value': item['user__username'] + ' - ' + item['phone_number'] +
                              ' - ' + item['user__referralcode__referral_code'],
                     'first_name': item['first_name'],
                     'last_name': item['last_name']}
                    if item['phone_number'] else {'key': item['email'], 'value': item['user__username']}
                    for item in ProfileModels]

    dump = json.dumps(listCompress)
    return HttpResponse(dump, content_type='application/json')



