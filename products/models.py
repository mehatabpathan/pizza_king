from django.db import models
from cloudinary.models import CloudinaryField
from django.utils.text import slugify


class Product(models.Model):
    name = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        unique=True)
    slug = models.SlugField(
        max_length=100,
        null=False,
        blank=False,
        unique=True)
    description = models.TextField(
        null=False,
        blank=False)
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=False,
        blank=False)
    image = CloudinaryField(
        'image',
        null=True,
        blank=True)
    is_spicy = models.BooleanField(
        default=False)
    is_vegetarian = models.BooleanField(
        default=False)
    is_premium = models.BooleanField(
        default=False)
    is_seafood = models.BooleanField(
        default=False)
    is_new = models.BooleanField(
        default=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Topping(models.Model):
    MEATS = 'Meats'
    SEAFOOD = 'Seafood'
    VEGETABLES = 'Vegetables'
    FRUITS = 'Fruits'
    CHEESES = 'Cheeses'
    OTHER = 'Other'

    CATEGORY_CHOICES = [
        (MEATS, 'Meats'),
        (SEAFOOD, 'Seafood'),
        (VEGETABLES, 'Vegetables'),
        (FRUITS, 'Fruits'),
        (CHEESES, 'Cheeses'),
        (OTHER, 'Other'),
    ]

    name = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        unique=True)
    slug = models.SlugField(
        max_length=100,
        null=False,
        blank=False,
        unique=True)
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=False,
        blank=False)
    image = CloudinaryField(
        'image',
        null=True,
        blank=True)
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default=OTHER,
    )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Topping, self).save(*args, **kwargs)

    def __str__(self):
        return self.name