#!/usr/bin/env python3
"""
Tennis Weekly Results Report
Scrapes tennis.de for match results of tracked players (last 7 days)
and sends an HTML email summary.

Run manually:   python3 tennis_weekly_report.py
Cron (Sunday 20:00): 0 20 * * 0 ...

Requires:
  pip3 install playwright && playwright install chromium
  export TENNIS_LOGIN_EMAIL="ton-email@tennis.de"
  export TENNIS_LOGIN_PASSWORD="ton-mot-de-passe"
  export TENNIS_GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"

Gmail App Password:
  https://myaccount.google.com/apppasswords
  -> Creer un mot de passe pour "Tennis Report"
"""

import asyncio
import os
import re
import smtplib
import sys
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from playwright.async_api import async_playwright

# -----------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------
PLAYERS = [
    {"name": "Erik Dhamo",     "dtb_id": "11000338", "nu_id": "NU3149591"},
    {"name": "Nicolas Ihlo",   "dtb_id": "11150919", "nu_id": "NU2592296"},
    {"name": "Moritz Volck",   "dtb_id": "11155100", "nu_id": "NU2780674"},
    {"name": "John Knittel",   "dtb_id": "11152267", "nu_id": "NU2659194"},
    {"name": "Anton Wiedmann", "dtb_id": "11152412", "nu_id": "NU2681833"},
]

RECIPIENTS     = ["jcdas1@gmail.com", "nath0612@yahoo.de"]

# --- Load .env from emeric-coaching-os (source of truth for shared creds) ---
_ENV_FILE = "/srv/.env.secrets"
def _load_env(path):
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                v = v.strip().strip('"').strip("'")
                os.environ[k.strip()] = v  # force (ecrase si vide)
    except FileNotFoundError:
        pass
_load_env(_ENV_FILE)

SENDER_EMAIL   = os.environ.get("TENNIS_SENDER_EMAIL", "jcdas1@gmail.com")
GMAIL_APP_PW   = os.environ.get("TENNIS_GMAIL_APP_PASSWORD") or os.environ.get("GMAIL_APP_PASSWORD", "")
TENNIS_EMAIL   = os.environ.get("TENNIS_LOGIN_EMAIL") or os.environ.get("TENNIS_DE_EMAIL", "")
TENNIS_PASS    = os.environ.get("TENNIS_LOGIN_PASSWORD") or os.environ.get("TENNIS_DE_PASSWORD", "")

BASE_URL       = "https://www.tennis.de/spielen/spielerprofil.html#id={nu_id}/games"
SESSION_FILE   = os.path.join(os.path.dirname(__file__), "..", ".tennis_session.json")
DAYS_BACK      = 7   # look-back window


# -----------------------------------------------------------------------
# Date helpers
# -----------------------------------------------------------------------
def parse_date_de(s: str):
    try:
        return datetime.strptime(s.strip(), "%d.%m.%Y")
    except ValueError:
        return None


# -----------------------------------------------------------------------
# Match-text parser
# -----------------------------------------------------------------------
def parse_matches(raw_text: str, player_name: str, cutoff: datetime) -> list:
    """
    Parse inner_text from the /games page.
    Returns list of match dicts for matches on or after `cutoff`.
    """
    player_last = player_name.split()[-1]
    lines = [l.strip() for l in raw_text.split("\n") if l.strip()]

    matches = []
    current_date = None
    current_tournament = None

    i = 0
    while i < len(lines):
        line = lines[i]

        # --- Date line DD.MM.YYYY ---
        if re.match(r"^\d{2}\.\d{2}\.\d{4}$", line):
            dt = parse_date_de(line)
            if dt:
                current_date = dt
            i += 1
            continue

        # --- Tournament / competition header ---
        if (current_date is None or True) and re.search(
            r"Liga|Turnier|Race|Bundesliga|Verband|Mannschaft|Meisterschaft|Cup", line
        ) and len(line) < 120:
            current_tournament = line
            i += 1
            continue

        # --- Match line containing tracked player ---
        if (
            player_last in line
            and current_date is not None
            and current_date >= cutoff
        ):
            info = {
                "date": current_date.strftime("%d.%m.%Y"),
                "tournament": current_tournament or "",
                "opponent": "",
                "opponent2": "",   # for doubles
                "partner": "",     # for doubles
                "score": "",
                "lk_change": "",
                "won": None,
                "is_double": False,
            }

            # Scan next lines to fill in details
            for j in range(1, min(20, len(lines) - i)):
                nxt = lines[i + j]

                # Stop conditions
                if re.match(r"^\d{2}\.\d{2}\.\d{4}$", nxt):
                    break
                if re.search(r"Liga|Turnier|Race|Bundesliga|Verband|Meisterschaft|Cup", nxt) and len(nxt) < 120:
                    break

                # Score: "6:2 / 6:3" or "6:2" or "6:2 / 4:6 / 10:8"
                if re.match(r"^\d:\d(\s*/\s*\d:\d)*$", nxt):
                    if not info["score"]:
                        info["score"] = nxt

                # LK change: "LK +0,396" or "LK +0,0" or "LK -"
                if re.match(r"^LK [+\-]", nxt):
                    if not info["lk_change"]:
                        info["lk_change"] = nxt

                # Opponent/partner names: "Lastname, Firstname" format
                if re.match(r"^[A-Za-zÄÖÜäöü][a-zA-ZÄÖÜäöüß]+,\s+[A-Za-zÄÖÜäöü]", nxt):
                    if player_last not in nxt:
                        if not info["opponent"]:
                            info["opponent"] = nxt
                        elif not info["opponent2"]:
                            info["opponent2"] = nxt
                    elif not info["partner"]:
                        # Second player on player's side in doubles
                        info["partner"] = nxt

                # LK level lines like "LK 10,8" or "LK -"
                # These appear under player/opponent names - skip them
                if re.match(r"^LK \d", nxt) or nxt == "LK -":
                    continue

            # Determine win/loss from score
            if info["score"]:
                sets = re.findall(r"(\d):(\d)", info["score"])
                if sets:
                    p_sets = sum(1 for p, o in sets if int(p) > int(o))
                    o_sets = sum(1 for p, o in sets if int(o) > int(p))
                    info["won"] = p_sets > o_sets

            # Detect doubles (partner present OR two opponents)
            if info["partner"] or info["opponent2"]:
                info["is_double"] = True

            # Only add if we got a score
            if info["score"]:
                matches.append(info)

        i += 1

    return matches


