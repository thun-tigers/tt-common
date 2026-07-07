# tt-common

Geteilte Bausteine fuer den Tigers-Microservice-Stack. Ziel: Code und UI, die heute
in `tt-auth`, `tt-members`, `tt-agenda`, `tt-analytics` und `tt-attendance` mehrfach
kopiert sind, an **einer** Stelle pflegen.

Aktueller Inhalt:
- **SSO-Code** (produktiv genutzt): `authz.py` (`normalize_auth_payload` & Co.),
  `sso.py` (`validate_sso_token`, Login-/Logout-URL-Helfer), `sso_replay.py`
  (Single-Use-Replay-Schutz). Die Downstream-Services binden diese ueber duenne
  Re-Export-Shims ein.
- **zentrales UI-Layout** (Proof of Concept, noch nicht in den Services aktiviert).

---

## Das Grundproblem bei UI-Sharing

Python-Code teilt man trivial: `pip install tt-common`, importieren, fertig – die
Bibliothek wird zur Laufzeit geladen. **Templates und CSS sind aber Dateien**, die
Flask im `app/templates`-Ordner des jeweiligen Service sucht. Ein `pip install` legt
sie zwar ins site-packages-Verzeichnis, aber Flask schaut da standardmaessig nicht
hinein. Man muss den Jinja-Loader explizit erweitern.

Zweiter Punkt: Die sechs `base.html`-Dateien teilen ~80 % (Head, Tailwind-Config,
Theme-Toggle, Flash-Messages, Farb-Schema), unterscheiden sich aber in der
**Navigation** (tt-auth: Benutzer/Services/Stammdaten; tt-agenda: Trainings; …).
Ein geteiltes Layout muss also den gemeinsamen Rahmen liefern und den
service-spezifischen Teil ueber Jinja-`{% block %}` offen lassen.

Dritter Punkt (der subtilste): Das geteilte Template darf **kein `url_for` auf
Endpoints aufrufen, die es im jeweiligen Service nicht gibt**. `dashboard.index`
existiert nur in tt-auth. tt-members behilft sich heute schon mit einer Variable
`auth_dashboard_url`. Genau dafuer liefert `register_shared_ui` einen
Context-Processor, der solche URLs zentral (und mit Fallback) aufloest.

---

## Zwei Liefermodelle

### Variante A – Python-Package mit Loader (in diesem Repo umgesetzt)

`tt-common` wird als pip-Package installiert und liefert Templates **und** Assets
mit. Beim App-Start ruft der Service `register_shared_ui(app)` auf; das haengt den
`PackageLoader` in den Jinja-`ChoiceLoader` und registriert einen Blueprint, der die
statischen Assets unter `/tt-common-static/...` ausliefert.

```
requirements.txt:
  tt-common @ git+https://github.com/thun-tigers/tt-common@v0.1.0
```

```python
# app/__init__.py
from tt_common import register_shared_ui

def create_app():
    app = Flask(__name__)
    ...
    register_shared_ui(app, brand_label="Members", brand_icon="bi-people-fill",
                       home_endpoint="main.index", logout_endpoint="auth.logout")
    return app
```

```jinja
{# app/templates/base.html – schrumpft auf wenige Zeilen #}
{% extends "tt_common/base.html" %}
{% block nav_desktop %} … service-eigene Navigation … {% endblock %}
{% block content %}{% endblock %}
```

**Pro:** ein Repo, ein Versionsstand fuer Code UND UI; Update per Versions-Bump;
kein Kopieren, kein Drift. **Contra:** Assets liegen im site-packages und werden
ueber einen Blueprint ausgeliefert (statt `app/static`); minimal mehr Setup.

### Variante B – nur Templates/Assets, beim Build kopiert

`tt-common` enthaelt nur die Dateien; ein Skript oder `COPY` im Dockerfile zieht sie
beim Image-Build in jeden Service (`app/templates/tt_common/`, `app/static/`).

**Pro:** einfacher zu verstehen, kein Loader-Setup, Assets liegen normal in
`app/static`. **Contra:** Die Kopie muss bei jeder UI-Aenderung neu gezogen und in
jedem Service-Image neu gebaut werden – das Drift-Risiko kehrt teilweise zurueck,
nur eben build-zeitlich statt per Copy-Paste.

### Empfehlung

**Variante A.** Sie loest dasselbe Problem wie beim geplanten SSO-Code auf demselben
Weg (ein Package, ein Versions-Pin) und passt damit konsistent zur Roadmap dieses
Repos. Variante B lohnt sich nur, falls ihr die Loader-Verdrahtung strikt vermeiden
wollt.

---

## Aufbau dieses Repos

```
tt_common/
  __init__.py                     register_shared_ui(app, ...)
  authz.py                        normalize_auth_payload, Rollen/Permissions
  sso.py                          validate_sso_token, Login-/Logout-URLs
  sso_replay.py                   Single-Use-Replay-Schutz (Redis)
  templates/tt_common/base.html   geteiltes Layout mit Bloecken
  static/tt_common/
    tt-logo.png
    js/table_enhancements.js
pyproject.toml
tests/                            Tests fuer authz, sso, sso_replay
docs/poc-tt-auth.md               Schritt-fuer-Schritt-Migration von tt-auth
```

### SSO-Code in einem Service nutzen

Die lokalen `app/authz.py` und `app/sso_replay.py` der Downstream-Services sind
jetzt duenne Shims, die aus tt-common re-exportieren – bestehende Imports
(`from ..authz import normalize_auth_payload`) laufen unveraendert weiter. Die
kanonische Implementierung liegt in tt-common. Neue Aufrufer koennen direkt
`from tt_common.sso import validate_sso_token` verwenden.

### Bloecke im geteilten `base.html`

| Block / Variable | Zweck | Default |
|---|---|---|
| `title` | Seitentitel | `ui_brand_name` |
| `brand` | Logo-Text + Icon (eingeloggt) | `ui_brand_label` / `ui_brand_icon` |
| `nav_desktop` | Desktop-Navigation (Service) | leer |
| `nav_mobile` | Mobile-Menue-Eintraege (Service) | leer |
| `bottom_nav` | Bottom-Tab-Bar mobil (Service) | leer |
| `appbar_actions` | Extra-Buttons rechts (z. B. Apps-Icon) | leer |
| `content` | Seiteninhalt | – |
| `extra_js` / `head_extra` / `head_style` | Erweiterungen | leer |

URLs (`ui_home_url`, `ui_profile_url`, `ui_logout_url`, `ui_logo_url`) liefert der
Context-Processor aus `register_shared_ui` – konfigurierbar ueber dessen Argumente.

---

## Migrationsstrategie

Der `ChoiceLoader` sucht **erst app-lokal, dann tt_common**. Dadurch laesst sich
Service fuer Service migrieren: `register_shared_ui` aktivieren, dann die lokale
`base.html` auf `{% extends "tt_common/base.html" %}` umstellen und testen. Solange
die lokale `base.html` unveraendert bleibt, gewinnt sie – der Umstieg ist also
jederzeit reversibel.

Reihenfolge-Vorschlag: **tt-auth** (PoC, siehe `docs/poc-tt-auth.md`) →
tt-members → tt-attendance → tt-analytics → tt-agenda (groesste/eigenstaendigste
`base.html` zuletzt).
