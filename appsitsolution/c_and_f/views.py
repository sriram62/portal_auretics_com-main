import json

import requests
import xlwt
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from accounts.models import Profile, ReferralCode
from c_and_f.utils import get_order_list_for_cnf_admin
from distributor.views import quantity_validate
from mlm_admin.common_code import *
from mlm_admin.forms import Orderform, AddressForm
# Create your views here.
from mlm_admin.sr_api_call import OrderMaintain
from pyjama import j
from mlm_admin.new_inventory_calculation import calculate_mlm_inventory
from mlm_admin.recalculate import recalculate_everything_mlm
import traceback


def is_c_and_f_admin(user):
    try:
        return user.is_authenticated and user.profile.c_and_f_admin is not False
    except Profile.DoesNotExist:
        return False


@user_passes_test(is_c_and_f_admin, login_url='D_login')
def cnf_purchase_pending(request):
    today = datetime.now().date()
    data = Sale.objects.filter(advisor_cnf_name=request.user, delete=False, accept=False).order_by('-date')
    print(data)
    return render(request, 'c_and_f/pending_purchase_list.html',
                  {'data': data, 'title': 'Pending Purchase List', 'today': today})


#
@user_passes_test(is_c_and_f_admin, login_url='D_login')
def cnf_purchase(request):
    today = datetime.now().date()
    cnf_material_center = Material_center.get_center_for_user(request.user, company_depot='YES')
    data = Sale.objects.filter(material_center_to=cnf_material_center, delete=False, accept=True).order_by('-date')
    print(data)
    return render(request, 'c_and_f/purchase_list.html', {'data': data, 'title': 'Purchase List', 'today': today})


#
# # def distributor_sale(request):
# #     today = datetime.now().date()
# #     data = Sale.objects.filter(sale_user_id = request.user).order_by('-date')
# #     print(data)
# #     return render(request, 'c_and_f/sale_list.html', {'data': data,'title':'Distributor Sale List','today':today})
# # return HttpResponse('<h1>data has been coming here</h1>')
# # return render(request,'c_and_f/purchase_list.html')
#
@user_passes_test(is_c_and_f_admin, login_url='D_login')
def view_cnf_pending_purchase(request, myid):
    today = datetime.now().date()
    if request.method == 'POST':
        cnf_purchase = Sale.objects.get(pk=myid)
        Sale.objects.filter(pk=myid).update(accept=True, accepted_date= today)
        purchase_item_list = Sale_itemDetails.objects.filter(sale=cnf_purchase)
        material = Material_center.get_center_for_user(request.user, company_depot='YES')
        purchase_record = Purchase.objects.create(
            purchase_user_id=request.user,
            material_name=material,
            date=cnf_purchase.date,
            narration=cnf_purchase.narration,
            purchase_type=cnf_purchase.sale_type,
            grand_total=cnf_purchase.grand_total,
            party_name=cnf_purchase.party_name
        )
        for i in purchase_item_list:
            product = i.item
            batch1 = i.batch
            material = material
            item_details.objects.create(
                item=i.item,
                purchase=purchase_record,
                batch=i.batch,
                quantity=i.quantity,
                price=i.distributor_price,
                cgst=i.cgst,
                sgst=i.sgst,
                igst=i.igst,
                vat=i.vat,
                total_amount=i.total_amount
            )
            try:
                addPurchaseCalculateTodayInventry(
                    product=product,
                    batch=batch1,
                    material_center=material,
                    quantity=i.quantity,
                    price= batch1.mrp
                )
                # today = datetime.now().date()
                # cnf_inventory_update = Inventry.objects.get(product=product, batch=batch1,
                #                                             material_center=material,
                #                                             created_on=today)
                # cnf_inventory_update_current_quantity = int(cnf_inventory_update.current_quantity) + int(i.quantity)
                # cnf_inventory_update_quantity_in = int(cnf_inventory_update.quantity_in) + int(i.quantity)
                # Inventry.objects.filter(product=product, batch=batch1, material_center=material,
                #                         created_on=today).update(
                #     current_quantity=cnf_inventory_update_current_quantity,
                #     quantity_in=cnf_inventory_update_quantity_in, purchase_price=batch1.mrp)
            except:
                try:
                    addPurchaseUpdateInventry(
                        product=product,
                        batch=batch1,
                        material_center=material,
                        quantity=i.quantity,
                        price= batch1.mrp
                    )
                    # CNF_inventory_update = Inventry.objects.filter(product=product, batch=batch1,
                    #                                                material_center=material).latest(
                    #     'created_on')
                    # CNF_current_quantity = int(CNF_inventory_update.current_quantity) + int(i.quantity)
                    # CNF_inventory = Inventry(product=product, batch=batch1, material_center=material,
                    #                          opening_quantity=CNF_inventory_update.opening_quantity,
                    #                          current_quantity=CNF_current_quantity,
                    #                          quantity_in=i.quantity, purchase_price=batch1.mrp)
                    # CNF_inventory.save()
                except:
                    addPurchageAddInventry(
                        product=product,
                        batch=batch1,
                        material_center=material,
                        quantity=i.quantity,
                        price= batch1.mrp
                    )
                    # CNF_inventory = Inventry(product=product, batch=batch1, material_center=material,
                    #                          opening_quantity=0, current_quantity=i.quantity,
                    #                          quantity_in=i.quantity, purchase_price=batch1.mrp)
                    # CNF_inventory.save()
                # here add code for inventry start here 20-03-2021
            # inventory code end
        # <----------------------------------------------------------------------------here we are creating inventory end code------------------------------------------------------------------------------------------------------>
        return redirect('cnf_purchase')
    sale_data = Sale.objects.get(pk=myid, accept=False)
    data = Sale_itemDetails.objects.filter(sale=sale_data)
    if sale_data.advisor_cnf_name != request.user:
        messages.warning(request, 'Sorry you are not authorize to check these records!')
        return redirect('cnf_pending_purchase')
    params = {
        'sale_data': sale_data,
        'data': data,
        'title': 'C&F  purchase View'
    }
    return render(request, 'c_and_f/view_pending_purchase.html', params)


@user_passes_test(is_c_and_f_admin, login_url='D_login')
def view_cnf_purchase(request, myid):
    sale_data = Sale.objects.get(pk=myid, accept=True)
    data = Sale_itemDetails.objects.filter(sale=sale_data)
    if sale_data.advisor_cnf_name != request.user:
        messages.warning(request, 'Sorry you are not authorize to check these records!')
        return redirect('distributor_purchase')
    params = {
        'sale_data': sale_data,
        'data': data,
        'title': 'Distributor  purchase View'
    }
    return render(request, 'c_and_f/view_purchase.html', params)


