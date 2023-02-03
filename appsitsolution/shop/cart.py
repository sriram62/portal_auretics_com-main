from django.shortcuts import get_object_or_404
from django.db.models import Q, Sum, Count
from .models import CartItem, Product, Ship_Charge
from shop.order_id import check_quantity
from .templatetags.shop_tag import *
from .utils import is_eligible_for_loyalty_purchase
from datetime import datetime
from mlm_admin.templatetags.template_tag import bussiness_value_calculation, point_value, distributor_in_tax, \
    distributor_ex_tax
from django.contrib import messages


def _cart_id(request):
    if 'cart_id' not in request.session:
        request.session['cart_id'] = _generate_cart_id()
    return request.session['cart_id']


def _generate_cart_id():
    import string, random
    return ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(50)])


def get_all_cart_items(request, for_total=False, warehouse_cart=False):
    items = CartItem.objects.filter(cart_id=_cart_id(request))
    if request.user.is_authenticated:
        if 'cart_warehouse_{}'.format(request.user.id) in request.session:
            cart_items = request.session['cart_warehouse_{}'.format(request.user.id)]
            if not warehouse_cart:
                items = items.exclude(id__in=cart_items)
    items = recalculate_cart(items)
    return items


def get_all_cart_items_pv(request, for_total=False, warehouse_cart=False):
    if for_total == False:
        items = CartItem.objects.filter(cart_id=_cart_id(request))
    else:
        items = CartItem.objects.filter(cart_id=_cart_id(request), in_stock=True)
    if request.user.is_authenticated:
        if 'cart_warehouse_{}'.format(request.user.id) in request.session:
            cart_items = request.session['cart_warehouse_{}'.format(request.user.id)]
            if not warehouse_cart:
                items = items.exclude(id__in=cart_items)
    from django.db.models import Sum
    return items.aggregate(total_pv=Sum('point_value')).get('total_pv') or 0


def add_item_to_cart(request):
    # cart_id = _cart_id(request)
    product_id = request.form_data['product_id']
    quantity = request.form_data['quantity']
    group_checkout_users = 'group_checkout_users_{}'.format(request.user.id)
    is_group_checkout = group_checkout_users in request.session
    user = request.form_data['user']
    p = get_object_or_404(Product, id=product_id)

    def price_according_batch(product):
        response = j.mrp_according_batch(product)
        return response
        # today = datetime.now().date()
        # if product.expiration_dated_product == 'YES':
        #     data = product.batch_set.filter(delete=False, date_of_expiry__gte=today).order_by(
        #         "date_of_expiry")[0:1]
        #     # data = product.batch_set.filter(delete=False, date_of_expiry__gte=today).order_by("date_of_expiry")[0:1]
        # else:
        #     # data = product.batch_set.filter(delete=False).order_by("date_of_expiry")[0:1]
        #     data = product.batch_set.filter(delete=False).order_by("date_of_expiry")[0:1]
        # mrp = 0
        # print('data', data)
        # for i in data:
        #     if i.mrp == None:
        #         i.mrp = 0
        #     mrp = i.mrp
        # return mrp

    def discount_price_according_batch(product):
        mrp = j.mrp_according_batch(product)
        # today = datetime.now().date()
        # if product.expiration_dated_product == 'YES':
        #     data = product.batch_set.filter(delete=False, date_of_expiry__gte=today).order_by(
        #         # data = product.batch_set.filter(delete=False, date_of_expiry__gte=today).order_by(
        #         "date_of_expiry")[0:1]
        # else:
        #     # data = product.batch_set.filter(delete=False).order_by("date_of_expiry")[0:1]
        #     data = product.batch_set.filter(delete=False, ).order_by("date_of_expiry")[0:1]
        # mrp = 0
        # print('data', data)
        # for i in data:
        #     if i.mrp == None:
        #         i.mrp = 0
        #     mrp = i.mrp
        discount_price = product.distributor_price
        if discount_price == None:
            discount_price = 0
        distributor_price_amount = float(mrp) / ((100 + discount_price) / 100)
        distributor_price_amount = round(distributor_price_amount, 2)
        return distributor_price_amount

    # <-----------------------------------------------------------to discount  price accordingly batch 28 feb price  ------------------------------------------------------->

    price = price_according_batch(p)
    discount_price = discount_price_according_batch(p)
    # adding code for pv and bv Start code here
    pv = point_volue(p)
    bv = business_volue(p)
    is_loyalty_purchase = request.session[
                              'can_use_loyalty_purchase'] or False  # this is true only if the user has enabled loyalty purchase and is eligible
    # adding code for pv and bv End code here
    if is_group_checkout:
        cart_items = CartItem.objects.filter(user_id=user.id, in_stock=True)
        cart_items = recalculate_cart(cart_items)
        item_in_cart = False
        for cart_item in cart_items:
            if cart_item.product_id == product_id:
                cart_item.update_quantity(quantity)
                item_in_cart = True
        if not item_in_cart:
            item = CartItem(
                user=user,
                cart_id=_cart_id(request),
                price=price,
                discount_price=discount_price,
                quantity=quantity,
                product_id=product_id,
                business_value=bv,
                point_value=pv,
                is_loyalty_purchase_cart=is_loyalty_purchase
            )
            # item.cart_id = cart_id
            item.save()

    elif request.user.pk:
        cart_items = get_all_cart_items(request)
        item_in_cart = False
        for cart_item in cart_items:
            if cart_item.product_id == product_id and cart_item.is_loyalty_purchase_cart == is_loyalty_purchase:
                cart_item.update_quantity(quantity)
                # cart_item.save()
                item_in_cart = True
        if not item_in_cart:
            item = CartItem(
                user=request.user,
                cart_id=_cart_id(request),
                price=price,
                discount_price=discount_price,
                quantity=quantity,
                product_id=product_id,
                business_value=bv,
                point_value=pv,
                is_loyalty_purchase_cart=is_loyalty_purchase

            )
            # item.cart_id = cart_id
            item.save()
    else:
        item = CartItem(
            user=request.user,
            cart_id=_cart_id(request),
            price=price,
            discount_price=discount_price,
            quantity=quantity,
            product_id=product_id,
            business_value=bv,
            point_value=pv,
            is_loyalty_purchase_cart=is_loyalty_purchase

        )
        # item.cart_id = cart_id
        item.save()


