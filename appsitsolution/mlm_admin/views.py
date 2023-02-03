import json
from django.http.response import HttpResponseRedirect

import requests
import xlwt
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.http import JsonResponse
from django.urls import reverse
from accounts.bank_proof import Bank_proof_api, Pan_verification
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from accounts.forms import *
from accounts.models import *
from wallet.models import Transaction
from distributor.models import *
from distributor.views import quantity_validate
from mlm_admin.decorator import allowed_users
from .forms import Categoryform, Categoryformview, Productform, Productformview, Orderform, Batchform, Batchformview, \
    Materialform, Materialformview, Bannerform, Bannerformview, Referralview, Referral, AddressForm, CheckForm, \
    ShipCharge, UploadFileForm, AddGatewayForm, PriorityGatewayForm, MobileNumberForm, EmailForm, SheetConfigForm
from .models import *
from .common_code import *
from shop.calculation import calculated_business_value, calculated_point_value
from .sr_api_call import OrderMaintain
from .utils import get_order_list_for_mlm_admin
from realtime_calculation.models import RealTimeDetail
from mlm_calculation.models import title_qualification_calculation_model, consistent_retailers_income, \
    commission_wallet_model, inner_configurations, commission_wallet_amount_out_detail_model
from activitylog.models import UserLoginActivity
from django.db import transaction
from business.views import month, year, last_month, last_year, previous_month, month_name

from django.views.decorators.cache import cache_page
from django.core.cache import cache
# Create your views here.
from accounts.sms import sendsms
import accounts.views
from wallet.models import Wallet
from .views_notify import *
from distributor.cron import update_inventry
from payment_gateway.models import Gateway, PaymentMode
from django.views.generic.edit import FormView, View, UpdateView
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.contrib.messages.views import SuccessMessageMixin
from datetime import datetime, date, timedelta
from distributor.recalculate import recalculate_everything
import os
import psutil

from mlm_admin.dv_api import DelhiveryApi
from mlm_admin.pickrr_api import PickrrApi
from mlm_admin.send_to_gs import SendToGS
from shop.models import Address
import time
import fiscalyear


class Objectify(object):
    pass


def is_mlm_admin(user):
    try:
        return user.is_authenticated and user.profile.mlm_admin is not False
    except Profile.DoesNotExist:
        return False


def is_super_admin(user):
    try:
        print(user, )
        return user.is_authenticated and user.profile.super_admin is not False
    except Profile.DoesNotExist:
        return False


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
def home(request):
    cpu_percent = psutil.cpu_percent()
    cpu_load_avg = psutil.getloadavg()

    permit_F = os.access('does_not_exist.txt', os.F_OK)
    permit_R = os.access('does_not_exist.txt', os.R_OK)
    permit_W = os.access('does_not_exist.txt', os.W_OK)
    permit_X = os.access('does_not_exist.txt', os.X_OK)

    no_of_users = User.objects.filter().count()

    monthly_bv = []
    monthly_bv_month = []
    monthly_order = []
    monthly_order_bv = 0
    prev_month, prev_year = month,year
    for x in range(12):
        monthly_order = Order.objects.filter(date__month=prev_month, date__year=prev_year, paid=True, delete=False).exclude(
        status=8).exclude(email="stockvariance@auretics.com").exclude(email="loyalty@auretics.com")
        monthly_order_bv = sum([li.bv for li in monthly_order])/1000
        monthly_bv.append(int(monthly_order_bv))

        monthly_bv_month.append(int(prev_month))
        prev_month, prev_year = previous_month(prev_month, prev_year)

    daily_bv = []
    daily_bv_date = []
    daily_order = []
    daily_order_bv = 0
    date_now = datetime.now()
    for x in range(30):
        daily_order = Order.objects.filter(date__day=date_now.day, date__month=date_now.month,
                                           date__year=date_now.year, paid=True, delete=False).exclude(
                                           status=8).exclude(email="stockvariance@auretics.com").exclude(
                                           email="loyalty@auretics.com")
        daily_order_bv = sum([li.bv for li in daily_order])/1000
        daily_bv.append(int(daily_order_bv))

        daily_bv_date.append(int(date_now.day))
        date_now = date_now - timedelta(days=1)

    monthly_bv.reverse()
    monthly_bv_month.reverse()
    daily_bv.reverse()
    daily_bv_date.reverse()

    return render(request, 'mlm_admin/base.html', {'title': 'Auretics Dashboard',
                                                   'cpu_percent':cpu_percent,
                                                   'cpu_load_avg':cpu_load_avg,
                                                   'permit_F':permit_F,
                                                   'permit_R':permit_R,
                                                   'permit_R':permit_W,
                                                   'permit_X':permit_X,
                                                   'no_of_users':no_of_users,
                                                   'monthly_bv':monthly_bv,
                                                   'monthly_bv_month':monthly_bv_month,
                                                   'daily_bv':daily_bv,
                                                   'daily_bv_date':daily_bv_date})


def Clear_cache(request):
    try:
        cache.clear()
        messages.success(request, "Cache Cleared")
    except:
        messages.error(request, "cache was not cleared")
    return redirect("mlm_admin")


def Auto_pincode(request):
    if 'pincode' in request.GET:
        qs = Pincode.objects.filter(pin__istartswith=request.GET.get('pincode'))
        pin_co = list()
        for pin in qs:
            pin_co.append(pin.state_name)
            pin_co.append(pin.city)
        return HttpResponse(pin_co)
    return render(request, 'templates/registration.html')


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['category_management', ['1']])
def add_category(request):
    # if '1' not in request.user.menu_permission.category_management:
    #     return redirect('mlm_admin')
    form = Categoryform()
    if request.method == 'POST':
        form = Categoryform(request.POST, request.FILES)
        if form.is_valid():
            dataform = form.save(commit=False)
            parent_category_id = request.POST['parent_category']
            try:
                category = Category.objects.get(pk=parent_category_id)
                dataform.parent_category_id = category
            except:
                pass
            dataform.save()
            messages.success(request, 'Category has been added Successfully')
            return redirect('category-list')
        else:
            print(form.errors)
            return HttpResponse('<h1>Please check what is going wrong with it.</h1>')

    data = Category.objects.filter(is_parent_category='yes')
    params = {
        'form': form,
        'data': data,
        'title': 'Add Category'
    }
    return render(request, 'mlm_admin/add_category.html', params)


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['category_management', ['1', '2', '3', '4']])
def category_list(reqeust):
    data = Category.objects.all().exclude(delete=True)
    return render(reqeust, 'mlm_admin/category-list.html', {'data': data, 'title': 'Category List'})


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['category_management', ['2']])
def edit_category(request, myid):
    category_qs = get_object_or_404(Category, pk=myid)
    parent_id = category_qs.parent_category_id
    image = category_qs.imag_path
    form = Categoryform(instance=category_qs)
    if request.method == 'POST':
        form = Categoryform(instance=category_qs, data=request.POST, files=(request.FILES or None), )
        dataform = form.save(commit=False)
        parent_category_id = request.POST['parent_category']
        try:
            category = Category.objects.get(pk=parent_category_id)
            dataform.parent_category_id = category
        except:
            pass
        dataform.save()
        messages.success(request, "Updated Record Updated Successfully!")
        return redirect('category-list')
    data = Category.objects.filter(is_parent_category='yes').exclude(pk=myid)
    return render(request, 'mlm_admin/edit_category.html', {
        'form': form, 'data': data, 'parent_id': parent_id, 'image': image, 'title': 'Edit Category'
    })


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['category_management', ['3']])
def view_category(request, myid):
    category_qs = get_object_or_404(Category, pk=myid)
    image = category_qs.imag_path
    parent_id = category_qs.parent_category_id
    form = Categoryformview(instance=category_qs)
    data = Category.objects.all().exclude(pk=myid)
    return render(request, 'mlm_admin/view_category.html', {
        'form': form, 'data': data, 'parent_id': parent_id, 'image': image, 'title': 'View Category'
    })


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['category_management', ['4']])
def delete_category(request, myid):
    Category.objects.filter(pk=myid).update(delete=True)
    category = Category.objects.get(pk=myid)
    category.category_set.filter().update(delete=True)
    messages.success(request, "Category Deleted Successfully!")
    return redirect('category-list')


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['product_management', ['1']])
def add_product(request):
    form = Productform()
    if request.method == 'POST':
        form = Productform(request.POST, request.FILES)
        if form.is_valid():
            dataform = form.save(commit=False)
            cat_id = request.POST['category']
            cat = Category.objects.get(pk=cat_id)
            gendar_id = request.POST['gender']
            gender = Gender.objects.get(pk=gendar_id)
            dataform.category = cat
            dataform.product_gender_name = gender
            # code start 21/1/2021
            variant = request.POST['variant']
            if variant == 'YES':
                main_variant_data = request.POST['main_variant_data']
                variant_name = request.POST['variant_name']
                variant_based_on = request.POST['variant_based_on']
                variant_tag = request.POST['variant_tag']
                try:
                    variant_tag = Product.objects.get(pk=variant_tag)
                    if main_variant_data == 'YES':
                        prod_Data = Product_Variant(product=dataform, variant=variant, main_variant=main_variant_data,
                                                    variant_name=variant_name, variant_based_on=variant_based_on,
                                                    variant_tag=dataform)
                        # prod_Data.save()
                        dataform.main_variant = True
                    elif main_variant_data == 'NO':
                        prod_Data = Product_Variant(product=dataform, variant=variant, main_variant=main_variant_data,
                                                    variant_name=variant_name, variant_based_on=variant_based_on,
                                                    variant_tag=variant_tag)
                        # prod_Data.save()
                        dataform.main_variant = False
                except:
                    if main_variant_data == 'YES':
                        prod_Data = Product_Variant(product=dataform, variant=variant, main_variant=main_variant_data,
                                                    variant_name=variant_name, variant_based_on=variant_based_on,
                                                    variant_tag=dataform)

                        dataform.main_variant = True
                    elif main_variant_data == 'NO':
                        prod_Data = Product_Variant(product=dataform, variant=variant, main_variant=main_variant_data,
                                                    variant_name=variant_name, variant_based_on=variant_based_on)
                        # prod_Data.save()
                        dataform.main_variant = False
                # code end 21/1/2021
                dataform.save()
                prod_Data.save()
            else:
                prod = Product_Variant(product=dataform, variant_tag=dataform)
                dataform.save()
                prod.save()
            messages.success(request, 'Product has been added Successfully')
            return redirect('product-list')
        else:
            print(form.errors)
            return HttpResponse('<h1>Please Check Somthing is going worng</h1>')
    cat = Category.objects.filter(is_parent_category='no').exclude(delete=True)
    gender = Gender.objects.all()
    brand = Brand.objects.all()
    product = Product.objects.filter(main_variant=True).exclude(delete=True)
    params = {
        'form': form,
        'cat': cat,
        'gender': gender,
        'brand': brand,
        'product': product,
        'title': 'Add Product'
    }
    return render(request, 'mlm_admin/add_product.html', params)


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['product_management', ['1', '2', '3', '4']])
def product_list(request):
    product = Product.objects.all().exclude(delete=True).exclude(category__delete=True)
    return render(request, 'mlm_admin/product-list.html', {'product': product, 'title': 'Product List'})

@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['product_management', ['2']])
def copy_product(request, myid):
    # AG :: We will copy product as well its variant
    product_qs = Product.objects.get(pk=myid)
    product_qs.pk = None
    product_qs.id = None
    product_qs.save()
    product_name = product_qs.product_name
    product_name = product_name + " Cloned on " + str(datetime.now().date()) + " at " + str(datetime.now().time())
    product_qs.product_name = product_name
    product_qs.save()

    # AG :: Copying variant and allocating it to the new product_qs
    variant_qs = Product_Variant.objects.get(product__pk=myid)
    variant_qs.pk = None
    variant_qs.id = None
    variant_qs.product = None
    variant_qs.save()
    variant_qs.product = product_qs
    variant_qs.variant_tag = product_qs
    variant_qs.save()
    return redirect('edit_product', myid=product_qs.pk)


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['product_management', ['2']])
def edit_product(request, myid):
    queryset = Product.objects.exclude(delete=True)
    product_qs = get_object_or_404(queryset, pk=myid)
    cat_id = product_qs.category.pk
    gender_id = product_qs.product_gender_name.pk
    brand_id = product_qs.product_brand.pk
    image = product_qs.image
    image2 = product_qs.image2
    image3 = product_qs.image3
    image4 = product_qs.image4
    image5 = product_qs.image5
    image6 = product_qs.image6
    image7 = product_qs.image7
    image8 = product_qs.image8
    image9 = product_qs.image9
    image10 = product_qs.image10
    try:
        prod_id = product_qs.tag.pk
    except:
        prod_id = 0
    if request.method == 'POST':
        form = Productform(instance=product_qs, data=request.POST, files=(request.FILES or None), )
        dataform = form.save(commit=False)
        cat = request.POST['category']
        gender = request.POST['gender']
        cat = Category.objects.get(pk=cat)
        gendar = Gender.objects.get(pk=gender)
        dataform.category = cat
        dataform.product_gender_name = gendar
        variant = request.POST['variant']
        if variant == 'YES':
            variant_pk = request.POST['variant_pk']
            main_variant_data = request.POST['main_variant_data']
            print(main_variant_data, 'main_variant_data')
            variant_name = request.POST['variant_name']
            variant_based_on = request.POST['variant_based_on']
            variant_tag = request.POST['variant_tag']
            try:
                value = Product_Variant.objects.get(pk=variant_pk)
                variant_tag = Product.objects.get(pk=variant_tag)
                data = Product_Variant.objects.filter(pk=variant_pk).update(variant=variant,
                                                                            main_variant=main_variant_data,
                                                                            variant_name=variant_name,
                                                                            variant_based_on=variant_based_on,
                                                                            variant_tag=variant_tag)
            except:
                try:
                    variant_tag = Product.objects.get(pk=variant_tag)
                    if main_variant_data == 'YES':
                        prod_Data = Product_Variant(product=dataform, variant=variant, main_variant=main_variant_data,
                                                    variant_name=variant_name, variant_based_on=variant_based_on,
                                                    variant_tag=variant_tag)
                        prod_Data.save()
                        dataform.main_variant = True
                    elif main_variant_data == 'NO':
                        prod_Data = Product_Variant(product=dataform, variant=variant, main_variant=main_variant_data,
                                                    variant_name=variant_name, variant_based_on=variant_based_on,
                                                    variant_tag=variant_tag)
                        prod_Data.save()
                        dataform.main_variant = False
                except:
                    if main_variant_data == 'YES':
                        prod_Data = Product_Variant(product=dataform, variant=variant, main_variant=main_variant_data,
                                                    variant_name=variant_name, variant_based_on=variant_based_on)
                        prod_Data.save()
                        dataform.main_variant = True
                    elif main_variant_data == 'NO':
                        prod_Data = Product_Variant(product=dataform, variant=variant, main_variant=main_variant_data,
                                                    variant_name=variant_name, variant_based_on=variant_based_on)
                        prod_Data.save()
                        dataform.main_variant = False
        else:
            variant_pk = request.POST['variant_pk']
            main_variant_data = request.POST['main_variant_data']
            print(main_variant_data, 'main_variant_data')
            variant_name = request.POST['variant_name']
            variant_based_on = request.POST['variant_based_on']
            variant_tag = request.POST['variant_tag']
            data = Product_Variant.objects.filter(pk=variant_pk).update(variant=variant, main_variant=main_variant_data,
                                                                        variant_name=variant_name,
                                                                        variant_based_on=variant_based_on,
                                                                        variant_tag=variant_tag)

        dataform.save()
        messages.success(request, "Updated the Profile Successfully!")
        return redirect('product-list')
    cat = Category.objects.filter(is_parent_category='no').exclude(delete=True)
    gender = Gender.objects.all()
    brand = Brand.objects.all()
    form = Productform(instance=product_qs)
    product = Product.objects.filter(delete=False, main_variant=True)

    if 'Clone' in product_qs.product_name:
        clone_option = False
    else:
        clone_option = True

    params = {
        'form': form,
        'cat': cat,
        'gender': gender,
        'brand': brand,
        'cat_id': cat_id,
        'gender_id': gender_id,
        'brand_id': brand_id,
        'image': image,
        'image2': image2,
        'image3': image3,
        'image4': image4,
        'image5': image5,
        'image6': image6,
        'image7': image7,
        'image8': image8,
        'image9': image9,
        'image10': image10,
        'product': product,
        'prod_id': prod_id,
        'product_qs': product_qs,
        'title': 'Edit Product',
        'myid':myid,
        'clone_option':clone_option,
    }
    return render(request, 'mlm_admin/edit_product.html', params)


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['product_management', ['3']])
def view_product(request, myid):
    product_qs = get_object_or_404(Product, pk=myid)
    cat_id = product_qs.category.pk
    gendar_id = product_qs.product_gender_name.pk
    brand_id = product_qs.product_brand.pk
    form = Productformview(instance=product_qs)
    try:
        prod_id = product_qs.tag.product_name
    except:
        prod_id = "No Tag Selected"
    cat = Category.objects.all().exclude(delete=True)
    gendar = Gender.objects.all()
    brand = Brand.objects.all()
    product = Product.objects.all().exclude(delete=True)
    image = product_qs.image
    image2 = product_qs.image2
    image3 = product_qs.image3
    image4 = product_qs.image4
    image5 = product_qs.image5
    image6 = product_qs.image6
    image7 = product_qs.image7
    image8 = product_qs.image8
    image9 = product_qs.image9
    image10 = product_qs.image10
    params = {
        'form': form,
        'cat': cat,
        'gendar': gendar,
        'brand': brand,
        'cat_id': cat_id,
        'gendar_id': gendar_id,
        'brand_id': brand_id,
        'image': image,
        'image2': image2,
        'image3': image3,
        'image4': image4,
        'image5': image5,
        'image6': image6,
        'image7': image7,
        'image8': image8,
        'image9': image9,
        'image10': image10,
        'prod_id': prod_id,
        'product_qs': product_qs,
        'product': product,
        'title': 'View Product'
    }
    return render(request, 'mlm_admin/view_product.html', params)


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['product_management', ['4']])
def delete_product(request, myid):
    product = Product.objects.filter(pk=myid).update(delete=True)
    messages.success(request, "Product Deleted Successfully!")
    return redirect('product-list')


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['order_management', ['1', '2', '3', '4']])
def order_list(request, cf=False):
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        data = get_order_list_for_mlm_admin(cf).filter(
            Q(name__icontains=q) | Q(order_id1__icontains=q) | Q(date__icontains=q) | Q(grand_total__contains=q),
            status=None, delete=False, paid=True ).order_by('id')
    else:
        q = ''
        data = get_order_list_for_mlm_admin(cf).filter(status=None).order_by('id')

    new_data = get_order_list_for_mlm_admin(cf).filter(
        Q(name__icontains=q) | Q(order_id1__icontains=q) | Q(date__icontains=q) | Q(grand_total__contains=q),
        status=None, group_checkout=True).order_by('id')

    paginator = Paginator(data, 10)
    # print(paginator,'paginator')
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'mlm_admin/order-list.html', {'data': page_obj, 'title': 'Order List', 'q': q, "new_data":new_data})

@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['order_management', ['1', '2', '3', '4']])
def group_order_list(request, cf=False):
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        data = get_order_list_for_mlm_admin(cf).filter(
            Q(name__icontains=q) | Q(order_id1__icontains=q) | Q(date__icontains=q) | Q(grand_total__contains=q),
            status=None, delete=False, paid=True, group_checkout=True).order_by('id')
    else:
        q = ''
        data = get_order_list_for_mlm_admin(cf).filter(status=None, delete=False, paid=True,
                                                     group_checkout=True).order_by('id')
    paginator = Paginator(data, 10)
    # print(paginator,'paginator')
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'mlm_admin/order-list.html', {'data': page_obj, 'title': 'Order List', 'q': q})

@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['order_management', ['1', '2', '3', '4']])
def allorder(request, cf=False):
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        data = get_order_list_for_mlm_admin(cf).filter(
            Q(name__icontains=q) | Q(order_id1__icontains=q) | Q(date__icontains=q) | Q(grand_total__contains=q),
            delete=False, paid=True).order_by('id')
    else:
        q = ''
        data = get_order_list_for_mlm_admin(cf).order_by('id')

    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'mlm_admin/Allorder-list.html', {'data': page_obj, 'title': 'All Order', 'q': q})


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['order_management', ['1', '2', '3', '4']])
def accepted_order(request, cf=False):
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        data = get_order_list_for_mlm_admin(cf).filter(
            Q(name__icontains=q) | Q(order_id1__icontains=q) | Q(date__icontains=q) | Q(grand_total__contains=q),
            status=1).order_by('id')
    else:
        q = ''
        data = get_order_list_for_mlm_admin(cf).filter(status=1).order_by('id')
    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'mlm_admin/accepted_order.html', {'data': page_obj, 'title': 'Accepted Order', 'q': q})


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['order_management', ['1', '2', '3', '4']])
def ready_to_dispatch(request, cf=False):
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        data = get_order_list_for_mlm_admin(cf).filter(
            Q(name__icontains=q) | Q(order_id1__icontains=q) | Q(grand_total__contains=q) | Q(date__icontains=q),
            status=2).order_by('id')
    else:
        q = ''
        data = get_order_list_for_mlm_admin(cf).filter(status=2).order_by('id')
    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'mlm_admin/ready_to_dispatch.html', {'data': page_obj, 'title': 'Ready To Dispatch', 'q': q})


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['order_management', ['1', '2', '3', '4']])
def dispatched(request, cf=False):
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        data = get_order_list_for_mlm_admin(cf).filter(Q(name__icontains=q) | Q(order_id1__icontains=q) | Q(date__icontains=q),
                                    status=3).order_by('id')
    else:
        q = ''
        data = get_order_list_for_mlm_admin(cf).filter(status=3).order_by('id')
    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'mlm_admin/dispatched.html', {'data': page_obj, 'title': 'Dispatched', 'q': q})


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['order_management', ['1', '2', '3', '4']])
def delivered(request, cf=False):
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        data = get_order_list_for_mlm_admin(cf).filter(
            Q(name__icontains=q) | Q(order_id1__icontains=q) | Q(grand_total__contains=q) | Q(date__icontains=q),
            status=4).order_by('id')
    else:
        q = ''
        data = get_order_list_for_mlm_admin(cf).filter(status=4).order_by('id')
    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'mlm_admin/delivered.html', {'data': page_obj, 'title': 'Delivered', 'q': q})


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['order_management', ['1', '2', '3', '4']])
def reject_order(request, cf=False):
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        data = get_order_list_for_mlm_admin(cf).filter(
            Q(name__icontains=q) | Q(order_id1__icontains=q) | Q(grand_total__contains=q) | Q(date__icontains=q),
            status=5).order_by('id')
    else:
        q = ''
        data = get_order_list_for_mlm_admin(cf).filter(status=5).order_by('id')
    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # data = Order.objects.filter(status=5).exclude(delete=True)
    return render(request, 'mlm_admin/reject.html', {'data': page_obj, 'title': 'Reject Order', 'q': q})


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['order_management', ['1', '2', '3', '4']])
def refund(request, cf=False):
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        data = get_order_list_for_mlm_admin(cf).filter(
            Q(name__icontains=q) | Q(order_id1__icontains=q) | Q(grand_total__contains=q) | Q(date__icontains=q),
            status=6).order_by('id')
    else:
        q = ''
        data = get_order_list_for_mlm_admin(cf).filter(status=6).order_by('id')
    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # data = Order.objects.filter(status=6).exclude(delete=True)
    return render(request, 'mlm_admin/refund.html', {'data': page_obj, 'title': 'Refund', 'q': q})


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['order_management', ['1', '2', '3', '4']])
def decline_order(request, cf=False):
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        data = get_order_list_for_mlm_admin(cf).filter(
            Q(name__icontains=q) | Q(order_id1__icontains=q) | Q(grand_total__contains=q) | Q(date__icontains=q),
            status=8).order_by('id')
    else:
        q = ''
        data = get_order_list_for_mlm_admin(cf).filter(status=8).order_by('id')
    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # data = Order.objects.filter(status=6).exclude(delete=True)
    return render(request, 'mlm_admin/decline_order.html', {'data': page_obj, 'title': 'Decline Orders', 'q': q})


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['order_management', ['1', '2', '3', '4']])
def returned(request, cf=False):
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        data = get_order_list_for_mlm_admin(cf).filter(
            Q(name__icontains=q) | Q(order_id1__icontains=q) | Q(grand_total__contains=q) | Q(date__icontains=q),
            status=7).order_by('id')
    else:
        q = ''
        data = get_order_list_for_mlm_admin(cf).filter(delete=False).order_by('id')
    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # data = Order.objects.filter(status=7).exclude(delete=True)
    return render(request, 'mlm_admin/returned.html', {'data': page_obj, 'title': 'Returned'})


# AG :: Functions for C&F View
def cf_order_list(request):
    response = order_list(request, cf=True)
    return response
def cf_allorder(request):
    response = allorder(request, cf=True)
    return response
def cf_accepted_order(request):
    response = accepted_order(request, cf=True)
    return response
def cf_ready_to_dispatch(request):
    response = ready_to_dispatch(request, cf=True)
    return response
def cf_dispatched(request):
    response = dispatched(request, cf=True)
    return response
def cf_delivered(request):
    response = delivered(request, cf=True)
    return response
def cf_reject_order(request):
    response = reject_order(request, cf=True)
    return response
def cf_refund(request):
    response = refund(request, cf=True)
    return response
def cf_decline_order(request):
    response = decline_order(request, cf=True)
    return response
