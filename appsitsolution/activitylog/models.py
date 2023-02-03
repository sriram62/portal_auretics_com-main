from django.db import models
from datetime import datetime

# Create your models here.
class UserLoginActivity(models.Model):
    # Login Status
    SUCCESS = 'S'
    FAILED = 'F'

    LOGIN_STATUS = ((SUCCESS, 'Success'),
                           (FAILED, 'Failed'))

    login_IP = models.GenericIPAddressField(null=True, blank=True)
    login_datetime = models.DateTimeField(auto_now=True)
    login_username = models.CharField(max_length=40, null=True, blank=True)
    status = models.CharField(max_length=1, default=SUCCESS, choices=LOGIN_STATUS, null=True, blank=True)
    user_agent_info = models.CharField(max_length=255)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        verbose_name = 'User login activity'
        verbose_name_plural = 'User login activities'
