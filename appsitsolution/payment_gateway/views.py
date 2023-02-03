import datetime
from django.shortcuts import render
from .ChecksumGenerator import Checksum
from portal_auretics_com import settings
from paywix.payu import Payu
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from shop.models import Payment, Order
from django.contrib.auth.models import User
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404, reverse
from django.contrib import messages
from .models import *


payu_config = settings.PAYU_CONFIG
merchant_key = payu_config.get('merchant_key')
merchant_salt = payu_config.get('merchant_salt')
surl = payu_config.get('success_url')
furl = payu_config.get('failure_url')
mode = payu_config.get('mode')
payu = Payu(merchant_key, merchant_salt, surl, furl, mode)


def payu_payment_gateway(request, whole_grand_total, group_checkout, orders):
    email = request.user.email
    firstname = request.user.profile.first_name
    lastname = request.user.profile.last_name
    phone = request.user.profile.phone_number
    # amount = o.grand_total
    amount = whole_grand_total
    cart_id = request.session['cart_id']
    order_ids = [order_obj.id for order_obj in orders]
    group_order_ids = 'order_ids_{}'.format(order_ids[0])
    if group_checkout:
        request.session[group_order_ids] = order_ids
    o_id = ''
    for order in order_ids:
        Order.objects.filter(pk=order)
        ord = Order.objects.filter(pk=order, name=request.user.username)
        for ordr in ord:
            o_id = ordr.id
    for order in order_ids:
        Order.objects.filter(pk=order).update(main_order=o_id)
    data = {
        'amount': amount, 'firstname': firstname,
        'email': email,
        'phone': phone, 'productinfo': 'Auretics Products', 'lastname': lastname, 'country': cart_id,
        # zipcode we are using to send autoincrement id of order table so that we get it in success and update the order paid
        'zipcode': orders[0].pk
    }

    user = request.user.referralcode

    txnid = str(orders[0].order_id1) + "-" + str(user) + "-" + str(datetime.now().hour) + str(
        datetime.now().minute)
    data.update({"txnid": txnid})
    payu_data = payu.transaction(**data)
    # Make sure the transaction ID is unique
    # payu_data = payu.transaction(**data)
    return render(request, 'payments/payu_checkout.html', {"posted": payu_data})
    # messages.add_message(request, messages.INFO, 'Order Placed!')
    # return redirect('order_summary')


def zaakpay_payment_gateway(request, whole_grand_total, orders, group_checkout):
    buyerEmail = request.user.email
    amount = int(whole_grand_total) * 100
    currency = "INR"
    merchantIdentifier = settings.ZAAKPAY_MERCHANT_IDENTIFIER
    returnUrl = settings.RETURN_URL
    user = request.user.referralcode
    orderId = str(orders[0].order_id1) + "-" + str(user) + "-" + str(datetime.now().hour) + str(
        datetime.now().minute)
    order_ids = [order_obj.id for order_obj in orders]
    orders_id = []
    o_id = ''
    for order in order_ids:
        Order.objects.filter(pk=order)
        ord = Order.objects.filter(pk=order, name=request.user.username)
        for ordr in ord:
            o_id = ordr.id
        orders_id.append(order)
    for order in order_ids:
        Order.objects.filter(pk=order).update(main_order=o_id)
    listToStr = '-'.join([str(elem) for elem in orders_id])
    product1Description = whole_grand_total

    product2Description = o_id
    # Make sure the order ID is unique

    product4Description = listToStr
    params = {"amount": amount, "merchantIdentifier": merchantIdentifier, "orderId": orderId,
              "currency": currency, "buyerEmail": buyerEmail, "returnUrl": returnUrl,
              "product1Description": product1Description, "product4Description":product4Description,
              "product2Description":product2Description}
    checksumString = Checksum.getChecksumString(params)
    checksum = Checksum.calculateChecksum(settings.ZAAKPAY_SECRET_KEY, checksumString)

    params['checksum'] = checksum

    return render(request, 'payments/zaakpay_checkout.html', {"posted": params})


# failure
def failure(request):
    return render(request, 'payment_failure.html')


razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))


