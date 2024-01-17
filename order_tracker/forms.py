from django import forms


class OrderTrackerForm(forms.Form):
    order_number = forms.CharField(
        label='Enter Order Number',
        max_length=200,
        required=True,
        error_messages={'required': 'Please enter the order number.',
                        'max_length': 'Please enter a valid order number.'}
    )