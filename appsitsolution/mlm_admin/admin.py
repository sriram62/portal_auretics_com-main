from django.contrib import admin
from shop.models import *
from .models import *
# Register your models here.

class InventryAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'batch','material_center', 'purchase_price','opening_quantity','current_quantity','quantity_in','quantity_out','created_on', ]
    search_fields = ('id', 'product', 'batch','material_center', 'purchase_price','opening_quantity','current_quantity','quantity_in','quantity_out','created_on',)

class SaleItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'item', 'sale', 'batch','quantity','distributor_price','cgst','sgst','igst','vat','total_amount', ]
    search_fields = ('id', 'item', 'sale', 'batch','quantity','distributor_price','cgst','sgst','igst','vat','total_amount',)

class PurchaseItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'item', 'purchase', 'batch','quantity','price','cgst','sgst','igst','vat','total_amount',]
    search_fields = ('id', 'item', 'purchase', 'batch','quantity','price','cgst','sgst','igst','vat','total_amount',)

class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['id', 'material_name', 'grand_total']
    search_fields = ('id', 'material_name', 'grand_total',)

class SaleAdmin(admin.ModelAdmin):
    list_display = ['id','party_name', 'material_center_to','material_center_from','advisor_distributor_name','grand_total' ]
    search_fields = ('id','party_name', 'material_center_to','material_center_from','advisor_distributor_name','grand_total',)

class ManualVerificationAdmin(admin.ModelAdmin):
    list_display = ['id','kyc_user', 'pan_number','date','verified' ]
    search_fields= ('id','kyc_user', 'pan_number', 'date')

class KycDoneAdmin(admin.ModelAdmin):
    list_display = ['id','kyc_user','kyc_verification_type']
    search_fields= ['id','kyc_user','kyc_verification_type']
admin.site.register(Banner)
admin.site.register(Product_Variant)
admin.site.register(Purchase,PurchaseAdmin)
admin.site.register(item_details,PurchaseItemAdmin)
admin.site.register(Sale,SaleAdmin)
admin.site.register(Sale_itemDetails,SaleItemAdmin)
admin.site.register(Inventry,InventryAdmin)
admin.site.register(ManualVerification,ManualVerificationAdmin)
admin.site.register(KycDone,KycDoneAdmin)