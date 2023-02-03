from django import forms
from django.conf import settings
from django.core.files.images import get_image_dimensions
from django.utils import timezone

from accounts.models import ReferralCode, Status, User_Check
from mlm_admin.models import ChangeEmail, ChangeMobileNumber, Sheet_config, Greeting
# from .models import Purchase
from notify.models import NoticeTemplate
from payment_gateway.models import Gateway, PaymentMode
from shop import models
from shop.models import Pincode


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()


class DateInput(forms.DateInput):
    input_type = 'date'


class EmailForm(forms.ModelForm, forms.Form):
    class Meta:
        model = ChangeEmail
        fields = ('date', 'old_email', 'new_email')
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'dd/mm/yy', 'type': 'date'}),
            'old_email': forms.TextInput(attrs={'placeholder': 'Enter old email', 'class': 'form-control'}),
            'new_email': forms.TextInput(attrs={'placeholder': 'Enter old email', 'class': 'form-control'}),
        }


class MobileNumberForm(forms.ModelForm, forms.Form):
    class Meta:
        model = ChangeMobileNumber
        fields = ('date', 'old_number', 'new_number')
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'dd/mm/yy', 'type': 'date'}),
            'old_number': forms.NumberInput(
                attrs={'placeholder': 'Enter SGST', 'class': 'form-control'}),
            'new_number': forms.NumberInput(
                attrs={'placeholder': 'Enter SGST', 'class': 'form-control'}),
        }


