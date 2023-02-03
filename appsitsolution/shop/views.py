# from decorators import login_required_message
import datetime
import re
from datetime import date, timedelta
from django.contrib.auth.models import User
from .models import *
import razorpay
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpResponseRedirect
from django.http import JsonResponse
# from decorators import login_required_message
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404, reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import View
from django.views.generic.list import ListView
from paywix.payu import Payu

from accounts.models import ReferralCode, Profile, Kyc
from accounts.models import User_Check, BankAccountDetails
from accounts.views import check_registration_form_fn
from portal_auretics_com import settings
from distributor.models import *
from mlm_admin.models import Inventry
from mlm_admin.views import Objectify
from payment_gateway.models import PaymentMode
from payment_gateway.views import payu_payment_gateway, zaakpay_payment_gateway, rozorpay_payment_gateway
from wallet.models import Wallet
from . import cart
from .cart import recalculate_cart
from .forms import AddressForm
from .forms import CartForm, CheckoutForm
from .order_id import order_id, check_quantity
from django.db.models import Q, Sum, Count
from payment_gateway.models import PaymentMode
from payment_gateway.views import payu_payment_gateway, zaakpay_payment_gateway, rozorpay_payment_gateway
import datetime
import razorpay
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.db.models import OuterRef, Subquery
from .utils import get_products_for, get_products_for_mc, is_eligible_for_loyalty_purchase
from .templatetags.shop_tag import hide_product
from pyjama import j

payu_config = settings.PAYU_CONFIG
merchant_key = payu_config.get('merchant_key')
merchant_salt = payu_config.get('merchant_salt')
surl = payu_config.get('success_url')
furl = payu_config.get('failure_url')
mode = payu_config.get('mode')
payu = Payu(merchant_key, merchant_salt, surl, furl, mode)
# from .serializes import *
import json

# import pagination stuff
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

payu_config = settings.PAYU_CONFIG
merchant_key = payu_config.get('merchant_key')
merchant_salt = payu_config.get('merchant_salt')
surl = payu_config.get('success_url')
furl = payu_config.get('failure_url')
mode = payu_config.get('mode')
payu = Payu(merchant_key, merchant_salt, surl, furl, mode)

# from .serializes import *


# Create your views here.

from tablib import Dataset


def pincode_upload_excel(request):
    if request.method == 'POST':
        pin_resource = Pincode()
        dataset = Dataset()
        new_persons = request.FILES['myfile']
        imported_data = dataset.load(new_persons.read())
        result = pin_resource.import_data(dataset, dry_run=True)  # Test the data import
        if not result.has_errors():
            pin_resource.import_data(dataset, dry_run=False)  # Actually import now
    return render(request, 'mlm_admin/upload_pincodes.html')


def Auto_pincode(request):
    qs = Pincode.objects.filter(request.GET.get('pincode'))
    citys = Pincode.objects.filter(request.GET.get('city'))
    stat = AdminState.objects.filter(request.GET.get('state_name'))
    pic_info = json.loads(qs.text)
    city_info = json.loads(citys.text)
    sate_info = json.loads(stat.text)
    necessary_info = pic_info[0]['pincode'][0]
    necessary_in = city_info[0]['city'][0]
    necessary = sate_info[0]['state_name'][0]

    return render(request, 'templates/registration.html')


CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


# Create your views here.


def home(request):
    cache_status = False
    if request.user.is_authenticated:
        category = cache.get("auth_category")
        if category is None:
            category = Category.objects.filter(is_parent_category='yes', delete=False).order_by('cat_order')
            cache.set("auth_category", category)
        else:
            cache_status = True
    else:
        category = cache.get("non_auth_category")
        if category is None:
            category = Category.objects.filter(is_parent_category='yes', delete=False, is_hide=False).order_by(
                'cat_order')
            # cache.set("non_auth_category", category)
        else:
            cache_status = True
    group_checkout_users = 'group_checkout_users_{}'.format(request.user.id)
    is_group_checkout = group_checkout_users in request.session
    cart_items_count = count(request, is_group_checkout, group_checkout_users)
    cart_items = group_cart(request, is_group_checkout, group_checkout_users)
    cart_total_pv = cart.get_all_cart_items_pv(request)
    is_eligible_for_loyalty_purchase(request)
    title = "Auretics Limited | Online Shopping Portal | Variety of Products at your Doorstep or Pick Up from any Distributor."
    context = {"cart_items": cart_items,
               'cart_items_count': cart_items_count,
               "cart_subtotal": cart.subtotal(request),
               'GROUP_CHECKOUT': settings.GROUP_CHECKOUT,
               # "banner_qs":banner_qs,
               'all_category': category,
               'title': title,
               'cache_status': cache_status,
               }
    return render(request, 'categories.html', context)


def validate_ref(request):
    referall_code = request.GET.get('referall_code', None)
    if referall_code:
        try:
            referall_code = referall_code.upper()
            queryset = ReferralCode.objects.filter(referral_code=referall_code)
            if queryset:
                queryset = queryset[0]
                ref_list = queryset.user_id.username
            else:
                referall_code = referall_code.lower()
                queryset = User.objects.filter(email=referall_code)
                if queryset:
                    queryset = queryset[0]
                    ref_list = queryset.username
                else:
                    queryset = Profile.objects.filter(phone_number=referall_code)
                    queryset = queryset[0]
                    ref_list = queryset.user.username
            # ref_list = queryset.user_id.username
            code = 200
        except ObjectDoesNotExist:
            ref_list = ''
            code = 404
    else:
        ref_list = ''
        code = 404

    data = {
        'refer_by': ref_list,
        'code': code
    }
    return JsonResponse(data)


def validate_email(request):
    email1 = request.GET.get('email', None)
    code = 400
    email = ''
    message = ''
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if (re.fullmatch(regex, email1)):
        pass
    else:
        code = 500
        message = "invalid Email"

    try:
        user = User.objects.get(email=email1)
        email = user.email
        code = 200

    except ObjectDoesNotExist:
        pass
    data = {
        'email': email,
        'code': code,
        'message': message
    }
    return JsonResponse(data)


def validate_mobile(request):
    mobile1 = request.GET.get('mobile', None)
    mobile = ''
    code = 400
    try:
        user = Profile.objects.get(phone_number=mobile1)
        mobile = user.phone_number
        code = 200
    except ObjectDoesNotExist:
        pass
    data = {
        'mobile': mobile,
        'code': code
    }
    return JsonResponse(data)


# cat display
def categry_name(request, main_cat, cat):
    mc = j.get_mc(request)
    qs = get_products_for(cat, mc)
    # AG :: Note replace main_cat & cat after running get_products_for function
    main_cat = str(main_cat).replace(" ", "")
    cat = str(cat).replace(" ", "")
    auth_cache_name = "auth_category" + str(main_cat)
    unauth_cache_name = "unauth_category" + str(main_cat)
    cache_status = False

    # qs =Product.objects.filter(category__cat_name=cat).exclude(delete=True)
    if request.user.is_authenticated:
        category = cache.get(auth_cache_name)
        if category is None:
            category = Category.objects.filter(is_parent_category='yes', delete=False).order_by('cat_order')
            cache.set(auth_cache_name, category)
        else:
            cache_status = True
    else:
        category = cache.get(unauth_cache_name)
        if category is None:
            category = Category.objects.filter(is_parent_category='yes', delete=False).order_by('cat_order')
            cache.set(unauth_cache_name, category)
        else:
            cache_status = True
    title = str(cat) + ":" + "Buy New " + str(cat) + " Products Online at Best Prices in India | Buy " + str(
        cat) + " Online - Auretics.com"
    group_checkout_users = 'group_checkout_users_{}'.format(request.user.id)
    is_group_checkout = group_checkout_users in request.session
    cart_items_count = count(request, is_group_checkout, group_checkout_users)
    cart_items = group_cart(request, is_group_checkout, group_checkout_users)
    return render(request, "lists.html", {
        'all_products': qs,
        "cart_items": cart_items,
        "cart_items_count": cart_items_count,
        "cart_subtotal": cart.subtotal(request),
        'GROUP_CHECKOUT': settings.GROUP_CHECKOUT,
        "category": category,
        'title': title,
        'mc': mc,
        'cache_status': cache_status
    })


def categry_name_sub(request, cat):
    auth_cache_name = "sub_auth_category" + str(cat)
    unauth_cache_name = "sub_unauth_category" + str(cat)
    cache_status = False
    qs = Product.objects.filter(category__cat_name=cat).exclude(delete=True)
    if request.user.is_authenticated:
        category = cache.get(auth_cache_name)
        if category is None:
            category = Category.objects.filter(is_parent_category='yes', delete=False).order_by('cat_order')
            cache.set(auth_cache_name, category)
        else:
            cache_status = True
    else:
        category = cache.get(unauth_cache_name)
        if category is None:
            category = Category.objects.filter(is_parent_category='yes', delete=False).order_by('cat_order')
            cache.set(unauth_cache_name, category)
        else:
            cache_status = True
    group_checkout_users = 'group_checkout_users_{}'.format(request.user.id)
    is_group_checkout = group_checkout_users in request.session
    cart_items_count = count(request, is_group_checkout, group_checkout_users)
    cart_items = group_cart(request, is_group_checkout, group_checkout_users)
    return render(request, "lists.html", {
        'all_products': qs,
        "cart_items": cart_items,
        'cart_items_count': cart_items_count,
        "cart_subtotal": cart.subtotal(request),
        'GROUP_CHECKOUT': settings.GROUP_CHECKOUT,
        "category": category,
        'title': 'Products',
        'mc': "0",
        'cache_status': cache_status,
    })


