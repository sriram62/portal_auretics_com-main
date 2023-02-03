from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin
from import_export import resources
# asdmin.site.register(Product)


# # Register your models here.
class PincodeResources(resources.ModelResource):
    class Meta:
        model = Pincode


class PincodeAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['pincode', 'city']
    search_fields = ('pincode', 'city',)
    pin_resource = PincodeResources


class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'product_name', 'price', 'quantity', 'purchase_price', 'mrp', 'delete']
    search_fields = ('id', 'product_name', 'price', 'quantity', 'purchase_price', 'mrp', 'delete',)


class OrderAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id','name', 'email', 'date', 'paid']
    search_fields = ('id', 'name', 'email', 'date', 'paid',)


class OrderItemAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'price', 'discount_price', 'quantity', 'product', 'in_stock']
    search_fields = ('id', 'price', 'discount_price', 'quantity', 'product', 'in_stock',)


class LineItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'price', 'quantity', 'date_added', 'order', 'pv', 'bv']
    search_fields = ('id', 'price', 'quantity', 'date_added', 'order', 'pv', 'bv',)


class StateAdmin(admin.ModelAdmin):
    list_display = ['id', 'state_name']
    search_fields = ('id', 'state_name',)


class GenderAdmin(admin.ModelAdmin):
    list_display = ['id', 'gender_name']
    search_fields = ('id', 'gender_name',)


class BrandAdmin(admin.ModelAdmin):
    list_display = ['id', 'brand_name']
    search_fields = ('id', 'brand_name',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'cat_name', 'is_parent_category', 'commission', 'status', 'descount',
                    'cat_order', 'imag_path', 'delete']
    search_fields = ('id', 'cat_name', 'is_parent_category', 'commission', 'status', 'descount',
                     'cat_order', 'imag_path', 'delete',)


class BatchAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'batch_name', 'mrp', 'quantity', 'pv', 'bv']
    search_fields = ('id', 'product', 'batch_name', 'mrp', 'quantity', 'pv', 'bv')


class MaterialAdmin(admin.ModelAdmin):
    list_display = ['id', 'advisor_registration_number', 'mc_name']
    search_fields = ('id', 'advisor_registration_number',)


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', ]
    search_fields = ('id', )


admin.site.register(Payment, PaymentAdmin)
admin.site.register(AdminState, StateAdmin)
admin.site.register(Gender, GenderAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(CartItem, OrderItemAdmin)
admin.site.register(LineItem, LineItemAdmin)
admin.site.register(Batch, BatchAdmin)
admin.site.register(Material_center, MaterialAdmin)
admin.site.register(Ship_Charge)
admin.site.register(State)
admin.site.register(Pincode, PincodeAdmin)
