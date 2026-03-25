from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User

class CustomUser(AbstractUser):
    Owner = 'Owner'
    Seeker = 'Seeker'
    USER_TYPES = (
        ('Owner', 'Owner'),
        ('Seeker', 'Seeker'),
        
    )

    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

    owner_rating = models.FloatField(default=0)
    total_owner_ratings = models.IntegerField(default=0)

    def update_rating(self):
        reviews = self.owner_reviews.all()
        if reviews.exists():
            self.owner_rating = sum(review.rating for review in reviews) / reviews.count()
            self.total_owner_ratings = reviews.count()
        else:
            self.owner_rating = 0
            self.total_owner_ratings = 0
        self.save()
        

class PasswordResetToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        from datetime import timedelta, timezone
        return self.created_at >= timezone.now() - timedelta(hours=1)