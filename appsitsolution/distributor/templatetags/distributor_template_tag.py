import datetime
from decimal import Decimal

from django import template

from distributor.models import *

register = template.Library()


@register.simple_tag()
def dis_check_quantity_inventory(material_center, prod, batch, quantity):
    try:
        today = datetime.datetime.now()
    except:
        today = datetime.now()
    try:
        inventory = Distributor_Inventry.objects.get(material_center=material_center, product=prod, batch=batch,
                                                     created_on=today, current_quantity__gt=0)
        final_quantity = int(inventory.current_quantity) + int(quantity)
    except:
        final_quantity = 0
    return final_quantity


@register.simple_tag()
def dis_check_quantity_inventory_loyalty_sale(material_center, prod, batch, quantity, last_month_cri, consumed_cri,
                                              is_partial):
    try:
        today = datetime.datetime.now()
    except:
        today = datetime.now()
    inventory = Distributor_Inventry.objects.get(material_center=material_center,
                                                 product=prod,
                                                 batch=batch,
                                                 created_on=today)
    total_cri = Decimal(last_month_cri) + consumed_cri
    quantity_acc_to_cri = total_cri // Decimal(batch.mrp)
    if is_partial and consumed_cri > Decimal(0):
        quantity_acc_to_cri = 1
    final_quantity = int(inventory.current_quantity) + int(quantity)
    print((inventory.current_quantity) + (quantity), '<------geting current_quantity + quantity')
    return final_quantity if final_quantity < quantity_acc_to_cri else quantity_acc_to_cri
