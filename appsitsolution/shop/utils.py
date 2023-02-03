from datetime import timedelta

from django.utils import timezone

from distributor.models import Distributor_Inventry
from mlm_admin.models import Inventry
from shop.models import Product, Batch, Material_center, CartItem
from pyjama import j


def get_products_for(category_name, mc):
    products_in_category = Product.objects.filter(category__cat_name=category_name,
                                                  # batch__date_of_expiry__gte=today,       # AG: Removed as non-expired items were not showing
                                                  batch__delete=False,
                                                  delete=False)
    # latest_inventory_date = Inventry.objects.filter(material_center=mc).latest('created_on').created_on
    # product_ids = Inventry.objects.filter(product__in=products_in_category, material_center=mc,
    #                                         current_quantity__gte = 1).values_list('product_id', flat=True)
    # return Product.objects.filter(id__in=product_ids)
    return price_product(products_in_category, aa='1', material=mc)


def get_products_for_mc(mc, request=None):
    is_loyalty_purchase_enabled = request.session.get('loyalty_purchase_enabled', False)
    products_in_category = Product.objects.filter(batch__delete=False,
                                                  # batch__quantity__gte=1,
                                                  delete=False).exclude(expiration_dated_product="YES",
                                                                        batch__date_of_expiry__lt=j.today_fn(), )
    if is_loyalty_purchase_enabled and is_eligible_for_loyalty_purchase(request):
        products_in_category = products_in_category.filter(loyalty_purchase='YES')
    return price_product(products_in_category, aa='1', material=mc)


def check(checkdata):
    if checkdata.expiration_dated_product == 'YES':
        data = checkdata.batch_set.filter(delete=False, date_of_expiry__gte=j.today_fn()).order_by(
            "date_of_expiry")[0:1]
    else:
        data = checkdata.batch_set.filter(delete=False).order_by("date_of_expiry")[0:1]
    mrp = 0
    for i in data:
        if i.mrp == None:
            i.mrp = 0
        mrp = i.mrp
    mrp = "{:.2f}".format(mrp)
    return mrp


def get_batch(product, material, distributor_checkout):
    """
    We will take product and find whether it is expiring product or not. (i.e. perishable or not)
    if expiring:
        We have to take the batch that has not expired
        We will further find whether the current material center has that batch in stock or not
        We will take the batch which is expiring first.
    else:
        We will filter the batches that has quantity in the current material.
        We will take the first batch.
    """
    response = j.usable_batches(product, material, distributor_checkout)
    return response

    # batchs = Batch.objects.filter(product=product, delete=False)
    # # products =(LineItem.objects.filter(date_added__range=["2022-01-01","2022-02-02"]).values('product').order_by('product').annotate(total_qty=Sum('quantity')))
    # # print(products)
    # if product.expiration_dated_product == 'YES':
    #     batchs = batchs.filter(date_of_expiry__gte=today).order_by('date_of_expiry')
    # else:
    #     batchs = batchs.order_by('pk')
    #
    # final_batches = []
    # for batch in batchs:
    #     try:
    #         if not distributor_checkout:
    #             inventory = Inventry.objects.filter(product=product,
    #                                                 batch=batch,
    #                                                 material_center=material,
    #                                                 created_on__gte=j.day_before_today_fn(),
    #                                                 current_quantity__gte=1).latest('created_on')
    #         else:
    #             inventory = Distributor_Inventry.objects.filter(product=product,
    #                                                             batch=batch,
    #                                                             material_center=material,
    #                                                             created_on__gte=j.day_before_today_fn(),
    #                                                             current_quantity__gte=1).latest('created_on')
    #
    #         if inventory:
    #             final_batches.append(batch)
    #
    #     except:
    #         pass
    # if len(final_batches) > 0:
    #     batch = final_batches[0]
    # else:
    #     batch = False
    # return batch

def check_any_inventory(distributor_checkout, material, check=False):
    try:
        if not distributor_checkout:
            any_inventory = Inventry.objects.filter(material_center=material,
                                                    created_on__gte=j.today_fn(), ).latest('created_on')
        else:
            any_inventory = Distributor_Inventry.objects.filter(material_center=material,
                                                                created_on__gte=j.today_fn(), ).latest('created_on')
        if any_inventory:
            any_inventory = True
        else:
            any_inventory = False
    except Exception as e:
        any_inventory = False

    if not check:
        if not any_inventory:
            from mlm_admin.cron_jobs import update_inventry
            update_inventry()
            check_any_inventory(distributor_checkout, material, check=True)

    return any_inventory


