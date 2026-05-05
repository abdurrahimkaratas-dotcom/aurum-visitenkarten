"""A4-Druckbögen für Hausdrucker erzeugen.

Layout: 2 Spalten × 5 Zeilen = 10 Karten pro A4-Bogen, mit Schnittmarken.
Erzeugt:
  print-cards/a4-vorderseiten.pdf  — alle Vorderseiten auf A4-Bögen
  print-cards/a4-rueckseiten.pdf   — alle Rückseiten auf A4-Bögen (gespiegelt für Doppelseitendruck)
  print-cards/a4-mix.pdf           — alle 3 Personen je 1× Vorder- und Rückseite gemischt (zum Probedruck)

Drucken-Einstellung: A4, "Originalgröße" / "Tatsächliche Größe" / "100 %",
Skalierung NICHT aktivieren. Sonst stimmen die 85×55 mm nicht.
"""
import os
import sys

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("Bitte installieren: pip install pillow")
    sys.exit(1)

# A4: 210 × 297 mm, 300 DPI
DPI = 300
MM = DPI / 25.4
A4_W = round(210 * MM)   # 2480
A4_H = round(297 * MM)   # 3508
CARD_W = round(85 * MM)  # 1004
CARD_H = round(55 * MM)  # 650
CROP_LEN = round(3 * MM) # 35 — Länge der Schnittmarke

# 2 Spalten × 5 Zeilen
COLS = 2
ROWS = 5
GAP_X = round(2 * MM)
GAP_Y = round(2 * MM)
GRID_W = COLS * CARD_W + (COLS - 1) * GAP_X
GRID_H = ROWS * CARD_H + (ROWS - 1) * GAP_Y
MARGIN_X = (A4_W - GRID_W) // 2
MARGIN_Y = (A4_H - GRID_H) // 2

ROOT = os.path.dirname(__file__)
PRINT_DIR = os.path.join(ROOT, "print-cards")

PERSONS_FRONT = [
    os.path.join(PRINT_DIR, "khafi-front.png"),
    os.path.join(PRINT_DIR, "holger-front.png"),
    os.path.join(PRINT_DIR, "abdul-front.png"),
    os.path.join(PRINT_DIR, "julia-front.png"),
    os.path.join(PRINT_DIR, "cornelia-front.png"),
]
PERSONS_BACK = [
    os.path.join(PRINT_DIR, "khafi-back.png"),
    os.path.join(PRINT_DIR, "holger-back.png"),
    os.path.join(PRINT_DIR, "abdul-back.png"),
    os.path.join(PRINT_DIR, "julia-back.png"),
    os.path.join(PRINT_DIR, "cornelia-back.png"),
]


def crop_full_bleed(img: Image.Image) -> Image.Image:
    """Beschnittzugabe wegnehmen — zentrum auf 85×55 mm zuschneiden."""
    bleed = (img.width - CARD_W) // 2
    return img.crop((bleed, bleed, bleed + CARD_W, bleed + CARD_H))


def draw_crop_marks(draw, x, y, w, h, length, color=(120, 120, 120), width=2):
    """Vier L-förmige Schnittmarken außerhalb der Karte."""
    off = round(0.5 * MM)
    # oben links
    draw.line([(x - length, y - off), (x - off, y - off)], fill=color, width=width)
    draw.line([(x - off, y - length), (x - off, y - off)], fill=color, width=width)
    # oben rechts
    draw.line([(x + w + off, y - off), (x + w + length, y - off)], fill=color, width=width)
    draw.line([(x + w + off, y - length), (x + w + off, y - off)], fill=color, width=width)
    # unten links
    draw.line([(x - length, y + h + off), (x - off, y + h + off)], fill=color, width=width)
    draw.line([(x - off, y + h + off), (x - off, y + h + length)], fill=color, width=width)
    # unten rechts
    draw.line([(x + w + off, y + h + off), (x + w + length, y + h + off)], fill=color, width=width)
    draw.line([(x + w + off, y + h + off), (x + w + off, y + h + length)], fill=color, width=width)


