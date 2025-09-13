# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserRegistrationForm(UserCreationForm):
    # on force l’email (utile pour reset mot de passe plus tard)
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "birth_date",
            "phone",
            "profile_image",
            "password1",
            "password2",
        ]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
        }

    # (optionnel) si tu veux imposer l’unicité de l’email
    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Un compte utilise déjà cet email.")
        return email
