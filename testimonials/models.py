from django.db import models
from django.contrib.auth.models import User


class Testimonial(models.Model):
    RATING_CHOICES = (
        (1, '1 star'),
        (2, '2 stars'),
        (3, '3 stars'),
        (4, '4 stars'),
        (5, '5 stars'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=False, null=False)
    rating = models.IntegerField(choices=RATING_CHOICES, default=5)
    testimonial = models.TextField(blank=False, null=False)
    publish_testimonial = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Testimonial from {self.user.username} - Rating: {self.rating}"