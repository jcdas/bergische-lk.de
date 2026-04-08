# Projet Tennis LK — Bergische LK-Turniere

> Organisation de tournois LK (Leistungsklasse) sur terre battue dans le Bergisches Land (NRW).
> Organisateur : Jean-Charles Das | Site : [bergische-lk.de](https://bergische-lk.de)
> Venues : ESV Wuppertal West (7 courts) + TC Gruiten (6 courts)

---

## 1. Site Internet — bergische-lk.de

**Repo** : `~/Tennis/` (GitHub Pages, branch main, root)
**Domaine** : bergische-lk.de (CNAME configuré)
**Stack** : HTML/CSS/JS statique, `data.js` = source unique de vérité

### Fichiers

| Fichier | Rôle |
|---------|------|
| `index.html` | Landing page : hero, tournois, venues, règlement, catégories, sponsoring, FAQ, newsletter, social, contact |
| `clubs.html` | Page B2B : lead gen pour clubs partenaires potentiels |
| `partner-sommer2026-b4.html` | Wizard multi-step offre partenaire (DE) |
| `partner-sommer2026-b4-en.html` | Idem (EN) |
| `legal.html` | Impressum + Datenschutzerklärung (obligatoire droit DE) |
| `data.js` | Config centrale : contenu bilingue DE/EN, tournois, venues, sponsors, FAQ, règles |
| `logo.svg` / `logo.jpg` | Logo (court vu du dessus) |
| `favicon.svg` | Favicon |
| `sitemap.xml` / `robots.txt` | SEO |
| `leads/` | Répertoire leads (vide, `.gitkeep`) |
| `.github/workflows/` | CI/CD GitHub Actions |
| `.claude/launch.json` | Dev server local (Python HTTP, port 8080) |

### Charte graphique

- Vert profond : `#1C3A0E`
- Vert terrain : `#2D5A18`
- Orange terre battue : `#B85A20`
- Crème : `#F0EBE0`
- Fonts : Bebas Neue (titres) + Barlow (corps) via Google Fonts

### Placeholders à compléter

| Donnée | Statut |
|--------|--------|
| `impressum.address` | ✅ Renseigné (Bergstr. 10, 42781 Haan) |
| `impressum.phone` | ❌ Manquant |
| `newsletter.action` | ❌ URL Buttondown/Brevo à configurer |
| `social.instagram` | ❌ Compte à créer |
| `social.whatsapp` | ❌ Numéro wa.me à renseigner |
| `gallery.enabled` | ❌ false (en attente de photos avec consentement KUG §22) |

### Email

- Adresse configurée dans `data.js` : `info@bergische-lk.de`
- **Setup technique email (MX, forwarding, boîte)** : non documenté, à vérifier/configurer

---

## 2. Communication Clubs — Prospection

### Stratégie

Démarcher les clubs à moins de 20 km de Haan (Bezirk 4, Bergisch Land).
JCD apporte tout (inscriptions TVN, balles, orga, arbitrage OSR, communication).
Le club fournit uniquement les terrains.

### Documents

| Ressource | Localisation | Contenu |
|-----------|-------------|---------|
| Concept master | [Notion : Tournois LK](https://www.notion.so/33aa2bf42be2813ba9a3e832ab75c01a) | P&L, offre club, répartition revenus, Free Tickets, confidentialité, email template DE |
| CRM Clubs | [Notion : Vereine Partnerschaft](https://www.notion.so/ab743a80c5894dce94627587aaea2dba) | DB leads avec pipeline : Kein Kontakt > Interesse > RDV > Partnerschaft > Kein Interesse |
| Dossier sponsoring | `~/CURSOR-RAG/output/sponsoring_dossier.html` | Dossier pro (dark/neon), tiers Bronze/Silver/Gold |
| Page clubs site | `~/Tennis/clubs.html` | Page B2B publique |
| Wizard partenaire | `~/Tennis/partner-sommer2026-b4.html` | Formulaire multi-step offre club |

### Modèle économique (par tournoi, base 48 joueurs)

- Recettes : 1 155 EUR (33 jeunes x 25 EUR + 11 adultes x 30 EUR)
- Coûts : DTB 168 EUR + balles 105 EUR + 25% club 289 EUR
- **Net organisateur : 593 EUR**
- **Projection saison (6 tournois) : ~3 558 EUR**

### Catégories

U12, U14, U16, Herren Erwachsene (Spiralturnier LK, 2 matchs/joueur, nombres pairs)

### Règle confidentialité

Le club voit UNIQUEMENT : sa part EUR, le package Free Tickets, les dimanches dispo.
Le club ne voit JAMAIS : net organisateur, coût balles, coût DTB Free Tickets.

### Statut

- [x] Concept + P&L finalisés
- [x] Email template DE rédigé
- [x] CRM Notion structuré
- [ ] Données clubs Bezirk 4 à importer dans CRM
- [ ] Emails de prospection à envoyer

---

## 3. Scraping TVN — Extraction données clubs et joueurs

### Scripts existants

| Script | Localisation | Fonction |
|--------|-------------|----------|
| `extract_tennis_players.py` | `~/CURSOR-RAG/src/etl/` | Extraction joueurs masculins depuis emails nuLiga Gmail > CSV |
| `build_tournament_db.py` | `~/CURSOR-RAG/scripts/` | Extraction joueurs depuis Qdrant (emails Turnieranmeldung/abmeldung) > SQLite |

### Données produites

| Fichier | Localisation | Contenu |
|---------|-------------|---------|
| `tennis_players_male.csv` | `~/CURSOR-RAG/output/` | 179 joueurs (nom, prénom, date naissance, email, tel, club, tournoi, catégorie) |

### Ce qui existe

- Extraction depuis **emails Gmail** (confirmations d'inscription/désinscription nuLiga)
- Parsing des emails Turnieranmeldung pour ESV Wuppertal + TC Gruiten

### Ce qui manque

- **Scraping live du site TVN** (nuLiga) pour lister tous les clubs Bezirk 4, leurs terrains, contacts Jugendwart/Sportwart
- Import automatisé des résultats dans le CRM Notion (Vereine Partnerschaft)
- Scraping des calendriers de tournois existants pour éviter les conflits de dates

---

## 4. Mailing List Parents — Agendas tournois

### Fichiers

| Fichier | Localisation | Contenu |
|---------|-------------|---------|
| `mailing_list_tournois.html` | `~/CURSOR-RAG/output/` | **174 jeunes joueurs** (U11-U18, Jahrgang 2008-2015), classés par année de naissance. Nom, club, email, tel, nb participations. Généré le 17 mars 2026. |
| `tennis_players_male.csv` | `~/CURSOR-RAG/output/` | Données brutes CSV (même base) |

### Pièces jointes emails récupérées

| Document | Localisation |
|----------|-------------|
| Anschreiben Anmeldung Ranglistenturnier 2026 (PDF) | `~/CURSOR-RAG/output/gmail_attachments/2bfacb374fea06a7/` |
| Anschreiben Anmeldung Jugend-Ranglistenturnier 2026 (PDF) | idem |
| Zeitplan Jugendturnier 2025 (PDF) | `~/CURSOR-RAG/output/gmail_attachments/4b44ea53e8dac808/` |

### Mailing GDPR avec Brevo

| Fichier | Localisation | Rôle |
|---------|-------------|------|
| `prepare_mailing.py` | `~/Tennis/scripts/` | Génère CSV Brevo depuis tennis_players_male.csv (179 contacts, 90 clubs) |
| `mailing_brevo_import.csv` | `~/Tennis/` | CSV prêt à importer dans Brevo (EMAIL;VORNAME;NACHNAME;TELEFON;VEREIN;KATEGORIEN) |
| `tournoi_annonce.html` | `~/Tennis/email_templates/` | Template email HTML avec merge tags Brevo + footer GDPR |
| `README_BREVO.md` | `~/Tennis/email_templates/` | Guide complet setup Brevo (compte, DNS, import, campagne) |

### GDPR Compliance

- Base légale : Art. 6(1)(f) DSGVO, berechtigtes Interesse (anciens participants)
- Opt-out : lien Brevo unsubscribe 1-clic en footer
- Transparence : explication source données + droit de désinscription dans chaque email

### Statut

- [x] Base joueurs extraite (179 contacts uniques, 90 clubs)
- [x] HTML mailing list généré avec contacts parents
- [x] Script préparation CSV Brevo fonctionnel
- [x] Template email GDPR-compliant créé
- [x] Guide setup Brevo rédigé
- [ ] Créer compte Brevo + vérifier domaine bergische-lk.de
- [ ] Importer CSV dans Brevo
- [ ] Envoyer première campagne (ESV Summer Smash 02.05)

---

## 5. Affiches Tournois + QR Code

### Statut : ✅ TEMPLATE CRÉÉ

### Fichier

`~/Tennis/poster.html` : template HTML paramétré, lit depuis `data.js`, QR code dynamique (qrcode-generator CDN).
Sélecteur de tournoi intégré, format A3 portrait, optimisé print (Cmd+P > PDF).

### Tournoi actif

- **LK Summer Smash Series - ESV - 1** (02.05.2026)
- Lien inscription : `https://www.tennis.de/spielen/turniersuche.html#detail/828059`
- QR code pointe vers ce lien
- Antragsnummer TVN : 905111

---

## 6. Notion — Pages liées

| Page | ID | Rôle |
|------|----|------|
| Tournois LK — Concept | `33aa2bf42be2813ba9a3e832ab75c01a` | Master doc stratégie + offre |
| Vereine Partnerschaft — Leads | `ab743a80c5894dce94627587aaea2dba` (DS: `2b8b6654-3ef9-4156-9387-f2646a1bf721`) | CRM clubs |
| Emeric — Tennis LK 12/13 + US College | `335a2bf42be281078604e586b31832f0` | Suivi tennis Emeric (PRJ-21) |

---

## 7. Emeric — Connexion projet

Emeric (15 ans) joue en LK 12-13 et participe aux tournois ESV/Gruiten.
Il apparaît dans la mailing list (5 participations, TC Gruiten).
Son parcours est suivi séparément dans Notion (PRJ-21) avec objectif UTR 9-9.5 et US College.

---

## Arborescence complète

```
~/Tennis/                              ← REPO SITE (GitHub Pages)
├── index.html                         Landing page
├── clubs.html                         Page B2B clubs
├── partner-sommer2026-b4.html         Wizard partenaire DE
├── partner-sommer2026-b4-en.html      Wizard partenaire EN
├── legal.html                         Impressum + DSGVO
├── data.js                            Config centrale bilingue
├── logo.svg / logo.jpg / favicon.svg  Branding
├── sitemap.xml / robots.txt           SEO
├── CNAME                              bergische-lk.de
├── CLAUDE.md                          Doc dev
├── PROJET_TENNIS_LK.md                CE FICHIER
├── leads/                             Leads (vide)
└── .github/workflows/                 CI/CD

~/CURSOR-RAG/                          ← REPO RAG (scripts + données)
├── src/etl/extract_tennis_players.py  Extraction joueurs Gmail > CSV
├── scripts/build_tournament_db.py     Extraction joueurs Qdrant > SQLite
├── output/
│   ├── tennis_players_male.csv        179 joueurs (données brutes)
│   ├── mailing_list_tournois.html     174 jeunes (HTML formaté)
│   ├── sponsoring_dossier.html        Dossier sponsoring pro
│   └── gmail_attachments/             PDFs tournois récupérés
└── ...

Notion                                 ← STRATÉGIE + CRM
├── Tournois LK — Concept             Master doc (P&L, offre, template email)
├── Vereine Partnerschaft — Leads      CRM pipeline clubs
└── Emeric — Tennis LK 12/13           Suivi perso Emeric
```

---

## Prochaines étapes (backlog)

| Priorité | Tâche | Dépendance |
|----------|-------|-----------|
| 🔴 | Setup email info@bergische-lk.de (MX/forwarding) | Hébergement DNS |
| 🔴 | Envoyer emails prospection clubs Bezirk 4 | Données clubs + email fonctionnel |
| 🟡 | Scraping TVN live (clubs Bezirk 4, terrains, contacts) | Script à construire |
| 🟡 | Importer clubs scrapés dans CRM Notion | Scraping TVN |
| 🟡 | Configurer newsletter (Buttondown/Brevo) | Choix outil |
| 🟡 | Construire template affiche tournoi + QR code | Charte graphique OK |
| 🟢 | Générer affiches pour chaque tournoi saison 2026 | Template affiche |
| 🟢 | Template email parents (annonce tournoi) | Newsletter configurée |
| 🟢 | Galerie photos site (avec consentement KUG §22) | Photos tournois |
| 🟢 | Compléter placeholders data.js (tel, Instagram, WhatsApp) | Comptes créés |

---

*Dernière mise à jour : 2026-04-08*
*Maintenu par : JCD + Claude*
