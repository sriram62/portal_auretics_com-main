from django.db import models
from django.contrib.auth.models import User
from shop.models import Order, Material_center
from accounts.models import ReferralCode
from datetime import datetime


# Create your models here.

class AuditOrderNo(models.Model):
    date = models.DateTimeField(auto_now_add=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True, blank=True)
    last_order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class AuditOrderECom(models.Model):
    date = models.DateTimeField(auto_now_add=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True, blank=True)
    order_id = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    order_no = models.CharField(default='', max_length=200, null=True, blank=True)
    order_by_user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_referral_code = models.CharField(default='', max_length=200, null=True, blank=True)
    user_email = models.CharField(default='', max_length=200, null=True, blank=True)
    expected_dp = models.DecimalField(null=True, max_digits=200, decimal_places=2, default=0.00)
    actual_dp = models.DecimalField(null=True, max_digits=200, decimal_places=2, default=0.00)
    expected_pv = models.DecimalField(null=True, max_digits=200, decimal_places=2, default=0.00)
    expected_bv = models.DecimalField(null=True, max_digits=200, decimal_places=2, default=0.00)
    actual_pv = models.DecimalField(null=True, max_digits=200, decimal_places=2, default=0.00)
    actual_bv = models.DecimalField(null=True, max_digits=200, decimal_places=2, default=0.00)
    is_pv_allocated = models.BooleanField(default=False)
    is_bv_allocated = models.BooleanField(default=False)
    is_pv_same = models.BooleanField(default=False)
    is_bv_same = models.BooleanField(default=False)
    line_item_wise_details = models.TextField(null=True, blank=True, default="")
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class AuditOrderDistributor(models.Model):
    date = models.DateTimeField(auto_now_add=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True, blank=True)
    order_id_dist = models.ForeignKey(Order, related_name="order_id_dist", on_delete=models.SET_NULL, null=True, blank=True)
    order_no_dist = models.CharField(default='', max_length=200, null=True, blank=True)
    material_center = models.ForeignKey(Material_center, related_name="material_center_dist", on_delete=models.SET_NULL, null=True, blank=True)
    found_in_order = models.BooleanField(default=False)
    order_id_order = models.ForeignKey(Order, related_name="order_id_order", on_delete=models.SET_NULL, null=True, blank=True)
    order_no_order = models.CharField(default='', max_length=200, null=True, blank=True)
    order_by_user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_referral_code = models.CharField(default='', max_length=200, null=True, blank=True)
    user_email = models.CharField(default='', max_length=200, null=True, blank=True)
    expected_dp = models.DecimalField(null=True, max_digits=200, decimal_places=2, default=0.00)
    actual_dp = models.DecimalField(null=True, max_digits=200, decimal_places=2, default=0.00)
    expected_pv = models.DecimalField(null=True, max_digits=200, decimal_places=2, default=0.00)
    expected_bv = models.DecimalField(null=True, max_digits=200, decimal_places=2, default=0.00)
    actual_pv = models.DecimalField(null=True, max_digits=200, decimal_places=2, default=0.00)
    actual_bv = models.DecimalField(null=True, max_digits=200, decimal_places=2, default=0.00)
    is_pv_allocated = models.BooleanField(default=False)
    is_bv_allocated = models.BooleanField(default=False)
    is_pv_same = models.BooleanField(default=False)
    is_bv_same = models.BooleanField(default=False)
    is_there_line_item = models.BooleanField(default=False)
    line_item_wise_details = models.TextField(null=True, blank=True, default="")
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)
