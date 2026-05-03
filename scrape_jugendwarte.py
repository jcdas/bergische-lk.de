#!/usr/bin/env python3
"""
Scrape nuLiga TVN Bezirk 4 — Jugendwart emails + names for all clubs.
Cities around Haan (42781), including Mettmann & Erkrath.
Outputs CSV + console summary.
"""

from __future__ import annotations

import csv
import os
import re
import sys
from datetime import datetime
from typing import List, Dict

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# ── Config ──────────────────────────────────────────────────────────────────
OUTPUT_CSV = os.path.join(os.path.dirname(__file__), "jugendwarte_bezirk4.csv")
START_URL = (
    "https://tvn.liga.nu/cgi-bin/WebObjects/nuLigaTENDE.woa/wa/clubSearch"
    "?federation=TVN&showSearchForm=1"
)
BASE_URL = "https://tvn.liga.nu"
HEADLESS = True
TIMEOUT = 15_000  # ms

EXCLUDED_CLUBS = [
    "tc hilden stadtwald",
    "stadtwald hilden",
    "grün-weiß langenfeld",
    "grun-weiss langenfeld",
    "gruen-weiss langenfeld",
    "grün weiß langenfeld",
]

CITIES = [
    ("Mettmann", "~6 km"),
    ("Erkrath", "~7 km"),
    ("Wülfrath", "~5 km"),
    ("Hilden", "~8 km"),
    ("Haan", "~0 km"),
    ("Solingen", "~10 km"),
    ("Velbert", "~12 km"),
    ("Langenfeld", "~13 km"),
    ("Remscheid", "~14 km"),
    ("Leichlingen", "~15 km"),
    ("Wuppertal", "~16 km"),
    ("Burscheid", "~17 km"),
    ("Monheim am Rhein", "~18 km"),
    ("Heiligenhaus", "~19 km"),
]

# Roles to extract (priority order — Jugendwart first)
TARGET_ROLES = [
    "1. jugendwart",
    "jugendwart",
    "jugendwartin",
    "2. jugendwart",
    "2. jugendwartin",
]

# Fallback roles if no Jugendwart found
FALLBACK_ROLES = [
    "1. sportwart",
    "sportwart",
    "1. vorsitzende",
    "1. vorsitzender",
    "vorsitzende",
    "vorsitzender",
    "geschäftsführer",
    "geschäftsführerin",
]


# ── Helpers ─────────────────────────────────────────────────────────────────
def normalize(name: str) -> str:
    return re.sub(r"[-–—]", " ", name.strip().lower())


def is_excluded(club_name: str) -> bool:
    n = normalize(club_name)
    return any(exc in n for exc in EXCLUDED_CLUBS)


