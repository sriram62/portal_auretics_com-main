from .models import *

from django.conf import settings

def extras(request):
    category = Category.objects.filter(is_parent_category='yes',delete = False).order_by('cat_order')
    return {'category' : category}

from . import cart


def cart_item_count(request):
    # import inspect
    # print("function: " + str(inspect.stack()[1].function))
    item_count = cart.item_count(request)
    a_sub_total = cart.a_subtotal(request)
    return {'cart_item_count' : item_count,'a_sub_total':a_sub_total }


def cart_distributor_checkout(request):
    distributor_checkout_name = ''
    distributor_mobile = ''
    distributor_address = ''
    distributor_address_line_2 = ''
    distributor_city = ''
    distributor_state = ''
    distributor_pin_code = ''
    if 'distributor_checkout' in request.session:
        distributor_checkout_name = Material_center.objects.get(id=request.session['distributor_checkout']).mc_name
        distributor_mobile = Material_center.objects.get(id=request.session['distributor_checkout']).advisor_registration_number.profile.phone_number
        distributor_address = Material_center.objects.get(id=request.session['distributor_checkout']).address
        distributor_address_line_2 = Material_center.objects.get(id=request.session['distributor_checkout']).address_line_2
        distributor_city = Material_center.objects.get(id=request.session['distributor_checkout']).city
        distributor_state = Material_center.objects.get(id=request.session['distributor_checkout']).state
        distributor_pin_code = Material_center.objects.get(id=request.session['distributor_checkout']).pin_code
    return {'distributor_checkout_name': distributor_checkout_name,
            'distributor_mobile':distributor_mobile,
            'distributor_address':distributor_address,
            'distributor_address_line_2':distributor_address_line_2,
            'distributor_city':distributor_city,
            'distributor_state':distributor_state,
            'distributor_pin_code':distributor_pin_code,
            }

def wallet_setup(request):
    if settings.WALLET == "ON":
        return {'wallet':'wallet'}
    else:
        return {'None':'None'}