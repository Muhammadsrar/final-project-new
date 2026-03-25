from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from user.models import CustomUser

class Message(models.Model):
    sender = models.ForeignKey(CustomUser, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(CustomUser, related_name="received_messages", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False) 
    
    def __str__(self):
        return f"From {self.sender} to {self.receiver} - {self.timestamp}"
