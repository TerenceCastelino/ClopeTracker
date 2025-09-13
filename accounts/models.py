# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.templatetags.static import static  # fallback image par défaut

class User(AbstractUser):
    """
    Modèle utilisateur personnalisé basé sur AbstractUser.
    Champs métier additionnels + champ d’avatar.
    """

    # Date de naissance (optionnelle)
    birth_date = models.DateField(
        null=True, blank=True, verbose_name="Date de naissance"
    )

    # Téléphone (optionnel)
    phone = models.CharField(
        max_length=20, null=True, blank=True, verbose_name="Téléphone"
    )

    # Rôle (métier simple)
    ROLE_CHOICES = [("admin", "Admin"), ("member", "Membre")]
    role = models.CharField(
        max_length=10, choices=ROLE_CHOICES, default="member", verbose_name="Rôle"
    )

    # Groupe (placeholder – sera remplacé par une FK plus tard)
    group_id = models.IntegerField(
        null=True, blank=True, verbose_name="Identifiant du groupe"
    )

    # Compteur total de cigarettes
    cigarettes_smoked = models.PositiveIntegerField(
        default=0, verbose_name="Cigarettes fumées depuis l’inscription"
    )

    # Avatar uploadé par l’utilisateur → va dans MEDIA_ROOT/profiles/
    # (L’image par défaut est gérée via STATIC en fallback dans profile_image_url)
    profile_image = models.ImageField(
        upload_to="profiles/", blank=True, null=True, verbose_name="Photo de profil"
    )

    @property
    def profile_image_url(self):
        """
        URL de la photo :
        - si l’utilisateur a uploadé une image → URL MEDIA
        - sinon → fallback vers l’image par défaut en STATIC
        """
        if self.profile_image:
            return self.profile_image.url
        return static("image/profiles/imageProfilDefaut.png")

    def __str__(self):
        return self.username
