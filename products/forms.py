from django import forms
from .widgets import CustomCloudinaryField
from .models import Product, Topping


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ['name',
                  'description',
                  'price',
                  'image',
                  'is_spicy',
                  'is_vegetarian',
                  'is_premium',
                  'is_seafood',
                  'is_new']

    image = CustomCloudinaryField(label='Image',
                                  required=False)

    name = forms.CharField(
        label='Name',
        max_length=100,
        required=True,
        error_messages={
            'required': 'Please provide the product name.',
            'max_length': 'The name cannot exceed 100 characters.'
        }
    )

    description = forms.CharField(
        label='Description',
        widget=forms.Textarea,
        required=True,
        error_messages={
            'required': 'Please provide the product description.',
        }
    )

    price = forms.DecimalField(
        label='Price',
        max_digits=6,
        decimal_places=2,
        required=True,
        error_messages={
            'required': 'Please specify the product price.',
            'max_digits': 'The price should have at most 6 digits.'
        }
    )

    def clean_name(self):
        name = self.cleaned_data['name']
        min_length = 5
        if len(name) < min_length:
            raise forms.ValidationError(
                f"Name must be at least {min_length} characters long."
                )
        return name

    def clean_description(self):
        description = self.cleaned_data['description']
        min_length = 20
        if len(description) < min_length:
            raise forms.ValidationError(
                f"Description must be at least {min_length} characters long."
                )
        return description


class ToppingForm(forms.ModelForm):
    class Meta:
        model = Topping
        fields = ['name', 'price', 'image', 'category']

    image = CustomCloudinaryField(label='Image',
                                  required=False)

    name = forms.CharField(
        label='Name',
        max_length=100,
        required=True,
        error_messages={
            'required': 'Please provide the topping name.',
            'max_length': 'The name cannot exceed 100 characters.'
        })

    price = forms.DecimalField(
        label='Price',
        max_digits=6,
        decimal_places=2,
        required=True,
        error_messages={
            'required': 'Please specify the topping price.',
            'max_digits': 'The price should have at most 6 digits.'
        })

    CATEGORY_CHOICES = Topping.CATEGORY_CHOICES

    category = forms.ChoiceField(
        label='Category',
        choices=CATEGORY_CHOICES,
        required=True,
        error_messages={
            'required': 'Please specify the topping category.',
        })

    def clean_category(self):
        category = self.cleaned_data['category']
        if category not in dict(self.fields['category'].choices).keys():
            raise forms.ValidationError(
                'Invalid choice. Please select a valid category.')
        return category


class PizzaFilterForm(forms.Form):
    is_spicy = forms.BooleanField(label='Spicy',
                                  required=False)
    is_vegetarian = forms.BooleanField(label='Vegetarian',
                                       required=False)
    is_premium = forms.BooleanField(label='Premium',
                                    required=False)
    is_seafood = forms.BooleanField(label='Seafood',
                                    required=False)
    is_new = forms.BooleanField(label='New',
                                required=False)