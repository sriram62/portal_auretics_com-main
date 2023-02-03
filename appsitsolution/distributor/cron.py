from distributor.models import Distributor_Inventry, Distributor_Sale, Distributor_Sale_itemDetails
from django.core.exceptions import ObjectDoesNotExist,MultipleObjectsReturned
from django.shortcuts import HttpResponse
from django.contrib import messages
from datetime import date,timedelta
from mlm_admin.models import Sale, Sale_itemDetails
from shop.models import Material_center, Product, Batch

# This function is used in new inventory calculation
def remove_multiple_inventory(date, product, batch, mc):
    ln_keep = Distributor_Inventry.objects.filter(created_on=date,
                                                  product=product,
                                                  batch=batch,
                                                  material_center=mc)
    # AG :: Deleting additional rows (cleaning data)
    z = 0
    for i in ln_keep:
        # Keep first entry and remove other
        z += 1
        if z != 1:
            i.delete()


def fast_cron_run():
    today = date.today()
    yesterday = today - timedelta(days=1)
    # update_inventry(yesterday, today, True)
    update_inventry()

def cron_run():
    today = date.today()
    yesterday = today - timedelta(days = 1)
    # update_inventry(yesterday, today)
    update_inventry()
    # inventries = Distributor_Inventry.objects.filter(created_on = yesterday)
    # for inventry in inventries:
    #     try:
    #         query = Distributor_Inventry.objects.get(product = inventry.product,batch = inventry.batch,material_center = inventry.material_center,
    #         created_on = today)
    #     except ObjectDoesNotExist:
    #         query = Distributor_Inventry(product = inventry.product,batch = inventry.batch,material_center = inventry.material_center,purchase_price = inventry.purchase_price,
    #                  opening_quantity = inventry.current_quantity,current_quantity = inventry.current_quantity,
    #                  )
    #         query.save()

def update_inventory_fn(i, check, date, today):
    opening_quantity, quantity_in, quantity_out, current_quantity = 0, 0, 0, 0

    # Let's calculate the total today sale inventry (calculate out quantity)
    sales = Distributor_Sale.objects.filter(
        material_center=i.material_center,
        created_on=date,
        delete=False,
        order__delete=False
    ).exclude(order__status=8)
    for sale in sales:
        sale_item = sale.distributor_sale_itemdetails_set.filter(item=i.product, batch=i.batch)
        for s in sale_item:
            quantity_out += int(s.quantity)

    # Let's calculate the total today purchase inventry (calculate in quantity)
    purchases = Sale.objects.filter(
        material_center_to=i.material_center,
        accepted_date=date,
        sale_itemdetails__item=i.product,
        sale_itemdetails__batch=i.batch,
        accept=True,
        delete=False
    )
    for purchase in purchases:
        purchase_item = purchase.sale_itemdetails_set.filter(item=i.product, batch=i.batch)
        for pur in purchase_item:
            quantity_in += int(pur.quantity)

    ''' Here I am using previous opening quantity (i.opening_quantity) because I am adding 
    and substracting again quantity_out and quantity_in'''
    if today:
        opening_quantity = int(i.current_quantity)
    else:
        opening_quantity = int(i.opening_quantity)
    current_quantity = opening_quantity - quantity_out + quantity_in

    for ch in check:
        myid = ch.pk

    return opening_quantity, quantity_in, quantity_out, current_quantity, myid


