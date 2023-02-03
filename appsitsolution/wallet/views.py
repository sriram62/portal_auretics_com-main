from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, reverse
from django.http import HttpResponse
import juspayp3
from random import randint
import requests

from .models import JuspayDipostedData, Wallet


juspayp3.api_key = ''
juspayp3.environment = 'sandbox'


def JuspayPayment(request, amount, c_id, c_email, c_phone):
    random_order_id = randint(100000, 200000)
    new_order = juspayp3.Orders.create(
        order_id=random_order_id,
        amount=amount,
        customer_id=c_id,
        customer_email=c_email,
        customer_phone=c_phone,
        return_url=request.build_absolute_uri(
            reverse('response', args=[amount]))
    )
    param_dict = vars(new_order)
    param_dict['links'] = vars(new_order.payment_links)

    return render(request, 'wallet/payment.html', param_dict)


def response(request, *args):
    amount = request.GET.get('amount')
    resp_dict = dict()
    resp_dict['order_id'] = request.GET.get('order_id')
    resp_dict['status'] = request.GET.get('status')
    resp_dict['signature'] = request.GET.get('signature')
    resp_dict['signature_algorithm'] = request.GET.get('signature_algorithm')

    if resp_dict["status"] == "CHARGED":
        with transaction.atomic():
            wallet = Wallet.objects.get(user=request.user)
            wallet.deposit(amount)
            obj = JuspayDipostedData.objects.create(
                order_id=resp_dict['order_id'], signature=resp_dict['signature'], signature_algorithm=resp_dict['signature_algorithm'])
            obj.save()

    return render(request, 'response.html', resp_dict)