def product_detail(request):
    product_id = request.GET['product_id']
    batch_id = request.GET['batch_id']
    material_center = request.GET['material_center']
    material = Material_center.objects.get(pk=material_center)
    # sale_type= 0 for with in state(cgst+sgst) and sale_type = 1 for inter_state(igst)
    sale_type = request.GET['sale_type']
    product = Product.objects.get(pk=product_id)
    batch = Batch.objects.get(pk=batch_id)
    # <-- here we are geting quantity from the inventry code start here -->
    try:
        today = datetime.now().date()
        D_inventory_update = Inventry.objects.get(product=product, batch=batch, material_center=material,
                                                  created_on=today)
        D_inventory_update_current_quantity = int(D_inventory_update.current_quantity)
        batch_quantity = D_inventory_update_current_quantity
    except:
        try:
            D_inventory_update = Inventry.objects.filter(product=product, batch=batch,
                                                         material_center=material).latest('created_on')
            D_inventory = Inventry(product=product, batch=batch, material_center=material,
                                   opening_quantity=D_inventory_update.opening_quantity,
                                   current_quantity=D_inventory_update.current_quantity,
                                   quantity_in=0, purchase_price=0)
            batch_quantity = D_inventory_update.current_quantity
            D_inventory.save()
        except:
            D_inventory = Inventry(product=product, batch=batch, material_center=material,
                                   opening_quantity=0, current_quantity=0,
                                   quantity_in=0, purchase_price=0)
            batch_quantity = 0
            D_inventory.save()

    mrp = batch.mrp

    cgst = product.cgst
    sgst = product.sgst
    igst = product.igst
    distributor_price = product.distributor_price
    vat = product.vat
    if cgst == None:
        cgst = 0
    if sgst == None:
        sgst = 0
    if igst == None:
        igst = 0
    if distributor_price == None:
        distributor_price = 0
    if vat == None:
        vat = 0

    if sale_type == '1':
        distributor_price = mrp / ((100 + igst) / 100) / ((100 + distributor_price) / 100)
        igst = distributor_price * (igst / 100)
        cgst = 0
        sgst = 0
        vat = distributor_price * (vat / 100)
    else:
        distributor_price = mrp / ((100 + (sgst + cgst)) / 100) / ((100 + distributor_price) / 100)
        cgst = distributor_price * (cgst / 100)
        sgst = distributor_price * (sgst / 100)
        vat = distributor_price * (vat / 100)
        igst = 0
    distributor_price = round(distributor_price, 2)
    cgst = round(cgst, 2)
    sgst = round(sgst, 2)
    vat = round(vat, 2)
    igst = round(igst, 2)
    params = {
        'distributor_price': distributor_price,
        'cgst': cgst,
        'sgst': sgst,
        'igst': igst,
        'vat': vat,
        'pv': batch.pv,
        'bv': batch.bv,
        'batch_quantity': batch_quantity
    }
    return JsonResponse(status=200, data=params)


def CNF_login(request):
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
                print(request.session['cart_id'])
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
                        cart_user_item = recalculate_cart(cart_user_item)
                        if cart_user_item != None:
                            request.session['cart_id'] = cart_user_item.cart_id
                else:
                    cart_id = CartItem.objects.filter(user=request.user).first()
                    cart_id = recalculate_cart(cart_id)
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
        return render(request, 'c_and_f/login.html')


