from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
# from django.contrib.auth.models import User
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from user.models import CustomUser
        
class Book(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Cancel', 'Cancel'),
        ('Rejected', 'Rejected'),
        ('Exchanged', 'Exchanged'),
    ]

    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    genre = models.CharField(max_length=100)
    condition = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    image = models.ImageField(upload_to='book_images/', blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=20, default="Available", choices=STATUS_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)

    average_rating = models.FloatField(default=0)
    total_ratings = models.IntegerField(default=0)
    def __str__(self):
        return f"Book {self.title} has status {self.status}"
    def get_reviews(self):
        return self.reviews.all().order_by('-created_at')
    


class ExchangeRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Exchanged', 'Exchanged'),
        ('Rejected', 'Rejected'),
    ]

    requested_book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="requested_exchanges", blank=True, null=True)
    offered_book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="offered_exchanges", blank=True, null=True)
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="sent_exchanges", blank=True, null=True)
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="received_exchanges", blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} wants to exchange {self.offered_book} for {self.requested_book} request status {self.status}"


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    exchange_request = models.ForeignKey('ExchangeRequest', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.message
    
class Wishlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  
    book_title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.book_title} - {self.user.username}"



class Review(models.Model):
    BOOK_REVIEW = 'book'
    USER_REVIEW = 'user'  

    REVIEW_CHOICES = [
        (BOOK_REVIEW, 'Book'),
        (USER_REVIEW, 'User'),
    ]

    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True, blank=True)
    reviewed_user = models.ForeignKey( 
        CustomUser, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='received_reviews'
    )
    reviewer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    review_text = models.TextField(null=True, blank=True)
    review_type = models.CharField(max_length=10, choices=REVIEW_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.reviewer.username} ({self.get_review_type_display()})"