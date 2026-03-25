from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from user.models import CustomUser
from book.models import Book, Review, Notification
from chat.models import Message


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    user_type = forms.ChoiceField(
        choices=CustomUser.USER_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Account Type"
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'user_type']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

        return cleaned_data

    
    
class LoginForm(forms.Form):
  
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if username and password:
            user = authenticate(request=self.request, username=username, password=password)
            if user is None:
                raise forms.ValidationError("Invalid email or password.")
        
        return cleaned_data
    

class CustomUserForm(UserChangeForm):
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        label="New Password"
    )
    confirm_new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        label="Confirm New Password"
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email'] 

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_new_password = cleaned_data.get('confirm_new_password')

        if new_password or confirm_new_password:
            if new_password != confirm_new_password:
                self.add_error('confirm_new_password', "Passwords do not match.")
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get('new_password')
        
        if new_password:
            user.set_password(new_password)
        
        if commit:
            user.save()
        
        return user