def price_product(products, aa=1, material=None):
    distributor_checkout = False
    if material:
        if material.advisory_owned == "YES":
            distributor_checkout = True

    latestproducts = []
    price = []
    if not material:
        material = Material_center.objects.filter(frontend=True).first()
    any_inventory = check_any_inventory(distributor_checkout, material)

    for product in products:
        batch = get_batch(product, material, distributor_checkout)
        price2 = price.copy()
        if not distributor_checkout:
            inventory = Inventry.objects.filter(batch=batch,
                                                # product=product,
                                                material_center=material,
                                                # created_on__gte=j.day_before_today_fn(),
                                                # current_quantity__gte=1
                                                )#.latest('created_on')
        else:
            inventory = Distributor_Inventry.objects.filter(batch=batch,
                                                            # product=product,
                                                            material_center=material,
                                                            # created_on__gte=j.day_before_today_fn(),
                                                            # current_quantity__gte=1
                                                            )#.latest('created_on')
        if inventory:
            inventory = inventory.latest('created_on')

        # Added by AG for showing products in case cron is not running.
        if not inventory:
            if not any_inventory:
                if not distributor_checkout:
                    inventory = Inventry.objects.filter(product=product,
                                                        # batch=batch, # AG :: Commented because get_batch always show result if batch is in stock.
                                                        material_center=material,
                                                        current_quantity__gte=1).latest('created_on')
                else:
                    inventory = Distributor_Inventry.objects.filter(product=product,
                                                                    # batch=batch,
                                                                    material_center=material,
                                                                    current_quantity__gte=1).latest(
                        'created_on')

        # Check whether product is in stock or not
        if inventory:
            if inventory.current_quantity >= 1:
                price_check = float(check(product))
                if len(latestproducts) == 0:
                    latestproducts.append(product.pk)
                    price.append(price_check)
                elif aa == '1':
                    ln = len(price2) - 1
                    last_price = 0
                    for i, j in enumerate(price2):
                        if price_check <= j:
                            latestproducts.insert(i, product.pk)
                            price.insert(i, price_check)
                            break
                        elif ln == i and price_check > j:
                            latestproducts.append(product.pk)
                            price.append(price_check)
                elif aa == '2':
                    ln = len(price2) - 1
                    last_price = 0
                    for i, j in enumerate(price2):
                        if price_check >= j:
                            latestproducts.insert(i, product.pk)
                            price.insert(i, price_check)
                            break
                        elif ln == i and price_check < j:
                            latestproducts.append(product.pk)
                            price.append(price_check)
        # except Exception as e:
        #     pass
    return Product.objects.filter(id__in=latestproducts)  # we need a queryset therefore


def validate_loyalty_cart(request, group_checkout=None):
    from . import cart
    from mlm_calculation.models import infinity_model
    infinity_model_instance = infinity_model.get_obj()
    minimum_purchase_in_redeeming_month = 0
    if infinity_model_instance:
        minimum_purchase_in_redeeming_month = infinity_model_instance.minimum_purchase_in_redeeming_month
    cart_amount_pv = cart.subtotal_pv(request, for_total=True, group_cart=group_checkout)
    loyalty_item_total = cart.loyalty_subtotal(request, for_total=True, group_cart=group_checkout)
    if cart_amount_pv < loyalty_item_total:
        empty_loyalty_cart(request, group_checkout)


def empty_loyalty_cart(request, group_checkout=None):
    from shop.cart import _cart_id
    CartItem.objects.filter(
        user=request.user,
        cart_id=_cart_id(request),
        is_loyalty_purchase_cart=True

    ).delete()


def is_eligible_for_loyalty_purchase(request, group_checkout=None):
    from . import cart
    from mlm_calculation.models import infinity_model
    validate_loyalty_cart(request, group_checkout)
    infinity_model_instance = infinity_model.get_obj()
    minimum_purchase_in_redeeming_month = 0
    if infinity_model_instance:
        minimum_purchase_in_redeeming_month = infinity_model_instance.minimum_purchase_in_redeeming_month
    cart_amount_pv = cart.subtotal_pv(request, for_total=True, group_cart=group_checkout)
    loyalty_item_total = cart.loyalty_subtotal(request, for_total=True, group_cart=group_checkout)
    has_crossed_maximum_amount = loyalty_item_total >= cart_amount_pv

    is_eligible = cart_amount_pv > minimum_purchase_in_redeeming_month
    can_use_loyalty_purchase = is_eligible and request.session.get(
        'loyalty_purchase_enabled') and not has_crossed_maximum_amount
    request.session[
        'remaining_loyalty_purchase_amount'] = round(float(cart_amount_pv) - float(loyalty_item_total),
                                                     2) if cart_amount_pv >= loyalty_item_total else 0
    request.session['is_eligible_for_loyalty_purchase'] = is_eligible
    request.session['can_use_loyalty_purchase'] = can_use_loyalty_purchase
    request.session['cart_total_pv'] = cart_amount_pv
    # print('minimum_purchase_in_redeeming_month', minimum_purchase_in_redeeming_month, 'cart pv', cart_amount_pv,
    #       'cart loyalty amount', loyalty_item_total, 'can user lp', can_use_loyalty_purchase,
    #       'can_use_loyalty_purchase', can_use_loyalty_purchase)
    return can_use_loyalty_purchase


def has_enough_pv_to_enable_loyalty_purchase(request, group_checkout=None):
    from . import cart
    from mlm_calculation.models import infinity_model
    infinity_model_instance = infinity_model.get_obj()
    minimum_purchase_in_redeeming_month = 0
    if infinity_model_instance:
        minimum_purchase_in_redeeming_month = infinity_model_instance.minimum_purchase_in_redeeming_month
    cart_amount_pv = cart.subtotal_pv(request, for_total=True, group_cart=group_checkout)
    loyalty_item_total = cart.loyalty_subtotal(request, for_total=True, group_cart=group_checkout)

    has_crossed_maximum_amount = loyalty_item_total >= cart_amount_pv

    is_eligible = cart_amount_pv > minimum_purchase_in_redeeming_month
    can_use_loyalty_purchase = is_eligible and request.session.get(
        'loyalty_purchase_enabled') and not has_crossed_maximum_amount
    request.session[
        'remaining_loyalty_purchase_amount'] = round(float(cart_amount_pv) - float(loyalty_item_total),
                                                     2) if cart_amount_pv >= loyalty_item_total else 0
    request.session['is_eligible_for_loyalty_purchase'] = is_eligible
    request.session['can_use_loyalty_purchase'] = can_use_loyalty_purchase
    request.session['cart_total_pv'] = cart_amount_pv

    print('Can use loyalty purchase value', can_use_loyalty_purchase)
    return is_eligible
