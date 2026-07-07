from tt_common.authz import (
    has_role_permission,
    is_platform_admin,
    normalize_auth_payload,
    normalize_permissions,
    normalize_role,
)


def test_normalize_role_faellt_auf_default_zurueck():
    assert normalize_role("admin") == "admin"
    assert normalize_role("bloedsinn") == "user"
    assert normalize_role(None, default="user") == "user"


def test_normalize_permissions_dedupliziert_und_filtert():
    assert normalize_permissions(["a", "a", " b ", 3, None]) == ["a", "b"]
    assert normalize_permissions("kein-list") == []


def test_wildcard_permission_macht_platform_admin():
    result = normalize_auth_payload({"role": "user", "permissions": ["*"]})
    assert result["platform_role"] == "admin"
    assert result["service_role"] == "admin"
    assert is_platform_admin(result["platform_role"]) is True


def test_service_role_wird_aus_role_abgeleitet():
    result = normalize_auth_payload({"role": "user", "permissions": ["profile:read"]})
    assert result["service_role"] == "user"
    assert result["claims"]["role"] == "user"


def test_has_role_permission_beachtet_service_und_wildcard():
    role_permissions = {"agenda": ["read", "write"], "*": ["read"]}
    assert has_role_permission(role_permissions, "write", "tt-agenda") is True
    assert has_role_permission(role_permissions, "write", "tt-analytics") is False
    assert has_role_permission(role_permissions, "read", "tt-analytics") is True