def ProductCategory(request, name):
    qs = Product.objects.filter(product_gender_name__gender_name=name).exclude(delete=True)
    # cart_items= cart.get_all_cart_items(request)
    cart_subtotal = cart.subtotal(request)
    auth_cache_name = "prod_auth_category" + str(name)
    unauth_cache_name = "prod_unauth_category" + str(name)
    cache_status = False
    if request.user.is_authenticated:
        category = cache.get(auth_cache_name)
        if category is None:
            category = Category.objects.filter(is_parent_category='yes', delete=False).order_by('cat_order')
            cache.set(auth_cache_name, category)
        else:
            cache_status = True
    else:
        category = cache.get(unauth_cache_name)
        if category is None:
            category = Category.objects.filter(is_parent_category='yes', delete=False).order_by('cat_order')
            cache.set(unauth_cache_name, category)
        else:
            cache_status = True
    group_checkout_users = 'group_checkout_users_{}'.format(request.user.id)
    is_group_checkout = group_checkout_users in request.session
    cart_items_count = count(request, is_group_checkout, group_checkout_users)
    cart_items = group_cart(request, is_group_checkout, group_checkout_users)
    return render(request, "lists.html", {
        'all_products': qs,
        'cart_items': cart_items,
        'cart_items_count': cart_items_count,
        'GROUP_CHECKOUT': settings.GROUP_CHECKOUT,
        'cart_subtotal': cart_subtotal,
        'category': category,
        'title': 'Products',
        'mc': "0",
        'cache_status': cache_status,
    })


def latest_sold_products(request):
    print("sorting is on")
    products_to_show = (LineItem.objects.filter(date_added__date__range=["2022-01-02", "2022-02-06"])
                        .values('product').order_by('product').annotate(total_qty=Sum('quantity')))
    print(products_to_show, '----')
    for data in products_to_show:
        product = Product.objects.get(id=int(data['product']))
        product.monthly_sales = int(data['total_qty'])
        product.save()
        print("product sales updated for " + str(product.product_name) + " as " + str(product.monthly_sales))


# @cache_page(CACHE_TTL)
def product_list(request, **kwargs):
    user_id = kwargs.get('user_id', None)
    product_user_name = ''
    if user_id is not None:
        user_data = User.objects.get(id=user_id)
        product_user_name = (user_data)
    mc = j.get_mc(request)
    dis_all_products_mc_cache_name = "dis_all_products" + str(mc.pk)
    no_dis_all_products_mc_cache_name = "no_dis_all_products" + str(mc.pk)
    cache_status = False
    cart_subtotal = cart.subtotal(request)
    if 'distributor_checkout' in request.session:
        all_products = cache.get(dis_all_products_mc_cache_name)
        if all_products is None:
            qs = get_products_for_mc(mc, request)
            merchant_center_id = Material_center.objects.get(id=request.session['distributor_checkout']).id
            distributor_inventory_products = Distributor_Inventry.objects.filter(material_center_id=merchant_center_id,
                                                                                 current_quantity__gt=0,
                                                                                 product__product_variant__main_variant='YES'). \
                exclude(product__delete=True,
                        product__category__delete=True).values_list('product', flat=True)
            all_products = qs.filter(id__in=distributor_inventory_products)
            cache.set(dis_all_products_mc_cache_name, all_products)
        else:
            cache_status = True
    else:
        all_products = cache.get(dis_all_products_mc_cache_name)
        if all_products is None:
            qs = get_products_for_mc(mc, request)
            all_products = qs.filter(product_variant__main_variant='YES').exclude(delete=True,
                                                                                  category__delete=True)
            cache.set(no_dis_all_products_mc_cache_name, all_products)
        else:
            cache_status = True

    auth_cache_name = "prod_list_auth_category"
    unauth_cache_name = "prod_list_unauth_category"
    if request.user.is_authenticated:
        category = cache.get(auth_cache_name)
        if category is None:
            category = Category.objects.filter(is_parent_category='yes', delete=False).order_by('cat_order')
            cache.set(auth_cache_name, category)
        else:
            cache_status = True
    else:
        category = cache.get(unauth_cache_name)
        if category is None:
            category = Category.objects.filter(is_parent_category='yes', delete=False).order_by('cat_order')
            cache.set(unauth_cache_name, category)
        else:
            cache_status = True

    page = request.GET.get('page', 1)
    page_obj_name = "product_list_paginator" + str(page)
    # page_obj = cache.get(page_obj_name)
    # # todo remove later
    # all_products_loop = Product.objects.all()
    # all_products = []
    # for i in all_products:
    #     p = j.usable_batches(i)
    #     all_products.append(p.pk)
    # all_products = Product.objects.filter(pk__in=all_products)

    if request.session.get('can_use_loyalty_purchase'):
        all_products = all_products.filter(loyalty_consume='YES', essential_product='NO').filter(
            batch__mrp__lte=request.session.get('remaining_loyalty_purchase_amount'))
    page_obj = all_products
    if page_obj is None:
        paginator = Paginator(all_products, 16)
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        cache.set(page_obj_name, page_obj)
    else:
        cache_status = True

    group_checkout_users = 'group_checkout_users_{}'.format(request.user.id)
    is_group_checkout = group_checkout_users in request.session
    cart_items_count = count(request, is_group_checkout, group_checkout_users)
    cart_items = group_cart(request, is_group_checkout, group_checkout_users)

    return render(request, "lists.html", {
        'user_id': user_id,
        'is_group_checkout': is_group_checkout,
        'all_products': page_obj,
        'cart_items': cart_items,
        'cart_items_count': cart_items_count,
        'GROUP_CHECKOUT': settings.GROUP_CHECKOUT,
        'cart_subtotal': cart_subtotal,
        'category': category,
        'title': 'Products',
        'product_user_name': product_user_name,
        'mc': mc,
        'cache_status': cache_status,
    })


def show_product(request, product_id, product_slug, **kwargs):
    group_user_id = kwargs.get('user_id', None)
    product = get_object_or_404(Product, id=product_id)
    group_checkout_users = 'group_checkout_users_{}'.format(request.user.id)
    is_group_checkout = group_checkout_users in request.session
    groups = {}
    if is_group_checkout:
        users = request.session[group_checkout_users]
        for group in users:
            group_user = User.objects.get(id=group).profile.first_name
            groups.update({group: group_user})
    if request.method == 'POST':
        form = CartForm(request, request.POST)
        if form.is_valid():
            request.form_data = form.cleaned_data
            cart.add_item_to_cart(request)
            is_eligible_for_loyalty_purchase(request)
            return redirect('show_cart')
    quantity = check_quantity(product, 1, request)
    form = CartForm(request, initial={'product_id': product.id})
    # sub_category=Category.objects.filter(is_parent_category='no').exclude(delete = False)
    category = cache.get("auth_category")
    if category is None:
        category = Category.objects.filter(is_parent_category='yes', delete=False).order_by('cat_order')
        cache.set("auth_category", category)  # sub_category=Category.objects.filter(is_parent_category='yes')
    description = product.description
    description = description.split('\r\n')
    ingredients = product.ingredients
    ingredients = ingredients.split('\r\n')
    usage = product.usage
    usage = usage.split('\r\n')
    directions = product.directions
    directions = directions.split('\r\n')
    indications = product.indications
    indications = indications.split('\r\n')
    special_feature = product.special_feature
    special_feature = special_feature.split('\r\n')
    safety_warning = product.safety_warning
    safety_warning = safety_warning.split('\r\n')
    wallet = settings.WALLET

    mc = j.get_mc(request)

    page_title = str(product.product_name) + " | Auretics.com | Best " + str(
        product.category.cat_name) + " Products at your Doorstep"
    cart_items_count = count(request, is_group_checkout, group_checkout_users)
    cart_items = group_cart(request, is_group_checkout, group_checkout_users)
    return render(request, 'detail.html', {'is_group_checkout': is_group_checkout,
                                           'group_user_id': group_user_id,
                                           'groups': groups,
                                           'product': product,
                                           'form': form,
                                           "cart_items": cart_items,
                                           "cart_items_count": cart_items_count,
                                           'GROUP_CHECKOUT': settings.GROUP_CHECKOUT,
                                           "cart_subtotal": cart.subtotal(request),
                                           # "sub_category":sub_category,
                                           "category": category,
                                           'quantity': quantity,
                                           'title': page_title,
                                           'description': description,
                                           'ingredients': ingredients,
                                           'usage': usage,
                                           'directions': directions,
                                           'indications': indications,
                                           'special_feature': special_feature,
                                           'safety_warning': safety_warning,
                                           'wallet': wallet,
                                           'mc': mc, }
                  )


