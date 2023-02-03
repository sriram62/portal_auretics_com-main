from .models import *
from datetime import datetime

def distributor_pending_purchase_inventry(**kwargs):
	try:
		today = datetime.now().date()
		D_inventory_update = Distributor_Inventry.objects.get(
								product= kwargs['product'], 
								batch= kwargs['batch'],
								material_center= kwargs['material_center'],
								created_on= today
							)
		D_inventory_update_current_quantity = int(D_inventory_update.current_quantity) + int(kwargs['quantity'])
		D_inventory_update_quantity_in = int(D_inventory_update.quantity_in) + int(kwargs['quantity'])
		Distributor_Inventry.objects.filter(
								product= kwargs['product'], 
								batch= kwargs['batch'], 
								material_center= kwargs['material_center'],
								created_on= today
							).update(
								current_quantity= D_inventory_update_current_quantity,
								quantity_in= D_inventory_update_quantity_in, 
								purchase_price= kwargs['batch_mrp']
							)
	except:
		try:
			D_inventory_update = Distributor_Inventry.objects.filter(
								product= kwargs['product'], 
								batch= kwargs['batch'],
								material_center= kwargs['material_center']
							).latest('created_on')
			D_current_quantity = int(D_inventory_update.current_quantity) + int(kwargs['quantity'])
			D_inventory = Distributor_Inventry(
								product= kwargs['product'], 
								batch= kwargs['batch'], 
								material_center= kwargs['material_center'],
								opening_quantity= D_inventory_update.opening_quantity,
								current_quantity= D_current_quantity,
								quantity_in= kwargs['quantity'], 
								purchase_price= kwargs['batch_mrp']
						)
			D_inventory.save()
		except:
			D_inventory = Distributor_Inventry(
							product= kwargs['product'], 
							batch= kwargs['batch'], 
							material_center= kwargs['material_center'],
							opening_quantity= 0, 
							current_quantity= kwargs['quantity'],
							quantity_in= kwargs['quantity'], 
							purchase_price= kwargs['batch_mrp']
						)
			D_inventory.save()

def distributor_add_sale_inventry(**kwargs):
	today = datetime.now().date()
	try:
		D_inventory_update = Distributor_Inventry.objects.get(
								product= kwargs['product'], 
								batch= kwargs['batch'],
								material_center= kwargs['material_center'],
								created_on= today
							)
		D_inventory_update_current_quantity = int(D_inventory_update.current_quantity) - int(kwargs['quantity'])
		D_inventory_update_quantity_out = int(D_inventory_update.quantity_out) + int(kwargs['quantity'])
		Distributor_Inventry.objects.filter(
								product= kwargs['product'], 
								batch= kwargs['batch'], 
								material_center= kwargs['material_center'],
								created_on= today
							).update(
								current_quantity=D_inventory_update_current_quantity,
								quantity_out=D_inventory_update_quantity_out
							)
	except:
		try:
			D_inventory_update = Distributor_Inventry.objects.filter(
								product= kwargs['product'], 
								batch= kwargs['batch'], 
								material_center= kwargs['material_center']
							).latest('created_on')
			
			current_quantity = int(D_inventory_update.current_quantity) + int(kwargs['quantity'])
			
			D_inventory = Distributor_Inventry(
								product= kwargs['product'], 
								batch= kwargs['batch'], 
								material_center= kwargs['material_center'],
								opening_quantity= D_inventory_update.opening_quantity,
								current_quantity= current_quantity,
								quantity_out= kwargs['quantity']
							)
			D_inventory.save()
		except:
			D_inventory = Distributor_Inventry(
								product= kwargs['product'], 
								batch= kwargs['batch'], 
								material_center= kwargs['material_center'],
								opening_quantity= 0, 
								current_quantity= kwargs['quantity'],
								quantity_out= kwargs['quantity']
							)
			D_inventory.save()


def distributor_delete_sale_inventry(**kwargs):
	today = datetime.now().date()
	update_time_inventry = Distributor_Inventry.objects.get(
					created_on= today,
					product= kwargs['product'],
					batch= kwargs['batch'],
					material_center= kwargs['material_center']
				)
	update_time_inventry_current_quantity = int(update_time_inventry.current_quantity) + int(kwargs['quantity'])
	update_time_inventry_quantity_out = int(update_time_inventry.quantity_out) - int(kwargs['quantity'])
	Distributor_Inventry.objects.filter(pk=update_time_inventry.pk).update(
		current_quantity=update_time_inventry_current_quantity,
		quantity_out=update_time_inventry_quantity_out
	)