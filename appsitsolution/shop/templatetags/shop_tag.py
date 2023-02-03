from django import template
from shop.models import *
from mlm_admin.models import *
from distributor.models import Distributor_Inventry
from shop.utils import get_batch
from django.utils.safestring import SafeData, SafeString, mark_safe

register = template.Library()
from mlm_admin.templatetags.template_tag import dis_price_exclude_tax
from datetime import datetime, date
from pyjama import j

@register.simple_tag()
def check(checkdata):
    data = j.usable_batches(checkdata)
    if data:
        mrp = data.mrp
        mrp = "{:.2f}".format(mrp)
    else:
        mrp = 0.0
    return mrp

@register.simple_tag()
def check1(checkdata):
    myid = checkdata['id']
    product = Product.objects.get(pk=myid)
    today = datetime.now().date()
    data = hide_product(product)
    mrp = 0
    for i in data:
        if i.mrp == None:
            i.mrp = 0
        mrp = i.mrp
    return mrp


@register.simple_tag()
def dis_price_include_tax(product):
    mrp = check(product)
    mrp = float(mrp)
    distributor_price = float(product.distributor_price)
    distributor_price_amount = mrp / ((100 + distributor_price) / 100)
    distributor_price_amount = round(distributor_price_amount, 2)
    distributor_price_amount = "{:.2f}".format(distributor_price_amount)
    return distributor_price_amount


@register.simple_tag()
def dis_price_include_tax1(product):
    mrp = check1(product)
    mrp = float(mrp)
    distributor_price = float(product['distributor_price'])
    distributor_price_amount = mrp / ((100 + distributor_price) / 100)
    distributor_price_amount = round(distributor_price_amount, 2)
    return distributor_price_amount


@register.simple_tag()
def category(request):
    category = Category.Object.filter(delete=False, is_parent_category='yes')


@register.simple_tag
def leftproductad():
    # product_add = advertisements.objects.filter(image__gte=one_week_ago).filter(ad_location='L').filter(active="1").filter(ad_type='Productad')
    category = Category.objects.filter(delete=False, is_parent_category='yes')
    left_ad = '<ul class="sub-menu mega-menu mega-menu-column-4 ecom_head_shubh">'
    for i in category:
        if i.delete == False:
            left_ad += '<li><a href="javascript:void(0)" class="mega-column-title">i.cat_name</a><ul class="mega-sub-menu">'
            for k in i.category_set.all:
                if k.delete == False:
                    left_ad += '<li><a href="/category/' + i.cat_name + '/' + k.cat_name + '>' + k.cat_name + '</a></li>'

        left_ad += '</ul></li>'
    return mark_safe(left_ad)


@register.filter
def sort_by(queryset, order):
    return queryset.order_by(order)


@register.simple_tag
def grand_total(order_list):
    grand_amount = 0
    for i in order_list:
        grand_amount = i.order.grand_total
    return grand_amount


@register.filter
def sort_of_error(queryset, order):
    today = date.today()
    unique_variant_list = []
    mc = Material_center.objects.filter(frontend=True)[0]
    distributor_checkout = False
    for i in queryset:
        get_batch(i.product, mc, distributor_checkout)
        # batch = Batch.objects.filter(product=i.product, delete=False, quantity__gte=1).order_by(
        #     "date_of_expiry")
        # batchs = batch.filter(date_of_expiry__gte=today)
        # batch = batchs.first()
        try:
            batch = Batch.objects.get(pk=batch.pk)
            # material = Material_center.objects.get(frontend=True)
            inventory = Inventry.objects.filter(product=i.product, batch=batch, material_center=mc).latest(
                'created_on')
            if inventory.current_quantity >= 1:
                if i.variant_based_on not in unique_variant_list:
                    unique_variant_list.append(i.variant_based_on)
        except:
            pass
    return unique_variant_list


@register.simple_tag
def total_of_particular_iteam_price(price, quantity):
    total = float(price) * float(quantity)
    total = "{:.2f}".format(total)
    return total


@register.filter()
def hide_product(products):
    try:
        mc = products.mc
    except:
        mc = Material_center.objects.filter(frontend=True)[0]
    try:
        distributor_checkout = products.distributor_checkout
    except:
        distributor_checkout = False
    today = date.today()
    latestproducts = []
    for product in products:
        batch = get_batch(product, mc, distributor_checkout)
        # batch = Batch.objects.filter(product=product, delete=False).order_by(
        #     "date_of_expiry")
        #
        # batchs = batch.filter(date_of_expiry__gte=today)
        # batch = batchs.first()
        try:
            batch = Batch.objects.get(pk=batch.pk)
            # material = mc # Material_center.objects.get(frontend=True)
            inventory = Inventry.objects.filter(product=product, batch=batch, material_center=mc).latest(
                'created_on')
            if inventory.current_quantity >= 1:
                latestproducts.append(product)
        except:
            pass
    return latestproducts


