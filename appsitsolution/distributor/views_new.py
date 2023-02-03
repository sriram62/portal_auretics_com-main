from decimal import Decimal
from django.db.models import Sum
import traceback
from shop.calculation import calculated_partial_loyalty_point_value, calculated_partial_loyalty_business_value, \
    calculate_loyalty_sale_product_total, calculated_partial_loyalty_details
from shop.models import Order, LineItem
from .utils import calculate_pro_rate_pv_bv
from .views import *
from business.views import Objectify, last_month_fn, last_year_fn, month_fn, year_fn
from .new_inventory_calculation import *
from mlm_calculation.models import consistent_retailers_income


def cri_validation_fn(request, user, batch=[], quaantity_item=[], check=False, edit=False, myid=False, essential=False):
    # AG :: We will find total CRI that will be consumed in this order.
    place = 0
    cri_consumed_in_this_order = 0
    # Adding up total amount from Batch List that we have got.
    for i in batch:
        i_batch = Batch.objects.get(id=i)
        i_total_amount = float(i_batch.mrp) * float(quaantity_item[place])
        cri_consumed_in_this_order += i_total_amount
        place += 1
        if not essential:
            # If order has essential item, then we will break the function
            # and return consumed_cri > available_cri, so that add/edit order results in a validation error.
            essential = i_batch.product.essential_product
            if essential == 'YES':
                return 0, 1, 0

    try:
        cri = consistent_retailers_income.objects.get(user=user,
                                                      input_date__month=last_month_fn(),
                                                      input_date__year=last_year_fn(),
                                                      )
    except:
        messages.warning(request, 'This user is not eligible for loyalty. For details, please contact Admin.')
        cri = Objectify()
        cri.cri_balance = 0

    # AG :: We will firstly check whether the CRI balance is correct.
    initial_cri = cri.cri_balance  # float(request.POST.get('available_cri_fixed', 0))
    cri_consumed_before_this_order = 0
    if edit:
        current_order_id = Distributor_Sale.objects.get(pk=myid).order.id
        ln = LineItem.objects.filter(order__email=user.email,
                                     order__loyalty_order=True,
                                     order__date__month=month_fn(),
                                     order__date__year=year_fn(),
                                     order__paid=True,
                                     order__delete=False).exclude(order__status=8).exclude(order__id=current_order_id)
    else:
        ln = LineItem.objects.filter(order__email=user.email,
                                     order__loyalty_order=True,
                                     order__date__month=month_fn(),
                                     order__date__year=year_fn(),
                                     order__paid=True,
                                     order__delete=False).exclude(order__status=8)
    for i in ln:
        cri_consumed_before_this_order += float(i.batch.mrp) * float(i.quantity)

    available_cri = float(cri.cri_earned) - float(cri_consumed_before_this_order)

    consumed_cri = cri_consumed_in_this_order  # initial_cri - available_cri

    # AG :: We will correct the User's CRI
    if consumed_cri > available_cri:
        cri.cri_balance = available_cri
    else:
        cri.cri_balance = (available_cri - consumed_cri)

    cri.save()

    return initial_cri, consumed_cri, available_cri


