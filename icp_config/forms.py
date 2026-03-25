# book/forms.py (add this at the bottom)
from django import forms
from .models import ICPProfile

from django import forms
from .models import ICPProfile

class ICPForm(forms.ModelForm):
    class Meta:
        model = ICPProfile
        fields = ['target_industries', 'max_company_size', 'min_company_size', 'target_roles', 'target_regions']
        widgets = {
            'target_industries': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Technology, Healthcare'}),
            'target_roles': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Head of Sales, VP Marketing'}),
            'target_regions': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., USA, Europe'}),
            'max_company_size': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'min_company_size': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

    def clean(self):
        cleaned_data = super().clean()
        min_size = cleaned_data.get('min_company_size')
        max_size = cleaned_data.get('max_company_size')
        target_industries = cleaned_data.get('target_industries')
        roles = cleaned_data.get('target_roles')

        if not target_industries:
            raise forms.ValidationError("At least one target industry is required.")
        if not roles:
            raise forms.ValidationError("At least one target role is required.")
        if min_size > max_size:
            raise forms.ValidationError("Minimum company size cannot exceed maximum size.")