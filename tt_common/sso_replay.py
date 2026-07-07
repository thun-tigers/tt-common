import logging

from flask import current_app

logger = logging.getLogger(__name__)

_redis_client = None


def _get_redis(uri):
    global _redis_client
    if _redis_client is None:
        import redis
        _redis_client = redis.Redis.from_url(uri)
    return _redis_client


def is_replayed_sso_token(payload):
    """True, wenn das SSO-Token bereits einmal eingelöst wurde (Single-Use-Check).

    Ohne konfigurierte Redis-URI oder bei Redis-Ausfall wird das Token
    akzeptiert (fail-open): der Schutz ergänzt die kurze Token-TTL,
    ersetzt sie aber nicht.
    """
    uri = current_app.config.get('SSO_REPLAY_STORAGE_URI') or ''
    if not uri.startswith('redis'):
        return False

    jti = payload.get('jti')
    if not jti:
        logger.warning('SSO-Token ohne jti-Claim, Replay-Schutz nicht anwendbar')
        return False

    ttl = current_app.config.get('SSO_REPLAY_TTL_SECONDS', 300)
    try:
        first_use = _get_redis(uri).set(f'sso:jti:{jti}', '1', nx=True, ex=ttl)
    except Exception:
        logger.exception('SSO-Replay-Check nicht verfügbar, Token wird akzeptiert')
        return False
    return not first_use