@user_passes_test(is_c_and_f_admin, login_url='D_login')
def CNF_purchase_downlaod(request):
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

        columns = ['Bill Number', 'material_center_to', 'material_center_from', 'advisor_cnf_name',
                   'party_name',
                   'grand_total', 'Billing Date', 'Created On', 'Narration', 'Product ID', 'item', 'Category',
                   'Variant', 'DV', 'BV', 'PV', 'batch', 'Batch Manufacture Date',
                   'Batch date_of_expiry', 'quantity', 'distributor_price', 'cgst', 'sgst', 'igst', 'vat',
                   'total_amount', 'Sale Type']
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        font_style = xlwt.XFStyle()
        # print(to_date)
        # print(from_date)
        rows = Sale_itemDetails.objects.filter(sale__created_on__gte=from_date, sale__created_on__lte=to_date,
                                               sale__delete=False, sale__advisor_cnf_name=request.user,
                                               sale__accept=True).values_list('sale__pk',
                                                                              'sale__material_center_to__mc_name',
                                                                              'sale__material_center_from__mc_name',
                                                                              'sale__advisor_cnf_name__email',
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
    return render(request,
                  'c_and_f/download_purchase.html')


@user_passes_test(is_c_and_f_admin, login_url='mlm_admin_login')
def add_sale_from_cnf(request):
    today = datetime.now().date()
    if request.method == "POST":
        # try:
        date = datetime.now().date() #request.POST['date']
        mc_center_to = request.POST['mc_center_to']
        mc_center_from = Material_center.objects.get(advisor_registration_number=request.user).pk #request.POST['mc_center_from']
        narration = request.POST['narration']
        party_name = request.POST['party_name']
        sale_type = request.POST['sale_type']
        grand_total = 0 #request.POST['grand_total']
        user = request.POST['user']
        quaantity_item = request.POST.getlist('quaantity_item')
        check_quantity = request.POST.getlist('check_quantity')
        result = quantity_validate(check_quantity, quaantity_item)
        if result == False:
            messages.success(request, "Bad Request (Quantity entered is greater than maximum allowed quantity).")
            return redirect('add_sale')
        item = request.POST.getlist('item')
        batch = request.POST.getlist('batch')

        # AG :: Validation to find if duplicate batch items exists
        if not len(batch) == len(set(batch)):
            messages.success(request,
                             "Order Validation Error: Duplicate Batch Found. Please Try Again or Contact Admin")
            return redirect('distributor_sale_list')

        totalamount_item = request.POST.getlist('totalamount_item')
        try:
            material_center_to = Material_center.objects.get(pk=mc_center_to)
            material_center_from = Material_center.objects.get(pk=mc_center_from)
            user = material_center_to.advisor_registration_number
            data = Sale(sale_user_id=request.user, material_center_to=material_center_to,
                        material_center_from=material_center_from, date=date,
                        narration=narration, advisor_distributor_name=user,
                        party_name=party_name,
                        sale_type=sale_type,
                        grand_total=grand_total,
                        sale_to=Sale.SALE_TO_DISTRIBUTOR)
            data.save()
            sale = data
            try:
                for i, k in enumerate(totalamount_item):
                    quantity = quaantity_item[i]
                    product = item[i]
                    product = Product.objects.get(pk=product)
                    batch1 = batch[i]
                    batch1 = Batch.objects.get(pk=batch1)
                    mrp = batch1.mrp or 0
                    cgst = product.cgst or 0
                    sgst = product.sgst or 0
                    igst = product.igst or 0
                    distributor_price = product.distributor_price or 0

                    distributor_price = mrp / ((100 + distributor_price) / 100)
                    igst = 0
                    cgst = 0
                    sgst = 0
                    vat = 0

                    distributor_price = round(distributor_price, 2)
                    cgst = round(cgst, 2)
                    sgst = round(sgst, 2)
                    vat = round(vat, 2)
                    igst = round(igst, 2)
                    total_amount = int(quantity) * (distributor_price + cgst + sgst + igst)
                    total_amount = round(total_amount, 2)
                    # inventory code start
                    product_quantity_update = int(product.quantity) - int(quantity)
                    p_quantity_update = Product.objects.filter(pk=product.pk).update(quantity=product_quantity_update)
                    batch_quantity = batch1.quantity
                    update_batch_quantity = int(batch_quantity) - int(quantity)
                    Batch.objects.filter(pk=batch1.pk).update(quantity=update_batch_quantity)
                    try:
                        batch_qty = Inventry.objects.get(created_on=today, batch=batch1,
                                                                     material_center=mc_center_from)
                    except ObjectDoesNotExist:
                        raise Exception(
                            f'Distributor_Batch does not exist for batch <b> {batch1} </b>, and for material_center <b> {material_center} </b> please contact to the administrator.')

                    # AG :: Re-calculating Distributor's Quantity First
                    calculate_mlm_inventory(product=product,
                                            batch=batch1,
                                            material_center=material_center_from,
                                            quantity=0
                                            )

                    # AG :: Checking whether stock of this item exist in our system.
                    available_quantity = Inventry.objects.filter(batch=batch1,
                                                                 material_center=mc_center_from).latest(
                        'pk').current_quantity
                    if not int(available_quantity) >= int(quantity):
                        messages.success(request,
                                         "Order Validation Error. Insufficient Quantity. Please Try Again or Contact Admin")
                        return redirect('distributor_sale_list')

                    try:
                        calculateTodayInventry(
                            product=product, 
                            batch= batch1,
                            quantity= quantity,
                            material_center= material_center_from
                        )
                    except Exception as e:
                        messages.error(request, "something went wrong " + str(e))
                        return redirect('cnf_sale_list')


                    saledata = Sale_itemDetails(item=product,
                                                sale=sale,
                                                batch=batch1,
                                                quantity=quantity,
                                                distributor_price=distributor_price,
                                                cgst=cgst, sgst=sgst, igst=igst, vat=vat,
                                                total_amount=total_amount, )
                    saledata.save()

                # updating pv, bv and grand total from the backend
                # saleId = Sale.objects.get(pk=data.id)
                # grand_pv = sum([li.pv for li in saleId.sale_itemdetails_set.all()])
                # grand_bv = sum([li.bv for li in saleId.sale_itemdetails_set.all()])
                # grand_total = sum([li.total_amount for li in saleId.sale_itemdetails_set.all()])
                # Sale.objects.filter(pk=data.id).update(grand_pv=grand_pv,
                #                                        grand_bv=grand_bv,
                #                                        grand_total=grand_total)

                messages.success(request, "Record added successfully!")
                return redirect('cnf_sale_list')
            except Exception as e:
                messages.success(request, "Something went wrong " + str(e))
                messages.warning(request, "Trace: " + str(traceback.format_exc()))
                return redirect('cnf_sale_list')

        except Exception as e:
            messages.error(request, "something went wrong " + str(e))
            messages.warning(request, "Trace: " + str(traceback.format_exc()))
            return redirect('cnf_sale_list')

        recalculate_everything_mlm(request, myid=sale.id, post_bill=True, check=False, mlm_admin=False, cf=True)
        return redirect('cnf_view_sale', myid=sale.id)

    # except:
    #     messages.warning(request, "You Try to add wrong data please check and try again")
    material_center_from = Material_center.objects.filter(company_depot='YES',
                                                          advisor_registration_number=request.user).exclude(delete=True)
    states = []
    for mc in material_center_from:
        for state in mc.associated_states.all():
            states.append(state)
    material_center_to = Material_center.objects.filter(advisory_owned='YES', state__in=[s.state_name for s in states]).exclude(
        delete=True)
    batches = Batch.objects.all().exclude(delete=True)
    # items = Product.objects.all().exclude(delete=True)
    material = Material_center.objects.get(advisor_registration_number=request.user)
    if material:
        products = Inventry.objects.filter(created_on=today, current_quantity__gt=0,
                                                       material_center=material).values_list('product')
    else:
        products = Inventry.objects.filter(created_on=today, current_quantity__gt=0).values_list('product')
    # products = Distributor_Inventry.objects.filter(current_quantity__gte = 0).values_list('product')
    products = set(products)
    product = []
    for i in products:
        for j in i:
            product.append(j)

    items = Product.objects.filter(pk__in=product).exclude(delete=True)
    users = User.objects.all()
    myDate = datetime.now()
    formatedDate = myDate.strftime("%Y-%m-%d")
    params = {
        'material_center_to': material_center_to,
        'material_center_from': material_center_from,
        'sale_to_options': ['Distributor', 'C&F'],
        'batches': batches,
        'items': items,
        'users': users,
        'prod_id': 1,
        'date': formatedDate,
        'title': 'Add Sale'
    }
    return render(request, 'c_and_f/add_cnf_sale.html', params)


@user_passes_test(is_c_and_f_admin, login_url='mlm_admin_login')
# @allowed_users(allowed_roles=['inventory_management',['1','2','3','4']])
def cnf_inventory_details(request):
    print(request.method)
    o_material_center = Material_center.objects.filter(advisor_registration_number=request.user,
                                                       company_depot='YES').first()
    if request.method == 'POST':
        stock_details = request.POST['stock_details']
        select_all = request.POST.getlist('select_all')
        purchase_price = request.POST.getlist('purchase_price')
        distributor_price_with_tax = request.POST.getlist('distributor_price_with_tax')
        distributor_price_without_tax = request.POST.getlist('distributor_price_without_tax')
        mrp = request.POST.getlist('mrp')
        bussiness_volume = request.POST.getlist('bussiness_volume')
        point_value = request.POST.getlist('point_value')
        tax_percentage = request.POST.getlist('tax_percentage')
        tax_amount = request.POST.getlist('tax_amount')
        stock = request.POST['stock']
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
            material_pk = o_material_center.pk
            if stock == 'yes':
                inventry = Inventry.objects.filter(created_on=blance_date, material_center__pk=material_pk)
            elif stock == 'no':
                inventry = Inventry.objects.filter(created_on=blance_date, material_center__pk=material_pk,
                                                   current_quantity__gt=0)
            # Purchase.objects.filter()
            material = Material_center.objects.all().exclude(delete=True)
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
                'title': 'Inventory Details',
                'page': 'cnf'
                # 'product1': product1,
                # 'material':material1
            }
            # print('material---->', material)
            if request.POST['batch'] == 'yes':
                return render(request, 'mlm_admin/blanceDetails-list.html', params)
            if request.POST['batch'] == 'no':
                return render(request, 'mlm_admin/No_blanceDetails-list.html', params)
        elif stock_details == 'detail':
            detail_end_date = request.POST['detail_end_date']
            detail_start_date = request.POST['detail_start_date']
            print('stock_details--->', stock_details)

            # here
            material_pk = o_material_center.pk
            inventry_data = Inventry.objects.filter(created_on__range=[detail_start_date, detail_end_date],
                                                    material_center__pk=material_pk)
            if stock == 'no':
                today = datetime.now().date()
                check_inventry = Inventry.objects.filter(created_on=today, current_quantity=0)
                for i in check_inventry:
                    inventry_data = inventry_data.exclude(product=i.product, batch=i.batch,
                                                          material_center=i.material_center)
            inventry = []
            for i in inventry_data:
                if len(inventry) == 0:
                    inventry.append(i)
                else:
                    check = 0
                    # for count, value in enumerate(values):
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
            print('here this-------------------------------', inventry)
            # Purchase.objects.filter()

            product = Product.objects.all().exclude(delete=True)
            product = []
            print('inventry--->', inventry)
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
                    print('current_qty----->', current_qty, '----------------product------------>', i.product)
                    i.product.quantity = current_qty
                    i.product.minimum_purchase_quantity = opening_qty
                    i.product.item_package_quantity = in_qty
                    i.product.weight = out_qty
                    product.append(i.product)

            print(product, 'here we are geting the name  of the product')
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
                'title': 'Inventory Detail',
                'page': 'cnf'
            }
            if request.POST['batch'] == 'no':
                return render(request, 'mlm_admin/no_batch_details-list.html', params)
            # print('material---->', material)
            if request.POST['batch'] == 'yes':
                return render(request, 'mlm_admin/details-list.html', params)
        # print(material)
    material = Material_center.objects.filter(company_depot='YES').exclude(delete=True)
    # material = Material_center.objects.filter(company_depot='YES').exclude(delete=True)
    today = datetime.now().date()
    today = today.strftime("%Y-%m-%d")
    return render(request, 'c_and_f/inventory_details.html',
                  {'material': material, 'today': today, 'title': 'Inventory Detail', 'page': 'cnf'})


