#!/usr/bin/env python3
"""
Generate tournament poster PDF natively with FPDF2 + QR code.
No browser, no Playwright, no screenshots. Clean vector PDF.

Usage:
    python scripts/generate_poster_native.py
    python scripts/generate_poster_native.py --date "02. Mai 2026" --name "LK Summer Smash Series - ESV - 1" --venue "ESV Wuppertal West" --address "Homannstr. 33b, 42327 Wuppertal" --url "https://www.tennis.de/spielen/turniersuche.html#detail/828059" --deadline "30. April 2026, 18:00" --output ~/Desktop/poster_esv1.pdf
"""

import argparse
import io
import os
import tempfile
from pathlib import Path

import qrcode
from fpdf import FPDF

# ── CHARTE GRAPHIQUE ──
GREEN_DEEP = (28, 58, 14)      # #1C3A0E
GREEN_COURT = (45, 90, 24)     # #2D5A18
ORANGE_CLAY = (184, 90, 32)    # #B85A20
CREAM = (240, 235, 224)        # #F0EBE0
WHITE = (255, 255, 255)
BLACK = (26, 26, 26)

TENNIS_DIR = Path(__file__).parent.parent
HERO_IMG = TENNIS_DIR / "hero-tennis.jpg"


class TournamentPoster(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=False)

        # Register fonts
        self.add_font("Barlow", "", os.path.join(os.path.dirname(__file__), "fonts", "Barlow-Regular.ttf"), uni=True)
        self.add_font("Barlow", "B", os.path.join(os.path.dirname(__file__), "fonts", "Barlow-Bold.ttf"), uni=True)
        self.add_font("BebasNeue", "", os.path.join(os.path.dirname(__file__), "fonts", "BebasNeue-Regular.ttf"), uni=True)


