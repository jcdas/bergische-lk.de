#!/usr/bin/env python3
"""Generate native PDF flyer + poster for Bergische LK-Turniere."""

import os
import io
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Brand colors ──
GREEN_DARK = HexColor("#1C3A0E")
GREEN_FIELD = HexColor("#2D5A18")
ORANGE_CLAY = HexColor("#B85A20")
CREAM = HexColor("#F0EBE0")
ORANGE_LIGHT = HexColor("#FFF3E0")
GREEN_LIGHT = HexColor("#E8F5E9")
GRAY = HexColor("#666666")
GRAY_LIGHT = HexColor("#999999")

W, H = A4  # 595.27 x 841.89 points


def make_qr(url, size=120):
    """Generate a QR code as an ImageReader."""
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M,
                        box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1C3A0E", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return ImageReader(buf)


def draw_rounded_rect(c, x, y, w, h, r, fill=None, stroke=None, stroke_width=1):
    """Draw a rounded rectangle."""
    p = c.beginPath()
    p.roundRect(x, y, w, h, r)
    p.close()
    if fill:
        c.setFillColor(fill)
    if stroke:
        c.setStrokeColor(stroke)
        c.setLineWidth(stroke_width)
    if fill and stroke:
        c.drawPath(p, fill=1, stroke=1)
    elif fill:
        c.drawPath(p, fill=1, stroke=0)
    elif stroke:
        c.drawPath(p, fill=0, stroke=1)


