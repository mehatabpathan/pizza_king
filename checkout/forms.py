from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    """
    Form for the user to fill in their details
    """
    class Meta:
        model = Order
        fields = ('full_name', 'email', 'phone_number',
                  'street_address1', 'street_address2',
                  'postcode')

    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto-generated
        labels and set autofocus on first field
        """
        super().__init__(*args, **kwargs)
        placeholders = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'postcode': 'Postal Code',
            'street_address1': 'Street Address 1',
            'street_address2': 'Street Address 2',
        }

        self.fields['full_name'].widget.attrs['autofocus'] = True
        for field in self.fields:
            if self.fields[field].required:
                placeholder = f'{placeholders[field]} *'
            else:
                placeholder = placeholders[field]
            self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = 'stripe-style-input'
            self.fields[field].label = False

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']

        if len(phone_number) < 8:
            raise forms.ValidationError("Please enter a valid phone number.")

        return phone_number

    def clean_postcode(self):
        postcode = self.cleaned_data['postcode']

        if postcode and len(postcode) < 7:
            raise forms.ValidationError("Please enter a valid postcode.")

        return postcode