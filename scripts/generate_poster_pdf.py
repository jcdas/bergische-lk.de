#!/usr/bin/env python3
"""
Generate tournament poster PDF using Playwright (headless Chrome).
Properly renders hero image, QR code, and all CSS.

Usage:
    python scripts/generate_poster_pdf.py
    python scripts/generate_poster_pdf.py --output ~/Desktop/poster_esv1.pdf
    python scripts/generate_poster_pdf.py --tournament esv-summer-smash-1
"""

import argparse
import http.server
import threading
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

TENNIS_DIR = Path(__file__).parent.parent
DEFAULT_OUTPUT = TENNIS_DIR / "poster_output.pdf"
PORT = 8099


def start_server(directory, port):
    """Start a simple HTTP server in a background thread."""
    handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(
        *args, directory=str(directory), **kwargs
    )
    server = http.server.HTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def generate_pdf(output_path: Path, tournament_id: str = None):
    """Generate poster PDF."""
    # Start local server
    server = start_server(TENNIS_DIR, PORT)
    time.sleep(0.5)

    url = f"http://127.0.0.1:{PORT}/poster.html"
    if tournament_id:
        url += f"?tournament={tournament_id}"

    print(f"Rendering: {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 800, "height": 1200})
        page.goto(url, wait_until="networkidle")

        # Wait for QR code to render
        page.wait_for_timeout(1000)

        # Hide controls + force poster to fill page
        page.evaluate("""
            document.querySelector('.controls').style.display = 'none';
            document.body.style.padding = '0';
            document.body.style.margin = '0';
            document.body.style.background = 'none';
            const poster = document.querySelector('.poster');
            poster.style.width = '100%';
            poster.style.maxWidth = 'none';
            poster.style.boxShadow = 'none';
            poster.style.minHeight = '100vh';
            // Distribute space evenly between elements
            document.querySelector('.content').style.flex = '1';
            document.querySelector('.content').style.justifyContent = 'space-evenly';
        """)

        # Generate A4 PDF
        page.pdf(
            path=str(output_path),
            format="A4",
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