# ── Extract Plätze + Mitgliederzahlen from Vereinsinfo ─────────────────────
def extract_club_stats(page) -> Dict[str, any]:
    """Extract from the Vereinsinfo page:
    - Plätze: Freiplätze, Hallenplätze
    - Mitgliederzahlen: age breakdown (0-6, 7-14, 15-18, etc.)
    Returns dict with courts and youth member counts."""
    result = {
        "freiplaetze": "?",
        "hallenplaetze": "0",
        "jugend_0_6_m": 0, "jugend_0_6_w": 0, "jugend_0_6": 0,
        "jugend_7_14_m": 0, "jugend_7_14_w": 0, "jugend_7_14": 0,
        "jugend_15_18_m": 0, "jugend_15_18_w": 0, "jugend_15_18": 0,
        "jugend_m": 0, "jugend_w": 0, "jugend_gesamt": 0,
        "mitglieder_gesamt": 0,
    }

    try:
        # ── Plätze table ──
        # Rows like: "7  Freiplätze  Aschenplatz"
        body = page.inner_text("body")

        m = re.search(r"(\d+)\s+Freiplätze", body)
        if m:
            result["freiplaetze"] = m.group(1)
        m = re.search(r"(\d+)\s+Hallenplätze", body)
        if m:
            result["hallenplaetze"] = m.group(1)

        # ── Mitgliederzahlen table ──
        # Format: "Alter  männlich  weiblich  Gesamt"
        # Rows:   "0-6    1         0         1"
        #         "7-14   27        10        37"
        #         "15-18  10        26        36"
        #         ...
        #         "Gesamt 119       95        214"

        # Extract each age group: männlich, weiblich, Gesamt
        # Row format: "7-14  27  10  37"
        age_groups = {
            "0_6":   r"0\s*-\s*6\s+(\d+)\s+(\d+)\s+(\d+)",
            "7_14":  r"7\s*-\s*14\s+(\d+)\s+(\d+)\s+(\d+)",
            "15_18": r"15\s*-\s*18\s+(\d+)\s+(\d+)\s+(\d+)",
        }
        for suffix, pattern in age_groups.items():
            m = re.search(pattern, body)
            if m:
                result[f"jugend_{suffix}_m"] = int(m.group(1))
                result[f"jugend_{suffix}_w"] = int(m.group(2))
                result[f"jugend_{suffix}"] = int(m.group(3))

        result["jugend_m"] = (
            result["jugend_0_6_m"] + result["jugend_7_14_m"] + result["jugend_15_18_m"]
        )
        result["jugend_w"] = (
            result["jugend_0_6_w"] + result["jugend_7_14_w"] + result["jugend_15_18_w"]
        )
        result["jugend_gesamt"] = (
            result["jugend_0_6"] + result["jugend_7_14"] + result["jugend_15_18"]
        )

        # Total members
        m = re.search(r"Gesamt\s+\d+\s+\d+\s+(\d+)", body)
        if m:
            result["mitglieder_gesamt"] = int(m.group(1))

    except Exception:
        pass

    return result


# ── Extract Jugendwart contacts ────────────────────────────────────────────
def extract_jugendwart(page) -> List[Dict[str, str]]:
    """Extract Jugendwart contacts from club info page.
    nuLiga shows rows: Rolle | Nachname, Vorname | Tel | Email
    Returns list of {role, name, email, phone}."""
    all_contacts = []
    found_emails = set()

    try:
        mailto_links = page.query_selector_all("a[href^='mailto:']")
        for link in mailto_links:
            email = link.get_attribute("href").replace("mailto:", "").strip()
            if email in found_emails:
                continue

            row_text = link.evaluate(
                "el => { let tr = el.closest('tr'); "
                "return tr ? tr.innerText : "
                "(el.parentElement ? el.parentElement.innerText : '') }"
            )
            if not row_text:
                continue

            row_lower = row_text.lower()

            # Skip team contacts
            if any(skip in row_lower for skip in [
                "damen", "herren", "u10", "u11", "u12", "u13", "u14", "u15",
                "u16", "u17", "u18", "platzadresse", "hallenadresse",
                "postadresse", "männlich", "weiblich", "mixed",
            ]):
                continue

            # Find role
            role = None
            is_jugendwart = False
            for r in TARGET_ROLES:
                if r in row_lower:
                    role = r.title()
                    is_jugendwart = True
                    break
            if not role:
                for r in FALLBACK_ROLES:
                    if r in row_lower:
                        role = r.title()
                        break
            if not role:
                role = "Kontakt"

            # Extract name (Nachname, Vorname -> Vorname Nachname)
            parts = row_text.split("\t")
            name = ""
            phone = ""
            for p in parts:
                p = p.strip()
                if "," in p and "@" not in p and len(p) > 3:
                    if not re.match(r"^\d", p):
                        name_parts = p.split(",", 1)
                        if len(name_parts) == 2:
                            name = f"{name_parts[1].strip()} {name_parts[0].strip()}"
                        else:
                            name = p
                # Phone: digits with spaces/dashes, at least 6 chars
                if re.match(r"^[\d\s/\-\+]{6,}$", p):
                    phone = p.strip()

            all_contacts.append({
                "role": role,
                "name": name or "NC",
                "email": email,
                "phone": phone,
                "is_jugendwart": is_jugendwart,
            })
            found_emails.add(email)

    except Exception:
        pass

    return all_contacts