@register.filter()
def hide_product_detail(products):
    try:
        mc = products.mc
    except:
        mc = Material_center.objects.filter(frontend=True)[0]
    try:
        distributor_checkout = products.distributor_checkout
    except:
        distributor_checkout = False

    today = date.today()
    latestproducts = []
    for k in products:
        batch = get_batch(k.product, mc, distributor_checkout)
        # batch = Batch.objects.filter(product=k.product, delete=False, quantity__gte=1).order_by(
        #     "date_of_expiry")
        # batchs = batch.filter(date_of_expiry__gte=today)
        # batch = batchs.first()
        try:
            batch = Batch.objects.get(pk=batch.pk)
            # material = Material_center.objects.get(frontend=True)
            inventory = Inventry.objects.filter(product=k.product, batch=batch, material_center=mc).latest(
                'created_on')
            if inventory.current_quantity >= 1:
                latestproducts.append(k)
        except:
            pass

    return latestproducts


@register.simple_tag
def ship_charge_check():
    shiping_qs = Ship_Charge.objects.last()
    return shiping_qs.minimum_amount


@register.simple_tag
def shiping_fee_check(subtotal=0):
    shiping_qs = Ship_Charge.objects.last()
    minimum_amount = float(shiping_qs.minimum_amount)
    if subtotal == '':
        subtotal = 0
    subtotal = float(subtotal)
    if minimum_amount < subtotal:
        data = 0.00
        data = "{:.2f}".format(data)
        return data
    shipping_change = round(shiping_qs.shiping_charge, 2)
    shipping_charge = "{:.2f}".format(shipping_change)
    return shipping_charge


@register.simple_tag
def add_ship_charge_n_user(subtotal):  # Here User is not authenticated
    shiping_qs = Ship_Charge.objects.last()
    subtotal = float(subtotal)
    subtotal = subtotal + float(shiping_qs.shiping_charge)
    subtotal = round(subtotal, 2)
    subtotal = "{:.2f}".format(subtotal)
    return subtotal


@register.simple_tag
def add_ship_charge_a_user(subtotal):  # Here User is Authenticated
    shiping_qs = Ship_Charge.objects.last()
    minimum_amount = float(shiping_qs.minimum_amount)
    subtotal = float(subtotal)
    if minimum_amount > subtotal:
        subtotal = subtotal + float(shiping_qs.shiping_charge)
    subtotal = round(subtotal, 2)
    subtotal = "{:.2f}".format(subtotal)
    return subtotal


@register.filter()
def price_product(products, aa):
    try:
        mc = products.mc
    except:
        mc = Material_center.objects.filter(frontend=True)[0]
    try:
        distributor_checkout = products.distributor_checkout
    except:
        distributor_checkout = False

    today = date.today()
    latestproducts = []
    price = []
    for product in products:
        batch = get_batch(product, mc, distributor_checkout)
        # batchs = Batch.objects.filter(product=product, delete=False, quantity__gte=1).order_by(
        #     "date_of_expiry")
        # if product.expiration_dated_product == 'YES':
        #     batchs = batchs.filter(date_of_expiry__gte=today)
        # batch = batchs.first()
        price2 = price.copy()
        try:
            batch = Batch.objects.get(pk=batch.pk)
            material = Material_center.objects.get(frontend=True)
            inventory = Inventry.objects.filter(product=product, batch=batch, material_center=material).latest(
                'created_on')
            if inventory.current_quantity >= 1:
                price_check = float(check(product))
                if len(latestproducts) == 0:
                    latestproducts.append(product)
                    price.append(price_check)
                elif aa == '1':
                    ln = len(price2) - 1
                    last_price = 0
                    for i, j in enumerate(price2):
                        if price_check <= j:
                            latestproducts.insert(i, product)
                            price.insert(i, price_check)
                            break
                        elif ln == i and price_check > j:
                            latestproducts.append(product)
                            price.append(price_check)
                elif aa == '2':
                    ln = len(price2) - 1
                    last_price = 0
                    for i, j in enumerate(price2):
                        if price_check >= j:
                            latestproducts.insert(i, product)
                            price.insert(i, price_check)
                            break
                        elif ln == i and price_check < j:
                            latestproducts.append(product)
                            price.append(price_check)
        except:
            pass
    return latestproducts

