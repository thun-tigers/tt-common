# PoC: tt-auth auf das geteilte Layout umstellen

Zeigt konkret, wie `tt-auth` von seiner 296-Zeilen-`base.html` auf das zentrale
Layout wechselt. Reversibel: Solange die lokale `base.html` ihren alten Inhalt
behaelt, greift sie weiter (ChoiceLoader zieht app-lokal vor).

## 1. Abhaengigkeit ergaenzen

`tt-auth/requirements.txt`:

```
tt-common @ git+https://github.com/thun-tigers/tt-common@v0.1.0
```

Lokal fuer die Entwicklung: `pip install -e ../tt-common`.

## 2. In `create_app()` aktivieren

`tt-auth/app/__init__.py`, nach dem Registrieren der Blueprints:

```python
from tt_common import register_shared_ui

register_shared_ui(
    app,
    brand_label="Plattform",
    brand_icon="bi-shield-lock",
    home_endpoint="dashboard.index",
    profile_endpoint="dashboard.profile",
    logout_endpoint="auth.logout",
)
```

## 3. `app/templates/base.html` ersetzen

Vorher: 296 Zeilen. Nachher (die service-spezifische Admin-Navigation bleibt, alles
andere kommt aus tt-common):

```jinja
{% extends "tt_common/base.html" %}
{% block title %}Tigers Auth{% endblock %}

{% block appbar_actions %}
  {% if current_user %}
  <a href="{{ url_for('dashboard.index') }}" class="relative hidden lg:inline-flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 hover:text-indigo-500 hover:bg-slate-100 dark:hover:bg-slate-800 transition" title="Apps">
    <i class="bi bi-grid-fill"></i>
    {% if pending_messages_count > 0 %}
    <span class="absolute -top-1 -right-1 min-w-[16px] h-[16px] px-1 flex items-center justify-center rounded-full bg-red-500 text-white text-[9px] font-bold">{{ pending_messages_count if pending_messages_count < 100 else '99+' }}</span>
    {% endif %}
  </a>
  {% endif %}
{% endblock %}

{% block nav_desktop %}
  {% if current_user and current_user.role == 'admin' %}
  {% set ep = request.endpoint %}
  <div class="hidden lg:flex items-center gap-1 ml-auto mr-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50/80 dark:bg-slate-900/50 p-1">
    <a href="{{ url_for('users.index') }}" class="...">Benutzer</a>
    <a href="{{ url_for('master_data.positions') }}" class="...">Stammdaten</a>
    <a href="{{ url_for('services.index') }}" class="...">Services</a>
  </div>
  {% endif %}
{% endblock %}

{% block nav_mobile %}
  {# die bestehenden mobilen Nav-Eintraege aus der alten base.html #}
{% endblock %}

{% block bottom_nav %}
  {# die bestehende Bottom-Tab-Bar aus der alten base.html #}
{% endblock %}

{% block content %}{% endblock %}
```

`dashboard.html`, `login.html` usw. bleiben unveraendert – sie erweitern weiterhin
`base.html`.

## 4. Was zentral wird

Aus der alten `base.html` wandern nach tt-common und verschwinden aus tt-auth:

- kompletter `<head>` inkl. Tailwind-Config und `brand`-Farbschema
- Theme-Toggle-Logik (Cookie + Dark-Mode, ~90 Zeilen JS)
- Flash-Message-Rendering
- Hintergrund-Orbs, Glass-Effekt, Formular-Styling
- Avatar/Logout-Bereich der App-Bar
- Einbindung von `table_enhancements.js` (jetzt aus tt-common-static)

Der Netto-Effekt: eine Aenderung am Theme-Toggle oder Farbschema passiert **einmal**
in tt-common statt sechsmal.

## 5. Verifikation

```bash
pip install -e ../tt-common
pytest tests/           # bestehende tt-auth-Tests muessen gruen bleiben
```

Danach App starten und pruefen: Login-Seite, Dashboard (eingeloggt), Theme-Toggle,
Logo, mobile Navigation.
