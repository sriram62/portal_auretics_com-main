import os
from datetime import time
from io import BytesIO

import PIL.Image
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.validators import RegexValidator
from django.utils.timezone import now
from django_resized import ResizedImageField

from shop.models import *
from shop.models import Batch

# Create your models here.
# phone validater
phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                             message="Phone number must be entered in the format: '9999999999'. Up to 15 digits allowed.")

Status = (
    ("Active", "Active"),
    ("InActive", "InActive"),)

ID_PROOF_TYPE_CHOICES = (
    ('Voter_ID', 'Voter ID'),
    ('Driving_License', 'Driving License'),
    ('Passport', 'Passport'),
    ('PAN', 'PAN'),
    ('Aadhar', 'Aadhar'),
)

ADDRESS_PROOF_TYPE_CHOICES = (
    ('Voter_ID', 'Voter ID'),
    ('Driving_License', 'Driving License'),
    ('Passport', 'Passport'),
    ('Aadhar', 'Aadhar'),
    ('Ration_Card', 'Ration Card'),
    ('Telephone_Bill', 'Telephone Bill'),
    ('Electricity_Bill', 'Electricity  Bill'),
    ('Gas_Connection_Bill', 'Gas Connection Bill'),
    ('Bank_Statement', 'Bank Statement'),
    ('Bank_Passbook', 'Bank Passbook')
)


class Purchase(models.Model):
    purchase_user_id = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='purchase_user')
    material_name = models.ForeignKey(Material_center, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    narration = models.TextField(null=True, blank=True)
    purchase_type = models.IntegerField(default=0)
    party_name = models.TextField(null=True, blank=True)
    grand_total = models.FloatField(default=0)
    created_on = models.DateField(auto_now_add=True)
    delete = models.BooleanField(default=False)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    # def __str__(self):
    #     return str(self.party_name)


class item_details(models.Model):
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    cgst = models.FloatField(null=True, blank=True)
    sgst = models.FloatField(null=True, blank=True)
    igst = models.FloatField(null=True, blank=True)
    vat = models.FloatField(null=True, blank=True)
    total_amount = models.FloatField(null=True, blank=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    # lets override the save function here
    def save(self, *args, **kwargs):
        batch_obj = self.batch
        product_obj = self.item
        BatchObj = Batch.objects.get(id=batch_obj.id)
        if BatchObj.product.id == product_obj.id:
            # if BatchObj.batch_number == "NB11":
            super(item_details, self).save(*args, **kwargs)
        else:
            # TBD: add this error on database
            raise Exception("Batch and product are not matching. Try cleaning data using mlm_admin remove_unlinked_product_batch utility.")


class Sale(models.Model):
    SALE_TO_DISTRIBUTOR = 'Distributor'
    SALE_TO_CNF = 'C&F'
    sale_user_id = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='sale_user')
    material_center_to = models.ForeignKey(Material_center, on_delete=models.CASCADE, related_name='material_center_to')
    material_center_from = models.ForeignKey(Material_center, on_delete=models.CASCADE,
                                             related_name='material_center_from')
    sale_to = models.CharField(max_length=20, choices=[(c, c) for c in [SALE_TO_DISTRIBUTOR, SALE_TO_CNF]],
                               default=SALE_TO_DISTRIBUTOR, null=True)
    advisor_distributor_name = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    advisor_cnf_name = models.ForeignKey(User, related_name='sales_as_cnf', on_delete=models.CASCADE, blank=True,
                                         null=True)
    date = models.DateField(null=True, blank=True)
    narration = models.TextField(null=True, blank=True)
    sale_type = models.IntegerField(default=0)
    party_name = models.TextField(null=True, blank=True)
    grand_total = models.FloatField(default=0)
    created_on = models.DateField(auto_now_add=True)
    delete = models.BooleanField(default=False)
    accept = models.BooleanField(default=False)
    accepted_date = models.DateField(null=True, blank=True)
    grand_pv = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    grand_bv = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    was_there_calculation_issue_in_li = models.BooleanField(default=False)
    was_there_calculation_issue_in_pv = models.BooleanField(default=False)
    was_there_calculation_issue_in_bv = models.BooleanField(default=False)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)
    # def __str__(self):
    #     return str(self.party_name)


