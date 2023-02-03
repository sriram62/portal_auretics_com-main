from django import template
from shop import models
from mlm_admin.models import *
from distributor.models import *
import datetime
register = template.Library()

def dis_price_exclude_tax(mrp,distributor_price,igst):
    if igst == None:
        igst = 0
    if mrp == None:
        mrp = 0
    igst = float(igst)
    distributor_price_amount_ex_tax = mrp/(((100+distributor_price)/100)*((100 + igst)/100))
    distributor_price_amount_ex_tax=round(distributor_price_amount_ex_tax,2)
    return distributor_price_amount_ex_tax

def dis_price_include_tax(mrp,distributor_price):
    if mrp == None:
        mrp = 0
    if distributor_price == None:
        distributor_price = 0

    mrp=float(mrp)
    distributor_price=float(distributor_price)
    distributor_price_amount = mrp/((100+distributor_price)/100)
    distributor_price_amount=round(distributor_price_amount, 2)
    return distributor_price_amount

@register.simple_tag()
def multiply(qty, unit_price):
    if qty == None:
        qty = 0
    qty= float(qty)
    if unit_price == None:
        unit_price = 0
    unit_price= float(unit_price)
    # you would need to do any localization of the result here
    return qty * unit_price

@register.simple_tag()
def distributor_in_tax(mrp,distributor_price):
    if (mrp == None):
        mrp = 0
    mrp=float(mrp)
    distributor_price=float(distributor_price)
    distributor_price_amount = mrp/((100+distributor_price)/100)
    distributor_price_amount=round(distributor_price_amount, 2)
    return distributor_price_amount
@register.simple_tag()
def totaldistributor_in_tax(mrp,distributor_price,quantity):
    if (mrp == None):
        mrp = 0
    mrp=float(mrp)
    distributor_price=float(distributor_price)
    quantity=float(quantity)
    distributor_price_amount = mrp/((100+distributor_price)/100)
    distributor_price_amount=distributor_price_amount * quantity
    distributor_price_amount = round(distributor_price_amount,2)
    return distributor_price_amount
@register.simple_tag()
def distributor_ex_tax(mrp,distributor_price,igst):
    if igst == None:
        igst = 0

    if (mrp == None):
        mrp = 0
    if (distributor_price == None):
        mrp = 0
    distributor_price_amount_ex_tax = mrp/(((100+distributor_price)/100)*((100 + igst)/100))
    distributor_price_amount_ex_tax=round(distributor_price_amount_ex_tax,2)
    return distributor_price_amount_ex_tax

@register.simple_tag()
def totaldistributor_ex_tax(mrp,distributor_price,igst,qty):
    if igst == None:
        igst = 0
    if (mrp == None):
        mrp = 0
    distributor_price_amount_ex_tax = mrp/(((100+distributor_price)/100)*((100 + igst)/100))
    distributor_price_amount_ex_tax= distributor_price_amount_ex_tax * qty
    distributor_price_amount_ex_tax = round(distributor_price_amount_ex_tax,2)
    return distributor_price_amount_ex_tax

def bussiness_value_calculation(mrp,distributor_price,igst,business_value):
    if igst == None:
        igst = 0
    distributor_price_amount_ex_tax = mrp/(((100+distributor_price)/100)*((100 + igst)/100))
    business_value=(distributor_price_amount_ex_tax  * business_value)/100
    business_value=round(business_value,2)
    return business_value

@register.simple_tag()
def bussiness_value(mrp,distributor_price,igst,business_value):
    if (mrp == None):
        mrp = 0
    business_value=bussiness_value_calculation(mrp,distributor_price,igst,business_value)
    return business_value

@register.simple_tag()
def bussiness_value_total(mrp,distributor_price,igst,business_value,quantity):
    if (mrp == None):
        mrp = 0
    business_value=bussiness_value_calculation(mrp,distributor_price,igst,business_value)
    total = business_value*quantity
    total=round(total,2)
    return total

@register.simple_tag()
def point_value(mrp,distributor_price,igst,point_value):
    if (mrp == None):
        mrp = 0
    distributor_price_exclude_tax=dis_price_exclude_tax(mrp,distributor_price,igst)
    point_value = (distributor_price_exclude_tax * point_value)/100
    point_value=round(point_value,2)
    return point_value

@register.simple_tag()
def point_value_total(mrp,distributor_price,igst,point_value,quantity):
    if (mrp == None):
        mrp = 0
    distributor_price_exclude_tax=dis_price_exclude_tax(mrp,distributor_price,igst)
    point_value = (distributor_price_exclude_tax * point_value)/100
    total_point_value=point_value * quantity
    total_point_value=round(total_point_value,2)
    return total_point_value

@register.simple_tag()
def total_tax(mrp,distributor_price,tax,quantity):
    if (mrp == None):
        mrp = 0 
    distributor_price_in_tax=dis_price_include_tax(mrp,distributor_price)
    if tax == None:
        tax=0
    distributor_price_ex_tax = dis_price_exclude_tax(mrp,distributor_price,tax)
    tax=distributor_price_in_tax-distributor_price_ex_tax
    total_tax=tax*quantity
    total_tax = round(total_tax)
    return total_tax

@register.simple_tag()
def total_tax_amount_per_unit(mrp,distributor_price,tax):
    distributor_price_in_tax=dis_price_include_tax(mrp,distributor_price)
    if tax == None:
        tax=0
    distributor_price_ex_tax = dis_price_exclude_tax(mrp,distributor_price,tax)
    tax_amount_per_unit = distributor_price_in_tax - distributor_price_ex_tax
    tax_amount_per_unit = round(tax_amount_per_unit,2)
    return tax_amount_per_unit

@register.simple_tag()
def excluded(category_set):
    data=category_set.exclude(delete = True)
    return data

@register.simple_tag()
def check_quantity_inventory(material_center,prod,batch,quantity):
    import datetime
    today = datetime.datetime.now()
    inventory = Inventry.objects.get(material_center = material_center,product = prod,batch = batch,created_on = today)
    final_quantity = int(inventory.current_quantity) + int(quantity)
    return final_quantity
@register.simple_tag()
def user_valid(user,management,permission):
    data = user.menu_permission.management
    return True

@register.simple_tag()
def dis_check_quantity_inventory(material_center,prod,batch,quantity):
    import datetime
    today = datetime.datetime.now()
    inventory = Distributor_Inventry.objects.filter(material_center = material_center,product = prod,batch = batch,created_on = today)
    if len(inventory) > 0:
        inventory = inventory[0]
        final_quantity = int(inventory.current_quantity) + int(quantity)
        return final_quantity
    else:
        return 0