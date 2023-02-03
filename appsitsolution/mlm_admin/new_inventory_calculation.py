from .models import *
from shop.models import *
from datetime import datetime
from django.db.models import Sum


def calculate_mlm_inventory(**kwargs):
	total_sale_items_obj = Sale_itemDetails.objects.filter(
									batch= kwargs['batch'],
									item= kwargs['product'],
									sale__material_center_from = kwargs['material_center'],
									sale__delete= False
								).aggregate(Sum('quantity'))

	if total_sale_items_obj['quantity__sum'] is None:
		total_sale_items_obj['quantity__sum'] = 0

	ordersObj = LineItem.objects.filter(
		order__material_center = kwargs['material_center'],
		batch=kwargs['batch'],
		product=kwargs['product'],
		order__paid=True,
		order__delete=False,
	).exclude(order__status=8).aggregate(Sum('quantity'))

	if ordersObj['quantity__sum'] is None:
		ordersObj['quantity__sum'] = 0

	purchases = item_details.objects.filter(
			item= kwargs['product'],
			batch= kwargs['batch'],
			purchase__material_name= kwargs['material_center']
		).aggregate(Sum('quantity'))

	if purchases['quantity__sum'] is None:
		purchases['quantity__sum'] = 0

	quantity_out = total_sale_items_obj['quantity__sum'] + ordersObj['quantity__sum']

	current_quantity = purchases['quantity__sum'] - quantity_out

	inventory = Inventry.objects.update_or_create(
		batch= kwargs['batch'],
		material_center= kwargs['material_center'],
		defaults={
			'product' : kwargs['product'],
		    'batch' : kwargs['batch'],
		    'material_center' : kwargs['material_center'],
			'opening_quantity' : 0,
		    'current_quantity' : current_quantity,
		    'quantity_in' : 0,
			'quantity_out' : 0,
	}
	)
	# inventory.save()