class Sale_itemDetails(models.Model):
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=True, blank=True)
    distributor_price = models.FloatField(null=True, blank=True)
    cgst = models.FloatField(null=True, blank=True)
    sgst = models.FloatField(null=True, blank=True)
    igst = models.FloatField(null=True, blank=True)
    vat = models.FloatField(null=True, blank=True)
    pv = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    bv = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    total_amount = models.FloatField(null=True, blank=True)
    was_there_calculation_issue_in_li = models.BooleanField(default=False)
    was_there_calculation_issue_in_grand_total = models.BooleanField(default=False)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class Inventry(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    # <--------------------------------------19 feb change add material_center_to field this will help in distribution ------------------>
    material_center = models.ForeignKey(Material_center, on_delete=models.CASCADE)
    # <--------------------------------------19 feb change add material_center_to field this will help in distribution ------------------>
    purchase_price = models.FloatField(default=0)
    opening_quantity = models.IntegerField(default=0)
    current_quantity = models.IntegerField(default=0)
    quantity_in = models.IntegerField(default=0)
    quantity_out = models.IntegerField(default=0)
    created_on = models.DateField(default=now)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return str(self.batch) + str(self.material_center)

    class Meta:
        unique_together = ('batch', 'material_center', 'created_on')

    # lets override the save function here
    def save(self, *args, **kwargs):
        batch_obj = self.batch
        product_obj = self.product
        BatchObj = Batch.objects.get(id=batch_obj.id)
        if BatchObj.product.id == product_obj.id:
            # if BatchObj.batch_number == "NB11":
            super(Inventry, self).save(*args, **kwargs)
        else:
            # TBD: add this error on database
            raise Exception("Batch and product are not matching. Try cleaning data using mlm_admin remove_unlinked_product_batch utility.")


class ManualVerification(models.Model):
    kyc_user = models.OneToOneField(User, on_delete=models.CASCADE)
    pan_name = models.CharField(max_length=255, default='')
    pan_number = models.CharField(max_length=255, default='')
    pan_file = models.FileField(
        upload_to='pan_card/images',
        default='avatar.jpg',
        blank=True
    )
    id_proof_type = models.CharField(max_length=255, default='Voter_ID', choices=ID_PROOF_TYPE_CHOICES)
    id_proof_file = models.FileField(
        upload_to='id_proof/images',
        default='avatar.jpg',
        blank=True
    )
    address_proof_type = models.CharField(max_length=255, default='Voter_ID', choices=ADDRESS_PROOF_TYPE_CHOICES)
    address_proof_file = models.FileField(
        upload_to='address_proof/images',
        default='avatar.jpg',
        blank=True
    )

    date = models.DateField(auto_now_add=True, null=True)

    verified = models.BooleanField(default=False)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.kyc_user.username


@receiver(pre_save, sender=ManualVerification)
def send_manual_verificatin_notification_email(sender, instance, **kwargs):
    if instance.verified == "True":
        # contents = f"As a security measure, our payment processor requests a picture of the credit card covering the numbers except the last 4 with a piece of paper or other material. This will only be done one time.\n\n\nOrder Details\n\nOrder ID: {instance.order_id}\nStatus: {instance.order_status}\nTotal{instance.order_total}\n\n\nBilling Address\n\nUsername: {instance.user.username}\nAddress: {instance.Address1}\nMobile Phone: {instance.contact}\nZip Code: {instance.zipcode}\nEmail address: {instance.email}"
        sendsms("PAN Verification", user_mobile_number="+91" + str(instance.profile.phone_number),
                referee_name=(str(instance.profile.username)))

        contents = f"Auretics Admins verified your PAN Details \nPAN Details:\nUsernme: {instance.kyc_user.username}\nPan Number: {instance.pan_number}"
        send_mail("PAN Verification", contents, settings.EMAIL_HOST_USER,
                  [instance.kyc_user.email])


class KycDone(models.Model):
    type = (
        ("None", "None"),
        ("Manually", "Manually"),
        ("Signzy", "Signzy"),)

    kyc_user = models.OneToOneField(User, on_delete=models.CASCADE)
    kyc_verification_type = models.CharField(max_length=255, choices=type, default="None",
                                             verbose_name="Verification Type")
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.kyc_user.username


@receiver(pre_save, sender=ManualVerification)
def send_manual_verificatin_notification_email(sender, instance, **kwargs):
    if instance.verified == True:

        # contents = f"As a security measure, our payment processor requests a picture of the credit card covering the numbers except the last 4 with a piece of paper or other material. This will only be done one time.\n\n\nOrder Details\n\nOrder ID: {instance.order_id}\nStatus: {instance.order_status}\nTotal{instance.order_total}\n\n\nBilling Address\n\nUsername: {instance.user.username}\nAddress: {instance.Address1}\nMobile Phone: {instance.contact}\nZip Code: {instance.zipcode}\nEmail address: {instance.email}"
        sendsms("PAN Verification", user_mobile_number="+91" + str(instance.kyc_user.profile.phone_number),
                referee_name=(str(instance.kyc_user.username)))

        contents = f"Auretics Admins verified your PAN Details \nPAN Details:\nUsernme: {instance.kyc_user.username}\nPan Number: {instance.pan_number}"
        send_mail("PAN Verification ", contents, settings.EMAIL_HOST_USER,
                  [instance.kyc_user.email])

        try:
            kyc_done = KycDone.objects.get(kyc_user=instance.kyc_user)
        except:
            kyc_done = KycDone.objects.create(kyc_user=instance.kyc_user)

        kyc_done.kyc_verification_type = "Manually"
        kyc_done.save()


class ChangeMobileNumber(models.Model):
    # id = models.IntegerField(primary_key=True)
    date = models.DateTimeField(null=True)
    old_number = models.CharField(max_length=200, blank=True)
    new_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    user_name = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    change_by_user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='users')
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

