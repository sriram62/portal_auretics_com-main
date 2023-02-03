from django.contrib import admin

# Register your models here.
from .models import *


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'email', 'phone_number', 'referral_id', 'reference_user_id','super_bv']
    search_fields=('id', 'first_name', 'email', 'phone_number', 'referral_id', 'reference_user_id','super_bv',)
class ReferalAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'referal_id', 'referral_code', 'referal_by','status','position','parent_id']
    search_fields=('id', 'user_id__id', 'referal_id', 'referral_code', 'referal_by__id','status','position','parent_id__id',)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'house_number', 'address_line', 'Landmark','city','default']
    search_fields=('id', 'user__id', 'house_number', 'address_line', 'Landmark','city','default',)

admin.site.register(Customer)

admin.site.register(Profile,ProfileAdmin)
admin.site.register(User_Check)
admin.site.register(ReferralCode,ReferalAdmin)
admin.site.register(Address,AddressAdmin)
admin.site.register(Kyc)
admin.site.register(BankAccountDetails)
admin.site.register(menu_permission)