# -----------------------------------------------------------------------
# Playwright scraper
# -----------------------------------------------------------------------
async def do_login(page):
    """Perform actual login and return True if successful."""
    if not TENNIS_EMAIL or not TENNIS_PASS:
        print("  WARNING: credentials not set — running unauthenticated")
        return False
    await page.goto("https://www.tennis.de/mein-court", wait_until="networkidle", timeout=20000)
    await asyncio.sleep(2)
    if "login" not in page.url and "mein-court" in page.url:
        print("  Session still valid")
        return True
    await page.fill('input[name="_com_liferay_login_web_portlet_LoginPortlet_login"]', TENNIS_EMAIL)
    await page.fill('input[name="_com_liferay_login_web_portlet_LoginPortlet_password"]', TENNIS_PASS)
    await page.keyboard.press("Enter")
    await page.wait_for_load_state("networkidle")
    await asyncio.sleep(2)
    return "login" not in page.url


async def login(context):
    """Login using saved session if available, otherwise do full login and save session."""
    import json, os
    page = await context.new_page()
    try:
        # Check if saved session works
        if os.path.exists(SESSION_FILE):
            await page.goto("https://www.tennis.de/mein-court", wait_until="networkidle", timeout=20000)
            await asyncio.sleep(2)
            if "login" not in page.url:
                print("  Session restauree depuis fichier")
                return page
            print("  Session expiree, re-login...")

        # Full login
        ok = await do_login(page)
        if ok:
            await context.storage_state(path=SESSION_FILE)
            print("  Login OK (session sauvegardee)")
        else:
            print("  Login echoue")
        return page
    except Exception as e:
        print(f"  Login error: {e}")
        return page


# scrape_player is now inlined in main() to share the browser context