# product details
def product_search(request):
    cache_status = False
    all_products = cache.get("all_products")
    if all_products is None:
        all_products = Product.objects.all().exclude(delete=True)
        cache.set("all_products", all_products)
    else:
        cache_status = True
    category = cache.get("auth_category")
    if category is None:
        category = Category.objects.filter(is_parent_category='yes', delete=False).order_by('cat_order')
        cache.set("auth_category", category)  # sub_category=Category.objects.filter(is_parent_category='yes')
    else:
        cache_status = True
    page = request.GET.get('page', 1)

    paginator = Paginator(all_products, 16)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    if request.method == 'POST':
        search_value = request.POST.get('search')
        all_products = Product.objects.filter(
            Q(product_name__icontains=search_value) | Q(description__icontains=search_value) |
            Q(print_name__icontains=search_value) | Q(name_in_accounting_software__icontains=search_value) |
            Q(ingredients__icontains=search_value)).exclude(delete=True)
        if all_products:
            mc = j.get_mc(request)
            all_products.mc = mc
            all_products.distributor_checkout = distributor_checkout
            all_products = hide_product(all_products)
            group_checkout_users = 'group_checkout_users_{}'.format(request.user.id)
            is_group_checkout = group_checkout_users in request.session
            cart_items_count = count(request, is_group_checkout, group_checkout_users)
            cart_items = group_cart(request, is_group_checkout, group_checkout_users, )
            return render(request, 'search_list.html',
                          {"all_products": all_products, 'category': category,
                           "cart_items": cart_items,
                           'GROUP_CHECKOUT': settings.GROUP_CHECKOUT,
                           'cart_items_count': cart_items_count,
                           "cart_subtotal": cart.subtotal(request), 'title': 'Search Products',
                           'cache_status': cache_status,
                           'mc': mc, })
        else:
            all_products = Product.objects.filter(main_variant=True).exclude(delete=True)
            error_msg = "no result"
            group_checkout_users = 'group_checkout_users_{}'.format(request.user.id)
            is_group_checkout = group_checkout_users in request.session
            cart_items_count = count(request, is_group_checkout, group_checkout_users)
            cart_items = group_cart(request, is_group_checkout, group_checkout_users, )
            return render(request, 'search_list.html',
                          {"all_products": page_obj, 'category': category,
                           'GROUP_CHECKOUT': settings.GROUP_CHECKOUT, 'error_msg': error_msg,
                           "cart_items": cart_items, 'cart_items_count': cart_items_count,
                           "cart_subtotal": cart.subtotal(request), 'title': 'Search Products',
                           'cache_status': cache_status,
                           'error_msg': error_msg})
    # return render(request, 'search_list.html', {"all_products":all_products, "cart_items":cart.get_all_cart_items(request),"cart_subtotal":cart.subtotal(request)})
    group_checkout_users = 'group_checkout_users_{}'.format(request.user.id)
    is_group_checkout = group_checkout_users in request.session
    cart_items_count = count(request, is_group_checkout, group_checkout_users)
    cart_items = group_cart(request, is_group_checkout, group_checkout_users)
    return render(request, 'lists.html', {"all_products": page_obj,
                                          'category': category,
                                          "cart_items": cart_items,
                                          'GROUP_CHECKOUT': settings.GROUP_CHECKOUT,
                                          'cart_items_count': cart_items_count,
                                          "cart_subtotal": cart.subtotal(request),
                                          'title': 'Search Products',
                                          'cache_status': cache_status,
                                          })


#
# product variant details

# product variant details

def show_product_variant(request, variant_id, product_id):
    product = get_object_or_404(Product, id=variant_id)
    main_product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = CartForm(request, request.POST)
        if form.is_valid():
            request.form_data = form.cleaned_data
            cart.add_item_to_cart(request)
            return redirect('show_cart')

    form = CartForm(request, initial={'product_id': product.id})
    group_checkout_users = 'group_checkout_users_{}'.format(request.user.id)
    is_group_checkout = group_checkout_users in request.session
    cart_items_count = count(request, is_group_checkout, group_checkout_users)
    cart_items = group_cart(request, is_group_checkout, group_checkout_users)
    # sub_category=Category.objects.filter(is_parent_category='no').exclude(delete = False)
    # category = Category.objects.filter(is_parent_category = 'yes',delete = False).order_by('cat_order')
    return render(request, 'detail_variant.html', {
        'product': product,
        'main_product': main_product,
        'form': form, 'GROUP_CHECKOUT': settings.GROUP_CHECKOUT,
        "cart_items": cart_items, 'cart_items_count': cart_items_count,
        "cart_subtotal": cart.subtotal(request),
        # "sub_category":sub_category,
        # "category":category
        'title': 'Products Details',
    })


