import uuid

from django.contrib.auth.models import User
from numpy import char
import accounts.models
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django_countries.fields import CountryField
from django.utils import timezone
from .calculation import calculate_values
from datetime import datetime

expdate = (
    ("YES", "YES"),
    ("NO", "No"),)
stock_blance_status = (
    ("YES", "YES"),
    ("NO", "No"),)
purchase_status = (
    ("YES", "YES"),
    ("NO", "No"),)
consume_status = (
    ("YES", "YES"),
    ("NO", "No"),)
essential_status = (
    ("YES", "YES"),
    ("NO", "No"),)
advisory_status = (
    ("YES", "YES"),
    ("NO", "No"),)
bill_status = (
    ("YES", "YES"),
    ("NO", "No"),)
depot_status = (
    ("YES", "YES"),
    ("NO", "No"),)
cash_status = (
    ("YES", "YES"),
    (" NO", "No"),)
vanor_status = (
    ("Active", "Active"),
    ("Inactive", "Inactive"),)
material_status = (
    ("Active", "Active"),
    ("Inactive", "Inactive"),)
# cat_status =(
#     ("instock", "In Stock"),
#     ("potof", "Out Of Stock"), )
cat_status = (
    ("Active", "Active"),
    ("Inactive", "Inactive"),)
# prod_status =(
#     ("instock", "In Stock"),
#     ("potof", "Out Of Stock"), )
prod_status = (
    ("Active", "Active"),
    ("Inactive", "Inactive"),)

show_on_home_page_choces = (
    ("show", "Show"),
    ("notShow", "Not Show"),)

is_hide = (
    ("True", "True"),
    ("False", "False"),)

_parent_category = (
    ("yes", "Yes"),
    ("no", "No"),)

GENDER_CHOICES = (
    ('Not Applicable', 'Not Applicable'),
    ('men', 'men'),
    ('women', 'women'),
    ('boy', 'boy'),
    ('girl', 'girl'),
)

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)

SIZE_CHOICES = (
    (
        ('Not Applicable', 'Not Applicable'),
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL'),
        ('XXXL', 'XXXL'),
        ('Small', 'Small'),
        ('Medium', 'Medium'),
        ('Large', 'Large'),
        ('Extra Large', 'Extra Large'),
        ('Mini', 'Mini'),
        ('Normal', 'Normal'),
        ('Huge', 'Huge'),
        ('One Size', 'One Size'),
    )
)


# class Address(models.Model):
#     user = models.ForeignKey(User,
#                              on_delete=models.CASCADE)
#     street_address = models.CharField(max_length=100)
#     apartment_address = models.CharField(max_length=100)
#     country = CountryField(multiple=False)
#     zip = models.CharField(max_length=100)
#     address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
#     default = models.BooleanField(default=False)

#     def __str__(self):
#         return self.user.username

#     class Meta:
#         verbose_name_plural = 'Addresses'


class AdminState(models.Model):
    state_name = models.CharField(max_length=191, )
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.state_name


class State(models.Model):
    state_name = models.CharField(max_length=191, )
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    @classmethod
    def get_state_as_choices(cls):
        return [(i.pk, i.state_name) for i in cls.objects.all()]

    def get_advisor_owned_mc(self):
        # return self.associated_material_center.all().filter(advisory_owned='YES')
        return Material_center.objects.filter(state=self.state_name, advisory_owned='YES')

    def get_company_depot_mc(self):
        return self.associated_material_center.all().filter(company_depot='YES')

    def __str__(self):
        return self.state_name

    class Meta:
        ordering = ['state_name']


