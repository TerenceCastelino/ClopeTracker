from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login
from .forms import UserRegistrationForm

def signup(request):
    """
    Affiche un formulaire d'inscription.
    À la validation :
      - crée l'utilisateur
      - connecte l'utilisateur
      - redirige vers la home
    """
    if request.method == "POST":
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()  # UserCreationForm s'occupe du hash du mot de passe
            login(request, user)  # auto-login
            return redirect("home")  # adapte si ton nom de route diffère
    else:
        form = UserRegistrationForm()
    return render(request, "accounts/signup.html", {"form": form})
