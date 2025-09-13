# accounts/signals.py
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.conf import settings

from .models import User
from .utils.images import process_avatar

# --- Helpers suppression de fichier ---
def _delete_file_safely(field_file):
    """
    Supprime physiquement le fichier si présent.
    Ne lève pas d’exception (fail-safe).
    """
    try:
        if field_file and field_file.name and field_file.storage.exists(field_file.name):
            field_file.storage.delete(field_file.name)
    except Exception:
        pass

@receiver(pre_save, sender=User)
def user_avatar_pre_save(sender, instance: User, **kwargs):
    """
    Avant de sauver :
    - Si un nouvel avatar est fourni → on le normalise
    - On mémorise l’ancienne image pour la supprimer après save
    """
    # On cherche l’ancien user (si existe) pour comparer les fichiers
    if instance.pk:
        try:
            old = User.objects.get(pk=instance.pk)
        except User.DoesNotExist:
            old = None
    else:
        old = None

    # Si un nouveau fichier est uploadé, on le traite
    if instance.profile_image and hasattr(instance.profile_image, "file"):
        try:
            processed = process_avatar(instance.profile_image.file)
            # Remplace le contenu du champ sans save immédiat
            instance.profile_image.save(processed.name, processed, save=False)
        except Exception:
            # En cas d’échec, on garde l’original
            pass

    # Si l’ancien fichier existe et que le nom a changé → à supprimer après save
    if old and old.profile_image and instance.profile_image and old.profile_image.name != instance.profile_image.name:
        instance._old_profile_image_to_delete = old.profile_image
    # Cas où on remplace une image par “rien” (clear)
    elif old and old.profile_image and not instance.profile_image:
        instance._old_profile_image_to_delete = old.profile_image

@receiver(post_save, sender=User)
def user_avatar_post_save(sender, instance: User, created, **kwargs):
    """
    Après save :
    - Si on a marqué une ancienne image → on la supprime maintenant
    """
    old_file = getattr(instance, "_old_profile_image_to_delete", None)
    if old_file:
        _delete_file_safely(old_file)
        try:
            delattr(instance, "_old_profile_image_to_delete")
        except Exception:
            pass

@receiver(post_delete, sender=User)
def user_avatar_post_delete(sender, instance: User, **kwargs):
    """
    À la suppression du user :
    - Supprime l'image associée du storage
    """
    if instance.profile_image:
        _delete_file_safely(instance.profile_image)
