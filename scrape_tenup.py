#!/usr/bin/env python3
"""Scraper TenUp — Normandie, 1-11 July 2026, 15-18 ans. All native clicks."""
import asyncio, csv
from playwright.async_api import async_playwright, TimeoutError as PwTimeout

URL = "https://tenup.fft.fr/recherche/tournois"
OUTPUT = "tournaments_tenup.csv"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await (await browser.new_context(viewport={"width":1280,"height":900}, locale="fr-FR")).new_page()

        print("1. Opening TenUp...")
        await page.goto(URL, wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(3000)
        if "queue-it" in page.url:
            try: await page.wait_for_url("**/tenup.fft.fr/**", timeout=60000)
            except PwTimeout: print("Stuck in queue"); return

        # Dismiss cookies — look for the cookie banner
        print("2. Cookies...")
        try:
            # Didomi cookie consent
            cookie_btn = page.locator("button:has-text('Continuer sans accepter'), button:has-text('Refuser'), button:has-text('Tout refuser'), #didomi-notice-disagree-button").first
            await cookie_btn.click(timeout=5000)
            await page.wait_for_timeout(1000)
            print("   Dismissed")
        except PwTimeout:
            print("   No cookie banner found")

        await page.screenshot(path="debug_tenup_step2.png")

        # 3. Click "Ligue" tab
        print("3. Click Ligue tab...")
        ligue_tab = page.locator("label:has-text('Ligue')").first
        await ligue_tab.click()
        await page.wait_for_timeout(2000)
        await page.screenshot(path="debug_tenup_step3.png")

        # 4. Click the ligue selector button
        print("4. Open ligue selector...")
        ligue_btn = page.locator("text=Dans quelle ligue").first
        if await ligue_btn.count() > 0:
            await ligue_btn.click(force=True)
            await page.wait_for_timeout(2000)
        await page.screenshot(path="debug_tenup_step4.png")

        # 5. Find and click NORMANDIE
        print("5. Select NORMANDIE...")
        normandie = page.locator("label:has-text('NORMANDIE')").first
        if await normandie.count() > 0:
            await normandie.click()
            await page.wait_for_timeout(500)
            print("   Clicked NORMANDIE label")
        else:
            # Try JS
            await page.evaluate("""() => {
                var labels = document.querySelectorAll('label');
                for (var l of labels) { if (l.textContent.trim() === 'NORMANDIE') { l.click(); return; } }
            }""")
            print("   Clicked via JS")

        await page.wait_for_timeout(1000)

        # Click Valider if visible
        valider = page.locator("button:has-text('Valider'), .btn-primary:has-text('Valider')").first
        if await valider.count() > 0 and await valider.is_visible():
            await valider.click()
            await page.wait_for_timeout(1000)
            print("   Validated")

        await page.screenshot(path="debug_tenup_step5.png")

        # 6. Scroll down to find more filters
        print("6. Looking for date/age filters...")
        await page.evaluate("window.scrollBy(0, 300)")
        await page.wait_for_timeout(500)

        # Set dates via JS (the date inputs might be hidden but functional)
        await page.evaluate("""() => {
            var start = document.getElementById('date-range-custom-input-start');
            var end = document.getElementById('date-range-custom-input-end');
            if (start) start.value = '01/07/26';
            if (end) end.value = '11/07/26';
        }""")

        # Check age categories
        await page.evaluate("""() => {
            ['edit-categorie-age-160', 'edit-categorie-age-180'].forEach(id => {
                var cb = document.getElementById(id);
                if (cb && !cb.checked) cb.checked = true;
            });
            var sm = document.getElementById('edit-epreuve-sm');
            if (sm && !sm.checked) sm.checked = true;
        }""")
        await page.wait_for_timeout(500)

        # 7. Click RECHERCHER
        print("7. Rechercher...")
        # Force enable and click Rechercher
        await page.evaluate("""() => {
            var btn = document.getElementById('edit-submit');
            if (btn) {
                btn.disabled = false;
                btn.removeAttribute('disabled');
                btn.click();
            }
        }""")
        print("   Forced click Rechercher")

        # Wait for AJAX results
        await page.wait_for_timeout(10000)
        print(f"   URL: {page.url}")
        await page.screenshot(path="debug_tenup_results.png")

        # 8. Extract results
        print("\n8. Extracting...")
        results = await page.evaluate("""
            () => {
                var items = [];
                // Find all tournament links
                document.querySelectorAll('a[href*="/tournoi/"]').forEach(a => {
                    var parent = a.closest('tr, .views-row, article, li, .card, div.row') || a.parentElement;
                    items.push({
                        name: a.textContent.trim(),
                        link: a.href,
                        context: parent ? parent.textContent.trim().replace(/\\s+/g, ' ').substring(0, 300) : ''
                    });
                });
                // Also check for table rows with tournament data
                document.querySelectorAll('table tr, .views-table tr').forEach(tr => {
                    var cells = tr.querySelectorAll('td');
                    if (cells.length >= 3) {
                        var link = tr.querySelector('a[href]');
                        items.push({
                            name: cells[0].textContent.trim(),
                            context: tr.textContent.trim().replace(/\\s+/g, ' ').substring(0, 300),
                            link: link ? link.href : ''
                        });
                    }
                });
                if (items.length === 0) {
                    return [{name: '__RAW__', context: document.body.textContent.replace(/\\s+/g, ' ').substring(0, 2000)}];
                }
                // Dedupe by link
                var seen = {};
                return items.filter(i => { if (seen[i.link || i.name]) return false; seen[i.link || i.name] = true; return true; });
            }
        """)

        if results and results[0].get('name') == '__RAW__':
            raw = results[0]['context']
            # Check if there are tournament names in the raw text
            if 'tournoi' in raw.lower() or 'Aucun' in raw:
                print(f"   Page content: {raw[:500]}")
            else:
                print(f"   No results found. Page: {raw[:300]}")
        else:
            print(f"   Found {len(results)} tournaments:")
            for r in results:
                print(f"     {r['name'][:55]}")
                print(f"       {r.get('link', '')}")

            if results:
                with open(OUTPUT, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=['name', 'link', 'context'])
                    writer.writeheader()
                    writer.writerows(results)
                print(f"\n   Exported to {OUTPUT}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