@user_passes_test(is_c_and_f_admin, login_url='mlm_admin_login')
def cnf_sale_list(request):
    material_center = Material_center.get_center_for_user(request.user, company_depot='YES')
    today = datetime.now().date()
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        data = Sale.objects.filter(Q(pk__icontains=q) | Q(material_center_to__mc_name__icontains=q) | Q(
            material_center_from__mc_name__icontains=q) | Q(created_on__icontains=q) | Q(party_name__icontains=q)
                                   | Q(grand_total__icontains=q), delete=False, material_center_from=material_center).order_by('-id')
    else:
        q = ''
        data = Sale.objects.filter(material_center_from=material_center, delete=False).order_by('-id')
    paginator = Paginator(data, 10)
    print(paginator, 'paginator')
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'c_and_f/sale_list.html',
                  {'data': page_obj, 'title': 'Sale List', 'q': q, 'today': today, 'page': 'cnf'})
    # data = Sale.objects.filter(delete = False)
    # print(today)
    # return render(request, 'mlm_admin/sale_list.html', {'data': data,'title':'Sale List','today':today})


@user_passes_test(is_c_and_f_admin, login_url='mlm_admin_login')
def cnf_view_sale(request, myid):
    material_center_to = Material_center.objects.filter(company_depot='NO').exclude(delete=True)
    material_center_from = Material_center.objects.filter(company_depot='YES').exclude(delete=True)
    material_c = Material_center.objects.all().exclude(delete=True)
    batches = Batch.objects.all().exclude(delete=True)
    items = Product.objects.all().exclude(delete=True)
    users = User.objects.all()
    sale_data = Sale.objects.get(pk=myid)
    data = Sale_itemDetails.objects.filter(sale=sale_data)
    params = {
        'material_center_to': material_center_to,
        'material_center_from': material_center_from,
        'material_c': material_c,
        'batches': batches,
        'items': items,
        'users': users,
        'sale_data': sale_data,
        'data': data,
        'page': 'cnf',
        'title': 'View Sale'
    }
    return render(request, 'mlm_admin/view_sale.html', params)


@user_passes_test(is_c_and_f_admin, login_url='mlm_admin_login')
def cnf_sale_list_pending(request):
    material_center = Material_center.get_center_for_user(request.user)
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        sales = Sale.objects.filter(
            Q(created_on__icontains=q) | Q(party_name__icontains=q) | Q(material_center_to__mc_name__icontains=q) | Q(
                material_center_from__mc_name__icontains=q) | Q(grand_total__contains=q), delete=False,
            accept=False).order_by('id')
    else:
        q = ''
        sales = Sale.objects.filter(material_center_from=material_center, delete=False, accept=False).order_by('id')
    paginator = Paginator(sales, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'c_and_f/pending_sale.html',
                  {'sales': page_obj, 'title': 'Pending sale', 'q': q, 'page': 'cnf'})