# @login_required_message(message="You should be logged in, in order to see the index!")
# @login_required(login_url='/accounts/login')
def show_cart(request, group_cart=None):
    cart_items_count = 0
    loyalty_cart_items_count = 0
    cart_items = {}
    if request.method == 'POST':
        if request.POST.get('submit') == 'Update':
            qty = int(float(request.POST.get('quantity')))
            if qty > 0:
                cart.update_item(request)
                is_eligible_for_loyalty_purchase(request, group_cart)
        if request.POST.get('submit') == 'Remove':
            cart.remove_item(request)
            if not is_eligible_for_loyalty_purchase(request, group_cart):
                cart.delete_loyalty_items(request, group_cart=group_cart)
                request.session['loyalty_purchase_enabled'] = False

    skip_kyc = False
    if request.user.is_authenticated:
        # AG :: If KYC is not done then the user should be redirected to the Edit Profile Page. << START >>
        try:
            if request.method == 'GET':
                skip_kyc = request.GET.get('skip_kyc', False)
                if skip_kyc == 'Y':
                    skip_kyc_date = Profile.objects.filter(user=request.user).update(
                        skip_kyc_date=datetime.date.today())
        except:
            pass

        # AG :: User will be first asked to complete the KYC and he should get option to skip KYC and complete registration later.
        blank_list = [None, "None", "none", "NONE", "", "NO", "no", "No", False, "False", "FALSE", "false", "NA", "na",
                      "Na"]
        if not skip_kyc == 'Y':
            try:
                kyc_done = Kyc.objects.get(kyc_user=request.user).kyc_done
            except:
                kyc_done = False

            # If KYC is done, then this function will not trigger, but in case KYC is manually verified by the admin, we will mark it as verified.
            if not kyc_done:
                # AG :: If user's KYC has been manually checked by the admin, we will mark his KYC as done and will not prompt him for KYC again.
                current_user = request.user
                check_user_qs = get_object_or_404(User_Check, user_check=current_user)
                registration_form = check_registration_form_fn(check_user_qs)
                if registration_form == 'Registration  is Complete':
                    kyc_done = True
                    kyc_obj = Kyc.objects.update_or_create(
                        kyc_user=request.user, defaults={
                            'kyc_user': request.user,
                            'kyc_done': True,
                            'manual': True,
                        })[0]

            if not kyc_done:
                try:
                    skip_kyc_date = Profile.objects.filter(user=current_user).first().skip_kyc_date
                except:
                    skip_kyc_date = '1997-02-01'
                can_we_skip_kyc = False
                try:
                    pan_number = Kyc.objects.get(kyc_user=request.user).pan_number
                    if len(pan_number) == 10:
                        user_bank_details = BankAccountDetails.objects.get(bank_account_user=request.user)
                        account_number = user_bank_details.account_number
                        ifsc_code = user_bank_details.ifsc_code
                        if account_number not in blank_list:
                            if ifsc_code not in blank_list:
                                can_we_skip_kyc = True
                except:
                    pass
                if skip_kyc_date:
                    if skip_kyc_date.date() >= (datetime.datetime.now().date() - timedelta(days=1)):
                        pass
                    elif can_we_skip_kyc == True:
                        pass
                    else:
                        messages.error(request,
                                       "<a href='/cart/?skip_kyc=Y'>Please verify KYC Details and Bank details. To skip and verify later, please scroll down and click \"skip for now\".</a>")
                        return redirect('edit_profile')
            # << KYC trigger END >>

        else:
            try:
                kyc_qs = Kyc.objects.get(kyc_user=user)
                if not kyc_qs.pan_number in blank_list:
                    kyc_qs_pan_number = kyc_qs.pan_number
            except:
                kyc_qs_pan_number = None

            try:
                bank_qs = BankAccountDetails.objects.get(bank_account_user=user)
                if not bank_qs.account_number in blank_list:
                    bank_qs_account_number = bank_qs.account_number
            except:
                bank_qs_account_number = None

            if kyc_qs_pan_number and bank_qs_account_number:
                kyc_obj = Kyc.objects.update_or_create(
                    kyc_user=request.user, defaults={
                        'kyc_user': request.user,
                        'manual': True,
                    })[0]

    group_checkout_users = 'group_checkout_users_{}'.format(request.user.id)
    """if group_cart and group_checkout_users in request.session:
        users = request.session[group_checkout_users]
        print(users, "USERS!")
        #users.append(request.user.id)/
        cart_items = cart.get_group_user_cart_items(users)
        print(cart_items, "cart_items")"""
    is_group_checkout = group_checkout_users in request.session
    # sub_category=Category.objects.filter(is_parent_category='yes').exclude(delete = False)
    # category = Category.objects.filter(is_parent_category = 'yes',delete = False).order_by('cat_order')
    if is_group_checkout:
        users = request.session[group_checkout_users]
        for cart_group_user in users:
            cart_group_user_name = User.objects.get(id=cart_group_user)
            items = cart.get_group_user_cart_items([cart_group_user])
            cart_items_count += items.count()
            loyalty_cart_items_count += items.filter(is_loyalty_purchase_cart=True).count()
            cart_items.update({cart_group_user_name: items})
        # cart_items = cart.get_group_user_cart_items(users)
        cart_subtotal = cart.subtotal(request, for_total=True, group_user=users)
        cart_loyalty_subtotal = cart.loyalty_subtotal(request, for_total=True, group_user=users)
        cart_sub_bv = cart.subtotal_bv(request, for_total=True, group_user=users)
        cart_sub_pv = cart.subtotal_pv(request, for_total=True, group_user=users)
        a_cart_subtotal = cart.a_subtotal(request, for_total=True, group_user=users)
        a_cart_loyalty_subtotal = cart.a_loyalty_subtotal(request, for_total=True, group_user=users)
    else:
        cart_user_name = request.user.profile.first_name if request.user.is_authenticated else ''
        items = CartItem.objects.filter(user_id=request.user.id, in_stock=True)
        items = recalculate_cart(items, request)
        cart_items_count = items.count()
        loyalty_cart_items_count = items.filter(is_loyalty_purchase_cart=True).count()
        cart_items.update({cart_user_name: items})
        cart_subtotal = cart.subtotal(request, for_total=True)
        cart_loyalty_subtotal = cart.loyalty_subtotal(request, for_total=True)
        cart_sub_bv = cart.subtotal_bv(request, for_total=True)
        cart_sub_pv = cart.subtotal_pv(request, for_total=True)
        a_cart_subtotal = cart.a_subtotal(request, for_total=True)
        a_cart_loyalty_subtotal = cart.a_loyalty_subtotal(request, for_total=True)

    # sub_category=Category.objects.filter(is_parent_category='yes').exclude(delete = False)
    # category = Category.objects.filter(is_parent_category = 'yes',delete = False).order_by('cat_order')
    for username, items in cart_items.items():
        for item in items:
            quantity = check_quantity(item.product, item.quantity, request)
            if (quantity == False):
                CartItem.objects.filter(pk=item.pk).update(in_stock=False)
                item.in_stock = False
            elif (item.in_stock == False and quantity == True):
                CartItem.objects.filter(pk=item.pk).update(in_stock=True)

    items = recalculate_cart(items, request)
    '''cart_subtotal = cart.subtotal(request, for_total=True)
    cart_sub_bv = cart.subtotal_bv(request, for_total=True)
    cart_sub_pv = cart.subtotal_pv(request, for_total=True)
    a_cart_subtotal = cart.a_subtotal(request, for_total=True)'''

    if not cart_items_count:
        messages.add_message(request, messages.INFO, "Your Cart is Empty.")
        return redirect('product_list')

    if "distributor_checkout" in request.session:
        material = Material_center.objects.get(id=request.session['distributor_checkout']).id

    material = Material_center.objects.filter(frontend=True).first()
    distributor_checkout = False
    if request.user.is_authenticated:
        # get the material center if distributor is selected if not then c&f state wise
        if "distributor_checkout" in request.session:
            material = Material_center.objects.get(id=request.session['distributor_checkout'])
            distributor_checkout = True
        else:
            try:
                material = request.user.profile.get_related_mc()
                if not material:
                    material = Material_center.objects.filter(frontend=True).first()
            except:
                pass
    if material:
        material = material.id
    params_dict = {
        'is_group_checkout': is_group_checkout,
        'cart_items': cart_items,
        'cart_items_count': cart_items_count,
        'GROUP_CHECKOUT': settings.GROUP_CHECKOUT,
        'loyalty_cart_items_count': loyalty_cart_items_count,
        'cart_subtotal': cart_subtotal,
        'cart_loyalty_subtotal': cart_loyalty_subtotal,
        'cart_sub_bv': cart_sub_bv,
        'cart_sub_pv': cart_sub_pv,
        'a_cart_subtotal': a_cart_subtotal,
        'a_cart_loyalty_subtotal': a_cart_loyalty_subtotal,
        'valuenext': 'data',
        'title': 'Show Cart',
        'material': material,
        'distributor_checkout': distributor_checkout,
        'skip_kyc': skip_kyc,
    }

    wallet = settings.WALLET
    if wallet == "ON":
        wallet_dict = {
            # "cart_items": cart.get_all_cart_items(request),
            'wallet': wallet
        }
        params = {**params_dict, **wallet_dict}
    else:
        params = params_dict

    return render(request, 'cart.html', params)


@csrf_exempt
def sitemap_xml(request):
    file_dir = '/static/root/'
    filename = 'sitemap.xml'
    root_file = open(str(settings.BASE_DIR) + file_dir + filename, 'rb')
    response = HttpResponse(content=root_file)
    response['Content-Type'] = 'text/xml'
    response['Content-Disposition'] = 'attachment; filename="%s"' % (filename)
    return response


@csrf_exempt
def robots_txt(request):
    file_dir = '/static/root/'
    filename = 'robots.txt'
    root_file = open(str(settings.BASE_DIR) + file_dir + filename, 'rb')
    response = HttpResponse(content=root_file)
    response['Content-Type'] = 'text/plain'
    response['Content-Disposition'] = 'attachment; filename="%s"' % (filename)
    return response


