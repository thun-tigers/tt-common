# Tigers Design System — Umsetzung in tt-common

Dieses Dokument beschreibt die Bausteine, die neu in `tt-common` zentralisiert werden,
und wie Services sie einbinden. Ziel: kein Copy-Paste von Nav-Tabs, Badges, Flash-Messages
und Empty-States mehr zwischen tt-auth/tt-members/tt-agenda/tt-analytics/tt-attendance.

## Dateien in diesem Patch

```
templates/tt_common/base.html      aktualisiert: Apps-Icon+Label, größere Touch-Targets, reichere Flash-Messages
templates/tt_common/macros.html    neu: badge(), empty_state(), nav_tab(), apps_link(); zusätzlich status_card() für service-interne Karten
```

## 1. Farben (unverändert, jetzt schriftlich fixiert)

- Brand: Indigo-Skala 50–950 (Tailwind-Config in base.html), Primärfarbe `600` (#4f46e5)
- Neutral: Slate-Skala 50–950
- Semantik: success=green, warning=amber, danger=red, info=blue — **immer** über `badge()`
  oder die Flash-Message-Kategorien, nie frei gemischte Tailwind-Klassen im Service-Template.

## 2. Radius/Schatten-Skala (neu, ersetzt gemischte rounded-xl/2xl + shadow-lg/2xl)

- Standard-Karte: `rounded-xl` (12px), `shadow-sm`
- Hervorgehobene Karte (Hero, Live-Status): `rounded-2xl` (16px), `shadow-lg`
- Hover-Elevation: `hover:shadow-md` — nicht härter, nur beim Hover

## 3. Neue Jinja-Makros (`tt_common/macros.html`)

```jinja
{% from "tt_common/macros.html" import badge, empty_state, nav_tab, apps_link %}

{{ badge('warning', 'bi-pencil-fill', 'ANGEPASST') }}
{{ empty_state('bi-calendar-x', 'Keine Trainings geplant', 'Es gibt derzeit keine bevorstehenden Trainings.') }}
{{ nav_tab('Übersicht', 'bi-house-door-fill', ep == 'main.index', url_for('main.index')) }}
{{ apps_link(auth_dashboard_url, pending_messages_count) }}
```

`badge(variant, icon, text)` — variant ∈ `success|warning|danger|info|neutral`, feste Farbpaare,
kein Freihand-Tailwind mehr pro Aufrufstelle.

`nav_tab(label, icon, active, href, count=None)` — ersetzt die in tt-auth und tt-agenda
identisch dupliziert Tab-Logik (aktiver Ring, Hover, Badge-Zahl).

`empty_state(icon, title, hint, action_html=None)` — ersetzt die fast identischen
"Keine Services verfügbar" (tt-auth) / "Keine Trainings geplant" (tt-agenda) Blöcke.

`apps_link(url, count, label="Apps")` — zentralisiert das App-Grid-Icon, das heute in
tt-auth UND tt-agenda separat mit leicht abweichender Badge-Logik existiert. Zeigt jetzt
Icon **und** Textlabel (vorher nur Icon+Tooltip — auf Touch-Geräten schlecht auffindbar,
siehe Mobile-First-Punkt unten).

## 4. Migration je Service

1. `templates/base.html` des Service: eigene Badge-/Empty-State-/Nav-Tab-Blöcke durch
   die Makro-Aufrufe ersetzen.
2. Eigene `appbar_actions`-Overrides (Apps-Icon-Duplikate in tt-auth/tt-agenda) entfernen —
   `apps_link()` ist jetzt Default-Verhalten im geteilten `base.html`, kein Override nötig,
   ausser ein Service will es explizit verstecken.
3. Reihenfolge wie in README: tt-auth → tt-members → tt-attendance → tt-analytics → tt-agenda.

## 5. Mobile-First-Bewertung (Ist-Zustand)

**Bereits gut:**
- Bottom-Tab-Bar mit `safe-bottom` (env(safe-area-inset-bottom)) für iOS-Homebar
- Separates `nav_mobile`-Block statt Desktop-Nav einfach nur ausgeblendet
- `viewport-fit=cover` gesetzt

**Lücken, die dieser Patch behebt:**
- **Touch-Targets zu klein:** Theme-Toggle, Mobile-Menu-Button, Apps-Icon, Logout-Icon
  waren `h-8 w-8` (32px) — unter der 44px-Empfehlung (Apple HIG / WCAG 2.5.5). Jetzt
  `h-11 w-11` auf Mobile, `lg:h-8 lg:w-8` auf Desktop.
- **Apps-Icon ohne Label:** nur Icon + `title`-Tooltip — Tooltips existieren auf Touch
  nicht. Jetzt Icon + sichtbarer Text "Apps" (siehe `apps_link()`).
- **Bottom-Nav ist `fixed` in tt-auth, `sticky` in tt-agenda** — uneinheitliches Scroll-
  Verhalten zwischen Services. Empfehlung: `sticky` überall (tt-agenda-Variante), da sie
  keinen Content verdeckt und mit dem `pb-24`-Padding in `<main>` zusammenspielt.

**Noch offen (nicht Teil dieses Patches, zur Diskussion):**
- Formularfelder sind bereits ausreichend gross (`py-[0.55rem]` ≈ 40px), aber Select-
  Dropdowns mit langen Optionslisten (z. B. Positionen in tt-auth) sind auf kleinen
  Screens nicht getestet — ggf. natives `<select>` durch Bottom-Sheet ersetzen.
- Tabellen (`table_enhancements.js`) sind nicht horizontal scroll-optimiert für schmale
  Screens — grosse Tabellen (`users.html`, `all_trainings_table.html`) könnten auf Mobile
  eine Karten-Ansicht statt Tabellenzeilen brauchen.
