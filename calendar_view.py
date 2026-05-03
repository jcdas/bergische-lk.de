#!/usr/bin/env python3
"""
Generate a calendar HTML view of M16 Ranglisten-Turniere
within 70km of Haan (42781), from May 2026, grouped by month.
"""

import csv
import math
import re
from datetime import date, timedelta
from collections import defaultdict

# Haan coordinates
HAAN_LAT, HAAN_LON = 51.19, 7.01
MAX_DIST = 70  # km

# Known city coordinates (approximate)
CITY_COORDS = {
    "solingen": (51.17, 7.08),
    "hilden": (51.17, 6.93),
    "wuppertal": (51.26, 7.17),
    "remscheid": (51.18, 7.19),
    "leverkusen": (51.05, 7.00),
    "dormagen": (51.10, 6.83),
    "ratingen": (51.30, 6.85),
    "düsseldorf": (51.23, 6.78),
    "meerbusch": (51.26, 6.69),
    "neuss": (51.20, 6.69),
    "mönchengladbach": (51.19, 6.44),
    "pulheim": (50.99, 6.81),
    "pulheim-brauweiler": (50.99, 6.81),
    "mülheim an der ruhr": (51.43, 6.88),
    "mülheim": (51.43, 6.88),
    "köln": (50.94, 6.96),
    "overath": (50.93, 7.28),
    "sprockhövel": (51.35, 7.24),
    "bocholt": (51.84, 6.62),
    "bochum": (51.48, 7.22),
    "essen": (51.46, 7.01),
    "oberhausen": (51.47, 6.85),
    "duisburg": (51.43, 6.76),
    "dortmund": (51.51, 7.47),
    "moers": (51.45, 6.63),
    "dinslaken": (51.57, 6.73),
    "recklinghausen": (51.61, 7.20),
    "schwerte": (51.44, 7.57),
    "st. augustin": (50.77, 7.19),
    "troisdorf": (50.82, 7.16),
    "erftstadt": (50.81, 6.77),
    "erftstadt-bliesheim": (50.81, 6.77),
    "bonn": (50.73, 7.10),
    "brühl": (50.83, 6.91),
    "meckenheim": (50.63, 7.03),
    "bergheim": (50.96, 6.64),
    "bad driburg": (51.73, 9.02),
    "gütersloh": (51.91, 8.38),
    "bad salzuflen": (52.09, 8.75),
    "mannheim": (49.49, 8.47),
    "frankfurt": (50.11, 8.68),
    "hamburg": (53.55, 10.00),
    "nürnberg": (49.45, 11.08),
    "münchen": (48.14, 11.58),
    "herten": (51.60, 7.14),
    "schermbeck": (51.69, 6.87),
    "waltrop": (51.62, 7.40),
    "bergkamen": (51.63, 7.63),
    "geldern": (51.52, 6.32),
    "krefeld": (51.33, 6.56),
    "viersen": (51.25, 6.39),
    "langenfeld": (51.11, 6.95),
    "velbert": (51.34, 7.04),
    "haan": (51.19, 7.01),
}


def calc_distance(lat, lon):
    """Approximate distance in km from Haan."""
    dlat = (lat - HAAN_LAT) * 111
    dlon = (lon - HAAN_LON) * 65
    return math.sqrt(dlat**2 + dlon**2)


def get_distance(location: str) -> float:
    """Get distance from Haan to a tournament location."""
    loc_lower = location.lower().strip()
    # Direct match
    if loc_lower in CITY_COORDS:
        return calc_distance(*CITY_COORDS[loc_lower])
    # Partial match
    for city, coords in CITY_COORDS.items():
        if city in loc_lower or loc_lower in city:
            return calc_distance(*coords)
    # Try first word
    first_word = loc_lower.split(",")[0].split("/")[0].strip()
    if first_word in CITY_COORDS:
        return calc_distance(*CITY_COORDS[first_word])
    return 999  # Unknown


