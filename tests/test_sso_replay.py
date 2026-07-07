import pytest

from tt_common import sso_replay
from tt_common.sso_replay import is_replayed_sso_token


class FakeRedis:
    def __init__(self):
        self.store = {}

    def set(self, key, value, nx=False, ex=None):
        if nx and key in self.store:
            return None
        self.store[key] = value
        return True


class BrokenRedis:
    def set(self, *args, **kwargs):
        raise ConnectionError("redis down")


@pytest.fixture()
def fake(monkeypatch):
    monkeypatch.setattr(sso_replay, "_redis_client", FakeRedis())


def test_ohne_uri_kein_check(app):
    with app.app_context():
        app.config["SSO_REPLAY_STORAGE_URI"] = ""
        assert is_replayed_sso_token({"jti": "a"}) is False


def test_erste_verwendung_erlaubt(app, fake):
    with app.app_context():
        app.config["SSO_REPLAY_STORAGE_URI"] = "redis://fake"
        assert is_replayed_sso_token({"jti": "t1"}) is False


def test_zweite_verwendung_abgelehnt(app, fake):
    with app.app_context():
        app.config["SSO_REPLAY_STORAGE_URI"] = "redis://fake"
        assert is_replayed_sso_token({"jti": "t1"}) is False
        assert is_replayed_sso_token({"jti": "t1"}) is True


def test_ohne_jti_akzeptiert(app, fake):
    with app.app_context():
        app.config["SSO_REPLAY_STORAGE_URI"] = "redis://fake"
        assert is_replayed_sso_token({}) is False


def test_redis_ausfall_fail_open(app, monkeypatch):
    monkeypatch.setattr(sso_replay, "_redis_client", BrokenRedis())
    with app.app_context():
        app.config["SSO_REPLAY_STORAGE_URI"] = "redis://fake"
        assert is_replayed_sso_token({"jti": "t2"}) is False
