from django.contrib.auth.models import User
from django.db import models
from mlm_admin.models import *


# Create your models here.
class ivr_user_created(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class ivr_logs(models.Model):
    '''
    bc = before cleanup
    ac = after cleanup
    '''
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    get_req = models.CharField(max_length=100000, default='')
    callsid = models.CharField(max_length=1000, default='')
    mynumber_bc = models.CharField(max_length=255, default='')
    myupline_bc = models.CharField(max_length=255, default='')
    CurrentTime_bc = models.CharField(max_length=255, default='')
    mynumber_ac = models.CharField(max_length=255, default='')
    myupline_ac = models.CharField(max_length=255, default='')
    CurrentTime_ac = models.CharField(max_length=255, default='')
    date_mismatch_error = models.BooleanField(default=False)
    mynumber_mismatch_error = models.BooleanField(default=False)
    myupline_mismatch_error = models.BooleanField(default=False)
    user_already_exist_error = models.BooleanField(default=False)
    sponsor_does_not_exist_error = models.BooleanField(default=False)
    user_created_successfully = models.BooleanField(default=False)
    user_not_created_error = models.BooleanField(default=False)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class ivr_check_logs(models.Model):
    '''
    bc = before cleanup
    ac = after cleanup
    '''
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    get_req = models.CharField(max_length=100000, default='')
    callsid = models.CharField(max_length=1000, default='')
    mynumber_bc = models.CharField(max_length=255, default='')
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)