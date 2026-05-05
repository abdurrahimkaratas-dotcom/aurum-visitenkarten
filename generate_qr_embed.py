"""Erzeugt schlanke QR-Codes für die Einbettung in die digitalen Visitenkarten.
Kein Text-Label, nur QR + Aurum-Logo in der Mitte. Speichert als embed-<slug>.png.
"""
import os
import sys

try:
    import qrcode
    from qrcode.image.styledpil import StyledPilImage
    from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer
    from qrcode.image.styles.colormasks import SolidFillColorMask
    from PIL import Image
except ImportError:
    print("pip install qrcode[pil]")
    sys.exit(1)

BASE = "https://splendorous-starship-7e8134.netlify.app/visitenkarten"

CARDS = [
    ("khafi",    f"{BASE}/khafi.html"),
    ("julia",    f"{BASE}/julia.html"),
    ("cornelia", f"{BASE}/cornelia.html"),
    ("holger",   f"{BASE}/holger.html"),
    ("abdul",    f"{BASE}/abdul.html"),
]

PETROL = (19, 54, 56)
WHITE = (255, 255, 255)

ROOT = os.path.dirname(__file__)
OUT_DIR = os.path.join(ROOT, "qr")
LOGO = os.path.join(ROOT, "images", "aurum-logo.png")
os.makedirs(OUT_DIR, exist_ok=True)

SIZE = 600  # Pixel — auf dem Display 180px gerendert, 3x für Retina


def make(url: str, out: str):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=20,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(radius_ratio=0.85),
        color_mask=SolidFillColorMask(back_color=WHITE, front_color=PETROL),
    ).convert("RGB").resize((SIZE, SIZE), Image.LANCZOS)

    if os.path.exists(LOGO):
        logo = Image.open(LOGO).convert("RGBA")
        target = int(SIZE * 0.22)
        ratio = target / max(logo.size)
        logo = logo.resize((int(logo.size[0]*ratio), int(logo.size[1]*ratio)), Image.LANCZOS)
        pad = 16
        tile = Image.new("RGB", (logo.size[0]+pad*2, logo.size[1]+pad*2), WHITE)
        cx, cy = SIZE // 2, SIZE // 2
        img.paste(tile, (cx - tile.size[0]//2, cy - tile.size[1]//2))
        img.paste(logo, (cx - logo.size[0]//2, cy - logo.size[1]//2), logo)

    img.save(out, "PNG", optimize=True)
    print(f"  -> {out}")


def main():
    for slug, url in CARDS:
        make(url, os.path.join(OUT_DIR, f"embed-{slug}.png"))


if __name__ == "__main__":
    main()
