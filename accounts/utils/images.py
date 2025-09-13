# accounts/utils/images.py
from io import BytesIO
import os
import sys
from PIL import Image, ImageOps
from django.core.files.uploadedfile import InMemoryUploadedFile

# Paramètres de normalisation
TARGET_SIZE = 512     # avatar carré
QUALITY = 85          # qualité d’encodage

def process_avatar(uploaded_file) -> InMemoryUploadedFile:
    """
    Normalise une photo de profil :
    - Corrige l’orientation EXIF
    - Crop centre → carré
    - Resize en 512x512 (LANCZOS)
    - Encode en WebP (fallback JPEG)
    - Supprime les métadonnées
    Retourne un InMemoryUploadedFile prêt pour un ImageField.
    """
    uploaded_file.seek(0)
    img = Image.open(uploaded_file)

    # Orientation EXIF (selfies en portrait, etc.)
    img = ImageOps.exif_transpose(img)

    # Mode couleur compatible (pas d’alpha pour WebP/JPEG lossy)
    if img.mode in ("P", "RGBA"):
        img = img.convert("RGB")

    # Crop centre → carré
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side))

    # Resize haute qualité
    img = img.resize((TARGET_SIZE, TARGET_SIZE), Image.Resampling.LANCZOS)

    # Tentative WebP (méthode=6). Fallback JPEG si besoin.
    buffer = BytesIO()
    out_ext = "webp"
    out_format = "WEBP"
    try:
        img.save(buffer, format=out_format, quality=QUALITY, method=6)
    except Exception:
        buffer = BytesIO()
        out_ext = "jpg"
        out_format = "JPEG"
        img.save(buffer, format=out_format, quality=QUALITY, optimize=True)

    buffer.seek(0)

    base_name, _ = os.path.splitext(getattr(uploaded_file, "name", "avatar"))
    new_name = f"{base_name}.{out_ext}"
    content_type = f"image/{'jpeg' if out_ext == 'jpg' else out_ext}"

    return InMemoryUploadedFile(
        buffer,
        field_name=getattr(uploaded_file, "field_name", "profile_image"),
        name=new_name,
        content_type=content_type,
        size=sys.getsizeof(buffer),
        charset=None,
    )