@user_passes_test(is_c_and_f_admin, login_url='mlm_admin_login')
def cnf_sale_download(request):
    material_center = Material_center.get_center_for_user(request.user, company_depot='YES')
    if request.method == 'POST':
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        response = HttpResponse(content_type='application/ms-excel')
        response['content-Disposition'] = 'attachment; filename = Sale' + str(datetime.now()) + '.xls'
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
        # print(to_date)
        # print(from_date)
        rows = Sale_itemDetails.objects.filter(sale__material_center_from=material_center,
                                               sale__created_on__gte=from_date, sale__created_on__lte=to_date,
                                               sale__delete=False).values_list('sale__pk',
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
        print(rows, 'here we are geting the data that is going to print in excel sheet')
        print(len(rows), 'here we are geting the length of data')
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
    return render(request, 'c_and_f/download_sale.html')


@user_passes_test(is_c_and_f_admin, login_url='mlm_admin_login')
def cnf_view_sale(request, myid):
    material_center_to = Material_center.objects.filter(company_depot='NO').exclude(delete=True)
    material_center_from = Material_center.objects.filter(company_depot='YES').exclude(delete=True)
    material_c = Material_center.objects.all().exclude(delete=True)
    batches = Batch.objects.all().exclude(delete=True)
    items = Product.objects.all().exclude(delete=True)
    users = User.objects.all()
    sale_data = Sale.objects.get(pk=myid)
    data = Sale_itemDetails.objects.filter(sale=sale_data)
    params = {
        'material_center_to': material_center_to,
        'material_center_from': material_center_from,
        'material_c': material_c,
        'batches': batches,
        'items': items,
        'users': users,
        'sale_data': sale_data,
        'data': data,
        'page': 'cnf',
        'title': 'View Sale',
        'page': 'cnf'
    }
    return render(request, 'mlm_admin/view_sale.html', params)


@user_passes_test(is_c_and_f_admin, login_url='mlm_admin_login')
def order_list(request):
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        # d=q.date()
        # print(d,'llllllllllllllllllllllllllllll')
        data = get_order_list_for_cnf_admin(request.user).filter(
            Q(name__icontains=q) | Q(order_id1__icontains=q) | Q(date__icontains=q) | Q(grand_total__contains=q),
            status=None, delete=False, paid=True).order_by('id')
    else:
        q = ''
        data = get_order_list_for_cnf_admin(request.user).filter(status=None, delete=False, paid=True).order_by('id')
    paginator = Paginator(data, 10)
    print(paginator, 'paginator')
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'mlm_admin/order-list.html',
                  {'data': page_obj, 'title': 'Order List', 'q': q, 'page': 'cnf'})


@user_passes_test(is_c_and_f_admin, login_url='mlm_admin_login')
def order_downlaod(request):
    if request.method == 'POST':
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        today = datetime.now()
        if str(today.date()) == to_date:
            to_date = today

        response = HttpResponse(content_type='application/ms-excel')
        response['content-Disposition'] = 'attachment; filename = Order' + str(datetime.now()) + '.xls'
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Expenses')
        row_num = 0
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        mc = Material_center.get_center_for_user(request.user, company_depot='YES')
        columns = ['Bill Number',
                   'grand_total', 'Billing Date', 'Product ID', 'item', 'Category',
                   'Variant', 'DV', 'BV', 'PV', 'batch', 'Batch Manufacture Date',
                   'Batch date_of_expiry', 'cgst', 'sgst', 'igst', 'Price', 'quantity'
                                                                            'total_amount']
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        font_style = xlwt.XFStyle()
        # print(to_date)
        # print(from_date)
        rows = LineItem.objects.filter(order__material_center=mc,
                                       order__date__gte=from_date, order__date__lte=to_date,
                                       order__delete=False).values_list('order__pk',
                                                                        'order__grand_total', 'order__date',
                                                                        'product__pk', 'product__product_name',
                                                                        'product__category__cat_name',
                                                                        'product__product_variant__variant_tag__product_name',
                                                                        'product__distributor_price',
                                                                        'product__business_value',
                                                                        'product__point_value',
                                                                        'batch__batch_name',
                                                                        'batch__date_of_manufacture',
                                                                        'batch__date_of_expiry',
                                                                        'cgst', 'sgst', 'igst', 'price', 'quantity')
        print(rows, 'here we are geting the data that is going to print in excel sheet')
        print(len(rows), 'here we are geting the length of data')
        for row in rows:
            row_num += 1
            counting = 0
            price = 0
            quantity = 0
            for col_num in range(len(row) + 1):
                counting += 1
                if counting < 19:
                    colmn = str(row[col_num])
                if counting == 17:
                    price = float(colmn)
                if counting == 18:
                    quantity = int(colmn)
                if counting == 19:
                    colmn = price * quantity
                ws.write(row_num, col_num, colmn, font_style)
        wb.save(response)
        return response
    return render(request, 'c_and_f/download_order.html')


@user_passes_test(is_c_and_f_admin, login_url='mlm_admin_login')
def transfer_order(request, order_id):
    print("Inside Transfer order")
    if request.method == 'POST':
        if request.POST.get('action') == 'YES':
            frontend_mc = Material_center.get_frontend_mc()
            if frontend_mc:
                Order.objects.filter(pk=order_id).update(material_center=frontend_mc)
        return redirect('cnf-order-list')
    return render(request, 'c_and_f/confirm_transfer.html')


@user_passes_test(is_c_and_f_admin, login_url='mlm_admin_login')
def allorder(request):
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        data = get_order_list_for_cnf_admin(request.user).filter(
            Q(name__icontains=q) | Q(order_id1__icontains=q) | Q(date__icontains=q) | Q(grand_total__contains=q),
            delete=False, paid=True).order_by('id')
    else:
        q = ''
        data = get_order_list_for_cnf_admin(request.user).filter(delete=False, paid=True).order_by('id')
    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'c_and_f/Allorder-list.html',
                  {'data': page_obj, 'title': 'All Order', 'q': q, 'page': 'cnf'})


@user_passes_test(is_c_and_f_admin, login_url='mlm_admin_login')
def accepted_order(request):
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        data = get_order_list_for_cnf_admin(request.user).filter(
            Q(name__icontains=q) | Q(order_id1__icontains=q) | Q(date__icontains=q) | Q(grand_total__contains=q),
            status=1, delete=False, paid=True).order_by('id')
    else:
        q = ''
        data = get_order_list_for_cnf_admin(request.user).filter(delete=False, status=1, paid=True).order_by('id')
    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'c_and_f/accepted_order.html',
                  {'data': page_obj, 'title': 'Accepted Order', 'q': q, 'page': 'cnf'})


@user_passes_test(is_c_and_f_admin, login_url='mlm_admin_login')
def accept_order(request, myid):
    print("Inside Accept_order")
    today = datetime.now().date()
    data = get_order_list_for_cnf_admin(request.user).get(pk=myid)
    om = OrderMaintain()
    om.set_token()
    om.get_channel_id()
    response = om.post_order(data)
    print(response)
    if response.get('status_code') == 1:
        data.sr_order_id = response['order_id']
        data.sr_shipment_id = response['shipment_id']
        data.sr_status = response['status']
        data.sr_status_code = response['status_code']
        data.sr_onboarding_completed_now = response['onboarding_completed_now']
        data.sr_awb_code = response['awb_code']
        data.sr_courier_company_id = response['courier_company_id']
        data.sr_courier_name = response['courier_name']
        data.save()
        get_order_list_for_cnf_admin(request.user).filter(pk=myid).update(status=1, accept_date=today)
        print(response)
        messages.success(request, "Username-" + str(data.name) + '  Order Id-' + str(
            data.order_id1) + "   Accepted Successfully" + " \n" + str(response))
    else:
        messages.warning(request,
                         response.get('message') + '  ' + str(response.get('data')) + ' ' + str(response.get('errors')))
    return redirect('cnf-order-list')


