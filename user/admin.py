from django.contrib import admin
from book.models import Book, ExchangeRequest, Notification, Review
from chat.models import Message
from user.models import CustomUser

admin.site.register(CustomUser)
admin.site.register(Book)
admin.site.register(ExchangeRequest)
admin.site.register(Notification)
admin.site.register(Message)
admin.site.register(Review)
