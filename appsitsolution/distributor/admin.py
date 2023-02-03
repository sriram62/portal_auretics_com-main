from django.contrib import admin

# Register your models here.
from .models import *



class D_BatchAdmin(admin.ModelAdmin):
    list_display =['id', 'batch', 'distributor_material_center','quantity','created_on']
    search_fields=('id', 'batch', 'distributor_material_center','quantity','created_on',)
class D_InventoryAdmin(admin.ModelAdmin):
    list_display =['id', 'product', 'batch','material_center','purchase_price','opening_quantity','current_quantity','quantity_in','quantity_out','created_on']
    search_fields=('id', 'product', 'batch','material_center','purchase_price','opening_quantity','current_quantity','quantity_in','quantity_out','created_on',)


# admin.site.register(Distributor_Batch,D_BatchAdmin)
admin.site.register(Distributor_Inventry,D_InventoryAdmin)
admin.site.register(Distributor_Sale)
admin.site.register(Distributor_Sale_itemDetails)
