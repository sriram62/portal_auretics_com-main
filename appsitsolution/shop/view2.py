from django.shortcuts import render
from accounts.models import *
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.contrib import messages
# from decorators import login_required_message
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponse, redirect, \
    get_object_or_404, reverse
from django.contrib import messages
from portal_auretics_com.accounts.models import Product, Order, LineItem
from portal_auretics_com.accounts.models import ReferralCode,Profile
from portal_auretics_com.accounts.forms import CartForm, CheckoutForm
from django.contrib.auth.decorators import login_required
from accounts import cart
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from portal_auretics_com.accounts.forms import AddressForm

from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from django.conf import settings

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


# Create your views here.
@cache_page(CACHE_TTL)
def home(request):
    cat_qs = Product.objects.filter(category__cat_name='Bottomwear', ).first()
    sun_qs = Product.objects.filter(category__cat_name='Sunglasses', ).first()
    brand = Product.objects.filter(product_brand__brand_name='Sunglasses', ).first()
    gender_qs = Product.objects.filter(product_gender_name__gender_name='men').first()
    women_qs = Product.objects.filter(product_gender_name__gender_name='women').first()
    context={"cat_qs":cat_qs,
            "gender_qs":gender_qs,
            "women_qs":women_qs,
            "sun_qs":sun_qs,
            "cart_items":cart.get_all_cart_items(request),
            "cart_subtotal":cart.subtotal(request)
            }
    # boy_qs = Product.objects.filter(product_gender_name__gender_name='women')

    return render(request, 'base.html', context)

#ajax filter
@cache_page(CACHE_TTL)
def filetr_view(request):
    aa =(request.GET['radioValue'])
    print (type(aa))
    # print (request)
    if (aa == "1"):
        all_products= Product.objects.all().order_by("price").values()
    if (aa == "2"):
        all_products= Product.objects.all().order_by("-price").values()
    aa = list(all_products)
    print (all_products)
    return JsonResponse({'all_products':aa})

def validate_ref(request):
    referall_code = request.GET.get('referall_code', None)

    try:
        queryset = ReferralCode.objects.get(referral_code=referall_code)
        ref_list = queryset.user_id.username
        code= 200
    except ObjectDoesNotExist:
        ref_list=''
        code= 404
    #

    data = {
        'refer_by':ref_list,
        'code':code
    }
    return JsonResponse(data)
def validate_email_phone(request):
    email = request.GET.get('email',None)
    mobile = request.GET.get('mobile',None)
    try:
        user = Profile.objects.get(email = email)
        emai = user.email
        mobile = 'data'
        code = 200
    except ObjectDoesNotExist:
        try:
            user2 = Profile.objects.get(phone_number = mobile)
            mobile = user2.phone_number
        except ObjectDoesNotExist:
            mobile = ''
        email='data'
        code = 200

    data = {
        'email':email,
        'mobile':mobile,
        'code': code
    }
    return JsonResponse(data)

# cat dispaly
def categry_name(request, cat):
    qs =Product.objects.filter(category__cat_name=cat)
    return render(request, "lists.html", {
                                    'all_products': qs,
                                    "cart_items":cart.get_all_cart_items(request),
                                    "cart_subtotal":cart.subtotal(request)
                                    })

# Gender dispaly
def ProductCategory(request, name):
    qs = Product.objects.filter(product_gender_name__gender_name=name)
    return render(request, "lists.html", {
                                    'all_products': qs, "cart_items": cart.get_all_cart_items(request),
                                    "cart_subtotal": cart.subtotal(request)
                                    })
    # print (qs, cat_name)

@cache_page(CACHE_TTL)
def product_list(request):
    all_products = Product.objects.all()
    return render(request, "lists.html", {
                                    'all_products': all_products,
                                    "cart_items":cart.get_all_cart_items(request),
                                    "cart_subtotal":cart.subtotal(request)
                                    })