def update_inventry():
    from .new_inventory_calculation import calculate_distributor_inventory
    # delta = end_date - start_date
    all_mc = Material_center.objects.filter(delete=False)
    Distributor_Inventry.objects.all().delete()
    # all_mc = Material_center.objects.filter(id=20, delete=False)
    all_product = Product.objects.all()
    # if not fast:
    #     previous_inventry = Distributor_Inventry.objects.filter(created_on=previous, created_on__gte=start_date, created_on__lte = end_date).delete()
    # for i in range(delta.days + 1):
    #     date = start_date + timedelta(days= i)
    #     print("Cron is cleaning data and creating rows for date:", date)
    #     previous = date - timedelta(days = 1)
    #     day_before = previous - timedelta(days = 1)
    #     # day_before_inventry = Distributor_Inventry.objects.filter(created_on=day_before,)
    for mc in all_mc:
        for product in all_product:
            all_batch = Batch.objects.filter(product=product)
            for batch in all_batch:
                calculate_distributor_inventory(product=product,
                                                batch=batch,
                                                material_center=mc,
                                                quantity=0,
                                                fast = True
                                            )
    # for i in range(delta.days + 1):
    #     date = start_date + timedelta(days= i)
    #     print("Cron is cleaning data and creating rows for date:", date)
    #     previous = date - timedelta(days = 1)
        # day_before = previous - timedelta(days = 1)
        # day_before_inventry = Distributor_Inventry.objects.filter(created_on=day_before,)
        # if not fast:
        #     previous_inventry = Distributor_Inventry.objects.filter(created_on = previous,).delete()


        # AG :: Check if any transaction (Purchase/Sale) exists for the previous date for a material center
        # If transaction exists, then create empty entries for that date + mc + product + batch
        # # list = [previous,date]
        # date_to_be_taken = previous
        # # for date_to_be_taken in list:
        # if 1==1:
        # for mc in all_mc:
        #     for product in all_product:
        #         all_batch = Batch.objects.filter(product=product, delete=False)
        #         for batch in all_batch:
        #             # if fast:
        #             calculate_distributor_inventory(product=product,
        #                                             batch=batch,
        #                                             material_center=mc,
        #                                             quantity=0,
        #                                             fast = True
        #                                             )
    #                 else:
    #                     # AG :: If inventory table has entry related to the current date + mc + product + batch, then we will not do anything.
    #                     previous_inventry_detail = Distributor_Inventry.objects.filter(product = product,
    #                                                                                    batch = batch,
    #                                                                                    material_center = mc,
    #                                                                                    created_on = previous,)

    #                     # Else we will check for inventory entry a day before.
    #                     if not previous_inventry_detail.exists():
    #                         day_before_inventry_detail = Distributor_Inventry.objects.filter(product = product,
    #                                                                                    batch = batch,
    #                                                                                    material_center = mc,
    #                                                                                    created_on = day_before,)

    #                         # If inventory entry is there a day before then we will copy that row to the current date row.
    #                         if day_before_inventry_detail.exists():
    #                             day_before_inventry_detail = day_before_inventry_detail[0]
    #                             entry_created = Distributor_Inventry.objects.update_or_create(created_on=previous,
    #                                                                                product=product,
    #                                                                                batch=batch,
    #                                                                                material_center=mc,
    #                                                                                defaults={
    #                                                                                    'product': product,
    #                                                                                    'batch': batch,
    #                                                                                    'material_center': mc,
    #                                                                                    'purchase_price': day_before_inventry_detail.purchase_price,
    #                                                                                    'opening_quantity': day_before_inventry_detail.current_quantity,
    #                                                                                    'current_quantity': day_before_inventry_detail.current_quantity,
    #                                                                                    'quantity_in': 0,
    #                                                                                    'quantity_out': 0,
    #                                                                                    'created_on': previous,
    #                                                                                }
    #                                                                                )

    #                         # If inventory row is not previously found, then we will check for transaction on current date + mc + product + batch
    #                         else:
    #                             mc_purchases = Sale.objects.filter(
    #                                 material_center_to=mc,
    #                                 accepted_date=previous,
    #                                 accept=True,
    #                                 delete=False,
    #                             )

    #                             for purchase in mc_purchases:
    #                                 # Create entries for each product if there are any purchases
    #                                 purchase_line_items = Sale_itemDetails.objects.filter(sale=purchase)
    #                                 for line_item in purchase_line_items:
    #                                     try:
    #                                         ln = Distributor_Inventry.objects.update_or_create(created_on = previous,
    #                                                                                            product = product,
    #                                                                                            batch = batch,
    #                                                                                            material_center = mc,
    #                                                                                            defaults = {
    #                                                                                                'product' : product,
    #                                                                                                'batch' : batch,
    #                                                                                                'material_center' : mc,
    #                                                                                                'created_on' : previous,
    #                                                                                                    }
    #                                                                                            )
    #                                     # AG :: In case we get more than 1 object, we will leave only 1.
    #                                     except MultipleObjectsReturned:
    #                                         remove_multiple_inventory(previous, product, batch, mc)

    #                             mc_sales = Distributor_Sale.objects.filter(
    #                                 material_center=mc,
    #                                 created_on=previous,
    #                                 delete=False,
    #                                 order__delete=False,
    #                             ).exclude(order__status=8)

    #                             for sale in mc_sales:
    #                                 # Create entries for each product if there are any purchases
    #                                 sale_line_items = Distributor_Sale_itemDetails.objects.filter(sale=sale)
    #                                 for line_item in sale_line_items:
    #                                     try:
    #                                         ln = Distributor_Inventry.objects.update_or_create(created_on=previous,
    #                                                                                            product=product,
    #                                                                                            batch=batch,
    #                                                                                            material_center=mc,
    #                                                                                            defaults={
    #                                                                                                'product': product,
    #                                                                                                'batch': batch,
    #                                                                                                'material_center': mc,
    #                                                                                                'created_on': previous,
    #                                                                                            }
    #                                                                                            )
    #                                     except MultipleObjectsReturned:
    #                                         remove_multiple_inventory(previous, product, batch, mc)

    #         # AG :: Rebuilding code check concludes
    # if not fast:
    #     for i in range(delta.days + 1):
    #         date = start_date + timedelta(days=i)
    #         print("Cron is building for date:", date)
    #         previous = date - timedelta(days=1)
    #         day_before = previous - timedelta(days=1)
    #         # day_before_inventry = Distributor_Inventry.objects.filter(created_on=day_before,)
    #         previous_inventry = Distributor_Inventry.objects.filter(created_on=previous,)
    #         select_date_inventry = Distributor_Inventry.objects.filter(created_on=date,)

    #         for i in previous_inventry:
    #             check = select_date_inventry.filter(product = i.product,batch = i.batch,material_center = i.material_center)
    #             if check:
    #                 # AG:: First we will correct previous day inventory if required
    #                 opening_quantity, quantity_in, quantity_out, current_quantity, myid = update_inventory_fn(i, check, previous, False)
    #                 Distributor_Inventry.objects.filter(created_on=previous,
    #                                                     product=i.product,
    #                                                     batch=i.batch,
    #                                                     material_center=i.material_center, ).update(
    #                                                                             purchase_price=i.purchase_price,
    #                                                                             opening_quantity=opening_quantity,  # i.current_quantity
    #                                                                             current_quantity=current_quantity,  # i.current_quantity
    #                                                                             quantity_in=quantity_in,  # 0
    #                                                                             quantity_out=quantity_out,  # 0
    #                                                                         )

    #                 # AG:: Then we will correct previous day inventory
    #                 new_i = previous_inventry.filter(product = i.product,batch = i.batch,material_center = i.material_center, created_on = previous)[0]
    #                 opening_quantity, quantity_in, quantity_out, current_quantity, myid = update_inventory_fn(new_i, check, date, True)
    #                 Distributor_Inventry.objects.filter(pk=myid).update(
    #                                                 # product=i.product,
    #                                                 # batch=i.batch,
    #                                                 # material_center=i.material_center,
    #                                                 # purchase_price=i.purchase_price,
    #                                                 quantity_in=quantity_in,
    #                                                 quantity_out=quantity_out,
    #                                                 current_quantity=current_quantity,
    #                                                 opening_quantity=opening_quantity
    #                                             )
    #             else:
    #                 inventry = Distributor_Inventry(
    #                     product = i.product,
    #                     batch = i.batch,
    #                     material_center = i.material_center,
    #                     purchase_price = i.purchase_price,
    #                     opening_quantity = i.current_quantity,
    #                     current_quantity = i.current_quantity,
    #                     quantity_in = 0,
    #                     quantity_out = 0,
    #                     created_on = date
    #                 )
    #                 inventry.save()

    #     # AG :: Cleanup - If nothing in inventory row, then we will remove that row
    # clean_inventory = Distributor_Inventry.objects.filter(opening_quantity = 0, current_quantity = 0, quantity_in = 0, quantity_out = 0).delete()


# def cron_runtest():
#     today = date.today()
#     yesterday = today - timedelta(days = 1)
#     inventries = Inventry.objects.filter(created_on = yesterday)
#     print(inventries,'here is the inventries')
#     for inventry in inventries:
#         try:
#             query_set = Inventry.objects.get(product = inventry.product,batch = inventry.batch,material_center = inventry.material_center,created_on = today)
#         except MultipleObjectsReturned:
#             print('we are geting multiple object of same quantity')
#         except ObjectDoesNotExist:
#             # query = Inventry(product = inventry.product,batch = inventry.batch,material_center = inventry.material_center,purchase_price = inventry.purchase_price,
#             #          opening_quantity = inventry.current_quantity,current_quantity = inventry.current_quantity,
#             #          )
#             print('Object  does not exist')
#             # query.save()
#
# def cron_manu(request):
#     cron_runtest()
#     return HttpResponse('<h1>evvery thing is fine</h1>')



# cron_run()