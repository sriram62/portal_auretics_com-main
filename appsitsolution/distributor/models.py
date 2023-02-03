# Create your models here.
from django.db import models
from django.utils.timezone import now

from shop.models import *
from datetime import datetime


# Create your models here.

# class Distributor_Batch(models.Model):
#     batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
#     distributor_material_center = models.ForeignKey(Material_center, on_delete=models.CASCADE)
#     quantity = models.IntegerField(default=0)
#     created_on = models.DateField(auto_now_add=True)
#     date_modified = models.DateTimeField(auto_now=True, blank=True)
#     date_published = models.DateTimeField(auto_now_add=True, blank=True)


class Distributor_Inventry(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch,on_delete=models.CASCADE)
    material_center = models.ForeignKey(Material_center,on_delete=models.CASCADE)
    purchase_price = models.FloatField(default=0)
    opening_quantity = models.IntegerField(default=0)
    current_quantity = models.IntegerField(default=0)
    quantity_in = models.IntegerField(default=0)
    quantity_out = models.IntegerField(default=0)
    created_on = models.DateField(default=now)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        unique_together = ('batch', 'material_center', 'created_on')

    # lets override the save function here
    def save(self, *args, **kwargs):
        batch_obj = self.batch
        product_obj = self.product
        BatchObj = Batch.objects.get(id=batch_obj.id)
        if BatchObj.product.id == product_obj.id:
        # if BatchObj.batch_number == "NB11":
            super(Distributor_Inventry, self).save(*args, **kwargs)
        else:
            #TBD: add this error on database
            raise Exception("Batch and product are not matching")


class Distributor_Sale(models.Model):
    sale_user_id = models.ForeignKey(User,null=True,on_delete=models.CASCADE,related_name='D_sale_user')
    material_center =  models.ForeignKey(Material_center, on_delete =models.CASCADE,related_name='D_material_center')
    advisor_distributor_name =  models.ForeignKey(User, on_delete =models.CASCADE)
    date = models.DateField(null=True,blank=True)
    narration = models.TextField(null=True,blank=True)
    sale_type = models.IntegerField(default=0)
    party_name = models.TextField(null=True,blank=True)
    grand_total = models.FloatField(default=0)
    grand_pv = models.FloatField(null=True,blank=True,default=0)
    grand_bv = models.FloatField(null=True,blank=True,default=0)
    created_on = models.DateField(auto_now_add=True)
    delete = models.BooleanField(default=False)
    accept = models.BooleanField(default=False)
    order = models.ForeignKey(Order,null=True,on_delete=models.CASCADE)
    payment_mode = models.CharField(max_length=100, null=True,blank=True)
    is_loyalty_sale = models.BooleanField(default=False)
    is_partial_loyalty_sale = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)
    is_pending = models.BooleanField(default=False)
    was_there_calculation_issue_in_li = models.BooleanField(default=False)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    def subtotal(self):
        total = 0
        data = Distributor_Sale_itemDetails.objects.filter(sale = self).values('quantity','distributor_price')
        for i in data:
            total += i['quantity'] * i['distributor_price']
        return total
    def total(self):
        total = 0
        data = Distributor_Sale_itemDetails.objects.filter(sale = self).values('total_amount')
        for i in data:
            total += i['total_amount']
        return total
    def cgst_amount(self):
        total_amount = 0
        data = Distributor_Sale_itemDetails.objects.filter(sale = self)
        for i in data:
            cgst = i.quantity * i.cgst
            total_amount += cgst
        return total_amount
    def sgst_amount(self):
        total_amount = 0
        data = Distributor_Sale_itemDetails.objects.filter(sale = self)
        for i in data:
            sgst = i.quantity * i.sgst
            total_amount += sgst
        return total_amount
    def igst_amount(self):
        total_amount = 0
        data = Distributor_Sale_itemDetails.objects.filter(sale = self)
        for i in data:
            igst = i.quantity * i.igst
            total_amount += igst
        return total_amount
    # def __str__(self):
    #     return str(self.party_name)

class Distributor_Sale_itemDetails(models.Model):
    item = models.ForeignKey(Product,on_delete=models.CASCADE)
    sale = models.ForeignKey(Distributor_Sale,on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch,on_delete=models.CASCADE)
    quantity = models.IntegerField(null=True,blank=True)
    distributor_price = models.FloatField(null=True,blank=True)
    cgst = models.FloatField(null=True,blank=True)
    sgst = models.FloatField(null=True,blank=True)
    igst = models.FloatField(null=True,blank=True)
    vat = models.FloatField(null=True,blank=True)
    total_amount = models.FloatField(null=True,blank=True)
    pv_total = models.FloatField(null=True,blank=True, default=0)
    bv_total = models.FloatField(null=True,blank=True, default=0)
    was_there_calculation_issue_in_li = models.BooleanField(default=False)
    was_there_calculation_issue_in_grand_total = models.BooleanField(default=False)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    def total_cgst(self):
        return self.quantity * self.cgst

    def total_sgst(self):
        return self.quantity * self.sgst

    def total_igst(self):
        return self.quantity * self.igst
    def per_igst(self):
        igst = (100 * self.igst) / self.distributor_price
        igst = round(igst,2)
        igst = "{:.2f}".format(igst)
        return igst
    def per_sgst(self):
        sgst = (100 * self.sgst)/self.distributor_price
        sgst = round(sgst,2)
        sgst = "{:.2f}".format(sgst)
        return sgst
    def per_cgst(self):
        cgst = (100 * self.cgst)/self.distributor_price
        cgst = round(cgst,2)
        cgst = "{:.2f}".format(cgst)
        return cgst

    # lets override the save function here
    def save(self, *args, **kwargs):
        batch_obj = self.batch
        product_obj = self.item
        BatchObj = Batch.objects.get(id=batch_obj.id)
        if BatchObj.product.id == product_obj.id:
            super(Distributor_Sale_itemDetails, self).save(*args, **kwargs)
        else:
            #TBD: add this error on database
            raise Exception("Batch and product are not matching. Try cleaning data using mlm_admin remove_unlinked_product_batch utility.")