def generate_poster(
    name: str,
    date_str: str,
    weekday: str,
    venue_name: str,
    address: str,
    url: str,
    deadline: str,
    output_path: Path,
):
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()

    W = 210  # A4 width mm
    H = 297  # A4 height mm

    # ══════════════════════════════════════════
    # 1. HERO IMAGE (top ~85mm)
    # ══════════════════════════════════════════
    hero_h = 85
    if HERO_IMG.exists():
        pdf.image(str(HERO_IMG), x=0, y=0, w=W, h=hero_h)

    # Dark green overlay (semi-transparent effect via a green rect)
    pdf.set_fill_color(*GREEN_DEEP)
    pdf.set_draw_color(*GREEN_DEEP)

    # ══════════════════════════════════════════
    # 2. HEADER BAND (green, overlapping hero)
    # ══════════════════════════════════════════
    header_y = hero_h - 15
    header_h = 55
    pdf.rect(0, header_y, W, header_h, "F")

    # "BERGISCHE LK-TURNIERE"
    pdf.set_text_color(*CREAM)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_y(header_y + 8)
    pdf.cell(W, 5, "B E R G I S C H E   L K - T U R N I E R E", align="C", new_x="LMARGIN", new_y="NEXT")

    # Tournament name
    pdf.set_text_color(*WHITE)
    pdf.set_font("Helvetica", "B", 26)
    pdf.set_y(header_y + 16)
    pdf.cell(W, 12, name, align="C", new_x="LMARGIN", new_y="NEXT")

    # Venue
    pdf.set_text_color(*ORANGE_CLAY)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_y(header_y + 32)
    pdf.cell(W, 8, venue_name.upper(), align="C", new_x="LMARGIN", new_y="NEXT")

    # Orange bar
    bar_y = header_y + header_h
    pdf.set_fill_color(*ORANGE_CLAY)
    pdf.rect(0, bar_y, W, 4, "F")

    # ══════════════════════════════════════════
    # 3. CONTENT AREA (cream background)
    # ══════════════════════════════════════════
    content_y = bar_y + 4
    footer_h = 10
    content_h = H - content_y - footer_h
    pdf.set_fill_color(*CREAM)
    pdf.rect(0, content_y, W, content_h, "F")

    # ── DATE BLOCK ──
    date_block_w = 55
    date_block_h = 38
    date_x = (W - date_block_w) / 2
    date_y = content_y + 8

    pdf.set_fill_color(*GREEN_DEEP)
    pdf.rect(date_x, date_y, date_block_w, date_block_h, "F")

    # Weekday
    pdf.set_text_color(*ORANGE_CLAY)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_xy(date_x, date_y + 4)
    pdf.cell(date_block_w, 4, weekday.upper(), align="C")

    # Day number
    day_num = date_str.split(".")[0].strip() if "." in date_str else "??"
    pdf.set_text_color(*WHITE)
    pdf.set_font("Helvetica", "B", 36)
    pdf.set_xy(date_x, date_y + 9)
    pdf.cell(date_block_w, 14, day_num, align="C")

    # Month year
    month_year = date_str.split(".", 1)[1].strip().rstrip(")").split("(")[0].strip() if "." in date_str else date_str
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_xy(date_x, date_y + 25)
    pdf.cell(date_block_w, 6, month_year.upper(), align="C")

    # ── CATEGORY BLOCKS ──
    cat_y = date_y + date_block_h + 8
    cat_w = 80
    cat_h = 22
    gap = 6
    left_x = (W - 2 * cat_w - gap) / 2

    # JUGEND
    pdf.set_fill_color(*GREEN_DEEP)
    pdf.rect(left_x, cat_y, cat_w, cat_h, "F")
    pdf.set_text_color(*WHITE)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_xy(left_x, cat_y + 2)
    pdf.cell(cat_w, 7, "JUGEND", align="C")
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_xy(left_x, cat_y + 9)
    pdf.cell(cat_w, 5, "U12 | U14 | U16", align="C")
    pdf.set_text_color(200, 200, 200)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_xy(left_x, cat_y + 15)
    pdf.cell(cat_w, 4, "25 EUR + 3 EUR DTB", align="C")

    # HERREN
    right_x = left_x + cat_w + gap
    pdf.set_fill_color(*ORANGE_CLAY)
    pdf.rect(right_x, cat_y, cat_w, cat_h, "F")
    pdf.set_text_color(*WHITE)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_xy(right_x, cat_y + 2)
    pdf.cell(cat_w, 7, "HERREN", align="C")
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_xy(right_x, cat_y + 9)
    pdf.cell(cat_w, 5, "Herren", align="C")
    pdf.set_text_color(200, 200, 200)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_xy(right_x, cat_y + 15)
    pdf.cell(cat_w, 4, "30 EUR + 5 EUR DTB", align="C")

    # ── INFO CARDS ──
    info_y = cat_y + cat_h + 6
    card_w = 80
    card_h = 14

    # Format
    pdf.set_fill_color(*WHITE)
    pdf.set_draw_color(*ORANGE_CLAY)
    pdf.rect(left_x, info_y, card_w, card_h, "F")
    pdf.set_fill_color(*ORANGE_CLAY)
    pdf.rect(left_x, info_y, 1.5, card_h, "F")
    pdf.set_text_color(*ORANGE_CLAY)
    pdf.set_font("Helvetica", "B", 6)
    pdf.set_xy(left_x + 4, info_y + 2)
    pdf.cell(card_w - 6, 4, "FORMAT")
    pdf.set_text_color(*BLACK)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_xy(left_x + 4, info_y + 7)
    pdf.cell(card_w - 6, 5, "Spiralturnier LK")

    # Meldeschluss
    pdf.set_fill_color(*WHITE)
    pdf.rect(right_x, info_y, card_w, card_h, "F")
    pdf.set_fill_color(*ORANGE_CLAY)
    pdf.rect(right_x, info_y, 1.5, card_h, "F")
    pdf.set_text_color(*ORANGE_CLAY)
    pdf.set_font("Helvetica", "B", 6)
    pdf.set_xy(right_x + 4, info_y + 2)
    pdf.cell(card_w - 6, 4, "MELDESCHLUSS")
    pdf.set_text_color(*BLACK)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_xy(right_x + 4, info_y + 7)
    pdf.cell(card_w - 6, 5, deadline)

    # ── ADDRESS ──
    addr_y = info_y + card_h + 5
    addr_w = 2 * card_w + gap
    addr_h = 14
    pdf.set_fill_color(*WHITE)
    pdf.rect(left_x, addr_y, addr_w, addr_h, "F")
    pdf.set_fill_color(*ORANGE_CLAY)
    pdf.rect(left_x, addr_y, 1.5, addr_h, "F")

    # Pin icon (orange circle)
    pin_x = left_x + 6
    pin_cy = addr_y + addr_h / 2
    pdf.set_fill_color(*ORANGE_CLAY)
    pdf.ellipse(pin_x - 2.5, pin_cy - 2.5, 5, 5, "F")
    pdf.set_fill_color(*WHITE)
    pdf.ellipse(pin_x - 1, pin_cy - 1, 2, 2, "F")

    pdf.set_text_color(*ORANGE_CLAY)
    pdf.set_font("Helvetica", "B", 6)
    pdf.set_xy(left_x + 14, addr_y + 2)
    pdf.cell(addr_w - 18, 4, "ADRESSE")
    pdf.set_text_color(*BLACK)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_xy(left_x + 14, addr_y + 7)
    pdf.cell(addr_w - 18, 5, f"{venue_name}, {address}")

    # ── QR CODE SECTION ──
    qr_y = addr_y + addr_h + 6
    qr_section_w = 2 * card_w + gap
    qr_section_h = 28

    pdf.set_fill_color(*WHITE)
    pdf.set_draw_color(*GREEN_COURT)
    pdf.rect(left_x, qr_y, qr_section_w, qr_section_h, "DF")

    # Generate QR code
    qr = qrcode.make(url, box_size=10, border=1)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        qr.save(tmp.name)
        qr_img_path = tmp.name

    qr_size = 22
    pdf.image(qr_img_path, x=left_x + 4, y=qr_y + 3, w=qr_size, h=qr_size)
    os.unlink(qr_img_path)

    # QR text
    text_x = left_x + qr_size + 8
    pdf.set_text_color(*GREEN_DEEP)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_xy(text_x, qr_y + 3)
    pdf.cell(qr_section_w - qr_size - 12, 7, "JETZT ANMELDEN!")
    pdf.set_text_color(100, 100, 100)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_xy(text_x, qr_y + 11)
    pdf.cell(qr_section_w - qr_size - 12, 4, "QR-Code scannen oder auf tennis.de anmelden")
    pdf.set_text_color(*ORANGE_CLAY)
    pdf.set_font("Helvetica", "", 6)
    pdf.set_xy(text_x, qr_y + 16)
    pdf.cell(qr_section_w - qr_size - 12, 4, url)

    # ══════════════════════════════════════════
    # 4. GREEN BOTTOM (fill remaining space)
    # ══════════════════════════════════════════
    green_y = qr_y + qr_section_h + 6
    pdf.set_fill_color(*GREEN_DEEP)
    pdf.rect(0, green_y, W, H - green_y, "F")

    # ══════════════════════════════════════════
    # 5. FOOTER
    # ══════════════════════════════════════════
    footer_y = H - footer_h
    pdf.set_fill_color(*GREEN_DEEP)
    pdf.rect(0, footer_y, W, footer_h, "F")
    pdf.set_text_color(*CREAM)
    pdf.set_font("Helvetica", "B", 6)
    pdf.set_xy(8, footer_y + 3)
    pdf.cell(100, 4, "Bergische LK-Turniere | Veranstalter: Jean-Charles Das")
    pdf.set_text_color(*ORANGE_CLAY)
    pdf.set_font("Helvetica", "", 6)
    pdf.set_xy(W - 58, footer_y + 3)
    pdf.cell(50, 4, "jcdas1@gmail.com", align="R")

    # ── SAVE ──
    pdf.output(str(output_path))
    print(f"PDF saved: {output_path}")
    print(f"Size: {output_path.stat().st_size / 1024:.0f} KB")


