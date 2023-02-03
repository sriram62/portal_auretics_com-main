from django_cron import CronJobBase, Schedule
from mlm_admin.dv_api import DelhiveryApi
from mlm_admin.pickrr_api import PickrrApi
from .models import *
from shop.models import Order, Material_center, Product, Batch

class ChechDeliveryStatus(CronJobBase):
    RUN_EVERY_MINS = 120 # every 2 hours
    RUN_AT_TIMES = ['8:30'] # run at 8:30 am

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS, run_at_times=RUN_AT_TIMES)
    code = 'mlm_admin.check_delivery_status' # a unique code

    def do(self):
        dv_orders = Order.objects.filter(status__in=[1,2,3], shipping_partner='Delhivery', shipping_tracking_id__isnull=False)
        for i in dv_orders:
            resp = DelhiveryApi().track_order(i.shipping_tracking_id)
            if resp['message'] == 'Success':
                resp_status = resp["data"][0]["status"]["status"]
                resp_inst = resp["data"][0]["status"]["instructions"]
                # print(i.status, resp_status, resp_inst)
                if resp_status == "WAITING_PICKUP" and 'cancelled' in resp_inst:
                    i.status = 2
                    i.save()
                    continue
                if resp_status == "NOT_PICKED" and resp_inst == "Shipment not received from client":
                    i.status = 2
                    i.save()
                    continue
                if resp_status == "WAITING_PICKUP" and i.status != 2:
                    i.status = 2
                    i.save()
                    continue
                if resp_status == "IN_TRANSIT" and i.status != 3:
                    i.status = 3
                    i.save()
                    continue
                if resp_status == "DELIVERED":
                    i.status = 4
                    i.save()
                    continue
        
        pkr_orders = Order.objects.filter(status__in=[1,2,3], shipping_partner='Pickrr', shipping_tracking_id__isnull=False)
        for i in pkr_orders:
            resp = PickrrApi().track_order(i.shipping_tracking_id)
            if "status" in resp:
                resp_status = resp["status"]["current_status_type"]
                if resp_status == "NDR":
                    i.status = 2
                    i.save()
                    continue
                if resp_status == "RTO":
                    i.status = 2
                    i.save()
                    continue
                if resp_status == "OC":
                    i.status = 2
                    i.save()
                    continue
                if resp_status == "PP" and i.status != 2:
                    i.status = 2
                    i.save()
                    continue
                if resp_status == "OT" and i.status != 3:
                    i.status = 3
                    i.save()
                    continue
                if resp_status == "DL":
                    i.status = 4
                    i.save()
                    continue


def update_inventry():
    from .new_inventory_calculation import calculate_mlm_inventory

    all_mc = Material_center.objects.filter(delete=False, advisory_owned='NO')
    Inventry.objects.all().delete()

    all_product = Product.objects.filter(delete=False,)

    for mc in all_mc:
        for product in all_product:
            all_batch = Batch.objects.filter(product=product, delete=False)
            for batch in all_batch:
                calculate_mlm_inventory(
                                        product=product,
                                        batch=batch,
                                        material_center=mc,
                                        quantity=0,
                                        fast = True
                                    )

                    


        