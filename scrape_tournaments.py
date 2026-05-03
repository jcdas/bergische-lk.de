#!/usr/bin/env python3
"""
Scraper for tennis.de Turniersuche — M16 DTB Ranglisten-Turniere
for TVN, TVM, WTV from today until 30.09.2026.

Strategy: search ALL M16 Ranglisten-Turniere, then filter by VerbandName.
"""

import csv
import asyncio
import os
import sys
from datetime import date
from playwright.async_api import async_playwright, Page, TimeoutError as PwTimeout

URL = "https://www.tennis.de/spielen/spielbetrieb/turniersuche.html"
TARGET_VERBAENDE = {
    "Tennis-Verband Niederrhein": "TVN",
    "Tennisverband Mittelrhein": "TVM",
    "Westfälischer Tennis-Verband": "WTV",
}
DATE_FROM = date.today().strftime("%d.%m.%Y")
DATE_TO = "30.09.2026"
OUTPUT = "tournaments_u16.csv"


async def wait_zk(page: Page, ms: int = 800):
    await page.wait_for_timeout(ms)
    try:
        await page.wait_for_function(
            "() => !document.querySelector('.z-loading')", timeout=5000
        )
    except PwTimeout:
        pass
    await page.wait_for_timeout(300)


async def dismiss_cookies(page: Page):
    btn = page.locator("#CybotCookiebotDialogBodyButtonDecline")
    if await btn.count() > 0:
        try:
            await btn.click(timeout=3000)
            await page.wait_for_timeout(1000)
        except PwTimeout:
            pass


async def set_date_range(page: Page):
    val = f"{DATE_FROM} - {DATE_TO}"
    print(f"  Date range: {val}")
    await page.evaluate(f"""
        (() => {{
            var embed = document.getElementById('embed-turniersuche');
            var inputs = embed.querySelectorAll('input.z-textbox-readonly');
            for (var el of inputs) {{
                var w = zk.Widget.$(el);
                if (w && w.getValue && w.getValue().includes('.')) {{
                    w.setValue('{val}');
                    zAu.send(new zk.Event(w, 'onChange', {{value: '{val}'}}));
                    return;
                }}
            }}
        }})()
    """)
    await wait_zk(page)


async def select_age_m16(page: Page):
    print("  Age: M16")
    await page.evaluate("""
        (() => {
            var embed = document.getElementById('embed-turniersuche');
            var bbs = embed.querySelectorAll('.z-bandbox');
            for (var bb of bbs) {
                var input = bb.querySelector('input');
                if (input && input.value && input.value.includes('Altersklassen')) {
                    var btn = bb.querySelector('.z-bandbox-button');
                    if (btn) btn.click();
                    return;
                }
            }
        })()
    """)
    await page.wait_for_timeout(1000)

    await page.evaluate("""
        (() => {
            var popups = document.querySelectorAll('.z-bandpopup');
            for (var p of popups) {
                if (p.offsetParent === null) continue;
                var items = p.querySelectorAll('.z-listitem');
                for (var item of items) {
                    if (item.textContent.trim() === 'M16') { item.click(); return; }
                }
            }
        })()
    """)
    await page.wait_for_timeout(300)
    await page.keyboard.press("Escape")
    await wait_zk(page)


async def select_ranglistenturnier(page: Page):
    """Open advanced filters and select DTB Ranglisten-Turniere."""
    # Open advanced filters
    await page.evaluate("""
        (() => {
            var embed = document.getElementById('embed-turniersuche');
            var btns = embed.querySelectorAll('button.z-button');
            for (var btn of btns) {
                if (btn.textContent.includes('weitere Filter')) {
                    var w = zk.Widget.$(btn);
                    if (w) w.fire('onClick');
                    return;
                }
            }
        })()
    """)
    await wait_zk(page, 1500)

    print("  Type: DTB Ranglisten-Turniere")
    await page.evaluate("""
        (() => {
            var embed = document.getElementById('embed-turniersuche');
            var selects = embed.querySelectorAll('select.z-select');
            for (var sel of selects) {
                for (var opt of sel.options) {
                    if (opt.text.includes('DTB Ranglisten')) {
                        var w = zk.Widget.$(sel);
                        if (w) {
                            w.setSelectedIndex(opt.index);
                            zAu.send(new zk.Event(w, 'onSelect', {value: opt.value}));
                            zAu.send(new zk.Event(w, 'onChange', {value: opt.value}));
                        }
                        return;
                    }
                }
            }
        })()
    """)
    await wait_zk(page)


async def do_search(page: Page):
    print("  Searching...")
    await page.evaluate("""
        (() => {
            var embed = document.getElementById('embed-turniersuche');
            var btns = embed.querySelectorAll('button.z-button');
            for (var btn of btns) {
                if (btn.textContent.trim().startsWith('Suchen')) {
                    var w = zk.Widget.$(btn);
                    if (w) w.fire('onClick');
                    return;
                }
            }
        })()
    """)
    await wait_zk(page, 4000)


