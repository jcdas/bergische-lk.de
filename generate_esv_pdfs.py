#!/usr/bin/env python3
"""Generate ESV-specific PDFs: display poster + digital flyer — full season 2026."""

import os
import io
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

GREEN_DARK   = HexColor("#1C3A0E")
GREEN_FIELD  = HexColor("#2D5A18")
ORANGE_CLAY  = HexColor("#B85A20")
CREAM        = HexColor("#F0EBE0")
ORANGE_LIGHT = HexColor("#FFF3E0")
GREEN_LIGHT  = HexColor("#E8F5E9")
GRAY         = HexColor("#555555")
GRAY_LIGHT   = HexColor("#888888")
GOLD         = HexColor("#E8A050")
PALE_GREEN   = HexColor("#c0daa0")

W, H = A4  # 595.27 x 841.89 pts

# ── Saison 2026 — dates ESV disponibles (depuis planning famille) ──────────
CONFIRMED = [
    ("Sa", "02. Mai 2026",  "LK Summer Smash #1", "30. April, 18 Uhr",
     "https://www.tennis.de/spielen/turniersuche.html#detail/828059"),
    ("So", "10. Mai 2026",  "LK Summer Smash #2", "08. Mai, 18 Uhr",
     "https://www.tennis.de/spielen/turniersuche.html#detail/829441"),
]

# 4 dates planifiées (pas encore soumises au TVN)
PLANNED = [
    ("So", "07. Juni 2026",  "LK Summer Smash #3"),
    ("So", "28. Juni 2026",  "LK Summer Smash #4"),
    ("So", "05. Juli 2026",  "LK Summer Smash #5"),
    ("Sa", "11. Juli 2026",  "LK Summer Smash #6"),
]


def make_qr(url):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M,
                       box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1C3A0E", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return ImageReader(buf)


def rr(c, x, y, w, h, r, fill=None, stroke=None, sw=1):
    p = c.beginPath()
    p.roundRect(x, y, w, h, r)
    p.close()
    if fill:
        c.setFillColor(fill)
    if stroke:
        c.setStrokeColor(stroke)
        c.setLineWidth(sw)
    if fill and stroke:
        c.drawPath(p, fill=1, stroke=1)
    elif fill:
        c.drawPath(p, fill=1, stroke=0)
    elif stroke:
        c.drawPath(p, fill=0, stroke=1)