def parse_date_range(date_str: str):
    """Parse '10.04. - 12.04.2026' or '10.04.2026' into (start_date, end_date)."""
    date_str = date_str.strip()
    if not date_str:
        return None, None

    parts = re.split(r'\s*[-–]\s*', date_str)
    try:
        if len(parts) == 2:
            end = parts[1].strip()
            end_match = re.match(r'(\d{1,2})\.(\d{1,2})\.(\d{4})', end)
            if not end_match:
                return None, None
            year = int(end_match.group(3))
            end_date = date(year, int(end_match.group(2)), int(end_match.group(1)))

            start = parts[0].strip()
            start_match = re.match(r'(\d{1,2})\.(\d{1,2})\.?(\d{4})?', start)
            if not start_match:
                return None, None
            s_year = int(start_match.group(3)) if start_match.group(3) else year
            start_date = date(s_year, int(start_match.group(2)), int(start_match.group(1)))
            return start_date, end_date
        else:
            m = re.match(r'(\d{1,2})\.(\d{1,2})\.(\d{4})', parts[0])
            if m:
                d = date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
                return d, d
    except (ValueError, IndexError):
        pass
    return None, None


def is_weekend(d: date) -> bool:
    return d.weekday() >= 5  # Saturday=5, Sunday=6


def get_weekend_days(start: date, end: date) -> list:
    """Get all weekend days in a date range."""
    days = []
    current = start
    while current <= end:
        if is_weekend(current):
            days.append(current)
        current += timedelta(days=1)
    return days


def tournament_type(age_classes: str) -> str:
    """Classify: 'rangliste' (J-x) or 'lk' (M16 etc.) or 'other'."""
    ac = age_classes.strip()
    if ac.startswith("J-"):
        return "rangliste"
    if "M16" in ac:
        return "lk"
    return "other"


def main():
    # Read ALL tournaments (not just TVN/TVM/WTV filtered)
    with open("tournaments_u16_all.csv") as f:
        tournaments = list(csv.DictReader(f))

    # Filter: distance < 70km, from May 2026, NOT restricted
    may_start = date(2026, 5, 1)
    filtered = []

    for t in tournaments:
        ttype = tournament_type(t.get("AgeClasses", ""))
        if ttype == "other":
            continue

        # Exclude restricted (Bezirk/Kreis/Club) for LK tournaments
        if ttype == "lk":
            name_lower = t.get("Name", "").lower()
            restricted = any(kw in name_lower for kw in [
                "clubmeisterschaft", "vereinsmeisterschaft",
            ])
            if restricted:
                continue

        t["_type"] = ttype
        loc = t.get("Location", "")
        dist = get_distance(loc)
        if dist > MAX_DIST:
            continue

        start, end = parse_date_range(t.get("Date", ""))
        if not start or not end:
            continue
        if end < may_start:
            continue

        # Adjust start if before May
        if start < may_start:
            start = may_start

        t["_dist"] = round(dist)
        t["_start"] = start
        t["_end"] = end
        t["_weekends"] = get_weekend_days(start, end)
        filtered.append(t)

    filtered.sort(key=lambda t: t["_start"])

    # Group by month
    months = defaultdict(list)
    for t in filtered:
        month_key = t["_start"].strftime("%Y-%m")
        months[month_key].append(t)

    # Generate HTML calendar
    html = generate_html(filtered, months)
    with open("tournaments_calendar.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Generated tournaments_calendar.html ({len(filtered)} tournaments)")

    # Print summary
    rangliste = [t for t in filtered if t.get("_type") == "rangliste"]
    lk = [t for t in filtered if t.get("_type") == "lk"]
    print(f"  Rangliste: {len(rangliste)}, LK: {len(lk)}")

    for mk in sorted(months):
        m = months[mk]
        month_name = date(int(mk[:4]), int(mk[5:7]), 1).strftime("%B %Y")
        r_count = sum(1 for t in m if t.get("_type") == "rangliste")
        l_count = sum(1 for t in m if t.get("_type") == "lk")
        print(f"\n{month_name}: {r_count} Rangliste + {l_count} LK")
        for t in sorted(m, key=lambda x: (x.get("_type") != "rangliste", x["_start"])):
            we = "WE" if t["_weekends"] else "  "
            tag = "RL" if t.get("_type") == "rangliste" else "LK"
            print(f"  {we} [{tag}] {t['Date']:25s} {t['_dist']:3d}km  {t['Location']:20s} {t['Name'][:45]}")