def cf_returned(request):
    response = returned(request, cf=True)
    return response


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['order_management', ['2']])
def orderstatus(request, myid):
    status = request.GET.get('status', False)
    data = Order.objects.filter(pk=myid)
    data.update(status=status)
    contents = "Auretics Email"
    try:
        mobile = data.billing_address.mobile
    except:
        mobile = data.shipping_address.mobile

    sendsms("Msg Order Status", user_mobile_number="+91" + str(mobile), ARN=final, referee_name=(str(data.name)))
    send_mail("Order Status", contents, settings.EMAIL_HOST_USER,
              [data.email])
    for i in data:
        data1 = i.order_id1
    if status == '1':
        data1 = data1 + ' is Accepted'
    return JsonResponse(status=200, data={'data': data1})

@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['order_management', ['2']])
def change_mc_status(request, myid):
    material_center = request.GET.get('change_mc_status', False)
    data = Order.objects.filter(pk=myid)
    data.update(material_center=material_center)

    if data:
        data = data.first()
    if status == '1':
        data1 = data1 + ' Material Center is Changed'
    return JsonResponse(status=200, data={'data': data1})


# AG :: Order Statuses
# Order Status:
# Order list = Null/Blank
# Accepted = 1
# Ready to Dispatch = 2
# Dispatched = 3
# Delivered = 4
# Reject = 5
# Refund = 6
# Returned = 7
# Decline = 8

@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['order_management', ['2']])
def accept_order(request, myid):
    print("Inside Accept_order")
    today = datetime.now().date()
    # data = get_order_list_for_mlm_admin(cf).get(pk=myid)
    data = Order.objects.get(pk=myid)

    # print("maintaing order")
    om = OrderMaintain()
    om.set_token()
    om.get_channel_id()
    response = om.post_order(data)
    print(f"This is Response {response}")

    if response['status_code'] == 1:
        data.status = 1
        data.sr_order_id = response['order_id']
        data.sr_shipment_id = response['shipment_id']
        data.sr_status = response['status']
        data.sr_status_code = response['status_code']
        data.sr_onboarding_completed_now = response['onboarding_completed_now']
        data.sr_awb_code = response['awb_code']
        data.sr_courier_company_id = response['courier_company_id']
        data.shipping_partner = 'Ship Rocket'
        data.shipping_tracking_id = response['awb_code']
        data.sr_courier_name = response['courier_name']
        data.save()
        #     get_order_list_for_mlm_admin(cf).filter(pk=myid).update(status=1, accept_date=today)
        # messages.success(request,"Username-" + str(data.name) + '  Order Id-' + str(data.order_id1) + "   Accepted Successfully" + " \n" + str(response))
        # return redirect('order-list')
        try:
            mobile = data.shipping_address.mobile
        except:
            mobile = data.billing_address.mobile

        Order.objects.filter(pk=myid).update(status=1, accept_date=today)

        messages.success(request, "Username-" + str(data.name) + '  Order Id-' + str(
            data.order_id1) + " Order is Accepted Successfully, currently the status of shiprocket order status is '1' \n")
        return redirect('accepted_order')

    else:
        messages.error(request, "Username-" + str(data.name) + '  Order Id-' + str(data.order_id1) + " is Not Accepted")
        return redirect('allorder-list')

    return redirect('allorder-list')

@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['order_management', ['2']])
def accept_order_dv(request, myid):
    today = datetime.now().date()
    order = Order.objects.get(pk=myid)
    status, resp = DelhiveryApi(verbose=True).create_order(order)
    # print(status, resp)
    if resp['packages'][0]['status'] == 'Success':
        messages.success(request, f"Order is Accepted Successfully with waybill no {resp['packages'][0]['waybill']}")
        order.status = 1
        order.accept_date = today
        order.shipping_partner = 'Delhivery'
        order.shipping_tracking_id = resp['packages'][0]['waybill']
        order.save()
        # send_to_sheet = SendToGS().send(order)
    else:
        messages.error(request, f"Order not accepted with error:\n{resp['packages'][0]['remarks'][0]}")

    return redirect('accepted_order')

@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['order_management', ['2']])
def accept_order_pkr(request, myid):
    today = datetime.now().date()
    order = Order.objects.get(pk=myid)
    status, resp = PickrrApi(verbose=True).create_order(order)
    # print(status, resp)
    if 'tracking_id' in resp:
        messages.success(request, f"Order is Accepted Successfully with waybill no {resp['tracking_id']}")
        order.status = 1
        order.accept_date = today
        order.shipping_partner = 'Pickrr'
        order.shipping_tracking_id = resp['tracking_id']
        order.save()
    else:
        messages.error(request, f"Order not accepted with error:\n{resp['err']}")

    return redirect('accepted_order')

@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['manual_configure', ['1', '2']])
def SheetConfigView(request):
    obj = Sheet_config.objects.last()
    if request.method == 'POST':
        form = SheetConfigForm(instance=obj, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('sheet_config')
        else:
            print(form.errors)
            return HttpResponse('<h1>' + str(form.erros) + '</h1>')
    form = SheetConfigForm(instance=obj)
    return render(request, 'mlm_admin/sheet_config.html', {'form': form})

@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['order_management', ['2']])
def send_to_sheet(request, myid):
    order = Order.objects.get(pk=myid)
    resp = SendToGS().send(order)
    if resp['status'] == 'Success':
        messages.success(request, "Order Details sended to google sheet Successfully")
    else:
        messages.error(request, "Error in code")
    return HttpResponseRedirect(reverse('view_order', kwargs={'myid': myid}))

def track_order(request, myid):
    order = Order.objects.get(pk=myid)
    sr_shipment_id = order.sr_shipment_id
    om = OrderMaintain()
    om.set_token()
    om.get_channel_id()

    response = om.track_order(sr_shipment_id)
    try:
        tracking_data = response["tracking_data"]
        track_url = response["tracking_data"]["track_url"]
        shipment_tack = response["tracking_data"]["shipment_track"]
        parms = {'tracking_data': tracking_data, 'track_url': track_url, 'shipment_track': shipment_track}
        return render(request, 'mlm_admin/track_order.html', parms)
    except:
        error = response["tracking_data"]["error"]
        messages.error(request, f"Shirocket Error '{error}' ")

    return render(request, 'mlm_admin/track_order.html')


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['order_management', ['2']])
def status_ready_to_dispatch(request, myid):
    today = datetime.now().date()
    Order.objects.filter(pk=myid).update(status=2, ready_to_dispatch_date=today)
    data = Order.objects.get(pk=myid)
    messages.success(request,
                     "Username-" + str(data.name) + '  Order Id-' + str(data.order_id1) + "  Ready  To Dispatch")
    return redirect('accepted_order')


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['order_management', ['2']])
def status_dispatched(request, myid):
    today = datetime.now().date()
    Order.objects.filter(pk=myid).update(status=3, dispatched_date=today)
    data = Order.objects.get(pk=myid)
    messages.success(request, "Username-" + str(data.name) + '  Order Id-' + str(data.order_id1) + "  is dispatched")
    return redirect('ready_to_dispatch')


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['order_management', ['2']])
def status_delivered(request, myid):
    today = datetime.now().date()
    Order.objects.filter(pk=myid).update(status=4, delivered_date=today)
    data = Order.objects.get(pk=myid)
    messages.success(request, "Username-" + str(data.name) + '  Order Id-' + str(data.order_id1) + "  is delivered")
    return redirect('dispatched')


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['order_management', ['2']])
def status_reject(request, myid):
    today = datetime.now().date()
    Order.objects.filter(pk=myid).update(status=5, rejected_date=today)
    data = Order.objects.get(pk=myid)
    messages.success(request, "Username-" + str(data.name) + '  Order Id-' + str(data.order_id1) + "  is reject")
    return redirect('order-list')


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['order_management', ['2']])
def status_refund(request, myid):
    today = datetime.now().date()
    Order.objects.filter(pk=myid).update(status=6, refunded_date=today)
    data = Order.objects.get(pk=myid)
    messages.success(request, "Username-" + str(data.name) + '  Order Id-' + str(data.order_id1) + "  is refund")
    return redirect('reject_order')


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['order_management', ['2']])
def status_returned(request, myid):
    today = datetime.now().date()
    Order.objects.filter(pk=myid).update(status=7, returned_date=today)
    data = Order.objects.get(pk=myid)
    messages.success(request, "Username-" + str(data.name) + '  Order Id-' + str(data.order_id1) + "  is returned")
    return redirect('dispatched')


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['order_management', ['4']])
def delete_order(request, myid, check):
    Order.objects.filter(pk=myid).update(delete=True)
    data = Order.objects.get(pk=myid)
    messages.success(request, "Username-" + str(data.name) + '  Order Id-' + str(data.order_id1) + "  is deleted")
    if check == 'allorder':
        return redirect('allorder-list')
    elif check == 'order':
        return redirect('order-list')
    elif check == 'delivered':
        return redirect('delivered')
    elif check == 'accepted_order':
        return redirect('accepted_order')
    elif check == 'ready_to_dispatch':
        return redirect('ready_to_dispatch')
    elif check == 'dispatched':
        return redirect('dispatched')
    elif check == 'rejected':
        return redirect('reject_order')
    elif check == 'refunded':
        return redirect('refund')
    return redirect('order-list')


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['order_management',['3']])
def view_order(request, myid):
    order_qs = get_object_or_404(Order, pk=myid)
    form = Orderform(instance=order_qs)
    date = order_qs.date
    status = order_qs.status
    order = LineItem.objects.filter(order_id=order_qs.pk)
    group_user = Order.objects.filter(main_order=order_qs.pk)
    user = User.objects.filter(username=order_qs.email)[0]
    user_profile = Profile.objects.get(user=user)
    ARN = ReferralCode.objects.get(user_id=user)
    mc_cnf = Material_center.objects.filter(advisory_owned='NO')

    # Show_prices to the end customer.
    show_prices = False
    # Show complete information like accepted date, ready to ship date, etc.
    show_complete = False
    # We will show MRP if admin want to show MRP:
    if request.method == "POST":
        order_qs.shipment_height = request.POST.get("shipment_height")
        order_qs.shipment_width = request.POST.get("shipment_width")
        order_qs.shipment_length = request.POST.get("shipment_length")
        order_qs.shipment_weight = request.POST.get("shipment_weight")
        order_qs.save()
        return HttpResponseRedirect(reverse('view_order', kwargs={'myid': myid}))
    if request.method == 'GET':
        show_prices = request.GET.get('show_prices', False)
        show_complete = request.GET.get('show_complete', False)
        if show_prices == "Y":
            show_prices = True
        if show_complete == "Y":
            show_complete = True
    if order_qs.shipping_address == None:
        address_qs = get_object_or_404(Address, pk=order_qs.billing_address.pk)
        # We will show MRP if user want to receive order at his billing address:
        show_prices = True
    else:
        address_qs = get_object_or_404(Address, pk=order_qs.shipping_address.pk)
    dataform = AddressForm(instance=address_qs)
    if dataform.initial["address_type"] == 'B':
        show_prices = True
    if show_complete:
        show_prices = True
    params = {
        'form': form,
        'dataform': dataform,
        'date': date,
        'status': status,
        'order_list': order,
        'title': 'View Order',
        'user': user,
        'user_profile': user_profile,
        'ARN': ARN,
        'myid': myid,
        'order_qs': order_qs,
        'group_user':group_user,
        'show_prices': show_prices,
        'show_complete': show_complete,
        'page':'mlm_admin',
        'cnf':False,
        'mlm_admin':True,
        'mc_cnf':mc_cnf,
    }
    return render(request, 'mlm_admin/view_order.html', params)


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['batch_management', ['1']])
def add_batch(request):
    form = Batchform()
    if request.method == 'POST':
        form = Batchform(request.POST, request.FILES)
        if form.is_valid():
            dataform = form.save(commit=False)
            myid = request.POST['product']
            product = Product.objects.get(pk=myid)
            dataform.product = product
            dataform.save()
            pv_bv_rebuilding(request, perform=True)
            messages.success(request, 'Batch details added successfully')
            return redirect('batch_list')
        else:
            print(form.errors)
            messages.success(request, form.errors)
            return redirect('batch_list')
    products = Product.objects.all().order_by('product_name').exclude(delete=True)
    params = {
        'form': form,
        'products': products,
        'title': 'Add Batch'
    }
    return render(request, 'mlm_admin/add_batch.html', params)


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['batch_management', ['1', '2', '3', '4']])
def batch_list(request):
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        data = Batch.objects.filter(Q(batch_name__icontains=q) | Q(product__product_name__icontains=q),
                                    delete=False).order_by('id')
    else:
        q = ''
        data = Batch.objects.filter(delete=False).order_by('id')
    page_number = request.GET.get('page', 1)
    paginator = Paginator(data, 5)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return render(request, 'mlm_admin/batch-list.html', {'data': page_obj, 'title': 'Batch List', 'q': q})


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['batch_management', ['4']])
def delete_batch(request, myid):
    batchs = Batch.objects.filter(pk=myid)
    batchs.update(delete=True)
    for i in batchs:
        msg = str(i.batch_name) + 'Batch Deleted Successfully'
    messages.success(request, msg)
    return redirect('batch_list')

@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['product_management', ['2']])
def copy_batch(request, myid):
    batch_qs = Batch.objects.get(pk=myid)
    batch_qs.pk = None
    batch_qs.id = None
    batch_qs.save()
    batch_name = batch_qs.batch_name
    batch_name = batch_name + " Cloned on " + str(datetime.now().date()) + " at " + str(datetime.now().time())
    batch_qs.batch_name = batch_name
    batch_qs.save()
    return redirect('edit_batch', myid=batch_qs.pk)

@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['batch_management', ['2']])
def edit_batch(request, myid):
    batch_qs = get_object_or_404(Batch, pk=myid)
    if request.method == 'POST':
        form = Batchform(instance=batch_qs, data=request.POST, files=(request.FILES or None), )
        dataform = form.save(commit=False)
        myid = request.POST['product']
        product = Product.objects.get(pk=myid)
        dataform.product = product
        dataform.save()
        pv_bv_rebuilding(request, perform=True)
        messages.success(request, "Updated the Batch Successfully!")
        return redirect('batch_list')
    product_id = batch_qs.product.pk
    form = Batchform(instance=batch_qs)
    products = Product.objects.all().order_by('product_name').exclude(delete=True)

    if 'Clone' in batch_qs.batch_name:
        clone_option = False
    else:
        clone_option = True

    params = {
        'form': form,
        'products': products,
        'product_id': product_id,
        'title': 'Edit Batch',
        'myid':myid,
        'clone_option':clone_option,
    }
    return render(request, 'mlm_admin/edit_batch.html', params)


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['batch_management', ['3']])
def view_batch(request, myid):
    batch_qs = get_object_or_404(Batch, pk=myid)
    manuf_date = batch_qs.date_of_manufacture
    exp_date = batch_qs.date_of_expiry
    product_id = batch_qs.product.pk
    form = Batchformview(instance=batch_qs)
    products = Product.objects.all()
    params = {
        'form': form,
        'products': products,
        'manuf_date': manuf_date,
        'exp_date': exp_date,
        'product_id': product_id,
        'title': 'View Batch'
    }
    return render(request, 'mlm_admin/view_batch.html', params)


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['mc_management', ['1']])
def add_material(request):
    form = Materialform()
    if request.method == 'POST':
        form = Materialform(request.POST, request.FILES)
        # data = form.is_valid()
        if form.is_valid():
            form.save()
            messages.success(request, 'Material Center added successfully')
            return redirect('material_list')
    material = Material_center.objects.filter(advisory_owned='YES').values('advisor_registration_number__email')
    material_company_depot = Material_center.objects.filter(company_depot='YES').values(
        'advisor_registration_number__email')
    user = User.objects.filter(profile__distributor=True).exclude(email__in=material)
    cnf_users = User.objects.filter(profile__c_and_f_admin=True)
    distributor_data_list = []
    cnf_data_list = []
    for u in user:
        distributor_data_list.append(dict(key='{}-{}'.format(u.referralcode.referral_code, u.email), value=u.pk))
    for u in cnf_users:
        cnf_data_list.append(dict(key='{}-{}'.format(u.referralcode.referral_code, u.email), value=u.pk))
    all_states = State.objects.all()
    frontend_mc_qs = Material_center.objects.filter(frontend=True)
    if frontend_mc_qs.exists():
        frontend_mc = frontend_mc_qs.first()
        state_qs = State.objects.filter(Q(associated_material_center=frontend_mc) | Q(associated_material_center=None))
    else:
        state_qs = State.objects.filter(associated_material_center=None)

    return render(request, 'mlm_admin/add_material.html',
                  {'form': form, 'title': 'Add Material',
                   'user': user,
                   'all_states': all_states,
                   'states': state_qs,
                   'cnf_user_list': cnf_data_list,
                   'distributor_user_list': distributor_data_list,
                   'states_for_company_depot': [{'pk': s.pk, 'name': s.state_name} for s in state_qs],
                   'states_for_advisory_owned': [],
                   })


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['mc_management', ['1']])
def add_cnf_material(request):
    form = Materialform()
    if request.method == 'POST':
        form = Materialform(request.POST, request.FILES)
        # data = form.is_valid()
        if form.is_valid():
            form.save()
            messages.success(request, 'Material Center added successfully')
            return redirect('material_list')
    material = Material_center.objects.filter(advisory_owned='YES').values('advisor_registration_number__email')
    material_company_depot = Material_center.objects.filter(company_depot='YES').values(
        'advisor_registration_number__email')
    user = User.objects.filter(profile__distributor=True).exclude(email__in=material)
    cnf_users = User.objects.filter(profile__c_and_f_admin=True)
    distributor_data_list = []
    cnf_data_list = []
    for u in user:
        distributor_data_list.append(dict(key='{}-{}'.format(u.referralcode.referral_code, u.email), value=u.pk))
    for u in cnf_users:
        cnf_data_list.append(dict(key='{}-{}'.format(u.referralcode.referral_code, u.email), value=u.pk))
    frontend_mc_qs = Material_center.objects.filter(frontend=True)
    if frontend_mc_qs.exists():
        frontend_mc = frontend_mc_qs.first()
        state_qs = State.objects.filter(Q(associated_material_center=frontend_mc) | Q(associated_material_center=None))
    else:
        state_qs = State.objects.filter(associated_material_center=None)

    return render(request, 'mlm_admin/add_material.html',
                  {'form': form,
                   'title': 'Add Material',
                   'user': user,
                   'states': state_qs,
                   'cnf_user_list': cnf_data_list,
                   'distributor_user_list': distributor_data_list,
                   })


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['mc_management', ['1', '2', '3', '4']])
def material_list(request):
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        data = Material_center.objects.filter(
            Q(mc_name__icontains=q) | Q(print_name__icontains=q) | Q(city__icontains=q) | Q(state__icontains=q),
            delete=False).order_by('id')
    else:
        q = ''
        data = Material_center.objects.filter(delete=False, ).order_by('id')
    paginator = Paginator(data, 10)
    print(paginator, 'paginator')
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'mlm_admin/material-list.html', {'data': page_obj, 'title': 'Material List', 'q': q})
    # data = Material_center.objects.all().exclude(delete=True)
    # return render(request, 'mlm_admin/material-list.html', {'data': data,'title':'Material List'})


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['mc_management', ['1', '2', '3', '4']])
def material_state_assignment_list_list(request):
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        states = State.objects.filter(
            Q(state_name__icontains=q) | Q(associated_material_center__mc_name__icontains=q)).order_by('state_name')
    else:
        q = ''
        states = State.objects.all().order_by('state_name')
    paginator = Paginator(states, 40)
    print(paginator, 'paginator')
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'mlm_admin/material-state-assignment-list.html',
                  {'data': page_obj, 'title': 'State MC Assignment List', 'q': q})
    # data = Material_center.objects.all().exclude(delete=True)
    # return render(request, 'mlm_admin/material-list.html', {'data': data,'title':'Material List'})


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['mc_management', ['1', '2', '3', '4']])
def material_center_wise_sale(request):
    today_date = datetime.now().date()
    month = today_date.month
    year = today_date.year
    # try:
    year_get = request.GET.get('year', None)
    month_get = request.GET.get('month', None)
    if year_get:
        year = int(year_get)
    if month_get:
        month = int(month_get)
    if request.method == 'POST':
        month_cal = request.POST.get('month', None)
        if month_cal != '' and month_cal != None:
            input_date = month_cal.split('-')
            year = input_date[0]
            month = input_date[1]
    # except:
    #     pass

    stock_variance = ["stockvariance@auretics.com", "loyalty@auretics.com", "pvpower@auretics.com", "pawan@auretics.com", ]

    if 'q' in request.GET:
        q = request.GET.get('q', False)
        data = Material_center.objects.filter(
            Q(mc_name__icontains=q) | Q(print_name__icontains=q) | Q(city__icontains=q) | Q(state__icontains=q),
            delete=False).exclude(advisor_registration_number__email__in=stock_variance).order_by('id')
    else:
        q = ''
        data = Material_center.objects.filter(delete=False, ).exclude(advisor_registration_number__email__in=stock_variance).order_by('id')

    mc_wise_details = {}
    mc_sale_data = []
    mc_loyalty_data = []
    mc_stock_variance_data = []
    mc_purchase_data_accept = []
    mc_purchase_data_in_transit = []
    mc_closing_stock = []

    for i in data:
        purchase_data_accept = Sale_itemDetails.objects.filter(sale__material_center_to=i,
                                                               sale__created_on__month=month,
                                                               sale__created_on__year=year,
                                                               sale__delete=False,
                                                               sale__accept=True).aggregate(Sum('total_amount'))[
            'total_amount__sum']
        purchase_data_in_transit = Sale_itemDetails.objects.filter(sale__material_center_to=i,
                                                                   sale__created_on__month=month,
                                                                   sale__created_on__year=year,
                                                                   sale__delete=False,
                                                                   sale__accept=False).aggregate(Sum('total_amount'))[
            'total_amount__sum']
        sale_data = Order.objects.filter(material_center=i,
                                         date__month = month,
                                         date__year = year,
                                         paid=True,
                                         delete=False,
                                         loyalty_order=False,).exclude(status=8).exclude(email__in=stock_variance).aggregate(Sum('grand_total'))['grand_total__sum']
        loyalty_data = Order.objects.filter(material_center=i,
                                            date__month = month,
                                            date__year = year,
                                            paid=True,
                                            delete=False,
                                            loyalty_order=True,).exclude(email__in=stock_variance).aggregate(Sum('grand_total'))['grand_total__sum']
        stock_variance_data = Order.objects.filter(material_center=i,
                                                   date__month = month,
                                                   date__year = year,
                                                   paid=True,
                                                   delete=False,
                                                   loyalty_order=False,
                                                   email__in=stock_variance,).exclude(status=8).aggregate(Sum('grand_total'))['grand_total__sum']

        closing_stock_cache_name = "closing_stock_cache" + str(i.id)
        closing_stock_total = cache.get(closing_stock_cache_name)
        if closing_stock_total is None:
            closing_stock = Distributor_Inventry.objects.filter(material_center=i,
                                                                created_on__month=today_date.month,
                                                                created_on__year=today_date.year, )
            closing_stock_total = 0.0
            for stock in closing_stock:
                closing_stock_total += stock.current_quantity * (
                            stock.batch.mrp / ((100 + stock.product.distributor_price) / 100))

            closing_stock = Inventry.objects.filter(material_center=i,
                                                                created_on__month=today_date.month,
                                                                created_on__year=today_date.year, )
            for stock in closing_stock:
                closing_stock_total += stock.current_quantity * (
                        stock.batch.mrp / ((100 + stock.product.distributor_price) / 100))
            cache.set(closing_stock_cache_name, closing_stock_total)
        else:
            pass

        # closing_stock = Distributor_Inventry.objects.filter(material_center = i,
        #                                                     created_on__month = today_date.month,
        #                                                     created_on__year = today_date.year,)
        # closing_stock_total = 0.0
        # for stock in closing_stock:
        #     closing_stock_total += stock.current_quantity * (stock.batch.mrp / ((100 + stock.product.distributor_price) / 100))

        if purchase_data_accept:
            purchase_data_accept = round(purchase_data_accept)
            mc_purchase_data_accept.append(purchase_data_accept)
        else:
            purchase_data_accept = '-'

        if purchase_data_in_transit:
            purchase_data_in_transit = round(purchase_data_in_transit)
            mc_purchase_data_in_transit.append(purchase_data_in_transit)
        else:
            purchase_data_in_transit = '-'

        if sale_data:
            sale_data = round(sale_data)
            mc_sale_data.append(sale_data)
        else:
            sale_data = '-'

        if loyalty_data:
            loyalty_data = round(loyalty_data)
            mc_loyalty_data.append(loyalty_data)
        else:
            loyalty_data = '-'

        if stock_variance_data:
            stock_variance_data = round(stock_variance_data)
            mc_stock_variance_data.append(stock_variance_data)
        else:
            stock_variance_data = '-'

        if closing_stock_total:
            closing_stock_total = round(closing_stock_total)
            mc_closing_stock.append(closing_stock_total)
        else:
            closing_stock_total = '-'

        mc_wise_details[i] = [purchase_data_accept, purchase_data_in_transit, sale_data, loyalty_data, stock_variance_data, closing_stock_total]

    total_mc_purchase_data_accept = sum(mc_purchase_data_accept)
    total_mc_purchase_data_in_transit = sum(mc_purchase_data_in_transit)
    total_mc_sale_data = sum(mc_sale_data)
    total_mc_loyalty_data = sum(mc_loyalty_data)
    total_mc_stock_variance_data = sum(mc_stock_variance_data)
    total_mc_closing_stock = sum(mc_closing_stock)

    try:
        month = month_name(month_cal.month)
        year = month_cal.year
    except:
        try:
            month = month_name(month)
            year = year
        except:
            month = "Please Select a Date"
            year = ""

    # paginator = Paginator(data, 40)
    # page_number = request.GET.get('page')
    # page_obj = paginator.get_page(page_number)
    return render(request, 'mlm_admin/material_wise_sale.html',
                  {
                   # 'data': page_obj,
                   'title': 'MC Wise Sale Details',
                   'q': q,
                   'month':month,
                   'year': year,
                   'mc_sale_data':mc_sale_data,
                   'mc_loyalty_data': mc_loyalty_data,
                   'mc_stock_variance_data': mc_stock_variance_data,
                   'mc_purchase_data_accept':mc_purchase_data_accept,
                   'mc_purchase_data_in_transit':mc_purchase_data_in_transit,
                   'mc_closing_stock':mc_closing_stock,
                   'mc_wise_details':mc_wise_details,
                   'total_mc_purchase_data_accept': total_mc_purchase_data_accept,
                   'total_mc_purchase_data_in_transit': total_mc_purchase_data_in_transit,
                   'total_mc_sale_data':total_mc_sale_data,
                   'total_mc_loyalty_data':total_mc_loyalty_data,
                   'total_mc_stock_variance_data':total_mc_stock_variance_data,
                   'total_mc_closing_stock':total_mc_closing_stock,
                   })


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['mc_management', ['4']])
def delete_material(request, myid):
    data = Material_center.objects.filter(pk=myid)
    data.update(delete=True)
    for i in data:
        msg = str(i.mc_name) + '  Material Center Deleted successfully'
    messages.success(request, msg)
    return redirect('material_list')


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['mc_management', ['2']])
def edit_material(request, myid):
    material_qs = get_object_or_404(Material_center, pk=myid)
    if material_qs.delete == True:
        return redirect('material_list')

    if request.method == 'POST':
        form = Materialform(request.POST, request.FILES)
        if form.is_valid():
            form = Materialform(instance=material_qs, data=request.POST, files=(request.FILES or None), )
            material_qs = form.save()
            # # add state to associated states so that query would be ea
            # state = State.objects.get(state_name=material_qs.state)
            # if material_qs.advisory_owned == 'YES' and state not in material_qs.associated_states.all():
            #     material_qs.associated_states.set(state)
            messages.success(request, 'Material Center Updated Successfully')
            return redirect('material_list')
    form = Materialform(instance=material_qs)
    vaild_user = material_qs.advisor_registration_number
    material = Material_center.objects.filter(advisory_owned='YES').values('advisor_registration_number__email')
    user = User.objects.filter(profile__distributor=True).exclude(email__in=material)
    cnf_users = User.objects.filter(profile__c_and_f_admin=True)
    actual_mc_name = material_qs.mc_name
    distributor_data_list = []
    cnf_data_list = []
    for u in user:
        distributor_data_list.append(dict(key='{}-{}'.format(u.referralcode.referral_code, u.email), value=u.pk))
    for u in cnf_users:
        cnf_data_list.append(dict(key='{}-{}'.format(u.referralcode.referral_code, u.email), value=u.pk))
    associated_states_name = [i.pk for i in material_qs.associated_states.all()]
    states_to_exclude = State.objects.filter(
        associated_material_center__in=Material_center.objects.filter(advisory_owned='YES')).values_list('pk',
                                                                                                         flat=True)
    all_states = State.objects.all()
    frontend_mc_qs = Material_center.objects.filter(frontend=True)
    if frontend_mc_qs.exists():
        frontend_mc = frontend_mc_qs.first()
        state_qs = State.objects.filter(Q(associated_material_center=frontend_mc) | Q(associated_material_center=None) |
                                        Q(pk__in=associated_states_name))
    else:
        state_qs = State.objects.filter(Q(associated_material_center=None) | Q(pk__in=associated_states_name))

    return render(request, 'mlm_admin/edit_material.html',
                  {'form': form, 'title': 'Edit Material', 'user': user, 'valid_user': vaild_user,
                   'actual_mc_name': actual_mc_name,
                   'cnf_user_list': cnf_data_list,
                   'distributor_user_list': distributor_data_list,
                   'states': state_qs,
                   'all_states': all_states,
                   'selected_states': associated_states_name,
                   'selected_state': material_qs.state,
                   'states_for_company_depot': [{'pk': s.pk, 'name': s.state_name} for s in state_qs],
                   'states_for_advisory_owned': [{'pk': s.pk, 'name': s.state_name} for s in []],

                   })


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['mc_management', ['3']])
def view_material(request, myid):
    material_qs = get_object_or_404(Material_center, pk=myid)
    if material_qs.delete == True:
        return redirect('material_list')
    form = Materialformview(instance=material_qs)
    vaild_user = material_qs.advisor_registration_number
    return render(request, 'mlm_admin/view-material.html',
                  {'form': form, 'title': 'View Material', 'valid_user': vaild_user})


