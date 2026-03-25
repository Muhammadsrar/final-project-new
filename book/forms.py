from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from user.models import CustomUser
from book.models import Book, Review, Wishlist


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'genre', 'condition', 'location', 'image', 'status', 'url']
        labels = {
            'title': 'Book Title',
            'author': 'Author Name',
            'genre': 'Genre',
            'condition': 'Book Condition',
            'location': 'Your Location',
            'image': 'Image',
            'status': 'Book Status',
            'url': 'External Link (e.g., Amazon, Daraz)',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter book title'}),
            'author': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter author name'}),
            'genre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Genre (e.g., Fiction, Science)'}),
            'condition': forms.Select(choices=[('New', 'New'), ('Like New', 'Like New'), ('Used - Good', 'Used - Good'), ('Used - Acceptable', 'Used - Acceptable')], attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your City or Area'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'status': forms.Select(choices=Book.STATUS_CHOICES, attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter external link (optional)'}),
        }
      

class WishlistForm(forms.ModelForm):
    class Meta:
        model = Wishlist
        fields = ['book_title', 'author']
        widgets = {
            'book_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Book Title'}),
            'author': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Author (Optional)'}),
        }

     
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'review_text', 'review_type', 'book', 'reviewed_user']
        widgets = {
            'book': forms.HiddenInput(),
            'reviewed_user': forms.HiddenInput(),
            'review_type': forms.HiddenInput()
        }