# ═══════════════════════════════════════════════════════════════════
#  POSTER — A4, affichage vitrine ESV, saison complète
# ═══════════════════════════════════════════════════════════════════
def create_esv_poster():
    filepath = os.path.join(OUTPUT_DIR, "poster_esv_saison.pdf")
    c = canvas.Canvas(filepath, pagesize=A4)
    c.setTitle("ESV Wuppertal West – LK Summer Smash Series 2026")
    c.setAuthor("Jean-Charles Das")

    margin = 18 * mm
    cw = W - 2 * margin

    # ── Header ────────────────────────────────────────────────────
    c.setFillColor(GREEN_DARK)
    c.rect(0, H - 140, W, 140, fill=1, stroke=0)
    c.setFillColor(ORANGE_CLAY)
    c.rect(0, H - 143, W, 7, fill=1, stroke=0)

    c.setFillColor(PALE_GREEN)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(W / 2, H - 22, "ESV WUPPERTAL WEST  ·  HOMANNSTR. 33B  ·  42327 WUPPERTAL")

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 38)
    c.drawCentredString(W / 2, H - 60, "LK SUMMER SMASH SERIES")
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(W / 2, H - 85, "SAISON 2026  ·  SANDPLATZ")

    c.setFillColor(PALE_GREEN)
    c.setFont("Helvetica", 10)
    c.drawCentredString(W / 2, H - 103, "Offizielle DTB-Turniere  ·  U12 · U14 · U16 · Herren  ·  LK1,0 bis LK25,0")

    # NEU badge
    rr(c, (W - 160) / 2, H - 133, 160, 22, 5, fill=ORANGE_CLAY)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(W / 2, H - 126, "NEU IN DER REGION!")

    y = H - 158

    # ── Confirmed cards (compact, side by side) ───────────────────
    c.setFillColor(GREEN_DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin, y, "BESTÄTIGTE TERMINE — ANMELDUNG OFFEN")
    y -= 6

    card_w = (cw - 8) / 2
    card_h = 72

    for i, (day, date, name, melde, url) in enumerate(CONFIRMED):
        cx = margin + i * (card_w + 8)
        cy = y - card_h
        rr(c, cx, cy, card_w, card_h, 7, fill=white, stroke=GREEN_FIELD, sw=1.5)

        # Left orange date strip
        c.setFillColor(ORANGE_CLAY)
        p = c.beginPath()
        p.roundRect(cx, cy, 60, card_h, 7)
        p.close()
        c.drawPath(p, fill=1, stroke=0)
        c.rect(cx + 46, cy, 14, card_h, fill=1, stroke=0)

        c.setFillColor(white)
        c.setFont("Helvetica", 7)
        c.drawCentredString(cx + 30, cy + card_h - 13, day.upper())
        date_parts = date.split(" ")
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(cx + 30, cy + card_h - 30, date_parts[0].replace(".", ""))
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(cx + 30, cy + card_h - 45, date_parts[1])
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(cx + 30, cy + card_h - 58, date_parts[2])

        tx = cx + 68
        c.setFillColor(GREEN_DARK)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(tx, cy + card_h - 18, name)
        c.setFillColor(GRAY)
        c.setFont("Helvetica", 8)
        c.drawString(tx, cy + card_h - 32, "U12 · U14 · U16 · Herren")
        c.setFillColor(ORANGE_CLAY)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(tx, cy + card_h - 46, "Meldeschluss: " + melde)

        # Mini QR
        qs = 34
        c.drawImage(make_qr(url), cx + card_w - qs - 6, cy + 6, qs, qs)

    y -= card_h + 14

    # ── Planned dates — 4 cards in a row ──────────────────────────
    c.setFillColor(GREEN_DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin, y, "WEITERE GEPLANTE TERMINE — ANMELDUNG FOLGT")
    y -= 6

    pl_w = (cw - 15) / 4
    pl_h = 68

    for i, (day, date, name) in enumerate(PLANNED):
        cx = margin + i * (pl_w + 5)
        cy = y - pl_h
        rr(c, cx, cy, pl_w, pl_h, 7, fill=white, stroke=GREEN_FIELD, sw=1)

        # Green header
        c.setFillColor(GREEN_FIELD)
        p = c.beginPath()
        p.roundRect(cx, cy + pl_h - 36, pl_w, 36, 7)
        p.close()
        c.drawPath(p, fill=1, stroke=0)
        c.rect(cx, cy + pl_h - 36, pl_w, 8, fill=1, stroke=0)

        c.setFillColor(white)
        c.setFont("Helvetica", 7)
        c.drawCentredString(cx + pl_w / 2, cy + pl_h - 13, day.upper())
        date_parts = date.split(" ")
        c.setFont("Helvetica-Bold", 13)
        c.drawCentredString(cx + pl_w / 2, cy + pl_h - 28, date_parts[0].replace(".", "") + ". " + date_parts[1])

        c.setFillColor(GREEN_DARK)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(cx + pl_w / 2, cy + pl_h - 46, name)

        rr(c, cx + 6, cy + 5, pl_w - 12, 14, 3, fill=GREEN_LIGHT, stroke=GREEN_FIELD, sw=0.5)
        c.setFillColor(GREEN_FIELD)
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(cx + pl_w / 2, cy + 10, "Anmeldung folgt")

    y -= pl_h + 10

    # Sommerferien
    rr(c, margin, y - 14, cw, 14, 3, fill=ORANGE_LIGHT, stroke=ORANGE_CLAY, sw=0.5)
    c.setFillColor(ORANGE_CLAY)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawCentredString(W / 2, y - 9, "Sommerferien NRW: 20. Juli – 01. September 2026 — kein Turnierbetrieb")
    y -= 22

    # ── Categories ────────────────────────────────────────────────
    cats = [("U12", "Jg. 2014+"), ("U14", "Jg. 2012+"), ("U16", "Jg. 2010+"), ("HERREN", "Erw.")]
    cat_w = (cw - 15) / 4
    for i, (label, sub) in enumerate(cats):
        cx = margin + i * (cat_w + 5)
        color = ORANGE_CLAY if label == "HERREN" else GREEN_FIELD
        rr(c, cx, y - 30, cat_w, 30, 6, fill=color)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 13)
        c.drawCentredString(cx + cat_w / 2, y - 13, label)
        c.setFont("Helvetica", 7)
        c.drawCentredString(cx + cat_w / 2, y - 25, sub)
    y -= 38

    # ── Key facts row ─────────────────────────────────────────────
    feats = [
        ("LK-gewertet", "DTB-Wertung"),
        ("2 Matches", "garantiert"),
        ("Spiralturnier", "Format"),
        ("Regional", "kurze Anfahrt"),
    ]
    feat_w = (cw - 15) / 4
    for i, (t, s) in enumerate(feats):
        fx = margin + i * (feat_w + 5)
        rr(c, fx, y - 28, feat_w, 28, 5, fill=CREAM)
        c.setFillColor(GREEN_DARK)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(fx + feat_w / 2, y - 11, t)
        c.setFillColor(GRAY)
        c.setFont("Helvetica", 7)
        c.drawCentredString(fx + feat_w / 2, y - 22, s)
    y -= 36

    # ── Nenngeld ─────────────────────────────────────────────────
    rr(c, margin, y - 22, cw, 22, 5, fill=ORANGE_LIGHT, stroke=ORANGE_CLAY, sw=0.5)
    c.setFillColor(ORANGE_CLAY)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(W / 2, y - 10, "Jugend 25 € (+3 € DTB)  ·  Herren 30 € (+5 € DTB)  ·  Anmeldung via mybigpoint.tennis.de")
    y -= 30

    # ── QR codes ─────────────────────────────────────────────────
    qr_size = 80
    qrs = [
        ("https://www.tennis.de/spielen/turniersuche.html#detail/828059", "ANMELDUNG #1", "02. Mai"),
        ("https://www.tennis.de/spielen/turniersuche.html#detail/829441", "ANMELDUNG #2", "10. Mai"),
        ("https://bergische-lk.de", "ALLE TERMINE", "bergische-lk.de"),
    ]
    qr_gap = (cw - 3 * qr_size) / 4
    for i, (url, label, sub) in enumerate(qrs):
        qx = margin + qr_gap + i * (qr_size + qr_gap)
        qy = y - qr_size - 6
        rr(c, qx - 7, qy - 20, qr_size + 14, qr_size + 30, 7, fill=white,
           stroke=HexColor("#e0e0e0"), sw=0.7)
        c.drawImage(make_qr(url), qx, qy, qr_size, qr_size)
        c.setFillColor(GREEN_DARK)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawCentredString(qx + qr_size / 2, qy - 9, label)
        c.setFillColor(GRAY_LIGHT)
        c.setFont("Helvetica", 6.5)
        c.drawCentredString(qx + qr_size / 2, qy - 18, sub)

    y -= qr_size + 32
    c.setFillColor(GRAY_LIGHT)
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(W / 2, y, "QR-Code scannen · direkt anmelden · DTB-Nummer erforderlich")

    # ── Footer ────────────────────────────────────────────────────
    fh = 42
    c.setFillColor(GREEN_DARK)
    c.rect(0, 0, W, fh, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(margin, fh - 15, "Jean-Charles Das · Organisator")
    c.setFillColor(GOLD)
    c.setFont("Helvetica", 8)
    c.drawString(margin, fh - 27, "info@bergische-lk.de")
    c.setFillColor(PALE_GREEN)
    c.setFont("Helvetica", 7)
    c.drawString(margin, fh - 38, "Bergische LK-Turniere · Saison 2026")
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 15)
    c.drawRightString(W - margin, fh - 18, "bergische-lk.de")
    c.setFillColor(PALE_GREEN)
    c.setFont("Helvetica", 7)
    c.drawRightString(W - margin, fh - 30, "Anmeldung via mybigpoint")

    c.save()
    print(f"Poster saved: {filepath}")


