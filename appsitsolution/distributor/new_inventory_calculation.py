from .models import *
from datetime import datetime
from django.db.models import Sum
from mlm_admin.models import *
from .cron import remove_multiple_inventory

def calculate_distributor_inventory(**kwargs):
	fast = False
	if 'fast' in kwargs:
		fast = kwargs['fast']

	total_sale_items_obj = {}
	try:
		total_sale_items_obj = Distributor_Sale_itemDetails.objects.filter(batch= kwargs['batch'],
													item= kwargs['product'],
													sale__material_center= kwargs['material_center'],
													sale__delete= False,
												).aggregate(Sum('quantity'))
	except:
		total_sale_items_obj['quantity__sum'] = 0

	if total_sale_items_obj['quantity__sum'] is None:
		total_sale_items_obj['quantity__sum'] = 0

	total_purchase_mlm_admin_sale_obj = {}
	try:
		total_purchase_mlm_admin_sale_obj = Sale_itemDetails.objects.filter(batch= kwargs['batch'],
													item= kwargs['product'],
													sale__material_center_to= kwargs['material_center'],
													sale__delete=False,
													sale__accept=True,
												).aggregate(Sum('quantity'))
	except:
		total_purchase_mlm_admin_sale_obj['quantity__sum'] = 0

	if total_purchase_mlm_admin_sale_obj['quantity__sum'] is None:
		total_purchase_mlm_admin_sale_obj['quantity__sum'] = 0

	try:
		current_quantity = total_purchase_mlm_admin_sale_obj['quantity__sum'] - (total_sale_items_obj['quantity__sum'] + int(kwargs['quantity']))
	except:
		raise Exception(f"Error: Current quantity for product {kwargs['product']} and batch {kwargs['batch']} is 0")

	if fast is False:
		if current_quantity < 0:
			raise Exception(f"Error: Current quantity for product {kwargs['product']} and batch {kwargs['batch']} is 0")

	if fast is True:
		try:
			D_inventory = Distributor_Inventry(
							product= kwargs['product'], 
							batch= kwargs['batch'], 
							material_center= kwargs['material_center'],
							opening_quantity= 0,
							current_quantity= current_quantity,
							quantity_in= 0,
							quantity_out= 0
						)
			D_inventory.save()
		except:
			pass

	else:
		try:
			today = datetime.now().date()

			try:
				D_inventory_update = Distributor_Inventry.objects.get(
										product= kwargs['product'],
										batch= kwargs['batch'],
										material_center= kwargs['material_center'],
										created_on= today
									)

			# AG :: Clean multiple entries
			except MultipleObjectsReturned:
				remove_multiple_inventory(today, kwargs['product'], kwargs['batch'], kwargs['material_center'])
				D_inventory_update = Distributor_Inventry.objects.get(
										product=kwargs['product'],
										batch=kwargs['batch'],
										material_center=kwargs['material_center'],
										created_on=today
									)

			Distributor_Inventry.objects.filter(
									product= kwargs['product'], 
									batch= kwargs['batch'], 
									material_center= kwargs['material_center'],
									created_on= today
								).update(
									current_quantity= current_quantity,
									# quantity_in= 0,
									quantity_out = D_inventory_update.quantity_out + int(kwargs['quantity']),
									# opening_quantity= current_quantity
								)
		except:
			
			D_inventory = Distributor_Inventry(
							product= kwargs['product'], 
							batch= kwargs['batch'], 
							material_center= kwargs['material_center'],
							opening_quantity= 0,
							current_quantity= current_quantity,
							quantity_in= 0,
							quantity_out= int(kwargs['quantity'])
						)
			D_inventory.save()