# ═══════════════════════════════════════════════════════════════════
#  FLYER — A4, email-friendly, text-oriented
# ═══════════════════════════════════════════════════════════════════
def create_flyer():
    filepath = os.path.join(OUTPUT_DIR, "flyer_eltern_lk.pdf")
    c = canvas.Canvas(filepath, pagesize=A4)
    c.setTitle("Bergische LK-Turniere — Sommer 2026")
    c.setAuthor("Jean-Charles Das")

    margin = 25 * mm
    content_w = W - 2 * margin

    # ── Header band ──
    c.setFillColor(GREEN_DARK)
    c.rect(0, H - 95, W, 95, fill=1, stroke=0)

    # Green gradient stripe
    c.setFillColor(GREEN_FIELD)
    c.rect(0, H - 100, W, 10, fill=1, stroke=0)

    # Title
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 26)
    c.drawString(margin, H - 42, "BERGISCHE")
    c.setFillColor(HexColor("#E8A050"))
    c.setFont("Helvetica-Bold", 26)
    c.drawString(margin, H - 68, "LK-TURNIERE")

    # Subtitle
    c.setFillColor(HexColor("#c0daa0"))
    c.setFont("Helvetica", 10)
    c.drawString(margin, H - 84, "Offizielle DTB-Turniere auf Sandplatz im Bergischen Land")

    # Website — top right
    c.setFillColor(HexColor("#E8A050"))
    c.setFont("Helvetica-Bold", 15)
    c.drawRightString(W - margin, H - 42, "bergische-lk.de")
    c.setFillColor(HexColor("#c0daa0"))
    c.setFont("Helvetica", 9)
    c.drawRightString(W - margin, H - 56, "Sommer 2026")

    y = H - 130

    # ── NEU badge ──
    badge_text = "NEU IN DER REGION!"
    c.setFillColor(GREEN_FIELD)
    tw = c.stringWidth(badge_text, "Helvetica-Bold", 10)
    draw_rounded_rect(c, margin, y - 4, tw + 16, 20, 4, fill=GREEN_FIELD)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin + 8, y + 2, badge_text)

    y -= 32

    # ── Intro text ──
    c.setFillColor(black)
    c.setFont("Helvetica", 11)
    c.drawString(margin, y, "Liebe Eltern, liebe Spieler:innen,")
    y -= 22

    lines = [
        "es gibt zu wenige LK-Turniere in unserer Region. Deshalb haben wir die",
        "LK Summer Smash Series ins Leben gerufen -- offizielle, DTB-gewertete Turniere",
        "auf Sandplatz, direkt vor der Haustur. Jede:r Teilnehmer:in spielt garantiert",
        "2 Matches (Spiralturnier-Format).",
    ]
    c.setFont("Helvetica", 10)
    for line in lines:
        c.drawString(margin, y, line)
        y -= 15
    y -= 10

    # ── Tournament cards ──
    card_w = (content_w - 10) / 2
    card_h = 155

    for i, (day, date_str, name, melde) in enumerate([
        ("Samstag", "02. MAI 2026", "LK Summer Smash #1", "Meldeschluss: 30. April 2026"),
        ("Sonntag", "10. MAI 2026", "LK Summer Smash #2", "Meldeschluss: 08. Mai 2026"),
    ]):
        cx = margin + i * (card_w + 10)
        cy = y - card_h

        # Card background
        draw_rounded_rect(c, cx, cy, card_w, card_h, 8, fill=white, stroke=HexColor("#e0e0e0"))

        # Orange header
        c.setFillColor(ORANGE_CLAY)
        p = c.beginPath()
        p.roundRect(cx, cy + card_h - 52, card_w, 52, 8)
        p.close()
        c.drawPath(p, fill=1, stroke=0)
        # Cover bottom rounded corners of header
        c.rect(cx, cy + card_h - 52, card_w, 10, fill=1, stroke=0)

        c.setFillColor(white)
        c.setFont("Helvetica", 9)
        c.drawCentredString(cx + card_w / 2, cy + card_h - 20, day)
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(cx + card_w / 2, cy + card_h - 42, date_str)

        # Card body
        bx = cx + 12
        by = cy + card_h - 68
        c.setFillColor(GREEN_DARK)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(bx, by, name)

        details = [
            ("ESV Wuppertal West", -14),
            ("Homannstr. 33b, Wuppertal", -13),
            ("7 Sandplatze", -13),
            ("Jugend 25 EUR | Herren 30 EUR", -13),
        ]
        c.setFont("Helvetica", 9)
        c.setFillColor(GRAY)
        for text, dy in details:
            by += dy
            c.drawString(bx, by, text)

        # Meldeschluss box
        by -= 18
        draw_rounded_rect(c, cx + 8, by - 4, card_w - 16, 18, 4,
                          fill=ORANGE_LIGHT, stroke=ORANGE_CLAY, stroke_width=0.5)
        c.setFillColor(ORANGE_CLAY)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(cx + card_w / 2, by, melde)

    y -= card_h + 15

    # ── Upcoming section ──
    draw_rounded_rect(c, margin, y - 55, content_w, 55, 8, fill=GREEN_LIGHT,
                      stroke=GREEN_FIELD, stroke_width=0.5)
    c.setFillColor(GREEN_DARK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin + 12, y - 18, "Weitere Termine im Sommer 2026")
    c.setFont("Helvetica", 9)
    c.setFillColor(GRAY)
    c.drawString(margin + 12, y - 33,
                 "Gruiten Cup -- TC Gruiten (6 Sandplatze), Haan -- Termin folgt")
    c.drawString(margin + 12, y - 46,
                 "Weitere LK-Turniere Juni-September -- Termine auf bergische-lk.de")

    y -= 72

    # ── QR codes ──
    qr_size = 65
    qr_gap = (content_w - 3 * qr_size) / 4
    qrs = [
        ("https://www.tennis.de/spielen/turniersuche.html#detail/828059",
         "Anmeldung #1", "02. Mai"),
        ("https://www.tennis.de/spielen/turniersuche.html#detail/829441",
         "Anmeldung #2", "10. Mai"),
        ("https://bergische-lk.de",
         "Alle Infos", "bergische-lk.de"),
    ]
    for i, (url, label, sublabel) in enumerate(qrs):
        qx = margin + qr_gap + i * (qr_size + qr_gap)
        qy = y - qr_size - 5

        draw_rounded_rect(c, qx - 5, qy - 22, qr_size + 10, qr_size + 32, 6, fill=white)
        qr_img = make_qr(url, qr_size)
        c.drawImage(qr_img, qx, qy, qr_size, qr_size)
        c.setFillColor(GREEN_DARK)
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(qx + qr_size / 2, qy - 10, label)
        c.setFillColor(GRAY_LIGHT)
        c.setFont("Helvetica", 6)
        c.drawCentredString(qx + qr_size / 2, qy - 18, sublabel)

    y -= qr_size + 40

    # ── Features row ──
    feat_w = (content_w - 30) / 4
    features = [
        ("LK-gewertet", "Offizielle DTB-Wertung"),
        ("Sandplatz", "Terre Battue"),
        ("2 Matches garantiert", "Spiralturnier-Format"),
        ("Regional", "Kurze Anfahrt"),
    ]
    for i, (title, desc) in enumerate(features):
        fx = margin + i * (feat_w + 10)
        draw_rounded_rect(c, fx, y - 38, feat_w, 38, 6, fill=white)
        c.setFillColor(GREEN_DARK)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(fx + feat_w / 2, y - 14, title)
        c.setFillColor(GRAY)
        c.setFont("Helvetica", 7)
        c.drawCentredString(fx + feat_w / 2, y - 26, desc)

    y -= 52

    # ── Categories ──
    c.setFillColor(GREEN_DARK)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(margin, y, "KATEGORIEN")
    y -= 8

    cat_w = (content_w - 30) / 4
    cats = [
        ("U12", "Jahrgang 2014+", GREEN_FIELD),
        ("U14", "Jahrgang 2012+", GREEN_FIELD),
        ("U16", "Jahrgang 2010+", GREEN_FIELD),
        ("HERREN", "Erwachsene", ORANGE_CLAY),
    ]
    for i, (age, label, color) in enumerate(cats):
        cx = margin + i * (cat_w + 10)
        draw_rounded_rect(c, cx, y - 32, cat_w, 32, 6, fill=color)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(cx + cat_w / 2, y - 14, age)
        c.setFont("Helvetica", 7)
        c.drawCentredString(cx + cat_w / 2, y - 26, label)

    # ── Footer ──
    footer_h = 50
    c.setFillColor(GREEN_DARK)
    c.rect(0, 0, W, footer_h, fill=1, stroke=0)

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(margin, footer_h - 18, "Jean-Charles Das -- Organisator")
    c.setFillColor(HexColor("#E8A050"))
    c.setFont("Helvetica", 8)
    c.drawString(margin, footer_h - 30, "info@bergische-lk.de")
    c.setFillColor(HexColor("#a0c080"))
    c.setFont("Helvetica", 7.5)
    c.drawString(margin, footer_h - 42, "Anmeldung uber mybigpoint.tennis.de")

    c.setFillColor(HexColor("#E8A050"))
    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(W - margin, footer_h - 20, "bergische-lk.de")
    c.setFillColor(HexColor("#a0c080"))
    c.setFont("Helvetica", 7.5)
    c.drawRightString(W - margin, footer_h - 34, "Bergische LK-Turniere -- Sommer 2026")

    c.save()
    print(f"Flyer saved: {filepath}")


