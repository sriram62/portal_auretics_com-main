from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from .models import *

# Register your models here.


class team_building_super(ImportExportModelAdmin, admin.ModelAdmin):
    list_display =['id', 'user', 'input_date','cm_no_of_new_advisor_in_left_position_referred','cm_no_of_new_advisor_in_right_position_referred','created_on','total_no_of_new_advisor_in_left_position',
                   'total_no_of_new_advisor_in_right_position']
    search_fields=('id', 'user', 'input_date','cm_no_of_new_advisor_in_left_position_referred','cm_no_of_new_advisor_in_right_position_referred','created_on','total_no_of_new_advisor_in_left_position',
                   'total_no_of_new_advisor_in_right_position',)
class title_qualification(ImportExportModelAdmin, admin.ModelAdmin):
    list_display =['id', 'user', 'date_model','calculation_stage','ppv','accumulated_ppv','pbv','accumulated_pbv','super_ppv','super_pbv','infinity_ppv',
                   'infinity_pbv']
    search_fields=('id', 'user', 'date_model','calculation_stage','ppv','accumulated_ppv','pbv','accumulated_pbv','super_ppv','super_pbv','infinity_ppv',
                   'infinity_pbv',)
class direct_bonus_super(ImportExportModelAdmin, admin.ModelAdmin):
    list_display =['id', 'user', 'input_date','calculation_stage','no_of_user_referred','direct_bonus_earned','direct_bonus_paid','direct_bonus_balance_payable','draft_date',
                   'public_date']
    search_fields=('id', 'user', 'input_date','calculation_stage','no_of_user_referred','direct_bonus_earned','direct_bonus_paid','direct_bonus_balance_payable','draft_date',
                   'public_date',)
class dynamic_compression_activeAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display =['id', 'user', 'input_date','calculation_stage','referral',
                   'draft_date',
                   'public_date']
    search_fields=('id', 'user', 'input_date','calculation_stage','referral',
                   'draft_date',
                   'public_date',)
admin.site.register(configurations)
admin.site.register(weekly_distributor)
admin.site.register(monthly_distributor)
admin.site.register(weekly_material)
admin.site.register(monthly_material)
admin.site.register(super_model)
admin.site.register(infinity_model)
admin.site.register(inner_configurations)
admin.site.register(team_building_bonus_super_plan_model,team_building_super)
admin.site.register(title_qualification_calculation_model,title_qualification)
admin.site.register(direct_bonus_super_plan_model,direct_bonus_super)
admin.site.register(dynamic_compression_active,dynamic_compression_activeAdmin)
admin.site.register(dynamic_compression_director)
@admin.register(leadership_building_bonus_super_plan_model)
class leader_ship_super_planAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display =['id', 'user', 'input_date','calculation_stage','draft_date',
                   'public_date']

@admin.register(life_style_fund_super_plan_model)
class life_styleAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display =['id', 'user', 'input_date','calculation_stage','leadership_building_bonus_earned','life_style_fund_earned','draft_date',
                   'public_date']
@admin.register(personal_bonus)
class PersonalAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display =['id', 'user', 'input_date','calculation_stage','draft_date',
                   'public_date']
@admin.register(retail_margin)
class DirectAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display =['id', 'user', 'input_date','calculation_stage','draft_date',
                   'public_date']
@admin.register(fortune_bonus)
class FortuneAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display =['id', 'user', 'input_date','calculation_stage','draft_date',
                   'public_date']
@admin.register(sharing_bonus)
class SharingAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display =['id', 'user', 'input_date','calculation_stage','draft_date',
                   'public_date']
@admin.register(nuturing_bonus)
class NuturingAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display =['id', 'user', 'input_date','calculation_stage','draft_date',
                   'public_date']
@admin.register(business_master_bonus)
class BusinessAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display =['id', 'user', 'input_date','calculation_stage','draft_date',
                   'public_date']
@admin.register(consistent_retailers_income)
class ConsistentAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display =['id', 'user', 'input_date','calculation_stage','draft_date',
                   'public_date']
@admin.register(vacation_fund)
class VacationAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display =['id', 'user', 'input_date','calculation_stage','draft_date',
                   'public_date']
@admin.register(automobile_fund)
class AutomobileAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display =['id', 'user', 'input_date','calculation_stage','draft_date',
                   'public_date']
@admin.register(shelter_fund)
class ShelterAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display =['id', 'user', 'input_date','calculation_stage','draft_date',
                   'public_date']

# @admin.register(Qualification)
# class life_styleAdmin(admin.ModelAdmin):
#     list_display =['id', 'name']
