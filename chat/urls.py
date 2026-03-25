from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('chats/', views.chat_list, name='chat_list'),
    path('inbox/<int:user_id>/', views.inbox, name='inbox'),
   
]
