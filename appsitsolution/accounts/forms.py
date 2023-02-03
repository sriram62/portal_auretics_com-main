from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError
from . import models
# from shop.model import Address

# class AddressForm(forms.ModelForm):
#     class Meta:
#         model = Address
#         fields = __all__

class KycForm(forms.ModelForm):
    class Meta:
        model = models.Kyc
        fields = ['pan_number','pan_file', 'id_proof_type',
                  'id_proof_file', 'address_proof_type', 'address_proof_file' ]
        widgets = {
            'id_proof_file': forms.FileInput(attrs={'enctype': 'multipart/form-data', 'accept':"image/x-png,image/gif,image/jpeg,image/png,application/pdf"}),
            'address_proof_file': forms.FileInput(attrs={'enctype': 'multipart/form-data', 'accept':"image/x-png,image/gif,image/jpeg,image/png,application/pdf"}),
            'pan_file': forms.FileInput(attrs={'enctype': 'multipart/form-data', 'accept':"image/x-png,image/gif,image/jpeg,image/png,application/pdf"}),
        }



class BankAccountDetailsForm(forms.ModelForm):
    class Meta:
        model = models.BankAccountDetails
        fields = ['distributors_name_in_bank_account',
                  'bank_name',
                  'account_number',
                  'ifsc_code',
                  'branch_name',
                  'cheque_photo',

                  'age_confirmation',
                  'self_declaration',
                  'patron_id',
                  'nameFuzzy'
                ]
        widgets = {
            'self_declaration':forms.CheckboxInput(attrs= {'id' : 'deid'}),
            'age_confirmation': forms.CheckboxInput(attrs = {'id': 'ageid'}),
            'cheque_photo': forms.FileInput(attrs={'enctype': 'multipart/form-data', 'accept':"image/x-png,image/gif,image/jpeg,image/png,application/pdf"}),
        }

class BankAccountDetailsForm_for_user(forms.ModelForm):
    class Meta:
        model = models.BankAccountDetails
        fields = ['distributors_name_in_bank_account',
                  'bank_name',
                  'account_number',
                  'ifsc_code',
                  'branch_name',
                  'cheque_photo',
                   'patron_id'
                ]
        widgets = {
            'cheque_photo': forms.FileInput(attrs={'enctype': 'multipart/form-data', 'accept':"image/x-png,image/gif,image/jpeg,image/png,application/pdf"}),
        }


class ProfileForm(forms.ModelForm):
    email=forms.EmailField(widget=forms.EmailInput(attrs={'disabled' : 'disabled'}))
    bio = forms.Textarea()

    class Meta:
        model = models.Profile
        fields = [
            "avatar",
            # "user",
			"first_name",
			"last_name",
			"email",
			"phone_number",
			"user_type",
			"status",
# 			"address",
# 			"city",
# 			"state",
# 			"country",
# 			"referral_id",
# 			"reference_user_id",

        ]
        exclude = ('shipping_address',)
        widgets = {
            'avatar': forms.FileInput(attrs={'type':'file', 'enctype': 'multipart/form-data','id':'profile_id'}),
            'first_name': forms.TextInput(attrs={'disabled':'disabled'}),
            'last_name': forms.TextInput(attrs={'disabled':'disabled'}),
            'email': forms.TextInput(attrs={'disabled':'disabled'}),
            'phone_number': forms.TextInput(attrs={'disabled':'disabled'}),
            'user_type': forms.TextInput(attrs={'disabled':'disabled'}),
            'status': forms.TextInput(attrs={'disabled':'disabled'})
        }

# class ReferalForm(forms.ModelForm):
#     class Meta:
#         model = models.ReferralCode
#         fields = [
#             'referal_by','referral_code',
#         ]
#         widgets = {
#             'referal_by': forms.TextInput(attrs={'type':'text'}),
#             'referral_code': forms.TextInput(attrs={'type':'text'})
#         }


class CreateUserForm(UserCreationForm):
	class Meta:
		model = User
		fields = ['username', 'email', 'password1', 'password2']



# class CustomUserCreationForm(forms.Form):
#     username = forms.CharField(label='Enter Username', min_length=4, max_length=150)
#     email = forms.EmailField(label='Enter email')
#     password1 = forms.CharField(label='Enter password', widget=forms.PasswordInput)
#     password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)

#     def clean_username(self):
#         username = self.cleaned_data['username'].lower()
#         r = User.objects.filter(username=username)
#         if r.count():
#             raise  ValidationError("Username already exists")
#         return username

#     def clean_email(self):
#         email = self.cleaned_data['email'].lower()
#         r = User.objects.filter(email=email)
#         if r.count():
#             raise  ValidationError("Email already exists")
#         return email

#     def clean_password2(self):
#         password1 = self.cleaned_data.get('password1')
#         password2 = self.cleaned_data.get('password2')

#         if password1 and password2 and password1 != password2:
#             raise ValidationError("Password don't match")

#         return password2

#     def save(self, commit=True):
#         user = User.objects.create_user(
#             self.cleaned_data['username'],
#             self.cleaned_data['email'],
#             self.cleaned_data['password1']
#         )
#         return user
# def AddressForm():
#     return None
