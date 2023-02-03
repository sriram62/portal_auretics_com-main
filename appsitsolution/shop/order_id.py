from .models import Order
from datetime import date,datetime
from shop.models import Batch,Material_center
from accounts.models import *
from mlm_admin.models import Inventry
from distributor.models import Distributor_Inventry

from django.shortcuts import render, HttpResponse
# def order_id():
#     try:
#         mid = Order.objects.latest('pk')
#         if mid.order_id1:
#             today = date.today()
#             print(today)
#             d3 = str(today.year)
#             d4 = str(today.month)
#             t1 = mid.order_id1
#             t = t1.split('-')
#             print(t, len(t))
#
#             lt = t[len(t) - 1]
#             print('lt', lt)
#             t2 = int(lt)
#             t3 = str(t2 + 1)
#             order_id1 = 'dmlm' + '-' + d3 + d4 + '-' + t3
#         else:
#             today = date.today()
#             d3 = str(today.year)
#             d4 = str(today.month)
#             order_id1 = 'dmlm' + '-' + d3 + d4 + '-' + '1'
#     except:
#         today = date.today()
#         d3 = str(today.year)
#         d4 = str(today.month)
#         order_id1 = 'dmlm' + '-' + d3 + d4 + '-' + '1'
#     return order_id1


def check_quantity(product,quantity = 1,request=None):
    quantity = int(float(quantity))
    today = date.today()
    material = Material_center.objects.get(frontend=True)
    if request:
        if request.user.is_authenticated:
            # get the material center if distributor is selected if not then c&f state wise
            if "distributor_checkout" in request.session:
                material = Material_center.objects.get(id=request.session['distributor_checkout'])
            else:
                material = request.user.profile.get_related_mc()

    batchs = Batch.objects.filter(product=product,
                                  delete=False,
                                  # quantity__gte=quantity,
                                  # inventry__material_center = material,
                                  # inventry__current_quantity__gte= quantity,
                                  ).order_by("date_of_expiry")
    if product.expiration_dated_product == 'YES':
        batchs = batchs.filter(date_of_expiry__gte=today)

    batch_with_inventory = []
    for batch in batchs:
        inventory = Inventry.objects.filter(batch=batch,
                                            material_center=material, created_on = datetime.today()) # .latest('created_on')
        if inventory:
            inventory = inventory.first()
            if inventory.current_quantity >= int(quantity):
                batch_with_inventory.append(batch.pk)

    batchs = Batch.objects.filter(pk__in=batch_with_inventory)

    if batchs:
        batch = batchs.first()

    try:
        batch = Batch.objects.get(pk=batch.pk)
        distributor_checkout = False
        if material:
            if material.advisory_owned == "YES":
                distributor_checkout = True
        if not distributor_checkout:
            inventory = Inventry.objects.filter(product=product,
                                                batch=batch,
                                                material_center=material).latest('created_on')
        else:
            inventory = Distributor_Inventry.objects.filter(product=product,
                                                batch=batch,
                                                material_center=material).latest('created_on')
        if inventory.current_quantity >= int(quantity):
            return True
        else:
            return False
    except:
        return False


def order_id(material_center):
    # result = Order.objects.filter(material_center =19)
    # result=result.latest('pk')
    obj = Order.objects.filter(material_center =material_center.pk).order_by('-id')[:1]
    if len(obj) > 0:
        for i in obj:
            try:
                if i.order_id1:
                    today = date.today()
                    d3 = str(today.year)
                    d4 = str(today.month)
                    t1 = i.order_id1
                    t = t1.split('-')
                    month = t[2]
                    if d4 == month:
                        lt = t[len(t) - 1]
                        t2 = int(lt)
                        t3 = str(t2 + 1)
                        order_id1 = str(material_center.pk) + '-' + d3 + '-' + d4 + '-' + t3
                    else:
                        t3 = 1
                        order_id1 = str(material_center.pk) + '-' + d3 + '-' + d4 + '-' + t3
                else:
                    today = date.today()
                    d3 = str(today.year)
                    d4 = str(today.month)
                    order_id1 = str(material_center.pk) + '-' + d3 + '-' + d4 + '-' + '1'
            except:
                today = date.today()
                d3 = str(today.year)
                d4 = str(today.month)
                order_id1 = str(material_center.pk) + '-' + d3+ '-' + d4 + '-' + '1'
    else:
        today = date.today()
        d3 = str(today.year)
        d4 = str(today.month)
        order_id1 = str(material_center.pk) + '-' + d3+ '-' + d4 + '-' + '1'

    return order_id1
    # print(obj,'<---value of esss--')
    # return HttpResponse('<h1>data is compnini</h1>')

# update_order_id(19)


# <-----------------------------------------------------------this is the function to add the value of bv in the user profile column to check the plan ---------------------------->
def updaate_super_bv(pv,user):
    left_value = 0
    profile = Profile.objects.get(user = user)
    if(profile.super_bv < 1000):
        super_pv = float(profile.super_pv) + float(pv)
        if super_pv > 1000:
            left_value = super_pv - 1000
            Profile.objects.filter(user = user).update(super_bv = 1000)
        else:
            Profile.objects.filter(user = user).update(super_bv = super_pv)

    return left_value


# <-----------------------------------------------------------this is the function to add the value of bv in the user profile column to check the plan ---------------------------->