class Pincode(models.Model):
    pincode = models.IntegerField()
    city = models.CharField(max_length=100, blank=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    # state = models.ForeignKey(AdminState, on_delete=models.CASCADE, null=True)
    def __str__(self):
        # return '{} {}'.format(self.pincode, self.city)
        return '%s %s' % (self.pincode, self.city,)


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, default="")
    house_number = models.CharField(max_length=100, blank=True)
    address_line = models.CharField(max_length=1000)
    Landmark = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.ForeignKey(AdminState, on_delete=models.SET_NULL, blank=True, null=True)
    street = models.CharField(max_length=100, blank=True)
    country = CountryField(multiple=False, default='IN')
    pin = models.CharField(max_length=100, blank=True, default='100000')
    mobile = models.CharField(max_length=100, blank=True)
    alternate_mobile = models.CharField(max_length=100, blank=True)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES, default='B')
    default = models.BooleanField(default=False)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)
        
    def __str__(self):
        return self.name
    
    def get_short_address(self):
        for_name = self.name 
        if self.nickname:
            for_name = "{} | {},".format( self.nickname, for_name)

        return "{for_name} {line1}, {city}".format(
        for_name = for_name or "",
        line1 = self.address_line,
        city = self.city
        )

    def get_address(self):
        return f'{self.address_line} {self.Landmark} {self.city} {self.state} {self.pin}'

    class Meta:
        verbose_name_plural = 'Addresses'


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.code


class Gender(models.Model):
    gender_name = models.CharField(max_length=191, choices=GENDER_CHOICES, default="Not Applicable")
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.gender_name


class Brand(models.Model):
    brand_name = models.CharField(max_length=191, blank=True, default="nike")
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.brand_name


class Category(models.Model):
    # cat_id = models.AutoField(primary_key=True)
    cat_name = models.CharField(max_length=191)
    is_parent_category = models.CharField(max_length=191, choices=_parent_category, default="yes")
    parent_category_id = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    imag_path = models.ImageField(upload_to='category_images/', default='2.jpg')
    description = models.TextField(null=True, blank=True)
    commission = models.CharField(max_length=191, null=True, blank=True)
    show_on_home_page = models.CharField(max_length=8, choices=show_on_home_page_choces, default="show")
    status = models.CharField(max_length=8, choices=cat_status, default="Active", null=True, blank=True)
    cat_order = models.CharField(max_length=191)
    descount = models.CharField(max_length=191, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    delete = models.BooleanField(default=False)
    is_hide = models.CharField(max_length=8, choices=is_hide, default="False")
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.cat_name


# Create your models here.
class Product(models.Model):
    product_name = models.CharField(max_length=191)
    print_name = models.CharField(max_length=191)
    product_code = models.CharField(max_length=191, null=True, blank=True)
    name_in_accounting_software = models.CharField(max_length=191, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='categories', default=1)
    hsn_code = models.CharField(max_length=191, null=True, blank=True)
    cgst = models.FloatField(null=True, blank=True)
    sgst = models.FloatField(null=True, blank=True)
    igst = models.FloatField(null=True, blank=True)
    vat = models.FloatField(blank=True, null=True)
    distributor_price = models.FloatField()
    business_value = models.FloatField()
    point_value = models.FloatField()
    loyalty_purchase = models.CharField(max_length=8, choices=purchase_status, default='NO')
    loyalty_consume = models.CharField(max_length=8, choices=consume_status, default='NO')
    essential_product = models.CharField(max_length=8, choices=essential_status, default='NO')
    minimum_purchase_quantity = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    maintain_stock_balance = models.CharField(max_length=9, choices=stock_blance_status, default='NO')
    country_of_origin = models.CharField(max_length=191, null=True, blank=True)
    brand = models.CharField(max_length=191, null=True, blank=True)
    item_package_quantity = models.IntegerField(null=True, blank=True)
    ingredients = models.TextField(max_length=19100, null=True, blank=True)
    expiration_dated_product = models.CharField(max_length=191, choices=expdate, default='YES')
    colour = models.CharField(max_length=191, null=True, blank=True)
    size = models.CharField(max_length=100, default='Not Applicable', choices=SIZE_CHOICES)
    product_gender_name = models.ForeignKey(Gender, on_delete=models.CASCADE, related_name='product_gender_names',
                                            default='1', null=True, blank=True)
    material = models.CharField(max_length=191, null=True, blank=True)
    flavour = models.CharField(max_length=191, null=True, blank=True)
    weight = models.CharField(null=True, blank=True, max_length=100)
    model_number = models.CharField(max_length=191, null=True, blank=True)
    launch_date = models.DateField(null=True, blank=True)
    usage = models.TextField(null=True, blank=True)
    directions = models.TextField(null=True, blank=True)
    indications = models.TextField(null=True, blank=True)
    special_feature = models.TextField(null=True, blank=True)
    safety_warning = models.TextField(null=True, blank=True)
    length = models.CharField(null=True, blank=True, max_length=100)
    width = models.CharField(null=True, blank=True, max_length=100)
    height = models.CharField(null=True, blank=True, max_length=100)
    product_brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='product_brand', default='1',
                                      null=True, blank=True)
    image = models.ImageField(upload_to='products_images/', blank=True)
    image2 = models.ImageField(upload_to='products_images/', blank=True, null=True)
    image3 = models.ImageField(upload_to='products_images/', blank=True, null=True)
    image4 = models.ImageField(upload_to='products_images/', blank=True, null=True)
    image5 = models.ImageField(upload_to='products_images/', blank=True, null=True)
    image6 = models.ImageField(upload_to='products_images/', blank=True, null=True)
    image7 = models.ImageField(upload_to='products_images/', blank=True, null=True)
    image8 = models.ImageField(upload_to='products_images/', blank=True, null=True)
    image9 = models.ImageField(upload_to='products_images/', blank=True, null=True)
    image10 = models.ImageField(upload_to='products_images/', blank=True, null=True)
    price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, default=0)
    mrp = models.FloatField(default=0)
    slug = models.SlugField(max_length=1000)
    status = models.CharField(max_length=8, choices=prod_status, default="Active")
    quantity = models.IntegerField(default=0)
    purchase_price = models.FloatField(default=0)
    delete = models.BooleanField(default=False)
    main_variant = models.BooleanField(default=True)
    monthly_sales = models.IntegerField(default=1, blank=True, null=True)
    consumption_rate = models.DecimalField(max_digits=20, decimal_places=2, default=100.00)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.product_name

    def save(self, *args, **kwargs):
        if self.pk:
            resp = calculate_values(self)
            for batch_resp in resp:
                try:
                    Batch.objects.filter(id=batch_resp['batch'].id).update(pv=batch_resp['point_value'],
                                                                           bv=batch_resp['business_value'])
                except:
                    Batch.objects.filter(id=batch_resp['batch'].id).update(pv=0, bv=0)
        super(Product, self).save(*args, **kwargs)

    # def get_total_discount_item_price(self):
    #     return self.price * self.discount_price


