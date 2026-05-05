"""Druckfertige Visitenkarten 85×55mm im Aurum-Look.

Format: 85×55 mm, 300 DPI = 1004×650 px. 3 mm Beschnitt = +35 px je Seite.
Sicherheitsabstand 4 mm vom Schnittrand für Texte.

Erzeugt:
  print-cards/<slug>-front.png        (Vorderseite)
  print-cards/<slug>-back.png         (Rückseite mit QR)
  print-cards/visitenkarten-druck.pdf (alle Karten als Druck-PDF)
"""
import os
import sys

try:
    import qrcode
    from qrcode.image.styledpil import StyledPilImage
    from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer
    from qrcode.image.styles.colormasks import SolidFillColorMask
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
except ImportError:
    print("Bitte installieren: pip install qrcode[pil]")
    sys.exit(1)

BASE_URL = "https://abdurrahimkaratas-dotcom.github.io/aurum-visitenkarten"

PERSONS = [
    {
        "slug": "khafi",
        "name": "Mustafa Khafi",
        "role": "Geschäftsführer",
        "phone": "+49 711 36083610",
        "email": "m.khafi@aurum-fassadenreinigung.de",
        "url": f"{BASE_URL}/khafi.html",
    },
    {
        "slug": "julia",
        "name": "Julia Schneider",
        "role": "Partnerschaften Wohnungswirtschaft",
        "phone": "+49 711 36083620",
        "email": "j.schneider@aurum-fassadenreinigung.de",
        "url": f"{BASE_URL}/julia.html",
    },
    {
        "slug": "cornelia",
        "name": "Cornelia Jöge",
        "role": "Bereichsleiterin Nord",
        "phone": "+49 511 51512250",
        "phone2": "+49 151 10393469",
        "email": "c.joege@aurum-fassadenreinigung.de",
        "url": f"{BASE_URL}/cornelia.html",
    },
]

# Farben (extrahiert von der Aurum-Webseite)
PETROL = (0, 70, 81)
PETROL_DARK = (0, 45, 53)
GOLD = (218, 176, 93)
GOLD_DARK = (153, 116, 51)
CREAM = (251, 248, 240)
INK = (0, 32, 37)
GREY = (74, 90, 93)
LIGHT_TEAL = (183, 216, 209)
WHITE = (255, 255, 255)

# Maße
DPI = 300
MM = DPI / 25.4
W = round(85 * MM)        # 1004 px
H = round(55 * MM)        # 650 px
BLEED = round(3 * MM)     # 35 px
SAFE = round(4 * MM)      # 47 px
W_BLEED = W + 2 * BLEED   # 1074 px
H_BLEED = H + 2 * BLEED   # 720 px

ROOT = os.path.dirname(__file__)
OUT_DIR = os.path.join(ROOT, "print-cards")
LOGO_PATH = os.path.join(ROOT, "images", "aurum-logo.png")
os.makedirs(OUT_DIR, exist_ok=True)


def font(name: str, size: int):
    paths = [name, f"C:/Windows/Fonts/{name}"]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def text_w(draw, text, fnt):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    return bbox[2] - bbox[0]