# ── Main ───────────────────────────────────────────────────────────────────
def scrape():
    results = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=HEADLESS)
        context = browser.new_context(
            locale="de-DE", viewport={"width": 1280, "height": 900}
        )
        page = context.new_page()
        page.set_default_timeout(TIMEOUT)

        for city_name, distance in CITIES:
            print(f"\n{'='*50}")
            print(f"  {city_name} ({distance})")
            print(f"{'='*50}")

            try:
                page.goto(START_URL, wait_until="domcontentloaded", timeout=TIMEOUT)
                page.wait_for_timeout(1000)
                page.fill('input[name="searchFor"]', city_name)
                page.click('input[name="clubSearch"]')
                page.wait_for_load_state("domcontentloaded", timeout=TIMEOUT)
                page.wait_for_timeout(1500)

                # Collect club links
                club_links = []
                links = page.query_selector_all("a[href*='clubInfoDisplay']")
                for link in links:
                    href = link.get_attribute("href") or ""
                    name = link.inner_text().strip()
                    if not name or len(name) < 3:
                        continue
                    if name.upper() in ("VEREINSINFO", "BEGEGNUNGEN", "MANNSCHAFTEN"):
                        continue
                    if not href.startswith("http"):
                        href = BASE_URL + href
                    club_links.append((name, href))

                # Handle single-result redirect
                if not club_links:
                    h1 = page.query_selector("h1")
                    if h1:
                        h1_text = h1.inner_text().strip()
                        h1_text = re.sub(r"\s*Vereinsinfo\s*$", "", h1_text).strip()
                        beg_link = page.query_selector("a[href*='clubMeetings']")
                        if beg_link and h1_text and len(h1_text) > 5:
                            beg_href = beg_link.get_attribute("href") or ""
                            club_id_m = re.search(r"club=(\d+)", beg_href)
                            if club_id_m:
                                club_id = club_id_m.group(1)
                                info_url = f"{BASE_URL}/cgi-bin/WebObjects/nuLigaTENDE.woa/wa/clubInfoDisplay?club={club_id}"
                                club_links.append((h1_text, info_url))

                if not club_links:
                    print(f"  → Aucun club trouvé")
                    continue

                for club_name, club_url in club_links:
                    if is_excluded(club_name):
                        print(f"  ⊘ {club_name} — exclu")
                        continue

                    print(f"  → {club_name}", end="")

                    try:
                        page.goto(club_url, wait_until="domcontentloaded", timeout=TIMEOUT)
                        page.wait_for_timeout(1000)

                        try:
                            official_name = page.locator("h1").first.inner_text().strip()
                            official_name = re.sub(r"\s*Vereinsinfo\s*$", "", official_name).strip()
                        except Exception:
                            official_name = club_name

                        # Extract Plätze + Mitgliederzahlen from Vereinsinfo
                        stats = extract_club_stats(page)

                        # Extract contacts (also from Vereinsinfo page)
                        contacts = extract_jugendwart(page)

                        # Pick Jugendwart if available, otherwise fallback
                        jugendwart = [c for c in contacts if c["is_jugendwart"]]
                        fallback = [c for c in contacts if not c["is_jugendwart"] and c["role"] != "Kontakt"]

                        chosen = jugendwart or fallback
                        if not chosen:
                            chosen = contacts[:1]  # take first available

                        base_row = {
                            "Stadt": city_name,
                            "Distanz": distance,
                            "Verein": official_name,
                            "Freiplaetze": stats["freiplaetze"],
                            "Hallenplaetze": stats["hallenplaetze"],
                            "Jugend_0_6_M": stats["jugend_0_6_m"],
                            "Jugend_0_6_W": stats["jugend_0_6_w"],
                            "Jugend_0_6": stats["jugend_0_6"],
                            "Jugend_7_14_M": stats["jugend_7_14_m"],
                            "Jugend_7_14_W": stats["jugend_7_14_w"],
                            "Jugend_7_14": stats["jugend_7_14"],
                            "Jugend_15_18_M": stats["jugend_15_18_m"],
                            "Jugend_15_18_W": stats["jugend_15_18_w"],
                            "Jugend_15_18": stats["jugend_15_18"],
                            "Jugend_M": stats["jugend_m"],
                            "Jugend_W": stats["jugend_w"],
                            "Jugend_Gesamt": stats["jugend_gesamt"],
                            "Mitglieder_Gesamt": stats["mitglieder_gesamt"],
                            "URL": club_url,
                        }

                        if chosen:
                            for c in chosen:
                                results.append({
                                    **base_row,
                                    "Rolle": c["role"],
                                    "Name": c["name"],
                                    "Email": c["email"],
                                    "Telefon": c["phone"],
                                })
                            jw_tag = " ✓ JW" if jugendwart else " (fallback)"
                            print(f" — {chosen[0]['name']} ({chosen[0]['role']}){jw_tag} | {stats['freiplaetze']}F+{stats['hallenplaetze']}H, {stats['jugend_gesamt']}J ({stats['jugend_m']}M/{stats['jugend_w']}W)")
                        else:
                            results.append({
                                **base_row,
                                "Rolle": "",
                                "Name": "",
                                "Email": "",
                                "Telefon": "",
                            })
                            print(f" — kein Kontakt | {stats['freiplaetze']}F+{stats['hallenplaetze']}H, {stats['jugend_gesamt']}J ({stats['jugend_m']}M/{stats['jugend_w']}W)")

                    except PWTimeout:
                        print(f" — TIMEOUT")
                    except Exception as e:
                        print(f" — FEHLER: {e}")

            except Exception as e:
                print(f"  FEHLER bei Stadtsuche: {e}")

        browser.close()

    # Export CSV
    fields = ["Stadt", "Distanz", "Verein", "Freiplaetze", "Hallenplaetze",
              "Jugend_0_6_M", "Jugend_0_6_W", "Jugend_0_6",
              "Jugend_7_14_M", "Jugend_7_14_W", "Jugend_7_14",
              "Jugend_15_18_M", "Jugend_15_18_W", "Jugend_15_18",
              "Jugend_M", "Jugend_W", "Jugend_Gesamt",
              "Mitglieder_Gesamt", "Rolle", "Name", "Email", "Telefon", "URL"]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    # Summary
    total = len(results)
    with_jw = sum(1 for r in results if "jugendwart" in r["Rolle"].lower())
    with_email = sum(1 for r in results if r["Email"])
    print(f"\n{'='*50}")
    print(f"  RÉSUMÉ")
    print(f"{'='*50}")
    print(f"  Clubs trouvés   : {total}")
    print(f"  Avec Jugendwart : {with_jw}")
    print(f"  Avec email      : {with_email}")
    print(f"  CSV             : {OUTPUT_CSV}")
    print(f"{'='*50}")

    # Print table
    print(f"\n{'Verein':<35} {'Plätze':<8} {'J.M':<5} {'J.W':<5} {'J.Tot':<6} {'Mitgl':<7} {'Rolle':<18} {'Name':<22} {'Email'}")
    print("-" * 155)
    for r in results:
        tag = "★" if "jugendwart" in r["Rolle"].lower() else " "
        plaetze = f"{r['Freiplaetze']}F+{r['Hallenplaetze']}H"
        print(f"{tag} {r['Verein']:<33} {plaetze:<8} {str(r['Jugend_M']):<5} {str(r['Jugend_W']):<5} {str(r['Jugend_Gesamt']):<6} {str(r['Mitglieder_Gesamt']):<7} {r['Rolle']:<18} {r['Name']:<22} {r['Email']}")


if __name__ == "__main__":
    scrape()