@login_required(login_url='/mlm_admin/login')
def add_banner(request):
    form = Bannerform()
    if request.method == 'POST':
        form = Bannerform(request.POST, request.FILES)
        # data = form.is_valid()
        if form.is_valid():
            form.save()
            messages.success(request, 'Vanor Added Successfully')
            return redirect('banner-list')
    return render(request, 'mlm_admin/add_banner.html', {'form': form, 'title': 'Add Banner'})


@login_required(login_url='/mlm_admin/login')
def banner_list(request):
    banners = Banner.objects.all()
    return render(request, 'mlm_admin/banner-list.html', {'banners': banners, 'title': 'Banner List'})


@login_required(login_url='/mlm_admin/login')
def edit_banner(request, myid):
    banner_qs = get_object_or_404(Banner, pk=myid)
    if request.method == 'POST':
        form = Bannerform(request.POST, request.FILES)
        if form.is_valid():
            form = Bannerform(instance=banner_qs, data=request.POST, files=(request.FILES or None), )
            form.save()
            messages.success(request, 'Banner Updated Successfully')
            return redirect('banner-list')
    form = Bannerform(instance=banner_qs)
    return render(request, 'mlm_admin/edit_banner.html', {'form': form, 'title': 'Edit Banner'})


@login_required(login_url='/mlm_admin/login')
def view_banner(request, myid):
    vanor_qs = get_object_or_404(Banner, pk=myid)
    form = Bannerformview(instance=vanor_qs)
    return render(request, 'mlm_admin/view_ banner.html', {'form': form, 'title': 'View Banner'})


@login_required(login_url='/mlm_admin/login')
def add_referral(request):
    form = Referral()
    if request.method == "POST":
        user = request.POST['user']
        status = request.POST['status']
        today = datetime.now()
        print(today)
        d3 = str(today.year)
        d4 = str(today.month)
        d7 = str(today.day)
        d8 = str(today.hour)
        d9 = str(today.minute)
        d0 = str(today.second)
        d1 = str(today.microsecond)
        import random
        number = random.randint(1000, 9999)
        random_num = str(number)
        final = d3 + d4 + d7 + d8 + d9 + d0 + random_num
        user = User.objects.get(pk=user)
        try:
            data = ReferralCode.objects.get(user_id=user)
            final = data.referral_code
        except:
            data = ReferralCode.objects.filter(user_id=user).update(referral_code=final)
        messages.success(request, 'Referral code  Activated Successfully')
        return redirect('referral_list')

    user = User
    data = user.objects.all()
    params = {
        'datas': data,
        'form': form,
        'title': 'Add User'
    }
    return render(request, 'mlm_admin/add_referral.html', params)


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['user_management', ['1', '2', '3', '4']])
def referral_list(request):
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        data = ReferralCode.objects.filter(Q(referal_id__icontains=q) |
                                           Q(referral_code__icontains=q) |
                                           Q(user_id__email__icontains=q) |
                                           Q(user_id__profile__phone_number=q) |
                                           Q(user_id__profile__first_name=q) |
                                           Q(user_id__profile__last_name=q)).order_by('id')
    else:
        q = ''
        data = ReferralCode.objects.filter().order_by('id')
    paginator = Paginator(data, 10)
    # print(paginator,'paginator')
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    rt_cm_data = {}
    rt_pm_data = {}
    rt_data_active = {}
    title_data = {}
    for i in page_obj:
        cm_data = RealTimeDetail.objects.filter(user_id=i.user_id, date__month=month, date__year=year)
        try:
            rt_cm_data[i.user_id] = cm_data.latest('date')
        except:
            cm_data = Objectify()
            cm_data.not_found = "User Details not Available for the Current Month."
            rt_cm_data[i.user_id] = cm_data

        pm_data = RealTimeDetail.objects.filter(user_id=i.user_id, date__month=last_month, date__year=last_year)
        try:
            rt_pm_data[i.user_id] = pm_data.latest('date')
        except:
            pm_data = Objectify()
            pm_data.not_found = "User Details not Available for the Previous Month."
            rt_pm_data[i.user_id] = data

        # User Green, Yellow, Grey details
        active_status = "NOT ACTIVATED"
        data_active = RealTimeDetail.objects.filter(user_id=i.user_id, rt_is_user_green=True)
        try:
            rt_data_active[i.user_id] = data_active.latest('date')

            data_active = RealTimeDetail.objects.filter(user_id=i.user_id, rt_is_user_green=True, date__month=month,
                                                        date__year=year)
            try:
                rt_data_active[i.user_id] = data_active.latest('date')
                active_status = "GREEN"
                data_active = Objectify()
                data_active.data_green = active_status
                rt_data_active[i.user_id] = data_active
            except:
                active_status = "YELLOW"
                data_active = Objectify()
                data_active.rt_is_user_green = True
                data_active.data_green = active_status
                rt_data_active[i.user_id] = data_active
        except:
            data_active = Objectify()
            data_active.rt_is_user_green = False
            data_active.data_green = active_status
            rt_data_active[i.user_id] = data_active

        title = title_qualification_calculation_model.objects.filter(user=i.user_id)
        try:
            title_data[i.user_id] = title.latest('date_model')
        except:
            title_data[i.user_id] = title

    return render(request, 'mlm_admin/referralcode-list.html', {'data': page_obj,
                                                                'title': 'User List',
                                                                'q': q,
                                                                'rt_cm_data': rt_cm_data,
                                                                'rt_pm_data': rt_pm_data,
                                                                'rt_data_active': rt_data_active,
                                                                'title_data': title_data})


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['user_management', ['3']])
def view_referral(request, myid):
    form_qs = get_object_or_404(ReferralCode, pk=myid)
    name = form_qs.user_id
    form = Referralview(instance=form_qs)
    referral = ReferralCode.objects.filter(referal_by=name)
    print(form_qs.user_id.profile.status, 'skldfjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj')
    params = {
        'name': name,
        'form': form,
        'upline': form_qs,
        'referral': referral,
        'title': 'View User'
    }
    return render(request, 'mlm_admin/view_referral.html', params)


@login_required(login_url='/mlm_admin/login')
def generat_referral(request, myid):
    today = datetime.now()
    d3 = str(today.year)
    d4 = str(today.month)
    d7 = str(today.day)
    d8 = str(today.hour)
    d9 = str(today.minute)
    d0 = str(today.second)
    d1 = str(today.microsecond)
    import random
    number = random.randint(1000, 9999)
    random_num = str(number)
    final = d3 + d4 + d7 + d8 + d9 + d0 + random_num
    user = User.objects.get(pk=myid)
    try:
        data = ReferralCode.objects.get(user_id=user, status=True)
        final = data.referral_code
    except:
        data = ReferralCode.objects.filter(user_id=user).update(referral_code=final, status=True)
    messages.success(request, 'Your referal code is-' + str(final))
    return redirect('home')


# for inventory management
# code start here
# This code is for puchase management
@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['purchase_management', ['1']])
def add_purchase(request):
    if request.method == "POST":
        date = request.POST['date']
        mc_name = request.POST['mc_name']
        party_name = request.POST['party_name']
        purchase_type = request.POST['purchase_type']
        narration = request.POST['narration']
        grand_total = request.POST['grand_total']
        quaantity_item = request.POST.getlist('quaantity_item')
        price_item = request.POST.getlist('price_item')
        cgst_item = request.POST.getlist('cgst_item')
        sgst_item = request.POST.getlist('sgst_item')
        igst_item = request.POST.getlist('igst_item')
        # vat_item = request.POST.getlist('vat_item')
        item = request.POST.getlist('item')
        batch = request.POST.getlist('batch')
        totalamount_item = request.POST.getlist('totalamount_item')
        try:
            material = Material_center.objects.get(pk=mc_name)
            data = Purchase(purchase_user_id=request.user, material_name=material, date=date, narration=narration,
                            purchase_type=purchase_type,
                            party_name=party_name, grand_total=grand_total)
            data.save()
            print('totalamount_item', totalamount_item, batch)
            try:
                for i, k in enumerate(totalamount_item):
                    purchase = data
                    print('obcet', purchase)
                    quantity = quaantity_item[i]
                    price = price_item[i]
                    cgst = cgst_item[i]
                    sgst = sgst_item[i]
                    igst = igst_item[i]
                    # vat = vat_item[i]
                    vat = 0
                    total_amount = totalamount_item[i]
                    product = item[i]
                    product = Product.objects.get(pk=product)
                    batch1 = batch[i]
                    batch1 = Batch.objects.get(pk=batch1)
                    # inventory code start
                    product_data = (product.quantity + int(quantity))
                    p_quantity_update = Product.objects.filter(pk=product.pk).update(quantity=product_data,
                                                                                     purchase_price=price)
                    batch_quantity = batch1.quantity
                    update_batch_quantity = int(batch_quantity) + int(quantity)
                    Batch.objects.filter(pk=batch1.pk).update(quantity=update_batch_quantity)
                    try:
                        addPurchaseCalculateTodayInventry(
                            product=product,
                            batch=batch1,
                            quantity=quantity,
                            material_center=material,
                            price=price
                        )
                    except:
                        try:
                            addPurchaseUpdateInventry(
                                product=product,
                                batch=batch1,
                                quantity=quantity,
                                material_center=material,
                                price=price
                            )
                        except:
                            addPurchageAddInventry(
                                product=product,
                                batch=batch1,
                                quantity=quantity,
                                material_center=material,
                                price=price
                            )

                    # inventory code end
                    purchase_data = item_details(item=product, batch=batch1, purchase=purchase, quantity=quantity,
                                                 price=price, cgst=cgst, sgst=sgst, igst=igst, vat=vat,
                                                 total_amount=total_amount, )
                    purchase_data.save()
                messages.success(request, "Record added successfully!")
                return redirect('purchase_list')
            except Exception as ex:
                # messages.error(request, "Something is going wrong")
                messages.error(request, "Error: " + str(ex))
                return redirect('purchase_list')

        except:
            messages.error(request, "Something is going wrong")
            return redirect('purchase_list')

    material_c = Material_center.objects.filter(frontend=True).exclude(delete=True)
    items = Product.objects.all().exclude(delete=True)
    batches = Batch.objects.all().exclude(delete=True)
    myDate = datetime.now()
    formatedDate = myDate.strftime("%Y-%m-%d")
    params = {
        'items': items,
        'batches': batches,
        'material_c': material_c,
        'prod_id': 1,
        'date': formatedDate,
        'title': 'Add Purchase'
    }
    return render(request, 'mlm_admin/add_purchase.html', params)


@csrf_exempt
def add_column(request):
    cnt_multiple_product = request.POST['cnt_multiple_product']
    items = Product.objects.all().exclude(delete=True)
    batches = Batch.objects.all().exclude(delete=True)
    params = {
        'items': items,
        'batches': batches,
        'cnt_multiple_product': cnt_multiple_product
    }
    return render(request, 'mlm_admin/add_column.html', params)


@csrf_exempt
def edit_column(request):
    cnt_multiple_product = request.POST['cnt_multiple_product']
    items = Product.objects.all().exclude(delete=True)
    batches = Batch.objects.all().exclude(delete=True)
    params = {
        'items': items,
        'batches': batches,
        'cnt_multiple_product': cnt_multiple_product
    }
    return render(request, 'mlm_admin/edit_column.html', params)


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['purchase_management', ['1', '2', '3', '4']])
def purchase_list(request):
    today = datetime.now().date()
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        data = Purchase.objects.filter(
            Q(pk__icontains=q) | Q(material_name__mc_name__icontains=q) | Q(created_on__icontains=q) | Q(
                party_name__icontains=q)
            | Q(grand_total__icontains=q), delete=False).order_by('-id')
    else:
        q = ''
        data = Purchase.objects.filter(delete=False).order_by('-id')
    paginator = Paginator(data, 10)
    print(paginator, 'paginator')
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'mlm_admin/purchase_list.html',
                  {'data': page_obj, 'title': 'Purchase List', 'q': q, 'today': today})
    # data = Purchase.objects.filter(delete = False).order_by('-pk')
    # print(data)
    # return render(request, 'mlm_admin/purchase_list.html', {'data': data,'title':'Purchase List','today':today})


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['purchase_management', ['2']])
def edit_purchase(request, myid):
    if request.method == "POST":
        date = request.POST['date']
        mc_name = request.POST['mc_name']
        party_name = request.POST['party_name']
        purchase_type = request.POST['purchase_type']
        narration = request.POST['narration']
        grand_total = request.POST['grand_total']
        quaantity_item = request.POST.getlist('quaantity_item')
        price_item = request.POST.getlist('price_item')
        cgst_item = request.POST.getlist('cgst_item')
        sgst_item = request.POST.getlist('sgst_item')
        igst_item = request.POST.getlist('igst_item')
        # vat_item = request.POST.getlist('vat_item')
        item = request.POST.getlist('item')
        batch = request.POST.getlist('batch')
        totalamount_item = request.POST.getlist('totalamount_item')
        print('narro', date, mc_name, narration, quaantity_item, price_item, cgst_item, sgst_item, igst_item,
              totalamount_item)
        try:
            material = Material_center.objects.get(pk=mc_name)
            data = Purchase.objects.filter(pk=myid).update(purchase_user_id=request.user, material_name=material,
                                                           date=date, narration=narration,
                                                           purchase_type=purchase_type, party_name=party_name,
                                                           grand_total=grand_total)
            data = Purchase.objects.get(pk=myid)
            # item_details.objects.filter(purchase=data).delete()
            items = item_details.objects.filter(purchase=data)
            for i in items:
                update_time_batch_quantity = int(i.batch.quantity) - int(i.quantity)
                update_time_product_quantity = int(i.item.quantity) - int(i.quantity)
                Batch.objects.filter(pk=i.batch.pk).update(quantity=update_time_batch_quantity)
                Product.objects.filter(pk=i.item.pk).update(quantity=update_time_product_quantity)
                today = datetime.now().date()
                update_time_inventry = Inventry.objects.get(created_on=today, product=i.item,
                                                            batch=i.batch, material_center=material)
                update_time_inventry_current_quantity = int(update_time_inventry.current_quantity) - int(i.quantity)
                update_time_inventry_quantity_in = int(update_time_inventry.quantity_in) - int(i.quantity)
                Inventry.objects.filter(created_on=today, product=i.item, batch=i.batch,
                                        material_center=material).update(
                    current_quantity=update_time_inventry_current_quantity,
                    quantity_in=update_time_inventry_quantity_in)
            item_details.objects.filter(purchase=data).delete()
            try:
                for i, k in enumerate(totalamount_item):
                    purchase = data
                    print('obcet', purchase)
                    quantity = quaantity_item[i]
                    price = price_item[i]
                    cgst = cgst_item[i]
                    sgst = sgst_item[i]
                    igst = igst_item[i]
                    # vat = vat_item[i]
                    vat = 0
                    total_amount = totalamount_item[i]
                    product = item[i]
                    product = Product.objects.get(pk=product)
                    product_data = (product.quantity + int(quantity))
                    p_quantity_update = Product.objects.filter(pk=product.pk).update(quantity=product_data)
                    batch1 = batch[i]
                    batch1 = Batch.objects.get(pk=batch1)
                    batch_quantity = batch1.quantity
                    update_batch_quantity = int(batch_quantity) + int(quantity)
                    Batch.objects.filter(pk=batch1.pk).update(quantity=update_batch_quantity)
                    try:
                        addPurchaseCalculateTodayInventry(
                            product=product,
                            batch=batch1,
                            quantity=quantity,
                            material_center=material,
                            price=price
                        )
                    except:
                        return HttpResponse('<h1> Please check your code something is wrong </h1>')

                    # inventory code end
                    purchase_data = item_details(item=product, batch=batch1, purchase=purchase, quantity=quantity,
                                                 price=price, cgst=cgst, sgst=sgst, igst=igst, vat=vat,
                                                 total_amount=total_amount)
                    purchase_data.save()
                    print('updateinventory', type(inventory))
                messages.success(request, "Record Updated successfully!")
                return redirect('purchase_list')
            except:
                messages.success(request, "Record Updated successfully!")
                return redirect('purchase_list')

        except:
            messages.warning(request, "something is going wrong")
            return redirect('purchase_list')

    purchases = Purchase.objects.get(pk=myid)
    data = item_details.objects.filter(purchase=purchases)
    print(data)
    material_c = Material_center.objects.all().exclude(delete=True)
    batches = Batch.objects.all()
    items = Product.objects.all()
    today = datetime.now().date()
    if purchases.created_on != today:
        messages.warning(request, 'You are not able to update these records')
        return redirect('purchase_list')
    params = {
        'purchases': purchases,
        'data': data,
        'material_c': material_c,
        'batches': batches,
        'items': items,
        'title': 'Edit Purchase'
    }
    return render(request, 'mlm_admin/edit_purchase.html', params)


# <----------------------------------------------------------------------Purchase-Delete -------------------------------------------------------------------------------------->
@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['purchase_management', ['4']])
def delete_purchase(request, myid):
    purchase = Purchase.objects.get(pk=myid)
    today = datetime.now().date()
    if purchase.created_on != today:
        messages.warning(request, 'You are not able to delete this records')
        return redirect('purchase_list')
    items = item_details.objects.filter(purchase=purchase)
    for i in items:
        update_time_batch_quantity = int(i.batch.quantity) - int(i.quantity)
        update_time_product_quantity = int(i.item.quantity) - int(i.quantity)
        Batch.objects.filter(pk=i.batch.pk).update(quantity=update_time_batch_quantity)
        Product.objects.filter(pk=i.item.pk).update(quantity=update_time_product_quantity)
        today = datetime.now().date()
        update_time_inventry = Inventry.objects.get(created_on=today, product=i.item,
                                                    batch=i.batch, material_center=purchase.material_name)
        update_time_inventry_current_quantity = int(update_time_inventry.current_quantity) - int(i.quantity)
        update_time_inventry_quantity_in = int(update_time_inventry.quantity_in) - int(i.quantity)
        Inventry.objects.filter(created_on=today, product=i.item, batch=i.batch,
                                material_center=purchase.material_name).update(
            current_quantity=update_time_inventry_current_quantity,
            quantity_in=update_time_inventry_quantity_in)

    purchase_delete = Purchase.objects.filter(pk=myid).update(delete=True)
    return redirect('purchase_list')