# -----------------------------------------------------------------------
# HTML email formatter
# -----------------------------------------------------------------------
def build_html(all_results: list, week_start: str, week_end: str) -> str:
    rows = ""
    for r in all_results:
        p       = r["player"]
        lk      = r["lk"]
        matches = r["matches"]

        wins   = sum(1 for m in matches if m["won"] is True)
        losses = sum(1 for m in matches if m["won"] is False)
        unkn   = sum(1 for m in matches if m["won"] is None)

        if matches:
            record = f"<strong>{wins}V - {losses}D</strong>"
            if unkn:
                record += f" + {unkn} ?"
            match_rows = ""
            for m in matches:
                if m["won"] is True:
                    icon, cls = "✅", "win"
                elif m["won"] is False:
                    icon, cls = "❌", "loss"
                else:
                    icon, cls = "❓", "unk"

                opp = m["opponent"]
                if m["is_double"] and m["opponent2"]:
                    opp += f" / {m['opponent2']}"

                lkc = f"&nbsp;<span style='color:#888;font-size:.85em'>{m['lk_change']}</span>" if m["lk_change"] else ""

                match_rows += f"""
            <tr class="{cls}">
              <td style="padding:4px 8px;font-size:.85em;color:#666">{m['date']}</td>
              <td style="padding:4px 8px">{icon} {opp}</td>
              <td style="padding:4px 8px;font-weight:bold">{m['score']}{lkc}</td>
              <td style="padding:4px 8px;font-size:.8em;color:#777">{m['tournament'][:50]}</td>
            </tr>"""
            body_section = f"""
          <p>{record} ({len(matches)} match(s))</p>
          <table style="width:100%;border-collapse:collapse;font-size:.95em">
            <tr style="background:#f0f0f0">
              <th style="padding:4px 8px;text-align:left">Date</th>
              <th style="padding:4px 8px;text-align:left">Adversaire</th>
              <th style="padding:4px 8px;text-align:left">Score</th>
              <th style="padding:4px 8px;text-align:left">Contexte</th>
            </tr>
            {match_rows}
          </table>"""
        else:
            body_section = '<p style="color:#999;font-style:italic">Aucun match cette semaine.</p>'

        rows += f"""
      <div style="margin-bottom:28px;padding-bottom:12px;border-bottom:1px solid #eee">
        <h2 style="margin:0 0 6px;color:#1a1a2e">
          {p['name']}
          <span style="display:inline-block;background:#2e7d32;color:#fff;
                       border-radius:50%;width:38px;height:38px;line-height:38px;
                       text-align:center;font-size:.9em;margin-left:8px">{lk}</span>
        </h2>
        <p style="margin:0 0 6px;font-size:.8em;color:#888">DTB {p['dtb_id']}</p>
        {body_section}
      </div>"""

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: Arial, sans-serif; max-width: 680px; margin: 0 auto; padding: 16px; color: #222; }}
  tr.win  td {{ background: #e8f5e9; }}
  tr.loss td {{ background: #fce4ec; }}
  tr.unk  td {{ background: #f5f5f5; }}
  table tr:hover td {{ filter: brightness(.97); }}
</style>
</head>
<body>
  <h1 style="color:#1a1a2e;border-bottom:3px solid #2e7d32;padding-bottom:8px">
    Tennis Results &#127934;
  </h1>
  <p style="color:#666">Semaine du <strong>{week_start}</strong> au <strong>{week_end}</strong></p>
  {rows}
  <p style="color:#bbb;font-size:.75em;margin-top:24px">
    Source&nbsp;: tennis.de &mdash; rapport automatique chaque dimanche soir
  </p>
</body>
</html>"""


# -----------------------------------------------------------------------
# Email sender
# -----------------------------------------------------------------------
def send_email(html: str, subject: str) -> bool:
    if not GMAIL_APP_PW:
        print("ERROR: TENNIS_GMAIL_APP_PASSWORD not set. Email not sent.")
        print("  -> Set it with: export TENNIS_GMAIL_APP_PASSWORD='xxxx xxxx xxxx xxxx'")
        # Save HTML to file for debugging
        out = "/tmp/tennis_report_debug.html"
        with open(out, "w") as f:
            f.write(html)
        print(f"  -> HTML saved to {out}")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = ", ".join(RECIPIENTS)
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SENDER_EMAIL, GMAIL_APP_PW)
            smtp.sendmail(SENDER_EMAIL, RECIPIENTS, msg.as_string())
        print(f"Email envoye a: {', '.join(RECIPIENTS)}")
        return True
    except Exception as e:
        print(f"Erreur envoi email: {e}")
        return False


# -----------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------
async def main():
    today    = datetime.now()
    cutoff   = today - timedelta(days=DAYS_BACK)
    week_str = cutoff.strftime("%d.%m.%Y")
    today_str = today.strftime("%d.%m.%Y")

    print(f"\nTennis Weekly Report")
    print(f"Periode: {week_str} -> {today_str}")
    print(f"Joueurs: {len(PLAYERS)}\n")

    all_results = []

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            import os, json
            storage = SESSION_FILE if os.path.exists(SESSION_FILE) else None
            context = await browser.new_context(storage_state=storage)
            login_page = await login(context)
            await login_page.close()

            for player in PLAYERS:
                # Reuse the logged-in context for each player
                page = await context.new_page()
                try:
                    url = BASE_URL.format(nu_id=player["nu_id"])
                    print(f"  -> {player['name']}  ({url})")
                    await page.goto(url, wait_until="networkidle", timeout=45000)
                    await asyncio.sleep(5)

                    # Get LK
                    lk = "?"
                    try:
                        raw = await page.evaluate("document.body.innerText")
                        m = re.search(r"Leistungsklasse\s*\n\s*(\d+[,\.]\d+)", raw)
                        if m:
                            lk = m.group(1).replace(",", ".")
                    except Exception as e:
                        print(f"    LK error: {e}")

                    try:
                        raw_text = await page.evaluate("document.body.innerText")
                    except Exception:
                        raw_text = ""

                    matches = parse_matches(raw_text, player["name"], cutoff)
                    print(f"    LK={lk}  matches={len(matches)}")
                    all_results.append({"player": player, "lk": lk, "matches": matches})
                except Exception as e:
                    print(f"    ERROR {player['name']}: {e}")
                    all_results.append({"player": player, "lk": "?", "matches": []})
                finally:
                    await page.close()

            await context.close()
        finally:
            await browser.close()

    html    = build_html(all_results, week_str, today_str)
    subject = f"Tennis Results - {cutoff.strftime('%d/%m')} au {today.strftime('%d/%m/%Y')}"

    send_email(html, subject)
    print("\nFait.")


if __name__ == "__main__":
    asyncio.run(main())
