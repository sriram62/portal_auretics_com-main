from django import forms
from .models import Order, Address
from django.contrib.auth.models import User

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = "__all__"
        exclude = ('user',)
        widgets = {
            'house_number': forms.TextInput(attrs={'placeholder': 'Enter House Number','disabled':'disabled'}),
            # 'address_line': forms.TextInput(attrs={'placeholder': 'Enter Address  '}),
            'Landmark': forms.TextInput(attrs={'placeholder': 'Enter Landmark','disabled':'disabled'}),
            'address': forms.TextInput(attrs={'placeholder': 'Enter Address','disabled':'disabled'}),
            'city': forms.TextInput(attrs={'placeholder': 'Enter City','disabled':'disabled'}),
            'street': forms.TextInput(attrs={'placeholder': 'Enter Street','disabled':'disabled'}),
            'street': forms.TextInput(attrs={'placeholder': 'Enter Street','disabled':'disabled'}),
            # 'country': forms.
            'pin': forms.TextInput(attrs={'placeholder': 'Enter PinCode','disabled':'disabled'}),
            'mobile': forms.TextInput(attrs={'placeholder': 'Enter Mobile Number','disabled':'disabled'}),
            'alternate_mobile': forms.TextInput(attrs={'placeholder': 'Enter Alternate Mobile Number','disabled':'disabled'}),
            # 'address_type': forms.TextInput(attrs={'placeholder': 'Enter Your Full Address'}),

        }
        # widgets = {
        #     'name': forms.TextInput(attrs={'placeholder': 'Enter Your Name'}),
        #     'email': forms.TextInput(attrs={'placeholder': 'Email '}),
        #     'postal_code': forms.TextInput(attrs={'placeholder': 'Pin Code'}),
        #     'address': forms.TextInput(attrs={'placeholder': 'Enter Your Full Address'}),

        # }


class CartForm(forms.Form):
    quantity = forms.IntegerField(initial='1')
    product_id = forms.IntegerField(widget=forms.HiddenInput)
    user = forms.ModelChoiceField(
            queryset=User.objects.all(),
            widget=forms.Select(attrs={'style': 'width:180px;'}),
            required=True)

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(CartForm, self).__init__(*args, **kwargs)

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude = ('paid',)
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter Your Name'}),
            'email': forms.TextInput(attrs={'placeholder': 'Email '}),
            'postal_code': forms.TextInput(attrs={'placeholder': 'Pin Code'}),
            'address': forms.TextInput(attrs={'placeholder': 'Enter Your Full Address'}),

        }
