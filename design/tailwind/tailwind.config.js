const colors = require('tailwindcss/colors');

const REPOS = '/Users/swisi/Repos/tigers';

// Dual-Tone: Club-Purpur (aus tt-logo.png gemessen, Stufe 700 = #702080)
// ersetzt Indigo global - keine Template-Aenderungen noetig, da alle
// Services durchgaengig `indigo-*`-Klassen aus base.html referenzieren.
const purple = {
  50: '#faf5fc',
  100: '#f3e8f9',
  200: '#e5cdf2',
  300: '#d3a8e8',
  400: '#b972d6',
  500: '#9d44be',
  600: '#83259e',
  700: '#702080',
  800: '#5a1a67',
  900: '#4a1655',
  950: '#2e0d36',
};

module.exports = {
  darkMode: 'class',
  content: [
    `${REPOS}/tt-auth/app/templates/**/*.html`,
    `${REPOS}/tt-members/app/templates/**/*.html`,
    `${REPOS}/tt-agenda/app/templates/**/*.html`,
    `${REPOS}/tt-attendance/app/templates/**/*.html`,
    `${REPOS}/tt-analytics/app/templates/**/*.html`,
    `${REPOS}/tt-infra/app/templates/**/*.html`,
    `${REPOS}/tt-common/tt_common/templates/**/*.html`,
    // Sicherheitsnetz: falls irgendwo Tailwind-Klassen dynamisch in Python
    // zusammengesetzt werden (z.B. Flash-Kategorien, Badges).
    `${REPOS}/tt-auth/app/**/*.py`,
    `${REPOS}/tt-members/app/**/*.py`,
    `${REPOS}/tt-agenda/app/**/*.py`,
    `${REPOS}/tt-attendance/app/**/*.py`,
    `${REPOS}/tt-analytics/app/**/*.py`,
    `${REPOS}/tt-infra/app/**/*.py`,
  ],
  theme: {
    extend: {
      colors: {
        indigo: purple,
        slate: colors.zinc,
        brand: purple,
      },
      fontFamily: {
        sans: ['InterVariable', 'Inter', 'sans-serif'],
      },
    },
  },
  safelist: [
    // Kategorien/Status werden in Templates teils dynamisch zusammengesetzt
    // (z.B. via Jinja-Bedingungen ueber mehrere Zeilen) - JIT-Scan erfasst
    // das meist trotzdem, dieses Netz haelt bekannte Statusfarben zusaetzlich fest.
    { pattern: /^(bg|text|border)-(green|red|amber|blue|emerald|rose)-(50|100|200|300|400|500|600|700|800|900)$/, variants: ['dark', 'hover', 'dark:hover'] },
  ],
};
