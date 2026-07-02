#!/usr/bin/env python3
"""Compose the 1200x630 OG image: fly-mode + satellite hero + brand overlay (HKS-28).

The hero is the in-app Snapshot (📷) taken in fly mode over the satellite surface
(it renders the WebGL scene only — no UI chrome). Usage, from any checkout:

    python3 -m venv venv && venv/bin/pip install Pillow
    venv/bin/python assets/brand/compose-og.py path/to/hero.png

All repo paths are derived from this file's location, so it runs anywhere; only the
hero PNG is passed in (or drop it at assets/brand/og-hero.png as the default).
Output → 3d-viewer/og-image.jpg (1200x630).
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# repo root = two levels up from this file (assets/brand/compose-og.py)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ICON = os.path.join(REPO, "assets/brand/hongkong-sandbox-icon-v2-rounded.png")
OUT  = os.path.join(REPO, "3d-viewer/og-image.jpg")
HERO = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO, "assets/brand/og-hero.png")
if not os.path.exists(HERO):
    sys.exit(f"hero image not found: {HERO}\n"
             f"usage: python {os.path.basename(__file__)} <hero.png>  "
             f"(a fly-mode + satellite Snapshot from the app)")

W, H = 1200, 630

def font(paths, size):
    for p in paths:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except Exception: pass
    return ImageFont.load_default()

LAT_BOLD = ["/System/Library/Fonts/Supplemental/Arial Bold.ttf"]
CJK      = ["/System/Library/Fonts/PingFang.ttc", "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"]
LAT_REG  = ["/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Helvetica.ttc"]

# --- hero: crop a landscape band featuring the plane + airport + mountains ---
hero = Image.open(HERO).convert("RGB")           # 1560 x 3376 (portrait)
hw, hh = hero.size
band_h = round(hw / (W / H))                      # 1560 / 1.904 = ~819
top = 1250                                         # plane ~y1520, airport ~y1750
top = max(0, min(top, hh - band_h))
hero = hero.crop((0, top, hw, top + band_h)).resize((W, H), Image.LANCZOS)

img = hero.copy()

# --- bottom scrim for text legibility (transparent -> dark) ---
scrim = Image.new("L", (1, H), 0)
for y in range(H):
    t = max(0.0, (y - H * 0.42) / (H * 0.58))     # start ~42% down
    scrim.putpixel((0, y), int(210 * (t ** 1.4)))
scrim = scrim.resize((W, H))
dark = Image.new("RGB", (W, H), (5, 8, 12))
img = Image.composite(dark, img, scrim)

# --- accent hairline along the very bottom ---
d = ImageDraw.Draw(img, "RGBA")
d.rectangle([0, H - 5, W, H], fill=(53, 203, 160, 235))   # brand #35cba0

# --- brand icon badge (bottom-left) ---
pad = 50
isz = 112
icon = Image.open(ICON).convert("RGBA").resize((isz, isz), Image.LANCZOS)
# soft shadow
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(sh).rounded_rectangle([pad-3, H-pad-isz-3, pad+isz+3, H-pad+3-6], 26, fill=(0,0,0,120))
sh = sh.filter(ImageFilter.GaussianBlur(7))
img = Image.alpha_composite(img.convert("RGBA"), sh)
img.paste(icon, (pad, H - pad - isz - 6), icon)
d = ImageDraw.Draw(img, "RGBA")

tx = pad + isz + 26
f_title = font(LAT_BOLD, 46)
f_cjk   = font(CJK, 33)
f_tag   = font(LAT_REG, 22)

def text_sh(xy, s, f, fill, sh_alpha=170):
    d.text((xy[0]+1, xy[1]+2), s, font=f, fill=(0, 0, 0, sh_alpha))
    d.text(xy, s, font=f, fill=fill)

# vertical stack, bottom-aligned with the icon
y = H - pad - isz - 6
text_sh((tx, y + 2),  "Hong Kong Sandbox", f_title, (255, 255, 255, 255))
text_sh((tx, y + 55), "香港沙盒", f_cjk, (53, 203, 160, 255))
text_sh((tx + f_cjk.getbbox("香港沙盒")[2] + 14, y + 62),
        "· Interactive 3D Hong Kong", f_tag, (207, 216, 224, 255))
text_sh((tx, y + 98),
        "Real LiDAR terrain · live HKO weather, tides & typhoons · fly it yourself",
        f_tag, (176, 187, 198, 255))

# --- attribution (bottom-right) ---
f_attr = font(LAT_REG, 15)
attr = "3D from real DEMs · satellite © Esri, Maxar, Earthstar Geographics"
aw = d.textlength(attr, font=f_attr)
d.text((W - pad - aw + 1, H - 34 + 1), attr, font=f_attr, fill=(0, 0, 0, 150))
d.text((W - pad - aw, H - 34), attr, font=f_attr, fill=(200, 208, 216, 220))

img.convert("RGB").save(OUT, "JPEG", quality=88, optimize=True)
print("wrote", OUT, os.path.getsize(OUT), "bytes", Image.open(OUT).size)
