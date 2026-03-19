# Bergische LK-Turniere — CLAUDE.md

## Projet
Site statique pour bergische-lk.de — tournois LK tennis sur terre battue dans le Bergisches Land (NRW).
Déployé sur GitHub Pages (branch main, root). Repo: jcdas/bergische-lk.de

## Architecture
- `data.js` — **source unique de vérité** pour tout le contenu. Ne jamais hardcoder du contenu dans les HTML.
- `index.html` — Landing page (hero, tournois, venues, règlement, catégories, sponsoring, FAQ, newsletter, social, contact)
- `clubs.html` — Page B2B lead generation pour clubs
- `legal.html` — Impressum + Datenschutzerklärung
- `logo.svg` — Logo (court de tennis vu du dessus) — sera remplacé par un logo externe
- `favicon.svg` — Favicon

## Charte graphique
- Vert profond: #1C3A0E
- Vert terrain: #2D5A18
- Orange terre battue: #B85A20
- Crème: #F0EBE0
- Fonts: Bebas Neue (titres) + Barlow (corps) via Google Fonts
- Style: sport & dynamique, terre battue / clay court

## Langues
- Allemand (DE) = langue principale
- English (EN) = switcher DE/EN en haut à droite
- Toutes les traductions sont dans data.js avec format `{ de: "...", en: "..." }`
- La langue est persistée dans localStorage

## Règles de développement
- Tout changement de contenu passe par `data.js` uniquement
- Les images doivent être libres de droit (Unsplash ou propres avec consentement)
- Galerie photos: uniquement avec `consent: true` (Recht am eigenen Bild / KUG §22)
- Toujours vérifier les URLs d'images (HTTP 200) avant de commit
- Pages légales (Impressum/Datenschutz) obligatoires — droit allemand
- DSGVO/RGPD : pas de cookies tracking, pas de Google Analytics sans consentement

## Données à compléter (placeholders dans data.js)
- `impressum.address` — vraie adresse postale
- `impressum.phone` — vrai numéro de téléphone
- `newsletter.action` — URL du service newsletter (Buttondown/Brevo)
- `social.instagram` — vrai compte Instagram
- `social.whatsapp` — vrai numéro WhatsApp (wa.me/...)
- `gallery.enabled` — passer à true quand photos disponibles

## Contacts
- Organisateur: Jean-Charles Das
- Email: info@bergische-lk.de
- Venues: ESV Wuppertal West (7 courts TB) + TC Gruiten (6 courts TB)
