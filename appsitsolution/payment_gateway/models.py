from django.db import models
from datetime import datetime


class Gateway(models.Model):
    code = models.IntegerField(unique=True)
    name = models.CharField(max_length=30, unique=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True, null=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return "%s-%s" % (self.code, self.name)


class PaymentMode(models.Model):
    gateway = models.OneToOneField(Gateway, on_delete=models.CASCADE)
    priority = models.IntegerField(unique=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True, null=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        ordering = ('priority',)

    def __str__(self):
        return str(self.gateway)