async def load_all_results(page: Page) -> int:
    """Click 'Mehr Turniere' until all results are loaded."""
    total_loaded = 0
    for attempt in range(200):
        row_count = await page.evaluate("""
            () => {
                var embed = document.getElementById('embed-turniersuche');
                var grid = embed.querySelector('.bottomgrid.z-grid .z-grid-body');
                return grid ? grid.querySelectorAll('tr.z-row').length : 0;
            }
        """)

        has_more = await page.evaluate("""
            () => {
                var embed = document.getElementById('embed-turniersuche');
                var btns = embed.querySelectorAll('button.z-button');
                for (var btn of btns) {
                    if (btn.textContent.includes('Mehr Turniere')) {
                        var w = zk.Widget.$(btn);
                        if (w) { w.fire('onClick'); return true; }
                    }
                }
                return false;
            }
        """)
        if not has_more:
            break
        total_loaded += 1
        await wait_zk(page, 1500)

        # Check if rows actually increased
        new_count = await page.evaluate("""
            () => {
                var embed = document.getElementById('embed-turniersuche');
                var grid = embed.querySelector('.bottomgrid.z-grid .z-grid-body');
                return grid ? grid.querySelectorAll('tr.z-row').length : 0;
            }
        """)
        if new_count <= row_count:
            break

        if total_loaded % 10 == 0:
            print(f"    ... {new_count} rows loaded")

    final = await page.evaluate("""
        () => {
            var embed = document.getElementById('embed-turniersuche');
            var grid = embed.querySelector('.bottomgrid.z-grid .z-grid-body');
            return grid ? grid.querySelectorAll('tr.z-row').length : 0;
        }
    """)
    print(f"  Loaded all: {final} rows ({total_loaded} pages)")
    return final


async def extract_results(page: Page) -> list[dict]:
    """Extract ALL tournament data from grid."""
    total = await load_all_results(page)

    tournaments = await page.evaluate("""
        () => {
            var embed = document.getElementById('embed-turniersuche');
            if (!embed) return [];

            var grid = embed.querySelector('.bottomgrid.z-grid .z-grid-body');
            if (!grid) return [];

            // Use broader selector and also check for rows in nested tables
            var rows = grid.querySelectorAll('.z-row');
            var results = [];
            var debugInfo = 'rows=' + rows.length;

            rows.forEach(row => {
                var name = '';
                var tbs = row.querySelectorAll('.z-toolbarbutton-content');
                for (var tb of tbs) {
                    var t = tb.textContent.trim();
                    if (t && t !== 'Favorit' && t.length > 3) { name = t; break; }
                }

                var labels = row.querySelectorAll('.z-label');
                var dateRange = '', location = '', verbandName = '', meldeschluss = '', ageClasses = '';
                var prevWasAge = false;

                labels.forEach(l => {
                    var t = l.textContent.trim();
                    if (!t || t === '-' || t === 'Favorit') return;

                    if (t.match(/^\\d{2}\\.\\d{2}\\./)) {
                        dateRange = t;
                    } else if (t.startsWith('Meldeschluss:')) {
                        meldeschluss = t.replace('Meldeschluss: ', '');
                    } else if (t === 'Altersklassen') {
                        prevWasAge = true;
                    } else if (prevWasAge) {
                        ageClasses = t;
                        prevWasAge = false;
                    } else if (t.includes('Verband') || t.includes('Bund')) {
                        verbandName = t;
                    } else if (!location && t.length > 2 && t.length < 80 &&
                               !t.match(/^[MWX]\\d/) && !t.includes('Turnier') &&
                               !t.match(/^\\d+$/)) {
                        location = t;
                    }
                });

                if (name || dateRange) {
                    results.push({
                        Name: name,
                        Date: dateRange,
                        Location: location,
                        VerbandName: verbandName,
                        Meldeschluss: meldeschluss,
                        AgeClasses: ageClasses,
                    });
                }
            });

            return results;
        }
    """)

    print(f"  Extracted: {len(tournaments)} tournaments")
    return tournaments


def classify_verband(tournament: dict) -> str:
    """Map tournament to TVN/TVM/WTV based on VerbandName, Name, or Location."""
    vname = tournament.get("VerbandName", "")
    name = tournament.get("Name", "")
    location = tournament.get("Location", "")

    # Direct VerbandName match
    for full, code in TARGET_VERBAENDE.items():
        if full.lower() in vname.lower():
            return code

    # Check for TVM in tournament name
    if "TVM" in name:
        return "TVM"

    # Check for TVM-area cities (Mittelrhein region)
    tvm_cities = [
        "Köln", "Bonn", "Aachen", "Koblenz", "Leverkusen", "Düren",
        "Troisdorf", "Siegburg", "Sankt Augustin", "St. Augustin",
        "Erftstadt", "Euskirchen", "Bergheim", "Brühl", "Frechen",
        "Kerpen", "Pulheim", "Bornheim", "Meckenheim", "Rheinbach",
        "Bad Neuenahr", "Andernach", "Mayen", "Neuwied", "Montabaur",
    ]
    for city in tvm_cities:
        if city.lower() in location.lower():
            return "TVM"

    return ""