def make_sheet(images: list[Image.Image], mirrored: bool = False) -> Image.Image:
    """Erzeuge einen A4-Bogen mit bis zu 10 Karten in 2×5 Anordnung."""
    sheet = Image.new("RGB", (A4_W, A4_H), (255, 255, 255))
    draw = ImageDraw.Draw(sheet)

    for idx, img in enumerate(images[:COLS * ROWS]):
        row = idx // COLS
        col = idx % COLS
        if mirrored:
            col = (COLS - 1) - col  # für Rückseite — horizontal spiegeln
        x = MARGIN_X + col * (CARD_W + GAP_X)
        y = MARGIN_Y + row * (CARD_H + GAP_Y)
        sheet.paste(img, (x, y))
        draw_crop_marks(draw, x, y, CARD_W, CARD_H, CROP_LEN)

    # Hinweistext am Fuß
    from PIL import ImageFont
    try:
        f = ImageFont.truetype("C:/Windows/Fonts/seguisb.ttf", 22)
    except OSError:
        f = ImageFont.load_default()
    note = "Drucken auf A4 mit Skalierung 100% / Originalgröße — nicht 'an Seite anpassen'!"
    draw.text((MARGIN_X, A4_H - round(14 * MM)), note, fill=(80, 80, 80), font=f)
    return sheet


def build(images_paths: list[str], out_pdf: str, mirrored=False, copies_per_card=4):
    """Bündele Karten zu A4-Bögen, jede Karte mehrfach."""
    cards = []
    for path in images_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        img = crop_full_bleed(Image.open(path))
        cards.extend([img] * copies_per_card)

    # in 10er-Päckchen verteilen
    sheets = []
    for i in range(0, len(cards), COLS * ROWS):
        sheet = make_sheet(cards[i:i + COLS * ROWS], mirrored=mirrored)
        sheets.append(sheet)
    if not sheets:
        return
    sheets[0].save(
        out_pdf, "PDF",
        save_all=True,
        append_images=sheets[1:],
        resolution=float(DPI),
    )
    print(f"  -> {out_pdf} ({len(sheets)} A4-Bogen, je {COLS*ROWS} Karten)")


def main():
    print(f"A4 = {A4_W}×{A4_H} px @ {DPI} DPI ({A4_W/MM:.0f}×{A4_H/MM:.0f} mm)")
    print(f"Karte = {CARD_W}×{CARD_H} px ({CARD_W/MM:.0f}×{CARD_H/MM:.0f} mm)")
    print(f"Anordnung: {COLS} Spalten × {ROWS} Zeilen = {COLS*ROWS} Karten/Bogen\n")

    out_front = os.path.join(PRINT_DIR, "a4-vorderseiten.pdf")
    out_back  = os.path.join(PRINT_DIR, "a4-rueckseiten.pdf")
    out_mix   = os.path.join(PRINT_DIR, "a4-mix-pruefen.pdf")

    # Standard: 4 Kopien pro Person → 12 Karten gesamt → 2 A4-Bögen
    build(PERSONS_FRONT, out_front, mirrored=False, copies_per_card=4)
    build(PERSONS_BACK, out_back, mirrored=True, copies_per_card=4)

    # Mix-Bogen: je eine Vorder- und Rückseite zum Probedrucken
    mix_paths = []
    for f, b in zip(PERSONS_FRONT, PERSONS_BACK):
        mix_paths.append(f)
        mix_paths.append(b)
    # je 1 Kopie reicht für Probebogen
    cards = [crop_full_bleed(Image.open(p)) for p in mix_paths]
    sheet = make_sheet(cards)
    sheet.save(out_mix, "PDF", resolution=float(DPI))
    print(f"  -> {out_mix} (1 A4-Bogen, je 1× Vorder- und Rückseite zum Probedrucken)")

    print("\nDrucken auf A4: Adobe Reader → Drucken → 'Tatsächliche Größe' / 'Skalierung 100 %'")
    print("Doppelseitig: erst a4-vorderseiten.pdf drucken, Papier wenden (lange Kante), dann a4-rueckseiten.pdf.")


if __name__ == "__main__":
    main()
