import requests
import json
from portal_auretics_com.settings import pickrr_api
from shop.models import Order, LineItem, Material_center
from accounts.models import Profile

class PickrrApi:
	def __init__(self, verbose=False):
		self.verbose = verbose
		self.token = pickrr_api

	def verbose_out(self, data):
		if self.verbose:
			print(json.dumps(data, indent=3))

	def track_order(self, awb_no):
		resp = requests.get('https://async.pickrr.com/track/tracking/',
			params={'tracking_id':awb_no}).json()
		self.verbose_out(resp)
		return resp

	def cancel_order(self, awb_no):
		resp = requests.post('https://pickrr.com/api/order-cancellation/',
			data=json.dumps({'tracking_id':awb_no,'auth_token':self.token})).json()
		self.verbose_out(resp)
		return resp

	def make_item_list(self, order):
		product_list = []
		sku_counter = 111
		line_items = LineItem.objects.filter(order = order)
		for item in line_items:
			product = {}
			product['name'] = str(item.product)
			if item.product.product_code is not None:
				product['sku'] = item.product.product_code
			else:
				product['sku'] = sku_counter
				sku_counter += 1
			product['quantity'] = item.quantity
			product['price'] = float(item.price)
			product_list.append(product)

		return product_list

	def make_payload(self, order):
		try:
			mc = Material_center.objects.get(mc_type="Delhivery")
			user = Profile.objects.get(email=order.shipping_address.user.username)
			line_items = LineItem.objects.filter(order = order)
			pd_desc = (''.join(str(i.product)+', ' for i in line_items))[:-2]
			item_list =  self.make_item_list(order) 
			payload = {"auth_token": self.token}
			payload["item_name"] = pd_desc
			payload["item_list"] = item_list
			payload["from_name"] = mc.mc_name
			payload["from_phone_number"] = mc.mobile
			payload["from_address"] = mc.address
			payload["from_pincode"] = mc.pin_code
			# payload["pickup_gstin"] = mc.gst_number
			payload["to_name"] = user.first_name + user.last_name
			# payload["to_email"] = user.email
			payload["to_phone_number"] = order.shipping_address.mobile or order.billing_address.mobile
			payload["to_pincode"] = order.shipping_address.pin or order.billing_address.pin
			payload["to_address"] = str(
				order.shipping_address.house_number +', '+ order.shipping_address.address_line) or str(
				order.billing_address.house_number +', '+ order.billing_address.address_line)
			payload["quantity"] = len(item_list)
			payload["invoice_value"] = (order.grand_total - order.shiping_charge)
			payload["cod_amount"] = 0
			payload["is_reverse"] = False
			payload["item_breadth"] = order.shipment_width
			payload["item_length"] = order.shipment_length
			payload["item_height"] = order.shipment_height
			payload["item_weight"] = order.shipment_weight
			payload["invoice_number"] = str(order.order_id1)
			payload["total_discount"] = 0
			payload["shipping_charge"] = order.shiping_charge
			payload["transaction_charge"] = 0
			payload["giftwrap_charge"] = 0
			payload['has_surface'] = True
			payload['next_day_delivery'] = False
			self.verbose_out(payload)
			return payload
		except:
			return {}

	def create_order(self, order):
		payload = self.make_payload(order)
		resp = requests.post('https://pickrr.com/api/place-order/', data=json.dumps(payload))
		self.verbose_out(resp.json())
		self.verbose_out(resp.status_code)
		return resp.status_code, resp.json()

if __name__ == '__main__':
	order = Order.objects.get(id='9598')
	test = PickrrApi(verbose=True)
	test.create_order(order)
