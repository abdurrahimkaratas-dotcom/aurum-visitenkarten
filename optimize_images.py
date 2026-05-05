"""WebP-Pipeline für die Visitenkarten-Bilder.

Erzeugt aus jedem Quell-JPEG mehrere WebP-Varianten (responsive srcset)
und optional AVIF wenn pillow-avif-plugin installiert ist.

Pipeline-Konzept aus dem image-optimization-cdn Skill (Custom/Headless-Pfad):
- resize variants
- WebP @ 80% quality (balance Größe/Qualität)
- AVIF @ 60% quality (wenn verfügbar)
- explicit dimensions
"""
import os
import sys
from PIL import Image

try:
    import pillow_avif  # noqa
    HAS_AVIF = True
except ImportError:
    HAS_AVIF = False

ROOT = os.path.dirname(__file__)
IMG_DIR = os.path.join(ROOT, "images")

# Portraits: 3 Varianten für srcset (kleine, mittlere, große Karte)
PORTRAIT_SIZES = [400, 600, 900]

PORTRAITS = ["khafi", "julia", "cornelia"]
LOGO = "aurum-logo"


def save_variants(src_path: str, base_name: str, sizes: list[int]):
    if not os.path.exists(src_path):
        print(f"  ! missing {src_path}")
        return
    img = Image.open(src_path).convert("RGB")
    sw, sh = img.size
    for w in sizes:
        if w > sw:
            continue  # don't upscale
        ratio = w / sw
        new_h = int(sh * ratio)
        scaled = img.resize((w, new_h), Image.LANCZOS)
        # WebP
        webp = os.path.join(IMG_DIR, f"{base_name}-{w}.webp")
        scaled.save(webp, "WEBP", quality=82, method=6)
        size = os.path.getsize(webp)
        print(f"  -> {os.path.basename(webp):30s} {w}x{new_h}  {size//1024} KB")
        # AVIF (optional)
        if HAS_AVIF:
            avif = os.path.join(IMG_DIR, f"{base_name}-{w}.avif")
            scaled.save(avif, "AVIF", quality=60)
            print(f"  -> {os.path.basename(avif):30s} (AVIF)")


def save_logo_webp():
    src = os.path.join(IMG_DIR, "aurum-logo.png")
    if not os.path.exists(src):
        return
    img = Image.open(src)
    out = os.path.join(IMG_DIR, "aurum-logo.webp")
    # Logo hat Transparenz — RGBA halten
    if img.mode == "P":
        img = img.convert("RGBA")
    img.save(out, "WEBP", quality=92, method=6, lossless=False)
    size = os.path.getsize(out)
    print(f"  -> aurum-logo.webp {size//1024} KB")


def main():
    print(f"WebP optimization (AVIF available: {HAS_AVIF})\n")
    print("Portraits:")
    for slug in PORTRAITS:
        src = os.path.join(IMG_DIR, f"{slug}.jpg")
        save_variants(src, slug, PORTRAIT_SIZES)
        print()
    print("Logo:")
    save_logo_webp()


if __name__ == "__main__":
    main()