@login_required(login_url='home')
def checkout(request, distributor_id=None, group_checkout=True):
    # try:
    #     temp = Address.objects.filter(user=request.user, address_type="B")[0]
    # except:
    #     temp = Address.objects.filter(user=request.user, address_type="S")[0]
    temp = ''
    # group_checkout_users = 'group_checkout_users_{}'.format(request.user.id)
    # address = Address.objects.get()'
    form = ''
    address_form = ''

    if request.method == 'POST':
        orders = []
        default_address = request.POST.get('order_address')
        billing_address = request.POST.get('billingforms')
        card_description = request.POST.get('card_description')

        address_qs_billing = ''
        address = ''
        try:
            address = cleaned_data.get('address')
        except:
            pass

        material_center = Material_center.objects.filter(frontend=True).first()
        if request.user.is_authenticated:
            # get the material center if distributor is selected if not then c&f state wise
            if "distributor_checkout" in request.session:
                material_center = Material_center.objects.get(id=request.session['distributor_checkout'])
            else:
                try:
                    material_center = request.user.profile.get_related_mc()
                    if not material_center:
                        material_center = Material_center.objects.filter(frontend=True).first()
                except:
                    pass

        try:
            whole_grand_total = cart.a_subtotal(request, for_total=True, group_cart=group_checkout)
            print(whole_grand_total, "whole_grand_total +++++++++++")
            if 'distributor_checkout' in request.session:
                shiping_charge = 0
            else:
                shiping_charge = cart.shiping_charge_add(whole_grand_total)
            whole_grand_total = float(request.POST["pending"])
        except:
            whole_grand_total = cart.a_subtotal(request, for_total=True, group_cart=group_checkout)
            # add shipping charge if distributor checkout is false
            if 'distributor_checkout' in request.session:
                shiping_charge = 0
            else:
                shiping_charge = cart.shiping_charge_add(whole_grand_total)
                whole_grand_total = cart.order_grand_total(whole_grand_total)
                print(shiping_charge, "whole_grand_total ++++++++++1")
                print(whole_grand_total, "whole_grand_total ++++++++++2")

        if default_address:
            address_qs = Address.objects.get(id=default_address)
            # nipur start code
            order_id1 = order_id(material_center)
            # # grand_total=cart.subtotal(request)
            grand_total = cart.a_subtotal(request, for_total=True)
            if 'distributor_checkout' in request.session:
                shiping_charge = 0
                grand_total = grand_total
            else:
                shiping_charge = cart.shiping_charge_add(grand_total)
                grand_total = cart.order_grand_total(grand_total)

        elif billing_address:
            house_number = request.POST.get('house_number')
            address_line = request.POST.get('address_line')
            landmark = request.POST.get('landmark')
            city = request.POST.get('city')
            street = request.POST.get('street')
            mobile = request.POST.get('mobile')
            # alternate_mobile=request.POST.get('alternate_mobile')
            alternate_mobile = request.POST.get('alternate_mobile')
            pin = request.POST.get('pin')
            address_qs = Address(
                user=request.user,
                house_number=house_number,
                address_line=address_line,
                Landmark=landmark,
                city=city,
                street=street,
                pin=pin,
                mobile=mobile,
                alternate_mobile=alternate_mobile,
                address_type='S'
            )
            address_qs.save()
            address_qs_bling = Address.objects.filter(
                user=request.user,
                address_type='B',
                default=True
            )[0]
        else:
            form = CheckoutForm(request.POST)
            if form.is_valid():
                cleaned_data = form.cleaned_data
                name = cleaned_data.get('name')
                email = cleaned_data.get('email')
                postal_code = cleaned_data.get('postal_code')
                address = cleaned_data.get('address')
        group_checkout_users = 'group_checkout_users_{}'.format(request.user.id)
        if group_checkout and group_checkout_users in request.session:
            users = request.session[group_checkout_users]
        else:
            users = [request.user.id]
        users_user = list(set(users))

        if not address_qs_billing:
            address_qs_billing = Address.objects.filter(
                user=request.user,
                address_type='B',
                default=True
            )
        if not address_qs_billing:
            address_qs_billing = Address.objects.filter(
                user=request.user,
                address_type='B',
            )
        if not address_qs_billing:
            address_qs_billing = Address.objects.filter(
                user=request.user,
            )
        try:
            address_qs_billing = address_qs_billing.first()
        except:
            address_qs_billing = []

        users_id = [request.user.id]
        print(users_id, "user iten @@@@@@@@@@@2")
        for user_ids in users_user:
            items = cart.get_group_user_cart_items([user_ids])
            print(items, "user iten @@@@@@@@@@@2")
            if items:
                users_id.append(user_ids)
                if user_ids == request.user.id:
                    users_id.remove(user_ids)
        users = users_id

        for user_id in users:
            user_name = User.objects.get(id=user_id).username
            user_email = User.objects.get(id=user_id).email
            user = User.objects.get(id=user_id)
            try:
                grand_total = float(request.POST["pending"])
                print(grand_total, "grand total iser id data ---")
            except:
                grand_total = cart.a_subtotal(request, for_total=True, group_user=[user_id])
                # print(grand_total, "grand total iser id data ---4")
                # if 'distributor_checkout' in request.session:
                #     grand_total = grand_total
                #     print(grand_total,"grand total iser id data ---2")
                # else:
                #     grand_total = cart.order_grand_total(grand_total)
                #     print(grand_total, "grand total iser id data ---3")
            postal_code = ''
            if default_address:
                order_id1 = order_id(material_center)

                address_qs_pin = address_qs.pin
                if not address_qs_pin:
                    address_qs_pin = 0
                    try:
                        address_qs.pin = address_qs_pin
                        address_qs.save()
                    except:
                        pass
            if default_address:
                order_id1 = order_id(material_center)

                o = Order(
                    name=address_qs.name,
                    email=user_email,
                    postal_code=address_qs.pin,
                    shipping_address=address_qs,
                    user_id=user,
                    order_by=request.user.username,
                    # nipur start code
                    address=address,
                    billing_address=address_qs,
                    order_id1=order_id1,
                    grand_total=grand_total,
                    material_center=material_center,
                    original_material_center=material_center,
                    card_description=card_description,
                )
            o.save()
            if group_checkout:
                all_items = cart.get_group_user_cart_items([user_id])
            else:
                all_items = cart.get_all_cart_items(request, for_total=True)
            for cart_item in all_items:
                try:
                    batch = \
                        cart_item.product.batch_set.filter(delete=False).order_by("date_of_expiry")[0]
                except:
                    batch = None
                # <here  we are subtracting quantity from the inventory 20-03-2021 end  here
                # here we are subtracting the quantity from the batch quantity end here
                business_value = float(cart_item.quantity * cart_item.business_value)
                business_value = round(business_value, 2)
                point_value = float(cart_item.quantity * cart_item.point_value)
                point_value = round(point_value, 2)
                li = LineItem(
                    order_by=request.user.email,
                    product_id=cart_item.product_id,
                    batch=batch,
                    price=cart_item.discount_price,
                    # price = cart_item.price,
                    quantity=cart_item.quantity,
                    order_id=o.id,
                    cgst=cart_item.product.cgst,
                    sgst=cart_item.product.sgst,
                    igst=cart_item.product.igst,
                    pv=point_value,
                    bv=business_value
                )
                li.save()
            cart_sub_bv = cart.subtotal_bv(request, for_total=True, group_user=[user_id])
            print(cart_sub_bv, "++++++++++++++++")
            cart_sub_pv = cart.subtotal_pv(request, for_total=True, group_user=[user_id])
            o = Order.objects.get(pk=o.id)
            print(cart_sub_pv, "++++++++++++++++")

            if distributor_id:
                print(distributor_id, "distributed id")
                distributor = Material_center.objects.get(id=distributor_id)
                print(distributor, "distributed id")
                data = Distributor_Sale(sale_user_id=request.user, material_center=distributor,
                                        narration='Submitted from distributor list checkout',
                                        advisor_distributor_name=request.user, date=date.today(),
                                        grand_total=whole_grand_total, order=o, grand_bv=cart_sub_bv,
                                        grand_pv=cart_sub_pv, is_pending=True)
                data.save()

                cart.clear(request)
                messages.add_message(request, messages.INFO, 'Order Placed Successfully!')
                return HttpResponseRedirect('/')
            if request.POST.get("paid_with_wallet", False):
                with transaction.atomic():
                    wallet = Wallet.objects.get(user=request.user)
                    wallet.withdraw(whole_grand_total)
                    o.pay_with_wallet = "Yes"
                    o.save()
                    wallet.save()
                    cart.clear(request)
                    messages.add_message(request, messages.INFO, 'Order Placed Successfully!')
                return HttpResponseRedirect('wallet')
            Order.objects.filter(pk=o.id).update(pv=cart_sub_pv, bv=cart_sub_bv)
            print('..............', o.id, cart_sub_pv, cart_sub_bv)
            request.session['order_id'] = o.id
            orders.append(o)

            cart_sub_bv = cart.subtotal_bv(request, for_total=True, group_cart=group_checkout)
            cart_sub_pv = cart.subtotal_pv(request, for_total=True, group_cart=group_checkout)
            print(cart_sub_bv, cart_sub_pv, "++++++++++++++++cart sub")
            x = Order.objects.filter(pk=o.id, name=request.user.username)

            if group_checkout:
                for or_id in x:
                    Order.objects.filter(pk=or_id.id).update(group_checkout=True, pv=cart_sub_pv, bv=cart_sub_bv,
                                                             grand_total=whole_grand_total,
                                                             shiping_charge=shiping_charge)
            else:
                Order.objects.filter(pk=o.id).update(shiping_charge=shiping_charge)

        pay_option = PaymentMode.objects.all().order_by('priority')
        gateway_code = []
        if pay_option:
            for gateway in pay_option:
                gateway_code.append(str(gateway).split('-', 1)[0])
            for gate in gateway_code:
                print("hoi gateway")
                if gate == "1":
                    payu_gateway = payu_payment_gateway(request, whole_grand_total, group_checkout, orders)
                    return payu_gateway
                elif gate == "2":
                    zaakpay_gateway = zaakpay_payment_gateway(request, whole_grand_total, orders, group_checkout)
                    return zaakpay_gateway
                elif gate == "3":
                    razorpay_gateway = rozorpay_payment_gateway(request, whole_grand_total, orders, group_checkout)
                    return razorpay_gateway
                else:
                    print('No one Gateway may be added in Future')
        else:
            print('please add gateway in mlm_admin')

    else:
        form = CheckoutForm()
        address_form = AddressForm()
    group_checkout_users = 'group_checkout_users_{}'.format(request.user.id)
    is_group_checkout = group_checkout_users in request.session
    cart_items_count = count(request, is_group_checkout, group_checkout_users)
    cart_items = group_cart(request, is_group_checkout, group_checkout_users)
    if cart_items_count == 0:
        messages.warning(request, "You do not have any Product.")
        return redirect('product_list')
    cart_sub_bv = cart.subtotal_bv(request, for_total=True, group_cart=group_checkout)
    cart_sub_pv = cart.subtotal_pv(request, for_total=True, group_cart=group_checkout)

    all_address = Address.objects.filter(user=request.user).order_by('-default')
    all_states = AdminState.objects.all()
    print('test.....', request.user.id)

    params = {'form': form, 'address_form': address_form,
              'cart_subtotal': cart.subtotal(request, for_total=True, group_cart=group_checkout),
              'a_cart_subtotal': cart.a_subtotal(request, for_total=True, group_cart=group_checkout),
              'temp': temp, 'cart_items': cart_items, 'cart_items_count': cart_items_count,
              'cart_sub_bv': cart_sub_bv, 'GROUP_CHECKOUT': settings.GROUP_CHECKOUT,
              'cart_sub_pv': cart_sub_pv,
              'title': 'Check Out',
              'group_checkout': group_checkout,
              'is_group_checkout': is_group_checkout,
              'all_address': all_address,
              'all_states': all_states}

    return render(request, 'checkout.html', params)


