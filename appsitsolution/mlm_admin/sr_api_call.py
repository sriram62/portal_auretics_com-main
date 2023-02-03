import json
import requests

from shop.models import Order, LineItem
from accounts.models import Profile
from inspect import currentframe, getframeinfo
from portal_auretics_com import settings



"""
For test create order

{
  "order_id": "224-447",
  "order_date": "2021-07-24 11:11",
  "pickup_location": "Jammu",
  "channel_id": "",
  "comment": "Reseller: M/s Goku",
  "billing_customer_name": "Naruto",
  "billing_last_name": "Uzumaki",
  "billing_address": "House 221B, Leaf Village",
  "billing_address_2": "Near Hokage House",
  "billing_city": "New Delhi",
  "billing_pincode": "110002",
  "billing_state": "Delhi",
  "billing_country": "India",
  "billing_email": "naruto@uzumaki.com",
  "billing_phone": "9876543210",
  "shipping_is_billing": true,
    "phone_verified": 1,
                "id": 1321935,
                "pickup_location": "Primary",
                "address": "Plot No. 190, Old Block Near LIC Colony",
                "address_2": "Mangal Bazar Road, Dilshad Garden",
                "city": "East Delhi",
                "email": "dispatch@auretics.com",
                "phone": "9999112999",
                "seller_name": "Auretics Limited",
                "state": "Delhi",
                "country": "India",
                "status": 1,
                "pin_code": "110095",
                "lat": "28.681264",
                "long": "77.331113",
  "order_items": [
    {
      "name": "Kunai",
      "sku": "chakra123",
      "units": 10,
      "selling_price": "900",
      "discount": "",
      "tax": "",
      "hsn": 441122
    }
  ],
  "payment_method": "Prepaid",
  "shipping_charges": 0,
  "giftwrap_charges": 0,
  "transaction_charges": 0,
  "total_discount": 0,
  "sub_total": 9000,
  "length": 10,
  "breadth": 15,
  "height": 20,
  "weight": 2.5
} 

"""

