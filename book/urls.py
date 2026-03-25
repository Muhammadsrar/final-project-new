from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    
    path('add_book/', views.add_book, name='add_book'),
    path('my_books/', views.my_books, name='my_books'),
    path('book_list/', views.book_list, name='book_list'),
    path('edit_book/<int:book_id>', views.edit_book, name='edit_book'),
    path('delete_book/<int:book_id>', views.delete_book, name='delete_book'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('add_wishlist/', views.add_to_wishlist, name='add_wishlist'),
    path('delete_wishlist/<int:wishlist_id>/', views.delete_from_wishlist, name='delete_from_wishlist'),
    path('book_details/<int:book_id>/', views.book_details_view, name='book_details'),
    
    path('search/', views.search, name='search'),


    path('mark_as_read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
    
    path('exchange_request/<int:book_id>/', views.exchange_request, name='exchange_request'),
    path('exchange_status/', views.exchange_status, name='exchange_status'),
    path('accept_exchange/<int:request_id>/', views.accept_exchange_request, name='accept_exchange_request'),
    path('reject_exchange/<int:request_id>/', views.reject_exchange_request, name='reject_exchange_request'),
    path('cancel_exchange_request/<int:request_id>/', views.cancel_exchange_request, name='cancel_exchange_request'),
    path('exchanged_books/', views.exchanged_books, name='exchanged_books'),
    # path('exchange/<int:book_id>/', views.exchange, name='exchange'),
    path('get_owner_books/', views.get_owner_books, name='get_owner_books'),

    path('get_user_books/', views.get_user_books, name='get_user_books'),
    path('add_reviews/', views.add_reviews, name='add_reviews'),
    path('reviews/', views.view_reviews, name='view_reviews'),    
    path('user_review/<int:user_id>/', views.user_review, name='user_review'),
    path('book_review/<int:book_id>/', views.book_review, name='book_review'),
]