# ═══════════════════════════════════════════════════════════════════
#  FLYER — A4 digital, email / WhatsApp, saison complète
# ═══════════════════════════════════════════════════════════════════
def create_esv_flyer():
    filepath = os.path.join(OUTPUT_DIR, "flyer_esv_digital.pdf")
    c = canvas.Canvas(filepath, pagesize=A4)
    c.setTitle("ESV Wuppertal West – LK Turniere Saison 2026")
    c.setAuthor("Jean-Charles Das")

    margin = 22 * mm
    cw = W - 2 * margin

    # ── Header ────────────────────────────────────────────────────
    c.setFillColor(GREEN_DARK)
    c.rect(0, H - 100, W, 100, fill=1, stroke=0)
    c.setFillColor(ORANGE_CLAY)
    c.rect(0, H - 103, W, 7, fill=1, stroke=0)

    c.setFillColor(PALE_GREEN)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(W / 2, H - 20, "ESV WUPPERTAL WEST · HOMANNSTR. 33B · WUPPERTAL")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 27)
    c.drawCentredString(W / 2, H - 50, "LK SUMMER SMASH SERIES")
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 17)
    c.drawCentredString(W / 2, H - 72, "SAISON 2026 · SANDPLATZ")
    c.setFillColor(PALE_GREEN)
    c.setFont("Helvetica", 8.5)
    c.drawCentredString(W / 2, H - 88, "Offizielle DTB-Turniere · U12 · U14 · U16 · Herren")

    y = H - 116

    # ── Intro ─────────────────────────────────────────────────────
    c.setFillColor(black)
    c.setFont("Helvetica", 9.5)
    c.drawString(margin, y, "Liebe Tennisspieler:innen,")
    y -= 14
    for line in [
        "ESV Wuppertal West richtet 2026 eine neue Serie offizieller LK-Turniere auf Sandplatz aus.",
        "Alle Termine werden laufend veröffentlicht — meldet euch rechtzeitig an!",
    ]:
        c.drawString(margin, y, line)
        y -= 13
    y -= 6

    # ── Confirmed — 2 cards side by side ──────────────────────────
    c.setFillColor(GREEN_DARK)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(margin, y, "BESTÄTIGTE TERMINE")
    y -= 6

    card_w = (cw - 8) / 2
    card_h = 100

    for i, (day, date, name, melde, url) in enumerate(CONFIRMED):
        cx = margin + i * (card_w + 8)
        cy = y - card_h
        rr(c, cx, cy, card_w, card_h, 7, fill=white, stroke=HexColor("#d0d0d0"), sw=0.8)

        # Orange header
        c.setFillColor(ORANGE_CLAY)
        p = c.beginPath()
        p.roundRect(cx, cy + card_h - 40, card_w, 40, 7)
        p.close()
        c.drawPath(p, fill=1, stroke=0)
        c.rect(cx, cy + card_h - 40, card_w, 10, fill=1, stroke=0)

        c.setFillColor(white)
        c.setFont("Helvetica", 8)
        c.drawCentredString(cx + card_w / 2, cy + card_h - 16, day.upper())
        c.setFont("Helvetica-Bold", 15)
        c.drawCentredString(cx + card_w / 2, cy + card_h - 34, date)

        # Status chip
        rr(c, cx + card_w / 2 - 38, cy + card_h - 52, 76, 14, 3, fill=GREEN_FIELD)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 6.5)
        c.drawCentredString(cx + card_w / 2, cy + card_h - 44, "ANMELDUNG OFFEN")

        bx = cx + 8
        by = cy + card_h - 66
        c.setFillColor(GREEN_DARK)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(bx, by, name)
        c.setFillColor(GRAY)
        c.setFont("Helvetica", 8)
        c.drawString(bx, by - 12, "U12 · U14 · U16 · Herren")
        c.drawString(bx, by - 24, "Jugend 25 € · Herren 30 € (+DTB)")
        rr(c, cx + 5, cy + 4, card_w - 10, 14, 3, fill=ORANGE_LIGHT, stroke=ORANGE_CLAY, sw=0.5)
        c.setFillColor(ORANGE_CLAY)
        c.setFont("Helvetica-Bold", 6.5)
        c.drawCentredString(cx + card_w / 2, cy + 9, "Meldeschluss: " + melde)

        # Mini QR
        qs = 30
        c.drawImage(make_qr(url), cx + card_w - qs - 5, cy + card_h - 34 - qs, qs, qs)

    y -= card_h + 12

    # ── Planned dates — 4 cards ────────────────────────────────────
    c.setFillColor(GREEN_DARK)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(margin, y, "WEITERE GEPLANTE TERMINE — ANMELDUNG FOLGT")
    y -= 6

    pl_w = (cw - 15) / 4
    pl_h = 58

    for i, (day, date, name) in enumerate(PLANNED):
        cx = margin + i * (pl_w + 5)
        cy = y - pl_h
        rr(c, cx, cy, pl_w, pl_h, 6, fill=white, stroke=GREEN_FIELD, sw=0.8)

        c.setFillColor(GREEN_FIELD)
        p = c.beginPath()
        p.roundRect(cx, cy + pl_h - 30, pl_w, 30, 6)
        p.close()
        c.drawPath(p, fill=1, stroke=0)
        c.rect(cx, cy + pl_h - 30, pl_w, 7, fill=1, stroke=0)

        c.setFillColor(white)
        c.setFont("Helvetica", 6.5)
        c.drawCentredString(cx + pl_w / 2, cy + pl_h - 12, day.upper())
        date_parts = date.split(" ")
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(cx + pl_w / 2, cy + pl_h - 25, date_parts[0].replace(".", "") + ". " + date_parts[1])

        c.setFillColor(GREEN_DARK)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawCentredString(cx + pl_w / 2, cy + pl_h - 40, name)

        rr(c, cx + 5, cy + 4, pl_w - 10, 12, 3, fill=GREEN_LIGHT, stroke=GREEN_FIELD, sw=0.4)
        c.setFillColor(GREEN_FIELD)
        c.setFont("Helvetica-Bold", 6)
        c.drawCentredString(cx + pl_w / 2, cy + 8, "Anmeldung folgt")

    y -= pl_h + 8

    # Sommerferien
    rr(c, margin, y - 13, cw, 13, 3, fill=ORANGE_LIGHT, stroke=ORANGE_CLAY, sw=0.4)
    c.setFillColor(ORANGE_CLAY)
    c.setFont("Helvetica-Bold", 6.5)
    c.drawCentredString(W / 2, y - 8.5, "Sommerferien NRW: 20. Juli – 01. September 2026 — kein Turnierbetrieb")
    y -= 20

    # ── Categories ────────────────────────────────────────────────
    cats = [("U12", "Jg. 2014+"), ("U14", "Jg. 2012+"), ("U16", "Jg. 2010+"), ("HERREN", "Erw.")]
    cat_w = (cw - 15) / 4
    for i, (label, sub) in enumerate(cats):
        cx = margin + i * (cat_w + 5)
        color = ORANGE_CLAY if label == "HERREN" else GREEN_FIELD
        rr(c, cx, y - 28, cat_w, 28, 5, fill=color)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(cx + cat_w / 2, y - 13, label)
        c.setFont("Helvetica", 6.5)
        c.drawCentredString(cx + cat_w / 2, y - 24, sub)
    y -= 36

    # ── Features ─────────────────────────────────────────────────
    feats = [("LK-gewertet", "DTB-Wertung"), ("2 Matches", "garantiert"),
             ("Spiralturnier", "Format"), ("Regional", "kurze Anfahrt")]
    feat_w = (cw - 15) / 4
    for i, (t, s) in enumerate(feats):
        fx = margin + i * (feat_w + 5)
        rr(c, fx, y - 26, feat_w, 26, 5, fill=GREEN_LIGHT, stroke=GREEN_FIELD, sw=0.4)
        c.setFillColor(GREEN_DARK)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(fx + feat_w / 2, y - 11, t)
        c.setFillColor(GRAY)
        c.setFont("Helvetica", 7)
        c.drawCentredString(fx + feat_w / 2, y - 22, s)
    y -= 34

    # ── Big central QR ────────────────────────────────────────────
    qr_size = 72
    qx = (W - qr_size) / 2
    qy = y - qr_size - 4
    rr(c, qx - 12, qy - 18, qr_size + 24, qr_size + 32, 9,
       fill=white, stroke=GREEN_FIELD, sw=1)
    c.drawImage(make_qr("https://bergische-lk.de"), qx, qy, qr_size, qr_size)
    c.setFillColor(GREEN_DARK)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(W / 2, qy - 9, "Alle Termine & Anmeldung")
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(W / 2, qy - 18, "bergische-lk.de")

    y -= qr_size + 32
    c.setFillColor(GRAY_LIGHT)
    c.setFont("Helvetica-Oblique", 7.5)
    c.drawCentredString(W / 2, y, "Anmeldung ausschließlich über mybigpoint.tennis.de · DTB-Nummer erforderlich")

    # ── Footer ────────────────────────────────────────────────────
    fh = 40
    c.setFillColor(GREEN_DARK)
    c.rect(0, 0, W, fh, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(margin, fh - 14, "Jean-Charles Das · Organisator")
    c.setFillColor(GOLD)
    c.setFont("Helvetica", 7.5)
    c.drawString(margin, fh - 25, "info@bergische-lk.de")
    c.setFillColor(PALE_GREEN)
    c.setFont("Helvetica", 6.5)
    c.drawString(margin, fh - 36, "Bergische LK-Turniere · Saison 2026")
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 13)
    c.drawRightString(W - margin, fh - 17, "bergische-lk.de")
    c.setFillColor(PALE_GREEN)
    c.setFont("Helvetica", 6.5)
    c.drawRightString(W - margin, fh - 29, "Anmeldung via mybigpoint")

    c.save()
    print(f"Flyer saved: {filepath}")


if __name__ == "__main__":
    create_esv_poster()
    create_esv_flyer()
    print("\nDone! ESV PDFs generated.")
