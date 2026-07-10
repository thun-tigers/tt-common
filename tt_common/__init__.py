"""Geteilte Bausteine fuer den Tigers-Microservice-Stack.

Enthaelt aktuell:
- ``register_shared_ui`` – bindet das zentrale Layout (Templates + statische Assets) in eine Flask-App ein.

Spaeter geplant: SSO-Client, JWT-Utils, Replay-Schutz (siehe README).
"""

from flask import Blueprint, url_for

__version__ = "0.1.15"

__all__ = ["register_shared_ui", "__version__"]


def register_shared_ui(
    app,
    *,
    brand_label="Plattform",
    brand_icon="bi-shield-lock",
    home_endpoint="main.index",
    profile_endpoint=None,
    logout_endpoint="auth.logout",
):
    """Macht das zentrale Layout aus tt-common in einer Flask-App verfuegbar.

    Danach koennen Service-Templates mit ``{% extends "tt_common/base.html" %}``
    das gemeinsame Grundgeruest nutzen und nur die Bloecke ``nav_desktop``,
    ``nav_mobile``, ``bottom_nav`` und ``content`` fuellen.

    Die service-spezifischen Ziel-URLs werden ueber einen Context-Processor
    bereitgestellt. So muss das geteilte Template kein ``url_for`` auf Endpoints
    aufrufen, die es im jeweiligen Service gar nicht gibt (z. B. ``dashboard.index``
    existiert nur in tt-auth). Fehlt ein Endpoint, wird still auf ``/`` bzw. die
    Home-URL zurueckgefallen.

    Konfigurierbare App-Config-Keys (optional, ueberschreiben die Argumente):
    ``UI_BRAND_LABEL``, ``UI_BRAND_ICON``.
    """
    from jinja2 import ChoiceLoader, PackageLoader

    # 1) Templates: erst app-lokal, dann tt_common. So kann ein Service jederzeit
    #    ein eigenes Template gleichen Namens vorziehen (schrittweise Migration).
    app.jinja_loader = ChoiceLoader([app.jinja_loader, PackageLoader("tt_common", "templates")])

    # 2) Statische Assets unter /tt-common-static/... ausliefern.
    shared_bp = Blueprint(
        "tt_common",
        __name__,
        static_folder="static/tt_common",
        static_url_path="/tt-common-static",
    )
    app.register_blueprint(shared_bp)

    # 3) Kontextvariablen fuer das geteilte Layout.
    def _safe_url(endpoint, **kwargs):
        if not endpoint:
            return None
        try:
            return url_for(endpoint, **kwargs)
        except Exception:
            return None

    @app.context_processor
    def _shared_ui_context():
        home_url = _safe_url(home_endpoint) or "/"
        return {
            "ui_brand_label": app.config.get("UI_BRAND_LABEL", brand_label),
            "ui_brand_icon": app.config.get("UI_BRAND_ICON", brand_icon),
            "ui_home_url": home_url,
            "ui_profile_url": _safe_url(profile_endpoint) or home_url,
            "ui_logout_url": _safe_url(logout_endpoint) or "/logout",
            "ui_logo_url": url_for("tt_common.static", filename="tt-logo.png"),
        }