# ── TOURNAMENT DATA ──
TOURNAMENTS = {
    "esv-1": {
        "name": "LK Summer Smash Series - ESV - 1",
        "date": "02. Mai 2026",
        "weekday": "Samstag",
        "venue": "ESV Wuppertal West",
        "address": "Homannstr. 33b, 42327 Wuppertal",
        "url": "https://www.tennis.de/spielen/turniersuche.html#detail/828059",
        "deadline": "30. April 2026, 18:00",
    },
    "esv-2": {
        "name": "LK Summer Smash Series - ESV - 2",
        "date": "10. Mai 2026",
        "weekday": "Sonntag",
        "venue": "ESV Wuppertal West",
        "address": "Homannstr. 33b, 42327 Wuppertal",
        "url": "https://www.tennis.de/spielen/turniersuche.html#detail/906353",
        "deadline": "08. Mai 2026, 18:00",
    },
}


def main():
    parser = argparse.ArgumentParser(description="Generate tournament poster PDF (native)")
    parser.add_argument("--tournament", type=str, default=None, help="Tournament key (esv-1, esv-2, or 'all')")
    parser.add_argument("--output", type=Path, default=None, help="Output PDF path")
    args = parser.parse_args()

    if args.tournament == "all" or args.tournament is None:
        for key, t in TOURNAMENTS.items():
            out = Path.home() / "Desktop" / f"Poster_{key.replace('-','_')}.pdf"
            generate_poster(
                name=t["name"], date_str=t["date"], weekday=t["weekday"],
                venue_name=t["venue"], address=t["address"],
                url=t["url"], deadline=t["deadline"], output_path=out,
            )
    else:
        t = TOURNAMENTS[args.tournament]
        out = args.output or Path.home() / "Desktop" / f"Poster_{args.tournament.replace('-','_')}.pdf"
        generate_poster(
            name=t["name"], date_str=t["date"], weekday=t["weekday"],
            venue_name=t["venue"], address=t["address"],
            url=t["url"], deadline=t["deadline"], output_path=out,
        )


if __name__ == "__main__":
    main()