# <----------------------------------------------------------------------Purchase-Delete --------------------------------------------------------------------------------------->
@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['purchase_management', ['3']])
def view_purchase(request, myid):
    purchases = Purchase.objects.get(pk=myid)
    data = item_details.objects.filter(purchase=purchases)
    print(data)
    material_c = Material_center.objects.all().exclude(delete=True)
    batches = Batch.objects.all()
    items = Product.objects.all()
    params = {
        'purchases': purchases,
        'data': data,
        'material_c': material_c,
        'batches': batches,
        'items': items,
        'title': 'View Purchase'
    }
    return render(request, 'mlm_admin/view_purchase.html', params)


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['sale_management', ['1']])
def add_sale(request):
    if request.method == "POST":
        # try:
        date = request.POST['date']
        mc_center_to = request.POST['mc_center_to']
        print(mc_center_to, '<----here we are geting the mc_center_to')
        mc_center_from = request.POST['mc_center_from']
        narration = request.POST['narration']
        party_name = request.POST['party_name']
        sale_type = request.POST['sale_type']
        grand_total = request.POST['grand_total']
        user = request.POST['user']
        quaantity_item = request.POST.getlist('quaantity_item')
        check_quantity = request.POST.getlist('check_quantity')
        result = quantity_validate(check_quantity, quaantity_item)
        if result == False:
            messages.success(request, "Bad Request (Quantity entered is greater than maximum allowed quantity).")
            return redirect('add_sale')
        distributor_price = request.POST.getlist('distributor_price')
        cgst_item = request.POST.getlist('cgst_item')
        sgst_item = request.POST.getlist('sgst_item')
        igst_item = request.POST.getlist('igst_item')
        vat_item = request.POST.getlist('vat_item')
        item = request.POST.getlist('item')
        batch = request.POST.getlist('batch')
        totalamount_item = request.POST.getlist('totalamount_item')
        print('narro', date, narration, quaantity_item, distributor_price, cgst_item, sgst_item, igst_item,
              vat_item, totalamount_item)
        try:
            material_center_to = Material_center.objects.get(pk=mc_center_to)
            material_center_from = Material_center.objects.get(pk=mc_center_from)
            user = material_center_to.advisor_registration_number
            data = Sale(
                sale_user_id=request.user,
                material_center_to=material_center_to,
                material_center_from=material_center_from,
                date=date,
                narration=narration,
                advisor_distributor_name=user,
                party_name=party_name,
                sale_type=sale_type,
                grand_total=grand_total,
                sale_to=Sale.SALE_TO_DISTRIBUTOR
            )
            data.save()
            try:
                for i, k in enumerate(totalamount_item):
                    sale = data
                    print('obcet', sale)
                    quantity = quaantity_item[i]
                    price = distributor_price[i]
                    cgst = cgst_item[i]
                    sgst = sgst_item[i]
                    igst = igst_item[i]
                    # vat = vat_item[i]
                    total_amount = totalamount_item[i]
                    product = item[i]
                    product = Product.objects.get(pk=product)
                    batch1 = batch[i]
                    batch1 = Batch.objects.get(pk=batch1)
                    # inventory code start
                    product_quantity_update = int(product.quantity) - int(quantity)
                    p_quantity_update = Product.objects.filter(pk=product.pk).update(quantity=product_quantity_update)
                    batch_quantity = batch1.quantity
                    update_batch_quantity = int(batch_quantity) - int(quantity)
                    Batch.objects.filter(pk=batch1.pk).update(quantity=update_batch_quantity)
                    try:
                        calculateTodayInventry(
                            product=product,
                            batch=batch1,
                            quantity=quantity,
                            material_center=material_center_from,
                        )
                    except:
                        try:
                            updateInventry(
                                product=product,
                                batch=batch1,
                                quantity=quantity,
                                material_center=material_center_from
                            )
                        except:
                            addInventry(
                                product=product,
                                batch=batch1,
                                material_center=material_center_from,
                                quantity=quantity
                            )

                    pv = calculated_point_value(product, price, quantity)
                    bv = calculated_business_value(product, price, quantity)
                    saledata = Sale_itemDetails(item=product, sale=sale, batch=batch1, quantity=quantity,
                                                distributor_price=price, cgst=cgst, sgst=sgst, igst=igst,
                                                total_amount=total_amount, pv=pv, bv=bv)
                    saledata.save()

                saleId = Sale.objects.get(pk=data.id)
                pv = sum([li.pv for li in saleId.sale_itemdetails_set.all()])
                bv = sum([li.bv for li in saleId.sale_itemdetails_set.all()])
                grand_total = sum([li.total_amount for li in saleId.sale_itemdetails_set.all()])
                Sale.objects.filter(pk=data.id).update(grand_pv=pv, grand_bv=bv, grand_total=grand_total)

                messages.success(request, "Record added successfully!")
                return redirect('sale_list')
            except:
                messages.success(request, "Something is going wrong")
                return redirect('sale_list')

        except:
            messages.warning(request, "Something is going wrong")
            return redirect('sale_list')
    # except:
    #     messages.warning(request, "You Try to add wrong data please check and try again")
    material_center_to = Material_center.objects.filter(company_depot='NO').exclude(delete=True)
    material_center_from = Material_center.objects.filter(company_depot='YES', frontend=True).exclude(delete=True)
    batches = Batch.objects.all().exclude(delete=True)
    items = Product.objects.all().exclude(delete=True)
    users = User.objects.all()
    myDate = datetime.now()
    formatedDate = myDate.strftime("%Y-%m-%d")
    params = {
        'material_center_to': material_center_to,
        'material_center_from': material_center_from,
        'sale_to_options': ['Distributor', 'C&F'],
        'batches': batches,
        'items': items,
        'users': users,
        'prod_id': 1,
        'date': formatedDate,
        'title': 'Add Sale'
    }
    return render(request, 'mlm_admin/add_sale.html', params)


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['sale_management', ['1']])
def add_sale_cnf(request):
    if request.method == "POST":
        # try:
        date = request.POST['date']
        mc_center_to = request.POST['mc_center_to']
        mc_center_from = request.POST['mc_center_from']
        narration = request.POST['narration']
        party_name = request.POST['party_name']
        sale_type = request.POST['sale_type']
        grand_total = request.POST['grand_total']
        user = request.POST['user']
        quaantity_item = request.POST.getlist('quaantity_item')
        check_quantity = request.POST.getlist('check_quantity')
        result = quantity_validate(check_quantity, quaantity_item)
        if result == False:
            messages.success(request, "Bad Request (Quantity entered is greater than maximum allowed quantity).")
            return redirect('add_sale')
        distributor_price = request.POST.getlist('distributor_price')
        cgst_item = request.POST.getlist('cgst_item')
        sgst_item = request.POST.getlist('sgst_item')
        igst_item = request.POST.getlist('igst_item')
        # vat_item = request.POST.getlist('vat_item')
        item = request.POST.getlist('item')
        batch = request.POST.getlist('batch')
        totalamount_item = request.POST.getlist('totalamount_item')
        print('narro', date, narration, quaantity_item, distributor_price, cgst_item, sgst_item, igst_item,
              totalamount_item)
        try:
            material_center_to = Material_center.objects.get(pk=mc_center_to)
            material_center_from = Material_center.objects.get(pk=mc_center_from)
            user = User.objects.get(pk=user)
            data = Sale(
                sale_user_id=request.user,
                material_center_to=material_center_to,
                material_center_from=material_center_from,
                date=date,
                narration=narration,
                advisor_cnf_name=user,
                party_name=party_name,
                sale_type=sale_type,
                grand_total=grand_total,
                sale_to=Sale.SALE_TO_CNF
            )
            data.save()
            try:
            # if 1 == 1:
                for i, k in enumerate(totalamount_item):
                    sale = data
                    print('obcet', sale)
                    quantity = quaantity_item[i]
                    product = item[i]
                    product = Product.objects.get(pk=product)
                    batch1 = batch[i]
                    batch1 = Batch.objects.get(pk=batch1)

                    mrp = batch1.mrp or 0
                    cgst = product.cgst or 0
                    sgst = product.sgst or 0
                    igst = product.igst or 0
                    distributor_price = product.distributor_price or 0
                    if sale_type == '1':
                        distributor_price = mrp / ((100 + igst) / 100) / ((100 + distributor_price) / 100)
                        igst = distributor_price * (igst / 100)
                        cgst = 0
                        sgst = 0
                        vat = 0 # distributor_price * (vat / 100)
                    else:
                        distributor_price = mrp / ((100 + (sgst + cgst)) / 100) / ((100 + distributor_price) / 100)
                        cgst = distributor_price * (cgst / 100)
                        sgst = distributor_price * (sgst / 100)
                        vat = 0 # distributor_price * (vat / 100)
                        igst = 0
                    distributor_price = round(distributor_price, 2)
                    cgst = round(cgst, 2)
                    sgst = round(sgst, 2)
                    vat = round(vat, 2)
                    igst = round(igst, 2)
                    total_amount = int(quantity) * (distributor_price + cgst + sgst + igst)
                    total_amount = round(total_amount, 2)
                    # inventory code start
                    product_quantity_update = int(product.quantity) - int(quantity)
                    p_quantity_update = Product.objects.filter(pk=product.pk).update(quantity=product_quantity_update)
                    batch_quantity = batch1.quantity
                    update_batch_quantity = int(batch_quantity) - int(quantity)
                    Batch.objects.filter(pk=batch1.pk).update(quantity=update_batch_quantity)
                    try:
                        calculateTodayInventry(
                            product=product,
                            batch=batch1,
                            quantity=quantity,
                            material_center=material_center_from,
                        )

                    except:
                        try:
                            updateInventry(
                                product=product,
                                batch=batch1,
                                quantity=quantity,
                                material_center=material_center_from
                            )
                        except:
                            addInventry(
                                product=product,
                                batch=batch1,
                                material_center=material_center_from,
                                quantity=quantity
                            )
                    # inventory code end
                    pv = calculated_point_value(product, distributor_price, quantity)
                    bv = calculated_business_value(product, distributor_price, quantity)
                    saledata = Sale_itemDetails(
                        item=product,
                        sale=sale,
                        batch=batch1,
                        quantity=quantity,
                        distributor_price=distributor_price,
                        cgst=cgst,
                        sgst=sgst,
                        igst=igst,
                        total_amount=total_amount,
                        pv=pv,
                        bv=bv
                    )
                    saledata.save()

                saleId = Sale.objects.get(pk=data.id)
                grand_pv = sum([li.pv for li in saleId.sale_itemdetails_set.all()])
                grand_bv = sum([li.bv for li in saleId.sale_itemdetails_set.all()])
                grand_total = sum([li.total_amount for li in saleId.sale_itemdetails_set.all()])
                Sale.objects.filter(pk=data.id).update(grand_pv=grand_pv,
                                                       grand_bv=grand_bv,
                                                       grand_total=grand_total)

                messages.success(request, "Record added successfully!")
                return redirect('sale_list')
            except Exception as e:
                messages.success(request, "Something is going wrong! " +  str(e))
                return redirect('sale_list')

        except Exception as e:
            messages.warning(request, "Something is going wrong " + str(e))
            return redirect('sale_list')
    # except:
    #     messages.warning(request, "You Try to add wrong data please check and try again")
    material_center_to = Material_center.objects.filter(company_depot='YES', frontend=False).exclude(delete=True)
    material_center_from = Material_center.objects.filter(company_depot='YES', frontend=True).exclude(delete=True)
    batches = Batch.objects.all().exclude(delete=True)
    items = Product.objects.all().exclude(delete=True)
    users = User.objects.all()
    myDate = datetime.now()
    formatedDate = myDate.strftime("%Y-%m-%d")
    print('to mc', material_center_to.count())
    params = {
        'material_center_to': material_center_to,
        'material_center_from': material_center_from,
        'sale_to_options': ['Distributor', 'C&F'],
        'batches': batches,
        'items': items,
        'users': users,
        'prod_id': 1,
        'date': formatedDate,
        'title': 'Add Sale'
    }
    return render(request, 'mlm_admin/add_sale_cnf.html', params)


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['sale_management', ['1']])
def add_loyalty_sale(request):
    print('something is better than nothing')
    if request.method == "POST":
        # try:
        date = request.POST['date']
        mc_center_to = request.POST['mc_center_to']
        print(mc_center_to, '<----here we are geting the mc_center_to')
        mc_center_from = request.POST['mc_center_from']
        narration = request.POST['narration']
        party_name = request.POST['party_name']
        sale_type = request.POST['sale_type']
        grand_total = request.POST['grand_total']
        user = request.POST['user']
        quaantity_item = request.POST.getlist('quaantity_item')
        check_quantity = request.POST.getlist('check_quantity')
        result = quantity_validate(check_quantity, quaantity_item)
        if result == False:
            messages.success(request, "Bad Request (Quantity entered is greater than maximum allowed quantity).")
            return redirect('add_sale')
        distributor_price = request.POST.getlist('distributor_price')
        cgst_item = request.POST.getlist('cgst_item')
        sgst_item = request.POST.getlist('sgst_item')
        igst_item = request.POST.getlist('igst_item')
        vat_item = request.POST.getlist('vat_item')
        item = request.POST.getlist('item')
        batch = request.POST.getlist('batch')
        totalamount_item = request.POST.getlist('totalamount_item')
        print('narro', date, narration, quaantity_item, distributor_price, cgst_item, sgst_item, igst_item,
              vat_item, totalamount_item)
        try:
            material_center_to = Material_center.objects.get(pk=mc_center_to)
            material_center_from = Material_center.objects.get(pk=mc_center_from)
            user = User.objects.get(pk=user)
            data = Sale(sale_user_id=request.user, material_center_to=material_center_to,
                        material_center_from=material_center_from, date=date,
                        narration=narration, advisor_cnf_name=user,
                        party_name=party_name, sale_type=sale_type, grand_total=grand_total, sale_to=Sale.SALE_TO_CNF)
            data.save()
            try:
                for i, k in enumerate(totalamount_item):
                    sale = data
                    print('obcet', sale)
                    quantity = quaantity_item[i]
                    # cgst = cgst_item[i]
                    # sgst = sgst_item[i]
                    # igst = igst_item[i]
                    vat = vat_item[i]
                    product = item[i]
                    product = Product.objects.get(pk=product)
                    batch1 = batch[i]
                    batch1 = Batch.objects.get(pk=batch1)

                    mrp = batch1.mrp or 0
                    cgst = product.cgst or 0
                    sgst = product.sgst or 0
                    igst = product.igst or 0
                    distributor_price = product.distributor_price or 0
                    if sale_type == '1':
                        distributor_price = mrp / ((100 + igst) / 100) / ((100 + distributor_price) / 100)
                        igst = distributor_price * (igst / 100)
                        cgst = 0
                        sgst = 0
                        vat = distributor_price * (vat / 100)
                    else:
                        distributor_price = mrp / ((100 + (sgst + cgst)) / 100) / ((100 + distributor_price) / 100)
                        cgst = distributor_price * (cgst / 100)
                        sgst = distributor_price * (sgst / 100)
                        vat = distributor_price * (vat / 100)
                        igst = 0
                    distributor_price = round(distributor_price, 2)
                    cgst = round(cgst, 2)
                    sgst = round(sgst, 2)
                    vat = round(vat, 2)
                    igst = round(igst, 2)
                    price = distributor_price
                    total_amount = int(quantity) * (distributor_price + cgst + sgst + igst)
                    total_amount = round(total_amount, 2)
                    # inventory code start
                    product_quantity_update = int(product.quantity) - int(quantity)
                    p_quantity_update = Product.objects.filter(pk=product.pk).update(quantity=product_quantity_update)
                    batch_quantity = batch1.quantity
                    update_batch_quantity = int(batch_quantity) - int(quantity)
                    Batch.objects.filter(pk=batch1.pk).update(quantity=update_batch_quantity)
                    try:
                        calculateTodayInventry(
                            product=product,
                            batch=batch1,
                            quantity=quantity,
                            material_center=material_center_from,
                        )

                    except:
                        try:
                            updateInventry(
                                product=product,
                                batch=batch1,
                                quantity=quantity,
                                material_center=material_center_from
                            )
                        except:
                            addInventry(
                                product=product,
                                batch=batch1,
                                material_center=material_center_from,
                                quantity=quantity
                            )
                    # inventory code end
                    saledata = Sale_itemDetails(item=product, sale=sale, batch=batch1, quantity=quantity,
                                                distributor_price=price, cgst=cgst, sgst=sgst, igst=igst, vat=vat,
                                                total_amount=total_amount, )
                    saledata.save()
                messages.success(request, "Record added successfully!")
                return redirect('sale_list')
            except:
                messages.success(request, "Record added successfully!")
                return redirect('sale_list')

        except Exception as e:
            print(e)
            messages.warning(request, "something is going wrong")
            return redirect('sale_list')
    # except:
    #     messages.warning(request, "You Try to add wrong data please check and try again")
    material_center_to = Material_center.objects.filter(company_depot='YES', frontend=False).exclude(delete=True)
    material_center_from = Material_center.objects.filter(company_depot='YES', frontend=True).exclude(delete=True)
    batches = Batch.objects.all().exclude(delete=True)
    items = Product.objects.filter(loyalty_purchase='YES').exclude(delete=True)
    users = User.objects.all()
    myDate = datetime.now()
    formatedDate = myDate.strftime("%Y-%m-%d")
    print('to mc', material_center_to.count())
    params = {
        'material_center_to': material_center_to,
        'material_center_from': material_center_from,
        'sale_to_options': ['Distributor', 'C&F'],
        'batches': batches,
        'items': items,
        'users': users,
        'prod_id': 1,
        'date': formatedDate,
        'title': 'Add Sale'
    }
    return render(request, 'mlm_admin/add_loyalty_sale.html', params)


@csrf_exempt
def add_saleField(request):
    cnt_multiple_product = request.POST['cnt_multiple_product']
    items = Product.objects.all().exclude(delete=True)
    batches = Batch.objects.all().exclude(delete=True)
    params = {
        'items': items,
        'batches': batches,
        'cnt_multiple_product': cnt_multiple_product
    }
    return render(request, 'mlm_admin/add_saleField.html', params)


@csrf_exempt
def edit_saleField(request):
    cnt_multiple_product = request.POST['cnt_multiple_product']
    items = Product.objects.all().exclude(delete=True)
    batches = Batch.objects.all().exclude(delete=True)
    params = {
        'items': items,
        'batches': batches,
        'cnt_multiple_product': cnt_multiple_product
    }
    return render(request, 'mlm_admin/edit_saleField.html', params)


@csrf_exempt
def check_f(request):
    cnt_multiple_seq_no = request.POST['cnt_multiple_seq_no']
    item_id = request.POST['cnt_multiple_product']
    item = Product.objects.get(pk=item_id, delete=False)
    batches = item.batch_set.filter(delete=False)
    params = {
        # 'items': item,
        'batches': batches,
        'cnt_multiple_product': cnt_multiple_seq_no
    }
    return render(request, 'mlm_admin/produ_check.html', params)


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['sale_management', ['1', '2', '3', '4']])
def sale_list(request, cf=False):
    today = datetime.now().date()
    if cf:
        cf_filter = [False]
    else:
        cf_filter = [True, False]

    if 'q' in request.GET:
        q = request.GET.get('q', False)
        data = Sale.objects.filter(Q(pk__icontains=q) | Q(material_center_to__mc_name__icontains=q) | Q(
            material_center_from__mc_name__icontains=q) | Q(created_on__icontains=q) | Q(party_name__icontains=q)
                                   | Q(grand_total__icontains=q), delete=False, material_center_from__frontend__in=cf_filter).order_by('-id')
    else:
        q = ''
        data = Sale.objects.filter(delete=False, material_center_from__frontend__in=cf_filter).order_by('-id')

    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'mlm_admin/sale_list.html', {'data': page_obj, 'title': 'Sale List', 'q': q, 'today': today})

@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['sale_management', ['1', '2', '3', '4']])
def cf_sale_list(request):
    response = sale_list(request, cf=True)
    return response

@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['sale_management', ['2']])
def edit_sale(request, myid):
    if request.method == "POST":
        date = request.POST['date']
        mc_center_to = request.POST['mc_center_to']
        mc_center_from = request.POST['material_center_from']
        narration = request.POST['narration']
        user = request.POST['user']
        party_name = request.POST['party_name']
        sale_type = request.POST['sale_type']
        grand_total = request.POST['grand_total']
        quaantity_item = request.POST.getlist('quaantity_item')
        check_quantity = request.POST.getlist('check_quantity')
        result = quantity_validate(check_quantity, quaantity_item)
        if result == False:
            messages.success(request, "Bad Request (Quantity entered is greater than maximum allowed quantity).")
            return redirect('sale_list')
        print(check_quantity)
        print(quaantity_item)
        print(len(check_quantity), '--------', len(quaantity_item))
        distributor_price = request.POST.getlist('distributor_price')
        cgst_item = request.POST.getlist('cgst_item')
        sgst_item = request.POST.getlist('sgst_item')
        igst_item = request.POST.getlist('igst_item')
        vat_item = request.POST.getlist('vat_item')
        item = request.POST.getlist('item')
        batch = request.POST.getlist('batch')
        totalamount_item = request.POST.getlist('totalamount_item')
        print('narro', date, narration, quaantity_item, distributor_price, cgst_item, sgst_item, igst_item,
              vat_item, totalamount_item, 'item', item, 'batch', batch)
        try:
            material_center_to = Material_center.objects.get(pk=mc_center_to)
            material_center_from = Material_center.objects.get(pk=mc_center_from)
            user = User.objects.get(pk=user)
            data = Sale.objects.filter(pk=myid).update(sale_user_id=request.user, material_center_to=material_center_to,
                                                       material_center_from=material_center_from, date=date,
                                                       narration=narration,
                                                       advisor_distributor_name=user, sale_type=sale_type,
                                                       party_name=party_name, grand_total=grand_total)
            obj = Sale.objects.get(pk=myid)
            sale_items = Sale_itemDetails.objects.filter(sale=obj)
            for i in sale_items:
                update_time_batch_quantity = int(i.batch.quantity) + int(i.quantity)
                update_time_product_quantity = int(i.item.quantity) + int(i.quantity)
                Batch.objects.filter(pk=i.batch.pk).update(quantity=update_time_batch_quantity)
                Product.objects.filter(pk=i.item.pk).update(quantity=update_time_product_quantity)
                today = datetime.now().date()
                update_time_inventry = Inventry.objects.get(created_on=today, product=i.item,
                                                            batch=i.batch, material_center=material_center_from)
                update_time_inventry_current_quantity = int(update_time_inventry.current_quantity) + int(i.quantity)
                update_time_inventry_quantity_out = int(update_time_inventry.quantity_out) - int(i.quantity)
                Inventry.objects.filter(created_on=today, product=i.item, batch=i.batch,
                                        material_center=material_center_from).update(
                    current_quantity=update_time_inventry_current_quantity,
                    quantity_out=update_time_inventry_quantity_out)
            Sale_itemDetails.objects.filter(sale=obj).delete()
            try:
                for i, k in enumerate(totalamount_item):
                    sale = obj
                    print('obcet', sale)
                    quantity = quaantity_item[i]
                    price = distributor_price[i]
                    cgst = cgst_item[i]
                    sgst = sgst_item[i]
                    igst = igst_item[i]
                    # vat = vat_item[i]
                    total_amount = totalamount_item[i]
                    product = item[i]
                    product = Product.objects.get(pk=product)
                    batch1 = batch[i]
                    batch1 = Batch.objects.get(pk=batch1)
                    update_product_quantity = (product.quantity - int(quantity))
                    p_quantity_update = Product.objects.filter(pk=product.pk).update(quantity=update_product_quantity)
                    batch_quantity = batch1.quantity
                    update_batch_quantity = int(batch_quantity) - int(quantity)
                    Batch.objects.filter(pk=batch1.pk).update(quantity=update_batch_quantity)
                    try:
                        calculateTodayInventry(
                            product=product,
                            batch=batch1,
                            quantity=quantity,
                            material_center=material_center_from,
                        )
                    except:
                        return HttpResponse('<h1> Please check your code something is wrong </h1>')

                    #  inventory code end
                    pv = calculated_point_value(product, price, quantity)
                    bv = calculated_business_value(product, price, quantity)
                    sale_details_data = Sale_itemDetails(item=product, batch=batch1, sale=sale, quantity=quantity,
                                                         distributor_price=price, cgst=cgst, sgst=sgst, igst=igst,
                                                         total_amount=total_amount,
                                                         pv=pv,
                                                         bv=bv)

                    sale_details_data.save()
                    saleId = Sale.objects.get(pk=myid)
                    grand_pv = sum([li.pv for li in saleId.sale_itemdetails_set.all()])
                    grand_bv = sum([li.bv for li in saleId.sale_itemdetails_set.all()])
                    grand_total = sum([li.total_amount for li in saleId.sale_itemdetails_set.all()])
                    Sale.objects.filter(pk=myid).update(grand_pv=grand_pv, grand_bv=grand_bv, grand_total=grand_total)

                messages.success(request, "Record added successfully!")
                return redirect('sale_list')
            except:
                messages.success(request, "Something is going wrong")
                return redirect('sale_list')

        except Exception as e:

            messages.warning(request, "Something is going wrong")
            return redirect('sale_list')
    material_center_to = Material_center.objects.filter(company_depot='NO').exclude(delete=True)
    material_center_from = Material_center.objects.filter(company_depot='YES').exclude(delete=True)
    batches = Batch.objects.all().exclude(delete=True)
    items = Product.objects.all().exclude(delete=True)
    users = User.objects.all()
    sale_data = Sale.objects.get(pk=myid, accept=False)
    data = Sale_itemDetails.objects.filter(sale=sale_data)
    today = datetime.now().date()
    if sale_data.created_on != today:
        messages.warning(request, 'You are not able to update these records')
        return redirect('sale_list')
    params = {
        'material_center_to': material_center_to,
        'material_center_from': material_center_from,
        'batches': batches,
        'items': items,
        'users': users,
        'sale_data': sale_data,
        'data': data,
        'title': 'Edit Sale'
    }
    return render(request, 'mlm_admin/edit_sale.html', params)


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['sale_management', ['4']])
def delete_sale(request, myid):
    sale = Sale.objects.get(pk=myid)
    today = datetime.now().date()
    if sale.created_on != today:
        messages.warning(request, 'You are not able to delete this records')
        return redirect('sale_list')
    sale_items = Sale_itemDetails.objects.filter(sale=sale)
    for i in sale_items:
        update_time_batch_quantity = int(i.batch.quantity) + int(i.quantity)
        update_time_product_quantity = int(i.item.quantity) + int(i.quantity)
        Batch.objects.filter(pk=i.batch.pk).update(quantity=update_time_batch_quantity)
        Product.objects.filter(pk=i.item.pk).update(quantity=update_time_product_quantity)
        today = datetime.now().date()
        update_time_inventry = Inventry.objects.get(created_on=today, product=i.item,
                                                    batch=i.batch, material_center=sale.material_center_from)
        update_time_inventry_current_quantity = int(update_time_inventry.current_quantity) + int(i.quantity)
        update_time_inventry_quantity_out = int(update_time_inventry.quantity_out) - int(i.quantity)
        Inventry.objects.filter(created_on=today, product=i.item, batch=i.batch,
                                material_center=sale.material_center_from).update(
            current_quantity=update_time_inventry_current_quantity,
            quantity_out=update_time_inventry_quantity_out)
    sale_delete = Sale.objects.filter(pk=myid).update(delete=True)
    return redirect('sale_list')


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['sale_management', ['3']])
def view_sale(request, myid):
    material_center_to = Material_center.objects.filter(company_depot='NO').exclude(delete=True)
    material_center_from = Material_center.objects.filter(company_depot='YES').exclude(delete=True)
    material_c = Material_center.objects.all().exclude(delete=True)
    batches = Batch.objects.all().exclude(delete=True)
    items = Product.objects.all().exclude(delete=True)
    users = User.objects.all()
    sale_data = Sale.objects.get(pk=myid)
    data = Sale_itemDetails.objects.filter(sale=sale_data)
    params = {
        'material_center_to': material_center_to,
        'material_center_from': material_center_from,
        'material_c': material_c,
        'batches': batches,
        'items': items,
        'users': users,
        'sale_data': sale_data,
        'data': data,
        'title': 'View Sale'
    }
    return render(request, 'mlm_admin/view_sale.html', params)


def batch_price(request):
    batchid = request.GET.get('batchid', False)
    myid = request.GET.get('myid', False)
    batch = Batch.objects.get(pk=batchid)
    price_id = myid.replace("batches", "price")
    return JsonResponse(status=200, data={'price': batch.mrp, 'price_id': price_id})