def update_address(request):
    if request.method == 'POST':
        ad_id = request.POST.get('id', '')
        user = User.objects.get(id=request.user.id)
        user_email = request.POST.get('user_email', '')
        name = request.POST.get('name', '')
        Landmark = request.POST.get('Landmark', '')
        address_line = request.POST.get('address_line', '')
        city = request.POST.get('city', '')
        pincode = request.POST.get('pincode', '')
        mobile = request.POST.get('mobile', '')
        alternate_mobile = request.POST.get('alternate_mobile', '')
        default = True if request.POST.get('default') == 'true' else False
        print(Landmark, alternate_mobile)
        if user_email != "":
            user = User.objects.get(email=user_email)
            print(user_email)
        if default:
            Address.objects.filter(user=user).update(default=False)

        state = AdminState.objects.get(state_name=request.POST.get('state', ''))

        if ad_id != '':
            address = Address.objects.get(id=ad_id)
            address.name = name
            address.Landmark = Landmark
            address.address_line = address_line
            address.city = city
            address.state = state
            address.pin = pincode
            address.mobile = mobile
            address.alternate_mobile = alternate_mobile
            address.address_type = 'S'
            address.default = default
            address.save()
            return JsonResponse({'status': 200, 'data': "Address Data Updated Succesfully"})
        else:
            Address.objects.create(
                user=user,
                name=name,
                Landmark=Landmark,
                address_line=address_line,
                city=city,
                state=state,
                pin=pincode,
                mobile=mobile,
                alternate_mobile=alternate_mobile,
                address_type='S',
                default=default
            )
            return JsonResponse({'status': 200, 'data': "Address Data Created Succesfully"})

    return JsonResponse({'status': 200, 'data': "Done"})


# def order_summary(request):

#     order_list = LineItem.objects.all()
#     return render(request, 'order.html', {'order_list':order_list})


@login_required(login_url='/checkout')
def withdraw_checkout(request, distributor_id=None, group_checkout=None):
    temp = Address.objects.filter(user=request.user, address_type="B")[0]
    with transaction.atomic():
        wallet = Wallet.objects.get(user=request.user)

    # try:
    #     kyc_done = Kyc.objects.get(kyc_user=request.user).kyc_done
    # except:
    #     kyc_done = False
    #
    # if kyc_done == False:
    #     messages.error(request, "Please verify KYC Details and Bank details. To skip and verify later, please scroll down and select skip for now.")
    #     return redirect('edit_profile')

    if request.method == 'POST':
        amount = float(request.POST["amountt"])
        form = CheckoutForm()
        address_form = AddressForm()
        # cart_items = cart.get_all_cart_items(request, for_total=True)
        group_checkout_users = 'group_checkout_users_{}'.format(request.user.id)
        is_group_checkout = group_checkout_users in request.session
        cart_items_count = count(request, is_group_checkout, group_checkout_users)
        cart_items = group_cart(request, is_group_checkout, group_checkout_users)
        if cart_items_count == 0:
            messages.warning(request, "You do not have any Product.")
            return redirect('product_list')

        cart_sub_bv = cart.subtotal_bv(request, for_total=True)
        cart_sub_pv = cart.subtotal_pv(request, for_total=True)

        if wallet.current_balance < amount:
            pending = amount - wallet.current_balance
            params = {'form': form, 'address_form': address_form,
                      'cart_subtotal': cart.subtotal(request, for_total=True),
                      'a_cart_subtotal': cart.a_subtotal(request, for_total=True, group_cart=group_checkout),
                      'temp': temp, 'cart_items': cart_items,
                      'cart_sub_bv': cart_sub_bv,
                      'cart_sub_pv': cart_sub_pv,
                      'title': 'Check Out',
                      'pay_with_wallet': 'pay_with_wallet',
                      'pending': pending,
                      'cart_items_count': cart_items_count,
                      'GROUP_CHECKOUT': settings.GROUP_CHECKOUT,
                      'withdrawn': wallet.current_balance
                      }

        else:
            with transaction.atomic():
                wallet = Wallet.objects.get(user=request.user)
                remaining_bal = wallet.current_balance - amount
                params = {'form': form, 'address_form': address_form, 'cart_items_checkout': cart_items,
                          'cart_subtotal': cart.subtotal(request, for_total=True),
                          'a_cart_subtotal': cart.a_subtotal(request, for_total=True, group_cart=group_checkout),
                          'temp': temp, 'cart_items': cart_items, 'GROUP_CHECKOUT': settings.GROUP_CHECKOUT,
                          'cart_sub_bv': cart_sub_bv,
                          'cart_sub_pv': cart_sub_pv,
                          'title': 'Check Out',
                          'paid_with_wallet': 'paid_with_wallet',
                          'withdrawn': amount,
                          'remaining_bal': remaining_bal,
                          'wallet_balance': wallet.current_balance,
                          }
        return render(request, 'checkout.html', params)


@login_required(login_url='home')
def order_summary(request):
    req_email = request.user.email
    try:
        order = Order.objects.filter(email=req_email, paid=True)

        if order.count() == 0:
            messages.warning(request, "You do not have any Order.")
            return redirect('product_list')

    except:
        messages.warning(request, "You do not have any Order.")
        return redirect('product_list')

    category = cache.get("auth_category")
    cache_status = False
    if category is None:
        category = Category.objects.filter(is_parent_category='yes', delete=False).order_by('cat_order')
        cache.set("auth_category", category)  # sub_category=Category.objects.filter(is_parent_category='yes')
    else:
        cache_status = True

    categey = cache.get("categey")
    if categey is None:
        categey = Category.objects.filter(is_parent_category='no')
        cache.set("categey", categey)  # sub_category=Category.objects.filter(is_parent_category='yes')
    else:
        cache_status = True
    return render(request, 'order.html', {'order_list': order,
                                          "category": category,
                                          "categey": categey,
                                          'title': 'Order',
                                          'cache_status': cache_status, })


@login_required(login_url='/accounts/login')
def order_details(request, email):
    try:
        req_email = request.user.email
        order = LineItem.objects.filter(order_id=email, order__email=req_email)
        order_other_details = Order.objects.get(pk=email)
        try:
            D_sale = Distributor_Sale.objects.get(order=order_other_details)
        except:
            D_sale = False
        if order.count() == 0:
            messages.warning(request, "You do not have any Order.")
            return redirect('product_list')
    except LineItem.DoesNotExist:
        messages.warning(request, "You do not have any Order.")
        return redirect('product_list')
    return render(request, 'order-details.html',
                  {'order_list': order, 'order_other_details': order_other_details, 'title': 'Order Details',
                   'D_sale': D_sale})


def address_edit(request):
    address_qs = get_object_or_404(Address, user=request.user, address_type='B')
    address_form = AddressForm(instance=address_qs)
    if request.method == 'POST':
        address_form = AddressForm(instance=address_qs, data=request.POST)
        if address_form.is_valid():
            address_form.save()
            messages.success(request, "Address Updated Successfully!")
            return HttpResponseRedirect(reverse('checkout'))
    return render(request, 'edit_address.html', {'address_form': address_form,
                                                 'title': 'Edit Address'
                                                 })


@csrf_exempt
def filter_list(request):
    # aa =(request.POST['radioValue'])
    aa = 200
    bb = (request.POST.getlist('checkValue[]'))

    categories = Category.objects.filter(cat_name__in=bb, delete=False)

    cat_list = []
    for i in categories:
        cat_list.append(i)
        for k in i.category_set.all():
            cat_list.append(k)
    all_products = Product.objects.filter(category__in=cat_list, price__lte=aa, delete=False)
    params = {
        'all_products': all_products,
    }
    # abc = list(all_products)
    # if all_products:
    #     abc = list(all_products.values())
    # else:
    #     messages.warning(request,  "No Product Found.")
    #     return redirect('product_list')
    # print (abc)
    # nipur code start 2 feb
    return render(request, 'suport_filter.html', params)
    # nipur code end 2 feb
    # return JsonResponse({'all_products': abc,})


def filetr_view(request):
    aa = request.GET.get('radioValue', False)
    # print (request)
    # if (aa == "1"):
    cache_status = False
    all_products = cache.get("all_products")
    if all_products is None:
        all_products = Product.objects.filter(delete=False)
        cache.set("all_products", all_products)
    else:
        cache_status = True

    params = {
        'all_products': all_products,
        'aa': aa,
        'cache_status': cache_status,
    }
    return render(request, 'suport_filter_view.html', params)


#  sattic page link
def about_us(request):
    return render(request, 'about_us.html', {})


def contact_us(request):
    return render(request, 'contact_us.html', {})


def return_policy(request):
    return render(request, 'return_policy.html', {})


