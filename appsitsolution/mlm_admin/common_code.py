from .models import *
from datetime import datetime


def calculateTodayInventry(**kwargs):
    today = datetime.now().date()
    inventory_update = Inventry.objects.get(
                            product= kwargs['product'], 
                            batch= kwargs['batch'],
                            material_center= kwargs['material_center'],
                            created_on=today
                        )
    inventory_update_current_quantity = int(inventory_update.current_quantity) - int(kwargs['quantity'])
    inventory_update_quantity_out = int(inventory_update.quantity_out) + int(kwargs['quantity'])
    Inventry.objects.filter(
        product=kwargs['product'], 
        batch=kwargs['batch'], 
        material_center=kwargs['material_center'],
        created_on=today
    ).update(
        current_quantity=inventory_update_current_quantity,
        quantity_out=inventory_update_quantity_out
    )

def updateInventry(**kwargs):
    inventory_update = Inventry.objects.filter(
        product=kwargs['product'], 
        batch=kwargs['batch'],
        material_center=kwargs['material_center']
    ).latest('created_on')
    current_quantity = int(inventory_update.current_quantity) + int(kwargs['quantity'])
    inventory = Inventry(
        product=kwargs['product'], 
        batch=kwargs['batch'], 
        material_center=kwargs['material_center'],
        opening_quantity=inventory_update.opening_quantity,
        current_quantity=current_quantity,
        quantity_out=kwargs['quantity']
    )
    inventory.save()

def addInventry(**kwargs):
    inventory = Inventry(
        product=kwargs['product'], 
        batch=kwargs['batch'], 
        material_center=kwargs['material_center'],
        opening_quantity=0,
        current_quantity=kwargs['quantity'],
        quantity_out=kwargs['quantity']
    )
    inventory.save()

def addPurchaseCalculateTodayInventry(**kwargs):
    today = datetime.now().date()
    inventory_update = Inventry.objects.get(
        product=kwargs['product'], 
        batch=kwargs['batch'], 
        material_center=kwargs['material_center'],
        created_on=today
    )
    inventory_update_current_quantity = int(inventory_update.current_quantity) + int(kwargs['quantity'])
    inventory_update_quantity_in = int(inventory_update.quantity_in) + int(kwargs['quantity'])
    Inventry.objects.filter(
        product=kwargs['product'], 
        batch=kwargs['batch'], 
        material_center=kwargs['material_center'],
        created_on=today
    ).update(
        current_quantity=inventory_update_current_quantity,
        quantity_in=inventory_update_quantity_in, purchase_price=kwargs['price']
    )

def addPurchaseUpdateInventry(**kwargs):
    inventory_update = Inventry.objects.filter(
        product=kwargs['product'], 
        batch=kwargs['batch'], 
        material_center=kwargs['material_center']
    ).latest('created_on')
    current_quantity = int(inventory_update.current_quantity) + int(kwargs['quantity'])
    inventory = Inventry(product=kwargs['product'], batch=kwargs['batch'], material_center=kwargs['material_center'],
                         opening_quantity=inventory_update.opening_quantity, current_quantity=current_quantity,
                         quantity_in=kwargs['quantity'], purchase_price=kwargs['price'])
    inventory.save()

def addPurchageAddInventry(**kwargs):
    inventory = Inventry(product=kwargs['product'], batch=kwargs['batch'], material_center=kwargs['material_center'],
                         opening_quantity=0, current_quantity=kwargs['quantity'],
                         quantity_in=kwargs['quantity'], purchase_price=kwargs['price'])
    inventory.save()


# def C_and_F_addPurchaseUpdateInventry(**kwargs):
#     inventory_update = Inventry.objects.filter(
#         product=kwargs['product'], 
#         batch=kwargs['batch'], 
#         material_center=kwargs['material_center']
#     ).latest('created_on')
#     current_quantity = int(inventory_update.current_quantity) + int(kwargs['quantity'])
#     inventory = Inventry(product=kwargs['product'], batch=kwargs['batch'], material_center=kwargs['material_center'],
#                          opening_quantity=inventory_update.opening_quantity, current_quantity=current_quantity,
#                          quantity_in=kwargs['quantity'], purchase_price=kwargs['price'])
#     inventory.save()

def calculateInventryForDelete(**kwargs):
    today = datetime.now().date()
    update_time_inventry = Inventry.objects.get(
        created_on=today, 
        product=kwargs['product'],
        batch=kwargs['batch'], 
        material_center=kwargs['material_center']
    )
    update_time_inventry_current_quantity = int(update_time_inventry.current_quantity) + int(kwargs['quantity'])
    update_time_inventry_quantity_out = int(update_time_inventry.quantity_out) - int(kwargs['quantity'])
    Inventry.objects.filter(
        created_on=today, 
        product=kwargs['product'], 
        batch=kwargs['batch'],
        material_center=kwargs['material_center']).update(
                    current_quantity=update_time_inventry_current_quantity,
                    quantity_out=update_time_inventry_quantity_out
    )