"""Gemeinsame SSO-Helfer fuer die Downstream-Services.

Zentralisiert die Logik, die bisher in jedem Service (tt-members, tt-agenda,
tt-analytics, tt-attendance) dupliziert war: Validierung eingehender SSO-Tokens
und der Aufbau der Login-/Logout-URLs Richtung tt-auth.

Der Replay-Schutz liegt in :mod:`tt_common.sso_replay`, die Normalisierung der
Claims in :mod:`tt_common.authz`.
"""

from urllib.parse import urlencode, urljoin, urlparse

import jwt
from flask import current_app, request


def get_sso_secret():
    """Signatur-Secret fuer SSO-Tokens (mit Fallback auf SECRET_KEY)."""
    return current_app.config.get("SSO_SHARED_SECRET") or current_app.config.get("SECRET_KEY")


def validate_sso_token(token, audience=None):
    """Validiert ein eingehendes SSO-Token.

    Gibt das dekodierte Payload zurueck oder ``None`` bei ungueltigem,
    abgelaufenem oder fuer die falsche Audience ausgestelltem Token.
    ``audience`` faellt auf ``SSO_EXPECTED_AUDIENCE`` aus der App-Config zurueck.
    """
    expected_audience = audience or current_app.config.get("SSO_EXPECTED_AUDIENCE")
    try:
        return jwt.decode(
            token,
            get_sso_secret(),
            algorithms=["HS256"],
            audience=expected_audience,
        )
    except jwt.InvalidTokenError:
        # deckt ExpiredSignatureError und InvalidAudienceError mit ab
        return None


def is_safe_url(target):
    """True, wenn ``target`` auf denselben Host zeigt (Open-Redirect-Schutz)."""
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


def get_auth_login_url(next_service, next_page=None):
    """Baut die zentrale tt-auth-Login-URL fuer diesen Service."""
    base = current_app.config.get("AUTH_BASE_URL", "http://localhost:8085").rstrip("/")
    query = {"next_service": next_service}
    if next_page:
        query["next"] = next_page
    return f"{base}/?{urlencode(query)}"


def get_auth_logout_url():
    """Baut die zentrale tt-auth-Logout-URL.

    Wichtig: Der Logout eines Microservice muss immer hierher zeigen, nicht auf
    die eigene Login-Seite - sonst loggt tt-auth den Benutzer per SSO sofort
    wieder ein.
    """
    base = current_app.config.get("AUTH_BASE_URL", "http://localhost:8085").rstrip("/")
    return f"{base}/logout"
