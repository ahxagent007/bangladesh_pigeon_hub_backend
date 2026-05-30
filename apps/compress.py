"""
Image compression utility used by all model save() methods.
Converts uploaded images to progressive JPEG and shrinks them
to a sensible maximum dimension before writing to storage.
"""

import os
from io import BytesIO
from typing import Optional

from django.core.files.base import ContentFile
from PIL import Image, ImageOps


def compress_image(field_file, max_width: int = 1200, quality: int = 65) -> Optional[ContentFile]:
    """
    Compress and resize an ImageField's in-memory upload.

    Call this inside a model's save() only when the field has
    not yet been committed (i.e. it is a fresh upload):

        if self.image and not self.image._committed:
            compressed = compress_image(self.image)
            if compressed:
                self.image = compressed

    Returns a ContentFile on success, or None so the caller can
    fall back to the original file without crashing.
    """
    try:
        img = Image.open(field_file)

        # Honour EXIF orientation (phones, cameras).
        img = ImageOps.exif_transpose(img)

        # JPEG does not support transparency — flatten onto white.
        if img.mode in ('RGBA', 'PA', 'LA', 'P'):
            bg = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            alpha = img.split()[-1] if img.mode in ('RGBA', 'PA', 'LA') else None
            bg.paste(img, mask=alpha)
            img = bg
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # Shrink proportionally if wider than max_width.
        if img.width > max_width:
            new_height = int(img.height * max_width / img.width)
            img = img.resize((max_width, new_height), Image.LANCZOS)

        buf = BytesIO()
        img.save(buf, format='JPEG', quality=quality, optimize=True, progressive=True)
        buf.seek(0)

        # Keep original stem, force .jpg extension.
        original_name = getattr(field_file, 'name', None) or 'image'
        stem = os.path.splitext(os.path.basename(original_name))[0]
        return ContentFile(buf.read(), name=stem + '.jpg')

    except Exception:
        # Never crash an upload due to compression failure.
        return None
