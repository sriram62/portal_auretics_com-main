import requests
import json
from portal_auretics_com.settings import dl_url, dl_api, dl_client
from shop.models import Order, LineItem, Material_center
from accounts.models import Profile

class DelhiveryApi:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.url = dl_url
        self.token = dl_api

    def verbose_out(self, data):
        if self.verbose:
            print(json.dumps(data, indent=3))

    def check_pincode(self, pincode):
        resp = requests.get(self.url+'/c/api/pin-codes/json/',
            headers={'Authorization': self.token, 'Content-Type': 'application/json'}, params={'filter_codes':pincode}).json()
        self.verbose_out(resp)
        return resp

    def cancel_order(self, awb_no):
        try:
            headers = {'Authorization': 'Token '+self.token, 'Content-Type': 'application/json'}
            resp = requests.get(self.url+'/api/p/edit', headers=headers,
                data={"waybill": awb_no, "cancellation": "true"}).json()
            self.verbose_out(resp)
            return resp
        except Exception as err:
            return err

    def track_order(self, awb_no):
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "application/json, text/plain, */*", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate",
        "Referer": "https://www.delhivery.com/", "Origin": "https://www.delhivery.com", "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-site", "Te": "trailers"}
        resp = requests.get('https://dlv-web-api.delhivery.com:443/v3/track', headers=headers,
            params={'wbn':awb_no}).json()
        self.verbose_out(resp)
        return resp

    def make_payload(self, order):
        try:
            mc = Material_center.objects.get(mc_type="Delhivery")
            user = Profile.objects.get(email=order.shipping_address.user.username)
            line_items = LineItem.objects.filter(order = order)
            pd_desc = (''.join(str(i.product)+', ' for i in line_items))[:-2]
            data = {}
            pl = {} # pickup location details
            pl['name'] = mc.mc_name
            pl['add'] = mc.address
            pl["pin"] = mc.pin_code
            pl['city'] = mc.city
            pl['state'] = mc.state
            data['pickup_location'] = pl
            sp = {} # shipment details
            sp['client'] = dl_client
            sp["return_name"] = mc.mc_name
            sp["return_pin"] = mc.pin_code
            sp["return_city"] = mc.city
            sp["return_phone"] = mc.mobile
            sp["return_add"] = mc.address
            sp["return_state"] = mc.city
            sp["return_country"] = "India"
            sp['order'] = order.id
            sp['order_date'] = order.date.isoformat()
            sp['name'] = user.first_name + user.last_name
            sp['products_desc'] = pd_desc
            sp["shipping_mode"] = "Surface"
            sp['add'] = str(
                order.shipping_address.house_number +', '+ order.shipping_address.address_line) or str(
                order.billing_address.house_number +', '+ order.billing_address.address_line)
            sp['city'] = order.shipping_address.city
            sp['state'] = order.shipping_address.state.state_name
            sp['pin'] = order.shipping_address.pin
            sp['phone'] = order.shipping_address.mobile or order.billing_address.mobile
            sp['payment_mode'] = 'Prepaid'
            sp['total_amount'] = order.grand_total
            sp["cod_amount"] = "0"
            sp["shipment_height"] = order.shipment_height
            sp["shipment_width"] = order.shipment_width
            sp["shipment_length"] = order.shipment_length
            sp["weight"] = order.shipment_weight * 1000
            data['shipments'] = [sp]
            self.verbose_out(data)
            payload = "format=json&data="+json.dumps(data)
            return payload
        except:
            return {}

    def create_order(self, order):
        payload = self.make_payload(order)
        resp = requests.post(self.url+'/api/cmu/create.json', 
            headers={'Authorization': 'Token '+self.token, 'Content-Type': 'application/json'}, data=payload)
        self.verbose_out(resp.json())
        self.verbose_out(resp.status_code)
        return resp.status_code, resp.json()

if __name__ == '__main__':
    order = Order.objects.get(id='9598')
    test = DelhiveryApi(verbose=True)
    test.create_order(order)