def support_policy(request):
    return render(request, 'support_policy.html', {})


def faqs(request):
    return render(request, 'faqs.html', {})


def size_guide(request):
    return render(request, 'size_guide.html', {})


# @cache_page(CACHE_TTL)
def js_product(request, myid):
    # l=[]
    # data = Product.objects.all()
    # data = list(data)
    # l.append(data)
    # context={
    #     'product':l
    # }
    # return render(request,'variant_prod.html',context)
    all_products = Product.objects.filter(pk=myid).order_by("price").values()
    aa = list(all_products)
    return JsonResponse({'product': aa})


@csrf_exempt
def ajax_product_quantity(request):
    if request.method == 'POST':
        prod_id = request.POST.get('product_id')
        qty = request.POST.get('qty')
        today = date.today()
        batchs = Batch.objects.filter(product_id=prod_id, delete=False).order_by(
            "date_of_expiry")
        prod = Product.objects.get(pk=prod_id)
        if prod.expiration_dated_product == 'YES':
            batchs = batchs.filter(date_of_expiry__gte=today)
        batch = batchs.first()
        try:
            batch = Batch.objects.get(pk=batch.pk)
            material = Material_center.objects.get(frontend=True)
            inventory = Inventry.objects.filter(product_id=prod_id, batch=batch, material_center=material).latest(
                'created_on')
            if (int(qty) > 0 and int(qty) <= inventory.current_quantity):
                qty = inventory.current_quantity
                result = 200
            else:
                qty = inventory.current_quantity
                result = 404
        except:
            qty = 0
            result = 404
        return JsonResponse({'qty': qty, 'result': result})


#
def payment(request):
    return render(request, 'home.html')


#
#
# from portal_auretics_com.settings import

def payu_demo(request):
    data = {
        'amount': '1', 'firstname': 'nipur',
        'email': 'nipursinghpal@gmail.com',
        'phone': '7532046631', 'productinfo': 'test', 'lastname': 'test', 'address1': 'test',
        'address2': 'test', 'city': 'test', 'state': 'test', 'country': 'test',
        'zipcode': 'tes', 'udf1': '', 'udf2': '', 'udf3': '', 'udf4': '', 'udf5': ''
    }
    txnid = "0923dskf9978"
    data.update({"txnid": txnid})
    payu_data = payu.transaction(**data)
    # Make sure the transaction ID is unique
    # payu_data = payu.transaction(**data)
    return render(request, 'payu_checkout.html', {"posted": payu_data})


@csrf_exempt
def payu_success(request):
    data = {k: v[0] for k, v in dict(request.POST).items()}
    response = payu.verify_transaction(data)
    data = response['return_data']
    # data = {
    #     'mihpayid': '23123',
    #     'mode': 'Cash',
    #     'status': 'Completed',
    #     'txnid': '2423',
    #     'amount': '2123',
    #     'net_amount_debit': '2123',
    #     'addedon': '2022-01-15',
    #     'hash': 'dasdasda',
    #     'bank_ref_num': 'rsadsa',
    #     'bankcode': 'bankcode',
    #     'error_Message': 'error_Message',
    #     'zipcode': '8730',
    #     'country': 'india'
    # }
    mihpayid = data['mihpayid']
    mode = data['mode']
    status = data['status']
    order_number = data['txnid']
    amount = data['amount']
    # cardCategory = data['cardCategory']
    net_amount_debit = data['net_amount_debit']
    addedon = data['addedon']
    hash = data['hash']
    bank_ref_num = data['bank_ref_num']
    bankcode = data['bankcode']
    error_Message = data['error_Message']
    # cardnum = data['cardnum']
    # name_on_card = data['name_on_card']
    # generated_hash = data['generated_hash']
    # recived_hash = data['recived_hash']
    # hash_verified = data['hash_verified']
    order_id = data['zipcode']
    payment_qs = Payment(order_id=order_id, order_number=order_number, mihpayid=mihpayid, mode=mode, status=status,
                         amount=amount,
                         net_amount_debit=net_amount_debit, hash=hash, bank_ref_num=bank_ref_num,
                         bankcode=bankcode, error_Message=error_Message, timestamp=addedon)
    payment_qs.save()
    Order.objects.filter(pk=order_id).update(paid=True)
    group_order_ids = 'order_ids_{}'.format(order_id)
    if group_order_ids in request.session:
        group_order_ids = request.session[group_order_ids]
        Order.objects.filter(id__in=group_order_ids).update(paid=True)
        del request.session[group_order_ids]
    cart_id = data['country']
    request.session['cart_id'] = cart_id
    order_data = Order.objects.get(pk=order_id)
    user = User.objects.get(email=order_data.email)
    # updaate_super_bv(order_data.bv,user)
    # cart.clear(request, user_id=user.id)
    result = after_success(order_number, order_id)

    messages.add_message(request, messages.INFO, 'Order Placed Successfully!')
    return redirect('order_summary')
    # return JsonResponse(response)


# failure
def failure(request):
    return render(request, 'payment_failure.html')


@login_required(login_url='home')
def invoice_check(request, myid):
    sale = Order.objects.get(pk=myid, delete=False)
    try:
        D_sale = Distributor_Sale.objects.get(order=sale)
    except:
        D_sale = Objectify()
        D_sale.sale_user_id_id = False
        D_sale.Objectified = True

    if sale.email == request.user.email or \
            D_sale.sale_user_id_id == request.user.id or \
            request.user.profile.mlm_admin:
        try:
            if D_sale.Objectified == True:
                D_sale = False
        except:
            pass
        return render(request, 'invoice.html', {'sale': sale, 'title': 'Invoice', 'D_sale': D_sale})
    else:
        messages.add_message(request, messages.INFO, 'You are not authorised!')
        return redirect(order_summary)


def after_success(order_number, order_pk):
    order_item = Order.objects.filter(pk=order_pk).first()
    line_items = LineItem.objects.filter(order__pk=order_pk)
    for line_item in line_items:
        today = date.today()
        # here we are subtracting the quantity from the batch quantity start here
        batchs = Batch.objects.filter(product=line_item.product,
                                      delete=False,
                                      ).order_by(
            "date_of_expiry")
        if line_item.product.expiration_dated_product == 'YES':
            batchs = batchs.filter(date_of_expiry__gte=today)
        batch = batchs.first()
        quantity = (batch.quantity - line_item.quantity)
        Batch.objects.filter(pk=batch.pk).update(quantity=quantity)
        batch = Batch.objects.get(pk=batch.pk)
        material = order_item.material_center or Material_center.objects.get(frontend=True)
        # <here  we are subtracting quantity from the inventory sudo -u postgres psql20-03-2021 start here
        try:
            today = datetime.datetime.now().date()
            inventory_update = Inventry.objects.get(product=line_item.product, batch=batch,
                                                    material_center=material,
                                                    created_on=today)
            inventory_update_current_quantity = int(inventory_update.current_quantity) - int(line_item.quantity)
            inventory_update_quantity_out = int(inventory_update.quantity_out) + int(line_item.quantity)
            Inventry.objects.filter(product=line_item.product, batch=batch, material_center=material,
                                    created_on=today).update(
                current_quantity=inventory_update_current_quantity,
                quantity_out=inventory_update_quantity_out)
        except:
            # here add code for inventry start here 20-03-2021
            try:
                inventory_update = Inventry.objects.filter(product=line_item.product, batch=batch,
                                                           material_center=material).latest(
                    'created_on')
                current_quantity = int(inventory_update.current_quantity) - int(line_item.quantity)
                inventory = Inventry(product=line_item.product, batch=batch, material_center=material,
                                     opening_quantity=inventory_update.current_quantity,
                                     current_quantity=current_quantity,
                                     quantity_out=line_item.quantity, purchase_price=inventory_update.purchase_price)
                inventory.save()
            except:
                inventory = Inventry(product=line_item.product, batch=batch, material_center=material,
                                     opening_quantity=0, current_quantity=line_item.quantity,
                                     quantity_out=line_item.quantity)
                inventory.save()
        LineItem.objects.filter(pk=line_item.pk).update(batch=batch)
    return True


from django.contrib.auth import login


def payment_failure_login(request, email):
    # here we are writing code for recaptchar
    user = User.objects.get(email=email)
    login(request, user)
    if request.session['cart_id']:
        cart_id = request.session['cart_id']
        cart_session_item = CartItem.objects.filter(cart_id=cart_id)
        # <--!-------------------------------------------nipur code start 9-02-2021--------------------------------------------------------!-->
        if len(cart_session_item) > 0:
            cart_user_item = CartItem.objects.filter(user=user).first()
            if cart_user_item != None:
                user_database_cart_id = cart_user_item.cart_id
            cart_user_item_delete = CartItem.objects.filter(user=user).delete()
            CartItem.objects.filter(cart_id=cart_id).update(user=user)
            if cart_user_item != None:
                CartItem.objects.filter(user=user).update(cart_id=user_database_cart_id)
                request.session['cart_id'] = user_database_cart_id
        else:
            cart_user_item = CartItem.objects.filter(user=user).first()
            if cart_user_item != None:
                request.session['cart_id'] = cart_user_item.cart_id
    # <--!-------------------------------------------nipur code end 9-02-2021--------------------------------------------------------!-->

    else:
        cart_id = CartItem.objects.filter(user=request.user).first()
        for i in cart_id:
            request.session['i.cart_id'] = i.cart_id

    return request