@user_passes_test(is_c_and_f_admin, login_url='mlm_admin_login')
def reject_order(request):
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        data = get_order_list_for_cnf_admin(request.user).filter(
            Q(name__icontains=q) | Q(order_id1__icontains=q) | Q(grand_total__contains=q) | Q(date__icontains=q),
            status=5, delete=False, paid=True).order_by('id')
    else:
        q = ''
        data = get_order_list_for_cnf_admin(request.user).filter(delete=False, status=5, paid=True).order_by('id')
    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # data = Order.objects.filter(status=5).exclude(delete=True)
    return render(request, 'c_and_f/reject.html', {'data': page_obj, 'title': 'Reject Order', 'q': q, 'page': 'cnf'})


@user_passes_test(is_c_and_f_admin, login_url='mlm_admin_login')
def decline_order(request):
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        data = get_order_list_for_cnf_admin(request.user).filter(
            Q(name__icontains=q) | Q(order_id1__icontains=q) | Q(grand_total__contains=q) | Q(date__icontains=q),
            status=8, delete=False, ).order_by('id')
    else:
        q = ''
        data = get_order_list_for_cnf_admin(request.user).filter(delete=False, status=8).order_by('id')
    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # data = get_order_list_for_cnf_admin(request.user).filter(status=6).exclude(delete=True)
    return render(request, 'c_and_f/decline_order.html',
                  {'data': page_obj, 'title': 'Decline Orders', 'q': q, 'page': 'cnf'})


@user_passes_test(is_c_and_f_admin, login_url='mlm_admin_login')
def orderstatus(request, myid):
    status = request.GET['status']
    print('status', status)
    data = get_order_list_for_cnf_admin(request.user).filter(pk=myid)
    data.update(status=status)
    for i in data:
        data1 = i.order_id1
    if status == '1':
        data1 = data1 + ' is Accepted'
    print('status', type(status))
    return JsonResponse(status=200, data={'data': data1, 'page': 'cnf'})


@user_passes_test(is_c_and_f_admin, login_url='mlm_admin_login')
def delete_order(request, myid, check):
    print('data ki value h ye ----->', check)
    get_order_list_for_cnf_admin(request.user).filter(pk=myid).update(delete=True)
    data = get_order_list_for_cnf_admin(request.user).get(pk=myid)
    messages.success(request, "Username-" + str(data.name) + '  Order Id-' + str(data.order_id1) + "  is deleted")
    if check == 'allorder':
        return redirect('allorder-list')
    elif check == 'order':
        return redirect('order-list')
    elif check == 'delivered':
        return redirect('delivered')
    elif check == 'accepted_order':
        return redirect('accepted_order')
    elif check == 'ready_to_dispatch':
        return redirect('ready_to_dispatch')
    elif check == 'dispatched':
        return redirect('dispatched')
    elif check == 'rejected':
        return redirect('reject_order')
    elif check == 'refunded':
        return redirect('refund')
    return redirect('cnf-order-list')


@user_passes_test(is_c_and_f_admin, login_url='mlm_admin_login')
def view_order(request, myid):
    order_qs = get_object_or_404(Order, pk=myid)
    form = Orderform(instance=order_qs)
    date = order_qs.date
    status = order_qs.status
    order = LineItem.objects.filter(order_id=order_qs.pk)
    group_user = Order.objects.filter(main_order=order_qs.pk)
    user = User.objects.filter(username=order_qs.email)[0]
    user_profile = Profile.objects.get(user=user)
    ARN = ReferralCode.objects.get(user_id=user)
    mc_cnf = Material_center.objects.filter(advisory_owned='NO')

    # Show_prices to the end customer.
    show_prices = False
    # Show complete information like accepted date, ready to ship date, etc.
    show_complete = False
    # We will show MRP if admin want to show MRP:
    if request.method == "POST":
        order_qs.shipment_height = request.POST.get("shipment_height")
        order_qs.shipment_width = request.POST.get("shipment_width")
        order_qs.shipment_length = request.POST.get("shipment_length")
        order_qs.shipment_weight = request.POST.get("shipment_weight")
        order_qs.save()
        return HttpResponseRedirect(reverse('view_order', kwargs={'myid': myid}))
    if request.method == 'GET':
        show_prices = request.GET.get('show_prices', False)
        show_complete = request.GET.get('show_complete', False)
        if show_prices == "Y":
            show_prices = True
        if show_complete == "Y":
            show_complete = True

    if order_qs.shipping_address == None:
        address_qs = get_object_or_404(Address, pk=order_qs.billing_address.pk)
        # We will show MRP if user want to receive order at his billing address:
        show_prices = True
    else:
        address_qs = get_object_or_404(Address, pk=order_qs.shipping_address.pk)
    # print('00000000000000000000000000000000000000',address_qs)
    dataform = AddressForm(instance=address_qs)
    if dataform.initial["address_type"] == 'B':
        show_prices = True
    if show_complete:
        show_prices = True
    params = {
        'form': form,
        'dataform': dataform,
        'date': date,
        'status': status,
        'order_list': order,
        'title': 'View Order',
        'user': user,
        'user_profile': user_profile,
        'ARN': ARN,
        'myid': myid,
        'order_qs': order_qs,
        'group_user': group_user,
        'show_prices': show_prices,
        'show_complete': show_complete,
        'page': 'cnf',
        'cnf':True,
        'mlm_admin': False,
        'mc_cnf': mc_cnf,
    }
    # return render(request, 'c_and_f/view_order.html', params)
    return render(request, 'mlm_admin/view_order.html', params)


@user_passes_test(is_c_and_f_admin, login_url='mlm_admin_login')
def ready_to_dispatch(request):
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        data = get_order_list_for_cnf_admin(request.user).filter(
            Q(name__icontains=q) | Q(order_id1__icontains=q) | Q(grand_total__contains=q) | Q(date__icontains=q),
            status=2, delete=False, paid=True).order_by('id')
    else:
        q = ''
        data = get_order_list_for_cnf_admin(request.user).filter(delete=False, status=2, paid=True).order_by('id')
    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'c_and_f/ready_to_dispatch.html',
                  {'data': page_obj, 'title': 'Ready To Dispatch', 'q': q, 'page': 'cnf'})


@user_passes_test(is_c_and_f_admin, login_url='mlm_admin_login')
def dispatched(request):
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        data = get_order_list_for_cnf_admin(request.user).filter(Q(name__icontains=q) | Q(order_id1__icontains=q) | Q(date__icontains=q), status=3,
                                    delete=False, paid=True).order_by('id')
    else:
        q = ''
        data = get_order_list_for_cnf_admin(request.user).filter(delete=False, status=3, paid=True).order_by('id')
    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'c_and_f/dispatched.html',
                  {'data': page_obj, 'title': 'Dispatched', 'q': q, 'page': 'cnf'})


