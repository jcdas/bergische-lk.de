# Setup Brevo (ex-Sendinblue) pour Bergische LK-Turniere

## Pourquoi Brevo ?

- Gratuit jusqu'a 300 emails/jour
- Unsubscribe GDPR integre (obligatoire)
- Merge tags pour personnalisation (prenom, club, categorie)
- Tracking ouvertures/clics
- API Python disponible si besoin d'automatisation

## Etapes de configuration

### 1. Creer le compte

1. Aller sur https://www.brevo.com
2. S'inscrire avec info@bergische-lk.de (ou jcdas1@gmail.com)
3. Plan gratuit = 300 emails/jour, suffisant pour 174 contacts

### 2. Verifier le domaine (DKIM + SPF)

Pour que les emails ne finissent pas en spam :

1. Brevo > Settings > Senders & IPs > Domains
2. Ajouter `bergische-lk.de`
3. Brevo donne 3 enregistrements DNS a ajouter :
   - **DKIM** : `mail._domainkey.bergische-lk.de` TXT record
   - **SPF** : modifier le TXT SPF existant pour inclure `include:sendinblue.com`
   - **DMARC** : optionnel mais recommande
4. Ajouter ces records chez ton registrar DNS (Namecheap, Cloudflare, etc.)
5. Verifier dans Brevo (propagation DNS : 5 min a 24h)

### 3. Preparer le CSV

```bash
cd ~/Tennis
python scripts/prepare_mailing.py
```

Ca genere `mailing_brevo_import.csv` avec les colonnes :
- EMAIL, VORNAME, NACHNAME, TELEFON, VEREIN, KATEGORIEN, ANZAHL_TURNIERE

### 4. Importer les contacts

1. Brevo > Contacts > Import contacts
2. Uploader `mailing_brevo_import.csv`
3. Separateur : point-virgule (;)
4. Mapper les colonnes sur les attributs Brevo
5. Creer une liste "LK Turniere 2026"

### 5. Creer la campagne

1. Brevo > Campaigns > Create an email campaign
2. Nom : "ESV Summer Smash Series 1 - 02.05.2026"
3. Sender : Jean-Charles Das <info@bergische-lk.de>
4. Reply-to : info@bergische-lk.de
5. Template : coller le HTML de `email_templates/tournoi_annonce.html`
6. Audience : liste "LK Turniere 2026"
7. **IMPORTANT** : envoyer une testmail a soi-meme d'abord

### 6. Verifier avant envoi

- [ ] Unsubscribe link fonctionne ({{ unsubscribe }} remplace par Brevo)
- [ ] Merge tags remplaces correctement ({{ contact.VORNAME }} etc.)
- [ ] Lien tennis.de pointe vers le bon tournoi
- [ ] Pas de fautes dans le texte allemand
- [ ] Email responsive sur mobile
- [ ] Sender verifie (pas en spam)

### 7. Envoyer

1. Brevo > Review & Send
2. Choisir "Send now" ou programmer un horaire (mardi/mercredi matin = meilleur taux d'ouverture)
3. Surveiller les stats apres envoi (taux ouverture, clics, unsubscribes)

## Merge tags disponibles

| Tag | Contenu | Exemple |
|-----|---------|---------|
| `{{ contact.VORNAME }}` | Prenom | Leo |
| `{{ contact.NACHNAME }}` | Nom | Dihne |
| `{{ contact.VEREIN }}` | Club | TC Stadtwald Hilden e.V. |
| `{{ contact.KATEGORIEN }}` | Categories | U14, U16 |
| `{{ contact.EMAIL }}` | Email | parent@example.de |
| `{{ unsubscribe }}` | Lien desinscription | Auto-genere par Brevo |

## GDPR Compliance

- **Base legale** : Art. 6(1)(f) DSGVO, berechtigtes Interesse
- **Source des donnees** : inscriptions precedentes via nuLiga (donnees du tournoi)
- **Opt-out** : lien Brevo 1-clic en footer de chaque email
- **Donnees stockees** : email, nom, club, categorie (rien de sensible)
- **Droit d'acces/suppression** : via info@bergische-lk.de

## Pour les prochains tournois

1. Dupliquer `tournoi_annonce.html`
2. Modifier les details (nom, date, venue, lien tennis.de)
3. Creer une nouvelle campagne dans Brevo
4. Reenvoyer a la meme liste (moins les unsubscribed, geres automatiquement)