def generate_html(filtered, months):
    import calendar

    month_names_de = {
        5: "Mai", 6: "Juni", 7: "Juli", 8: "August", 9: "September"
    }

    html = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<title>M16 Ranglisten-Turniere — Mai–Sept 2026 — &lt;70km ab Haan</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Segoe UI', sans-serif; background: #f5f5f0; color: #1a1a1a; padding: 20px; }
  h1 { font-size: 1.6em; margin-bottom: 5px; color: #1C3A0E; }
  .subtitle { color: #666; margin-bottom: 25px; font-size: 0.95em; }
  .month-section { margin-bottom: 35px; }
  .month-title { font-size: 1.3em; font-weight: 700; color: #2D5A18; margin-bottom: 12px;
    border-bottom: 3px solid #B85A20; padding-bottom: 5px; display: inline-block; }
  .calendar { display: grid; grid-template-columns: repeat(7, 1fr); gap: 2px; margin-bottom: 15px; }
  .cal-header { text-align: center; font-weight: 700; font-size: 0.8em; padding: 6px 2px;
    background: #2D5A18; color: white; border-radius: 4px 4px 0 0; }
  .cal-day { min-height: 60px; padding: 4px; font-size: 0.75em; background: white;
    border: 1px solid #e0e0e0; position: relative; }
  .cal-day.empty { background: #f0f0f0; border-color: #eee; }
  .cal-day.weekend { background: #FFF8E7; }
  .cal-day.has-tournament { background: #E8F5E9; border-color: #4CAF50; }
  .cal-day.weekend.has-tournament { background: #FFF3E0; border-color: #B85A20; border-width: 2px; }
  .day-num { font-weight: 700; font-size: 1.1em; color: #333; }
  .day-num.weekend { color: #B85A20; }
  .tournament-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%;
    margin: 1px; cursor: pointer; }
  .tournament-dot.tvn { background: #2D5A18; }
  .tournament-dot.tvm { background: #B85A20; }
  .tournament-dot.wtv { background: #1565C0; }
  .tournament-list { margin-top: 8px; }
  .tournament-card { background: white; border-radius: 8px; padding: 10px 14px; margin-bottom: 8px;
    border-left: 4px solid #ccc; box-shadow: 0 1px 3px rgba(0,0,0,0.08); display: flex; gap: 12px; align-items: flex-start; }
  .tournament-card.rangliste { border-left-color: #B85A20; background: #FFF8F0; }
  .tournament-card.lk { border-left-color: #888; }
  .tournament-card .date { font-weight: 700; min-width: 150px; font-size: 0.9em; }
  .tournament-card .date .we-badge { display: inline-block; background: #B85A20; color: white;
    font-size: 0.7em; padding: 1px 5px; border-radius: 3px; margin-left: 4px; font-weight: 400; }
  .tournament-card .date .type-badge { display: inline-block; color: white;
    font-size: 0.7em; padding: 1px 5px; border-radius: 3px; margin-left: 4px; font-weight: 700; }
  .tournament-card .date .type-badge.rl { background: #B85A20; }
  .tournament-card .date .type-badge.lk { background: #888; }
  .tournament-card .info { flex: 1; }
  .tournament-card .name { font-weight: 600; font-size: 0.95em; }
  .tournament-card .location { color: #666; font-size: 0.85em; }
  .tournament-card .dist { min-width: 50px; text-align: right; color: #888; font-size: 0.85em; }
  .legend { display: flex; gap: 20px; margin-bottom: 20px; font-size: 0.85em; align-items: center; }
  .legend-item { display: flex; align-items: center; gap: 5px; }
  .legend-dot { width: 12px; height: 12px; border-radius: 50%; }
  .stats { display: flex; gap: 30px; margin-bottom: 20px; }
  .stat { text-align: center; }
  .stat .num { font-size: 2em; font-weight: 700; color: #2D5A18; }
  .stat .label { font-size: 0.8em; color: #666; }
</style>
</head>
<body>
<h1>🎾 M16 Turniere — Rangliste + LK</h1>
<p class="subtitle">Mai – September 2026 · Radius 70km ab Haan (42781)</p>
"""

    # Stats
    total = len(filtered)
    rl_count = sum(1 for t in filtered if t.get("_type") == "rangliste")
    lk_count = sum(1 for t in filtered if t.get("_type") == "lk")
    we_count = sum(1 for t in filtered if t["_weekends"])
    tvn_count = sum(1 for t in filtered if t.get("Verband") == "TVN")
    tvm_count = sum(1 for t in filtered if t.get("Verband") == "TVM")
    wtv_count = sum(1 for t in filtered if t.get("Verband") == "WTV")

    html += f"""
<div class="stats">
  <div class="stat"><div class="num">{total}</div><div class="label">Tournois</div></div>
  <div class="stat"><div class="num" style="color:#B85A20">{rl_count}</div><div class="label">Rangliste</div></div>
  <div class="stat"><div class="num" style="color:#888">{lk_count}</div><div class="label">LK</div></div>
  <div class="stat"><div class="num">{we_count}</div><div class="label">Weekend</div></div>
</div>
<div class="legend">
  <div class="legend-item"><div class="legend-dot" style="background:#B85A20"></div> Rangliste (J-1 à J-5)</div>
  <div class="legend-item"><div class="legend-dot" style="background:#888"></div> LK-Turnier</div>
  <div class="legend-item"><div style="width:20px;height:12px;background:#FFF3E0;border:2px solid #B85A20;border-radius:2px"></div> Weekend + Tournoi</div>
</div>
"""

    # For each month May-September
    for month in range(5, 10):
        mk = f"2026-{month:02d}"
        month_tournaments = months.get(mk, [])
        month_name = month_names_de.get(month, "")

        # Build set of days with tournaments
        day_tournaments = defaultdict(list)
        for t in month_tournaments:
            current = max(t["_start"], date(2026, month, 1))
            end = min(t["_end"], date(2026, month, calendar.monthrange(2026, month)[1]))
            while current <= end:
                day_tournaments[current.day].append(t)
                current += timedelta(days=1)

        html += f'<div class="month-section">\n'
        html += f'<div class="month-title">{month_name} 2026</div>\n'

        # Calendar grid
        html += '<div class="calendar">\n'
        for day_name in ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]:
            html += f'<div class="cal-header">{day_name}</div>\n'

        first_weekday = date(2026, month, 1).weekday()  # 0=Monday
        days_in_month = calendar.monthrange(2026, month)[1]

        # Empty cells before first day
        for _ in range(first_weekday):
            html += '<div class="cal-day empty"></div>\n'

        for day in range(1, days_in_month + 1):
            d = date(2026, month, day)
            classes = ["cal-day"]
            if d.weekday() >= 5:
                classes.append("weekend")
            if day in day_tournaments:
                classes.append("has-tournament")

            html += f'<div class="{" ".join(classes)}">'
            day_cls = "day-num weekend" if d.weekday() >= 5 else "day-num"
            html += f'<div class="{day_cls}">{day}</div>'

            if day in day_tournaments:
                for t in day_tournaments[day]:
                    ttype = t.get("_type", "lk")
                    dot_color = "#B85A20" if ttype == "rangliste" else "#888"
                    html += f'<span class="tournament-dot" style="background:{dot_color}" title="{t["Name"][:40]} ({t["Location"]})"></span>'

            html += '</div>\n'

        # Fill remaining cells
        last_weekday = date(2026, month, days_in_month).weekday()
        for _ in range(6 - last_weekday):
            html += '<div class="cal-day empty"></div>\n'

        html += '</div>\n'

        # Tournament list for this month
        if month_tournaments:
            html += '<div class="tournament-list">\n'
            # Sort: Rangliste first, then by date
            for t in sorted(month_tournaments, key=lambda x: (x.get("_type") != "rangliste", x["_start"])):
                ttype = t.get("_type", "lk")
                has_we = bool(t["_weekends"])
                we_badge = '<span class="we-badge">WE</span>' if has_we else ''
                type_cls = "rl" if ttype == "rangliste" else "lk"
                type_label = t.get("AgeClasses", "").split(",")[0].strip() if ttype == "rangliste" else "LK"
                type_badge = f'<span class="type-badge {type_cls}">{type_label}</span>'
                # Search link on tennis.de
                import urllib.parse
                search_q = urllib.parse.quote(t["Name"][:50])
                link = f'https://www.tennis.de/spielen/spielbetrieb/turniersuche.html?q={search_q}'
                html += f"""<div class="tournament-card {ttype}">
  <div class="date">{t['Date']}{we_badge}{type_badge}</div>
  <div class="info">
    <div class="name"><a href="{link}" target="_blank" style="color:inherit;text-decoration:none;border-bottom:1px dashed #999">{t['Name']}</a></div>
    <div class="location">📍 {t['Location']} · {t.get('AgeClasses', '')[:50]}</div>
  </div>
  <div class="dist">{t['_dist']}km</div>
</div>\n"""
            html += '</div>\n'
        else:
            html += '<p style="color:#999;font-style:italic;margin:10px 0">Aucun tournoi ce mois</p>\n'

        html += '</div>\n'

    html += """
</body>
</html>"""
    return html


if __name__ == "__main__":
    main()