class Product_Variant(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, null=True, blank=True)
    variant = models.CharField(max_length=10, default='NO')
    main_variant = models.CharField(max_length=10, default='YES')
    variant_name = models.CharField(null=True, blank=True, max_length=700)
    variant_based_on = models.CharField(null=True, blank=True, max_length=700, default='Other')
    variant_tag = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variant_tags', null=True,
                                    blank=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.product.product_name


# product Image part
# cart details
class CartItem(models.Model):
    # nipur code start
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    # nipur code end
    cart_id = models.CharField(max_length=50)
    log_cart_id = models.CharField(max_length=50, null=True, blank=True)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    # <-------------------------------------------------------------------------discount price 28feb----------------------------------------->
    discount_price = models.DecimalField(max_digits=20, decimal_places=2)
    business_value = models.FloatField(default=0.0)
    point_value = models.FloatField(default=0.0)
    # <-------------------------------------------------------------------------discount price 28feb----------------------------------------->
    quantity = models.IntegerField()
    date_added = models.DateTimeField(auto_now_add=True)
    in_stock = models.BooleanField(default=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    is_loyalty_purchase_cart = models.BooleanField(default=False)

    def __str__(self):
        return "{}:{}".format(self.product.product_name, self.id)

    def update_quantity(self, quantity):
        self.quantity = self.quantity + quantity
        self.save()

    # nipur code start
    def update_point_value(self):
        self.quantity = float(self.point_value) * float(self.quantity)
        self.save()

    def update_business_value(self):
        self.quantity = float(self.business_value) * float(self.quantity)
        self.save()

    def user_update(self, user):
        self.user = user
        self.save()

    def lg_cart_id(self, log_cart_id):
        self.log_cart_id = log_cart_id
        self.save()

    # nipur code end
    def mrp(self):
        return self.price

    def total_mrp(self):
        return self.mrp() * self.quantity

    def total_cost(self):
        return self.quantity * self.price

    # this is for discount price
    def total_discount_cost(self):
        return self.quantity * self.discount_price

    def total_bv(self):
        return self.quantity * self.business_value

    def total_pv(self):
        return self.quantity * self.point_value
    # this is for discount price


# order summery


class Material_center(models.Model):
    mc_name = models.CharField(max_length=191)
    print_name = models.CharField(max_length=191)
    associated_states = models.ManyToManyField(State, blank=True, related_name='associated_material_center')
    address = models.CharField(max_length=400)
    address_line_2 = models.CharField(max_length=400, null=True, blank=True)
    city = models.CharField(max_length=400)
    state = models.CharField(max_length=400)
    pin_code = models.CharField(max_length=100)
    mobile = models.CharField(max_length=50, null=True, blank=True, default=0)
    mc_type = models.CharField(max_length=50, null=True, blank=True, default='')
    gst_number = models.CharField(max_length=200, null=True, blank=True)
    company_depot = models.CharField(max_length=100, choices=depot_status, default="NO")
    billing_allowed = models.CharField(max_length=100, choices=bill_status, default="YES")
    advisory_owned = models.CharField(max_length=100, choices=advisory_status, default="NO")
    advisor_name = models.CharField(max_length=200, null=True, blank=True)
    advisor_registration_number = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    cash = models.CharField(max_length=100, choices=cash_status, default="NO")
    status = models.CharField(max_length=100, choices=material_status, default="Active")
    delete = models.BooleanField(default=False)
    frontend = models.BooleanField(default=False)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    @classmethod
    def get_center_for_user(cls, user, company_depot='NO', advisory_owned='NO'):
        mc_qs = cls.objects.filter(advisor_registration_number=user, company_depot=company_depot,
                                   advisory_owned=advisory_owned)
        if mc_qs.exists():
            return mc_qs.first()
        return None

    @property
    def material_to_type(self):
        if self.advisory_owned == 'YES':
            return 'Distributor'
        elif self.company_depot == 'YES':
            return 'C&F'

    @classmethod
    def get_frontend_mc(cls):
        return cls.objects.filter(frontend=True).first()

    def __str__(self):
        return self.mc_name


class Order(models.Model):
    wallet_yes_no = (('Yes', 'Yes'), ('No', 'No'))
    order_by = models.CharField(max_length=191, blank=True, null=True)
    transction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    # nipur start code
    order_id1 = models.CharField(max_length=1000, blank=True, null=True)
    material_center = models.ForeignKey(Material_center, on_delete=models.SET_NULL, null=True, blank=True)
    original_material_center = models.ForeignKey(Material_center, on_delete=models.SET_NULL, null=True, blank=True,
                                                 related_name='original_mc_order')
    # nipur end code
    name = models.CharField(max_length=191)
    email = models.EmailField()
    user_id = models.ForeignKey(User, related_name='order_user',
                                on_delete=models.CASCADE, blank=True, null=True)
    card_description = models.CharField(max_length=10000, blank=True, null=True)
    postal_code = models.IntegerField()
    address = models.CharField(max_length=191)
    paid = models.BooleanField(default=False)
    # <---------------------------------------------------------------------shiping Charge Added 23-4-2021---------------------------------------------->
    shiping_charge = models.FloatField(default=0)
    # <---------------------------------------------------------------------shiping Charge Added 23-4-2021---------------------------------------------->
    grand_total = models.FloatField(default=0)
    shipping_address = models.ForeignKey(
        Address, related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(
        Address, related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)
    status = models.IntegerField(null=True)
    delete = models.BooleanField(default=False)
    modified = models.BooleanField(default=False)
    loyalty_order = models.BooleanField(default=False)
    is_partial_loyalty_order = models.BooleanField(default=False)
    consumed_cri = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    accept_date = models.DateField(null=True, blank=True)
    ready_to_dispatch_date = models.DateField(null=True, blank=True)
    dispatched_date = models.DateField(null=True, blank=True)
    delivered_date = models.DateField(null=True, blank=True)
    rejected_date = models.DateField(null=True, blank=True)
    returned_date = models.DateField(null=True, blank=True)
    refunded_date = models.DateField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    pv = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    bv = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    sr_order_id = models.CharField(max_length=50, blank=True, null=True, default=None)
    sr_shipment_id = models.CharField(max_length=50, blank=True, null=True, default=None)
    sr_status = models.CharField(max_length=50, blank=True, null=True, default=None)
    sr_status_code = models.IntegerField(default=0, blank=True, null=True)
    sr_onboarding_completed_now = models.IntegerField(default=0, blank=True, null=True)
    sr_awb_code = models.CharField(max_length=100, blank=True, null=True, default=None)
    sr_courier_company_id = models.CharField(max_length=100, blank=True, null=True, default=None)
    sr_courier_name = models.CharField(max_length=100, blank=True, null=True, default=None)
    pay_with_wallet = models.CharField(max_length=100, choices=wallet_yes_no, default="No")
    group_checkout = models.BooleanField(default=False)
    main_order = models.ForeignKey("self", related_name='unique_order',
                                   on_delete=models.SET_NULL, blank=True, null=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)
    was_there_calculation_issue_in_li = models.BooleanField(default=False)
    was_there_calculation_issue_in_pv = models.BooleanField(default=False)
    was_there_calculation_issue_in_bv = models.BooleanField(default=False)
    # fields added by piyush
    shipment_height = models.FloatField(null=True, blank=True, default=0)
    shipment_width = models.FloatField(null=True, blank=True, default=0)
    shipment_length = models.FloatField(null=True, blank=True, default=0)
    shipment_weight = models.FloatField(null=True, blank=True, default=0)
    shipping_partner = models.CharField(max_length=100, blank=True, null=True, default=None)
    shipping_tracking_id = models.CharField(max_length=100, blank=True, null=True, default=None)

    class Meta:
        ordering = ['-date', ]

    def __str__(self):
        return "{}:{}".format(self.id, self.email)

    def total_cost(self):
        return sum([li.cost() for li in self.lineitem_set.all()])

    def tax_amount(self):
        return float(self.grand_total) - float(sum([li.cost() for li in self.lineitem_set.all()]))

    def cgst_amount(self):
        total_amount = 0
        data = LineItem.objects.filter(order=self)
        for i in data:
            cgst = i.cgst
            if cgst == None:
                cgst = 0
            igst = i.igst
            if igst == None:
                igst = 0
            amount = (float(i.price) / (1 + (float(igst) / 100))) * float(cgst) / 100
            # amount = float(i.price) - (float(i.price)/(1 + (float(cgst)/100)))
            cgst = i.quantity * amount
            total_amount += cgst
        total_amount = "{:.2f}".format(total_amount)
        return total_amount

    def sgst_amount(self):
        total_amount = 0
        data = LineItem.objects.filter(order=self)
        for i in data:
            sgst = i.sgst
            if sgst == None:
                sgst = 0
            igst = i.igst
            if igst == None:
                igst = 0
            amount = (float(i.price) / (1 + (float(igst) / 100))) * float(sgst) / 100
            sgst = i.quantity * amount
            total_amount += sgst
        total_amount = "{:.2f}".format(total_amount)
        return total_amount

    def igst_amount(self):
        total_amount = 0
        data = LineItem.objects.filter(order=self)
        for i in data:
            igst = i.igst
            if igst == None:
                igst = 0
            igst = float(i.price) - (float(i.price) / (1 + (float(igst) / 100)))
            igst = i.quantity * igst
            total_amount += igst
        total_amount = "{:.2f}".format(total_amount)
        return total_amount

    @property
    def get_stock_product_order_items(self):
        from distributor.models import Distributor_Inventry
        result = []
        lineitems = self.lineitem_set.all()
        for lineitem in lineitems:
            if Distributor_Inventry.objects.filter(pk=self.material_center.id,
                                                   product__id=lineitem.product.id,
                                                   current_quantity__gte=lineitem.quantity).exists():
                result.append(lineitem)
        return result

    def actual_mrp_grand_total(self):
        from distributor.models import Distributor_Inventry
        result = []
        lineitems = self.lineitem_set.all()
        for lineitem in lineitems:
            result.append(lineitem.actual_mrp_total_amount())
        return sum(result)


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return f"{self.pk}"


class Batch(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    batch_name = models.CharField(max_length=191)
    print_name = models.CharField(max_length=191, null=True, blank=True)
    batch_number = models.CharField(max_length=191)
    mrp = models.FloatField(blank=True, null=True)
    date_of_manufacture = models.DateField(null=True, blank=True)
    date_of_expiry = models.DateField(null=True, blank=True)
    shelf_life = models.IntegerField(null=True, blank=True)
    quantity = models.IntegerField(default=0)
    pv = models.FloatField(null=True, blank=True, default=0)
    bv = models.FloatField(null=True, blank=True, default=0)
    created_on = models.DateField(auto_now_add=True)
    delete = models.BooleanField(default=False)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    def get_distributor_price(self, sale_type=1):
        mrp = self.mrp
        cgst = self.product.cgst or 0
        sgst = self.product.sgst or 0
        igst = self.product.igst or 0
        vat = self.product.vat or 0
        distributor_price = self.product.distributor_price
        if sale_type == '1':
            distributor_price = mrp / ((100 + igst) / 100) / ((100 + distributor_price) / 100)
        else:
            distributor_price = mrp / ((100 + (sgst + cgst)) / 100) / ((100 + distributor_price) / 100)
        return distributor_price

    def __str__(self):
        return self.batch_name

    # lets override the save function here
    def save(self, *args, **kwargs):
        resp = calculate_values(self.product)
        if len(resp) > 0:
            self.pv = resp[0]['point_value']
            self.bv = resp[0]['business_value']
        super(Batch, self).save(*args, **kwargs)


# multiple product
class LineItem(models.Model):
    order_by = models.CharField(max_length=191, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    pv = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    bv = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    # # <------------------------------------27feb to add dicountedprice-------------------------------------------------------------->
    # discount_price = models.DecimalField(max_digits=20,decimal_places=2)
    # # <------------------------------------27feb to add dicountedprice-------------------------------------------------------------->
    quantity = models.IntegerField()
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True, blank=True)
    cgst = models.FloatField(default=0.00)
    sgst = models.FloatField(default=0.00)
    igst = models.FloatField(default=0.00)
    total_amount = models.FloatField(null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        ordering = ['-date_added', ]

    # lets override the save function here
    def save(self, *args, **kwargs):
        batch_obj = self.batch
        product_obj = self.product
        if batch_obj:
            BatchObj = Batch.objects.filter(id=batch_obj.id)
            if BatchObj:
                BatchObj = BatchObj.first()
                if BatchObj.product.id == product_obj.id:
                    # if BatchObj.batch_number == "NB11":
                    super(LineItem, self).save(*args, **kwargs)
                else:
                    # TBD: add this error on database
                    raise Exception(
                        "Batch and product are not matching. Try cleaning data using mlm_admin remove_unlinked_product_batch utility.")
            else:
                BatchObj = Batch.objects.filter(product=product_obj)
                if BatchObj:
                    BatchObj = BatchObj.last()
                else:
                    raise Exception("Error: Batch Not Found.")
        else:
            BatchObj = Batch.objects.filter(product=product_obj)
            if BatchObj:
                BatchObj = BatchObj.last()
            else:
                raise Exception("Error: Batch Not Added.")


    def actual_mrp_total_amount(self):
        return self.batch.mrp * self.quantity

    def __str__(self):
        return "{}:{}".format(self.product.product_name, self.id)

    def cost(self):
        return self.price * self.quantity

    def total_cgst(self):
        cgst = self.cgst
        if cgst == None:
            cgst = 0
        igst = self.igst
        if igst == None:
            igst = 0
        cgst = (float(self.price) / (1 + (float(igst) / 100))) * float(cgst) / 100
        total_amount = self.quantity * cgst
        total_amount = "{:.2f}".format(total_amount)
        return total_amount

    def total_sgst(self):
        sgst = self.sgst
        if sgst == None:
            sgst = 0
        igst = self.igst
        if igst == None:
            igst = 0
        sgst = (float(self.price) / (1 + (float(igst) / 100))) * float(sgst) / 100
        total_amount = self.quantity * sgst
        total_amount = "{:.2f}".format(total_amount)
        return total_amount

    def total_igst(self):
        igst = self.igst
        if igst == None:
            igst = 0
        amount = float(self.price) - (float(self.price) / (1 + (float(igst) / 100)))
        total_amount = self.quantity * amount
        total_amount = "{:.2f}".format(total_amount)
        return total_amount


@receiver(pre_save, sender=Order)
def recalculate_cart_items_and_update_product_quant(sender, instance, **kwargs):
    if instance.paid == True:
        # # contents = f"As a security measure, our payment processor requests a picture of the credit card covering the numbers except the last 4 with a piece of paper or other material. This will only be done one time.\n\n\nOrder Details\n\nOrder ID: {instance.order_id}\nStatus: {instance.order_status}\nTotal{instance.order_total}\n\n\nBilling Address\n\nUsername: {instance.user.username}\nAddress: {instance.Address1}\nMobile Phone: {instance.contact}\nZip Code: {instance.zipcode}\nEmail address: {instance.email}"
        # sendsms("Msg Order Status", user_mobile_number = "+91" + str(instance.shipping_address.mobile), referee_name = (str(instance.name)))

        # contents = "Auretics Email update order notification email Status  of order #{instance.order_id} is {instance.status} and shipping Status code is {instance.sr_status_code}"
        # send_mail("Order Notes", contents, settings.EMAIL_HOST_USER,
        #           [instance.email])

        lin_itm = LineItem.objects.filter(order=instance)
        for itm in lin_itm:
            prod = Product.objects.get(id=itm.product.id)
            prod.quantity = prod.quantity - itm.quantity
            prod.save()

        # prod = Product.objects.filter(id=instance.product.id)
        # prod.quantity = prod.quantity - instance.quantity
        # prod.save()


class Wishlist(models.Model):
    # user = models.ForeignKey(User ,on_delete=models.CASCADE)
    wished_item = models.ForeignKey(Product, on_delete=models.CASCADE)
    slug = models.CharField(max_length=30, null=True, blank=True)
    added_date = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.wished_item.product_name


class Banner(models.Model):
    name = models.CharField(max_length=191)
    banner = models.ImageField(upload_to='vanor_images/', null=True, blank=True)
    ranking = models.CharField(max_length=191)
    status = models.CharField(max_length=191, choices=vanor_status, default="Active")
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class Ship_Charge(models.Model):
    minimum_amount = models.FloatField()
    shiping_charge = models.FloatField(default=0.00)
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50, default='stripe_charge_id')
    order = models.ForeignKey(Order,
                              on_delete=models.SET_NULL, blank=True, null=True)
    order_number = models.CharField(max_length=200, null=True, blank=True)
    mihpayid = models.CharField(max_length=300, blank=True)
    mode = models.CharField(max_length=250, blank=True)
    status = models.CharField(max_length=250)
    # txnid = models.CharField(max_length=250)
    amount = models.FloatField(default=0.00)
    # card_category = models.CharField(max_length=250,default='0')
    net_amount_debit = models.FloatField(default=0.00)
    hash = models.CharField(max_length=1400, default='0')
    bank_ref_num = models.CharField(max_length=300, default='0')
    bankcode = models.CharField(max_length=100, default='0')
    error_Message = models.CharField(max_length=1000, default='0')
    # cardnum = models.CharField(max_length=100,default='0')
    # name_on_card = models.CharField(max_length=100,default='0')
    generated_hash = models.CharField(max_length=1400, default='0')
    recived_hash = models.CharField(max_length=1400, default='0')
    hash_verified = models.CharField(max_length=50, default='0')
    timestamp = models.DateTimeField(blank=True, null=True)
    created_on = models.DateField(auto_now_add=True)
    razorpay_signature = models.CharField(max_length=1400, default='0')
    date_modified = models.DateTimeField(auto_now=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.recived_hash

# @receiver(pre_save, sender=Order)
# def send_update_order_notification_email(sender, instance,**kwargs):

# if instance.status or instance.sr_status_code:

# contents = f"As a security measure, our payment processor requests a picture of the credit card covering the numbers except the last 4 with a piece of paper or other material. This will only be done one time.\n\n\nOrder Details\n\nOrder ID: {instance.order_id}\nStatus: {instance.order_status}\nTotal{instance.order_total}\n\n\nBilling Address\n\nUsername: {instance.user.username}\nAddress: {instance.Address1}\nMobile Phone: {instance.contact}\nZip Code: {instance.zipcode}\nEmail address: {instance.email}"
# sendsms("Msg Order Status", user_mobile_number = "+91" + str(instance.shipping_address.mobile), referee_name = (str(instance.name)))
#
# contents = "Auretics Email update order notification email Status  of order #{instance.order_id} is {instance.status} and shipping Status code is {instance.sr_status_code}"
# send_mail("Order Notes", contents, settings.EMAIL_HOST_USER,
#           [instance.email])