def rozorpay_payment_gateway(request, whole_grand_total, orders, group_checkout):
    currency = 'INR'
    email = request.user.email
    firstname = request.user.profile.first_name
    lastname = request.user.profile.last_name
    phone = request.user.profile.phone_number
    username = str(firstname) + str(lastname)
    amount = int(whole_grand_total) * 100
    cart_id = request.session['cart_id']
    order_ids = [order_obj.id for order_obj in orders]
    group_order_ids = 'order_ids_{}'.format(order_ids[0])
    if group_checkout:
        request.session[group_order_ids] = order_ids
    order_id = ''
    for order in order_ids:
        ord = Order.objects.filter(pk=order, name=request.user.username)
        for ordr in ord:
            order_id = ordr.id
    for order in order_ids:
        Order.objects.filter(pk=order).update(main_order=order_id)
    # Create a Razorpay Order
    razorpay_order = razorpay_client.order.create(
        dict(amount=amount, currency=currency, receipt=str(order_id)))
    razorpay_order_id = razorpay_order['id']
    # Order.objects.filter(pk=order_id).update(razorpay_order_id=razorpay_order['id'])
    request.session['order_id'] = order_id
    callback_url = str(settings.SITE_URL) + '/razorpay_payment_success/'

    # we need to pass these details to frontend.
    context = {}
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
    context['razorpay_amount'] = amount
    context['currency'] = currency
    context['callback_url'] = callback_url
    context['phone'] = phone
    context['email'] = email
    context['name'] = firstname
    context['callback_url'] = callback_url
    context['username'] = username
    return render(request, 'payments/razorpay_checkout.html', context=context)

# Payu failure page
@csrf_exempt
def payu_failure(request):
    # cart = request.session['country']
    data = {k: v[0] for k, v in dict(request.POST).items()}
    response = payu.verify_transaction(data)
    pay_option = PaymentMode.objects.all().order_by('priority')
    second_priority = ''

    for index, item in enumerate(pay_option):
        if index == 1:
            second_priority = item
    second_id = second_priority

    if second_id:
        gateway_name = PaymentMode.objects.get(id=second_id.id)
        obj = PaymentMode.objects.values_list('priority').filter(id=second_id.id).last()
        gateway_name.priority = int(str(obj[0])) * -1
        gateway_name.save()
        order_id = data['zipcode']
        error_Message = data['error_Message']
        Order.objects.filter(pk=order_id).update(status=8)
        messages.add_message(request, messages.INFO, error_Message)
        return redirect('checkout')
    else:
        return render(request, 'payment_failure.html')

# zaakpay failure page
@csrf_exempt
def zaakpay_failure(request):
    # cart = request.session['country']
    data = {k: v[0] for k, v in dict(request.POST).items()}
    pay_option = PaymentMode.objects.all().order_by('priority')
    second_priority = ''

    for index, item in enumerate(pay_option):
        if index == 2:
            second_priority = item
    second_id = second_priority

    if second_id:
        gateway_name = PaymentMode.objects.get(id=second_id.id)
        obj = PaymentMode.objects.values_list('priority').filter(id=second_id.id).last()
        gateway_name.priority = int(str(obj[0])) * -1
        gateway_name.save()
        return redirect('checkout')
    else:
        return render(request, 'payment_failure.html')

# razorpay failure page
@csrf_exempt
def razorpay_failure(request):
    # cart = request.session['country']
    data = {k: v[0] for k, v in dict(request.POST).items()}
    pay_option = PaymentMode.objects.all().order_by('priority')
    second_priority = ''
    third_priority = ''

    for index, item in enumerate(pay_option):
        if index == 0:
            second_priority = item
        if index == 1:
            third_priority = item
    second_id = second_priority
    third_id = third_priority

    if second_id:
        gateway_name = PaymentMode.objects.get(id=second_id.id)
        obj = PaymentMode.objects.values_list('priority').filter(id=second_id.id).last()
        gateway_name.priority = abs(int(str(obj[0])))
        gateway_name.save()
    if third_id:
        gateway_name = PaymentMode.objects.get(id=third_id.id)
        obj = PaymentMode.objects.values_list('priority').filter(id=third_id.id).last()
        gateway_name.priority = abs(int(str(obj[0])))
        gateway_name.save()
        return redirect('checkout')
    else:
        return render(request, 'payment_failure.html')