@register.filter()
def price_product_new(products, aa):
    today = date.today()
    latestproducts = []
    price = []
    for product in products:
        price2 = price.copy()
        try:
            price_check = float(check(product))
            if len(latestproducts) == 0:
                latestproducts.append(product)
                price.append(price_check)
            elif aa == '1':
                ln = len(price2) - 1
                last_price = 0
                for i, j in enumerate(price2):
                    if price_check <= j:
                        latestproducts.insert(i, product)
                        price.insert(i, price_check)
                        break
                    elif ln == i and price_check > j:
                        latestproducts.append(product)
                        price.append(price_check)
            elif aa == '2':
                ln = len(price2) - 1
                last_price = 0
                for i, j in enumerate(price2):
                    if price_check >= j:
                        latestproducts.insert(i, product)
                        price.insert(i, price_check)
                        break
                    elif ln == i and price_check < j:
                        latestproducts.append(product)
                        price.append(price_check)

        except:
            pass
    return latestproducts


@register.simple_tag
def maximum_product_qty(product, user=None, mc=False, distributor_checkout=False):
    today = date.today()
    batch = get_batch(product, mc, distributor_checkout)
    # batch = Batch.objects.filter(product=product, delete=False, quantity__gte=1).order_by(
    #     "date_of_expiry")
    # batchs = batch.filter(date_of_expiry__gte=today)
    # batch = batchs.first()
    material = False
    if user:
        if user.is_authenticated:
            material = user.profile.get_related_mc()
            # get the material center if distributor is selected if not then c&f state wise
            if material:
                material = Material_center.objects.get(id=mc)
    if not material:
        material = Material_center.objects.get(frontend=True)
    try:
        batch = Batch.objects.get(pk=batch.pk)
        if not distributor_checkout:
            inventory = Inventry.objects.filter(product=product,
                                                batch=batch,
                                                material_center=material).latest('created_on')
        else:
            inventory = Distributor_Inventry.objects.filter(product=product,
                                                batch=batch,
                                                material_center=material).latest('created_on')
        qty = inventory.current_quantity
    except:
        qty = 0
    return qty


@register.simple_tag
def get_gst_number():
    material = Material_center.objects.get(frontend=True)
    return material.gst_number


@register.simple_tag
def get_print_name():
    material = Material_center.objects.get(frontend=True)
    return material.print_name


@register.simple_tag
def material_center_address():
    material = Material_center.objects.get(frontend=True)
    return material.address


@register.simple_tag
def material_center_address_line_2():
    material = Material_center.objects.get(frontend=True)
    return material.address_line_2


@register.simple_tag
def material_center_phone_number():
    material = Material_center.objects.get(frontend=True)
    try:
        return material.advisor_registration_number.profile.phone_number
    except:
        return '1800 889 0360'


@register.simple_tag
def material_center_email():
    material = Material_center.objects.get(frontend=True)
    try:
        return material.advisor_registration_number.email
    except:
        return 'support@auretics.com'


@register.simple_tag
def material_center_city():
    material = Material_center.objects.get(frontend=True)
    return material.city


@register.simple_tag
def material_center_state():
    material = Material_center.objects.get(frontend=True)
    return material.state


@register.simple_tag
def material_center_mc_name():
    material = Material_center.objects.get(frontend=True)
    return material.mc_name


@register.simple_tag
def material_center_pin_code():
    material = Material_center.objects.get(frontend=True)
    return material.pin_code


@register.simple_tag()
def point_volue(product):
    mrp = check(product)
    mrp = float(mrp)
    value = dis_price_exclude_tax(mrp, product.distributor_price, product.igst)
    value = float(value)
    p_value = product.point_value
    actual_value = value * p_value / 100
    actual_value = round(actual_value, 2)
    actual_value = "{:.2f}".format(actual_value)
    return actual_value


@register.simple_tag()
def business_volue(product):
    mrp = check(product)
    mrp = float(mrp)
    value = dis_price_exclude_tax(mrp, product.distributor_price, product.igst)
    value = float(value)
    p_value = product.business_value
    actual_value = value * p_value / 100
    actual_value = round(actual_value, 2)
    actual_value = "{:.2f}".format(actual_value)
    return actual_value

@register.simple_tag()
def invoice_ex_tax(price, total_igst, quantity = None, quantity_multiply=None):
    if quantity == None:
        quantity = 1
    total_igst = float(total_igst) / float(quantity)
    price = float(price) - float(total_igst)
    if quantity_multiply:
        price = price * quantity_multiply
    price = "{:.2f}".format(price)
    return price