def item_count(request):
    return get_all_cart_items(request).count()


def get_group_items(request, for_total, group_cart, group_user):
    '''
    Note: This function called sub functions:
        get_group_user_cart_items &
        get_all_cart_items
    which cause issues with the recalculate_cart function.
    '''
    cart_item = []
    group_checkout_users = 'group_checkout_users_{}'.format(request.user.id)
    is_group_checkout = group_checkout_users in request.session
    if group_user:
        cart_item = get_group_user_cart_items(group_user)
    elif group_cart:
        users = [request.user.id]
        group_checkout_users = 'group_checkout_users_{}'.format(request.user.id)
        if group_checkout_users in request.session:
            users.extend(request.session[group_checkout_users])
        cart_item = get_group_user_cart_items(users)
    elif is_group_checkout:
        cart_item = get_all_cart_items(request, for_total)
    elif not is_group_checkout:
        cart_item = CartItem.objects.filter(user_id=request.user.id, in_stock=True)
    else:
        cart_item = get_all_cart_items(request, for_total)
    # cart_item = recalculate_cart(cart_item)
    return cart_item


def subtotal(request, for_total=False, group_cart=False, group_user=None):
    cart_item = get_group_items(request, for_total, group_cart, group_user)
    sub_total = 0

    for item in cart_item:
        if item.is_loyalty_purchase_cart:
            continue
        sub_total += item.total_cost()
    return sub_total


def loyalty_subtotal(request, for_total=False, group_cart=False, group_user=None):
    cart_item = get_group_items(request, for_total, group_cart, group_user)
    sub_total = 0

    for item in cart_item:
        if not item.is_loyalty_purchase_cart:
            continue
        sub_total += item.total_cost()
    return sub_total


def subtotal_bv(request, for_total=False, group_cart=False, group_user=None):
    cart_item = get_group_items(request, for_total, group_cart, group_user)
    sub_bv = 0
    for item in cart_item:
        if item.is_loyalty_purchase_cart:
            continue
        sub_bv += item.total_bv()

    return sub_bv


def subtotal_pv(request, for_total=False, group_cart=False, group_user=None):
    cart_item = get_group_items(request, for_total, group_cart, group_user)
    sub_pv = 0
    for item in cart_item:
        if item.is_loyalty_purchase_cart:
            continue
        sub_pv += item.total_pv()
    return round(sub_pv, 2)


def delete_loyalty_items(request, for_total=False, group_cart=False, group_user=None):
    cart_item = get_group_items(request, for_total, group_cart, group_user)
    for item in cart_item:
        if item.is_loyalty_purchase_cart:
            item.delete()


def a_subtotal(request, for_total=False, group_cart=False, group_user=None):
    cart_item = get_group_items(request, for_total, group_cart, group_user)
    a_sub_total = 0
    for item in cart_item:
        if item.is_loyalty_purchase_cart:
            continue
        a_sub_total += item.total_discount_cost()

    return a_sub_total


def a_loyalty_subtotal(request, for_total=False, group_cart=False, group_user=None):
    cart_item = get_group_items(request, for_total, group_cart, group_user)
    a_sub_total = 0
    for item in cart_item:
        if not item.is_loyalty_purchase_cart:
            continue
        a_sub_total += item.total_cost()
    return a_sub_total


def remove_item(request):
    item_id = request.POST.get('item_id')
    ci = get_object_or_404(CartItem, id=item_id)
    ci.delete()


def update_item(request):
    item_id = request.POST.get('item_id')
    quantity = request.POST.get('quantity')
    ci = get_object_or_404(CartItem, id=item_id)
    add_or_not = check_quantity(ci.product, int(float(quantity)))

    if quantity.isdigit() and add_or_not:
        quantity = int(float(quantity))
        ci.quantity = quantity
        ci.save()


