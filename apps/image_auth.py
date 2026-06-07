from __future__ import annotations

"""
Image authenticity analysis.

Scores how much an uploaded image appears to have been edited (0 = raw, 100 = heavily edited).

IMPORTANT: Call analyze_image_edit() BEFORE compress_image() — compression strips all EXIF.

Signals (in order of reliability):
  1. EXIF Software / ProcessingSoftware — editing tools leave a direct fingerprint
  2. Missing EXIF on a JPEG — common after editing or app re-export
  3. DateTimeOriginal vs DateTime mismatch — modified after capture
  4. File format — PNG/WebP are uncommon for direct camera output
  5. ELA (Error Level Analysis) — JPEG recompression variance across the image
"""

import io
import math
from PIL import Image, ImageChops
from PIL.ExifTags import TAGS


# Editing app/tool keywords → score contribution (0-100)
_EDIT_SOFTWARE = {
    'photoshop':    78,
    'lightroom':    72,
    'gimp':         70,
    'affinity':     65,
    'darktable':    62,
    'rawtherapee':  60,
    'capture one':  65,
    'on1':          60,
    'luminar':      65,
    'snapseed':     55,
    'picsart':      60,
    'vsco':         55,
    'facetune':     82,
    'pixlr':        65,
    'canva':        62,
    'meitu':        72,
    'afterlight':   55,
    'instagram':    52,
    'facebook':     48,
    'twitter':      45,
    'whatsapp':     40,
    'telegram':     38,
    'paint.net':    58,
    'paint':        48,
    'photos':       28,   # Apple Photos (minor edits)
    'preview':      25,   # macOS Preview (minor edits)
}

# Camera / firmware keywords — negative signal (reduces score)
_CAMERA_SW = [
    'nikon', 'canon', 'sony', 'fujifilm', 'olympus', 'pentax',
    'panasonic', 'leica', 'hasselblad', 'sigma', 'silkypix', 'picasa',
]


def _read_exif(img: Image.Image) -> dict:
    """Return {tag_name: value} from JPEG EXIF, empty dict on failure."""
    try:
        raw = img._getexif()
        if raw:
            return {TAGS.get(tid, str(tid)): val for tid, val in raw.items()}
    except Exception:
        pass
    return {}


def _ela(img: Image.Image, quality: int = 92) -> int:
    """
    Error Level Analysis: re-save image at known quality and measure
    difference from original. Returns 0–35.

    A uniform low-error pattern (typical of re-encoded images) or
    high-variance blocks (composite areas) both indicate editing.
    """
    try:
        rgb = img.convert('RGB')
        buf = io.BytesIO()
        rgb.save(buf, 'JPEG', quality=quality)
        buf.seek(0)
        resaved = Image.open(buf).convert('RGB')
        diff    = ImageChops.difference(rgb, resaved)
        hist    = diff.histogram()
        rms     = math.sqrt(
            sum((i % 256) ** 2 * v for i, v in enumerate(hist))
            / max(rgb.width * rgb.height * 3, 1)
        )
        return min(35, int(rms * 6))
    except Exception:
        return 0


def analyze_image_edit(image_field) -> tuple[int, str]:
    """
    Analyze an in-memory ImageField upload for editing signals.

    Args:
        image_field: An InMemoryUploadedFile / TemporaryUploadedFile
                     (the raw value of a model's ImageField before save).

    Returns:
        (score, notes)
        score — int 0–100 where:
            0–20   raw / unedited
            21–50  possibly processed
            51–75  likely edited
            76–100 heavily edited
        notes — semicolon-separated human-readable explanation
    """
    score   = 0
    signals = []

    # ── Open image ───────────────────────────────────────────────────────────
    try:
        image_field.seek(0)
        img = Image.open(image_field)
        img.load()
        fmt  = (img.format or '').upper()
        exif = _read_exif(img)
    except Exception:
        return 0, ''

    # ── 1. Software field ─────────────────────────────────────────────────────
    sw_raw  = exif.get('Software') or exif.get('ProcessingSoftware') or ''
    sw      = str(sw_raw).lower().strip()

    if sw:
        matched_edit = False
        for kw, contrib in _EDIT_SOFTWARE.items():
            if kw in sw:
                score = max(score, contrib)
                signals.append(f'Editing software detected: {str(sw_raw).strip()}')
                matched_edit = True
                break
        if not matched_edit:
            for kw in _CAMERA_SW:
                if kw in sw:
                    score = max(0, score - 5)
                    signals.append(f'Camera firmware: {str(sw_raw).strip()}')
                    break

    # ── 2. Missing / stripped EXIF ────────────────────────────────────────────
    if fmt == 'JPEG':
        if not exif:
            score += 30
            signals.append('No EXIF metadata (often stripped after editing or app re-export)')
        elif 'Make' not in exif and 'Model' not in exif and not sw:
            score += 15
            signals.append('No camera make/model in EXIF')

    # ── 3. Date discrepancy ───────────────────────────────────────────────────
    dt_orig = exif.get('DateTimeOriginal') or exif.get('DateTimeDigitized')
    dt_mod  = exif.get('DateTime')
    if dt_orig and dt_mod and dt_orig != dt_mod:
        score += 20
        signals.append(f'Capture date ({dt_orig}) differs from modification date ({dt_mod})')

    # ── 4. File format ────────────────────────────────────────────────────────
    if fmt == 'PNG':
        score += 12
        signals.append('PNG format — screenshots and edited exports are often PNG')
    elif fmt == 'WEBP' and not exif:
        score += 8
        signals.append('WebP with no metadata — re-encoded')
    elif fmt == 'BMP':
        score += 18
        signals.append('BMP format — not typical for camera output')

    # ── 5. ELA (JPEG only) ────────────────────────────────────────────────────
    if fmt == 'JPEG':
        try:
            image_field.seek(0)
            img2 = Image.open(image_field)
        except Exception:
            img2 = img
        ela = _ela(img2)
        if ela > 18:
            score += int((ela - 18) * 0.55)
            signals.append(f'ELA recompression variance: {ela}/35')

    score = max(0, min(100, score))
    notes = '; '.join(signals) if signals else 'No editing signals detected'

    # Reset file position for the caller (compress_image reads it next)
    try:
        image_field.seek(0)
    except Exception:
        pass

    return score, notes


def edit_label(score: int | None) -> str:
    """Human-readable label used in templates."""
    if score is None:
        return ''
    if score <= 20:
        return 'Raw'
    return f'{score}% edited'


def edit_color(score: int | None) -> str:
    """CSS color class used in templates."""
    if score is None or score <= 20:
        return 'auth-raw'
    if score <= 50:
        return 'auth-low'
    if score <= 75:
        return 'auth-mid'
    return 'auth-high'
