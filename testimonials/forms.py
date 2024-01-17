from django import forms
from .models import Testimonial


class TestimonialForm(forms.ModelForm):
    RATING_CHOICES = (
        (1, '1 star'),
        (2, '2 stars'),
        (3, '3 stars'),
        (4, '4 stars'),
        (5, '5 stars'),
    )

    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect)

    class Meta:
        model = Testimonial
        fields = ['name', 'testimonial', 'rating', 'publish_testimonial']
        labels = {
            'testimonial': 'Please write a testimonial',
            'publish_testimonial': 'Allow your testimonial to be published',
        }
        widgets = {
            'testimonial': forms.Textarea(attrs={'rows': 10}),
        }

    name = forms.CharField(
        label='Name',
        max_length=100,
        required=True,
        error_messages={
            'required': 'Please provide your name for the testimonial.',
            'max_length': 'The name cannot exceed 100 characters.'
        }
    )

    testimonial = forms.CharField(
        label='Testimonial',
        widget=forms.Textarea(attrs={'rows': 10}),
        required=True,
        error_messages={
            'required': 'Please write your testimonial.',
        }
    )

    rating = forms.ChoiceField(
        choices=Testimonial.RATING_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        error_messages={
            'required': 'Please select a rating for the testimonial.'
        }
    )

    def clean_rating(self):
        rating = self.cleaned_data['rating']
        rating_val = [str(choice[0]) for choice in Testimonial.RATING_CHOICES]
        if rating not in rating_val:
            raise forms.ValidationError('Invalid rating value.')
        return rating

    def clean_name(self):
        name = self.cleaned_data['name']
        min_length = 5
        if len(name) < min_length:
            raise forms.ValidationError(
                f"Name must be at least {min_length} characters long.")
        return name

    def clean_testimonial(self):
        testimonial = self.cleaned_data['testimonial']
        min_length = 20
        if len(testimonial) < min_length:
            raise forms.ValidationError(
                f"Testimonial must be at least {min_length} characters long."
            )
        return testimonial