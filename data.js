/*
 * ============================================================
 *  BERGISCHE LK-TURNIERE — CONFIGURATION
 * ============================================================
 *
 *  Pour modifier le contenu du site, éditez CE FICHIER uniquement.
 *  Sauvegardez, commitez, poussez → le site se met à jour.
 *
 *  Format : chaque texte a une version { de: "...", en: "..." }
 *
 * ============================================================
 */

const SITE = {

  // ── GÉNÉRAL ─────────────────────────────────────────────
  name: "Bergische LK-Turniere",
  email: "info@bergische-lk.de",
  organizer: "Jean-Charles Das",
  organizerShort: "Jean-Charles",
  year: 2026,
  domain: "bergische-lk.de",

  // ── IMPRESSUM (à compléter avec tes vraies données) ────
  impressum: {
    fullName: "Jean-Charles Das",
    address: "Bergstr. 10, 42781 Haan",
    email: "info@bergische-lk.de",
    responsible: "Jean-Charles Das",             // Verantwortlich i.S.d. §18 Abs. 2 MStV
  },

  // ── NEWSLETTER ─────────────────────────────────────────
  // Mettre l'URL du formulaire Buttondown / Brevo quand prêt
  newsletter: {
    enabled: true,
    // action: "https://buttondown.com/api/emails/embed-subscribe/bergische-lk",
    action: "",  // ← à remplir avec ton service newsletter
    placeholder: { de: "Deine E-Mail-Adresse", en: "Your email address" },
    cta: { de: "ANMELDEN", en: "SUBSCRIBE" },
    text: {
      de: "Erhalte Infos zu kommenden Turnieren direkt in dein Postfach.",
      en: "Get info about upcoming tournaments straight to your inbox.",
    },
  },

  // ── FAQ ────────────────────────────────────────────────
  faq: [
    {
      q: { de: "Brauche ich eine DTB-Nummer?", en: "Do I need a DTB number?" },
      a: { de: "Ja, für die Anmeldung über mybigpoint.tennis.de ist eine gültige DTB-Nummer erforderlich.", en: "Yes, a valid DTB number is required to register via mybigpoint.tennis.de." },
    },
    {
      q: { de: "Was passiert bei Regen?", en: "What happens if it rains?" },
      a: { de: "Bei Regen werden die Spiele verschoben. Bitte prüfen Sie unsere Instagram-Seite oder WhatsApp-Gruppe für aktuelle Updates.", en: "Matches are postponed in case of rain. Please check our Instagram page or WhatsApp group for live updates." },
    },
    {
      q: { de: "Gibt es Umkleiden und Duschen?", en: "Are there changing rooms and showers?" },
      a: { de: "Ja, beide Anlagen verfügen über Umkleidekabinen und Duschen.", en: "Yes, both venues have changing rooms and showers." },
    },
    {
      q: { de: "Wie funktioniert der Check-in am Turniertag?", en: "How does check-in work on match day?" },
      a: { de: "Bitte melden Sie sich mindestens 30 Minuten vor Ihrem ersten Spiel am Turnierbüro. Bringen Sie einen Ausweis mit.", en: "Please check in at the tournament desk at least 30 minutes before your first match. Bring valid ID." },
    },
    {
      q: { de: "Gibt es Parkplätze?", en: "Is there parking?" },
      a: { de: "Ja, beide Anlagen bieten kostenlose Parkplätze in der Nähe.", en: "Yes, both venues have free parking nearby." },
    },
    {
      q: { de: "Werden Fotos gemacht?", en: "Will photos be taken?" },
      a: { de: "Ja, während der Turniere werden Fotos gemacht. Am Check-in können Sie Ihre Einwilligung zur Veröffentlichung erteilen. Diese kann jederzeit widerrufen werden (info@bergische-lk.de).", en: "Yes, photos are taken during tournaments. You can give consent for publication at check-in. Consent can be withdrawn at any time (info@bergische-lk.de)." },
    },
  ],

  // ── SAISON / DATES ──────────────────────────────────────
  season: {
    label: { de: "SAISON 2026", en: "SEASON 2026" },
    status: { de: "TERMINE FOLGEN", en: "DATES TBA" },
    // Quand les dates sont confirmées, passer à :
    // status: { de: "MAI — SEPTEMBER", en: "MAY — SEPTEMBER" },
  },

  // ── HERO (index.html) ──────────────────────────────────
  hero: {
    title: { de: "BERGISCHE <span>LK-TURNIERE</span>", en: "BERGISCHE <span>LK TOURNAMENTS</span>" },
    subtitle: {
      de: "Offizielle DTB-Turniere auf Sandplatz im Bergischen Land",
      en: "Official DTB tournaments on clay courts in Bergisches Land",
    },
    cta: {
      url: "#tournaments",
      label: { de: "UNSERE TURNIERE", en: "OUR TOURNAMENTS" },
    },
    // Image de fond (Unsplash free — terre battue close-up)
    image: "https://images.unsplash.com/photo-1554068865-24cecd4e34b8?w=1600&q=80",  // clay court surface close-up with line
  },

  // ── TOURNOIS ────────────────────────────────────────────
  //  Ajoutez / supprimez des tournois ici.
  //  Ils s'afficheront automatiquement sur la page d'accueil.
  tournaments: [
    {
      id: "esv-open-2026",
      name: "ESV Open",
      venue: "esv-wuppertal",        // doit correspondre à un id dans venues[]
      dates: { de: "Termin folgt", en: "Date TBA" },
      categories: ["U12", "U14", "U16"],
      status: "upcoming",            // upcoming | registration | ongoing | completed
      mybigpoint: "",                 // lien direct mybigpoint quand disponible
    },
    {
      id: "gruiten-cup-2026",
      name: "Gruiten Cup",
      venue: "tc-gruiten",
      dates: { de: "Termin folgt", en: "Date TBA" },
      categories: ["U14", "U16", "H00"],
      status: "upcoming",
      mybigpoint: "",
    },
    // ➕ Ajoutez un nouveau tournoi ici :
    // {
    //   id: "mon-tournoi",
    //   name: "Mon Tournoi",
    //   venue: "esv-wuppertal",
    //   dates: { de: "15.–17. Juli 2026", en: "Jul 15–17, 2026" },
    //   categories: ["U16", "H00"],
    //   status: "upcoming",
    //   mybigpoint: "https://mybigpoint.tennis.de/...",
    // },
  ],

  // ── ANLAGEN / VENUES ────────────────────────────────────
  venues: [
    {
      id: "esv-wuppertal",
      name: "ESV Wuppertal West",
      address: "Homannstr. 33b, 42327 Wuppertal",
      courts: 7,
      surface: { de: "Sandplätze (Terre Battue)", en: "Clay courts (Terre Battue)" },
      image: "https://images.unsplash.com/photo-1751275061863-db6d9d0857ce?w=800&q=80",  // court TB avec filet Roland Garros
      maps: "https://maps.google.com/?q=Homannstr.+33b,+42327+Wuppertal",
    },
    {
      id: "tc-gruiten",
      name: "TC Gruiten",
      address: "Neandertalweg 6, 42781 Haan",
      courts: 6,
      surface: { de: "Sandplätze (Terre Battue)", en: "Clay courts (Terre Battue)" },
      image: "https://images.unsplash.com/photo-1752400879796-fa953a301e11?w=800&q=80",  // chaise Perrier terre battue Roland Garros
      maps: "https://maps.google.com/?q=Neandertalweg+6,+42781+Haan",
    },
  ],

  // ── RÈGLEMENT ───────────────────────────────────────────
  rules: [
    {
      title: { de: "Satzformat", en: "Set Format" },
      text: { de: "2 Gewinnsätze bis 6 Spiele", en: "Best of 3 sets, first to 6 games" },
    },
    {
      title: { de: "Tie-Break", en: "Tie-Break" },
      text: { de: "Tie-Break bei 6:6 in jedem Satz", en: "Tie-break at 6:6 in each set" },
    },
    {
      title: { de: "3. Satz", en: "3rd Set" },
      text: { de: "Match-Tie-Break bis 10 Punkte im 3. Satz", en: "Match tie-break to 10 points in the 3rd set" },
    },
    {
      title: { de: "Anmeldung", en: "Registration" },
      text: { de: "Über mybigpoint.tennis.de — DTB-Nummer erforderlich", en: "Via mybigpoint.tennis.de — DTB number required" },
    },
  ],

  // ── CATÉGORIES D'ÂGE ───────────────────────────────────
  categories: ["U12", "U14", "U16", "H00"],

  // ── SPONSORING ──────────────────────────────────────────
  sponsoring: [
    {
      tier: "bronze",
      label: "BRONZE",
      perks: [
        { de: "Logo auf der Website", en: "Logo on the website" },
        { de: "Erwähnung in Social Media", en: "Social media mention" },
        { de: "Banner vor Ort (1 Turnier)", en: "On-site banner (1 tournament)" },
      ],
    },
    {
      tier: "silver",
      label: "SILBER",
      featured: true,
      perks: [
        { de: "Alles aus Bronze +", en: "Everything in Bronze +" },
        { de: "Logo auf Spielerpässen", en: "Logo on player passes" },
        { de: "Banner vor Ort (alle Turniere)", en: "On-site banner (all tournaments)" },
        { de: "Story-Feature auf Instagram", en: "Instagram story feature" },
      ],
    },
    {
      tier: "gold",
      label: "GOLD",
      perks: [
        { de: "Alles aus Silber +", en: "Everything in Silver +" },
        { de: "Namenssponsor eines Turniers", en: "Title sponsor of a tournament" },
        { de: "Exklusiver Stand vor Ort", en: "Exclusive booth on-site" },
        { de: "Highlights-Video mit Logo", en: "Highlights video with logo" },
      ],
    },
  ],

  // ── RÉSEAUX SOCIAUX ─────────────────────────────────────
  social: {
    instagram: "https://instagram.com/bergische.lk.turniere",  // à mettre à jour
    whatsapp: "https://wa.me/491234567890",                     // à mettre à jour
  },

  // ── GALERIE ─────────────────────────────────────────────
  //  Ajoutez des photos de tournois ici.
  //  consent: true = la personne a donné son accord (Einwilligung)
  //  Seules les photos avec consent: true seront affichées.
  gallery: {
    enabled: false,  // ← passer à true quand vous avez des photos
    photos: [
      // {
      //   src: "photos/esv-open-2026-01.jpg",
      //   alt: { de: "Spieler auf Sandplatz", en: "Player on clay court" },
      //   tournament: "esv-open-2026",
      //   consent: true,
      // },
    ],
  },

  // ── CLUBS PAGE (clubs.html) ─────────────────────────────
  clubs: {
    hero: {
      title: {
        de: "SIE WOLLEN EIN LK-TURNIER ORGANISIEREN?<br><span>WIR ÜBERNEHMEN ALLES.</span>",
        en: "WANT TO ORGANIZE AN LK TOURNAMENT?<br><span>WE HANDLE EVERYTHING.</span>",
      },
      subtitle: {
        de: "Von der Anmeldung beim DTB über die Kommunikation mit dem WTB bis zur Durchführung am Turniertag — wir kümmern uns um alles.",
        en: "From DTB registration and WTB communication to tournament day operations — we take care of everything.",
      },
      image: "https://images.unsplash.com/photo-1646343253681-eaafc374b2b1?w=1600&q=80",  // chaussures joueur terre battue gros plan
    },
    services: [
      {
        icon: "document",
        title: { de: "BIG POINT", en: "BIG POINT" },
        text: {
          de: "Komplette Turnieranmeldung und -verwaltung über das DTB-Portal mybigpoint.tennis.de",
          en: "Complete tournament registration and management via the DTB portal mybigpoint.tennis.de",
        },
      },
      {
        icon: "check",
        title: { de: "WTB-KOORDINATION", en: "WTB COORDINATION" },
        text: {
          de: "Abstimmung mit dem Westfälischen Tennis-Bund: Genehmigungen, Oberschiedsrichter, Regularien",
          en: "Coordination with the Westphalian Tennis Federation: approvals, chief umpires, regulations",
        },
      },
      {
        icon: "logistics",
        title: { de: "LOGISTIK", en: "LOGISTICS" },
        text: {
          de: "Bälle, Beschilderung, Spielplan-Aushang, Verpflegung — wir koordinieren alles vor Ort",
          en: "Balls, signage, draw sheets, catering — we coordinate everything on-site",
        },
      },
      {
        icon: "clock",
        title: { de: "TURNIERTAG", en: "MATCH DAY" },
        text: {
          de: "Turnierleitung vor Ort, Spieler-Check-in, Zeitplan-Management, Ergebnismeldung an den DTB",
          en: "On-site tournament direction, player check-in, schedule management, result reporting to DTB",
        },
      },
    ],
    steps: [
      {
        title: { de: "ANFRAGE", en: "INQUIRY" },
        text: { de: "Füllen Sie das Formular aus — wir melden uns innerhalb von 48h", en: "Fill out the form — we'll get back to you within 48h" },
      },
      {
        title: { de: "PLANUNG", en: "PLANNING" },
        text: { de: "Gemeinsame Abstimmung zu Terminen, Kategorien und Umfang", en: "Joint coordination on dates, categories and scope" },
      },
      {
        title: { de: "ANMELDUNG", en: "REGISTRATION" },
        text: { de: "Wir übernehmen die komplette Anmeldung bei DTB & WTB", en: "We handle the complete registration with DTB & WTB" },
      },
      {
        title: { de: "TURNIER", en: "TOURNAMENT" },
        text: { de: "Wir leiten das Turnier — Ihr Verein genießt den Tag", en: "We run the tournament — your club enjoys the day" },
      },
    ],
    formPeriods: [
      { value: "mai-juni", label: "Mai – Juni / May – June" },
      { value: "juli-august", label: "Juli – August / Jul – Aug" },
      { value: "september-oktober", label: "September – Oktober / Sep – Oct" },
      { value: "flexibel", label: { de: "Flexibel", en: "Flexible" } },
    ],
  },
};