@user_passes_test(is_c_and_f_admin, login_url='mlm_admin_login')
def delivered(request):
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        data = get_order_list_for_cnf_admin(request.user).filter(
            Q(name__icontains=q) | Q(order_id1__icontains=q) | Q(grand_total__contains=q) | Q(date__icontains=q),
            status=4, delete=False, paid=True).order_by('id')
    else:
        q = ''
        data = get_order_list_for_cnf_admin(request.user).filter(delete=False, status=4, paid=True).order_by('id')
    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'c_and_f/delivered.html', {'data': page_obj, 'title': 'Delivered', 'q': q, 'page': 'cnf'})


@user_passes_test(is_c_and_f_admin, login_url='mlm_admin_login')
def refund(request):
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        data = get_order_list_for_cnf_admin(request.user).filter(
            Q(name__icontains=q) | Q(order_id1__icontains=q) | Q(grand_total__contains=q) | Q(date__icontains=q),
            status=6, delete=False, paid=True).order_by('id')
    else:
        q = ''
        data = get_order_list_for_cnf_admin(request.user).filter(delete=False, status=6, paid=True).order_by('id')
    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # data = get_order_list_for_cnf_admin(request.user).filter(status=6).exclude(delete=True)
    return render(request, 'c_and_f/refund.html', {'data': page_obj, 'title': 'Refund', 'q': q, 'page': 'cnf'})


@user_passes_test(is_c_and_f_admin, login_url='mlm_admin_login')
def returned(request):
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        data = get_order_list_for_cnf_admin(request.user).filter(
            Q(name__icontains=q) | Q(order_id1__icontains=q) | Q(grand_total__contains=q) | Q(date__icontains=q),
            status=7, delete=False, paid=True).order_by('id')
    else:
        q = ''
        data = get_order_list_for_cnf_admin(request.user).filter(delete=False, status=7, paid=True).order_by('id')
    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # data = get_order_list_for_cnf_admin(request.user).filter(status=7).exclude(delete=True)
    return render(request, 'c_and_f/returned.html', {'data': page_obj, 'title': 'Returned', 'page': 'cnf'})


@user_passes_test(is_c_and_f_admin, login_url='mlm_admin_login')
def status_reject(request, myid):
    today = datetime.now().date()
    get_order_list_for_cnf_admin(request.user).filter(pk=myid).update(status=5, rejected_date=today)
    data = get_order_list_for_cnf_admin(request.user).get(pk=myid)
    messages.success(request, "Username-" + str(data.name) + '  Order Id-' + str(data.order_id1) + "  is reject")
    return redirect('cnf-order-list')

@user_passes_test(is_c_and_f_admin, login_url='mlm_admin_login')
def status_dispatched(request, myid):
    today = datetime.now().date()
    get_order_list_for_cnf_admin(request.user).filter(pk=myid).update(status=3,dispatched_date = today)
    data = get_order_list_for_cnf_admin(request.user).get(pk=myid)
    messages.success(request, "Username-" + str(data.name) + '  Order Id-' + str(data.order_id1) + "  is dispatched")
    return redirect('cnf-ready_to_dispatch')


@user_passes_test(is_c_and_f_admin, login_url='mlm_admin_login')
def status_ready_to_dispatch(request, myid):
    today = datetime.now().date()
    get_order_list_for_cnf_admin(request.user).filter(pk=myid).update(status=2,ready_to_dispatch_date = today)
    data = get_order_list_for_cnf_admin(request.user).get(pk=myid)
    messages.success(request,
                     "Username-" + str(data.name) + '  Order Id-' + str(data.order_id1) + "  Ready  To Dispatch")
    return redirect('cnf-accepted_order')

@user_passes_test(is_c_and_f_admin, login_url='mlm_admin_login')
def status_delivered(request, myid):
    today = datetime.now().date()
    get_order_list_for_cnf_admin(request.user).filter(pk=myid).update(status=4,delivered_date = today)
    data = get_order_list_for_cnf_admin(request.user).get(pk=myid)
    messages.success(request, "Username-" + str(data.name) + '  Order Id-' + str(data.order_id1) + "  is delivered")
    return redirect('cnf-dispatched')

@user_passes_test(is_c_and_f_admin, login_url='mlm_admin_login')
def status_returned(request, myid):
    today = datetime.now().date()
    get_order_list_for_cnf_admin(request.user).filter(pk=myid).update(status=7,returned_date = today)
    data = get_order_list_for_cnf_admin(request.user).get(pk=myid)
    messages.success(request, "Username-" + str(data.name) + '  Order Id-' + str(data.order_id1) + "  is returned")
    return redirect('cnf-dispatched')


@user_passes_test(is_c_and_f_admin, login_url='mlm_admin_login')
def status_refund(request, myid):
    today = datetime.now().date()
    get_order_list_for_cnf_admin(request.user).filter(pk=myid).update(status=6,refunded_date = today)
    data = get_order_list_for_cnf_admin(request.user).get(pk=myid)
    messages.success(request, "Username-" + str(data.name) + '  Order Id-' + str(data.order_id1) + "  is refund")
    return redirect('cnf-reject_order')


