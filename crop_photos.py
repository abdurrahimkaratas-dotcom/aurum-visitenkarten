"""Crop the team photos to a face-centered square. Originals -> images/originals/, cropped overwrites the main filenames."""
from PIL import Image
import os
import shutil

IMAGES_DIR = os.path.join(os.path.dirname(__file__), "images")
ORIG_DIR = os.path.join(IMAGES_DIR, "originals")
os.makedirs(ORIG_DIR, exist_ok=True)

# Manually-tuned face center as fraction of source image (x, y)
# All photos share a similar composition (subject in right half, face upper portion).
TARGETS = {
    "julia.jpg":    (0.43, 0.22),
    "cornelia.jpg": (0.44, 0.24),
    "khafi.jpg":    (0.46, 0.24),
}

CROP_SIZE = 1400  # output square size in source pixels (then we keep at full res)

for filename, (fx, fy) in TARGETS.items():
    src = os.path.join(IMAGES_DIR, filename)
    backup = os.path.join(ORIG_DIR, filename)
    if not os.path.exists(backup):
        shutil.copy2(src, backup)
    img = Image.open(backup)
    w, h = img.size
    side = min(w, h, CROP_SIZE)
    cx = int(w * fx)
    # vertical: place face at ~32% from top of the crop
    cy = int(h * fy + side * 0.18)
    left = max(0, min(w - side, cx - side // 2))
    top = max(0, min(h - side, cy - int(side * 0.32)))
    box = (left, top, left + side, top + side)
    cropped = img.crop(box)
    # downscale slightly to keep file size reasonable while staying sharp
    cropped = cropped.resize((900, 900), Image.LANCZOS)
    cropped.save(src, "JPEG", quality=92, optimize=True, progressive=True)
    print(f"{filename}: source {w}x{h}, crop box {box}, output 900x900")

print("Done.")
