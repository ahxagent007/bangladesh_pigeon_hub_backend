"""
Google reCAPTCHA v2 server-side verification.
"""
import json
import urllib.parse
import urllib.request

from django.conf import settings


def verify_recaptcha(token: str, min_score: float = 0.5) -> bool:
    """
    Verify a reCAPTCHA v3 token against Google's API.

    v3 returns a score 0.0–1.0 (1.0 = very likely human).
    Tokens below min_score are treated as bots.
    Returns True on success, False on failure, missing token, low score, or network error.
    """
    if not token:
        return False
    try:
        payload = urllib.parse.urlencode({
            'secret':   settings.RECAPTCHA_SECRET_KEY,
            'response': token,
        }).encode()
        with urllib.request.urlopen(
            'https://www.google.com/recaptcha/api/siteverify',
            data=payload,
            timeout=5,
        ) as resp:
            result = json.loads(resp.read().decode())
        return bool(result.get('success')) and float(result.get('score', 0)) >= min_score
    except Exception:
        return False


def recaptcha_context(request):
    """Context processor: injects recaptcha_site_key into every template."""
    return {'recaptcha_site_key': getattr(settings, 'RECAPTCHA_SITE_KEY', '')}