class Productform(forms.ModelForm, forms.Form):
    class Meta:
        model = models.Product
        fields = ('product_name', 'slug', 'print_name', 'hsn_code', 'sgst', 'cgst', 'igst', 'vat', 'distributor_price',
                  'business_value', 'point_value',
                  'loyalty_purchase', 'loyalty_consume', 'essential_product', 'minimum_purchase_quantity', 'description',
                  'maintain_stock_balance', 'country_of_origin', 'item_package_quantity',
                  'ingredients', 'expiration_dated_product', 'colour', 'size', 'material', 'flavour', 'weight',
                  'model_number', 'usage', 'directions', 'indications', 'special_feature',
                  'safety_warning', 'length', 'width', 'height', 'image', 'image2', 'image3', 'image4', 'image5',
                  'image6', 'image7', 'image8', 'image9', 'image10', 'launch_date', 'brand', 'product_code',
                  'name_in_accounting_software')
        widgets = {
            'product_name': forms.TextInput(attrs={'placeholder': 'Enter Product Name', 'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'placeholder': 'Enter Alias', 'class': 'form-control'}),
            'product_code': forms.TextInput(attrs={'placeholder': 'Enter Product Code', 'class': 'form-control'}),
            'name_in_accounting_software': forms.TextInput(
                attrs={'placeholder': 'Enter Name in Accounting Software', 'class': 'form-control'}),
            'print_name': forms.TextInput(attrs={'placeholder': 'Enter Print Name', 'class': 'form-control'}),
            'hsn_code': forms.TextInput(attrs={'placeholder': 'Enter HSN Code', 'class': 'form-control'}),
            'sgst': forms.NumberInput(
                attrs={'placeholder': 'Enter SGST', 'class': 'form-control', 'readonly': 'readonly'}),
            'cgst': forms.NumberInput(
                attrs={'placeholder': 'Enter CGST', 'class': 'form-control', 'readonly': 'readonly'}),
            'igst': forms.TextInput(attrs={'placeholder': 'Enter IGST', 'class': 'form-control'}),
            'vat': forms.TextInput(attrs={'placeholder': 'Enter VAT', 'class': 'form-control'}),
            'distributor_price': forms.TextInput(
                attrs={'placeholder': 'Enter Distributor Price', 'class': 'form-control'}),
            'business_value': forms.TextInput(attrs={'placeholder': 'Enter Business Value', 'class': 'form-control'}),
            'point_value': forms.TextInput(attrs={'placeholder': 'Enter Point Value', 'class': 'form-control'}),
            'loyalty_purchase': forms.Select(choices=models.purchase_status, attrs={'class': 'form-control'}),
            'essential_product': forms.Select(choices=models.purchase_status, attrs={'class': 'form-control'}),
            'loyalty_consume': forms.Select(choices=models.consume_status, attrs={'class': 'form-control'}),
            'minimum_purchase_quantity': forms.TextInput(
                attrs={'placeholder': 'Enter Quantity', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'placeholder': 'Enter Description', 'class': 'form-control'}),
            'maintain_stock_balance': forms.Select(choices=models.stock_blance_status, attrs={'class': 'form-control'}),
            'country_of_origin': forms.TextInput(
                attrs={'placeholder': 'Enter Country Of Origin', 'class': "form-control"}),
            'brand': forms.TextInput(attrs={'placeholder': 'Enter Brand Name', 'class': "form-control"}),
            'item_package_quantity': forms.TextInput(attrs={'placeholder': 'Enter Quantity', 'class': "form-control"}),
            'ingredients': forms.Textarea(attrs={'placeholder': 'Enter Ingredients', 'class': "form-control"}),
            'expiration_dated_product': forms.Select(choices=models.expdate, attrs={'class': 'form-control'}),
            'colour': forms.TextInput(attrs={'placeholder': 'Enter Colour', 'class': "form-control"}),
            'size': forms.Select(choices=models.SIZE_CHOICES, attrs={'class': 'form-control'}),
            # 'size': forms.SelectMultiple(choices=models.SIZE_CHOICES,attrs={'class':"form-control select2"}),
            'material': forms.TextInput(attrs={'placeholder': 'Enter Material', 'class': "form-control"}),
            'flavour': forms.TextInput(attrs={'placeholder': 'Enter Flavour', 'class': "form-control"}),
            'weight': forms.TextInput(attrs={'placeholder': 'Enter Weight', 'class': "form-control"}),
            'model_number': forms.TextInput(attrs={'placeholder': 'Enter Model Number', 'class': "form-control"}),
            'usage': forms.Textarea(attrs={'placeholder': 'Enter Usage', 'class': "form-control"}),
            'directions': forms.Textarea(attrs={'placeholder': 'Enter Directions', 'class': "form-control"}),
            'indications': forms.Textarea(attrs={'placeholder': 'Enter Indications', 'class': "form-control"}),
            'special_feature': forms.Textarea(attrs={'placeholder': 'Enter Special Feature', 'class': "form-control"}),
            'safety_warning': forms.Textarea(attrs={'placeholder': 'Enter Safety Warning', 'class': "form-control"}),
            'length': forms.TextInput(attrs={'placeholder': 'Enter Length', 'class': "form-control"}),
            'width': forms.TextInput(attrs={'placeholder': 'Enter Width', 'class': "form-control"}),
            'height': forms.TextInput(attrs={'placeholder': 'Enter Height', 'class': "form-control"}),
            # 'launch_date':forms.DateField(widget=DateInput),
            # 'imag_path': forms.ImageField(attrs={'class':'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'enctype': 'multipart/form-data'}),
            'image2': forms.FileInput(attrs={'class': 'form-control', 'enctype': 'multipart/form-data'}),
            'image3': forms.FileInput(attrs={'class': 'form-control', 'enctype': 'multipart/form-data'}),
            'image4': forms.FileInput(attrs={'class': 'form-control', 'enctype': 'multipart/form-data'}),
            'image5': forms.FileInput(attrs={'class': 'form-control', 'enctype': 'multipart/form-data'}),
            'image6': forms.FileInput(attrs={'class': 'form-control', 'enctype': 'multipart/form-data'}),
            'image7': forms.FileInput(attrs={'class': 'form-control', 'enctype': 'multipart/form-data'}),
            'image8': forms.FileInput(attrs={'class': 'form-control', 'enctype': 'multipart/form-data'}),
            'image9': forms.FileInput(attrs={'class': 'form-control', 'enctype': 'multipart/form-data'}),
            'image10': forms.FileInput(attrs={'class': 'form-control', 'enctype': 'multipart/form-data'}),
            'launch_date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'dd/mm/yy', 'type': 'date'}),
            # 'launch_date':forms.DateInput(attrs={'class':'form-control datepicker','placeholder':'dd/mm/yy' }),
            # 'expire_date':forms.DateInput(attrs={'class':'form-control datepicker','placeholder':'dd/mm/yy','type':'date'})
            # 'price': forms.NumberInput(attrs={'placeholder': 'Enter Commission', 'class': 'form-control'}),
            # 'mrp': forms.NumberInput(attrs={'class': 'form-control'}),
            # 'status': forms.Select(choices=models.prod_status,attrs={'class':'form-control'}),
        }


class Productformview(forms.ModelForm):
    class Meta:
        model = models.Product
        fields = ('product_name', 'slug', 'print_name', 'hsn_code', 'sgst', 'cgst', 'igst', 'vat', 'distributor_price',
                  'business_value', 'point_value',
                  'loyalty_purchase', 'loyalty_consume', 'essential_product', 'minimum_purchase_quantity',
                  'description',
                  'maintain_stock_balance', 'country_of_origin', 'item_package_quantity',
                  'ingredients', 'expiration_dated_product', 'colour', 'size', 'material', 'flavour', 'weight',
                  'model_number', 'usage', 'directions', 'indications', 'special_feature',
                  'safety_warning', 'length', 'width', 'height', 'image', 'image2', 'image3', 'image4', 'image5',
                  'image6', 'image7', 'image8', 'image9', 'image10', 'launch_date', 'brand',
                  'product_code', 'name_in_accounting_software')
        widgets = {
            'product_name': forms.TextInput(
                attrs={'placeholder': 'Enter Product Name', 'class': 'form-control', 'disabled': 'disabled'}),
            'slug': forms.TextInput(
                attrs={'placeholder': 'Enter Alias', 'class': 'form-control', 'disabled': 'disabled'}),
            'product_code': forms.TextInput(
                attrs={'placeholder': 'Enter Product Code', 'class': 'form-control', 'disabled': 'disabled'}),
            'name_in_accounting_software': forms.TextInput(
                attrs={'placeholder': 'Enter Name in Accounting Software', 'class': 'form-control',
                       'disabled': 'disabled'}),

            'print_name': forms.TextInput(
                attrs={'placeholder': 'Enter Print Name', 'class': 'form-control', 'disabled': 'disabled'}),
            'hsn_code': forms.NumberInput(
                attrs={'placeholder': 'Enter HSN Code', 'class': 'form-control', 'disabled': 'disabled'}),
            'sgst': forms.NumberInput(
                attrs={'placeholder': 'Enter SGST', 'class': 'form-control', 'disabled': 'disabled'}),
            'cgst': forms.NumberInput(
                attrs={'placeholder': 'Enter CGST', 'class': 'form-control', 'disabled': 'disabled'}),
            'igst': forms.NumberInput(
                attrs={'placeholder': 'Enter IGST', 'class': 'form-control', 'disabled': 'disabled'}),
            'vat': forms.NumberInput(
                attrs={'placeholder': 'Enter VAT', 'class': 'form-control', 'disabled': 'disabled'}),
            'distributor_price': forms.NumberInput(
                attrs={'placeholder': 'Enter Distributor Price', 'class': 'form-control', 'disabled': 'disabled'}),
            'business_value': forms.NumberInput(
                attrs={'placeholder': 'Enter Business Value', 'class': 'form-control', 'disabled': 'disabled'}),
            'point_value': forms.NumberInput(
                attrs={'placeholder': 'Enter Point Value', 'class': 'form-control', 'disabled': 'disabled'}),
            'loyalty_purchase': forms.Select(choices=models.purchase_status,
                                             attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'essential_product': forms.Select(choices=models.purchase_status,
                                              attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'loyalty_consume': forms.Select(choices=models.consume_status,
                                            attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'minimum_purchase_quantity': forms.NumberInput(
                attrs={'placeholder': 'Enter Quantity', 'class': 'form-control', 'disabled': 'disabled'}),
            'description': forms.Textarea(
                attrs={'placeholder': 'Enter Description', 'class': 'form-control', 'disabled': 'disabled'}),
            'maintain_stock_balance': forms.Select(choices=models.stock_blance_status,
                                                   attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'country_of_origin': forms.TextInput(
                attrs={'placeholder': 'Enter Country Of Origin', 'class': "form-control", 'disabled': 'disabled'}),
            'brand': forms.TextInput(
                attrs={'placeholder': 'Enter Brand Name', 'class': "form-control", 'disabled': 'disabled'}),
            'item_package_quantity': forms.NumberInput(
                attrs={'placeholder': 'Enter Quantity', 'class': "form-control", 'disabled': 'disabled'}),
            'ingredients': forms.TextInput(
                attrs={'placeholder': 'Enter Ingredients', 'class': "form-control", 'disabled': 'disabled'}),
            'expiration_dated_product': forms.Select(choices=models.expdate,
                                                     attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'colour': forms.TextInput(
                attrs={'placeholder': 'Enter Colour', 'class': "form-control", 'disabled': 'disabled'}),
            'size': forms.Select(choices=models.SIZE_CHOICES, attrs={'class': 'form-control', 'disabled': 'disabled'}),
            # 'size': forms.MultipleChoiceField(choices=models.SIZE_CHOICES,widget=Select2MultipleWidget),
            'material': forms.TextInput(
                attrs={'placeholder': 'Enter material', 'class': "form-control", 'disabled': 'disabled'}),
            'flavour': forms.TextInput(
                attrs={'placeholder': 'Enter Flavour', 'class': "form-control", 'disabled': 'disabled'}),
            'weight': forms.TextInput(
                attrs={'placeholder': 'Enter Weight', 'class': "form-control", 'disabled': 'disabled'}),
            'model_number': forms.TextInput(
                attrs={'placeholder': 'Enter Model Number', 'class': "form-control", 'disabled': 'disabled'}),
            'usage': forms.Textarea(
                attrs={'placeholder': 'Enter Usage', 'class': "form-control", 'disabled': 'disabled'}),
            'directions': forms.Textarea(
                attrs={'placeholder': 'Enter Directions', 'class': "form-control", 'disabled': 'disabled'}),
            'indications': forms.Textarea(
                attrs={'placeholder': 'Enter Indications', 'class': "form-control", 'disabled': 'disabled'}),
            'special_feature': forms.Textarea(
                attrs={'placeholder': 'Enter Special Feature', 'class': "form-control", 'disabled': 'disabled'}),
            'safety_warning': forms.Textarea(
                attrs={'placeholder': 'Enter Safety Warning', 'class': "form-control", 'disabled': 'disabled'}),
            'length': forms.TextInput(
                attrs={'placeholder': 'Enter Length', 'class': "form-control", 'disabled': 'disabled'}),
            'width': forms.TextInput(
                attrs={'placeholder': 'Enter Width', 'class': "form-control", 'disabled': 'disabled'}),
            'height': forms.TextInput(
                attrs={'placeholder': 'Enter Height', 'class': "form-control", 'disabled': 'disabled'}),
            # 'launch_date':forms.DateField(widget=DateInput),
            # 'imag_path': forms.ImageField(attrs={'class':'form-control'}),
            'image': forms.FileInput(
                attrs={'class': 'form-control', 'enctype': 'multipart/form-data', 'disabled': 'disabled'}),
            'image2': forms.FileInput(
                attrs={'class': 'form-control', 'enctype': 'multipart/form-data', 'disabled': 'disabled'}),
            'image3': forms.FileInput(
                attrs={'class': 'form-control', 'enctype': 'multipart/form-data', 'disabled': 'disabled'}),
            'image4': forms.FileInput(
                attrs={'class': 'form-control', 'enctype': 'multipart/form-data', 'disabled': 'disabled'}),
            'image5': forms.FileInput(
                attrs={'class': 'form-control', 'enctype': 'multipart/form-data', 'disabled': 'disabled'}),
            'image6': forms.FileInput(
                attrs={'class': 'form-control', 'enctype': 'multipart/form-data', 'disabled': 'disabled'}),
            'image7': forms.FileInput(
                attrs={'class': 'form-control', 'enctype': 'multipart/form-data', 'disabled': 'disabled'}),
            'image8': forms.FileInput(
                attrs={'class': 'form-control', 'enctype': 'multipart/form-data', 'disabled': 'disabled'}),
            'image9': forms.FileInput(
                attrs={'class': 'form-control', 'enctype': 'multipart/form-data', 'disabled': 'disabled'}),
            'image10': forms.FileInput(
                attrs={'class': 'form-control', 'enctype': 'multipart/form-data', 'disabled': 'disabled'}),
            'launch_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'disabled': 'disabled'})
            # 'price': forms.NumberInput(attrs={'placeholder': 'Enter Commission', 'class': 'form-control'}),
            # 'mrp': forms.NumberInput(attrs={'class': 'form-control'}),
            # 'status': forms.Select(choices=models.prod_status,attrs={'class':'form-control'}),
        }


class Categoryform(forms.ModelForm):
    class Meta:
        model = models.Category
        fields = "__all__"
        exclude = ('parent_category_id',)
        widgets = {
            'cat_name': forms.TextInput(attrs={'placeholder': 'Enter Category Name', 'class': 'form-control'}),
            'is_parent_category': forms.Select(choices=models._parent_category, attrs={'class': 'form-control'}),
            # 'imag_path': forms.ImageField(attrs={'class':'form-control'}),
            'imag_path': forms.FileInput(
                attrs={'class': 'form-control', 'enctype': 'multipart/form-data'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Description'}),
            'show_on_home_page': forms.Select(choices=models.show_on_home_page_choces, attrs={'class': 'form-control'}),
            'cat_order': forms.TextInput(attrs={'placeholder': 'Enter Cat Order', 'class': 'form-control'}),
            'status': forms.Select(choices=models.cat_status,
                                   attrs={'class': 'form-control', 'required': 'required'}, ),
            'is_hide': forms.Select(choices=models.is_hide, attrs={'class': 'form-control'}),
            #
        }


class Categoryformview(forms.ModelForm):
    class Meta:
        model = models.Category
        fields = "__all__"
        exclude = ('parent_category_id',)
        widgets = {
            'cat_name': forms.TextInput(
                attrs={'placeholder': 'Enter Category Name', 'class': 'form-control', 'disabled': 'disabled'}),
            'is_parent_category': forms.Select(choices=models._parent_category,
                                               attrs={'class': 'form-control', 'disabled': 'disabled'}),
            # 'imag_path': forms.ImageField(attrs={'class':'form-control'}),
            'imag_path': forms.FileInput(
                attrs={'class': 'form-control', 'enctype': 'multipart/form-data', 'disabled': 'disabled'}),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Enter Description', 'disabled': 'disabled'}),
            'show_on_home_page': forms.Select(choices=models.show_on_home_page_choces,
                                              attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'status': forms.Select(choices=models.cat_status, attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'cat_order': forms.TextInput(
                attrs={'placeholder': 'Enter Cat Order', 'class': 'form-control', 'disabled': 'disabled'}),
            'status': forms.Select(choices=models.cat_status,
                                   attrs={'class': 'form-control', 'required': 'required', 'disabled': 'disabled'}, ),
            'is_hide': forms.Select(choices=models.is_hide,
                                    attrs={'class': 'form-control', 'disabled': 'disabled'}),
        }


class Orderform(forms.ModelForm):
    class Meta:
        model = models.Order
        fields = "__all__"
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'email': forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}),
            # 'imag_path': forms.ImageField(attrs={'class':'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'disabled': 'disabled'}),
            'postal_code': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter Description', 'disabled': 'disabled'}),
            'address': forms.TextInput(
                attrs={'placeholder': 'Enter Address', 'class': 'form-control', 'disabled': 'disabled'}),
            'paid': forms.NullBooleanSelect(attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'status': forms.Select(choices=models.cat_status, attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'accept_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'disabled': 'disabled'}),
            'ready_to_dispatch_date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control', 'disabled': 'disabled'}),
            'dispatched_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'disabled': 'disabled'}),
            'delivered_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'disabled': 'disabled'}),
            'rejected_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'disabled': 'disabled'}),
            'returned_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'disabled': 'disabled'}),
            'refunded_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'disabled': 'disabled'}),
            'shipment_height': forms.TextInput(attrs={'type': 'number', 'step': '0.01', 'class': 'form-control'}),
            'shipment_width': forms.TextInput(attrs={'type': 'number', 'step': '0.01', 'class': 'form-control'}),
            'shipment_length': forms.TextInput(attrs={'type': 'number', 'step': '0.01', 'class': 'form-control'}),
            'shipment_weight': forms.TextInput(attrs={'type': 'number', 'step': '0.01', 'class': 'form-control'}),
        }


class Batchform(forms.ModelForm):
    class Meta:
        model = models.Batch
        fields = "__all__"
        exclude = ('quantity',)
        widgets = {
            'batch_name': forms.TextInput(attrs={'placeholder': 'Enter Batch Name', 'class': 'form-control'}),
            'print_name': forms.TextInput(attrs={'placeholder': 'Enter Print Name', 'class': 'form-control'}),
            'batch_number': forms.TextInput(attrs={'placeholder': 'Enter Batch Number', 'class': 'form-control'}),
            'mrp': forms.NumberInput(
                attrs={'placeholder': 'Enter MRP', 'class': 'form-control', 'required': 'required'}),
            'date_of_manufacture': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control', 'onchange': 'cal()'}),
            # 'date_of_manufacture': forms.DateInput(attrs={'placeholder':'Enter Manufacture Date','class':'form-control'}),
            'date_of_expiry': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'onchange': 'cal()'}),
            'shelf_life': forms.NumberInput(
                attrs={'placeholder': 'Enter Shelf Life', 'class': 'form-control', 'readonly': 'readonly'}),
            # 'quantity': forms.NumberInput(attrs={'placeholder':'Enter Quantity','class':'form-control'})
        }


class Batchformview(forms.ModelForm):
    class Meta:
        model = models.Batch
        fields = "__all__"
        exclude = ('date_of_manufacture', 'date_of_expiry')
        widgets = {
            'batch_name': forms.TextInput(
                attrs={'placeholder': 'Enter Batch Name', 'class': 'form-control', 'disabled': 'disabled'}),
            'print_name': forms.TextInput(
                attrs={'placeholder': 'Enter Print Name', 'class': 'form-control', 'disabled': 'disabled'}),
            'batch_number': forms.TextInput(
                attrs={'placeholder': 'Enter Print Name', 'class': 'form-control', 'disabled': 'disabled'}),
            'mrp': forms.NumberInput(attrs={'placeholder': 'Enter MRP', 'class': 'form-control', 'disabled': 'disabled',
                                            'required': 'required'}),
            # 'date_of_manufacture':forms.DateInput(format='%d/%m/%Y'),
            # 'date_of_manufacture': forms.DateInput(attrs={'placeholder':'Enter Manufacture Date','class':'form-control'}),
            # 'date_of_expiry': forms.DateInput(format='%d/%m/%Y',attrs={'class':'form-control'}),
            'shelf_life': forms.NumberInput(
                attrs={'placeholder': 'Enter Self Life', 'class': 'form-control', 'disabled': 'disabled'}),
            # 'quantity': forms.NumberInput(attrs={'placeholder':'Enter Quantity','class':'form-control','disabled':'disabled'})
        }


class Materialform(forms.ModelForm):
    class Meta:
        model = models.Material_center
        fields = "__all__"
        widgets = {
            'mc_name': forms.TextInput(attrs={'placeholder': 'Enter MC Name', 'class': 'form-control'}),
            'print_name': forms.TextInput(attrs={'placeholder': 'Enter Print Name', 'class': 'form-control'}),
            'address': forms.TextInput(attrs={'placeholder': 'Enter Address', 'class': 'form-control'}),
            'address_line_2': forms.TextInput(attrs={'placeholder': 'Enter Address', 'class': 'form-control'}),
            'city': forms.TextInput(attrs={'placeholder': 'Enter City', 'class': 'form-control'}),
            'state': forms.TextInput(attrs={'placeholder': 'Enter State', 'class': 'form-control'}),
            'pin_code': forms.TextInput(attrs={'placeholder': 'Enter Pin Code', 'class': 'form-control'}),
            'mobile': forms.TextInput(attrs={'placeholder': 'Enter Mobile Number', 'class': 'form-control'}),
            'mc_type': forms.TextInput(attrs={'placeholder': 'Enter mc type', 'class': 'form-control'}),
            'gst_number': forms.TextInput(attrs={'placeholder': 'Enter GST Number', 'class': 'form-control'}),
            'company_depot': forms.Select(choices=models.depot_status,
                                          attrs={'placeholder': 'Enter Company Depot', 'class': 'form-control'}),

            'billing_allowed': forms.Select(choices=models.bill_status,
                                            attrs={'class': 'form-control'}),
            'advisory_owned': forms.Select(choices=models.advisory_status,
                                           attrs={'class': 'form-control'}),
            'advisor_name': forms.TextInput(
                attrs={'placeholder': 'Enter Advisor Name', 'class': 'form-control', 'required': 'required',
                       'readonly': 'readonly'}),
            # 'advisor_registration_number': forms.TextInput(attrs={'placeholder':'Enter Advisor Registration Number','class':'form-control','required':'required' }),
            'cash': forms.Select(choices=models.cash_status,
                                 attrs={'placeholder': 'Enter cash', 'class': 'form-control'}),
            'status': forms.Select(choices=models.material_status,
                                   attrs={'placeholder': 'Enter status', 'class': 'form-control'}),

        }


class Materialformview(forms.ModelForm):
    class Meta:
        model = models.Material_center
        fields = "__all__"
        widgets = {
            'mc_name': forms.TextInput(
                attrs={'placeholder': 'Enter MC Name', 'class': 'form-control', 'disabled': 'disabled'}),
            'print_name': forms.TextInput(
                attrs={'placeholder': 'Enter Print Name', 'class': 'form-control', 'disabled': 'disabled'}),
            'address': forms.TextInput(
                attrs={'placeholder': 'Enter Address', 'class': 'form-control', 'disabled': 'disabled'}),
            'address_line_2': forms.TextInput(
                attrs={'placeholder': 'Enter Address', 'class': 'form-control', 'disabled': 'disabled'}),
            'city': forms.TextInput(
                attrs={'placeholder': 'Enter City', 'class': 'form-control', 'disabled': 'disabled'}),
            'state': forms.TextInput(
                attrs={'placeholder': 'Enter State', 'class': 'form-control', 'disabled': 'disabled'}),
            'pin_code': forms.TextInput(
                attrs={'placeholder': 'Enter Pin Code', 'class': 'form-control', 'disabled': 'disabled'}),
            'gst_number': forms.TextInput(
                attrs={'placeholder': 'Enter GST Number', 'class': 'form-control', 'disabled': 'disabled'}),
            'company_depot': forms.Select(choices=models.depot_status,
                                          attrs={'placeholder': 'Enter Company Depot', 'class': 'form-control',
                                                 'disabled': 'disabled'}),
            'billing_allowed': forms.Select(choices=models.bill_status,
                                            attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'advisory_owned': forms.Select(choices=models.advisory_status,
                                           attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'advisor_name': forms.TextInput(
                attrs={'placeholder': 'Enter Advisor Name', 'class': 'form-control', 'disabled': 'disabled'}),
            # 'advisor_registration_number': forms.TextInput(attrs={'placeholder':'Enter Advisor Registration Number','class':'form-control','disabled':'disabled'}),
            'cash': forms.Select(choices=models.cash_status,
                                 attrs={'placeholder': 'Enter cash', 'class': 'form-control', 'disabled': 'disabled'}),
            'status': forms.Select(choices=models.material_status,
                                   attrs={'placeholder': 'Enter status', 'class': 'form-control',
                                          'disabled': 'disabled'}),
        }


class Bannerform(forms.ModelForm):
    class Meta:
        model = models.Banner
        fields = "__all__"
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter banner Name', 'class': 'form-control'}),
            'banner': forms.FileInput(attrs={'class': 'form-control', 'enctype': 'multipart/form-data'}),
            'ranking': forms.TextInput(attrs={'placeholder': 'Enter Ranking', 'class': 'form-control'}),
            'status': forms.Select(choices=models.vanor_status, attrs={'class': 'form-control'})
        }

        def __init__(self, *args, **kwargs):
            super(Bannerform, self).__init__(*args, **kwargs)
            self.fields['banner'].required = False


class Bannerformview(forms.ModelForm):
    class Meta:
        model = models.Banner
        fields = "__all__"
        widgets = {
            'name': forms.TextInput(
                attrs={'placeholder': 'Enter banner Name', 'class': 'form-control', 'disabled': 'disabled'}),
            'banner': forms.FileInput(
                attrs={'class': 'form-control', 'enctype': 'multipart/form-data', 'disabled': 'disabled'}),
            'ranking': forms.TextInput(
                attrs={'placeholder': 'Enter Ranking', 'class': 'form-control', 'disabled': 'disabled'}),
            'status': forms.Select(choices=models.vanor_status, attrs={'class': 'form-control', 'disabled': 'disabled'})
        }


class Referralview(forms.ModelForm):
    class Meta:
        model = ReferralCode
        fields = "__all__"
        widgets = {
            'user_id': forms.TextInput(
                attrs={'placeholder': 'Enter Vanor Name', 'class': 'form-control', 'disabled': 'disabled'}),
            'referal_id': forms.TextInput(
                attrs={'placeholder': 'Enter Vanor Name', 'class': 'form-control', 'disabled': 'disabled'}),
            'referral_code': forms.TextInput(
                attrs={'placeholder': 'Enter Vanor Name', 'class': 'form-control', 'disabled': 'disabled'}),
            'status': forms.TextInput(
                attrs={'placeholder': 'Enter Vanor Name', 'class': 'form-control', 'disabled': 'disabled'}),
        }


class Referral(forms.ModelForm):
    class Meta:
        model = ReferralCode
        fields = ('status',)
        widgets = {
            'status': forms.Select(choices=Status, attrs={"class": "form-control"})
        }


class AddressForm(forms.ModelForm):
    class Meta:
        model = models.Address
        fields = "__all__"
        exclude = ('user',)
        widgets = {
            'house_number': forms.TextInput(
                attrs={'placeholder': 'Enter Vanor Name', 'class': 'form-control', 'disabled': 'disabled'}),
            'address_line': forms.TextInput(
                attrs={'placeholder': 'Enter Vanor Name', 'class': 'form-control', 'disabled': 'disabled'}),
            'Landmark': forms.TextInput(
                attrs={'placeholder': 'Enter Vanor Name', 'class': 'form-control', 'disabled': 'disabled'}),
            'city': forms.TextInput(
                attrs={'placeholder': 'Enter Vanor Name', 'class': 'form-control', 'disabled': 'disabled'}),
            'street': forms.TextInput(
                attrs={'placeholder': 'Enter Vanor Name', 'class': 'form-control', 'disabled': 'disabled'}),
            'country': forms.TextInput(
                attrs={'placeholder': 'Enter Vanor Name', 'class': 'form-control', 'disabled': 'disabled'}),
            'pin': forms.TextInput(
                attrs={'placeholder': 'Enter Vanor Name', 'class': 'form-control', 'disabled': 'disabled'}),
            'mobile': forms.TextInput(
                attrs={'placeholder': 'Enter Vanor Name', 'class': 'form-control', 'disabled': 'disabled'}),
            'alternate_mobile': forms.TextInput(
                attrs={'placeholder': 'Enter Vanor Name', 'class': 'form-control', 'disabled': 'disabled'}),
        }


class CheckForm(forms.ModelForm):
    class Meta:
        model = User_Check
        fields = "__all__"
        exclude = ('user_check',)


class ShipCharge(forms.ModelForm):
    class Meta:
        model = models.Ship_Charge
        fields = "__all__"
        widgets = {
            'minimum_amount': forms.TextInput(
                attrs={"Placeholder": 'Enter Minimum Amount', 'type': 'number', 'step': "0.001", 'min': '0',
                       'class': 'form-control'}),
            'shiping_charge': forms.TextInput(
                attrs={"Placeholder": 'Enter Amount', 'type': 'number', 'step': "0.001", 'min': '0',
                       'class': 'form-control'})
        }


class SheetConfigForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SheetConfigForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Sheet_config
        fields = "__all__"


class pincode_form(forms.ModelForm):
    class Meta:
        model = Pincode
        fields = "__all__"


from ckeditor.widgets import CKEditorWidget


class NoticeTemplateForm(forms.ModelForm):
    def save(self, commit=True):
        item = super().save(commit)
        return item

    class Meta:
        model = NoticeTemplate
        exclude = ['datetime_created']
        widgets = {
            'template_name': forms.TextInput(attrs={'class': 'form-control col-sm-6'}),
            'template_event': forms.TextInput(attrs={'class': 'form-control col-sm-6'}),
            'template_type': forms.TextInput(attrs={'class': 'form-control col-sm-6'}),
            'template_category': forms.TextInput(attrs={'class': 'form-control col-sm-6'}),
            'sms_sender_id': forms.Select(choices=[(c, c) for c in ['AURTCS']],
                                          attrs={'class': 'form-control col-sm-6'}),
            'message_template': forms.Textarea(attrs={'class': 'form-control col-sm-6'}),
            'template_id': forms.TextInput(attrs={'class': 'form-control col-sm-6'}),
            'header': forms.TextInput(attrs={'class': 'form-control col-sm-6'}),
            'approval_date': forms.TextInput(attrs={'class': 'form-control col-sm-6'}),
            'email_sender_id': forms.EmailInput(attrs={'class': 'form-control col-sm-6'}),
            'email_subject': forms.TextInput(attrs={'class': 'form-control col-sm-6'}),
            'email_text': CKEditorWidget(attrs={'class': 'form-control col-sm-6'}),
            'remarks': forms.TextInput(attrs={'class': 'form-control col-sm-6'}),
        }


class ReadOnlyNoticeTemplateForm(NoticeTemplateForm):
    class Meta:
        model = NoticeTemplate
        exclude = ['datetime_created']
        widgets = {
            'template_name': forms.TextInput(attrs={'class': 'form-control col-sm-6', 'readonly': True}),
            'template_event': forms.TextInput(attrs={'class': 'form-control col-sm-6', 'readonly': True}),
            'sms_sender_id': forms.TextInput(attrs={'class': 'form-control col-sm-6', 'readonly': True}),
            'message_template': forms.Textarea(attrs={'class': 'form-control col-sm-6', 'readonly': True}),
            'template_id': forms.TextInput(attrs={'class': 'form-control col-sm-6', 'readonly': True}),
            'header': forms.TextInput(attrs={'class': 'form-control col-sm-6', 'readonly': True}),
            'approval_date': forms.TextInput(attrs={'class': 'form-control col-sm-6', 'readonly': True}),
            'email_sender_id': forms.EmailInput(attrs={'class': 'form-control col-sm-6', 'readonly': True}),
            'email_subject': forms.TextInput(attrs={'class': 'form-control col-sm-6', 'readonly': True}),
            'email_text': CKEditorWidget(attrs={'class': 'form-control col-sm-6', 'readonly': True}),
            'remarks': forms.TextInput(attrs={'class': 'form-control col-sm-6', 'readonly': True}),
        }


class AddGatewayForm(forms.ModelForm):
    class Meta:
        model = Gateway
        fields = "__all__"
        widgets = {
            'code': forms.TextInput(attrs={'placeholder': 'Enter Gateway Code',
                                           'class': 'form-control'}),
            'name': forms.TextInput(attrs={'placeholder': 'Enter Gateway Name',
                                           'class': 'form-control'}),
        }


class PriorityGatewayForm(forms.ModelForm):
    class Meta:
        model = PaymentMode
        fields = "__all__"
        widgets = {
            'gateway': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.TextInput(attrs={'placeholder': 'Enter priority',
                                               'class': 'form-control'}),
        }


class GreetingForm(forms.ModelForm):
    class Meta:
        model = Greeting
        fields = "__all__"
        # exclude = ('parent_category_id',)
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'placeholder': 'Give a name for your greeting',
                    'class': 'form-control',
                    'required': 'required',
                }),

            'status': forms.Select(
                choices=Greeting.STATUS_CHOICES,
                attrs={
                    'class': 'form-control',
                }),

            'image': forms.FileInput(
                attrs={
                    'class': 'form-control',
                    'enctype': 'multipart/form-data',
                }),

            'trigger_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                    'required': 'required',
                    'min': str(timezone.now().date()),
                }, ),

            'trigger_time': forms.TimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'time',
                    # 'min': str(datetime.time(hour=9).strftime("hh:mm")),
                }
            ),

            'user_type': forms.Select(
                choices=Greeting.USER_TYPES,
                attrs={
                    'class': 'form-control',
                }
            ),
        }

    def clean_image(self):
        desired_width = settings.GREETINGS_SIZE[0]
        desired_height = settings.GREETINGS_SIZE[1]
        image = self.cleaned_data.get('image')
        if not image:
            raise forms.ValidationError("Greeting Image not found")
        else:
            w, h = get_image_dimensions(image)
            if w != desired_width:
                raise forms.ValidationError(
                    f"The image is {w} pixel wide. It's supposed to be {desired_width}px wide x {desired_height}px high")
            if h != desired_height:
                raise forms.ValidationError(
                    f"The image is {h} pixel high. It's supposed to be {desired_width}px wide x {desired_height}px high")
            return image

    # def clean_trigger_time(self):
    #     trigger_time = self.cleaned_data.get('trigger_time')
    #     trigger_date = self.cleaned_data.get('trigger_date')

    # def clean_trigger_date(self):
    #     pass