#     nipur code end

def clear_cart(request):
    data = cart.clear_Cart(request)
    return redirect('home')


class DistributorList(ListView):
    template_name = 'distributor/distributor_list.html'
    model = Material_center


class SetDistributorCheckout(View):

    def get(self, request, *ar, **kwargs):
        distributor_obj = Material_center.objects.get(id=kwargs['pk'])
        request.session['distributor_checkout'] = distributor_obj.id
        cart_items = cart.get_all_cart_items(request)
        if cart_items and request.user.is_authenticated:
            cart_items = list(cart_items.values_list('id', flat=True))
            request.session['cart_warehouse_{}'.format(request.user.id)] = cart_items
        group_checkout_users = 'group_checkout_users_{}'.format(request.user.id)
        if group_checkout_users in request.session:
            del request.session[group_checkout_users]
        return HttpResponseRedirect('/')


class RemoveDistributorCheckout(View):

    def get(self, request, *ar, **kwargs):
        if 'distributor_checkout' in request.session:
            del request.session['distributor_checkout']
            if request.user.is_authenticated and 'cart_warehouse_{}'.format(request.user.id) in request.session:
                cart.clear_Cart(request, warehouse_cart=True)
        return HttpResponseRedirect('/')


class AddItemsGroupCheckout(View):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = request.POST
        user = data.get('group-user', '')
        if user:
            user_id = ''
            if User.objects.filter(email__iexact=user).exists():
                user_id = User.objects.filter(email__iexact=user)[0]
            elif Profile.objects.filter(phone_number__iexact=user).exists():
                user_id = Profile.objects.filter(phone_number__iexact=user)[0].user
            elif ReferralCode.objects.filter(referral_code=user).exists():
                user_id = ReferralCode.objects.get(referral_code__iexact=user).user_id
            if user_id:
                # cart_items = cart.get_all_cart_items(request)
                group_checkout_users = 'group_checkout_users_{}'.format(request.user.id)
                if group_checkout_users in request.session:
                    users = request.session[group_checkout_users]
                    if user_id.id not in users:
                        users.append(user_id.id)
                        items = CartItem.objects.filter(user__id=user_id.id, in_stock=True)
                        for item in items:
                            ci = get_object_or_404(CartItem, id=item.id)
                            ci.delete()
                    request.session[group_checkout_users] = users
                else:
                    request.session[group_checkout_users] = [request.user.id, user_id.id]
                print(request.session[group_checkout_users], "USERS")
            else:
                messages.add_message(request, messages.INFO, "User is not Register.")
                return redirect('checkout')
        return HttpResponseRedirect(reverse('group-checkout'))


def error_404_view(request, exception):
    data = {"name": "auretics.com"}
    return render(request, (os.path.join(os.path.dirname(os.path.dirname(__file__)), "static/html/404.html")), data)


razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))


@csrf_exempt
def razorpay_success(request):
    response = request.POST
    razorpay_payment_id = response['razorpay_payment_id'],
    razorpay_order_id = response['razorpay_order_id'],
    razorpay_signature = response['razorpay_signature']

    params_dict = {
        'razorpay_payment_id': response['razorpay_payment_id'],
        'razorpay_order_id': response['razorpay_order_id'],
        'razorpay_signature': response['razorpay_signature']
    }

    # VERIFYING SIGNATURE
    try:
        status = razorpay_client.utility.verify_payment_signature(params_dict)
        order_id = request.session['order_id']
        Order.objects.filter(pk=order_id).update(paid=True)
        group_order_ids = 'order_ids_{}'.format(order_id)
        if group_order_ids in request.session:
            group_order_ids = request.session[group_order_ids]
            Order.objects.filter(id__in=group_order_ids).update(paid=True)
            # del request.session[group_order_ids]
        cart_id = request.session['cart_id']
        order_data = Order.objects.get(pk=order_id)
        user = User.objects.get(email=order_data.email)
        order_number = str(order_data.order_id1) + "-" + str(user) + "-" + str(datetime.datetime.now().hour) + str(
            datetime.datetime.now().minute)
        payment_qs = Payment(order_id=order_data.pk, order_number=order_number,
                             mihpayid=razorpay_payment_id[0], razorpay_signature=razorpay_signature,
                             status='success', net_amount_debit=order_data.grand_total, amount=order_data.grand_total, )
        payment_qs.save()
        cart.clear(request, user_id=user.id)
        result = after_success(order_number, order_id)
        messages.add_message(request, messages.INFO, 'Order Placed Successfully!')
        return redirect('order_summary')
    except:
        return redirect('razorpay_failure')


@csrf_exempt
def zaakpay_callback(request):
    data = {k: v[0] for k, v in dict(request.POST).items()}
    mihpayid = settings.ZAAKPAY_MERCHANT_IDENTIFIER
    mode = data['paymentMode']
    order_number = data['orderId']
    hash = data['cardhashid']
    bank_ref_num = data['bank']
    bankcode = data['bankid']
    status = data['responseDescription']
    response_code = data['responseCode']
    order_id1 = data['product4Description']
    ord = data['product2Description']

    sperate = order_id1.split("-")
    order = []
    for c in sperate:
        order.append(int(c))
    if response_code == 100:
        for order_id in order:
            Order.objects.filter(pk=order_id).update(paid=True)

        grand_total = data['product1Description']
        payment_qs = Payment(order_id=ord, order_number=order_number, mihpayid=mihpayid, mode=mode,
                             status=status, amount=grand_total,
                             net_amount_debit=grand_total, hash=hash, bank_ref_num=bank_ref_num,
                             bankcode=bankcode)
        payment_qs.save()
        for card in order:
            card_id = Order.objects.filter(pk=card)
            for s in card_id:
                items = CartItem.objects.filter(user__id=s.user_id.id, in_stock=True)
                for item in items:
                    ci = get_object_or_404(CartItem, id=item.id)
                    ci.delete()
        result = after_success(order_number, ord)
        messages.add_message(request, messages.INFO, 'Order Placed Successfully!')
        return redirect('order_summary')
    else:
        messages.add_message(request, messages.INFO, status)
        return redirect('zaakpay_failure')


def group_cart(request, is_group_checkout, group_checkout_users):
    cart_items_count = 0
    cart_items = {}
    if is_group_checkout:
        users = request.session[group_checkout_users]
        for cart_group_user in users:
            cart_group_user_name = User.objects.get(id=cart_group_user)
            items = cart.get_group_user_cart_items([cart_group_user])
            cart_items_count += items.count()
            cart_items.update({cart_group_user_name: items})
    elif request.user.is_authenticated:
        cart_user_name = request.user.profile.first_name if request.user.is_authenticated else ''
        items = CartItem.objects.filter(user_id=request.user.id, in_stock=True)
        cart_items.update({cart_user_name: items})
    else:
        cart_items = None
    return cart_items


def count(request, is_group_checkout, group_checkout_users):
    cart_items_count = 0
    cart_items = {}
    if is_group_checkout:
        users = request.session[group_checkout_users]
        for cart_group_user in users:
            cart_group_user_name = User.objects.get(id=cart_group_user)
            items = cart.get_group_user_cart_items([cart_group_user])
            cart_items_count += items.count()
            cart_items.update({cart_group_user_name: items})
    elif request.user.is_authenticated:
        items = CartItem.objects.filter(user_id=request.user.id, in_stock=True)
        cart_items_count = items.count()
    else:
        cart_items_count = None
    return cart_items_count


@login_required(login_url='home')
def group_checkout(request):
    group_checkout_users = 'group_checkout_users_{}'.format(request.user.id)
    is_group_checkout = group_checkout_users in request.session
    cart_items_count = count(request, is_group_checkout, group_checkout_users)
    cart_items = group_cart(request, is_group_checkout, group_checkout_users)
    context = {'is_group_checkout': is_group_checkout,
               'cart_items': cart_items,
               'cart_items_count': cart_items_count, 'GROUP_CHECKOUT': settings.GROUP_CHECKOUT,
               'title': 'Group Check Out | Auretics Limited', }
    return render(request, "group_checkout.html", context)


class LatestSoldProductsView(View):
    def post(self, request):
        all_products = Product.objects.all()
        print("Product", all_products)
        total_sale_product = LineItem.object.get(total_amount=total_amount)
        count_monthly = total_sale_product / price
        for data in all_products:
            product_sale = Product.objects.values('product_name').annotate(monthly_sales=Sum('monthly_sales')) \
                .order_by('monthly_sales')
            product_sale.monthly_sales.save()
        return redirect(product_sale)