def clear(request, user_id=None):
    cart_items = get_all_cart_items(request, for_total=True)
    cart_items.delete()
    if user_id:
        group_checkout_users = 'group_checkout_users_{}'.format(user_id)
        if group_checkout_users in request.session:
            users = request.session[group_checkout_users]
            get_group_user_cart_items(users).delete()
            del request.session[group_checkout_users]


def order_grand_total(grand_total, distributor_id=None):
    if distributor_id:
        return grand_total
    shiping_qs = Ship_Charge.objects.last()
    minimum_amount = float(shiping_qs.minimum_amount)
    grand_total = float(grand_total)
    if grand_total <= minimum_amount:
        grand_total = grand_total + float(shiping_qs.shiping_charge)
    grand_total = round(grand_total, 2)
    return grand_total


def shiping_charge_add(grand_total):
    shiping_qs = Ship_Charge.objects.last()
    minimum_amount = float(shiping_qs.minimum_amount)
    grand_total = float(grand_total)
    if grand_total <= minimum_amount:
        shiping_charge = shiping_qs.shiping_charge
    else:
        shiping_charge = 0
    return shiping_charge


def clear_Cart(request, warehouse_cart=False):
    cart_items = get_all_cart_items(request, warehouse_cart=warehouse_cart)
    if warehouse_cart and request.user.is_authenticated:
        if 'cart_warehouse_{}'.format(request.user.id) in request.session:
            warehouse_items = request.session['cart_warehouse_{}'.format(request.user.id)]
            cart_items = cart_items.exclude(id__in=warehouse_items)
            del request.session['cart_warehouse_{}'.format(request.user.id)]
    cart_items.delete()


def get_group_user_cart_items(users):
    # items = CartItem.objects.filter(user__id__in=users, in_stock=True)
    items = CartItem.objects.filter(user__id__in=users)
    items = recalculate_cart(items)

    return items


def recalculate_cart(cart_qs, request=False, loyalty=False):
    cart_qs_pk = []

    # AG :: Get only distinct cart items decreasing order of date.
    cart_qs_dist = cart_qs.order_by('-date_added').order_by('product').distinct('product')

    # AG :: remove unwanted cart_items from the table also
    cart_qs_old_remove = cart_qs.exclude(id__in=cart_qs_dist).delete()

    for i in cart_qs_dist:
        if i.product.expiration_dated_product == 'YES':
            batch = Batch.objects.filter(product=i.product, delete=False,
                                         date_of_expiry__gte=datetime.now()).order_by('date_of_expiry')
        else:
            batch = Batch.objects.filter(product=i.product, delete=False, )

        batch_with_inventory = []

        material = Material_center.objects.get(frontend=True)
        if request:
            if request.user.is_authenticated:
                # get the material center if distributor is selected if not then c&f state wise
                if "distributor_checkout" in request.session:
                    material = Material_center.objects.get(id=request.session['distributor_checkout'])
                else:
                    material = request.user.profile.get_related_mc()

        for b in batch:
            inventory = Inventry.objects.filter(batch=b,
                                                material_center=material,
                                                created_on=datetime.today())  # .latest('created_on')
            if inventory:
                inventory = inventory.first()
                if inventory.current_quantity >= 1:
                    batch_with_inventory.append(b.pk)
                    break

        batchs = Batch.objects.filter(pk__in=batch_with_inventory)

        if batchs:
            batch = batchs.first()
        else:
            continue

        max_qty = Inventry.objects.get(batch=batch,
                                       material_center=material,
                                       created_on=datetime.today()).current_quantity

        if i.quantity > max_qty:
            i.quantity = max_qty

        if i.is_loyalty_purchase_cart:
            bv = 0
            pv = 0
            dp_ex_tax = batch.mrp
            dp_in_tax = batch.mrp
        else:
            bv = bussiness_value_calculation(batch.mrp, i.product.distributor_price, i.product.igst,
                                             i.product.business_value)
            pv = point_value(batch.mrp, i.product.distributor_price, i.product.igst,
                             i.product.point_value)
            dp_ex_tax = distributor_ex_tax(batch.mrp, i.product.distributor_price, i.product.igst)
            dp_in_tax = distributor_in_tax(batch.mrp, i.product.distributor_price)

        if request:
            if request.user.is_authenticated:
                price = dp_in_tax
            else:
                price = batch.mrp
        else:
            price = dp_in_tax

        newcart = CartItem.objects.filter(pk=i.pk).update(business_value=bv,
                                                          point_value=pv,
                                                          discount_price=dp_in_tax,
                                                          price=price, )
        cart_qs_pk.append(i.pk)

    final_cart_qs = CartItem.objects.filter(pk__in=cart_qs_pk)

    if request:
        if len(cart_qs) != len(final_cart_qs):
            messages.warning(request, 'Few items were removed from the cart as they went Out of Stock.')

    return final_cart_qs