@user_passes_test(is_distributor, login_url='D_login')
def distributor_add_loyalty_sale_new(request, distributor_sale_id=None):
    if request.method == "POST":
        # AG :: Partial CRI is allowed only once for a User.
        # Once Partial Loyalty order is placed, then user will not get option to add/edit new loyalty.
        advisor_user = request.POST['advisor_user']
        user = User.objects.get(email=advisor_user)
        partial_cri = Order.objects.filter(email=user.email,
                                           date__month=month_fn(),
                                           date__year=year_fn(),
                                           is_partial_loyalty_order=True,
                                           delete=False,
                                           paid=True,
                                           ).exclude(status=8)
        if partial_cri:
            messages.warning(request, "Order Validation Error. Only One Partial Loyalty is allowed per user.")
            return redirect('distributor_loyalty_sale_list')

        date_data = datetime.now().date()
        mc_center = request.POST['material_center']

        # TBD
        # user = request.POST['user']
        sale_type = request.POST['sale_type']
        narration = request.POST['narration']
        grand_total = request.POST['grand_total']
        payment_mode = request.POST['payment_mode']
        quaantity_item = request.POST.getlist('quaantity_item')
        check_quantity = request.POST.getlist('check_quantity')
        result = quantity_validate(check_quantity, quaantity_item)

        if result == False:
            messages.success(request, "Bad Request (Quantity entered is greater than maximum allowed quantity).")
            return redirect('distributor_add_loyalty_sale_new')
        item = request.POST.getlist('item')
        batch = request.POST.getlist('batch')

        # AG :: Validation to find if duplicate batch items exists
        if not len(batch) == len(set(batch)):
            messages.warning(request,
                             "Order Validation Error: Duplicate Batch Found. Please Try Again or Contact Admin")
            return redirect('distributor_sale_list')

        initial_cri, consumed_cri, available_cri = cri_validation_fn(request, user, batch, quaantity_item)
        if consumed_cri > available_cri:
            messages.warning(request,
                             "Order Validation Error: CRI Consumed in this order is more than available CRI. Please try again.")
            return redirect('distributor_add_loyalty_sale_new')
        if initial_cri != available_cri:
            messages.success(request, "CRI Validation has been corrected with this order.")

        totalamount_item = request.POST.getlist('total_incurred_amount_item')
        pv_item = 0  # request.POST.getlist('pv_item')
        bv_item = 0  # request.POST.getlist('bv_item')
        # TBD
        material_center = Material_center.objects.get(pk=mc_center)
        order_id1 = order_id(material_center)
        address = Objectify()
        address.pin = 0
        try:
            # Shipping address is shipping address
            address = user.profile.shipping_address
        except:
            try:
                # Billing address is shipping address
                address = user.profile.billing_address
            except:
                pass
        try:
            o = Order(
                name=user.username,
                email=user.email,
                postal_code=address.pin,
                shipping_address=address,
                order_id1=order_id1,
                grand_total=grand_total,
                delivered_date=date_data,
                status=4,
                paid=True,
                material_center=material_center,
                consumed_cri=consumed_cri,
                loyalty_order=True,
                bv=0,
                pv=0,
            )
        except:
            o = Order(
                name=user.username,
                email=user.email,
                order_id1=order_id1,
                grand_total=grand_total,
                delivered_date=date_data,
                status=4,
                paid=True,
                material_center=material_center,
                consumed_cri=consumed_cri,
                loyalty_order=True,
                bv=0,
                pv=0,
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
            data.is_loyalty_sale = True
        else:
            data = Distributor_Sale(sale_user_id=request.user, material_center=material_center, date=date_data,
                                    narration=narration, advisor_distributor_name=user, payment_mode=payment_mode,
                                    sale_type=sale_type, grand_total=grand_total, order=o, is_pending=False
                                    , is_loyalty_sale=True
                                    )
        data.save()

        for i, k in enumerate(totalamount_item):
            try:
                sale = data
                quantity = quaantity_item[i]
                total_pv = 0  # pv_item[i]
                total_bv = 0  # bv_item[i]
                product = item[i]
                product = Product.objects.get(pk=product)
                batch1 = batch[i]
                batch1 = Batch.objects.get(pk=batch1)
                mrp = batch1.mrp or 0
                # cgst = product.cgst or 0
                # sgst = product.sgst or 0
                # igst = product.igst or 0
                # vat = product.vat or 0
                distributor_price = product.distributor_price or 0
                distributor_price = mrp / ((100 + distributor_price) / 100)
                igst = 0
                cgst = 0
                sgst = 0
                vat = 0
                # if sale_type == '1':
                #     distributor_price = mrp / ((100 + distributor_price) / 100)
                #     igst = 0
                #     cgst = 0
                #     sgst = 0
                #     vat = 0
                # else:
                #     distributor_price = mrp / ((100 + distributor_price) / 100)
                #     cgst = 0
                #     sgst = 0
                #     vat = 0
                #     igst = 0
                distributor_price = round(distributor_price, 2)
                price = distributor_price
                cgst = round(cgst, 2)
                sgst = round(sgst, 2)
                vat = round(vat, 2)
                igst = round(igst, 2)
                total_amount = int(quantity) * (distributor_price)
                total_amount = round(total_amount, 2)
                # try:
                #     batch_qty = Distributor_Batch.objects.get(batch=batch1, distributor_material_center=material_center)
                # except ObjectDoesNotExist:
                #     raise Exception(
                #         f'Distributor_Batch does not exist for batch <b> {batch1} </b>, and for material_center <b> {material_center} </b> please contact to the administrator.')
                # inventory code start
                # batch_quantity = batch_qty.quantity
                # update_batch_quantity = int(batch_quantity) - int(quantity)
                # Distributor_Batch.objects.filter(pk=batch_qty.pk).update(quantity=update_batch_quantity)

                # AG :: Re-calculating Distributor's Quantity First
                calculate_distributor_inventory(product=product,
                                                batch=batch1,
                                                material_center=material_center,
                                                quantity=0
                                                )

                # AG :: Checking whether stock of this item exist in our system.
                available_quantity = Distributor_Inventry.objects.filter(batch=batch1,
                                                                         material_center=material_center).latest(
                    'pk').current_quantity
                if not int(available_quantity) >= int(quantity):
                    messages.warning(request,
                                     "Order Validation Error. Insufficient Quantity. Please Try Again or Contact Admin")
                    return redirect('distributor_sale_list')

                # AG :: Now deducting the quantity from Distributor's Inventory and recalulating inventory again.
                calculate_distributor_inventory(product=product,
                                                batch=batch1,
                                                material_center=material_center,
                                                quantity=quantity
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
                    order_id=o.id,
                    batch=batch1,
                    cgst=product.cgst,
                    sgst=product.sgst,
                    igst=product.igst,
                    total_amount=total_amount,
                    pv=total_pv,
                    bv=total_bv
                )
                li.save()
                saledata.save()

            except Exception as error:
                # messages.warning(request, str(error))
                messages.error(request, str(error))
                return redirect('distributor_add_loyalty_sale_new')

        # # Saving BV & PV of edited item on Database.
        # o = Order.objects.get(pk=o.id)
        # pv = 0
        # bv = 0
        # grand_total = 0
        # Order.objects.filter(pk=o.id).update(pv=pv, bv=bv, grand_total=grand_total,loyalty_order=True)
        # Distributor_Sale.objects.filter(pk=sale.id).update(grand_pv=pv, grand_bv=bv, grand_total=grand_total)

        # order_data = Order.objects.get(pk=o.pk)
        # user = User.objects.get(email=order_data.email)
        # # updaate_super_bv(order_data.bv, user)

        recalculate_everything(request, myid=sale.id, post_bill=True, check=False, mlm_admin=False)
        initial_cri, consumed_cri, available_cri = cri_validation_fn(request, user, batch, quaantity_item, True)

        messages.success(request, "Record added successfully!")
        return redirect('distributor_view_sale', myid=sale.id)

    # referral_code = request.user.pk
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

    items = Product.objects.filter(pk__in=product, loyalty_consume='YES').exclude(delete=True)
    myDate = datetime.now()
    formatedDate = myDate.strftime("%Y-%m-%d")
    params = {
        'date': formatedDate,
        'batches': batches,
        'items': items,
        'material': material,
        'users': User.objects.all(),
        'loyalty': True,
    }
    if request.method == 'GET' and distributor_sale_id:
        pending_sale = Distributor_Sale.objects.get(pk=distributor_sale_id)
        order = pending_sale.order
        line_items = order.lineitem_set.all()
        params.update(line_items=line_items)
        params.update(sale_data=pending_sale)

    return render(request, 'distributor/add_loyalty_sale_new.html', params)


def get_product_based_on_cri_available(request):
    # try:
    # material = Material_center.get_center_for_user(request.user, advisory_owned='YES')
    material = Material_center.objects.filter(advisor_registration_number=request.user, advisory_owned='YES')
    if material:
        material = material.first()
    else:
        material = None
    # except ObjectDoesNotExist:
    #     material = None
    # batches = Batch.objects.all().exclude(delete=True)
    today = datetime.now().date()
    if material:
        products = Distributor_Inventry.objects.filter(created_on=today, current_quantity__gt=0, material_center=material).values_list('product')
    else:
        products = Distributor_Inventry.objects.filter(created_on=today, current_quantity__gt=0).values_list('product')
    # products = Distributor_Inventry.objects.filter(current_quantity__gte = 0).values_list('product')

    available_cri = request.GET.get('available_cri', 0)
    get_essential_items = request.GET.get('essential_items', False)
    # products = Distributor_Inventry.objects.filter(created_on=today, current_quantity__gte=0).values_list('product')
    product = []
    for i in products:
        for j in i:
            product.append(j)
    items = Product.objects.filter(pk__in=product, loyalty_consume='YES', batch__mrp__lte=available_cri).exclude(
        delete=True)
    # items = Product.objects.filter(pk__in=product, batch__mrp__lte=available_cri).exclude(
    #     delete=True)
    if get_essential_items:
        items = items.filter(essential_product='YES')
    else:
        items = items.exclude(essential_product='YES')
    list_of_product = [dict(
        id=item.id,
        display=f'{item.product_code} - {item.product_name}',
        distributor_price=item.distributor_price,
        mrp=item.mrp
    ) for item in items]
    list_of_product.insert(0,dict(
        id='',
        display='Select product',
        distributor_price=0,
        mrp=0
    ))
    return JsonResponse(list_of_product, safe=False)


@user_passes_test(is_distributor, login_url='D_login')
def distributor_add_fmcg_loyalty_sale_new(request, distributor_sale_id=None):
    if request.method == "POST":
        # AG :: Partial CRI is allowed only once for a User.
        # Once Partial Loyalty order is placed, then user will not get option to add/edit new loyalty.
        advisor_user = request.POST['advisor_user']
        user = User.objects.get(email=advisor_user)
        partial_cri = Order.objects.filter(email=user.email,
                                           date__month=month_fn(),
                                           date__year=year_fn(),
                                           is_partial_loyalty_order=True,
                                           delete=False,
                                           paid=True,
                                           ).exclude(status=8)
        if partial_cri:
            messages.warning(request, "Order Validation Error. Only One Partial Loyalty is allowed per user.")
            return redirect('distributor_loyalty_sale_list')

        date_data = datetime.now().date()
        mc_center = request.POST['material_center']

        # TBD
        # user = request.POST['user']
        sale_type = request.POST['sale_type']
        narration = request.POST['narration']
        grand_total = request.POST['grand_total']
        payment_mode = request.POST['payment_mode']
        quaantity_item = request.POST.getlist('quaantity_item')
        check_quantity = request.POST.getlist('check_quantity')
        result = quantity_validate(check_quantity, quaantity_item)

        if result == False:
            messages.success(request, "Bad Request (Quantity entered is greater than maximum allowed quantity).")
            return redirect('distributor_add_fmcg_loyalty_sale_new')
        item = request.POST.getlist('item')
        batch = request.POST.getlist('batch')

        # AG :: Validation to find if duplicate batch items exists
        if not len(batch) == len(set(batch)):
            messages.warning(request,
                             "Order Validation Error: Duplicate Batch Found. Please Try Again or Contact Admin")
            return redirect('distributor_add_fmcg_loyalty_sale_new')

        initial_cri, consumed_cri, available_cri = cri_validation_fn(request, user, batch, quaantity_item, essential=True)
        # AG :: We will validate essential order separately.
        essential_cri_li = LineItem.objects.filter(order__email=user.email,
                                                   order__loyalty_order=True,
                                                   order__date__month=month_fn(),
                                                   order__date__year=year_fn(),
                                                   order__paid=True,
                                                   order__delete=False,
                                                   product__essential_product='YES'
                                                  ).exclude(order__status=8)
        essential_cri_total = 0
        for i in essential_cri_li:
            essential_cri_total += (i.batch.mrp * i.quantity)

        try:
            cri = consistent_retailers_income.objects.get(user=user,
                                                          input_date__month=last_month_fn(),
                                                          input_date__year=last_year_fn(),
                                                          )
        except:
            messages.warning(request, 'This user is not eligible for loyalty. For details, please contact Admin.')
            cri = Objectify()
            cri.cri_balance = 0
            cri.cri_earned = 0

        if essential_cri_total > (float(cri.cri_earned) * 0.25):
            messages.warning(request,
                             "Order Validation Error: CRI Consumed in this order is more than Consumable CRI for Essential Loyalty Order . Please try again.")
            return redirect('distributor_add_fmcg_loyalty_sale_new')

        if consumed_cri > available_cri:
            messages.warning(request,
                             "Order Validation Error: CRI Consumed in this order is more than available CRI. Please try again.")
            return redirect('distributor_add_fmcg_loyalty_sale_new')
        if initial_cri != available_cri:
            messages.success(request, "CRI Validation has been corrected with this order.")

        totalamount_item = request.POST.getlist('total_incurred_amount_item')
        pv_item = 0  # request.POST.getlist('pv_item')
        bv_item = 0  # request.POST.getlist('bv_item')
        # TBD
        material_center = Material_center.objects.get(pk=mc_center)
        order_id1 = order_id(material_center)
        address = Objectify()
        address.pin = 0
        try:
            # Shipping address is shipping address
            address = user.profile.shipping_address
        except:
            try:
                # Billing address is shipping address
                address = user.profile.billing_address
            except:
                pass
        try:
            o = Order(
                name=user.username,
                email=user.email,
                postal_code=address.pin,
                shipping_address=address,
                order_id1=order_id1,
                grand_total=grand_total,
                delivered_date=date_data,
                status=4,
                paid=True,
                material_center=material_center,
                consumed_cri=consumed_cri,
                loyalty_order=True,
                bv=0,
                pv=0,
            )
        except:
            o = Order(
                name=user.username,
                email=user.email,
                order_id1=order_id1,
                grand_total=grand_total,
                delivered_date=date_data,
                status=4,
                paid=True,
                material_center=material_center,
                consumed_cri=consumed_cri,
                loyalty_order=True,
                bv=0,
                pv=0,
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
            data.is_loyalty_sale = True
        else:
            data = Distributor_Sale(sale_user_id=request.user, material_center=material_center, date=date_data,
                                    narration=narration, advisor_distributor_name=user, payment_mode=payment_mode,
                                    sale_type=sale_type, grand_total=grand_total, order=o, is_pending=False
                                    , is_loyalty_sale=True
                                    )
        data.save()

        for i, k in enumerate(totalamount_item):
            try:
                sale = data
                quantity = quaantity_item[i]
                total_pv = 0  # pv_item[i]
                total_bv = 0  # bv_item[i]
                product = item[i]
                product = Product.objects.get(pk=product)
                batch1 = batch[i]
                batch1 = Batch.objects.get(pk=batch1)
                mrp = batch1.mrp or 0
                distributor_price = product.distributor_price or 0
                distributor_price = mrp / ((100 + distributor_price) / 100)
                igst = 0
                cgst = 0
                sgst = 0
                vat = 0
                distributor_price = round(distributor_price, 2)
                price = distributor_price
                cgst = round(cgst, 2)
                sgst = round(sgst, 2)
                vat = round(vat, 2)
                igst = round(igst, 2)
                total_amount = int(quantity) * (distributor_price)
                total_amount = round(total_amount, 2)

                # AG :: Re-calculating Distributor's Quantity First
                calculate_distributor_inventory(product=product,
                                                batch=batch1,
                                                material_center=material_center,
                                                quantity=0
                                                )

                # AG :: Checking whether stock of this item exist in our system.
                available_quantity = Distributor_Inventry.objects.filter(batch=batch1,
                                                                         material_center=material_center).latest(
                    'pk').current_quantity
                if not int(available_quantity) >= int(quantity):
                    messages.warning(request,
                                     "Order Validation Error. Insufficient Quantity. Please Try Again or Contact Admin")
                    return redirect('distributor_sale_list')

                # AG :: Now deducting the quantity from Distributor's Inventory and recalulating inventory again.
                calculate_distributor_inventory(product=product,
                                                batch=batch1,
                                                material_center=material_center,
                                                quantity=quantity
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
                    order_id=o.id,
                    batch=batch1,
                    cgst=product.cgst,
                    sgst=product.sgst,
                    igst=product.igst,
                    total_amount=total_amount,
                    pv=total_pv,
                    bv=total_bv
                )
                li.save()
                saledata.save()

            except Exception as error:
                # messages.warning(request, str(error))
                messages.error(request, str(error))
                return redirect('distributor_add_fmcg_loyalty_sale_new')

        recalculate_everything(request, myid=sale.id, post_bill=True, check=False, mlm_admin=False)
        initial_cri, consumed_cri, available_cri = cri_validation_fn(request, user, batch, quaantity_item, True, essential=True)

        essential_cri_total += o.consumed_cri

        if essential_cri_total > (float(cri.cri_earned) * 0.25):
            distributor_delete_loyalty_sale(request, myid=sale.id)
            messages.warning(request,
                             "Order Validation Error: CRI Consumed in this order is more than Consumable CRI for Essential Loyalty Order . Please try again.")
            return redirect('distributor_add_fmcg_loyalty_sale_new')

        messages.success(request, "Record added successfully!")
        return redirect('distributor_view_sale', myid=sale.id)
        # return redirect('distributor_loyalty_sale_list')

    # referral_code = request.user.pk
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

    items = Product.objects.filter(pk__in=product, loyalty_consume='YES').exclude(delete=True)
    myDate = datetime.now()
    formatedDate = myDate.strftime("%Y-%m-%d")
    params = {
        'date': formatedDate,
        'batches': batches,
        'items': items,
        'material': material,
        'users': User.objects.all(),
        'loyalty':True,
    }
    if request.method == 'GET' and distributor_sale_id:
        pending_sale = Distributor_Sale.objects.get(pk=distributor_sale_id)
        order = pending_sale.order
        line_items = order.lineitem_set.all()
        params.update(line_items=line_items)
        params.update(sale_data=pending_sale)

    return render(request, 'distributor/add_fmcg_loyalty_sale.html', params)


@user_passes_test(is_distributor, login_url='D_login')
def distributor_add_partial_loyalty_sale(request, distributor_sale_id=None):
    if request.method == "POST":
        # AG :: Partial CRI is allowed only once for a User. Once Partial Loyalty order is placed, then user will not get option to add/edit new loyalty.
        advisor_user = request.POST['advisor_user']
        user = User.objects.get(email=advisor_user)
        partial_cri = Order.objects.filter(email=user.email,
                                           date__month=month_fn(),
                                           date__year=year_fn(),
                                           is_partial_loyalty_order=True,
                                           delete=False,
                                           paid=True,
                                           ).exclude(status=8)
        if partial_cri:
            messages.warning(request, "Order Validation Error. Only One Partial Loyalty is allowed per user.")
            return redirect('distributor_loyalty_sale_list')
        date_data = datetime.now().date()
        mc_center = request.POST['material_center']
        # available_cri = float(request.POST.get('available_cri', 0))
        # initial_cri = float(request.POST.get('available_cri_fixed', 0))
        # consumed_cri = initial_cri - available_cri
        # TBD
        # user = request.POST['user']
        # advisor_user = request.POST['advisor_user']
        sale_type = request.POST['sale_type']
        narration = request.POST['narration']
        grand_total = request.POST['grand_total']
        payment_mode = request.POST['payment_mode']
        quaantity_item = [1, ]  # request.POST.getlist('quaantity_item')
        check_quantity = request.POST.getlist('check_quantity')
        result = quantity_validate(check_quantity, quaantity_item)

        if result == False:
            messages.success(request, "Bad Request (Quantity entered is greater than maximum allowed quantity).")
            return redirect('distributor_add_loyalty_sale_new')
        # distributor_price = request.POST.getlist('distributor_price')
        # cgst_item = request.POST.getlist('cgst_item')
        # sgst_item = request.POST.getlist('sgst_item')
        # igst_item = request.POST.getlist('igst_item')
        # vat_item = request.POST.getlist('vat_item')
        item = request.POST.getlist('item')
        batch = request.POST.getlist('batch')

        # AG :: Validation to find if duplicate batch items exists
        if not len(batch) == len(set(batch)):
            messages.warning(request,
                             "Order Validation Error: Duplicate Batch Found. Please Try Again or Contact Admin")
            return redirect('distributor_sale_list')

        initial_cri, consumed_cri, available_cri = cri_validation_fn(request, user, batch, quaantity_item)
        if consumed_cri > available_cri:
            excess_cri = consumed_cri - available_cri
            consumed_cri = available_cri
        else:
            messages.warning(request,
                             "Order Validation Error: Partial CRI not possible as CRI is not fully consumed. Please use Add Loyalty option instead.")
            return redirect('distributor_sale_list')
        if initial_cri != available_cri:
            messages.success(request, "CRI Validation has been corrected with this order.")

        totalamount_item = request.POST.getlist('total_incurred_amount_item')
        pv_item = 0  # request.POST.getlist('pv_item')
        bv_item = 0  # request.POST.getlist('bv_item')
        # TBD
        # user = User.objects.get(email=advisor_user)
        material_center = Material_center.objects.get(pk=mc_center)
        order_id1 = order_id(material_center)
        address = Objectify()
        address.pin = 0
        try:
            # Shipping address is shipping address
            address = user.profile.shipping_address
        except:
            try:
                # Billing address is shipping address
                address = user.profile.billing_address
            except:
                pass
        try:
            # Shipping address is shipping address
            o = Order(
                name=user.username,
                email=user.email,
                postal_code=address.pin,
                shipping_address=address,
                order_id1=order_id1,
                grand_total=grand_total,
                delivered_date=date_data,
                status=4,
                paid=True,
                material_center=material_center,
                consumed_cri=consumed_cri,
                loyalty_order=True,
                is_partial_loyalty_order=True,
                bv=bv_item,
                pv=pv_item,
            )
        except:
            # shipping address is billing address here
            o = Order(
                name=user.username,
                email=user.email,
                postal_code=address.pin,
                shipping_address=address,
                order_id1=order_id1,
                grand_total=grand_total,
                delivered_date=date_data,
                status=4,
                paid=True,
                material_center=material_center,
                consumed_cri=consumed_cri,
                loyalty_order=True,
                is_partial_loyalty_order=True,
                bv=bv_item,
                pv=pv_item,
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
            data.is_loyalty_sale = True
            data.is_partial_loyalty_sale = True
        else:
            data = Distributor_Sale(sale_user_id=request.user, material_center=material_center, date=date_data,
                                    narration=narration, advisor_distributor_name=user, payment_mode=payment_mode,
                                    sale_type=sale_type, grand_total=grand_total, order=o, is_pending=False
                                    , is_partial_loyalty_sale=True, is_loyalty_sale=True)
        data.save()
        # update_last_month_cri(user, consumed_cri, available_cri)

        try:
            for i, k in enumerate(totalamount_item):
                sale = data
                quantity = 1
                product = item[i]
                product = Product.objects.get(pk=product)
                batch1 = batch[i]
                batch1 = Batch.objects.get(pk=batch1)
                # mrp = batch1.mrp or 0
                # cgst = product.cgst or 0
                # sgst = product.sgst or 0
                # igst = product.igst or 0
                distributor_price = product.distributor_price or 0
                pv, bv, distributor_price = calculated_partial_loyalty_details(product, excess_cri)
                igst = 0
                cgst = 0
                sgst = 0
                vat = 0
                # if sale_type == '1':
                #     distributor_price = mrp / ((100 + igst) / 100) / ((100 + distributor_price) / 100)
                #     igst = distributor_price * (igst / 100)
                #     cgst = 0
                #     sgst = 0
                #     vat = distributor_price * (vat / 100)
                # else:
                #     distributor_price = mrp / ((100 + (sgst + cgst)) / 100) / ((100 + distributor_price) / 100)
                #     cgst = distributor_price * (cgst / 100)
                #     sgst = distributor_price * (sgst / 100)
                #     vat = distributor_price * (vat / 100)
                #     igst = 0
                distributor_price = round(distributor_price, 2)
                price = distributor_price
                cgst = round(cgst, 2)
                sgst = round(sgst, 2)
                vat = round(vat, 2)
                igst = round(igst, 2)

                # total_amount = calculate_loyalty_sale_product_total(batch1, consumed_cri)
                total_amount = distributor_price
                total_amount = round(total_amount, 2)
                # try:
                #     batch_qty = Distributor_Batch.objects.get(batch=batch1, distributor_material_center=material_center)
                # except ObjectDoesNotExist:
                #     raise Exception(
                #         f'Distributor_Batch does not exist for batch <b> {batch1} </b>, and for material_center <b> {material_center} </b> please contact to the administrator.')
                # # inventory code start
                # batch_quantity = batch_qty.quantity
                # update_batch_quantity = int(batch_quantity) - int(quantity)
                # Distributor_Batch.objects.filter(pk=batch_qty.pk).update(quantity=update_batch_quantity)

                # AG :: Re-calculating Distributor's Quantity First
                calculate_distributor_inventory(product=product,
                                                batch=batch1,
                                                material_center=material_center,
                                                quantity=0
                                                )

                # AG :: Checking whether stock of this item exist in our system.
                available_quantity = Distributor_Inventry.objects.filter(batch=batch1,
                                                                         material_center=material_center).latest(
                    'pk').current_quantity
                if not int(available_quantity) >= int(quantity):
                    messages.warning(request,
                                     "Order Validation Error. Insufficient Quantity. Please Try Again or Contact Admin")
                    return redirect('distributor_sale_list')

                # AG :: Now deducting the quantity from Distributor's Inventory and recalulating inventory again.
                calculate_distributor_inventory(product=product,
                                                batch=batch1,
                                                material_center=material_center,
                                                quantity=quantity
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
                    order_id=o.id,
                    batch=batch1,
                    cgst=product.cgst,
                    sgst=product.sgst,
                    igst=product.igst,
                    total_amount=total_amount,
                    pv=pv,
                    bv=bv, )
                li.save()
                saledata.save()

                # AG :: Breaking for loop as we will run it only for 1 item.
                break

            # # AG :: We are using conventional method here as we dont want to perform calculation using cri_validation_fn in partial CRI.
            # # Saving BV & PV of edited item on Database.
            # o = Order.objects.get(pk=o.id)
            # pv = sum([li.pv for li in o.lineitem_set.all()])
            # bv = sum([li.bv for li in o.lineitem_set.all()])
            # grand_total = sum([li.total_amount for li in o.lineitem_set.all()])
            # Order.objects.filter(pk=o.id).update(pv=pv, bv=bv, grand_total=grand_total, loyalty_order=True)
            # Distributor_Sale.objects.filter(pk=sale.id).update(grand_pv=pv, grand_bv=bv, grand_total=grand_total)

            # order_data = Order.objects.get(pk=o.pk)
            # user = User.objects.get(email=order_data.email)
            # updaate_super_bv(order_data.bv, user)

        except Exception as error:
            # messages.warning(request, str(error))
            messages.error(request, str(error))
            return redirect('distributor_add_loyalty_sale_new')

        recalculate_everything(request, myid=sale.id, post_bill=True, check=False, mlm_admin=False, loop=0,
                               dist_order=True, excess_cri=excess_cri)
        # initial_cri, consumed_cri, available_cri = cri_validation_fn(request, user, batch, quaantity_item, True)

        messages.success(request, "Record added successfully!")
        return redirect('distributor_view_sale', myid=sale.id)

    # referral_code = request.user.pk
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

    items = Product.objects.filter(pk__in=product, loyalty_consume='YES').exclude(delete=True)
    myDate = datetime.now()
    formatedDate = myDate.strftime("%Y-%m-%d")
    params = {
        'date': formatedDate,
        'batches': batches,
        'items': items,
        'material': material,
        'users': User.objects.all(),
        # 'loyalty': True,
    }
    if request.method == 'GET' and distributor_sale_id:
        pending_sale = Distributor_Sale.objects.get(pk=distributor_sale_id)
        order = pending_sale.order
        line_items = order.lineitem_set.all()
        params.update(line_items=line_items)
        params.update(sale_data=pending_sale)
    return render(request, 'distributor/add_partial_loyalty_sale.html', params)


@user_passes_test(is_distributor, login_url='D_login')
def distributor_edit_loyalty_sale(request, myid):
    sale = Distributor_Sale.objects.get(pk=myid)

    # AG :: We will not allow edit for Partial Loyalty Order. Users has to delete it and create a new one.
    is_partial_loyalty = sale.order.is_partial_loyalty_order
    if is_partial_loyalty:
        messages.success(request,
                         "Edit for Partial Loyalty is not allowed. Please delete partial loyalty order and create a new one.")
        return redirect('distributor_loyalty_sale_list')

    # AG :: Partial CRI is allowed only once for a User. Once Partial Loyalty order is placed, then user will not get option to add/edit new loyalty.
    # advisor_user = request.POST['advisor_user']
    user = User.objects.get(email=sale.order.email)
    partial_cri = Order.objects.filter(email=user.email,
                                       date__month=month_fn(),
                                       date__year=year_fn(),
                                       is_partial_loyalty_order=True,
                                       delete=False,
                                       paid=True,
                                       ).exclude(status=8)
    if partial_cri:
        messages.warning(request, "Order Validation Error. Only One Partial Loyalty is allowed per user.")
        return redirect('distributor_loyalty_sale_list')

    today = datetime.now().date()
    if sale.created_on != today:
        messages.warning(request, 'You are not able to edit this records')
        return redirect('distributor_loyalty_sale_list')
    if sale.sale_user_id != request.user:
        messages.warning(request, 'You are not able to edit this records')
        return redirect('distributor_loyalty_sale_list')

    # distributor_delete_loyalty_sale(request, myid)
    # distributor_add_loyalty_sale_new(request)

    # check that myid belongs to the current logged in user, required.
    # <--------------------------------------------------Dealing with post request Start here---------------------------------------------------------------------------------------------------------------------->
    if request.method == "POST":
        date = datetime.now().date()
        mc_center = request.POST['material_center']
        # available_cri = float(request.POST.get('available_cri', 0))
        # initial_cri = float(request.POST.get('available_cri_fixed', 0))
        # current_consumed_cri = initial_cri - available_cri
        # mc_center_from = request.POST['material_center_from']
        sale_type = request.POST['sale_type']
        narration = request.POST['narration']
        # user = request.POST['advisor_user']
        # party_name = request.POST['party_name']
        grand_total = request.POST['grand_total']
        # grand_pv = request.POST['grand_pv']
        # grand_bv = request.POST['grand_bv']
        payment_mode = request.POST['payment_mode']
        quaantity_item = request.POST.getlist('quaantity_item')
        check_quantity = request.POST.getlist('check_quantity')
        result = quantity_validate(check_quantity, quaantity_item)
        advisor_user = request.POST['advisor_user']
        user = User.objects.get(email=advisor_user)

        pv_item = 0  # request.POST.getlist('pv_item')
        bv_item = 0  # request.POST.getlist('bv_item')
        if result == False:
            messages.success(request, "Bad Request (Quantity entered is greater than maximum allowed quantity).")
            return redirect('distributor_edit_loyalty_sale', myid=myid)
        item = request.POST.getlist('item')
        batch = request.POST.getlist('batch')

        # AG :: Validation to find if duplicate batch items exists
        if not len(batch) == len(set(batch)):
            messages.warning(request,
                             "Order Validation Error: Duplicate Batch Found. Please Try Again or Contact Admin")
            return redirect('distributor_sale_list')

        initial_cri, consumed_cri, available_cri = cri_validation_fn(request, user, batch, quaantity_item, False, True,
                                                                     myid)
        if consumed_cri > available_cri:
            messages.warning(request,
                             "Order Validation Error: CRI Consumed in this order is more than available CRI. Please try again.")
            return redirect('distributor_edit_loyalty_sale', myid=myid)
        if initial_cri != available_cri:
            messages.success(request, "CRI Validation has been corrected with this order.")

        distributor_price = request.POST.getlist('distributor_price')
        cgst_item = request.POST.getlist('cgst_item')
        sgst_item = request.POST.getlist('sgst_item')
        igst_item = request.POST.getlist('igst_item')
        pv_item = 0  # request.POST.getlist('pv_item')
        bv_item = 0  # request.POST.getlist('bv_item')
        # vat_item = request.POST.getlist('vat_item')
        totalamount_item = request.POST.getlist('total_incurred_amount_item')
        # user = User.objects.get(email=user)
        # try:
        material_center = Material_center.objects.get(pk=mc_center)
        # material_center_from = Material_center.objects.get(pk=mc_center_from)
        # user = User.objects.get(pk=user)
        data = Distributor_Sale.objects.filter(pk=myid).update(
            # sale_user_id=request.user,      # AG: removed as we dont want to update user in any case.
            # material_center=material_center,# AG: removed as we dont want to update user in any case.
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
            postal_code = 0
            shipping_address = 0

        Order.objects.filter(pk=obj.order.pk).update(grand_total=grand_total,
                                                     # name=user.username,          # AG: removed as we dont want to update user in any case.
                                                     # email=user.email,            # AG: removed as we dont want to update user in any case.
                                                     paid=True,
                                                     postal_code=postal_code,
                                                     shipping_address=shipping_address,
                                                     consumed_cri=consumed_cri,
                                                     # material_center=material_center  # AG: removed as we dont want to update MC in any case.
                                                     )

        # sale_items = Distributor_Sale_itemDetails.objects.filter(sale=obj)

        # for i in sale_items:
        # distributor_batch = Distributor_Batch.objects.get(batch=i.batch,
        #                                                   distributor_material_center=obj.material_center)
        # update_time_batch_quantity = int(distributor_batch.quantity) + int(i.quantity)
        # Distributor_Batch.objects.filter(pk=distributor_batch.pk).update(quantity=update_time_batch_quantity)
        # today = datetime.now().date()
        #     update_time_inventry = Distributor_Inventry.objects.get(created_on=today, product=i.item,
        #                                                             batch=i.batch, material_center=obj.material_center)
        #     update_time_inventry_current_quantity = int(update_time_inventry.current_quantity) + int(i.quantity)
        #     update_time_inventry_quantity_out = int(update_time_inventry.quantity_out) - int(i.quantity)
        #     Distributor_Inventry.objects.filter(pk=update_time_inventry.pk).update(
        #         current_quantity=update_time_inventry_current_quantity,
        #         quantity_out=update_time_inventry_quantity_out)
        # Distributor_Sale_itemDetails.objects.filter(sale=obj).delete()
        # LineItem.objects.filter(order_id=obj.order.pk).delete()

        for i, k in enumerate(totalamount_item):
            try:
                sale = obj
                quantity = quaantity_item[i]
                # price = distributor_price[i]
                total_pv = 0  # [i]
                total_bv = 0  # bv_item[i]
                product = item[i]
                product = Product.objects.get(pk=product)
                batch1 = batch[i]
                batch1 = Batch.objects.get(pk=batch1)
                mrp = batch1.mrp or 0
                # cgst = cgst_item[i]
                # sgst = sgst_item[i]
                # igst = igst_item[i]
                #
                # # vat = vat_item[i]
                distributor_price = product.distributor_price or 0
                distributor_price = mrp / ((100 + distributor_price) / 100)
                igst = 0
                cgst = 0
                sgst = 0
                vat = 0
                distributor_price = round(distributor_price, 2)
                price = distributor_price
                cgst = round(cgst, 2)
                sgst = round(sgst, 2)
                vat = round(vat, 2)
                igst = round(igst, 2)
                # total_amount = totalamount_item[i]
                total_amount = int(quantity) * (distributor_price)
                total_amount = round(total_amount, 2)
                # product = item[i]
                # product = Product.objects.get(pk=product)
                batch1 = batch[i]
                batch1 = Batch.objects.get(pk=batch1)
                # batch_qty = Distributor_Batch.objects.get(batch=batch1, distributor_material_center=material_center)
                # inventory code start
                # batch_quantity = batch_qty.quantity
                # update_batch_quantity = int(batch_quantity) - int(quantity)
                # Distributor_Batch.objects.filter(pk=batch_qty.pk).update(quantity=update_batch_quantity)

                # AG :: Re-calculating Distributor's Quantity First
                calculate_distributor_inventory(product=product,
                                                batch=batch1,
                                                material_center=material_center,
                                                quantity=0
                                                )

                # AG :: Checking whether stock of this item exist in our system.
                available_quantity = Distributor_Inventry.objects.filter(batch=batch1,
                                                                         material_center=material_center).latest(
                    'pk').current_quantity
                if not int(available_quantity) >= int(quantity):
                    messages.warning(request,
                                     "Order Validation Error. Insufficient Quantity. Please Try Again or Contact Admin")
                    return redirect('distributor_sale_list')

                # AG :: Now deducting the quantity from Distributor's Inventory and recalulation inventory again.
                calculate_distributor_inventory(product=product,
                                                batch=batch1,
                                                material_center=material_center,
                                                quantity=quantity
                                                )

                saledata = Distributor_Sale_itemDetails(item=product, sale=sale, batch=batch1, quantity=quantity,
                                                        distributor_price=price, cgst=cgst, sgst=sgst, igst=igst, vat=0,
                                                        total_amount=total_amount)
                li = LineItem.objects.update_or_create(order_by=user.email,
                                                       order_id=obj.order.id,
                                                       batch=batch1, defaults={
                        'order_by': user.email,
                        'product_id': product.id,
                        'price': price,
                        # price: cart_item.price,
                        'quantity': quantity,
                        'order_id': obj.order.id,
                        'batch': batch1,
                        'cgst': product.cgst,
                        'sgst': product.sgst,
                        'igst': product.igst,
                        'total_amount': total_amount,
                        'pv': 0,  # total_pv,
                        'bv': 0,  # total_bv,
                    }
                                                       )
                li.save()
                saledata.save()
            except Exception as e:
                print(e)
                messages.error(request, "something went wrong")
                return redirect('distributor_loyalty_sale_list')

        # Saving BV & PV of edited item on Database.
        # o = Order.objects.get(pk=obj.order.id)
        # pv = sum([li.pv for li in obj.order.lineitem_set.all()])
        # bv = sum([li.bv for li in obj.order.lineitem_set.all()])
        # grand_total = sum([li.total_amount for li in obj.order.lineitem_set.all()])
        # Order.objects.filter(pk=obj.order.id).update(pv=pv, bv=bv, grand_total=grand_total, modified=True)
        # Distributor_Sale.objects.filter(pk=myid).update(grand_pv=pv, grand_bv=bv, grand_total=grand_total)
        #
        # order_data = Order.objects.get(pk=o.pk)
        # user = User.objects.get(email=order_data.email)

        recalculate_everything(request, myid=sale.id, post_bill=True, check=False, mlm_admin=False)
        initial_cri, consumed_cri, available_cri = cri_validation_fn(request, user, batch, quaantity_item, True)

        messages.success(request, "Record edited successfully!")
        # handle_cri_consumed_record(user, current_consumed_cri, order_data.consumed_cri)
        # order_data.consumed_cri = current_consumed_cri
        # order_data.save()
        return redirect('distributor_view_sale', myid=sale.id)

    # # <--------------------------------------------------Dealing with post request End here--------------------------------------------------------------------------------------------------------------------->
    #
    # today = datetime.now().date()

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
        return redirect('distributor_loyalty_sale_list')
    params = {
        'batches': batches,
        'items': items,
        'sale_data': sale_data,
        'data': shopLineObj,
        'title': 'Edit Sale',
        'cri_details': get_cri_details_for(sale_data.sale_user_id),
        'loyalty': True,
    }
    return render(request, 'distributor/edit_loyalty_sale.html', params)


@csrf_exempt
def add_loyalty_saleField(request):
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
        'cnt_multiple_product': cnt_multiple_product,
        'loyalty': True,
    }
    return render(request, 'distributor/add_loyalty_saleField.html', params)


@csrf_exempt
def add_partial_loyalty_saleField(request):
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
        'cnt_multiple_product': cnt_multiple_product,
        'loyalty': True,
    }
    return render(request, 'distributor/add_partial_loyalty_saleField.html', params)


def handle_cri_consumed_record(user, current_consumed_cri, previous_consumed_cri):
    if current_consumed_cri == previous_consumed_cri:
        return
    last_month = datetime.today() - timedelta(days=30)
    last_month_consistent_retailer_incomes = consistent_retailers_income.objects.filter(user=user,
                                                                                        input_date__month=last_month.month,
                                                                                        input_date__year=last_month.year)

    if last_month_consistent_retailer_incomes.exists():
        cri_item = last_month_consistent_retailer_incomes.first()
        consumed = float(cri_item.cri_consumed) - float(previous_consumed_cri) + float(current_consumed_cri)
        available = float(cri_item.cri_earned) - float(consumed)
        last_month_consistent_retailer_incomes.update(cri_consumed=consumed, cri_balance=available)


@user_passes_test(is_distributor, login_url='D_login')
def distributor_loyalty_deleted_sale_list(request):
    response = distributor_loyalty_sale_list(request, deleted=True)
    return response


@user_passes_test(is_distributor, login_url='D_login')
def distributor_loyalty_sale_list(request, deleted=False):
    pending_sales_view = request.GET.get('pending_sales', '')
    today = datetime.now().date()
    data = Distributor_Sale.objects.filter(delete=deleted, sale_user_id=request.user,
                                           is_pending=False, is_loyalty_sale=True)
    return render(request, 'distributor/loyalty_sale_list.html', {'data': data, 'title': 'Sale List',
                                                                  'today': today,
                                                                  'pending_sales_view': pending_sales_view,
                                                                  'data_from_pending_sale': False,
                                                                  'deleted': deleted, })


def update_last_month_cri(user, consumed, available):
    last_month_consistent_retailer_incomes = consistent_retailers_income.objects.filter(user=user,
                                                                                        input_date__month=last_month_fn(),
                                                                                        input_date__year=last_year)
    if last_month_consistent_retailer_incomes.exists():
        item = last_month_consistent_retailer_incomes.first()
        consumed = item.cri_consumed + Decimal(consumed)
        last_month_consistent_retailer_incomes.update(cri_consumed=consumed, cri_balance=available)


def get_cri_details_for(user):
    from mlm_calculation.models import consistent_retailers_income
    # this_month = datetime.today().replace(day=1)
    # # last_day_of_prev_month = this_month - timedelta(month=1)
    # last_month = this_month - timedelta(month=1)
    # # last_month = last_month.replace(day=1)
    last_month_consistent_retailer_incomes = consistent_retailers_income.objects.filter(user=user,
                                                                                        input_date__month=last_month_fn(),
                                                                                        input_date__year=last_year_fn(),
                                                                                        )
    # this_month_consistent_retailer_incomes = consistent_retailers_income.objects.filter(user=user,
    #                                                                                     input_date__year=month_fn(),
    #                                                                                     input_date__month=year_fn(),
    #                                                                                     )
    last_month_cri = 0
    current_month_cri = 0
    from mlm_calculation.models import infinity_model
    infinity_model_instance = infinity_model.get_obj()
    minimum_purchase_in_redeeming_month = 0
    if infinity_model_instance:
        minimum_purchase_in_redeeming_month = infinity_model_instance.minimum_purchase_in_redeeming_month
    if last_month_consistent_retailer_incomes.exists():
        consistent_retailer_income = last_month_consistent_retailer_incomes.first()
        last_month_cri = consistent_retailer_income.cri_balance
    # if this_month_consistent_retailer_incomes.exists():
    #     consistent_retailer_income = this_month_consistent_retailer_incomes.first()
    #     current_month_cri = consistent_retailer_income.cri_earned
    try:
        o = Order.objects.filter(email=user.username,
                                 date__month=month_fn(),
                                 date__year=year_fn(),
                                 paid=True,
                                 delete=False).exclude(status=8)
        current_month_cri = sum([li.bv for li in o])
    except:
        current_month_cri = 0
    return {
        'current_month': str(current_month_cri),
        # 'current_month': '50',
        'last_month': str(last_month_cri),
        'min_purchase_in_redeeming_month': str(minimum_purchase_in_redeeming_month),
    }


def get_fmcg_cri_details_for(user):
    from mlm_calculation.models import consistent_retailers_income
    # this_month = datetime.today().replace(day=1)
    # # last_day_of_prev_month = this_month - timedelta(month=1)
    # last_month = this_month - timedelta(month=1)
    # # last_month = last_month.replace(day=1)
    last_month_consistent_retailer_incomes = consistent_retailers_income.objects.filter(user=user,
                                                                                        input_date__month=last_month_fn(),
                                                                                        input_date__year=last_year_fn(),
                                                                                        )
    this_month_consistent_retailer_incomes = consistent_retailers_income.objects.filter(user=user,
                                                                                        input_date__year=month_fn(),
                                                                                        input_date__month=year_fn(),
                                                                                        )
    last_month_cri = 0
    current_month_cri = 0
    last_month_earned_cri = 0
    from mlm_calculation.models import infinity_model
    infinity_model_instance = infinity_model.get_obj()
    minimum_purchase_in_redeeming_month = 0
    if infinity_model_instance:
        minimum_purchase_in_redeeming_month = infinity_model_instance.minimum_purchase_in_redeeming_month
    if last_month_consistent_retailer_incomes.exists():
        consistent_retailer_income = last_month_consistent_retailer_incomes.first()
        last_month_earned_cri =consistent_retailer_income.cri_earned
        last_month_cri = consistent_retailer_income.cri_balance
    # if this_month_consistent_retailer_incomes.exists():
    #     consistent_retailer_income = this_month_consistent_retailer_incomes.first()
    #     current_month_available_cri = consistent_retailer_income.cri_balance
    try:
        o = Order.objects.filter(email=user.username,
                                 date__month=month_fn(),
                                 date__year=year_fn(),
                                 paid=True,
                                 delete=False).exclude(status=8)
        current_month_cri = sum([li.bv for li in o])
    except:
        current_month_cri = 0
    eligible_cri_for_fmcg_sales = float(last_month_earned_cri) * .25
    eligible_cri_for_fmcg_sales = eligible_cri_for_fmcg_sales if eligible_cri_for_fmcg_sales < last_month_cri else last_month_cri
    print(eligible_cri_for_fmcg_sales, last_month_earned_cri, last_month_cri)
    return {
        # 'current_month': str(current_month_cri),
        'current_month': '50',
        'last_month': str(eligible_cri_for_fmcg_sales),
        'min_purchase_in_redeeming_month': str(minimum_purchase_in_redeeming_month),
    }


@csrf_exempt
def get_user_info(request):
    user_email = request.POST.get('user_id')
    user = User.objects.get(email=user_email)
    return HttpResponse(json.dumps(get_cri_details_for(user)),
                        content_type='application/json')


@csrf_exempt
def get_user_info_for_fmcg_sale(request):
    user_email = request.POST.get('user_id')
    user = User.objects.get(email=user_email)
    return HttpResponse(json.dumps(get_fmcg_cri_details_for(user)),
                        content_type='application/json')


@user_passes_test(is_distributor, login_url='D_login')
def distributor_delete_loyalty_sale(request, myid):
    sale = Distributor_Sale.objects.get(pk=myid)
    today = datetime.now().date()
    if sale.created_on != today:
        messages.warning(request, 'You are not able to delete this records')
        return redirect('distributor_loyalty_sale_list')
    if sale.sale_user_id != request.user:
        messages.warning(request, 'You are not able to delete this records')
        return redirect('distributor_loyalty_sale_list')
    # sale_items = Distributor_Sale_itemDetails.objects.filter(sale=sale)
    #
    # # Updating Distributor Quantity
    # for i in sale_items:
    #     distributor_batch = Distributor_Batch.objects.get(batch=i.batch,
    #                                                       distributor_material_center=sale.material_center)
    #     update_time_batch_quantity = int(distributor_batch.quantity) + int(i.quantity)
    #     Distributor_Batch.objects.filter(pk=distributor_batch.pk).update(quantity=update_time_batch_quantity)
    #     today = datetime.now().date()
    #     update_time_inventry = Distributor_Inventry.objects.get(created_on=today, product=i.item,
    #                                                             batch=i.batch, material_center=sale.material_center)
    #     update_time_inventry_current_quantity = int(update_time_inventry.current_quantity) + int(i.quantity)
    #     update_time_inventry_quantity_out = int(update_time_inventry.quantity_out) - int(i.quantity)
    #     Distributor_Inventry.objects.filter(pk=update_time_inventry.pk).update(
    #         current_quantity=update_time_inventry_current_quantity,
    #         quantity_out=update_time_inventry_quantity_out)

    # Marking Distributor Sale as Delete
    sale_delete = Distributor_Sale.objects.filter(pk=myid).update(delete=True)
    # Marking Shop Order Sale as Delete & zeroing bv & pv.
    shop_sale_delete = Order.objects.filter(pk=sale.order.id).update(delete=True, modified=True, bv=0, pv=0)
    # order_data = Order.objects.get(pk=sale.order.id)
    # user = User.objects.get(email=order_data.email)
    # handle_cri_consumed_record(user, 0, order_data.consumed_cri)

    # AG :: Now we will run CRI calculation and Inventory Updation function
    # AG :: Re-calculating Distributor's Quantity
    sale_items = Distributor_Sale_itemDetails.objects.filter(sale=sale)
    # Updating Distributor Quantity
    for i in sale_items:
        calculate_distributor_inventory(product=i.item,
                                        batch=i.batch,
                                        material_center=i.sale.material_center,
                                        quantity=0
                                        )
    # AG :: Recalculating Advisor's CRI
    user = User.objects.get(email=sale.order.email)
    initial_cri, consumed_cri, available_cri = cri_validation_fn(request, user)

    messages.success(request, "Record deleted successfully!")

    return redirect('distributor_loyalty_sale_list')