def product_detail(request):
    product_id = request.GET.get('product_id', False)
    batch_id = request.GET.get('batch_id', False)
    material_center_from = request.GET.get('material_center_from', False)
    material = Material_center.objects.get(pk=material_center_from)
    # sale_type= 0 for with in state(cgst+sgst) and sale_type = 1 for inter_state(igst)
    sale_type = request.GET.get('sale_type', False)
    product = Product.objects.get(pk=product_id)
    try:
        batch = Batch.objects.get(pk=batch_id)
    except:
        batch = Batch.objects.filter(pk=product)[0]
    # <-- here we are geting quantity from the inventry code start here -->
    try:
        today = datetime.now().date()
        inventory_update = Inventry.objects.get(product=product, batch=batch, material_center=material,
                                                created_on=today)
        inventory_update_current_quantity = int(inventory_update.current_quantity)
        batch_quantity = int(inventory_update.current_quantity)
    except:
        try:
            inventory_update = Inventry.objects.filter(product=product, batch=batch, material_center=material).latest(
                'created_on')
            inventory = Inventry(product=product, batch=batch, material_center=material,
                                 opening_quantity=inventory_update.current_quantity,
                                 current_quantity=inventory_update.current_quantity,
                                 quantity_in=0, purchase_price=inventory_update.purchase_price)
            batch_quantity = int(inventory_update.current_quantity)
            inventory.save()
        except:
            inventory = Inventry(product=product, batch=batch, material_center=material,
                                 opening_quantity=0, current_quantity=0,
                                 quantity_in=0, purchase_price=0)
            batch_quantity = 0
            inventory.save()

    mrp = batch.mrp
    print('mrp', type(mrp))
    cgst = product.cgst
    sgst = product.sgst
    igst = product.igst
    distributor_price = product.distributor_price
    vat = product.vat
    if cgst == None:
        cgst = 0
    if sgst == None:
        sgst = 0
    if igst == None:
        igst = 0
    if distributor_price == None:
        distributor_price = 0
    if vat == None:
        vat = 0
    print('igst', igst)
    if sale_type == '1':
        distributor_price = mrp / ((100 + igst) / 100) / ((100 + distributor_price) / 100)
        igst = distributor_price * (igst / 100)
        cgst = 0
        sgst = 0
        vat = distributor_price * (vat / 100)
    else:
        distributor_price = mrp / ((100 + (sgst + cgst)) / 100) / ((100 + distributor_price) / 100)
        cgst = distributor_price * (cgst / 100)
        sgst = distributor_price * (sgst / 100)
        vat = distributor_price * (vat / 100)
        igst = 0
    distributor_price = round(distributor_price, 2)
    cgst = round(cgst, 2)
    sgst = round(sgst, 2)
    vat = round(vat, 2)
    igst = round(igst, 2)
    print(mrp)
    print('distributor_price', distributor_price)
    params = {
        'distributor_price': distributor_price,
        'cgst': cgst,
        'sgst': sgst,
        'igst': igst,
        'vat': vat,
        'pv': batch.pv,
        'bv': batch.bv,
        'batch_quantity': batch_quantity
    }
    return JsonResponse(status=200, data=params)


def batch_field(request):
    myid = request.GET.get('myid', False)
    product_id = request.GET.get('product_id', False)
    cnt_multiple_product = request.GET.get('cnt_multiple_product', False)
    try:
        product = Product.objects.get(pk=product_id)
        batch = Batch.objects.filter(product=product, delete=False)
    except:
        batch = []

    if batch:
        batch_list = []
        if not request.user.profile.mlm_admin:
            if request.user.profile.distributor:
                d_inventory = Distributor_Inventry.objects.filter(batch__in=batch,
                                                                  material_center__advisor_registration_number=request.user,
                                                                  created_on=datetime.today(),)
                for i in d_inventory:
                    if i.current_quantity > 0:
                        batch_list.append(i.batch.pk)

            if request.user.profile.c_and_f_admin:
                inventory = Inventry.objects.filter(batch__in=batch,
                                                    material_center__advisor_registration_number = request.user,
                                                    created_on=datetime.today(),)
                for i in inventory:
                    if i.current_quantity > 0:
                        batch_list.append(i.batch.pk)

            batch_list = set(batch_list)

            try:
                batch = Batch.objects.filter(pk__in=batch_list)
            except:
                batch = []

    params = {
        'batch': batch,
        'cnt_multiple_product': cnt_multiple_product,
    }
    return render(request, 'mlm_admin/batch_field.html', params)


def editbatch_field(request):
    product_id = request.GET.get('product_id', False)
    cnt_multiple_product = request.GET.get('cnt_multiple_product', False)
    myid = request.GET.get('myid', False)
    product = Product.objects.get(pk=product_id)
    batch = Batch.objects.filter(product=product).exclude(delete=True)
    params = {
        'batch': batch,
        'cnt_multiple_product': cnt_multiple_product
    }
    return render(request, 'mlm_admin/editbatch_field.html', params)


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['manual_verification', ['1', '2', '3', '4']])
def manual_verification(request):
    verification_list = ManualVerification.objects.all()
    paginator = Paginator(verification_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'mlm_admin/manual_verification.html', {'verification_list': page_obj})


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['manual_verification',['1','2','3','4']])
def mv_details(request, myid):
    if request.method == 'POST':
        verify_detail = ManualVerification.objects.get(pk=myid)

        verify_detail.verified = request.POST["verified"]

        verify_detail.save()
        if verify_detail.verified == "True":
            kyc = Kyc.objects.get(kyc_user=verify_detail.kyc_user)
            kyc.kyc_done = verify_detail.verified
            kyc.manual = True
            kyc.save()
            kyc_done = KycDone.objects.get(kyc_user=verify_detail.kyc_user)
            kyc_done.kyc_verification_type = "Manually"
            kyc_done.save()
        else:
            kyc = Kyc.objects.get(kyc_user=verify_detail.kyc_user)

            kyc.kyc_done = False
            kyc.manual = False
            kyc.save()
            kyc_done = KycDone.objects.get(kyc_user=verify_detail.kyc_user)
            kyc_done.kyc_verification_type = "None"
            kyc_done.save()
        messages.success(request, f"Action for PAN {verify_detail.pan_number} performed")
        return render(request, 'mlm_admin/verify_detail.html', {'verify_detail': verify_detail})

    verify_detail = ManualVerification.objects.get(pk=myid)
    print(verify_detail.pan_file.path)

    return render(request, 'mlm_admin/verify_detail.html', {'verify_detail': verify_detail})


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['manual_verification', ['1', '2', '3', '4']])
def bank_manual_verification(request):
    print("Inside manual verification")
    verification_list = ManualVerification.objects.all()
    paginator = Paginator(verification_list, 10)
    print(paginator, 'paginator')
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'mlm_admin/bank_manual_verification.html', {'verification_list': page_obj})


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['wallet_cofiguration',['1','2','3','4']])
def wallet_cofiguration_list(request):
    print("Wallet Configuration")
    with transaction.atomic():
        wallet_list = Wallet.objects.all()
    paginator = Paginator(wallet_list, 10)
    print(paginator, 'paginator')
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'mlm_admin/wallet_cofiguration_list.html', {'wallet_list': page_obj})


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['manual_verification',['1','2','3','4']])
def wc_details(request, myid):
    with transaction.atomic():
        wallet_detail = Wallet.objects.get(pk=myid)

    return render(request, 'mlm_admin/wallet_detail.html', {'wallet_detail': wallet_detail})


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['manual_verification',['1','2','3','4']])
def wallet_detail_edit(request, myid):
    if request.method == 'POST':
        with transaction.atomic():
            wallet = Wallet.objects.get(pk=myid)
            if request.POST["action"] == "plus":
                wallet.deposit(int(request.POST['balance']))
            elif request.POST["action"] == "min":
                wallet.withdraw(int(request.POST['balance']))

            wallet.type = request.POST["type"]
            wallet.narration = request.POST["narration"]
            wallet.remarks = request.POST["remarks"]
            wallet.added_by_detail = request.POST["added_by_detail"]
            wallet.save()
        return HttpResponseRedirect(reverse('wallet_details', kwargs={'myid': myid}))
    with transaction.atomic():
        wallet_detail = Wallet.objects.get(pk=myid)

    return render(request, 'mlm_admin/wallet_detail_edit.html', {'wallet_detail': wallet_detail})


def wallet_transaction(request, myid):
    with transaction.atomic():
        wallet = Wallet.objects.get(pk=myid)
        transactions = Transaction.objects.filter(wallet=wallet)
    paginator = Paginator(transactions, 10)
    print(paginator, 'paginator')
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'mlm_admin/transaction_history.html', {'transactions': page_obj})


def purchase_product_detail(request):
    product_id = request.GET.get('product_id', False)
    batch_id = request.GET.get('batch_id', False)
    purchase_type = request.GET.get('purchase_type', False)
    product = Product.objects.get(pk=product_id)
    batch = Batch.objects.get(pk=batch_id)
    mrp = batch.mrp
    cgst = product.cgst
    sgst = product.sgst
    igst = product.igst
    vat = product.vat
    if cgst == None:
        cgst = 0
    if sgst == None:
        sgst = 0
    if igst == None:
        igst = 0
    if vat == None:
        vat = 0
    print('price--->', mrp)
    price = mrp
    if mrp == None:
        mrp = 0
    # igst = mrp * (igst / 100)
    # cgst = mrp * (cgst / 100)
    # sgst = mrp * (sgst / 100)
    # vat = mrp * (vat / 100)
    params = {
        'price': price,
        'cgst': cgst,
        'sgst': sgst,
        'igst': igst,
        'vat': vat,
        'pv': batch.pv,
        'bv': batch.bv
    }
    return JsonResponse(status=200, data=params)


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['inventory_management', ['1', '2', '3', '4']])
def inventory_details(request):
    if request.method == 'POST':
        stock_details = request.POST['stock_details']
        type = request.POST['m_center']
        select_all = request.POST.getlist('select_all')
        purchase_price = request.POST.getlist('purchase_price')
        distributor_price_with_tax = request.POST.getlist('distributor_price_with_tax')
        distributor_price_without_tax = request.POST.getlist('distributor_price_without_tax')
        mrp = request.POST.getlist('mrp')
        bussiness_volume = request.POST.getlist('bussiness_volume')
        point_value = request.POST.getlist('point_value')
        tax_percentage = request.POST.getlist('tax_percentage')
        tax_amount = request.POST.getlist('tax_amount')
        stock = request.POST['stock']
        if len(select_all) == 1:
            purchase_price = True
            distributor_price_with_tax = True
            distributor_price_without_tax = True
            mrp = True
            bussiness_volume = True
            point_value = True
            tax_amount = True
            tax_percentage = True
        else:
            if len(purchase_price) == 1:
                purchase_price = True
            if len(distributor_price_with_tax) == 1:
                distributor_price_with_tax = True
            if len(distributor_price_without_tax) == 1:
                distributor_price_without_tax = True
            if len(mrp) == 1:
                mrp = True
            if len(bussiness_volume) == 1:
                bussiness_volume = True
            if len(point_value) == 1:
                point_value = True
            if len(tax_amount) == 1:
                tax_amount = True
            if len(tax_percentage) == 1:
                tax_percentage = True

        if stock_details == 'balance':
            blance_date = request.POST['blance_date']
            if type == 'all_mc':
                if stock == 'yes':
                    inventry = Inventry.objects.filter(created_on=blance_date, current_quantity__gt=0)
                elif stock == 'no':
                    inventry = Inventry.objects.filter(created_on=blance_date, current_quantity__gt=0)
            elif type == 'o_mc':
                o_material_center = request.POST['o_material_center']
                material_pk = o_material_center
                if stock == 'yes':
                    inventry = Inventry.objects.filter(created_on=blance_date, material_center__pk=material_pk, current_quantity__gt=0)
                elif stock == 'no':
                    inventry = Inventry.objects.filter(created_on=blance_date, material_center__pk=material_pk,
                                                       current_quantity__gt=0)
            elif type == 's_mc':
                s_material_center = request.POST.getlist('s_material_center')
                if stock == 'yes':
                    inventry = Inventry.objects.filter(material_center__in=s_material_center, created_on=blance_date, current_quantity__gt=0)
                elif stock == 'no':
                    inventry = Inventry.objects.filter(material_center__in=s_material_center, created_on=blance_date,
                                                       current_quantity__gt=0)

            material = Material_center.objects.all().exclude(delete=True)
            product = []

            for i in inventry:
                # AG :: Adding product to the list and checking for repeatation.
                if i.product not in product:
                    for_quantity = inventry.filter(product=i.product)
                    qty = 0
                    batch_quantity = 0

                    for k in for_quantity:
                        qty = qty + k.current_quantity
                        i.product.quantity = qty
                        if k.batch.quantity > batch_quantity:
                            batch_quantity = k.batch.quantity
                            i.product.mrp = k.batch.mrp

                    product.append(i.product)

            params = {
                'purchase_price': purchase_price,
                'distributor_price_with_tax': distributor_price_with_tax,
                'distributor_price_without_tax': distributor_price_without_tax,
                'mrp': mrp,
                'bussiness_volume': bussiness_volume,
                'point_value': point_value,
                'tax_percentage': tax_percentage,
                'inventory': inventry,
                'product': product,
                'title': 'Inventory Details'
            }

            if request.POST['batch'] == 'yes':
                return render(request, 'mlm_admin/blanceDetails-list.html', params)
            if request.POST['batch'] == 'no':
                return render(request, 'mlm_admin/No_blanceDetails-list.html', params)

        elif stock_details == 'detail':
            detail_end_date = request.POST['detail_end_date']
            detail_start_date = request.POST['detail_start_date']

            if type == 'all_mc':
                inventry_data = Inventry.objects.filter(created_on__range=[detail_start_date, detail_end_date])
                if stock == 'no':
                    today = datetime.now().date()
                    check_inventry = Inventry.objects.filter(created_on=today, current_quantity=0)
                    for i in check_inventry:
                        inventry_data = inventry_data.exclude(product=i.product, batch=i.batch,
                                                              material_center=i.material_center)
                inventry = []
                for i in inventry_data:
                    if len(inventry) == 0:
                        inventry.append(i)
                    else:
                        check = 0
                        # for count, value in enumerate(values):
                        for count, j in enumerate(inventry):
                            if i.material_center == j.material_center and i.batch == j.batch:
                                if i not in inventry:
                                    if int(j.purchase_price) == 0:
                                        j.purchase_price = i.purchase_price
                                    j.current_quantity = i.current_quantity
                                    j.quantity_in = int(i.quantity_in) + int(j.quantity_in)
                                    j.quantity_out = int(i.quantity_out) + int(j.quantity_out)
                                    check = check + 1
                            elif (len(inventry) == (count + 1) and check == 0):
                                inventry.append(i)

            elif type == 'o_mc':
                o_material_center = request.POST['o_material_center']
                material_pk = o_material_center
                inventry_data = Inventry.objects.filter(created_on__range=[detail_start_date, detail_end_date],
                                                        material_center__pk=material_pk)
                if stock == 'no':
                    today = datetime.now().date()
                    check_inventry = Inventry.objects.filter(created_on=today, current_quantity=0)
                    for i in check_inventry:
                        inventry_data = inventry_data.exclude(product=i.product, batch=i.batch,
                                                              material_center=i.material_center)
                inventry = []
                for i in inventry_data:
                    if len(inventry) == 0:
                        inventry.append(i)
                    else:
                        check = 0
                        # for count, value in enumerate(values):
                        for count, j in enumerate(inventry):
                            if i.material_center == j.material_center and i.batch == j.batch:
                                if i not in inventry:
                                    if int(j.purchase_price) == 0:
                                        j.purchase_price = i.purchase_price
                                    j.current_quantity = i.current_quantity
                                    j.quantity_in = int(i.quantity_in) + int(j.quantity_in)
                                    j.quantity_out = int(i.quantity_out) + int(j.quantity_out)
                                    check = check + 1
                            elif (len(inventry) == (count + 1) and check == 0):
                                inventry.append(i)
            elif type == 's_mc':
                s_material_center = request.POST.getlist('s_material_center')

                inventry_data = Inventry.objects.filter(material_center__in=s_material_center,
                                                        created_on__range=[detail_start_date, detail_end_date])
                if stock == 'no':
                    today = datetime.now().date()
                    check_inventry = Inventry.objects.filter(created_on=today, current_quantity=0)
                    for i in check_inventry:
                        inventry_data = inventry_data.exclude(product=i.product, batch=i.batch,
                                                              material_center=i.material_center)
                inventry = []
                for i in inventry_data:
                    if len(inventry) == 0:
                        inventry.append(i)
                    else:
                        check = 0
                        # for count, value in enumerate(values):
                        for count, j in enumerate(inventry):
                            if i.material_center == j.material_center and i.batch == j.batch:
                                if i not in inventry:
                                    if int(j.purchase_price) == 0:
                                        j.purchase_price = i.purchase_price
                                    j.current_quantity = i.current_quantity
                                    j.quantity_in = int(i.quantity_in) + int(j.quantity_in)
                                    j.quantity_out = int(i.quantity_out) + int(j.quantity_out)
                                    check = check + 1
                            elif (len(inventry) == (count + 1) and check == 0):
                                inventry.append(i)
            product = Product.objects.all().exclude(delete=True)
            product = []
            # if request.POST['batch'] == 'yes':
            for i in inventry:
                if i.product not in product:
                    current_qty = 0
                    batch_quantity = 0
                    opening_qty = 0
                    in_qty = 0
                    out_qty = 0
                    for k in inventry:
                        if k.product == i.product:
                            current_qty = current_qty + k.current_quantity
                            opening_qty = k.opening_quantity
                            in_qty = in_qty + k.quantity_in
                            out_qty = out_qty + k.quantity_out
                            if k.batch.quantity > batch_quantity:
                                batch_quantity = k.batch.quantity
                                i.product.mrp = k.batch.mrp
                    i.product.quantity = current_qty
                    i.product.minimum_purchase_quantity = opening_qty
                    i.product.item_package_quantity = in_qty
                    i.product.weight = out_qty
                    product.append(i.product)
            params = {
                'purchase_price': purchase_price,
                'distributor_price_with_tax': distributor_price_with_tax,
                'distributor_price_without_tax': distributor_price_without_tax,
                'mrp': mrp,
                'bussiness_volume': bussiness_volume,
                'point_value': point_value,
                'tax_amount': tax_amount,
                'tax_percentage': tax_percentage,
                'inventory': inventry,
                'product': product,
                'title': 'Inventory Detail'
            }
            if request.POST['batch'] == 'no':
                return render(request, 'mlm_admin/no_batch_details-list.html', params)
            if request.POST['batch'] == 'yes':
                return render(request, 'mlm_admin/details-list.html', params)
    material = Material_center.objects.filter(company_depot='YES').exclude(delete=True)
    today = datetime.now().date()
    today = today.strftime("%Y-%m-%d")
    return render(request, 'mlm_admin/inventory_details.html',
                  {'material': material, 'today': today, 'title': 'Inventory Detail'})


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['inventory_management', ['1', '2', '3', '4']])
def distributor_inventory_details(request):
    print(request.method)
    if request.method == 'POST':
        stock_details = request.POST['stock_details']
        # type = request.POST['m_center']
        select_all = request.POST.getlist('select_all')
        purchase_price = request.POST.getlist('purchase_price')
        distributor_price_with_tax = request.POST.getlist('distributor_price_with_tax')
        distributor_price_without_tax = request.POST.getlist('distributor_price_without_tax')
        mrp = request.POST.getlist('mrp')
        bussiness_volume = request.POST.getlist('bussiness_volume')
        point_value = request.POST.getlist('point_value')
        tax_percentage = request.POST.getlist('tax_percentage')
        tax_amount = request.POST.getlist('tax_amount')
        # print('length of select all---->', len(select_all))
        # print('select_all--->', select_all, 'purchase_price--->', purchase_price, 'distributor_price_with_tax',
        #       distributor_price_with_tax
        #       , 'distributor_price_without_tax', distributor_price_without_tax, 'mrp', mrp, 'bussiness_volume',
        #       bussiness_volume, 'point_value', point_value
        #       , 'tax_percentage', tax_percentage, 'tax_amount', tax_amount)
        if len(select_all) == 1:
            purchase_price = True
            distributor_price_with_tax = True
            distributor_price_without_tax = True
            mrp = True
            bussiness_volume = True
            point_value = True
            tax_amount = True
            tax_percentage = True
        else:
            if len(purchase_price) == 1:
                purchase_price = True
            if len(distributor_price_with_tax) == 1:
                distributor_price_with_tax = True
            if len(distributor_price_without_tax) == 1:
                distributor_price_without_tax = True
            if len(mrp) == 1:
                mrp = True
            if len(bussiness_volume) == 1:
                bussiness_volume = True
            if len(point_value) == 1:
                point_value = True
            if len(tax_amount) == 1:
                tax_amount = True
            if len(tax_percentage) == 1:
                tax_percentage = True

        if stock_details == 'balance':
            blance_date = request.POST['blance_date']
            o_material_center = request.POST['material_center']
            material_pk = o_material_center
            inventry = Distributor_Inventry.objects.filter(created_on=blance_date, material_center__pk=material_pk)
            product = []

            for i in inventry:
                if i.product not in product:
                    for_quantity = inventry.filter(product=i.product)
                    qty = 0
                    batch_quantity = 0
                    for k in for_quantity:
                        qty = qty + k.current_quantity
                        i.product.quantity = qty
                        if k.batch.quantity > batch_quantity:
                            batch_quantity = k.batch.quantity
                            i.product.mrp = k.batch.mrp
                    product.append(i.product)
            params = {
                'purchase_price': purchase_price,
                'distributor_price_with_tax': distributor_price_with_tax,
                'distributor_price_without_tax': distributor_price_without_tax,
                'mrp': mrp,
                'bussiness_volume': bussiness_volume,
                'point_value': point_value,
                'tax_percentage': tax_percentage,
                'inventory': inventry,
                'product': product,
                'title': 'Inventory Details'
            }
            if request.POST['batch'] == 'yes':
                return render(request, 'mlm_admin/blanceDetails-list.html', params)
            if request.POST['batch'] == 'no':
                return render(request, 'mlm_admin/No_blanceDetails-list.html', params)
        elif stock_details == 'detail':
            detail_end_date = request.POST['detail_end_date']
            detail_start_date = request.POST['detail_start_date']
            # print('stock_details--->', stock_details)
            o_material_center = request.POST['material_center']
            material_pk = o_material_center
            inventry_data = Distributor_Inventry.objects.filter(created_on__range=[detail_start_date, detail_end_date],
                                                                material_center__pk=material_pk)
            inventry = []
            for i in inventry_data:
                if len(inventry) == 0:
                    inventry.append(i)
                else:
                    check = 0
                    for count, j in enumerate(inventry):
                        if i.material_center == j.material_center and i.batch == j.batch:
                            if i not in inventry:
                                if int(j.purchase_price) == 0:
                                    j.purchase_price = i.purchase_price
                                j.current_quantity = i.current_quantity
                                j.quantity_in = int(i.quantity_in) + int(j.quantity_in)
                                j.quantity_out = int(i.quantity_out) + int(j.quantity_out)
                                check = check + 1
                        elif (len(inventry) == (count + 1) and check == 0):
                            inventry.append(i)
            # print('here this-------------------------------',inventry)
            # Purchase.objects.filter()
            product = Product.objects.all().exclude(delete=True)
            product = []
            # print('inventry--->',inventry)
            # if request.POST['batch'] == 'yes':
            for i in inventry:
                if i.product not in product:
                    current_qty = 0
                    batch_quantity = 0
                    opening_qty = 0
                    in_qty = 0
                    out_qty = 0
                    for k in inventry:
                        if k.product == i.product:
                            current_qty = current_qty + k.current_quantity
                            # opening_qty = opening_qty + k.opening_quantity
                            opening_qty = k.opening_quantity
                            in_qty = in_qty + k.quantity_in
                            out_qty = out_qty + k.quantity_out
                            if k.batch.quantity > batch_quantity:
                                batch_quantity = k.batch.quantity
                                i.product.mrp = k.batch.mrp
                    # print('current_qty----->',current_qty,'----------------product------------>',i.product)
                    i.product.quantity = current_qty
                    i.product.minimum_purchase_quantity = opening_qty
                    i.product.item_package_quantity = in_qty
                    i.product.weight = out_qty
                    product.append(i.product)
            # print(product,'here we are geting the name  of the product')
            params = {
                'purchase_price': purchase_price,
                'distributor_price_with_tax': distributor_price_with_tax,
                'distributor_price_without_tax': distributor_price_without_tax,
                'mrp': mrp,
                'bussiness_volume': bussiness_volume,
                'point_value': point_value,
                'tax_amount': tax_amount,
                'tax_percentage': tax_percentage,
                'inventory': inventry,
                'product': product,
                'title': 'Inventory Detail'
            }
            if request.POST['batch'] == 'no':
                return render(request, 'mlm_admin/no_batch_details-list.html', params)
            if request.POST['batch'] == 'yes':
                return render(request, 'mlm_admin/details-list.html', params)
    material = Material_center.objects.filter(company_depot='NO').exclude(delete=True)
    # material = Material_center.objects.filter(company_depot='YES').exclude(delete=True)
    today = datetime.now().date()
    today = today.strftime("%Y-%m-%d")
    return render(request, 'mlm_admin/distributor_inventory_details.html',
                  {'material': material, 'today': today, 'title': 'Inventory Detail'})


def blanceDetails(request):
    return render(request, 'mlm_admin/blanceDetails-list.html')


def details(request):
    return render(request, 'mlm_admin/Details-list.html')


