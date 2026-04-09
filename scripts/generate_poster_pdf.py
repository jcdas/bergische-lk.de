#!/usr/bin/env python3
"""
Generate tournament poster PDF using Playwright (headless Chrome).
Takes a pixel-perfect screenshot at A4 ratio, then wraps it in a PDF.

Usage:
    python scripts/generate_poster_pdf.py
    python scripts/generate_poster_pdf.py --output ~/Desktop/poster.pdf
"""

import argparse
import base64
import http.server
import threading
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

TENNIS_DIR = Path(__file__).parent.parent
DEFAULT_OUTPUT = TENNIS_DIR / "poster_output.pdf"
PORT = 8099

# A4 ratio: 210mm x 297mm = 1:1.414
# Use 2x resolution for crisp print
A4_W = 1588  # 794 * 2
A4_H = 2246  # 1123 * 2


def start_server(directory, port):
    handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(
        *args, directory=str(directory), **kwargs
    )
    server = http.server.HTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def generate_pdf(output_path: Path, tournament_id: str = None):
    server = start_server(TENNIS_DIR, PORT)
    time.sleep(0.5)

    url = f"http://127.0.0.1:{PORT}/poster.html"
    if tournament_id:
        url += f"?tournament={tournament_id}"

    print(f"Rendering: {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": A4_W, "height": A4_H}, device_scale_factor=1)
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(1500)

        # Force poster to fill exactly the viewport
        page.evaluate(f"""
            document.querySelector('.controls').style.display = 'none';
            document.body.style.padding = '0';
            document.body.style.margin = '0';
            document.body.style.background = '#F0EBE0';

            const poster = document.querySelector('.poster');
            poster.style.width = '{A4_W}px';
            poster.style.height = '{A4_H}px';
            poster.style.maxWidth = 'none';
            poster.style.boxShadow = 'none';
            poster.style.overflow = 'hidden';
            poster.style.borderRadius = '0';
            poster.style.background = '#1C3A0E';

            // Scale up fonts and elements for high-res
            document.querySelector('.content').style.flex = '1';

            // Hero: controlled size

            // Bigger title
            document.querySelector('.tournament-name').style.fontSize = '56pt';
            document.querySelector('.venue-name').style.fontSize = '28pt';
            document.querySelector('.site-name').style.fontSize = '18pt';

            // Bigger date block
            const dateBlock = document.querySelector('.date-block');
            dateBlock.style.padding = '24px 64px';
            document.querySelector('.date-block .day').style.fontSize = '72pt';
            document.querySelector('.date-block .month-year').style.fontSize = '36pt';
            document.querySelector('.date-block .weekday').style.fontSize = '16pt';

            // Bigger category blocks
            document.querySelectorAll('.cat-block').forEach(el => {{
                el.style.padding = '24px 20px';
            }});
            document.querySelectorAll('.cat-title').forEach(el => el.style.fontSize = '32pt');
            document.querySelectorAll('.cat-detail').forEach(el => el.style.fontSize = '16pt');
            document.querySelectorAll('.cat-fee').forEach(el => el.style.fontSize = '13pt');

            // Bigger info cards
            document.querySelectorAll('.info-card .label').forEach(el => el.style.fontSize = '12pt');
            document.querySelectorAll('.info-card .value').forEach(el => el.style.fontSize = '20pt');

            // Bigger QR section
            const qrSection = document.querySelector('.qr-section');
            qrSection.style.padding = '24px 32px';
            qrSection.style.gap = '32px';
            document.querySelector('.qr-text .cta').style.fontSize = '36pt';
            document.querySelector('.qr-text .sub').style.fontSize = '14pt';
            document.querySelector('.qr-text .url').style.fontSize = '12pt';
            const qrImg = document.querySelector('#qrContainer img');
            if (qrImg) {{
                qrImg.style.width = '160px';
                qrImg.style.height = '160px';
            }}

            // Bigger address
            document.querySelector('.address-icon svg').style.width = '48px';
            document.querySelector('.address-icon svg').style.height = '48px';

            // Footer — stick to bottom
            const footer = document.querySelector('.footer-band');
            footer.style.padding = '16px 32px';
            footer.style.fontSize = '12pt';
            footer.style.position = 'absolute';
            footer.style.bottom = '0';
            footer.style.left = '0';
            footer.style.right = '0';

            // Header band
            const header = document.querySelector('.header-band');
            header.style.padding = '28px 40px 32px';
            header.style.marginTop = '-100px';

            // Orange bar
            const style = document.createElement('style');
            style.textContent = '.header-band::after {{ bottom: -32px; height: 32px; }}';
            document.head.appendChild(style);

            // Content: fixed gaps, flex-start
            const content = document.querySelector('.content');
            content.style.padding = '40px 40px 24px';
            content.style.gap = '24px';
            content.style.justifyContent = 'flex-start';
            content.style.flex = '0 0 auto';
            content.style.background = '#F0EBE0';

            // Set hero to fixed size (1/3 of page)
            document.querySelector('.hero-image').style.height = '500px';

            // Category row
            document.querySelector('.cat-row').style.gap = '16px';

            // Info grid
            document.querySelector('.info-grid').style.gap = '12px';
        """)

        page.wait_for_timeout(500)

        # Take screenshot at exact A4 dimensions
        png_bytes = page.screenshot(clip={"x": 0, "y": 0, "width": A4_W, "height": A4_H})
        b64 = base64.b64encode(png_bytes).decode()

        # Create a clean page with the screenshot as an A4 image, then PDF it
        page.goto("about:blank")
        page.set_content(f"""<!DOCTYPE html>
        <html><head><style>
            * {{ margin:0; padding:0; }}
            body {{ width:210mm; height:297mm; }}
            img {{ width:210mm; height:297mm; display:block; }}
        </style></head>
        <body><img src="data:image/png;base64,{b64}"></body></html>""")
        page.wait_for_timeout(500)

        page.pdf(
            path=str(output_path),
            width="210mm",
            height="297mm",
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
        )

        browser.close()

    server.shutdown()
    print(f"PDF saved: {output_path}")
    print(f"Size: {output_path.stat().st_size / 1024:.0f} KB")


def main():
    parser = argparse.ArgumentParser(description="Generate tournament poster PDF")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output PDF path")
    parser.add_argument("--tournament", type=str, default=None, help="Tournament ID from data.js")
    args = parser.parse_args()

    generate_pdf(args.output, args.tournament)


if __name__ == "__main__":
    main()
