import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from mlm_admin.models import Sheet_config
from shop.models import Order, LineItem, Material_center
from accounts.models import Profile

# pip install gspread oauth2client
class SendToGS:
	"""docstring for SendToGS"""
	def __init__(self, verbose=False):
		self.verbose = verbose
		obj = Sheet_config.objects.filter(type='service_account')
		self.data = obj.values()[0]
		self.cred_json = self.get_json()
		self.worksheet = self.auth_sheet()

	def verbose_out(self, data):
		if self.verbose:
			print(json.dumps(data, indent=3))

	def get_json(self):
		json = {}
		for k, v in self.data.items():
			if k not in ['id', 'workbook_name', 'sheet_name']:
				json[k] = v.replace('\\n', '\n')
		return json

	def auth_sheet(self):
		scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',
		"https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
		creds = ServiceAccountCredentials.from_json_keyfile_dict(self.cred_json, scope)
		client = gspread.authorize(creds)
		spreadsheet  = client.open(self.data['workbook_name'])
		worksheet = spreadsheet.worksheet(self.data['sheet_name'])
		return worksheet

	def make_paylod(self, order):
		mc = Material_center.objects.get(mc_type="Delhivery")
		user = Profile.objects.get(email=order.shipping_address.user.username)
		data = {}
		data["Date"] = order.accept_date.isoformat()
		data["AWB"] = order.shipping_tracking_id
		data["Consignee Name"] = user.first_name + user.last_name
		data["City"] = order.shipping_address.city
		data["State"] = order.shipping_address.state.state_name
		data["Country"] = "India"
		data["Address"] = str(
			order.shipping_address.house_number +', '+ order.shipping_address.address_line) or str(
			order.billing_address.house_number +', '+ order.billing_address.address_line)
		data["Pincode"] = order.shipping_address.pin
		data["Mobile"] = order.shipping_address.mobile or oredr.billing_address.mobile
		data["Weight"] = str(order.shipment_weight * 1000)+" kg"
		data["Length"] = order.shipment_length
		data["Breadth"] = order.shipment_width
		data["Height"] = order.shipment_height
		data["Payment Mode"] = 'prepaid'
		data["Package Amount"] = order.grand_total
		data["Shipping Mode"] = mc.address
		data["Return Address"] = mc.address
		data["Return Pin"] = mc.pin_code
		data["fragile_shipment"] = "Surface 2"
		data["Mobile No."] = mc.mobile
		data["Seller CST No"] = mc.mc_name
		self.verbose_out(data)
		headers = self.worksheet.row_values(1)
		insert_data = []
		for i in headers:
			ci = i.strip()
			if ci in data:
				d = data[ci] or ""
				insert_data.append(d)
			else:
				insert_data.append('')
		return insert_data

	def send(self, order):
		payload = self.make_paylod(order)
		str_list = list(filter(None, self.worksheet.col_values(1)))
		self.worksheet.insert_row(payload, len(str_list)+1)
		self.verbose_out({'status' :'Success'})
		return {'status' :'Success'}


if __name__ == '__main__':
	order = Order.objects.get(id='9598')
	test = SendToGS(verbose=True)
	test.send(order)