def get_address(order):
	payload = {}
	if order.billing_address is not None:
		print("Reached:" + str(getframeinfo(currentframe()).lineno))
		try:
			payload['billing_customer_name'] = Profile.objects.get(email=order.billing_address.user.username).first_name
		except:
			payload['billing_customer_name'] = order.billing_address.user.username
		try:
			payload['billing_last_name'] = Profile.objects.get(email=order.billing_address.user.username).last_name
		except:
			payload['billing_last_name'] = ""
		payload['billing_address'] = str(order.billing_address.house_number) + ", " + str(order.billing_address.address_line)
		payload['billing_address_2'] = str(order.billing_address.Landmark) + ", " + str(order.billing_address.street)
		payload['billing_city'] = order.billing_address.city
		payload['billing_pincode'] = order.billing_address.pin
		try:
			payload['billing_state'] = order.billing_address.state.state_name
		except:
			try:
				payload['billing_state'] = order.shipping_address.state.state_name
			except:
				payload['billing_state'] = " "
		payload['billing_country'] = order.billing_address.country.name
		try:
			payload['billing_email'] = order.email
		except:
			payload['billing_email'] = order.billing_address.user.username
		payload['billing_phone'] = order.billing_address.mobile
		try:
			print(len(order.billing_address.alternate_mobile))
			if len(order.billing_address.alternate_mobile) == 10:
				payload['billing_alternate_phone'] = order.billing_address.alternate_mobile
		except:
			pass
	elif order.shipping_address is not None:
		print("Reached:" + str(getframeinfo(currentframe()).lineno))
		print("Profile Object is:")
		print(Profile.objects.get(email=order.shipping_address.user.username).first_name)
		try:
			payload['billing_customer_name'] = Profile.objects.get(
				email=order.shipping_address.user.username).first_name
		except:
			payload['billing_customer_name'] = order.shipping_address.user.username
		try:
			payload['billing_last_name'] = Profile.objects.get(email=order.shipping_address.user.username).last_name
		except:
			payload['billing_last_name'] = ""
		payload['billing_address'] = str(order.shipping_address.house_number) + ", " + str(
			order.shipping_address.address_line)
		payload['billing_address_2'] = str(order.shipping_address.Landmark) + ", " + str(order.shipping_address.street)
		payload['billing_city'] = order.shipping_address.city
		payload['billing_pincode'] = order.shipping_address.pin
		try:
			payload['billing_state'] = order.shipping_address.state.state_name
		except:
			try:
				payload['billing_state'] = order.billing_address.state.state_name
			except:
				payload['billing_state'] = " "
		payload['billing_country'] = order.shipping_address.country.name
		try:
			payload['billing_email'] = order.email
		except:
			payload['billing_email'] = order.shipping_address.user.username
		payload['billing_phone'] = order.shipping_address.mobile
		try:
			print(len(order.shipping_address.alternate_mobile))
			if len(order.shipping_address.alternate_mobile) == 10:
				payload['billing_alternate_phone'] = order.shipping_address.alternate_mobile
		except:
			pass
	else:
		print("Reached:" + str(getframeinfo(currentframe()).lineno))
		payload['billing_customer_name'] = " "
		payload['billing_last_name'] = " "
		payload['billing_address'] = " "
		payload['billing_address_2'] = " "
		payload['billing_city'] = " "
		payload['billing_pincode'] = " "
		payload['billing_state'] = " "
		payload['billing_country'] = " "
		payload['billing_email'] = " "
		payload['billing_phone'] = " "
	payload['shipping_is_billing'] = True
	if order.shipping_address is not None:
		print("Reached:" + str(getframeinfo(currentframe()).lineno))
		try:
			payload['shipping_customer_name'] = Profile.objects.get(
				email=order.shipping_address.user.username).first_name
		except:
			payload['shipping_customer_name'] = order.shipping_address.user.username
		try:
			payload['shipping_last_name'] = Profile.objects.get(email=order.shipping_address.user.username).last_name
		except:
			payload['shipping_last_name'] = ""
		payload['shipping_address'] = str(order.shipping_address.house_number) + ", " + str(
			order.shipping_address.address_line)
		payload['shipping_address_2'] = str(order.shipping_address.Landmark) + ", " + str(order.shipping_address.street)
		payload['shipping_city'] = order.shipping_address.city
		payload['shipping_pincode'] = order.shipping_address.pin
		payload['shipping_country'] = order.shipping_address.country.name
		try:
			payload['shipping_state'] = order.shipping_address.state.state_name
		except:
			try:
				payload['shipping_state'] = order.billing_address.state.state_name
			except:
				payload['shipping_state'] = "DELHI"
		try:
			payload['shipping_email'] = order.email
		except:
			payload['shipping_email'] = order.shipping_address.user.username
		payload['shipping_phone'] = order.shipping_address.mobile
	elif order.billing_address is not None:
		print("Reached:" + str(getframeinfo(currentframe()).lineno))
		try:
			payload['shipping_customer_name'] = Profile.objects.get(
				email=order.billing_address.user.username).first_name
		except:
			payload['shipping_customer_name'] = order.billing_address.user.username
		try:
			payload['shipping_last_name'] = Profile.objects.get(email=order.billing_address.user.username).last_name
		except:
			payload['shipping_last_name'] = ""
		payload['shipping_address'] = str(order.billing_address.house_number) + ", " + str(
			order.billing_address.address_line)
		payload['shipping_address_2'] = str(order.billing_address.Landmark) + ", " + str(order.billing_address.street)
		payload['shipping_city'] = order.billing_address.city
		payload['shipping_pincode'] = order.billing_address.pin
		payload['shipping_country'] = order.billing_address.country.name
		try:
			payload['shipping_state'] = order.billing_address.state.state_name
		except:
			try:
				payload['shipping_state'] = order.shipping_address.state.state_name
			except:
				payload['shipping_state'] = " "
		try:
			payload['shipping_email'] = order.email
		except:
			payload['shipping_email'] = order.billing_address.user.username
		payload['shipping_phone'] = order.billing_address.mobile
	else:
		print("Reached:" + str(getframeinfo(currentframe()).lineno))
		payload['shipping_customer_name'] = ""
		payload['shipping_last_name'] = ""
		payload['shipping_address'] = ""
		payload['shipping_address_2'] = ""
		payload['shipping_city'] = ""
		payload['shipping_pincode'] = ""
		payload['shipping_country'] = ""
		payload['shipping_state'] = ""
		payload['shipping_email'] = ""
		payload['shipping_phone'] = ""

	return payload