def make_qr(url: str, size_px: int, fg=PETROL_DARK, bg=WHITE, with_logo=True):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=20,
        border=1,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(radius_ratio=0.85),
        color_mask=SolidFillColorMask(back_color=bg, front_color=fg),
    ).convert("RGB")
    img = img.resize((size_px, size_px), Image.LANCZOS)

    if with_logo and os.path.exists(LOGO_PATH):
        logo = Image.open(LOGO_PATH).convert("RGBA")
        target = int(size_px * 0.22)
        ratio = target / max(logo.size)
        logo = logo.resize((int(logo.size[0]*ratio), int(logo.size[1]*ratio)), Image.LANCZOS)
        pad = 12
        tile = Image.new("RGB", (logo.size[0]+pad*2, logo.size[1]+pad*2), bg)
        cx, cy = size_px // 2, size_px // 2
        img.paste(tile, (cx - tile.size[0]//2, cy - tile.size[1]//2))
        img.paste(logo, (cx - logo.size[0]//2, cy - logo.size[1]//2), logo)
    return img


def render_front(p: dict) -> Image.Image:
    """Vorderseite: Petrol-Topbar, Cream-Body, Name + Kontakt + QR rechts."""
    card = Image.new("RGB", (W_BLEED, H_BLEED), CREAM)
    draw = ImageDraw.Draw(card)

    # Petrol-Header oben (12 mm Höhe)
    header_h = round(12 * MM) + BLEED
    draw.rectangle([0, 0, W_BLEED, header_h], fill=PETROL_DARK)

    # Gold-Akzent oben rechts (radial-ähnlich mit konzentrischen Ringen)
    accent = Image.new("RGBA", (W_BLEED, header_h), (0, 0, 0, 0))
    ad = ImageDraw.Draw(accent)
    cx, cy = W_BLEED - round(20 * MM), header_h // 2
    for r in range(round(40 * MM), 0, -8):
        a = int(15 * (1 - r / (40 * MM)))
        ad.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(218, 176, 93, a))
    card.paste(accent, (0, 0), accent)

    # Goldene Zier-Linie unter Petrol-Header
    draw.rectangle([0, header_h, W_BLEED, header_h + 3], fill=GOLD)

    # AURUM Schriftzug zentriert im Petrol-Header
    aurum_font = font("georgiab.ttf", 64)
    sub_font = font("seguisb.ttf", 18)
    aurum = "AURUM"
    aw = text_w(draw, aurum, aurum_font)
    ax = (W_BLEED - aw) // 2
    ay = BLEED + 6
    draw.text((ax, ay), aurum, fill=WHITE, font=aurum_font)
    sub = "FASSADENREINIGUNG"
    sw = text_w(draw, sub, sub_font)
    draw.text(((W_BLEED - sw) // 2, ay + 70), sub, fill=GOLD, font=sub_font)

    # ----- Body -----
    body_top = header_h + round(6 * MM)
    left_pad = BLEED + SAFE
    right_pad = BLEED + SAFE

    # QR rechts unten
    qr_size = round(28 * MM)
    qr_x = W_BLEED - right_pad - qr_size
    qr_y = H_BLEED - BLEED - SAFE - qr_size
    qr = make_qr(p["url"], qr_size, fg=PETROL_DARK, bg=WHITE)
    card.paste(qr, (qr_x, qr_y))

    # SCAN-Label über QR
    scan_font = font("seguisb.ttf", 14)
    scan_text = "SCAN MICH"
    sw2 = text_w(draw, scan_text, scan_font)
    draw.text((qr_x + (qr_size - sw2) // 2, qr_y - 22),
              scan_text, fill=GOLD_DARK, font=scan_font)

    # Texte links (Name + Kontakt)
    text_x = left_pad
    text_w_avail = qr_x - left_pad - round(4 * MM)

    name_font = font("georgiab.ttf", 54)
    role_font = font("seguisb.ttf", 18)
    label_font = font("seguisb.ttf", 13)
    value_font = font("seguisb.ttf", 19)
    url_font = font("seguisb.ttf", 17)

    # Name
    draw.text((text_x, body_top), p["name"], fill=PETROL_DARK, font=name_font)
    # Goldene Linie unter Name
    rule_y = body_top + 64
    draw.rectangle([text_x, rule_y, text_x + round(14 * MM), rule_y + 2], fill=GOLD)
    # Rolle
    draw.text((text_x, rule_y + 12), p["role"].upper(),
              fill=GOLD_DARK, font=role_font)

    # Kontakt
    contacts = [("TELEFON", p["phone"])]
    if "phone2" in p:
        contacts.append(("MOBIL", p["phone2"]))
    contacts.append(("E-MAIL", p["email"]))

    cy = rule_y + round(13 * MM)
    line_h = round(7 * MM) if "phone2" in p else round(8 * MM)
    for label, value in contacts:
        draw.text((text_x, cy), label, fill=GOLD_DARK, font=label_font)
        draw.text((text_x, cy + 16), value, fill=PETROL_DARK, font=value_font)
        cy += line_h + 4

    # URL ganz unten links
    url_y = H_BLEED - BLEED - SAFE - 22
    draw.text((text_x, url_y), "aurum-fassadenreinigung.de",
              fill=GOLD_DARK, font=url_font)

    return card


def render_back(p: dict) -> Image.Image:
    """Rückseite: kompletter Petrol-Hintergrund mit großem QR-Code."""
    card = Image.new("RGB", (W_BLEED, H_BLEED), PETROL_DARK)
    draw = ImageDraw.Draw(card)

    # Subtiler Lichtschein-Effekt oben links
    glow = Image.new("RGBA", (W_BLEED, H_BLEED), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for r in range(round(45 * MM), 0, -10):
        a = int(50 * (1 - r / (45 * MM)))
        gd.ellipse([-r, -r, r, r], fill=(218, 176, 93, a))
    card.paste(glow, (0, 0), glow)

    # Goldlinien oben & unten
    draw.rectangle([0, 0, W_BLEED, 4], fill=GOLD)
    draw.rectangle([0, H_BLEED - 4, W_BLEED, H_BLEED], fill=GOLD)

    # ----- QR-Block links -----
    qr_size = round(36 * MM)
    qr_pad = round(4 * MM)
    qr_card_size = qr_size + qr_pad * 2

    # weißes Cardlet als Hintergrund
    qr_card = Image.new("RGB", (qr_card_size, qr_card_size), WHITE)
    qr = make_qr(p["url"], qr_size, fg=PETROL_DARK, bg=WHITE)
    qr_card.paste(qr, (qr_pad, qr_pad))

    qr_x = BLEED + SAFE
    qr_y = (H_BLEED - qr_card_size) // 2
    card.paste(qr_card, (qr_x, qr_y))

    # ----- Text rechts -----
    text_x = qr_x + qr_card_size + round(5 * MM)

    # AURUM klein oben
    brand_font = font("georgiab.ttf", 30)
    sub_small = font("seguisb.ttf", 13)
    draw.text((text_x, qr_y + 4), "AURUM", fill=WHITE, font=brand_font)
    draw.text((text_x, qr_y + 42), "FASSADENREINIGUNG", fill=GOLD, font=sub_small)

    # Goldene Linie
    draw.rectangle([text_x, qr_y + 70, text_x + round(12 * MM), qr_y + 72], fill=GOLD)

    # Headline "Digitale Visitenkarte"
    title_font = font("georgiab.ttf", 36)
    draw.text((text_x, qr_y + 86), "Digitale", fill=WHITE, font=title_font)
    draw.text((text_x, qr_y + 124), "Visitenkarte", fill=GOLD, font=title_font)

    # Name in caps
    name_font = font("seguisb.ttf", 14)
    draw.text((text_x, qr_y + 178), p["name"].upper(), fill=LIGHT_TEAL, font=name_font)

    # Anweisung
    body_font = font("seguisb.ttf", 16)
    instructions = [
        "QR-Code scannen",
        "und Kontakt direkt im",
        "Adressbuch speichern.",
    ]
    iy = qr_y + 208
    for line in instructions:
        draw.text((text_x, iy), line, fill=WHITE, font=body_font)
        iy += 22

    return card


def main():
    pdf_pages = []
    print(f"Format: {W}x{H} px (85x55 mm) + {BLEED} px Beschnitt = {W_BLEED}x{H_BLEED} px @ 300 DPI\n")

    for p in PERSONS:
        front = render_front(p)
        back = render_back(p)
        front_path = os.path.join(OUT_DIR, f"{p['slug']}-front.png")
        back_path = os.path.join(OUT_DIR, f"{p['slug']}-back.png")
        front.save(front_path, "PNG", dpi=(DPI, DPI), optimize=True)
        back.save(back_path, "PNG", dpi=(DPI, DPI), optimize=True)
        print(f"  -> {front_path}")
        print(f"  -> {back_path}")
        pdf_pages.append(front)
        pdf_pages.append(back)

    pdf_path = os.path.join(OUT_DIR, "visitenkarten-druck.pdf")
    pdf_pages[0].save(
        pdf_path, "PDF",
        save_all=True,
        append_images=pdf_pages[1:],
        resolution=float(DPI),
    )
    print(f"\nFertig — Druck-PDF: {pdf_path}")


if __name__ == "__main__":
    main()