class ChangeEmail(models.Model):
    # id = models.IntegerField(primary_key=True)
    date = models.DateTimeField(null=True)
    old_email = models.CharField(max_length=200, blank=True)
    new_email = models.EmailField(default='none@email.com')
    user_name = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    change_by_user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='users_by')
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

class Sheet_config(models.Model):
    type = models.CharField(max_length=500, default='', null=True, blank=True)
    project_id = models.CharField(max_length=500, default='', null=True, blank=True)
    private_key_id = models.CharField(max_length=500, default='', null=True, blank=True)
    private_key = models.TextField(max_length=2500, default='', null=True, blank=True)
    client_email = models.CharField(max_length=500, default='', null=True, blank=True)
    client_id = models.CharField(max_length=500, default='', null=True, blank=True)
    auth_uri = models.CharField(max_length=500, default='', null=True, blank=True)
    token_uri = models.CharField(max_length=500, default='', null=True, blank=True)
    auth_provider_x509_cert_url = models.CharField(max_length=500, default='', null=True, blank=True)
    client_x509_cert_url = models.CharField(max_length=500, default='', null=True, blank=True)
    workbook_name = models.CharField(max_length=500, default='', null=True, blank=True)
    sheet_name = models.CharField(max_length=500, default='', null=True, blank=True)


class Tds_calculation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.DateField()
    earning = models.DecimalField(max_digits=100, decimal_places=2)
    cum_earning = models.DecimalField(max_digits=100, decimal_places=2, default=0)
    tds = models.DecimalField(max_digits=100, decimal_places=2, default=0)
    tds_payable = models.DecimalField(max_digits=100, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=100, decimal_places=2, default=0)

    class Meta:
        unique_together = ('user', 'month')


class Greeting(models.Model):
    STATUS_CHOICES = (
        ("ACTIVE", "Active"),
        ("DRAFT", "Draft"),
        ("INACTIVE", "Inactive"),
    )

    USER_TYPES = (
        ('A', 'Active this Month'),
        ('B', 'Active last Month'),
        ('C', 'Ever Active'),
        ('D', 'All Green Users'),
        ('E', 'KYC Done'),
    )
    # TODO: Move to settings
    DEFAULT_THUMBNAIL_PATH = 'greeting_images/thumbnails/default_thumbnail.png'
    DEFAULT_IMAGE_PATH = 'greeting_images/default_greeting.png'

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=80)
    image = ResizedImageField(size=[1280, 1280], upload_to='greeting_images/', default=DEFAULT_IMAGE_PATH, blank=True)
    thumbnail = models.ImageField(upload_to='greeting_images/thumbnails/', editable=False,
                                  default=DEFAULT_THUMBNAIL_PATH)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="DRAFT")
    trigger_date = models.DateField()
    trigger_time = models.TimeField(default=time(hour=9))
    user_type = models.CharField(max_length=50, choices=USER_TYPES, default='A')
    # TODO: Arjun Gupta:: Define valid user_types in a class variable or make this foreign key
    created_on = models.DateTimeField(auto_now_add=True)

    # created_by = models.ForeignKey() # Should add user name or id

    # description = models.TextField(null=True, blank=True)
    # date_published = models.DateTimeField(auto_now_add=True, blank=True)
    # date_modified = models.DateTimeField(auto_now=True, blank=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):

        if not self.id:
            # If greeting is new
            if not self.create_thumbnail():
                self.thumbnail = self.DEFAULT_THUMBNAIL_PATH
                raise Exception('Could not create thumbnail - is the file type valid?')

        super().save(force_insert=False, force_update=False, using=None, update_fields=None)

    def create_thumbnail(self):
        image = PIL.Image.open(self.image)
        image.thumbnail(settings.GREETING_THUMBNAIL_SIZE, PIL.Image.ANTIALIAS)

        thumb_name, thumb_extension = os.path.splitext(self.image.name)
        thumb_extension = thumb_extension.lower()

        thumb_filename = thumb_name + '_thumb' + thumb_extension

        if thumb_extension in ['.jpg', '.jpeg']:
            FTYPE = 'JPEG'
        elif thumb_extension == '.png':
            FTYPE = 'PNG'
        # elif thumb_extension == '.gif':
        #     FTYPE = 'GIF'
        else:
            return False

        # Save thumbnail to in-memory file as StringIO
        temp_thumb = BytesIO()
        image.save(temp_thumb, FTYPE)
        temp_thumb.seek(0)

        # set save=False, otherwise it will run in an infinite loop
        print(thumb_filename)
        self.thumbnail.save(thumb_filename, ContentFile(temp_thumb.read()), save=False)
        temp_thumb.close()

        return True

    def __str__(self):
        return self.name


class BulkMessages(models.Model):
    sent_date = models.DateField()
    receiver_number = models.CharField(max_length=10)
    message = models.CharField(max_length=300)
    status = models.CharField(max_length=20)
    file_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.receiver_number


class WaConfiguration(models.Model):
    wassenger_token = models.CharField(max_length=250)
    queue_size = models.IntegerField(default=500)