# code end here
def inventory(request):
    data = Batch.objects.get(pk=3)
    # data= Purchase.objects.all()
    # data=Purchase.objects.get(pk=17)

    print(data.inventry_set.filter(purchase_price=200.0))
    # print(i)

    data = Material_center.objects.all().values_list('pk')
    print('all material center', data)
    data = [1, 2, 3, 4, 5, 6, 13]
    inventry = Inventry.objects.filter(material_center__in=data)
    print('this is inventry', inventry)
    # for i in one_objs:
    # print(data)
    # print(k)
    # print(one_objs)
    #     print('data',i.items,'data_product',i.material_name,'data.part_name',i.party_name,'data.grand_total',i.grand_total)
    return render(request, 'mlm_admin/inventorytest-list.html', {'data': data})


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['user_management', ['2']])
def registration_edit_user(request, myid):
    user = get_object_or_404(User, pk=myid)
    profile = get_object_or_404(Profile, user=user)
    check_user_qs = get_object_or_404(User_Check, user_check=user)

    try:
        kyc_qs = get_object_or_404(Kyc, kyc_user=user)
        pan_file = kyc_qs.pan_file
        id_proof_file = kyc_qs.id_proof_file
        address_proof_file = kyc_qs.address_proof_file
        form = KycForm(instance=kyc_qs)
    except:
        kyc_qs = False
        pan_file = False
        id_proof_file = False
        address_proof_file = False
        form = KycForm()

    try:
        bank_qs = get_object_or_404(BankAccountDetails, bank_account_user=user)
        cheque_photo = bank_qs.cheque_photo
        bank_form = BankAccountDetailsForm_for_user(instance=bank_qs)
    except:
        bank_qs = False
        cheque_photo = False
        bank_form = BankAccountDetailsForm_for_user()
    # <-----------------------------------------------------------------for changing data in reqistration field ----------------------------------->   if request.method == 'POST':
    if request.method == 'POST':
        form = CheckForm(instance=check_user_qs, data=request.POST, )
        if form.is_valid():
            form.save()
            profile_active = request.POST.get('check_profile_active')
            if profile_active == None:
                Profile.objects.filter(user=check_user_qs.user_check).update(status='InActive')
            else:
                Profile.objects.filter(user=check_user_qs.user_check).update(status='Active')
        else:
            return HttpResponse(form.errors)
        profile_firstname = request.POST['firstname']
        profile_lastname = request.POST['lastname']
        profile_birthday = request.POST['birthday']
        profile_co_applicant = request.POST['co_applicant']
        profile_gender = request.POST['gender']
        shipping_house = request.POST['house']
        shipping_street = request.POST['street']
        shipping_address2 = request.POST['address2']
        shipping_landmark = request.POST['landmark']
        shipping_city = request.POST['city']
        shipping_state = request.POST['state']
        own_state = request.POST['own_state']
        shipping_pincode = request.POST['pincode']
        shipping_phone = request.POST['phone']
        shipping_altphone = request.POST['altphone']
        profile_update = Profile.objects.filter(pk=profile.pk).update(first_name=profile_firstname,
                                                                      last_name=profile_lastname,
                                                                      date_of_birth=profile_birthday,
                                                                      co_applicant=profile_co_applicant,
                                                                      gender=profile_gender, state=own_state)
        profile = Profile.objects.get(pk=profile.pk)
        user = profile.user

        try:
            address_update = Address.objects.filter(pk=profile.shipping_address.pk).update(house_number=shipping_house,
                                                                                           address_line=shipping_address2,
                                                                                           Landmark=shipping_landmark,
                                                                                           city=shipping_city,
                                                                                           street=shipping_street,
                                                                                           pin=shipping_pincode,
                                                                                           mobile=shipping_phone,
                                                                                           alternate_mobile=shipping_altphone,
                                                                                           state_id=shipping_state)
            Address.objects.filter(pk=profile.shipping_address.pk).first().save()  # to trigger signals
        except AttributeError:
            # address_update = Address.objects.update(house_number = shipping_house,address_line = shipping_address2,Landmark = shipping_landmark,
            #                                                             city = shipping_city,street = shipping_street,pin = shipping_pincode,mobile = shipping_phone,
            #                                                             alternate_mobile = shipping_altphone,state_id = shipping_state)
            address_update = Address.objects.filter(user=user).update(house_number=shipping_house,
                                                                      address_line=shipping_address2,
                                                                      Landmark=shipping_landmark,
                                                                      city=shipping_city, street=shipping_street,
                                                                      pin=shipping_pincode, mobile=shipping_phone,
                                                                      alternate_mobile=shipping_altphone,
                                                                      state_id=shipping_state, address_type='B')
            pass

        position = request.POST.get('position')
        ReferralCode.objects.filter(user_id=user).update(position=position)
        if kyc_qs:
            kyc_form = KycForm(instance=kyc_qs, data=request.POST, files=(request.FILES or None), )
            if kyc_form.is_valid():
                kyc_form.save()
            else:
                return HttpResponse('<h1>' + str(kyc_form.errors) + '</h1>')
        else:
            form = KycForm(request.POST, request.FILES)
            if form.is_valid():
                dataform = form.save(commit=False)
                dataform.kyc_user = user
                dataform.save()
        if bank_qs:
            bank_form = BankAccountDetailsForm_for_user(instance=bank_qs, data=request.POST,
                                                        files=(request.FILES or None), )
            bank_form.save()
        else:
            bank_form = BankAccountDetailsForm_for_user(data=request.POST, files=(request.FILES or None), )
            if bank_form.is_valid():
                databankform = bank_form.save(commit=False)
                databankform.bank_account_user = user
                databankform.save()
            else:
                return HttpResponse('<h1>' + bank_form.errors + '</h1>')

        # return redirect('referral_list')
    # <-----------------------------------------------------------------for changing data in reqistration field ----------------------------------->

    registration_form = accounts.views.check_registration_form_fn(check_user_qs)

    try:
        kyc_qs = get_object_or_404(Kyc, kyc_user=user)
        pan_file = kyc_qs.pan_file
        id_proof_file = kyc_qs.id_proof_file
        address_proof_file = kyc_qs.address_proof_file
        form = KycForm(instance=kyc_qs)
    except:
        kyc_qs = False
        pan_file = False
        id_proof_file = False
        address_proof_file = False
        form = KycForm()

    try:
        bank_qs = get_object_or_404(BankAccountDetails, bank_account_user=user)
        cheque_photo = bank_qs.cheque_photo
        bank_form = BankAccountDetailsForm_for_user(instance=bank_qs)
    except:
        bank_qs = False
        cheque_photo = False
        bank_form = BankAccountDetailsForm_for_user()
    check_form = CheckForm(instance=check_user_qs)
    # data = User_Check(user_check = user,check_first_name = check)
    # data.save()
    referal_code = ReferralCode.objects.filter(user_id=user)[0]
    address_qs = Address.objects.filter(user=user, address_type='B')[0]
    state = AdminState.objects.filter()
    profile = Profile.objects.filter(user=user)[0]
    if profile.first_name == None:
        profile.first_name = ''
    if profile.last_name == None:
        profile.last_name = ''
    name = profile.first_name.title() + '  ' + profile.last_name.title()
    context = {
        'profile': profile,
        'referal_code': referal_code,
        'address': address_qs,
        'form': form,
        'bank_form': bank_form,
        'check_form': check_form,
        'registration_form': registration_form,
        'cheque_photo': cheque_photo,
        'address_proof_file': address_proof_file,
        'id_proof_file': id_proof_file,
        'pan_file': pan_file,
        'title': name,
        'state': state,
    }
    return render(request, 'mlm_admin/registration_user.html', context)


def loginAdmin(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        email = request.POST.get('username')
        try:
            referal = ReferralCode.objects.get(referral_code=email)
            email = referal.user_id.username
        except:
            pass
        try:
            prof = Profile.objects.get(phone_number=email)
            email = prof.user.username
        except:
            pass
        email = email.lower()
        password = request.POST.get('password')
        print('password', password)
        user = authenticate(request, username=email, password=password)
        print('user', user)
        valuenext = request.POST.get('next')
        print('valuenext', valuenext)
        # here we are writing code for recaptchar
        clientkey = request.POST['g-recaptcha-response']
        serverkey = '6LeVCKgaAAAAADsn51OcTxu6-wZ_THxWCT7b_GoA'
        captchaData = {
            'secret': serverkey,
            'response': clientkey
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=captchaData)
        response = json.loads(r.text)
        verify = response['success']
        print('this is verified', verify)
        if verify:
            # here we are writing code for recaptchar
            if user is not None and valuenext == '':
                login(request, user)
                if request.session['cart_id']:
                    cart_id = request.session['cart_id']
                    cart_session_item = CartItem.objects.filter(cart_id=cart_id)
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
                else:
                    cart_id = CartItem.objects.filter(user=request.user).first()
                    for i in cart_id:
                        request.session['i.cart_id'] = i.cart_id
                context = {'valuenext': valuenext}
                print(request.session['cart_id'])
                if request.user.profile.mlm_admin:
                    messages.success(
                        request, "Welcome! You've been signed in"
                    )
                else:
                    messages.warning(
                        request, "You are not Mlm Admin"
                    )
                return redirect('mlm_admin')
            elif user is not None and valuenext != '':
                login(request, user)
                if request.session['cart_id']:
                    cart_id = request.session['cart_id']
                    cart_session_item = CartItem.objects.filter(cart_id=cart_id)
                    # <--!-------------------------------------------nipur code start 9-02-2021--------------------------------------------------------!-->
                    if len(cart_session_item) > 0:
                        # < ------------------------------------------ this is my new code 20 feb -------------------------------->

                        cart_user_item = CartItem.objects.filter(user=user).first()
                        if cart_user_item != None:
                            user_database_cart_id = cart_user_item.cart_id
                        cart_user_item_delete = CartItem.objects.filter(user=user).delete()
                        CartItem.objects.filter(cart_id=cart_id).update(user=user)

                        if cart_user_item != None:
                            CartItem.objects.filter(user=user).update(cart_id=user_database_cart_id)
                            request.session['cart_id'] = user_database_cart_id
                        # < ------------------------------------------ this is my new code 20 feb -------------------------------->
                        # cart_user_item = CartItem.objects.filter(user = user).delete()
                        # CartItem.objects.filter(cart_id = cart_id).update(user=user)
                    else:
                        cart_user_item = CartItem.objects.filter(user=user).first()
                        if cart_user_item != None:
                            request.session['cart_id'] = cart_user_item.cart_id

                        # for i in cart_user_item:
                        #     request.session['cart_id'] = i.cart_id
                # <--!-------------------------------------------nipur code end 9-02-2021--------------------------------------------------------!-->
                # #
                #                 cart_session_item_list=[]
                #                 for i in cart_session_item:
                #                     cart_session_item_list.append(i.product)
                #                 cart_user_item = CartItem.objects.filter(user = user)
                #                 for i in cart_user_item:
                #                     log_cart_id = i.cart_id
                #                     if i.product in cart_session_item_list:
                #                         i.delete()
                #                 CartItem.objects.filter(cart_id = cart_id).update(user=user)
                #                 try:
                #                     cart_id = log_cart_id
                #                     request.session['cart_id'] = cart_id
                #                     CartItem.objects.filter(user=user).update(cart_id = cart_id)
                #                 except:
                #                     request.session['cart_id'] = cart_id
                #                     CartItem.objects.filter(user=user).update(cart_id = cart_id)
                else:
                    cart_id = CartItem.objects.filter(user=request.user).first()
                    for i in cart_id:
                        request.session['i.cart_id'] = i.cart_id

                # nipur code end
                messages.success(request, "You have successfully logged in")
                valuenext = valuenext.strip('/')
                context = {'valuenext': valuenext}
                return redirect('checkout')
                # return redirect(valuenext)
            else:
                messages.warning(request, "Wrong Credentials")
                return redirect('mlm_admin_login')
        else:
            pass
    #     nipur code end

    else:
        # return render(request, 'base.html', {})
        # nipur code start
        return render(request, 'mlm_admin/login.html')


def validate_ref(request):
    referall_code = request.GET.get('referall_code', None)
    company_depot = request.GET.get('company_depot', 'NO')
    advisory_owned = request.GET.get('advisory_owned', 'NO')
    print('here we are geting the value of referall code', referall_code)
    try:
        queryset = ReferralCode.objects.get(user_id_id=referall_code)
        try:
            material_Center = Material_center.objects.get(advisor_registration_number_id=referall_code,
                                                          advisory_owned=advisory_owned, company_depot=company_depot)
            ref_list = ''
            code = 404
        except:
            first_name = queryset.user_id.profile.first_name
            last_name = queryset.user_id.profile.last_name
            if first_name == None:
                first_name = ''
            if last_name == None:
                last_name = ''
            ref_list = str(first_name) + ' ' + str(last_name)
            code = 200
    except ObjectDoesNotExist:
        ref_list = ''
        code = 404
    #
    data = {
        'refer_by': ref_list,
        'code': code
    }
    return JsonResponse(data)


# def rebuilding_cron(request):
#     from datetime import date,timedelta,datetime
#     today = date.today()
#     if request.method == 'POST':
#         date = request.POST.get('rebuildingdate',None)
#         if date != None:
#             date = datetime.strptime(date, '%Y-%m-%d').date()
#             select_date_inventry = Inventry.objects.filter(created_on = date)
#             previous = date - timedelta(days = 1)
#             previous_inventry = Inventry.objects.filter(created_on = previous)
#             for i in select_date_inventry:
#                 check = previous_inventry.filter(product = i.product,batch = i.batch,material_center = i.material_center)
#                 if check:
#                     quantity_in = 0
#                     quantity_out = 0
#                     opening_quantity = 0
#                     sales = Sale.objects.filter(material_center_from = i.material_center,created_on = date,sale_itemdetails__item = i.product,sale_itemdetails__batch = i.batch)
#                     print('sale is getting here-->',sales)
#                     for sale in sales:
#                         sale_item = sale.sale_itemdetails_set.filter(item = i.item,batch = i.batch)
#                         for s in sale_item:
#                             quantity_out += int(s.quantity)
#                     purchases = Purchase.objects.filter(material_name = i.material_center,created_on = date,item_details__item = i.product,item_details__batch = i.batch)
#                     print(purchases,'<here we are geting are purchases>')
#                     for purchase in purchases:
#                         purchase_item = purchase.item_details_set.filter(item = i.product,batch = i.batch)
#                         for pur in purchase_item:
#                             quantity_in += int(pur.quantity)
#                     current_quantity = int(i.opening_quantity) - quantity_out + quantity_in
#                     pre_inventry = previous_inventry.filter(product = i.product,batch = i.batch,material_center = i.material_center)
#                     for pre in pre_inventry:
#                         opening_quantity = pre.current_quantity
#                         print('pre current quantity-->',opening_quantity)
#                     print(len(pre_inventry),'<------here we are geting the pre_inventry>',pre_inventry)
#                     Inventry.objects.filter(pk = i.pk).update(product = i.product,batch = i.batch,material_center = i.material_center,quantity_in = quantity_in,quantity_out =quantity_out,
#                             current_quantity = current_quantity,opening_quantity = opening_quantity)
#                 else:
#                     quantity_in = 0
#                     quantity_out = 0
#                     sales = Sale.objects.filter(material_center_from = i.material_center,created_on = date,sale_itemdetails__item = i.product,sale_itemdetails__batch = i.batch)
#                     print('sale is getting here-->',sales)
#                     for sale in sales:
#                         sale_item = sale.sale_itemdetails_set.filter(item = i.item,batch = i.batch)
#                         for s in sale_item:
#                             quantity_out += int(s.quantity)
#                     purchases = Purchase.objects.filter(material_name = i.material_center,created_on = date,item_details__item = i.product,item_details__batch = i.batch)
#                     print(purchases,'<here we are geting are purchases>')
#                     for purchase in purchases:
#                         purchase_item = purchase.item_details_set.filter(item = i.product,batch = i.batch)
#                         for pur in purchase_item:
#                             quantity_in += int(pur.quantity)
#                     current_quantity = int(i.opening_quantity) - quantity_out + quantity_in
#                     Inventry.objects.filter(pk = i.pk).update(product = i.product,batch = i.batch,material_center = i.material_center,quantity_in = quantity_in,quantity_out =quantity_out,
#                              opening_quantity = 0,current_quantity = current_quantity)
#             print('data--->',previous_inventry.count())
#         else:
#             pass
#     return render(request,'mlm_admin/rebuildingCron.html',{'today':today})

# class Add_shiping_config(generic.CreateView):
#     model = Ship_Charge
#     fields = "__all__"
#     template_name ="mlm_admin/ship_charge.html"
#     success_url = reverse_lazy('home')
@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['manual_configure', ['1', '2']])
def Add_shiping_config(request):
    shiping_qs = Ship_Charge.objects.last()
    if request.method == 'POST':
        form = ShipCharge(instance=shiping_qs, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('mlm_admin_shiping_charge')
        else:
            print(form.errors)
            return HttpResponse('<h1>' + str(form.erros) + '</h1>')
    form = ShipCharge(instance=shiping_qs)
    return render(request, 'mlm_admin/ship_charge.html', {'form': form})


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['sale_management', ['1', '2']])
def pending_sale(request):
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        # d=q.date()
        # print(d,'llllllllllllllllllllllllllllll')
        sales = Sale.objects.filter(
            Q(created_on__icontains=q) | Q(party_name__icontains=q) | Q(material_center_to__mc_name__icontains=q) | Q(
                material_center_from__mc_name__icontains=q) | Q(grand_total__contains=q), delete=False,
            accept=False).order_by('id')
    else:
        q = ''
        sales = Sale.objects.filter(delete=False, accept=False).order_by('id')
    paginator = Paginator(sales, 10)
    print(paginator, 'paginator')
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'mlm_admin/pending_sale.html', {'sales': page_obj, 'title': 'Pending sale', 'q': q})


@user_passes_test(is_super_admin, login_url='mlm_admin_login')
def add_user_permission(request):
    if request.method == 'POST':
        category_management = request.POST.getlist('category_management')
        product_management = request.POST.getlist('product_management')
        order_management = request.POST.getlist('order_management')
        batch_management = request.POST.getlist('batch_management')
        mc_management = request.POST.getlist('mc_management')
        user_management = request.POST.getlist('user_management')
        purchase_management = request.POST.getlist('purchase_management')
        sale_management = request.POST.getlist('sale_management')
        inventory_management = request.POST.getlist('inventory_management')
        cron_configuration = request.POST.getlist('cron_configuration')
        manual_configuration = request.POST.getlist('manual_configuration')
        crm_management = request.POST.getlist('crm_management')
        manual_verification = request.POST.getlist('manual_verification')
        wallet_configuration = request.POST.getlist('wallet_configuration')
        mis_report = request.POST.getlist('mis_report')
        pincode = request.POST.getlist('pincode')
        calculations = request.POST.getlist('calculations')
        realtime = request.POST.getlist('realtime')
        user_id = request.POST.get('user')
        permission = menu_permission(user_id=user_id, category_management=category_management,
                                     product_management=product_management,
                                     order_management=order_management,
                                     batch_management=batch_management,
                                     mc_management=mc_management,
                                     user_management=user_management,
                                     purchase_management=purchase_management,
                                     sale_management=sale_management,
                                     inventory_management=inventory_management,
                                     cron_management=cron_configuration,
                                     manual_configure=manual_configuration,
                                     crm_management=crm_management,
                                     manual_verification=manual_verification,
                                     wallet_configuration=wallet_configuration,
                                     mis_report=mis_report,
                                     pincode=pincode,
                                     calculations=calculations,
                                     realtime=realtime,
                                     )
        permission.save()
        messages.success(request, 'Permission Add Successfully')
        return redirect('mlm_admin_user_permission_list')
    user = User.objects.filter(profile__mlm_admin=True).exclude(menu_permission__menu_permission=True)
    if len(user) > 0:
        return render(request, 'mlm_admin/add_user_permission.html', {'title': 'add_user_permission', 'data': user})
    else:
        return HttpResponse('<h1>Here is no mlm admin  to give permission</h1>')


def export_excel(request, myid):
    response = HttpResponse(content_type='application/ms-excel')
    response['content-Disposition'] = 'attachment; filename = Expenses' + str(datetime.now()) + '.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Expenses')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['material_center_to', 'material_center_from', 'advisor_distributor_name', 'party_name',
               'grand_total', 'item', 'batch', 'quantity', 'total_amount', 'cgst', 'sgst', 'igst', 'vat',
               'distributor_price']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()
    rows = Sale_itemDetails.objects.filter(sale__pk=myid).values_list('sale__material_center_to__mc_name',
                                                                      'sale__material_center_from__mc_name',
                                                                      'sale__advisor_distributor_name__email',
                                                                      'sale__party_name', 'sale__grand_total',
                                                                      'item__product_name',
                                                                      'batch__batch_name', 'quantity',
                                                                      'distributor_price', 'cgst', 'sgst', 'igst',
                                                                      'vat', 'total_amount')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)
    wb.save(response)
    return response


from django.template.loader import get_template


def sendemail(profile, final):
    Body = '''<h1>here we are geting mail having h1 tag</h1>'''
    email = EmailMessage('Subject', Body, )
    email.send()
    ctx = {
        'profile': profile,
        'finall_ref': final
    }
    message = get_template('mlm_admin/mail.html').render(ctx)
    msg = EmailMessage(
        'Subject',
        message,
        to=[profile.email]
    )
    msg.content_subtype = "html"  # Main content is now text/html
    msg.send()
    return True


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['user_management', ['1', '2', '3', '4']])
def distributor_list(request):
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        # d=q.date()
        # print(d,'llllllllllllllllllllllllllllll')
        data = Profile.objects.filter(
            Q(user__email__icontains=q) | Q(user__referralcode__referral_code__icontains=q) | Q(
                phone_number__icontains=q) | Q(first_name__contains=q), distributor=False).order_by('id')
    else:
        q = ''
        data = Profile.objects.filter(distributor=False)
    paginator = Paginator(data, 10)
    print(paginator, 'paginator')
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'mlm_admin/distributor-list.html', {'data': page_obj, 'title': 'Distributor List', 'q': q})


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['user_management', ['1', '2', '3', '4']])
def cnf_list(request):
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        # d=q.date()
        # print(d,'llllllllllllllllllllllllllllll')
        data = Profile.objects.filter(
            Q(user__email__icontains=q) | Q(user__referralcode__referral_code__icontains=q) | Q(
                phone_number__icontains=q) | Q(first_name__contains=q), c_and_f_admin=False).order_by('id')
    else:
        q = ''
        data = Profile.objects.filter(c_and_f_admin=False)
    paginator = Paginator(data, 10)
    print(paginator, 'paginator')
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'mlm_admin/c_and_f/cnf-list.html', {'data': page_obj, 'title': 'Distributor List', 'q': q})


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['user_management', ['1', '2', '3', '4']])
def everdistributor_list(request):
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        # d=q.date()
        # print(d,'llllllllllllllllllllllllllllll')
        data = Profile.objects.filter(
            Q(user__email__icontains=q) | Q(user__referralcode__referral_code__icontains=q) | Q(
                phone_number__icontains=q) | Q(first_name__contains=q), ever_distributor=True,
            distributor=False).order_by('id')
    else:
        q = ''
        data = Profile.objects.filter(ever_distributor=True, distributor=False)
    paginator = Paginator(data, 10)
    print(paginator, 'paginator')
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'mlm_admin/ever-distributor-list.html',
                  {'data': page_obj, 'title': 'Ever Distributor List', 'q': q})


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['user_management', ['1', '2', '3', '4']])
def evercnf_list(request):
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        # d=q.date()
        # print(d,'llllllllllllllllllllllllllllll')
        data = Profile.objects.filter(
            Q(user__email__icontains=q) | Q(user__referralcode__referral_code__icontains=q) | Q(
                phone_number__icontains=q) | Q(first_name__contains=q), ever_c_and_f_admin=True,
            c_and_f_admin=False).order_by('id')
    else:
        q = ''
        data = Profile.objects.filter(ever_c_and_f_admin=True, c_and_f_admin=False)
    paginator = Paginator(data, 10)
    print(paginator, 'paginator')
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'mlm_admin/c_and_f/ever-cnf-list.html',
                  {'data': page_obj, 'title': 'Ever Distributor List', 'q': q})


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['user_management', ['1', '2']])
def make_distributor(request, myid):
    data = Profile.objects.filter(pk=myid).update(distributor=True, ever_distributor=True)
    return redirect('mlm_admin_distributor_list')


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['user_management', ['1', '2']])
def remove_distributor(request, myid):
    data = Profile.objects.filter(pk=myid).update(distributor=False)
    return redirect('mlm_admin_current_distributor')


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['user_management', ['1', '2']])
def make_cnf(request, myid):
    data = Profile.objects.filter(pk=myid).update(c_and_f_admin=True, ever_c_and_f_admin=True)
    return redirect('mlm_admin_cnf_list')


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['user_management', ['1', '2']])
def remove_cnf(request, myid):
    data = Profile.objects.filter(pk=myid).update(c_and_f_admin=False)
    return redirect('mlm_admin_current_cnf')


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['user_management', ['1', '2', '3', '4']])
def current_distributor(request):
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        # d=q.date()
        # print(d,'llllllllllllllllllllllllllllll')
        data = Profile.objects.filter(
            Q(user__email__icontains=q) | Q(user__referralcode__referral_code__icontains=q) | Q(
                phone_number__icontains=q) | Q(first_name__contains=q), distributor=True).order_by('id')
    else:
        q = ''
        data = Profile.objects.filter(distributor=True)
    paginator = Paginator(data, 10)
    print(paginator, 'paginator')
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'mlm_admin/current_distributor-list.html',
                  {'data': page_obj, 'title': 'Current Distributor List', 'q': q})