def export_csv(tournaments: list[dict], filename: str):
    fields = ["Name", "Date", "Location", "Verband", "VerbandName",
              "Meldeschluss", "AgeClasses"]
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(tournaments)
    print(f"\nExported {len(tournaments)} tournaments to {filename}")


def get_biweekly_ranges():
    """Generate 2-week date ranges from today to 30.09.2026."""
    from datetime import timedelta
    today = date.today()
    ranges = []
    current = today
    end_limit = date(2026, 9, 30)

    while current <= end_limit:
        range_end = min(current + timedelta(days=13), end_limit)
        ranges.append((
            current.strftime("%d.%m.%Y"),
            range_end.strftime("%d.%m.%Y"),
        ))
        current = range_end + timedelta(days=1)

    return ranges


async def reset_filters(page: Page):
    """Reset all filters."""
    await page.evaluate("""
        (() => {
            var embed = document.getElementById('embed-turniersuche');
            var tbs = embed.querySelectorAll('.z-toolbarbutton');
            for (var tb of tbs) {
                if (tb.textContent.includes('zurücksetzen')) {
                    var w = zk.Widget.$(tb);
                    if (w) w.fire('onClick');
                    return;
                }
            }
        })()
    """)
    await wait_zk(page, 2000)


async def main():
    monthly_ranges = get_biweekly_ranges()

    print(f"Tennis.de M16 DTB Ranglisten-Turniere Scraper")
    print(f"Date range: {DATE_FROM} - {DATE_TO} ({len(monthly_ranges)} biweekly batches)")
    print(f"Target: TVN, TVM, WTV\n")

    all_tournaments = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            locale="de-DE",
        )
        page = await context.new_page()

        print(f"Opening {URL}...")
        await page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(8000)
        await dismiss_cookies(page)

        try:
            await page.wait_for_function(
                "() => document.querySelector('#embed-turniersuche .z-button')",
                timeout=15000,
            )
            print("Widget loaded.\n")
        except PwTimeout:
            print("WARNING: Widget may not be loaded")

        for i, (d_from, d_to) in enumerate(monthly_ranges):
            print(f"\n--- Batch {i+1}/{len(monthly_ranges)}: {d_from} - {d_to} ---")

            if i > 0:
                await reset_filters(page)
                await page.wait_for_timeout(1000)

            # Set date range for this month
            await page.evaluate(f"""
                (() => {{
                    var embed = document.getElementById('embed-turniersuche');
                    var inputs = embed.querySelectorAll('input.z-textbox-readonly');
                    for (var el of inputs) {{
                        var w = zk.Widget.$(el);
                        if (w && w.getValue && w.getValue().includes('.')) {{
                            w.setValue('{d_from} - {d_to}');
                            zAu.send(new zk.Event(w, 'onChange', {{value: '{d_from} - {d_to}'}}));
                            return;
                        }}
                    }}
                }})()
            """)
            await wait_zk(page)

            await select_age_m16(page)
            await select_ranglistenturnier(page)
            await do_search(page)

            batch = await extract_results(page)
            all_tournaments.extend(batch)

        await page.screenshot(path="debug_final.png")
        await browser.close()

    # Post-process: filter by VerbandName (TVN/TVM/WTV)
    filtered = []
    for t in all_tournaments:
        code = classify_verband(t)
        if code:
            t["Verband"] = code
            filtered.append(t)

    # Also keep unclassified ones for review
    unclassified = [t for t in all_tournaments if not classify_verband(t)]

    # Deduplicate
    seen = set()
    unique = []
    for t in filtered:
        key = (t["Name"], t["Date"])
        if key not in seen:
            seen.add(key)
            unique.append(t)

    export_csv(unique, OUTPUT)

    # Also export all for reference
    for t in all_tournaments:
        t["Verband"] = classify_verband(t)
    with open("tournaments_u16_all.csv", "w", newline="", encoding="utf-8") as f:
        fields = ["Name", "Date", "Location", "Verband", "VerbandName",
                  "Meldeschluss", "AgeClasses"]
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_tournaments)

    print(f"\nSummary:")
    print(f"  Total found: {len(all_tournaments)}")
    for code in ["TVN", "TVM", "WTV"]:
        count = sum(1 for t in unique if t["Verband"] == code)
        print(f"  {code}: {count}")
    print(f"  Filtered (TVN+TVM+WTV): {len(unique)}")
    print(f"  Other Verbände: {len(unclassified)}")
    print(f"\n  tournaments_u16.csv — TVN/TVM/WTV only")
    print(f"  tournaments_u16_all.csv — all tournaments")


if __name__ == "__main__":
    asyncio.run(main())
