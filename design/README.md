# tigers-ui — Design-Build

Ersetzt das Tailwind-CDN-Script (`cdn.tailwindcss.com`, Laufzeit-JIT, ~300&nbsp;KB JS)
durch ein einmalig kompiliertes, statisches Stylesheet. Wird als
`tt_common/static/tt_common/css/tigers.css` ausgeliefert und von allen Services
über das gemeinsame `base.html` eingebunden.

## Theme

Dual-Tone: Club-Purpur (aus `tt-logo.png` gemessen, Stufe 700 = `#702080`) ersetzt
Indigo, Zinc (warm) ersetzt Slate. Beides als Override der eingebauten Tailwind-
Farbnamen in `tailwind/tailwind.config.js` — Templates referenzieren weiterhin
`indigo-*` / `slate-*`, es muss kein Template angefasst werden. Amber bleibt für
Warnungen und den neuen Live-Akzent (Werte bereits CVD-geprüft, siehe
`references/palette.md` im dataviz-Skill bzw. das Claude-Designer-Projekt
"Tigers Design System").

## Neu bauen

Nötig, wenn ein Service neue Tailwind-Klassen einführt, die vorher nirgends
verwendet wurden (das JIT-Scanning erfasst nur Klassen, die tatsächlich in den
gescannten Dateien vorkommen).

```bash
cd tt-common/design/tailwind
npm install
npm run build
```

Scannt alle sechs Repos (`content` in `tailwind.config.js`, absolute Pfade,
setzt ein lokales Checkout aller Repos nebeneinander voraus — wie im
tt-infra-Schnellstart beschrieben). Schreibt direkt nach
`tt_common/static/tt_common/css/tigers.css`.

## Fonts & Icons

Self-hosted statt CDN:

- `tt_common/static/tt_common/fonts/InterVariable.woff2` — Inter Variable,
  offizielles Release (rsms/inter v4.1)
- `tt_common/static/tt_common/fonts/bootstrap-icons.woff(2)` +
  `tt_common/static/tt_common/css/bootstrap-icons.css` — Bootstrap Icons 1.11.3,
  Klassennamen unverändert (`bi bi-*`), keine Template-Änderungen nötig.

## Nicht (mehr) im Einsatz

- `cdn.tailwindcss.com` Script
- `fonts.googleapis.com` / `fonts.gstatic.com`
- `cdn.jsdelivr.net/npm/bootstrap-icons`

Diese CDN-Referenzen wurden aus `tt_common/templates/tt_common/base.html`
entfernt.