def product_search(request):
    # error_msg =False
    all_products = Product.objects.all()
    if request.method == 'POST':
        search_value= request.POST.get('search')
        all_products = Product.objects.filter(product_name__contains=search_value)
        if all_products:
            return render(request, 'search_list.html', {"all_products": all_products})
        else:
            all_products = Product.objects.all()
            error_msg = "no result"
            return render(request, 'search_list.html', {"all_products": all_products, 'error_msg': error_msg, "cart_items":cart.get_all_cart_items(request),
            "cart_subtotal":cart.subtotal(request)})

    return render(request, 'search_list.html', {"all_products": all_products, "cart_items": cart.get_all_cart_items(request),"cart_subtotal":cart.subtotal(request)})

# @login_required(login_url='/accounts/login')
#product details
@cache_page(CACHE_TTL)
def show_product(request, product_id, product_slug):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = CartForm(request, request.POST)
        if form.is_valid():
            request.form_data = form.cleaned_data
            cart.add_item_to_cart(request)
            return redirect('show_cart')
            # return HttpResponseRedirect(request.path_info)

    form = CartForm(request, initial={'product_id': product.id})
    return render(request, 'detail.html', {
                                            'product': product,
                                            'form': form,
                                            "cart_items": cart.get_all_cart_items(request),
                                            "cart_subtotal": cart.subtotal(request)
                                            })

# @login_required_message(message="You should be logged in, in order to see the index!")
@login_required(login_url='/accounts/login')
@cache_page(CACHE_TTL)
def show_cart(request):

    if request.method == 'POST':
        if request.POST.get('submit') == 'Update':
            cart.update_item(request)
        if request.POST.get('submit') == 'Remove':
            cart.remove_item(request)

    cart_items = cart.get_all_cart_items(request)
    cart_subtotal = cart.subtotal(request)
    if cart_items.count():
        print("you have item")
    else:
        messages.add_message(request, messages.INFO, "Your Cart is Empty.")
        return redirect('product_list')
    return render(request, 'cart.html', {
                                            'cart_items': cart_items,
                                            'cart_subtotal': cart_subtotal,
                                            "cart_items":cart.get_all_cart_items(request)
                                            })

# @login_required(login_url='/accounts/login')
# def checkout(request):
#     temp = Address.objects.filter(user=request.user, address_type="B" )[0]
#     if request.method == 'POST':
#         form = CheckoutForm(request.POST)
#         if form.is_valid():
#             default_address = request.POST.get('shipping_address')
#             if default_address:
#                 address_qs = Address.objects.filter(
#                                 user=request.user,
#                                 address_type='B',
#                                 default=True
#                             )
#                 print (address_qs)
#                 o = Order(
#                         name = request.user.get_full_name,
#                         email = request.user.email,
#                         postal_code = address_qs[0].pin,
#                         shipping_address = address_qs[0],
#                         # shipping_address
#                     )
#                 o.save()
#             else:
#                 cleaned_data = form.cleaned_data
#                 o = Order(
#                     order_by = request.user.email,
#                     name = cleaned_data.get('name'),
#                     email = cleaned_data.get('email'),
#                     postal_code = cleaned_data.get('postal_code'),
#                     address = cleaned_data.get('address'),
#                 )
#                 o.save()

#             all_items = cart.get_all_cart_items(request)
#             for cart_item in all_items:
#                 li = LineItem(
#                     order_by = request.user.email,
#                     product_id = cart_item.product_id,
#                     price = cart_item.price,
#                     quantity = cart_item.quantity,
#                     order_id = o.id
#                 )

#                 li.save()

#             cart.clear(request)

#             request.session['order_id'] = o.id

#             messages.add_message(request, messages.INFO, 'Order Placed!')
#             return redirect('order_summary')