@user_passes_test(is_c_and_f_admin, login_url='mlm_admin_login')
def edit_sale(request, myid):
    print('somethin is better than nothing')
    if request.method == "POST":
        date = request.POST['date']
        mc_center_to = request.POST['mc_center_to']
        mc_center_from = request.POST['material_center_from']
        narration = request.POST['narration']
        user = request.POST['user']
        party_name = request.POST['party_name']
        sale_type = request.POST['sale_type']
        grand_total = request.POST['grand_total']
        quaantity_item = request.POST.getlist('quaantity_item')
        check_quantity = request.POST.getlist('check_quantity')
        result = quantity_validate(check_quantity,quaantity_item)
        if result == False:
            messages.success(request, "Bad Request (Quantity entered is greater than maximum allowed quantity).")
            return redirect('cnf_sale_list')
        print(check_quantity)
        print(quaantity_item)
        print(len(check_quantity) ,'--------',len(quaantity_item))
        distributor_price = request.POST.getlist('distributor_price')
        cgst_item = request.POST.getlist('cgst_item')
        sgst_item = request.POST.getlist('sgst_item')
        igst_item = request.POST.getlist('igst_item')
        vat_item = request.POST.getlist('vat_item')
        item = request.POST.getlist('item')
        batch = request.POST.getlist('batch')
        totalamount_item = request.POST.getlist('totalamount_item')
        print('narro', date, narration, quaantity_item, distributor_price, cgst_item, sgst_item, igst_item,
              vat_item, totalamount_item, 'item', item, 'batch', batch)
        try:
            material_center_to = Material_center.objects.get(pk=mc_center_to)
            material_center_from = Material_center.objects.get(pk=mc_center_from)
            user = User.objects.get(pk=user)
            data = Sale.objects.filter(pk=myid).update(sale_user_id = request.user,material_center_to=material_center_to,
                                                       material_center_from=material_center_from, date=date,
                                                       narration=narration,
                                                       advisor_distributor_name=user, sale_type=sale_type,
                                                       party_name=party_name, grand_total=grand_total)
            obj = Sale.objects.get(pk=myid)
            sale_items = Sale_itemDetails.objects.filter(sale=obj)
            for i in sale_items:
                update_time_batch_quantity = int(i.batch.quantity) + int(i.quantity)
                update_time_product_quantity = int(i.item.quantity) + int(i.quantity)
                Batch.objects.filter(pk=i.batch.pk).update(quantity=update_time_batch_quantity)
                Product.objects.filter(pk=i.item.pk).update(quantity=update_time_product_quantity)
                today = datetime.now().date()
                update_time_inventry = Inventry.objects.get(created_on=today, product=i.item,
                                                            batch=i.batch, material_center=material_center_from)
                update_time_inventry_current_quantity = int(update_time_inventry.current_quantity) + int(i.quantity)
                update_time_inventry_quantity_out = int(update_time_inventry.quantity_out) - int(i.quantity)
                Inventry.objects.filter(created_on=today, product=i.item, batch=i.batch,
                                        material_center=material_center_from).update(
                    current_quantity=update_time_inventry_current_quantity,
                    quantity_out=update_time_inventry_quantity_out)
            Sale_itemDetails.objects.filter(sale=obj).delete()
            try:
                for i, k in enumerate(totalamount_item):
                    sale = obj
                    print('obcet', sale)
                    quantity = quaantity_item[i]
                    price = distributor_price[i]
                    cgst = cgst_item[i]
                    sgst = sgst_item[i]
                    igst = igst_item[i]
                    vat = vat_item[i]
                    total_amount = totalamount_item[i]
                    product = item[i]
                    product = Product.objects.get(pk=product)
                    batch1 = batch[i]
                    batch1 = Batch.objects.get(pk=batch1)
                    update_product_quantity = (product.quantity - int(quantity))
                    p_quantity_update = Product.objects.filter(pk=product.pk).update(quantity=update_product_quantity)
                    batch_quantity = batch1.quantity
                    update_batch_quantity = int(batch_quantity) - int(quantity)
                    Batch.objects.filter(pk=batch1.pk).update(quantity=update_batch_quantity)
                    try:
                        # today = datetime.now().date()
                        # print(today)
                        # inventory_update = Inventry.objects.get(product=product, batch=batch1,
                        #                                         material_center=material_center_from,
                        #                                         created_on=today)
                        # inventory_update_current_quantity = int(inventory_update.current_quantity) - int(quantity)
                        # inventory_update_quantity_out = int(inventory_update.quantity_out) + int(quantity)
                        # Inventry.objects.filter(product=product, batch=batch1, material_center=material_center_from,
                        #                         created_on=today).update(
                        #     current_quantity=inventory_update_current_quantity,
                        #     quantity_out=inventory_update_quantity_out)
                        calculateTodayInventry(
                            product=product, 
                            batch= batch1,
                            quantity= quantity,
                            material_center= material_center_from
                        )
                    except:
                        return HttpResponse('<h1> Please check your code something is wrong </h1>')

                    #  inventory code end
                    sale_details_data = Sale_itemDetails(item=product, batch=batch1, sale=sale, quantity=quantity,
                                                         distributor_price=price, cgst=cgst, sgst=sgst, igst=igst,
                                                         vat=vat,
                                                         total_amount=total_amount)
                    sale_details_data.save()

                messages.success(request, "Record added successfully!")
                return redirect('cnf_sale_list')
            except:
                messages.success(request, "Record added successfully!")
                return redirect('cnf_sale_list')

        except Exception as e:

            messages.warning(request, "something is going wrong")
            return redirect('cnf_sale_list')
    material_center_to = Material_center.objects.filter(company_depot='NO').exclude(delete=True)
    material_center_from = Material_center.objects.filter(advisor_registration_number=request.user).exclude(delete=True)
    batches = Batch.objects.all().exclude(delete=True)
    items = Product.objects.all().exclude(delete=True)
    users = User.objects.all()
    sale_data = Sale.objects.get(pk=myid,accept=False)
    data = Sale_itemDetails.objects.filter(sale=sale_data)
    today = datetime.now().date()
    if sale_data.created_on != today:
        messages.warning(request,'You are not able to update these records')
        return redirect('cnf_sale_list')
    params = {
        'material_center_to': material_center_to,
        'material_center_from': material_center_from,
        'batches': batches,
        'items': items,
        'users': users,
        'sale_data': sale_data,
        'data': data,
        'title': 'Edit Sale'
    }
    return render(request, 'c_and_f/edit_sale.html', params)


@user_passes_test(is_c_and_f_admin, login_url='mlm_admin_login')
def delete_sale(request,myid):
    sale = Sale.objects.get(pk = myid)
    today = datetime.now().date()
    if sale.created_on != today:
        messages.warning(request,'You are not able to delete this records')
        return redirect('cnf_sale_list')
    sale_items = Sale_itemDetails.objects.filter(sale = sale)
    for i in sale_items:
        update_time_batch_quantity = int(i.batch.quantity) + int(i.quantity)
        update_time_product_quantity = int(i.item.quantity) + int(i.quantity)
        Batch.objects.filter(pk=i.batch.pk).update(quantity=update_time_batch_quantity)
        Product.objects.filter(pk=i.item.pk).update(quantity=update_time_product_quantity)
        calculateInventryForDelete(
            product= i.item,
            batch= i.batch,
            material_center= sale.material_center_from,
            quantity= i.quantity
        )
        # today = datetime.now().date()
        # update_time_inventry = Inventry.objects.get(created_on=today, product=i.item,
        #                                             batch=i.batch, material_center=sale.material_center_from)
        # update_time_inventry_current_quantity = int(update_time_inventry.current_quantity) + int(i.quantity)
        # update_time_inventry_quantity_out = int(update_time_inventry.quantity_out) - int(i.quantity)
        # Inventry.objects.filter(created_on=today, product=i.item, batch=i.batch,
        #                         material_center=sale.material_center_from).update(
        #     current_quantity=update_time_inventry_current_quantity,
        #     quantity_out=update_time_inventry_quantity_out)
    sale_delete=Sale.objects.filter(pk = myid).update(delete = True)
    return redirect('cnf_sale_list')
