from django import forms
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user',)

    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto-generated
        labels and set autofocus on first field
        """
        super().__init__(*args, **kwargs)
        placeholders = {
            'default_full_name': 'Full Name',
            'default_phone_number': 'Phone Number',
            'default_postcode': 'Postal Code',
            'default_street_address1': 'Street Address 1',
            'default_street_address2': 'Street Address 2',
        }

        self.fields['default_full_name'].widget.attrs['autofocus'] = True
        for field in self.fields:
            if self.fields[field].required:
                placeholder = f'{placeholders[field]} *'
            else:
                placeholder = placeholders[field]
            self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = 'border-custom'
            self.fields[field].label = False

    default_full_name = forms.CharField(
        label='Full Name',
        max_length=80,
        error_messages={
            'required': 'Please enter your full name.',
            'max_length': 'Full name should have at most 80 characters.'
        }
    )

    default_street_address1 = forms.CharField(
        label='Street Address 1',
        max_length=80,
        error_messages={
            'required': 'Please enter your street address.',
            'max_length': 'Street Address 1 should have at most 80 characters.'
        }
    )

    default_street_address2 = forms.CharField(
        label='Street Address 2',
        max_length=80,
        error_messages={
            'max_length': 'Street Address 2 should have at most 80 characters.'
        }
    )

    default_phone_number = forms.CharField(
        label='Phone Number',
        max_length=20,
        error_messages={
            'required': 'Please enter your phone number.',
            'max_length': 'Phone number should have at most 20 characters.'
        }
    )

    default_postcode = forms.CharField(
        label='Postal Code',
        max_length=20,
        error_messages={
            'required': 'Please enter your postal code.',
            'max_length': 'Postal code should have at most 20 characters.'
        }
    )

    def clean_default_phone_number(self):
        phone_number = self.cleaned_data['default_phone_number']

        if len(phone_number) < 8:
            raise forms.ValidationError("Please enter a valid phone number.")

        return phone_number

    def clean_default_postcode(self):
        postcode = self.cleaned_data['default_postcode']

        if postcode and len(postcode) < 7:
            raise forms.ValidationError("Please enter a valid postcode.")

        return postcode