#     else:
#         form = CheckoutForm()
#     return render(request, 'checkout.html', {'form': form, 'temp':temp, 'cart_items':cart.get_all_cart_items(request), 'cart_subtotal': cart.subtotal(request)})
# @login_required(login_url='/accounts/login')
@login_required(login_url='/checkout')
def checkout(request):
    temp = Address.objects.filter(user=request.user, address_type="B")[0]
    print (temp.user)
    # address = Address.objects.get()
    if request.method == 'POST':
        default_address = request.POST.get('shipping_address')
        if default_address:
            address_qs = Address.objects.filter(
                            user=request.user,
                            address_type='B',
                            default=True
                        )
            print (address_qs)
            o = Order(
                    name = request.user.username,
                    email = request.user.email,
                    postal_code = address_qs[0].pin,
                    shipping_address = address_qs[0],
                    # shipping_address
                )
            o.save()
        else:
            form = CheckoutForm(request.POST)
            if form.is_valid():
                cleaned_data = form.cleaned_data
                o = Order(
                    name = cleaned_data.get('name'),
                    email = cleaned_data.get('email'),
                    postal_code = cleaned_data.get('postal_code'),
                    address = cleaned_data.get('address'),
                    # shipping_address
                )
                o.save()
        all_items = cart.get_all_cart_items(request)
        for cart_item in all_items:
            li = LineItem(
                order_by=request.user.email,
                product_id=cart_item.product_id,
                price=cart_item.price,
                quantity=cart_item.quantity,
                order_id=o.id
            )
            li.save()

        cart.clear(request)

        request.session['order_id'] = o.id

        messages.add_message(request, messages.INFO, 'Order Placed!')
        return redirect('order_summary')


    else:
        form = CheckoutForm()
    return render(request, 'checkout.html', {'form': form, 'cart_items':cart.get_all_cart_items(request), 'cart_subtotal': cart.subtotal(request), 'temp':temp})


# def order_summary(request):
#     order_list = LineItem.objects.all()
#     return render(request, 'order.html', {'order_list':order_list})


@login_required(login_url='/accounts/login')
def order_summary(request):
    req_email = request.user.email
    print (request.user.email)
    try:
        # order= Order.objects.filter(order_by = req_email)[0]order.lineitem_set.all()
        order= Order.objects.filter(email = req_email)
        # order= LineItem.objects.filter(order_by=req_email).order_by('-date_added')
        if order.count() == 0:
            messages.warning(request,  "You do not have any Order.")
            return redirect('product_list')

    except LineItem.DoesNotExist:
        messages.warning(request,  "You do not have any Order.")
        return redirect('product_list')
    return render(request, 'order.html', {'order_list':order})


def order_details(request, email):
    print (email)
    try:
        order= LineItem.objects.filter(order_by=email)
        if order.count() == 0:
            messages.warning(request,  "You do not have any Order.")
            return redirect('product_list')
    except LineItem.DoesNotExist:
        messages.warning(request,  "You do not have any Order.")
        return redirect('product_list')
    # order= LineItem.objects.filter(order_by=email)
    return render(request, 'order-details.html', {'order_list':order})


def address_edit(request):
    address_qs= get_object_or_404(Address, user=request.user)
    address_form = AddressForm(instance=address_qs)
    if request.method == 'POST':
        address_form = AddressForm(instance=address_qs, data=request.POST )
        if address_form.is_valid():
            address_form.save()
            messages.success(request, "Address Updated Successfully!")
            return HttpResponseRedirect(reverse('checkout'))
    return render(request, 'edit_address.html', {'address_form':address_form
    })

@csrf_exempt
@cache_page(CACHE_TTL)
def filter_list(request):
    aa = (request.POST['radioValue'])
    bb = (request.POST.getlist('checkValue[]'))
    # db = json.load(request)['data']
    if not bb:
        bb = ['Footwear','TopWear','Sunglasses']
    for i in bb:
        print(i)
    print(type(bb))
    print('thi is data ', aa)
    print('thi is data ', bb)
    all_products = Product.objects.filter(category__cat_name__in=bb, price__lte=aa).values()
    abc = list(all_products)
    # if all_products:
    #     abc = list(all_products.values())
    # else:
    #     messages.warning(request,  "No Product Found.")
    #     return redirect('product_list')
    print(abc)
    return JsonResponse({'all_products': abc})


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