@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['user_management', ['1', '2', '3', '4']])
def current_distributor_cri(request):
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        data = consistent_retailers_income.objects.filter(
            Q(user__email__icontains=q) | Q(
                user__referralcode__referral_code__icontains=q) | Q(
                user__profile__phone_number__icontains=q) | Q(
                user__profile__first_name__contains=q), cri_earned__gt=0, input_date__month=1,
                input_date__year=year, ).order_by('cri_balance')
    else:
        q = ''
        data = consistent_retailers_income.objects.filter(cri_earned__gt=0,
                                                          input_date__month=1,
                                                          input_date__year=last_year,)
    paginator = Paginator(data, 10)
    print(paginator, 'paginator')
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'mlm_admin/current_distributor_cri.html',
                  {'data': page_obj, 'title': 'User-Wise Consistency', 'q': q})


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['user_management', ['1', '2', '3', '4']])
def current_cnf(request):
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        # d=q.date()
        # print(d,'llllllllllllllllllllllllllllll')
        data = Profile.objects.filter(
            Q(user__email__icontains=q) | Q(user__referralcode__referral_code__icontains=q) | Q(
                phone_number__icontains=q) | Q(first_name__contains=q), c_and_f_admin=True).order_by('id')
    else:
        q = ''
        data = Profile.objects.filter(c_and_f_admin=True)
    paginator = Paginator(data, 10)
    print(paginator, 'paginator')
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'mlm_admin/c_and_f/current_cnf-list.html',
                  {'data': page_obj, 'title': 'Current Distributor List', 'q': q})


@user_passes_test(is_super_admin, login_url='mlm_admin_login')
def user_permission_list(request):
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        data = menu_permission.objects.filter(Q(user__email__icontains=q), user__profile__mlm_admin=True,
                                              menu_permission=True).order_by('id')
    else:
        q = ''
        data = menu_permission.objects.filter(user__profile__mlm_admin=True, menu_permission=True)
    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'mlm_admin/user_permission-list.html',
                  {'data': page_obj, 'title': 'User Permission List', 'q': q})


@user_passes_test(is_super_admin, login_url='mlm_admin_login')
def view_user_permission(request, myid):
    data = menu_permission.objects.get(pk=myid)
    return render(request, 'mlm_admin/view_user_permission.html', {'title': 'View Permission', 'data': data})


@user_passes_test(is_super_admin, login_url='mlm_admin_login')
def edit_user_permission(request, myid):
    if request.method == 'POST':
        category_management = request.POST.getlist('category_management')
        product_management = request.POST.getlist('product_management')
        order_management = request.POST.getlist('order_management')
        batch_management = request.POST.getlist('batch_management')
        mc_management = request.POST.getlist('mc_management')
        user_management = request.POST.getlist('user_management')
        purchase_management = request.POST.getlist('purchase_management')
        sale_management = request.POST.getlist('sale_management')
        inventory_management = request.POST.getlist('inventory_management')
        cron_configuration = request.POST.getlist('cron_configuration')
        manual_configuration = request.POST.getlist('manual_configuration')
        crm_management = request.POST.getlist('crm_management')
        manual_verification = request.POST.getlist('manual_verification')
        wallet_configuration = request.POST.getlist('wallet_configuration')
        mis_report = request.POST.getlist('mis_report')
        pincode = request.POST.getlist('pincode')
        calculations = request.POST.getlist('calculations')
        realtime = request.POST.getlist('realtime')
        permission = menu_permission.objects.filter(pk=myid).update(category_management=category_management,
                                                                    product_management=product_management,
                                                                    order_management=order_management,
                                                                    batch_management=batch_management,
                                                                    mc_management=mc_management,
                                                                    user_management=user_management,
                                                                    purchase_management=purchase_management,
                                                                    sale_management=sale_management,
                                                                    inventory_management=inventory_management,
                                                                    cron_management=cron_configuration,
                                                                    manual_configure=manual_configuration,
                                                                    crm_management=crm_management,
                                                                    manual_verification=manual_verification,
                                                                    wallet_configuration=wallet_configuration,
                                                                    mis_report=mis_report,
                                                                    pincode=pincode,
                                                                    calculations=calculations,
                                                                    realtime=realtime,
                                                                    )
        messages.success(request, 'Permission Updated Successfully')
        return redirect('mlm_admin_user_permission_list')
    data = menu_permission.objects.get(pk=myid)
    return render(request, 'mlm_admin/edit_user_permission.html', {'title': 'Edit Permission', 'data': data})


@csrf_exempt
def ajax_material_center(request):
    if request.method == 'POST':
        myid = request.POST.get('material_center_pk', None)
        company_depot = request.POST.get('company_depot', 'NO')
        advisory_owned = request.POST.get('advisory_owned', 'NO')
        material = Material_center.objects.get(advisor_registration_number_id=myid, company_depot=company_depot,
                                               advisory_owned=advisory_owned)
        print(material.pk, '<-------------------geting the data of material center')
        data = {
            'material': material.mc_name,
            'material_id': material.pk,
        }
        return JsonResponse(data)


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['sale_management', ['1', '2', '3', '4']])
def sale_downlaod(request):
    if request.method == 'POST':
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        response = HttpResponse(content_type='application/ms-excel')
        response['content-Disposition'] = 'attachment; filename = Sale' + str(datetime.now()) + '.xls'
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Expenses')
        row_num = 0
        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        columns = ['Bill Number', 'material_center_to', 'material_center_from', 'advisor_distributor_name',
                   'party_name',
                   'grand_total', 'Billing Date', 'Created On', 'Narration', 'Product ID', 'item', 'Category',
                   'Variant', 'DV', 'BV', 'PV', 'batch', 'Batch Manufacture Date',
                   'Batch date_of_expiry', 'quantity', 'distributor_price', 'cgst', 'sgst', 'igst', 'vat',
                   'total_amount', 'Sale Type']
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        font_style = xlwt.XFStyle()
        # print(to_date)
        # print(from_date)
        rows = Sale_itemDetails.objects.filter(sale__created_on__gte=from_date, sale__created_on__lte=to_date,
                                               sale__delete=False,).values_list('sale__pk',
                                                                               'sale__material_center_to__mc_name',
                                                                               'sale__material_center_from__mc_name',
                                                                               'sale__advisor_distributor_name__email',
                                                                               'sale__party_name', 'sale__grand_total',
                                                                               'sale__date', 'sale__created_on',
                                                                               'sale__narration', 'item__pk',
                                                                               'item__product_name',
                                                                               'item__category__cat_name',
                                                                               'item__product_variant__variant_tag__product_name',
                                                                               'item__distributor_price',
                                                                               'item__business_value',
                                                                               'item__point_value',
                                                                               'batch__batch_name',
                                                                               'batch__date_of_manufacture',
                                                                               'batch__date_of_expiry', 'quantity',
                                                                               'distributor_price', 'cgst', 'sgst',
                                                                               'igst', 'vat', 'total_amount',
                                                                               'sale__sale_type')
        print(rows, 'here we are geting the data that is going to print in excel sheet')
        print(len(rows), 'here we are geting the length of data')
        for row in rows:
            row_num += 1
            counting_sale_type = 0
            for col_num in range(len(row)):
                colmn = str(row[col_num])
                counting_sale_type += 1
                if counting_sale_type == 27:
                    if colmn == '0':
                        colmn = 'With in State'
                    elif colmn == '1':
                        colmn = 'Inter State'
                ws.write(row_num, col_num, colmn, font_style)
        wb.save(response)
        return response
    return render(request, 'mlm_admin/download_sale.html')


from datetime import datetime


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['sale_management', ['1', '2', '3', '4']])
def order_downlaod(request):
    if request.method == 'POST':
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        today = datetime.now()
        if str(today.date()) == to_date:
            to_date = today

        response = HttpResponse(content_type='application/ms-excel')
        response['content-Disposition'] = 'attachment; filename = Sale' + str(datetime.now()) + '.xls'
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Expenses')
        row_num = 0
        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        columns = ['Order Number (No Use)', 'Material Center', 'Order ID',
                   'grand_total', 'Billing Date', 'Item Name', 'Name in Accounting Software', 'Category',
                   'Variant', 'batch', 'Batch Manufacture Date',
                   'Batch date_of_expiry', 'CGST', 'SGST', 'IGST', 'Price', 'Quantity', 'Total Price',
                   'Grand Total Amount', 'Order ID',
                   'First Name', 'Last Name', 'House Number', 'Address Line', 'Street',
                   'City', 'Landmark', 'State', 'PIN', 'Mobile',
                   'Loyalty','Partial Loyalty', 'CRI Consumed', 'PV', 'BV', 'Group Checkout', 'Group Main Order',
                   'Email',
                   ]
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        font_style = xlwt.XFStyle()
        # print(to_date)
        # print(from_date)
        stock_variance = ['stockvariance@auretics.com', 'loyalty@auretics.com', ]
        power_material_center = [3, 4, 6, ]
        rows = LineItem.objects.filter(order__date__gte=from_date,
                                       order__date__lte=to_date, order__delete=False,
                                       order__paid=True, ).exclude(order__status=8).exclude(
            order__email__in=stock_variance).exclude(order__material_center__id__in=power_material_center).values_list(
            'order__pk',
            'order__material_center__mc_name',
            'order__order_id1',
            'order__grand_total',
            'order__date',
            'product__product_name',
            'product__name_in_accounting_software',
            'product__category__cat_name',
            'product__product_variant__variant_tag__product_name',
            'batch__batch_name',
            'batch__date_of_manufacture',
            'batch__date_of_expiry',
            'cgst',
            'sgst',
            'igst',
            'price',
            'quantity',
            'price',
            'order__grand_total',
            'order__order_id1',
            'order__shipping_address__user__profile__first_name',
            'order__shipping_address__user__profile__last_name',
            'order__shipping_address__house_number',
            'order__shipping_address__address_line',
            'order__shipping_address__street',
            'order__shipping_address__city',
            'order__shipping_address__Landmark',
            'order__shipping_address__state__state_name',
            'order__shipping_address__pin',
            'order__shipping_address__mobile',
            'order__loyalty_order',
            'order__is_partial_loyalty_order',
            'order__consumed_cri',
            'order__pv',
            'order__bv',
            'order__group_checkout',
            'order__main_order',
            'order__email',
            )
        for row in rows:
            row_num += 1
            counting = 0
            price = 0
            quantity = 0
            for col_num in range(len(row) + 1):
                counting += 1
                if counting < 39:
                    colmn = str(row[col_num])
                if counting == 16:
                    price = float(colmn)
                if counting == 17:
                    quantity = int(colmn)
                if counting == 18:
                    colmn = price * quantity
                ws.write(row_num, col_num, colmn, font_style)
        wb.save(response)
        return response
    return render(request, 'mlm_admin/download_order.html')


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['purchase_management', ['1', '2', '3', '4']])
def purchase_downlaod(request):
    if request.method == 'POST':
        to_date = request.POST.get('to_date')
        from_date = request.POST.get('from_date')
        response = HttpResponse(content_type='application/ms-excel')
        response['content-Disposition'] = 'attachment; filename = Purchase' + str(datetime.now()) + '.xls'
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Expenses')
        row_num = 0
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        columns = ['material_name', 'party_name',
                   'grand_total', 'item', 'batch', 'quantity', 'price', 'cgst', 'sgst', 'igst', 'vat', 'total_amount']
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)
        font_style = xlwt.XFStyle()
        # print(to_date)
        # print(from_date)
        rows = item_details.objects.filter(purchase__created_on__gte=from_date, purchase__created_on__lte=to_date,
                                           purchase__delete=False).values_list('purchase__material_name__mc_name',
                                                                               'purchase__party_name',
                                                                               'purchase__grand_total',
                                                                               'item__product_name',
                                                                               'batch__batch_name', 'quantity',
                                                                               'price', 'cgst', 'sgst', 'igst', 'vat',
                                                                               'total_amount')
        print(rows, 'here we are geting the data that is going to print in excel sheet')
        print(len(rows), 'here we are geting the length of data')
        for row in rows:
            row_num += 1
            for col_num in range(len(row)):
                ws.write(row_num, col_num, str(row[col_num]), font_style)
        wb.save(response)
        return response
    return render(request, 'mlm_admin/download_purchase.html')


# <-----------------------------------------------------------------------------------------------------------------------testing rebuilding  code here start-->
def rebuilding_cron_fn(i, check, date, previous_inventry, today):
    quantity_in = 0
    quantity_out = 0
    opening_quantity = 0
    order_quantity_out = 0
    sales = Sale.objects.filter(
        material_center_from=i.material_center,
        created_on=date,
        sale_itemdetails__item=i.product,
        sale_itemdetails__batch=i.batch,
        delete=False,
    )
    # print('sale qty is getting here-->', sales)
    for sale in sales:
        sale_item = sale.sale_itemdetails_set.filter(item=i.product, batch=i.batch)
        for s in sale_item:
            quantity_out += int(s.quantity)
            # print(s.sale.pk)

    orders = Order.objects.filter(
        material_center=i.material_center,
        # date__contains= date,
        date__day=date.day,
        date__month=date.month,
        date__year=date.year,
        # date= "2022-01-29 18:29:26.151078+00",
        lineitem__batch=i.batch,
        lineitem__product=i.product,
        paid=True,
        delete=False,
    ).exclude(status=8)

    for order in orders:
        order_items = order.lineitem_set.filter(batch=i.batch, product=i.product)
        for order_item in order_items:
            order_quantity_out += int(order_item.quantity)
            # print(order_item.quantity)

    purchases = Purchase.objects.filter(
        material_name=i.material_center,
        created_on=date,
        item_details__item=i.product,
        item_details__batch=i.batch
    )
    for purchase in purchases:
        purchase_item = purchase.item_details_set.filter(item=i.product, batch=i.batch)
        for pur in purchase_item:
            quantity_in += int(pur.quantity)
    quantity_out = quantity_out + order_quantity_out
    current_quantity = int(i.current_quantity) - quantity_out + quantity_in
    pre_inventry = previous_inventry.filter(product=i.product, batch=i.batch,
                                            material_center=i.material_center)
    for pre in pre_inventry:
        if today:
            opening_quantity = pre.current_quantity
        else:
            opening_quantity = pre.opening_quantity
    for ch in check:
        myid = ch.pk

    return opening_quantity, quantity_in, quantity_out, current_quantity, myid

@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['cron_management', ['1', '2']])
def remove_unlinked_product_batch(request):
    try:
        today = date.today()
        latest_built = today
        if request.method == 'POST':
            inventory = Inventry.objects.all()
            for i in inventory:
                batch_to_check = i.batch
                product_to_check = i.product
                if not Batch.objects.filter(id = batch_to_check.id, product = product_to_check):
                    i.delete()
                    print(i)
    except Exception as e:
        messages.error(request, "something went wrong" + str(e))

    return render(request, 'mlm_admin/rebuildingCron.html', {'today': today, 'latest_built': latest_built})

@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['cron_management', ['1', '2']])
def rebuilding_cron(request):
    from .cron_jobs import update_inventry
    from datetime import datetime, date, timedelta
    today = date.today()
    try:
        if request.method == 'POST':
            update_inventry()

            # dateStart = request.POST.get('rebuildingStartdate', None)
            # dateEnd = request.POST.get('rebuildingEnddate', None)

            # if dateStart and dateEnd:
            #     dateStart_object = datetime.strptime(dateStart, '%Y-%m-%d')
            #     dateEnd_object = datetime.strptime(dateEnd, '%Y-%m-%d')

            #     delta = dateEnd_object - dateStart_object
            #     for i in range(delta.days + 1):
            #         date = dateStart_object + timedelta(days=i)
            #         print("Cron is building for date:", date)
            #         previous = date - timedelta(days=1)
            #         select_date_inventry = Inventry.objects.filter(created_on=date,)
            #         previous_inventry = Inventry.objects.filter(created_on=previous,)
            #         for i in previous_inventry:
            #             check = select_date_inventry.filter(product=i.product, batch=i.batch,
            #                                                 material_center=i.material_center)
            #             if check:
            #                 # AG:: First we will correct previous day inventory is required
            #                 opening_quantity, quantity_in, quantity_out, current_quantity, myid = rebuilding_cron_fn(i, check, date, previous_inventry, False)
            #                 Inventry.objects.filter(created_on=previous,
            #                                         product=i.product,
            #                                         batch=i.batch,
            #                                         material_center=i.material_center, ).update(
            #                                                             quantity_in=quantity_in,
            #                                                             quantity_out=quantity_out,
            #                                                             current_quantity=current_quantity,
            #                                                             opening_quantity=opening_quantity
            #                                                         )

            #                 # AG:: Then we will correct previous day inventory
            #                 new_i = previous_inventry.filter(product = i.product,batch = i.batch,material_center = i.material_center, created_on = previous)[0]
            #                 opening_quantity, quantity_in, quantity_out, current_quantity, myid = rebuilding_cron_fn(new_i, check, date, previous_inventry, True)
            #                 Inventry.objects.filter(pk=myid).update(
            #                                     product=i.product,
            #                                     batch=i.batch,
            #                                     material_center=i.material_center,
            #                                     quantity_in=quantity_in,
            #                                     quantity_out=quantity_out,
            #                                     current_quantity=current_quantity,
            #                                     opening_quantity=opening_quantity
            #                                 )
            #             else:
            #                 inventry = Inventry(
            #                     product=i.product,
            #                     batch=i.batch,
            #                     material_center=i.material_center,
            #                     purchase_price=i.purchase_price,
            #                     opening_quantity=i.current_quantity,
            #                     current_quantity=i.current_quantity,
            #                     quantity_in=0,
            #                     quantity_out=0,
            #                     created_on=date
            #                 )
            #                 inventry.save()

            #         # print('data--->',previous_inventry.count())
                # else:
                #     pass
    except Exception as e:
        messages.error(request, "something went wrong" + str(e))
    try:
        latest_built = Inventry.objects.all().latest('created_on').created_on
    except:
        latest_built = date.today()

    return render(request, 'mlm_admin/rebuildingCron_timed.html', {'today': today, 'latest_built': latest_built})



@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['cron_management', ['1', '2']])
def recalculate_distributor_orders(request):
    from datetime import datetime, date, timedelta
    today = date.today()
    try:
        if request.method == 'POST':
            dateStart = request.POST.get('rebuildingStartdate', None)
            dateEnd = request.POST.get('rebuildingEnddate', None)

            if dateStart and dateEnd:
                dateStart_object = datetime.strptime(dateStart, '%Y-%m-%d')
                dateEnd_object = datetime.strptime(dateEnd, '%Y-%m-%d')

                delta = dateEnd_object - dateStart_object
                for i in range(delta.days + 1):
                    date = dateStart_object + timedelta(days=i)
                    print("Cron is building for date:", date)
                    distributor_sales = Distributor_Sale.objects.filter(date=date)
                    for distributor_sale in distributor_sales:
                        recalculate_everything(request, myid=distributor_sale.id, post_bill=True, check=False, mlm_admin=True)
                else:
                    pass
    except Exception as e:
        messages.error(request, "something went wrong" + str(e))
    try:
        latest_built = Inventry.objects.all().latest('created_on').created_on
    except:
        latest_built = date.today()

    return render(request, 'mlm_admin/rebuildingCron_timed.html', {'today': today, 'latest_built': latest_built, 'fast_option':'hide'})



@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['cron_management', ['1', '2']])
def D_rebuilding_cron(request):
    from datetime import datetime, date, timedelta
    today = date.today()
    try:
        if request.method == 'POST':
            # dateStart = request.POST.get('rebuildingStartdate', None)
            # dateEnd = request.POST.get('rebuildingEnddate', None)
            # fast = request.POST.get('fast', False)
            # if fast == 'fast':
            #     fast = True

            try:
                update_inventry()
            except Exception as error:
                messages.error(request, str(error))

            # if dateStart and dateEnd:
            #     dateStart_object = datetime.strptime(dateStart, '%Y-%m-%d')
            #     dateEnd_object = datetime.strptime(dateEnd, '%Y-%m-%d')

            #     try:
            #         update_inventry(dateStart_object, dateEnd_object, fast)
            #     except Exception as error:
            #         messages.error(request, str(error))

                # delta = dateEnd_object - dateStart_object

                # for i in range(delta.days + 1):
                #     date = dateStart_object + timedelta(days= i)
                #     print("Cron is building for date:", date)
                #     previous = date - timedelta(days = 1)
                #     previous_inventry = Distributor_Inventry.objects.filter(created_on = previous)
                #     select_date_inventry = Distributor_Inventry.objects.filter(created_on=date)
                #     # previous_inventry = Distributor_Inventry.objects.filter(created_on = previous,
                #     #     material_center_id=7, product_id=36)
                #     # print("Cron previous date", previous)
                #     for i in previous_inventry:
                #         check = select_date_inventry.filter(product = i.product,batch = i.batch,material_center = i.material_center)
                #         if check:
                #             quantity_in = 0
                #             quantity_out = 0
                #             opening_quantity = 0

                #             # Let's calculate the total today sale inventry (calculate out quantity)
                #             # sales = Distributor_Sale.objects.filter(
                #             #         material_center=i.material_center,
                #             #         created_on=date,
                #             #         distributor_sale_itemdetails__item=i.product,
                #             #         distributor_sale_itemdetails__batch=i.batch,
                #             #         delete=False,
                #             #         order__delete=False
                #             #     ).exclude(order__status=8)
                #             sales = Distributor_Sale.objects.filter(
                #                     material_center=i.material_center,
                #                     created_on=date,
                #                     delete=False,
                #                     order__delete=False
                #                 ).exclude(order__status=8)
                #             for sale in sales:
                #                 sale_item = sale.distributor_sale_itemdetails_set.filter(item=i.product, batch=i.batch)
                #                 for s in sale_item:
                #                     quantity_out += int(s.quantity)

                #             # print(quantity_out, "quantity_out*********************************")

                #             # Let's calculate the total today purchase inventry (calculate in quantity)
                #             purchases = Sale.objects.filter(
                #                     material_center_to=i.material_center,
                #                     accepted_date=date,
                #                     sale_itemdetails__item=i.product,
                #                     sale_itemdetails__batch =i.batch,
                #                     accept= True,
                #                     delete= False

                #                 )
                #             for purchase in purchases:
                #                 purchase_item = purchase.sale_itemdetails_set.filter(item=i.product, batch=i.batch)
                #                 for pur in purchase_item:
                #                     quantity_in += int(pur.quantity)
                #             # print(quantity_in, "quantity_in*********************************")

                #             ''' Here I am using previous opening quantity (i.opening_quantity) because I am adding
                #             and substracting again quantity_out and quantity_in'''
                #             opening_quantity = int(i.current_quantity)
                #             current_quantity = opening_quantity - quantity_out + quantity_in
                #             # print(current_quantity, "current_quantity#######################################")

                #             for ch in check:
                #                 myid = ch.pk

                #             Distributor_Inventry.objects.filter(pk=myid).update(product=i.product,
                #                                                 batch=i.batch,
                #                                                 material_center=i.material_center,
                #                                                 quantity_in=quantity_in,
                #                                                 quantity_out=quantity_out,
                #                                                 current_quantity=current_quantity,
                #                                                 opening_quantity=opening_quantity
                #                                             )

                #         else:
                #             inventry = Distributor_Inventry(
                #                 product = i.product,
                #                 batch = i.batch,
                #                 material_center = i.material_center,
                #                 purchase_price = i.purchase_price,
                #                 opening_quantity = i.current_quantity,
                #                 current_quantity = i.current_quantity,
                #                 quantity_in = 0,
                #                 quantity_out = 0,
                #                 created_on = date
                #             )
                #             inventry.save()

                #     print('data--->',previous_inventry.count())
                # else:
                #     pass
    except Exception as e:
        messages.error(request, "something went wrong " + str(e))
    try:
        latest_built = Distributor_Inventry.objects.all().latest('created_on').created_on
    except:
        latest_built = date.today()
    return render(request, 'mlm_admin/rebuildingCron.html', {'today': today, 'latest_built': latest_built})


# <-----------------------------------------------------------------------------------------------------------------------testing rebuilding  code here end-->

