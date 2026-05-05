"""Erzeugt QR-Codes für die Visitenkarten im Aurum-Look (Petrol + Gold).

Aufruf:
    python generate_qr.py https://deine-domain.de

Erzeugt:
    qr/qr-uebersicht.png   -> https://deine-domain.de/
    qr/qr-khafi.png        -> https://deine-domain.de/khafi.html
    qr/qr-julia.png        -> https://deine-domain.de/julia.html
    qr/qr-cornelia.png     -> https://deine-domain.de/cornelia.html
"""
import sys
import os

try:
    import qrcode
    from qrcode.image.styledpil import StyledPilImage
    from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer
    from qrcode.image.styles.colormasks import SolidFillColorMask
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Bitte zuerst installieren: pip install qrcode[pil]")
    sys.exit(1)

PETROL = (0, 70, 81)
GOLD   = (218, 176, 93)
WHITE  = (255, 255, 255)

CARDS = [
    ("uebersicht", "visitenkarten/",             "Alle Visitenkarten"),
    ("khafi",      "visitenkarten/khafi.html",   "Mustafa Khafi · Geschäftsführer"),
    ("julia",      "visitenkarten/julia.html",   "Julia Schneider · Partnerschaften"),
    ("cornelia",   "visitenkarten/cornelia.html","Cornelia Jöge · Bereichsleiterin Nord"),
]

def make_qr(url: str, label: str, out: str, logo_path: str | None = None):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=14,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(radius_ratio=0.85),
        color_mask=SolidFillColorMask(back_color=WHITE, front_color=PETROL),
    ).convert("RGB")

    qw, qh = img.size

    # Optional: paste logo in the center
    if logo_path and os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        target = qw // 5
        ratio = target / max(logo.size)
        logo = logo.resize((int(logo.size[0]*ratio), int(logo.size[1]*ratio)), Image.LANCZOS)
        # white tile behind logo
        tile = Image.new("RGB", (logo.size[0]+24, logo.size[1]+24), WHITE)
        bx = (qw - tile.size[0]) // 2
        by = (qh - tile.size[1]) // 2
        img.paste(tile, (bx, by))
        img.paste(logo, ((qw - logo.size[0])//2, (qh - logo.size[1])//2), logo)

    # Card with label below
    pad_x, pad_top, pad_bottom = 60, 60, 110
    card_w = qw + pad_x*2
    card_h = qh + pad_top + pad_bottom
    card = Image.new("RGB", (card_w, card_h), WHITE)
    card.paste(img, (pad_x, pad_top))

    # Gold rule above label
    draw = ImageDraw.Draw(card)
    rule_y = pad_top + qh + 30
    rule_w = 160
    draw.rectangle(
        [(card_w - rule_w)//2, rule_y, (card_w + rule_w)//2, rule_y + 2],
        fill=GOLD,
    )

    # Label text
    try:
        font_large = ImageFont.truetype("seguisb.ttf", 28)  # Segoe UI Semibold (Win)
        font_small = ImageFont.truetype("segoeui.ttf", 22)
    except OSError:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    title_y = rule_y + 18
    bbox = draw.textbbox((0,0), label, font=font_large)
    tw = bbox[2] - bbox[0]
    draw.text(((card_w - tw)//2, title_y), label, fill=PETROL, font=font_large)

    sub = "AURUM FASSADENREINIGUNG"
    bbox2 = draw.textbbox((0,0), sub, font=font_small)
    sw = bbox2[2] - bbox2[0]
    draw.text(((card_w - sw)//2, title_y + 40), sub, fill=GOLD, font=font_small)

    card.save(out, "PNG", optimize=True)
    print(f"  -> {out}")


def main():
    if len(sys.argv) < 2:
        print("Aufruf: python generate_qr.py https://deine-domain.de")
        print("Beispiel: python generate_qr.py https://aurum-cards.netlify.app")
        sys.exit(1)

    base = sys.argv[1].rstrip("/")
    out_dir = os.path.join(os.path.dirname(__file__), "qr")
    os.makedirs(out_dir, exist_ok=True)
    logo = os.path.join(os.path.dirname(__file__), "images", "aurum-logo.png")

    print(f"Erzeuge QR-Codes für {base} ...")
    for slug, path, label in CARDS:
        url = f"{base}/{path}" if path else f"{base}/"
        out = os.path.join(out_dir, f"qr-{slug}.png")
        print(f"{slug}: {url}")
        make_qr(url, label, out, logo)

    print("\nFertig — die PNGs liegen im Ordner qr/. Druckfertig mit transparentem Logo in der Mitte.")


if __name__ == "__main__":
    main()
