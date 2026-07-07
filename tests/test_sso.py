from datetime import datetime, timedelta, timezone

import jwt as pyjwt

from tt_common.sso import (
    get_auth_login_url,
    get_auth_logout_url,
    is_safe_url,
    validate_sso_token,
)


def _make_token(app, *, audience="tt-members", secret=None, ttl=60):
    now = datetime.now(timezone.utc)
    return pyjwt.encode(
        {"sub": "1", "username": "admin", "aud": audience, "iat": now, "exp": now + timedelta(seconds=ttl)},
        secret or app.config["SSO_SHARED_SECRET"],
        algorithm="HS256",
    )


def test_gueltiges_token_wird_akzeptiert(app):
    with app.app_context():
        payload = validate_sso_token(_make_token(app))
    assert payload is not None
    assert payload["username"] == "admin"


def test_falsche_audience_wird_abgelehnt(app):
    with app.app_context():
        token = _make_token(app, audience="tt-agenda")
        assert validate_sso_token(token) is None
        assert validate_sso_token(token, audience="tt-agenda") is not None


def test_falsches_secret_wird_abgelehnt(app):
    with app.app_context():
        assert validate_sso_token(_make_token(app, secret="angreifer")) is None


def test_abgelaufenes_token_wird_abgelehnt(app):
    with app.app_context():
        assert validate_sso_token(_make_token(app, ttl=-10)) is None


def test_login_und_logout_url(app):
    with app.app_context():
        login = get_auth_login_url("tt-members", next_page="/x")
        assert login.startswith("http://localhost:8085/?")
        assert "next_service=tt-members" in login
        assert get_auth_logout_url() == "http://localhost:8085/logout"


def test_is_safe_url(app):
    with app.test_request_context("http://members.example/"):
        assert is_safe_url("/dashboard") is True
        assert is_safe_url("http://boese.example/x") is False
        assert is_safe_url("") is False