class OrderMaintain:
	def __init__(self):
		self.email = settings.shiprocket_api_user
		self.password = settings.shiprocket_api_pass
		self.token = ''
		self.channel_ids = []
		self.order = ''


	def set_token(self):
		headers = {'Content-Type': 'application/json'}
		url = 'https://apiv2.shiprocket.in/v1/external/auth/login'
		payload = {
			'email': self.email,
			'password': self.password
		}
		response = requests.post(
			url,
			headers = headers,
			json = payload
		)
		self.token = json.loads(response.text)['token']


	def get_channel_id(self):
		url = 'https://apiv2.shiprocket.in/v1/external/channels'
		headers = {
			'Content-Type': 'application/json',
			'Authorization': 'Bearer {}'.format(self.token)
		}
		response = requests.get(url, headers=headers)
		print(response.text)
		for channel in json.loads(response.text)['data']:
			self.channel_ids.append(channel['id'])


	def make_order_item_list(self, order):
		product_list = []
		sku_counter = 111
		line_items = LineItem.objects.filter(order = order)
		for item in line_items:
			product = {}

			print("item is:")
			print(str(item.product))
			# product['name'] = order.shipping_address.user.username
			product['name'] = str(item.product)
			if item.product.product_code is not None:
				product['sku'] = item.product.product_code
			else:
				product['sku'] = sku_counter
				sku_counter += 1
			product['units'] = item.quantity
			product['selling_price'] = float(item.price)
			product['discount'] = ""
			product['tax'] = item.product.igst
			if item.product.hsn_code is not None:
				product['hsn'] = item.product.hsn_code
			else:
				if item.product.igst == 12.0:
					product['hsn'] = 3004
				elif item.product.igst == 18.0:
					product['hsn'] = 3305
				elif item.product.igst == 5.0:
					product['hsn'] = 1701
				else:
					product['hsn'] = 1000

			product_list.append(product)

		return product_list


	def make_payload(self, order):
		try:
		# if 1==1:
			print("Reached:" + str(getframeinfo(currentframe()).lineno))
			payload = {}
			item_list = self.make_order_item_list(order)
			payload['order_id'] = order.order_id1
			payload['order_date'] = order.date.isoformat()
			payload['pickup_location'] = order.material_center.mc_name
			payload['channel_id'] = self.channel_ids[0]
			payload['comment'] = ""
			payload = {**payload, **get_address(order)}
			try:
				print("Reached:" + str(getframeinfo(currentframe()).lineno))
				payload['order_items'] = item_list
				print(item_list)
				payload['payment_method'] = "Prepaid"
				payload['shipping_charges'] = order.shiping_charge
				payload['giftwrap_charges'] =  0
				payload['transaction_charges'] =  0
				payload['total_discount'] =  0
				payload['sub_total'] = (order.grand_total - order.shiping_charge)
			except:
				print("Reached:" + str(getframeinfo(currentframe()).lineno))
				payload['order_items'] = "Multiple Items"
				payload['payment_method'] = "Prepaid"
				payload['shipping_charges'] = 0
				payload['giftwrap_charges'] =  0
				payload['transaction_charges'] =  0
				payload['total_discount'] =  0
				payload['sub_total'] = 100
			payload['length'] = order.shipment_length
			payload['breadth'] = order.shipment_width
			payload['height'] = order.shipment_height
			payload['weight'] = order.shipment_weight

			print("Reached:" + str(getframeinfo(currentframe()).lineno))
			print("payload is:")
			print(payload)
			return payload
		except:
			print("Reached:" + str(getframeinfo(currentframe()).lineno))
			print("ERROR occurred during make_payload")


	def post_order(self, order):
		url = 'https://apiv2.shiprocket.in/v1/external/orders/create/adhoc'
		headers = {
			'Content-Type': 'application/json',
			'Authorization': 'Bearer {}'.format(self.token)
		}
		payload = self.make_payload(order)
		response = requests.post(
			url,
			headers=headers,
			json=payload
		)


# 		{
#   "order_id": 16161616,
#   "shipment_id": 15151515,
#   "status": "NEW",
#   "status_code": 1,
#   "onboarding_completed_now": 0,
#   "awb_code": null,
#   "courier_company_id": null,
#   "courier_name": null
# }
		return json.loads(response.text)



    
	def track_order(self, sr_shipment_id):
		url = f'https://apiv2.shiprocket.in/v1/external/courier/track/shipment/{sr_shipment_id}'
		headers = {
			'Content-Type': 'application/json',
			'Authorization': 'Bearer {}'.format(self.token)
		}
		 
		response = requests.get(
			url,
			headers=headers 
		 
		)
		
		return json.loads(response.text)


     

if __name__ == "__main__":
	om = OrderMaintain()
	om.set_token()
	om.get_channel_id()
	om.post_order()
