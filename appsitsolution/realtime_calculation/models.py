from django.db import models
import django
from django.contrib.auth.models import User
from shop.models import Order
from accounts.models import ReferralCode, Position
from django.core.validators import MinValueValidator
from decimal import Decimal


class RealTimeOrder(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    last_order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    order_completed_till = models.ForeignKey(Order, related_name='order_completed_till', on_delete=models.SET_NULL, null=True, blank=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)
    
class RealTimeUser(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    last_user = models.ForeignKey(ReferralCode, on_delete=models.SET_NULL, null=True, blank=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

class RealTimeUserDetails(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(ReferralCode, on_delete=models.SET_NULL, null=True, blank=True)
    is_user_green = models.BooleanField(default=False)
    is_user_calculated = models.BooleanField(default=False)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

class RealTimeDetail(models.Model):
    user_id = models.ForeignKey(User, related_name='realtime_user', on_delete=models.CASCADE)
    date = models.DateTimeField(default=django.utils.timezone.now)
    date_now = models.DateTimeField(blank=True,default=django.utils.timezone.now)
    rt_year = models.DateTimeField(blank=True,default=django.utils.timezone.now)
    rt_ppv = models.DecimalField(null=True, max_digits=20, decimal_places=2,default=0.00)
    rt_pbv = models.DecimalField(null=True, max_digits=20, decimal_places=2,default=0.00)
    rt_user_super_ppv = models.DecimalField(null=True, max_digits=20, decimal_places=2,default=0.00)
    rt_user_super_pbv = models.DecimalField(null=True, max_digits=20, decimal_places=2,default=0.00)
    rt_user_infinity_ppv = models.DecimalField(null=True, max_digits=20, decimal_places=2,default=0.00)
    rt_user_infinity_pbv = models.DecimalField(null=True, max_digits=20, decimal_places=2,default=0.00)
    rt_left_pv_month = models.DecimalField(max_digits=20, decimal_places=2,default=0.00)
    rt_right_pv_month = models.DecimalField(max_digits=20, decimal_places=2,default=0.00)
    rt_gpv_month = models.DecimalField(max_digits=20, decimal_places=2,default=0.00)
    rt_left_bv_month = models.DecimalField(max_digits=20, decimal_places=2,default=0.00)
    rt_right_bv_month = models.DecimalField(max_digits=20, decimal_places=2,default=0.00)
    rt_left_dp_month = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    rt_right_dp_month = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    rt_gbv_month = models.DecimalField(max_digits=20, decimal_places=2,default=0.00)
    rt_tbv_month = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    rt_tpv_month = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    rt_tdp_month = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    rt_left_new_users_month = models.IntegerField(default=0)
    rt_right_new_users_month = models.IntegerField(default=0)
    rt_new_direct_sponsors_month = models.IntegerField(default=0)
    # rt_left_pv_till_date = models.DecimalField(max_digits=20, decimal_places=2,default=0.00)
    # rt_right_pv_till_date = models.DecimalField(max_digits=20, decimal_places=2,default=0.00)
    # rt_gpv_till_date = models.DecimalField(max_digits=20, decimal_places=2,default=0.00)
    # rt_left_bv_till_date = models.DecimalField(max_digits=20, decimal_places=2,default=0.00)
    # rt_right_bv_till_date = models.DecimalField(max_digits=20, decimal_places=2,default=0.00)
    # rt_gbv_till_date = models.DecimalField(max_digits=20, decimal_places=2,default=0.00)
    # rt_tbv_till_date = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    # rt_tpv_till_date = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    # rt_tdp_till_date = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    rt_left_new_users = models.IntegerField(default=0)
    rt_right_new_users = models.IntegerField(default=0)
    rt_new_direct_sponsors = models.IntegerField(default=0)
    rt_group_users = models.IntegerField(default=0)
    rt_group_users_month = models.IntegerField(default=0)
    rt_audit_case_1_pv = models.DecimalField(max_digits=20, decimal_places=2,default=0.00)
    rt_audit_case_2_pv = models.DecimalField(max_digits=20, decimal_places=2,default=0.00)
    rt_audit_case_3_infinity_pv = models.DecimalField(max_digits=20, decimal_places=2,default=0.00)
    rt_audit_case_3_super_pv = models.DecimalField(max_digits=20, decimal_places=2,default=0.00)
    rt_audit_case_4_pv = models.DecimalField(max_digits=20, decimal_places=2,default=0.00)
    rt_audit_case_1_bv = models.DecimalField(max_digits=20, decimal_places=2,default=0.00)
    rt_audit_case_2_bv = models.DecimalField(max_digits=20, decimal_places=2,default=0.00)
    rt_audit_case_3_infinity_bv = models.DecimalField(max_digits=20, decimal_places=2,default=0.00)
    rt_audit_case_3_super_bv = models.DecimalField(max_digits=20, decimal_places=2,default=0.00)
    rt_audit_case_4_bv = models.DecimalField(max_digits=20, decimal_places=2,default=0.00)
    user_highest_qualification = models.CharField(default='',max_length=200000,null=True,blank=True)
    rt_is_user_green = models.BooleanField(default=False)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return str(self.user_id)


class RealTimeOrderAudit(models.Model):
    date = models.DateTimeField(blank=True,default=django.utils.timezone.now)
    order_id =  models.ForeignKey(Order, on_delete=models.CASCADE)
    rt_calculation_done = models.BooleanField(default=False)
    is_stock_variance_order = models.BooleanField(default=False)
    date_now = models.DateTimeField(blank=True,default=django.utils.timezone.now)
    grand_total = models.FloatField(default=0)
    paid = models.BooleanField(default=False)
    delete = models.BooleanField(default=False)
    status = models.IntegerField(null=True)
    pv = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    bv = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class RealTimeAudit(models.Model):
    rt_order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    rt_order_user = models.ForeignKey(User, on_delete=models.CASCADE)
    rt_order_pv = models.DecimalField(max_digits=20, decimal_places=2,default=0.00)
    rt_pv_allocated_to_super = models.DecimalField(max_digits=20, decimal_places=2,default=0.00)
    rt_pv_allocated_to_left_of_top_id = models.DecimalField(max_digits=20, decimal_places=2,default=0.00)
    rt_pv_allocated_to_right_of_top_id = models.DecimalField(max_digits=20, decimal_places=2,default=0.00)
    rt_pv_allocated_to_no_position_of_top_id = models.DecimalField(max_digits=20, decimal_places=2,default=0.00)
    rt_pv_allocated_to_infinity = models.DecimalField(max_digits=20, decimal_places=2,default=0.00)
    rt_pv_allocated_to_gpv_of_top_id = models.DecimalField(max_digits=20, decimal_places=2,default=0.00)
    rt_order_bv = models.DecimalField(max_digits=20, decimal_places=2,default=0.00)
    rt_bv_allocated_to_super = models.DecimalField(max_digits=20, decimal_places=2,default=0.00)
    rt_bv_allocated_to_left_of_top_id = models.DecimalField(max_digits=20, decimal_places=2,default=0.00)
    rt_bv_allocated_to_right_of_top_id = models.DecimalField(max_digits=20, decimal_places=2,default=0.00)
    rt_bv_allocated_to_infinity = models.DecimalField(max_digits=20, decimal_places=2,default=0.00)
    rt_bv_allocated_to_gbv_of_top_id = models.DecimalField(max_digits=20, decimal_places=2,default=0.00)
    rt_bv_allocated_to_no_position_of_top_id = models.DecimalField(max_digits=20, decimal_places=2,default=0.00)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return str(self.rt_order_id)


class generation(models.Model):
    user = models.ForeignKey(User, related_name='gen_user', on_delete=models.CASCADE)
    upline = models.ForeignKey(User, related_name='gen_upline', on_delete=models.CASCADE)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        unique_together = ('user', 'upline')


class organisation(models.Model):
    user = models.ForeignKey(User, related_name='org_user', on_delete=models.CASCADE)
    parent = models.ForeignKey(User, related_name='org_parent', on_delete=models.CASCADE)
    position = models.CharField(max_length=20,choices=Position,default='LEFT')
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        unique_together = ('user', 'parent')

class execution_time(models.Model):
    date = models.DateTimeField(default=django.utils.timezone.now)
    create_structure = models.BooleanField(default=False)
    start_time_structure = models.DateTimeField(null=True,blank=True)
    end_time_structure = models.DateTimeField(null=True,blank=True)
    create_detail = models.BooleanField(default=False)
    create_detail_self = models.BooleanField(default=False)
    start_time_details_self = models.DateTimeField(null=True,blank=True)
    end_time_details_self = models.DateTimeField(null=True,blank=True)
    create_detail_down = models.BooleanField(default=False)
    start_time_details_down = models.DateTimeField(null=True,blank=True)
    end_time_details_down = models.DateTimeField(null=True,blank=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class InstantDetail(models.Model):
    user = models.ForeignKey(User, related_name='instant_user', on_delete=models.CASCADE)
    date = models.DateTimeField(default=django.utils.timezone.now)
    date_now = models.DateTimeField(blank=True,default=django.utils.timezone.now)
    rt_year = models.DateTimeField(blank=True, default=django.utils.timezone.now)
    rt_ppv = models.DecimalField(null=True, max_digits=200, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])
    rt_pbv = models.DecimalField(null=True, max_digits=200, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])
    rt_user_super_ppv = models.DecimalField(null=True, max_digits=200, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])
    rt_user_super_pbv = models.DecimalField(null=True, max_digits=200, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])
    rt_user_infinity_ppv = models.DecimalField(null=True, max_digits=200, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])
    rt_user_infinity_pbv = models.DecimalField(null=True, max_digits=200, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])
    rt_left_pv_month = models.DecimalField(max_digits=200, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])
    rt_left_bv_month = models.DecimalField(max_digits=200, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])
    rt_left_dp_month = models.DecimalField(max_digits=200, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])
    rt_right_pv_month = models.DecimalField(max_digits=200, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])
    rt_right_bv_month = models.DecimalField(max_digits=200, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])
    rt_right_dp_month = models.DecimalField(max_digits=200, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])
    rt_gpv_month = models.DecimalField(max_digits=200, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])
    rt_gbv_month = models.DecimalField(max_digits=200, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])
    gdp = models.DecimalField(max_digits=200, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])
    rt_tpv_month = models.DecimalField(max_digits=200, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])
    rt_tbv_month = models.DecimalField(max_digits=200, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])
    rt_tdp_month = models.DecimalField(max_digits=200, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])
    rt_left_new_users_month = models.IntegerField(default=0)
    rt_right_new_users_month = models.IntegerField(default=0)
    rt_new_direct_sponsors_month = models.IntegerField(default=0)
    group_users = models.IntegerField(default=0)
    left_new_users_pv = models.DecimalField(max_digits=200, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])
    right_new_users_pv = models.DecimalField(max_digits=200, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])
    new_direct_sponsors_pv = models.DecimalField(max_digits=200, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])
    left_new_users_bv = models.DecimalField(max_digits=200, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])
    right_new_users_bv = models.DecimalField(max_digits=200, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])
    new_direct_sponsors_bv = models.DecimalField(max_digits=200, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])
    left_new_users_dp = models.DecimalField(max_digits=200, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])
    right_new_users_dp = models.DecimalField(max_digits=200, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])
    new_direct_sponsors_dp = models.DecimalField(max_digits=200, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])
    rt_audit_case_1_pv = models.DecimalField(max_digits=200, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])
    rt_audit_case_2_pv = models.DecimalField(max_digits=200, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])
    rt_audit_case_3_infinity_pv = models.DecimalField(max_digits=200, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])
    rt_audit_case_3_super_pv = models.DecimalField(max_digits=200, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])
    rt_audit_case_4_pv = models.DecimalField(max_digits=200, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])
    rt_audit_case_1_bv = models.DecimalField(max_digits=200, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])
    rt_audit_case_2_bv = models.DecimalField(max_digits=200, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])
    rt_audit_case_3_infinity_bv = models.DecimalField(max_digits=200, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])
    rt_audit_case_3_super_bv = models.DecimalField(max_digits=200, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])
    rt_audit_case_4_bv = models.DecimalField(max_digits=200, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])
    user_highest_qualification = models.CharField(default='',max_length=200000,null=True,blank=True)
    rt_is_user_green = models.BooleanField(default=False)
    status = models.BooleanField(default=False)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return str(self.user_id)

    class Meta:
        unique_together = ('user', 'date')