def mc_name(request):
    mc_name = request.GET.get('mc_name')
    mc_name = request.GET.get('mc_name')
    data = Material_center.objects.filter(mc_name__iexact=mc_name)
    if len(data) > 0:
        code = 404
    else:
        code = 200
    return JsonResponse({'code': code})


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['sale_management', ['1', '2', '3', '4']])
def distributors_sale_list(request):
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        data = Distributor_Sale.objects.filter(
            Q(material_center__mc_name__icontains=q) | Q(created_on__icontains=q) | Q(party_name__icontains=q)
            | Q(grand_total__icontains=q), delete=False).order_by('-id')
    else:
        q = ''
        data = Distributor_Sale.objects.filter(delete=False).order_by('-id')
    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'mlm_admin/distributors_sale_list.html', {'data': page_obj, 'title': 'Sale List', 'q': q})


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['sale_management', ['1', '2', '3', '4']])
def distributor_view_sale(request, myid):
    # <------------------------------------------------------------------------------------------------------------------------------------------------------------------------>
    batches = Batch.objects.all().exclude(delete=True)
    items = Product.objects.all().exclude(delete=True)
    users = User.objects.all()
    sale_data = Distributor_Sale.objects.get(pk=myid)
    data = Distributor_Sale_itemDetails.objects.filter(sale=sale_data)
    params = {
        'batches': batches,
        'items': items,
        'users': users,
        'sale_data': sale_data,
        'data': data,
        'title': 'View Sale'
    }
    return render(request, 'mlm_admin/distributor_view_sale.html', params)


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['sale_management', ['1', '2', '3', '4']])
def distributors_edit_sale(request, myid):
    # <--------------------------------------------------Dealing with post request Start here---------------------------------------------------------------------------------------------------------------------->
    if request.method == "POST":
        date = request.POST['date']
        mc_center = request.POST['material_center']
        # mc_center_from = request.POST['material_center_from']
        narration = request.POST['narration']
        user = request.POST['user']
        # party_name = request.POST['party_name']
        sale_type = request.POST['sale_type']
        grand_total = request.POST['grand_total']
        item = request.POST.getlist('item')
        batch = request.POST.getlist('batch')
        quaantity_item = request.POST.getlist('quaantity_item')
        distributor_price = request.POST.getlist('distributor_price')
        cgst_item = request.POST.getlist('cgst_item')
        sgst_item = request.POST.getlist('sgst_item')
        igst_item = request.POST.getlist('igst_item')
        vat_item = request.POST.getlist('vat_item')
        totalamount_item = request.POST.getlist('totalamount_item')
        user = User.objects.get(pk=user)
        print('narro', date, narration, quaantity_item, distributor_price, cgst_item, sgst_item, igst_item,
              vat_item, totalamount_item, 'item', item, 'batch', batch)
        # try:
        material_center = Material_center.objects.get(pk=mc_center)
        # material_center_from = Material_center.objects.get(pk=mc_center_from)
        # user = User.objects.get(pk=user)
        data = Distributor_Sale.objects.filter(pk=myid).update(sale_user_id=request.user,
                                                               material_center=material_center,
                                                               advisor_distributor_name=user, date=date,
                                                               narration=narration, sale_type=sale_type,
                                                               grand_total=grand_total)
        obj = Distributor_Sale.objects.get(pk=myid)
        Order.objects.filter(pk=obj.order.pk).update(grand_total=grand_total, name=user.username, email=user.email)
        sale_items = Distributor_Sale_itemDetails.objects.filter(sale=obj)
        for i in sale_items:
            distributor_batch = Distributor_Batch.objects.get(batch=i.batch,
                                                              distributor_material_center=obj.material_center)
            update_time_batch_quantity = int(distributor_batch.quantity) + int(i.quantity)
            Distributor_Batch.objects.filter(pk=distributor_batch.pk).update(quantity=update_time_batch_quantity)
            today = datetime.now().date()
            update_time_inventry = Distributor_Inventry.objects.get(created_on=obj.created_on, product=i.item,
                                                                    batch=i.batch, material_center=obj.material_center)
            update_time_inventry_current_quantity = int(update_time_inventry.current_quantity) + int(i.quantity)
            update_time_inventry_quantity_out = int(update_time_inventry.quantity_out) - int(i.quantity)
            Distributor_Inventry.objects.filter(pk=update_time_inventry.pk).update(
                current_quantity=update_time_inventry_current_quantity,
                quantity_out=update_time_inventry_quantity_out)
        Distributor_Sale_itemDetails.objects.filter(sale=obj).delete()
        try:
            for i, k in enumerate(totalamount_item):
                sale = obj
                print('object', sale)
                quantity = quaantity_item[i]
                price = distributor_price[i]
                cgst = cgst_item[i]
                sgst = sgst_item[i]
                igst = igst_item[i]
                vat = vat_item[i]
                total_amount = totalamount_item[i]
                product = item[i]
                product = Product.objects.get(pk=product)
                batch1 = batch[i]
                batch1 = Batch.objects.get(pk=batch1)
                batch_qty = Distributor_Batch.objects.get(batch=batch1, distributor_material_center=material_center)
                # inventory code start
                batch_quantity = batch_qty.quantity
                update_batch_quantity = int(batch_quantity) - int(quantity)
                Distributor_Batch.objects.filter(pk=batch_qty.pk).update(quantity=update_batch_quantity)
                try:
                    today = datetime.now().date()
                    D_inventory_update = Distributor_Inventry.objects.get(product=product, batch=batch1,
                                                                          material_center=material_center,
                                                                          created_on=obj.created_on)
                    D_inventory_update_current_quantity = int(D_inventory_update.current_quantity) - int(quantity)
                    D_inventory_update_quantity_out = int(D_inventory_update.quantity_out) + int(quantity)
                    Distributor_Inventry.objects.filter(product=product, batch=batch1, material_center=material_center,
                                                        created_on=obj.created_on).update(
                        current_quantity=D_inventory_update_current_quantity,
                        quantity_out=D_inventory_update_quantity_out)
                except:
                    # here add code for inventry start here 20-03-2021
                    try:
                        D_inventory_update = Distributor_Inventry.objects.filter(product=product, batch=batch1,
                                                                                 material_center=material_center,
                                                                                 created_on=obj.created_on)
                        current_quantity = int(D_inventory_update.current_quantity) + int(quantity)
                        D_inventory = Distributor_Inventry(product=product, batch=batch1,
                                                           material_center=material_center,
                                                           opening_quantity=D_inventory_update.opening_quantity,
                                                           current_quantity=current_quantity,
                                                           quantity_out=quantity,
                                                           created_on=obj.created_on)
                        D_inventory.save()
                    except:
                        D_inventory = Distributor_Inventry(product=product, batch=batch1,
                                                           material_center=material_center,
                                                           opening_quantity=0, current_quantity=quantity,
                                                           quantity_out=quantity,
                                                           created_on=obj.created_on)
                        D_inventory.save()

                saledata = Distributor_Sale_itemDetails(item=product, sale=sale, batch=batch1, quantity=quantity,
                                                        distributor_price=price, cgst=cgst, sgst=sgst, igst=igst,
                                                        vat=vat,
                                                        total_amount=total_amount, )
                print(obj.order.order_id1, 'here is the order id')
                LineItem.objects.filter(order_id=obj.order.pk).delete()
                li = LineItem(
                    order_by=user.email,
                    product_id=product.id,
                    price=price,
                    # price = cart_item.price,
                    quantity=quantity,
                    order_id=obj.order.id,
                    batch=batch1,
                    cgst=product.cgst,
                    sgst=product.sgst,
                    igst=product.igst
                )
                li.save()
                saledata.save()
            messages.success(request, "Record added successfully!")
            return redirect('mlm_admin_distributors_sale_list')
        except:
            messages.success(request, "Record added successfully!")
            return redirect('mlm_admin_distributors_sale_list')

        # except:
        #     messages.warning(request, "something is going wrong")
        #     return redirect('distributor_sale_list')
    # <--------------------------------------------------Dealing with post request End here--------------------------------------------------------------------------------------------------------------------->

    today = datetime.now().date()
    products = Distributor_Inventry.objects.filter(created_on=today).values_list('product')
    print(products, '<sdfjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj>')
    print(set(products), '<sdfjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj>')
    products = set(products)
    product = []
    for i in products:
        for j in i:
            product.append(j)
    batches = Batch.objects.all().exclude(delete=True)
    items = Product.objects.filter(pk__in=product).exclude(delete=True)
    users = User.objects.filter(profile__normal=True)
    sale_data = Distributor_Sale.objects.get(pk=myid)
    data = Distributor_Sale_itemDetails.objects.filter(sale=sale_data)
    params = {
        'batches': batches,
        'items': items,
        'users': users,
        'sale_data': sale_data,
        'data': data,
        'title': 'Edit Sale'
    }
    return render(request, 'mlm_admin/distributors_edit_sale.html', params)


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['sale_management', ['1', '2', '3', '4']])
def distributor_delete_sale(request, myid):
    sale = Distributor_Sale.objects.get(pk=myid)
    sale_items = Distributor_Sale_itemDetails.objects.filter(sale=sale)
    for i in sale_items:
        distributor_batch = Distributor_Batch.objects.get(batch=i.batch,
                                                          distributor_material_center=sale.material_center)
        update_time_batch_quantity = int(distributor_batch.quantity) + int(i.quantity)
        Distributor_Batch.objects.filter(pk=distributor_batch.pk).update(quantity=update_time_batch_quantity)
        today = datetime.now().date()
        update_time_inventry = Distributor_Inventry.objects.get(created_on=sale.created_on, product=i.item,
                                                                batch=i.batch, material_center=sale.material_center)
        update_time_inventry_current_quantity = int(update_time_inventry.current_quantity) + int(i.quantity)
        update_time_inventry_quantity_out = int(update_time_inventry.quantity_out) - int(i.quantity)
        Distributor_Inventry.objects.filter(pk=update_time_inventry.pk).update(
            current_quantity=update_time_inventry_current_quantity,
            quantity_out=update_time_inventry_quantity_out)
    sale_delete = Distributor_Sale.objects.filter(pk=myid).update(delete=True)
    messages.success(request, "Record deleted successfully!")
    return redirect('mlm_admin_distributors_sale_list')


from distributor.utils import render_to_pdf
from django.core.mail import EmailMessage, EmailMultiAlternatives
from portal_auretics_com.settings import EMAIL_HOST_USER
from django.conf import settings


def invoice_check(request, myid):
    if request.method == 'POST':
        sale = Distributor_Sale.objects.get(pk=myid, delete=False)
        order = Order.objects.get(pk=sale.order.pk, delete=False)
        Body = '''<h1>here we are geting mail having h1 tag</h1>'''
        email = EmailMessage('Subject', Body, )
        email.send()
        ctx = {
            'sale': sale,
            'order': order
        }
        email_id = sale.advisor_distributor_name.email
        message = get_template('mlm_admin/invoice_send.html').render(ctx)
        msg = EmailMessage(
            'Subject',
            message,
            to=[email_id]
        )
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()
        print("Mail successfully sent")
    sale = Distributor_Sale.objects.get(pk=myid, delete=False)
    order = Order.objects.get(pk=sale.order.pk, delete=False)
    return render(request, 'mlm_admin/invoice.html', {'sale': sale, 'order': order, 'title': 'Invoice'})


def pv_bv_rebuilding(request, perform=False):
    if request.method == 'POST':
        perform = True
    if perform:
        for product in Product.objects.all():
            batchResp = calculate_values(product)
            for batch in batchResp:
                try:
                    Batch.objects.filter(id=batch['batch'].id).update(pv=batch['point_value'],
                                                                      bv=batch['business_value'])
                except:
                    Batch.objects.filter(id=batch['batch'].id).update(pv=0, bv=0)
        messages.success(request, "PV and BV calculated successfully!")
    return render(request, 'mlm_admin/pv_bv_rebuilding.html')


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['wallet_cofiguration',['1','2','3','4']])
def useractivity_log(request):
    useractivity = UserLoginActivity.objects.all()
    paginator = Paginator(useractivity, 10)
    print(paginator, 'paginator')
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'mlm_admin/useractivity_log.html', {'useractivity': page_obj})


@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['manual_verification',['1','2','3','4']])
def Useractivity_detail(request, myid):
    useractivity = UserLoginActivity.objects.get(pk=myid)

    return render(request, 'mlm_admin/useractivity_detail.html', {'useractivity': useractivity})


def kyc_user_screen_verified(request):
    verified_users = KycDone.objects.filter(kyc_verification_type="Signzy")

    paginator = Paginator(verified_users, 10)
    print(paginator, 'paginator')
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    params = {'verified_users': page_obj}
    return render(request, "mlm_admin/kyc_users_screen_verified.html", params)


def kyc_user_screen_manual(request):
    manual_verification = KycDone.objects.filter(kyc_verification_type="Manually")
    paginator = Paginator(manual_verification, 10)
    print(paginator, 'paginator')
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    params = {'manual_verification': page_obj}

    return render(request, "mlm_admin/kyc_users_screen_manual.html", params)


def kyc_user_screen_unverified(request):
    unverified_users = KycDone.objects.filter(kyc_verification_type="None")
    paginator = Paginator(unverified_users, 10)
    print(paginator, 'paginator')
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    params = {'unverified_users': page_obj}

    return render(request, "mlm_admin/kyc_users_screen_unverified.html", params)


def auto_kyc_verification(request, mid):
    details = ManualVerification.objects.get(id=mid)
    kyc = Kyc.objects.get(kyc_user=details.kyc_user)
    pan_number = details.pan_number
    try:
        img_path = details.id_proof_file.path
    except:
        img_path = None
    response_kyc = Pan_verification(request, img_path, pan_number)

    if response_kyc["error"]:
        details.verified = False
        kyc.kyc_done = False
        kyc.manual = False
        kyc.save()
        details.save()
        messages.error(request, f"The {details.kyc_user}'s Pan verification is failed")

    result = response_kyc["result"]
    if result["verified"] == True:

        details.verified = True
        kyc.kyc_done = True
        kyc.manual = True
        kyc.save()
        details.save()
        messages.success(request, f"Congrats {details.kyc_user}'s KYC verified ")

    else:
        details.verified = False
        kyc.kyc_done = False
        kyc.manual = False
        kyc.save()
        details.save()
        messages.error(request, f"Sory {details.kyc_user}'s KYC Verification Failed")
    return redirect("manual_verification")


def change_mobile_number(request, myid):
    user = User.objects.get(pk=myid)

    if request.method == 'POST':
        date = datetime.now()
        old_number = Profile.objects.get(user=user).phone_number
        new_number = request.POST.get('new_number',None)
        if not new_number:
            return HttpResponse("Please enter a number")
        if len(new_number) != 10:
            return HttpResponse("Number must be of 10 digits")
        try:
            check_number = Profile.objects.get(phone_number=new_number)
            return HttpResponse("This number is already in used")
        except:
            pass

        number_change = ChangeMobileNumber.objects.create(
            date=date,
            old_number=old_number,
            new_number=new_number,
            user_name=user,
        )
        number_change.save()

        profile_update = Profile.objects.filter(user=user).update(
            phone_number=new_number,
        )
        address_update = Address.objects.filter(user=user).update(
            mobile=new_number,
        )

    return render(request, "mlm_admin/change_mobile.html", {'user':user,})


def change_email_id(request, myid):
    user = User.objects.get(pk=myid)

    if request.method == 'POST':
        date = datetime.now()
        old_email = user.username
        new_email = request.POST.get('new_email',None)
        new_email = new_email.lower()
        if not new_email:
            return HttpResponse("Please enter a valid Email Id")
        if not '@' in new_email:
            return HttpResponse("Email not valid")
        try:
            check_email = User.objects.get(username=new_email)
            return HttpResponse("This Email is already used")
        except:
            pass

        email_change = ChangeEmail.objects.create(
            date=date,
            old_email=old_email,
            new_email=new_email,
            user_name=user,
        )
        email_change.save()

        profile_update = Profile.objects.filter(user=user).update(
            email=new_email,
        )

        user_update = User.objects.filter(pk=user.pk).update(
            username=new_email,
            email=new_email,
        )

        order_update = Order.objects.filter(email=old_email).update(
            name=new_email,
            email=new_email,
        )

    return render(request, "mlm_admin/change_email.html", {'user': user,})


def email_sanitation_check(request):
    '''
    This function checks the whether email id everywhere is smae or not.
    '''

    user_with_email_issues = cache.get("user_with_email_issues")
    orders_with_email_issues = cache.get("orders_with_email_issues")
    if user_with_email_issues is None:
        user = User.objects.all()

        user_with_email_issues = []
        orders_with_email_issues = []
        for i in user:
            email = i.username
            profile_email = Profile.objects.get(user=i).email
            user_email = User.objects.get(pk=i.pk).email
            if email != profile_email:
                user_with_email_issues.append(str(email) + " - " + str("Profile Email") + " << (" + str(profile_email) + ")")
            if email != user_email:
                user_with_email_issues.append(str(email) + " - " + str("User Email") + " << (" + str(user_email) + ")")

            if email:
                order_email = Order.objects.filter(user_id=i, paid=True, delete=False).exclude(status=8)
                for j in order_email:
                    if email != j.email:
                        orders_with_email_issues.append(str(email) + " - " + str("Issue in Order PK: ") + str(j.pk) + " << (" + str(j.email) + " Date: " + str(j.date) + ")")

        cache.set("user_with_email_issues", user_with_email_issues)
        cache.set("orders_with_email_issues", orders_with_email_issues)

    return render(request, "mlm_admin/blank.html", {'a':user_with_email_issues,
                                                    'b':orders_with_email_issues,})


class GatewayAddUpdateView(SuccessMessageMixin, FormView):
    model = Gateway
    template_name = 'mlm_admin/gateway/add_gateway.html'
    form_class = AddGatewayForm
    success_url = reverse_lazy('list_gateway')

    def get_context_data(self, **kwargs):
        gateway_id = self.kwargs.get('pk', None)
        if gateway_id is not None:
            gateway = get_object_or_404(Gateway, pk=gateway_id)
            form = self.form_class(self.request.POST or None, instance=gateway)
            context = {'form': form}
            return context
        form = self.form_class(self.request.POST or None)
        context = {'form': form}
        return context

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        gateway_id = self.kwargs.get('pk', None)
        if gateway_id is not None:
            gateway = get_object_or_404(Gateway, pk=gateway_id)
            form = self.form_class(request.POST or None, instance=gateway)
            if form.is_valid():
                form.save()
                messages.success(self.request, 'Gateway was successfully Updated!')
                return HttpResponseRedirect(self.success_url)
            return render(self.request, self.template_name, {'form': form})
        else:
            form = self.form_class(self.request.POST or None)
            if form.is_valid():
                form.save()
                messages.success(self.request, 'Gateway was successfully added!')
                return HttpResponseRedirect(self.success_url)
            return render(self.request, self.template_name, {'form': form})


class PriorityGatewayAddUpdateView(SuccessMessageMixin, FormView):
    model = PaymentMode
    template_name = 'mlm_admin/gateway/priority_gateway.html'
    form_class = PriorityGatewayForm
    success_url = reverse_lazy('list_priority')

    def get_context_data(self, **kwargs):
        priority_id = self.kwargs.get('pk', None)
        if priority_id is not None:
            gateway = get_object_or_404(PaymentMode, pk=priority_id)
            form = self.form_class(self.request.POST or None, instance=gateway)
            context = {'form': form}
            return context
        form = self.form_class(self.request.POST or None)
        context = {'form': form}
        return context

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        priority_id = self.kwargs.get('pk', None)
        if priority_id is not None:
            gateway = get_object_or_404(PaymentMode, pk=priority_id)
            form = self.form_class(request.POST or None, instance=gateway)
            if form.is_valid():
                form.save()
                messages.success(self.request, 'Gateway Priority was successfully Updated!')
                return HttpResponseRedirect(self.success_url)
            return render(self.request, self.template_name, {'form': form})
        else:
            form = self.form_class(self.request.POST or None)
            if form.is_valid():
                form.save()
                messages.success(self.request, 'Gateway Priority was successfully added!')
                return HttpResponseRedirect(self.success_url)
            return render(self.request, self.template_name, {'form': form})


class GatewayNameListView(ListView):
    model = Gateway
    template_name = 'mlm_admin/gateway/gateway_name_list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        object_list = Gateway.objects.all()
        paginator = Paginator(object_list, self.paginate_by)
        page = self.request.GET.get('page')
        try:
            pagination = paginator.page(page)
        except PageNotAnInteger:
            pagination = paginator.page(1)
        except EmptyPage:
            pagination = paginator.page(paginator.num_pages)
        context = {'object_list': pagination}
        return context

    def get_queryset(self):
        object_list = Gateway.objects.all()
        return object_list


class GatewayPriorityListView(ListView):
    model = PaymentMode
    template_name = 'mlm_admin/gateway/priority_list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        object_list = PaymentMode.objects.all()
        paginator = Paginator(object_list, self.paginate_by)
        page = self.request.GET.get('page')
        try:
            pagination = paginator.page(page)
        except PageNotAnInteger:
            pagination = paginator.page(1)
        except EmptyPage:
            pagination = paginator.page(paginator.num_pages)
        context = {'object_list': pagination}
        return context

    def get_queryset(self):
        object_list = PaymentMode.objects.all()
        return object_list


def delete_gateway(request, myid):
    gateway_name = Gateway.objects.get(pk=myid)
    gateway_name.delete()
    messages.success(request, "Gateway Deleted Successfully!")
    return redirect('list_gateway')

def delete_priority(request, myid):
    priority = PaymentMode.objects.get(pk=myid)
    priority.delete()
    messages.success(request, "PaymentMode Deleted Successfully!")
    return redirect('list_priority')


class BlockedUserListView(ListView):
    model = PaymentMode
    template_name = 'mlm_admin/blocked_user.html'
    paginate_by = 10

    def get_queryset(self):
        user_list = User.objects.all()
        return user_list

@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['mc_management', ['1', '2', '3', '4']])
def address_list(request):
    if 'q' in request.GET:
        q = request.GET.get('q', False)
        data = Address.objects.filter(
            Q(name__icontains=q) | Q(address_line__icontains=q) | Q(city__icontains=q) | Q(mobile__icontains=q)).order_by('-id')
    else:
        q = ''
        data = Address.objects.all().order_by('-id')
    
    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'mlm_admin/address_list.html', {'data': page_obj, 'title': 'Address List', 'q': q})

@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['mc_management', ['1', '2', '3', '4']])
def address_add(request):
    all_states = AdminState.objects.all()
    return render(request, 'mlm_admin/address_add.html', {"all_states":all_states, 'title':'Add New Address'})

@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['mc_management', ['1', '2', '3', '4']])
def address_edit(request, myid):
    ad = Address.objects.get(id=myid)
    all_states = AdminState.objects.all()
    return render(request, 'mlm_admin/address_add.html', {"ad":ad, "all_states":all_states, 'title':'Edit Address'})

@user_passes_test(is_mlm_admin, login_url='mlm_admin_login')
@allowed_users(allowed_roles=['mc_management', ['3']])
def address_view(request, myid):
    ad = Address.objects.get(id=myid)
    return render(request, 'mlm_admin/address_add.html', {"ad":ad, "ad_view":True, 'title':'View Address'})


def tds_calculation(request):
    if 'recal' in request.GET:
        inner_configurations_qs = inner_configurations.objects.last()
        tds_rate = float(inner_configurations_qs.tds_percentage / 100)     # 5/100
        min_amount = float(inner_configurations_qs.tds_min_amount)         # 5000

        fiscalyear.START_MONTH = 4
        # c_data = commission_wallet_model.objects.filter(tds_job_done=False)
        c_data = commission_wallet_model.objects.filter(amount_in__gt=0)
        c_data2 = c_data.dates('input_date', 'month', order="ASC")\
            .values('id','user', 'input_date')\
                .annotate(earning=Sum('amount_in'))\
                    .filter(earning__gt=0)
        for i in c_data2:
            year = i['input_date'].year if i['input_date'].month>=1 and i['input_date'].month<=3 else i['input_date'].year+1
            o_year = i['input_date'].year-1 if i['input_date'].month == 1 else i['input_date'].year
            o_month = 12 if i['input_date'].month == 1 else i['input_date'].month-1
            cur_y = fiscalyear.FiscalYear(year)
            tds_qs = Tds_calculation.objects.filter(user_id=i['user'], month__gte=cur_y.start.date(), month__lte=f'{o_year}-{o_month}-1')
            cum_earning = (tds_qs.aggregate(cum_earning=Sum('earning'))['cum_earning'] or 0) + i['earning']
            tds = float(cum_earning) * tds_rate if cum_earning>=min_amount else 0
            # print(o_year, o_month)
            try:
                tds_payable = float(Tds_calculation.objects.get(
                    user_id=i['user'], month__year=o_year, month__month=o_month).tds)
            except:
                tds_payable = 0.0
            # print(tds_payable)
            tds_payable = float(tds) - float(tds_payable)

            Tds_calculation.objects.update_or_create(user_id=i['user'],
                                                     month=i['input_date'],
                                                     defaults = {
                                                                'user_id':i['user'],
                                                                'month':i['input_date'],
                                                                'earning':i['earning'],
                                                                'cum_earning':cum_earning,
                                                                'tds':tds,
                                                                'tds_payable':tds_payable,
                                                                'amount':float(i['earning'])-tds_payable
                                                        })
            input_date = i['input_date']#.split('-')
            year = input_date.year#[0]
            month = input_date.month#[1]
            user_commission_wallet_model_qs = commission_wallet_model.objects.get(user = i['user'],
                                                                                  input_date__month = month,
                                                                                  input_date__year = year,)
            user_commission_wallet_model_qs.tds = tds
            user_commission_wallet_model_qs.commission_payable = float(user_commission_wallet_model_qs.amount_in) - tds_payable
            user_commission_wallet_model_qs.save()

            user_commission_wallet_amount_out_detail_model_qs = commission_wallet_amount_out_detail_model.objects.get(user = i['user'],
                                                                                  input_date__month = month,
                                                                                  input_date__year = year,)
            user_commission_wallet_amount_out_detail_model_qs.instrument_amount_without_comma_style = float(user_commission_wallet_model_qs.commission_payable)
            user_commission_wallet_amount_out_detail_model_qs.save()
            
        c_data.update(tds_job_done=True)

    if 'month' in request.GET:
        month = request.GET.get('month', False)
        f_month = month.split('-')
        data = Tds_calculation.objects.filter(month__year=f_month[0], month__month=f_month[1]).order_by('-month')
    else:
        month = ''
        data = Tds_calculation.objects.all().order_by('-month')
    
    if 'download' in request.GET:
        response = HttpResponse(content_type='application/ms-excel')
        response['content-Disposition'] = f'attachment; filename = TDS Report {str(datetime.now())}.xls'
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('TDS Report')
        row_num = 0
        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        columns = ['Email','First Name','Last Name','Mobile Number','PAN','Referral Code','Month','Earning','CUM Earning','CUM TDS','TDS Payable','Amount']
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        font_style = xlwt.XFStyle()
        for my_row in data:
            pan = Kyc.objects.filter(kyc_user=my_row.user)
            if pan:
                pan = pan[0].pan_number
            else:
                pan = ''
            row_num += 1
            ws.write(row_num, 0, my_row.user.username, font_style)
            ws.write(row_num, 1, my_row.user.profile.first_name, font_style)
            ws.write(row_num, 2, my_row.user.profile.last_name, font_style)
            ws.write(row_num, 3, my_row.user.profile.phone_number, font_style)
            ws.write(row_num, 4, pan, font_style)
            ws.write(row_num, 5, my_row.user.referralcode.referral_code, font_style)
            ws.write(row_num, 6, my_row.month.strftime('%B %Y'), font_style)
            ws.write(row_num, 7, my_row.earning, font_style)
            ws.write(row_num, 8, my_row.cum_earning, font_style)
            ws.write(row_num, 9, my_row.tds, font_style)
            ws.write(row_num, 10, my_row.tds_payable, font_style)
            ws.write(row_num, 11, my_row.amount, font_style)
        
        wb.save(response)
        return response

    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'mlm_admin/tds_calculation.html', {'data': page_obj, 'title': 'TDS Calculation Report','month':month})