# ═══════════════════════════════════════════════════════════════════
#  POSTER — A4, bold, eye-catching, for club display
# ═══════════════════════════════════════════════════════════════════
def create_poster():
    filepath = os.path.join(OUTPUT_DIR, "poster_lk_turniere.pdf")
    c = canvas.Canvas(filepath, pagesize=A4)
    c.setTitle("Bergische LK-Turniere -- Poster Sommer 2026")
    c.setAuthor("Jean-Charles Das")

    margin = 20 * mm

    # ── Full green header ──
    header_h = 130
    c.setFillColor(GREEN_DARK)
    c.rect(0, H - header_h, W, header_h, fill=1, stroke=0)

    # Orange accent stripe
    c.setFillColor(ORANGE_CLAY)
    c.rect(0, H - header_h, W, 6, fill=1, stroke=0)

    # Title — big and bold
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 40)
    c.drawCentredString(W / 2, H - 50, "BERGISCHE")
    c.setFillColor(HexColor("#E8A050"))
    c.setFont("Helvetica-Bold", 40)
    c.drawCentredString(W / 2, H - 90, "LK-TURNIERE")

    c.setFillColor(HexColor("#c0daa0"))
    c.setFont("Helvetica", 12)
    c.drawCentredString(W / 2, H - 112, "Offizielle DTB-Turniere auf Sandplatz im Bergischen Land")

    y = H - header_h - 20

    # ── NEU badge ──
    badge_w = 200
    draw_rounded_rect(c, (W - badge_w) / 2, y - 6, badge_w, 26, 6, fill=ORANGE_CLAY)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(W / 2, y, "NEU IN DER REGION!")

    y -= 40

    # ── Tournament 1 ──
    card_w = W - 2 * margin
    card_h = 80

    for day, date_str, name, venue_line, melde in [
        ("SAMSTAG", "02. MAI 2026", "LK Summer Smash Series #1",
         "ESV Wuppertal West -- 7 Sandplatze -- Wuppertal", "Meldeschluss: 30. April"),
        ("SONNTAG", "10. MAI 2026", "LK Summer Smash Series #2",
         "ESV Wuppertal West -- 7 Sandplatze -- Wuppertal", "Meldeschluss: 08. Mai"),
    ]:
        draw_rounded_rect(c, margin, y - card_h, card_w, card_h, 10,
                          fill=white, stroke=GREEN_FIELD, stroke_width=1.5)

        # Orange date block on left
        date_block_w = 140
        c.setFillColor(ORANGE_CLAY)
        p = c.beginPath()
        p.roundRect(margin, y - card_h, date_block_w, card_h, 10)
        p.close()
        c.drawPath(p, fill=1, stroke=0)
        # Cover right rounded corners
        c.rect(margin + date_block_w - 15, y - card_h, 15, card_h, fill=1, stroke=0)

        c.setFillColor(white)
        c.setFont("Helvetica", 10)
        c.drawCentredString(margin + date_block_w / 2, y - 22, day)
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(margin + date_block_w / 2, y - 43, date_str.split("2026")[0].strip())
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(margin + date_block_w / 2, y - 62, "2026")

        # Text content
        tx = margin + date_block_w + 15
        c.setFillColor(GREEN_DARK)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(tx, y - 25, name)

        c.setFillColor(GRAY)
        c.setFont("Helvetica", 10)
        c.drawString(tx, y - 42, venue_line)

        c.setFillColor(ORANGE_CLAY)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(tx, y - 58, melde)

        y -= card_h + 12

    # ── Upcoming ──
    draw_rounded_rect(c, margin, y - 45, card_w, 45, 8, fill=GREEN_LIGHT,
                      stroke=GREEN_FIELD, stroke_width=1)
    c.setFillColor(GREEN_DARK)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(W / 2, y - 18, "Weitere Termine im Sommer 2026")
    c.setFillColor(GRAY)
    c.setFont("Helvetica", 10)
    c.drawCentredString(W / 2, y - 35, "Gruiten Cup (TC Gruiten, Haan) + weitere LK-Turniere Juni-September")

    y -= 62

    # ── Key features — big icons style ──
    feat_w = (card_w - 20) / 4
    features = [
        ("LK-gewertet", "Offizielle", "DTB-Wertung"),
        ("Sandplatz", "Terre", "Battue"),
        ("2 Matches", "garantiert", "pro Spieler:in"),
        ("U12-U16", "+ Herren", "Erwachsene"),
    ]
    for i, (t1, t2, t3) in enumerate(features):
        fx = margin + i * (feat_w + 6.7)
        draw_rounded_rect(c, fx, y - 58, feat_w, 58, 8, fill=GREEN_FIELD)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(fx + feat_w / 2, y - 18, t1)
        c.setFont("Helvetica", 9)
        c.drawCentredString(fx + feat_w / 2, y - 33, t2)
        c.drawCentredString(fx + feat_w / 2, y - 45, t3)

    y -= 72

    # ── Nenngeld ──
    draw_rounded_rect(c, margin, y - 35, card_w, 35, 8, fill=ORANGE_LIGHT,
                      stroke=ORANGE_CLAY, stroke_width=1)
    c.setFillColor(ORANGE_CLAY)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(W / 2, y - 14, "Nenngeld: Jugend 25 EUR (+3 EUR DTB)  |  Herren 30 EUR (+5 EUR DTB)")
    c.setFillColor(GRAY)
    c.setFont("Helvetica", 8)
    c.drawCentredString(W / 2, y - 28, "Anmeldung ausschliesslich uber mybigpoint.tennis.de")

    y -= 50

    # ── QR codes — prominent ──
    qr_size = 105
    qr_gap = (card_w - 3 * qr_size) / 4
    qrs = [
        ("https://www.tennis.de/spielen/turniersuche.html#detail/828059",
         "ANMELDUNG #1", "02. Mai 2026"),
        ("https://www.tennis.de/spielen/turniersuche.html#detail/829441",
         "ANMELDUNG #2", "10. Mai 2026"),
        ("https://bergische-lk.de",
         "ALLE INFOS", "bergische-lk.de"),
    ]
    for i, (url, label, sublabel) in enumerate(qrs):
        qx = margin + qr_gap + i * (qr_size + qr_gap)
        qy = y - qr_size - 10

        draw_rounded_rect(c, qx - 8, qy - 30, qr_size + 16, qr_size + 42, 8, fill=white,
                          stroke=HexColor("#e0e0e0"))
        qr_img = make_qr(url, qr_size)
        c.drawImage(qr_img, qx, qy, qr_size, qr_size)
        c.setFillColor(GREEN_DARK)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(qx + qr_size / 2, qy - 12, label)
        c.setFillColor(GRAY)
        c.setFont("Helvetica", 8)
        c.drawCentredString(qx + qr_size / 2, qy - 23, sublabel)

    # ── Scan-Hinweis ──
    y -= qr_size + 50
    c.setFillColor(GRAY)
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(W / 2, y, "QR-Code scannen und direkt anmelden!")

    # ── Footer ──
    footer_h = 45
    c.setFillColor(GREEN_DARK)
    c.rect(0, 0, W, footer_h, fill=1, stroke=0)

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin, footer_h - 18, "Jean-Charles Das -- Organisator")
    c.setFillColor(HexColor("#E8A050"))
    c.setFont("Helvetica", 9)
    c.drawString(margin, footer_h - 32, "info@bergische-lk.de")

    c.setFillColor(HexColor("#E8A050"))
    c.setFont("Helvetica-Bold", 16)
    c.drawRightString(W - margin, footer_h - 20, "bergische-lk.de")
    c.setFillColor(HexColor("#a0c080"))
    c.setFont("Helvetica", 8)
    c.drawRightString(W - margin, footer_h - 34, "Bergische LK-Turniere -- Sommer 2026")

    c.save()
    print(f"Poster saved: {filepath}")


if __name__ == "__main__":
    create_flyer()
    create_poster()
    print("\nDone! Both PDFs generated.")
