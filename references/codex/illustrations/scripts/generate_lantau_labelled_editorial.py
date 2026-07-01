#!/usr/bin/env python3
"""
Generate a labelled editorial side-profile illustration from the DEM skyline.

This is an art-directed derivative of the DEM skyline, intentionally closer to
the supplied nineteenth-century engraving reference than a strict GIS plot.
"""

from __future__ import annotations

import csv
import html
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).resolve().parent
CSV_PATH = OUT / "lantau-projected-skyline.csv"
SONGTI = Path("/System/Library/Fonts/Supplemental/Songti.ttc")

WIDTH = 12000
HEIGHT = 5250
BASELINE = 3820
TOP = 1520
LEFT_PAD = 180
RIGHT_PAD = 180

LANDMARKS = [
    {"zh": "大澳", "en": "Tai O", "elev": "4 m", "lon": 113.862, "label_y": 1080, "label_dx": -120},
    {"zh": "鳳凰山", "en": "Lantau Peak", "elev": "934 m", "lon": 113.921, "label_y": 340, "label_dx": 0},
    {"zh": "大東山", "en": "Sunset Peak", "elev": "869 m", "lon": 113.958, "label_y": 560, "label_dx": 140},
    {"zh": "二東山", "en": "Yi Tung Shan", "elev": "747 m", "lon": 113.974, "label_y": 730, "label_dx": 250},
    {"zh": "蓮花山", "en": "Lin Fa Shan", "elev": "766 m", "lon": 113.995, "label_y": 620, "label_dx": 340},
    {"zh": "梅窩", "en": "Mui Wo", "elev": "6 m", "lon": 114.002, "label_y": 1040, "label_dx": 470},
    {"zh": "老虎頭", "en": "Lo Fu Tau", "elev": "465 m", "lon": 114.021, "label_y": 850, "label_dx": -40},
    {"zh": "愉景灣", "en": "Discovery Bay", "elev": "12 m", "lon": 114.016, "label_y": 1160, "label_dx": 650},
]


def load_skyline() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rows = []
    with CSV_PATH.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(
                (
                    float(row["lon"]),
                    float(row["x_m_from_west"]),
                    float(row["skyline_elevation_m"]),
                )
            )
    lon = np.array([r[0] for r in rows], dtype=float)
    x_m = np.array([r[1] for r in rows], dtype=float)
    elev = np.array([r[2] for r in rows], dtype=float)
    return lon, x_m, smooth(elev, 121)


def smooth(values: np.ndarray, window: int) -> np.ndarray:
    kernel = np.hanning(window)
    kernel = kernel / kernel.sum()
    padded = np.pad(values, (window // 2, window // 2), mode="edge")
    return np.convolve(padded, kernel, mode="valid")[: len(values)]


def points_from_skyline(x_m: np.ndarray, elev: np.ndarray, simplify: int = 8) -> list[tuple[float, float]]:
    x = LEFT_PAD + (x_m - x_m.min()) / (x_m.max() - x_m.min()) * (WIDTH - LEFT_PAD - RIGHT_PAD)
    # A controlled vertical scale: recognisable and poster-like, not strict metre-to-pixel.
    y = BASELINE - (elev / elev.max()) ** 0.86 * (BASELINE - TOP)
    pts = list(zip(x[::simplify].tolist(), y[::simplify].tolist()))
    if pts[-1][0] < WIDTH - RIGHT_PAD:
        pts.append((WIDTH - RIGHT_PAD, BASELINE))
    return pts


def interp_at_lon(lon_values: np.ndarray, x_m: np.ndarray, elev: np.ndarray, lon: float) -> tuple[float, float]:
    x = np.interp(lon, lon_values, x_m)
    e = np.interp(lon, lon_values, elev)
    x_px = LEFT_PAD + (x - x_m.min()) / (x_m.max() - x_m.min()) * (WIDTH - LEFT_PAD - RIGHT_PAD)
    y_px = BASELINE - (e / elev.max()) ** 0.86 * (BASELINE - TOP)
    return x_px, y_px


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(SONGTI), size=size)


def draw_centred_text(draw: ImageDraw.ImageDraw, xy: tuple[float, float], text: str, fnt, fill=(20, 20, 20)):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    draw.text((xy[0] - (bbox[2] - bbox[0]) / 2, xy[1]), text, font=fnt, fill=fill)


def mountain_mask(points: list[tuple[float, float]]) -> Image.Image:
    mask = Image.new("L", (WIDTH, HEIGHT), 0)
    draw = ImageDraw.Draw(mask)
    polygon = [(0, BASELINE)] + points + [(WIDTH, BASELINE)]
    draw.polygon([(round(x), round(y)) for x, y in polygon], fill=255)
    return mask


def draw_art_png(lon: np.ndarray, x_m: np.ndarray, elev: np.ndarray, points: list[tuple[float, float]]) -> None:
    img = Image.new("RGB", (WIDTH, HEIGHT), (252, 251, 248))
    draw = ImageDraw.Draw(img)
    mask = mountain_mask(points)

    # Mountain body.
    body = Image.new("RGB", (WIDTH, HEIGHT), (18, 18, 17))
    img.paste(body, mask=mask)

    # Engraving lines clipped to mountain.
    line_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    ldraw = ImageDraw.Draw(line_layer)
    for offset in range(120, 1820, 115):
        ridge = []
        phase = offset * 0.009
        for x, y in points:
            wave = math.sin(x * 0.0028 + phase) * 28 + math.sin(x * 0.0009 + phase) * 42
            ridge.append((x, y + offset + wave))
        ldraw.line([(round(x), round(y)) for x, y in ridge], fill=(245, 244, 239, 190), width=7)

    # Diagonal etched slope strokes.
    for i in range(150):
        x0 = 400 + i * 128
        amp = 180 + (i % 7) * 28
        ldraw.line(
            [
                (x0, BASELINE - 180 - (i % 11) * 82),
                (x0 + 260 + (i % 5) * 36, BASELINE - 760 - amp),
            ],
            fill=(250, 249, 244, 95),
            width=3,
        )
    for i in range(120):
        x0 = 520 + i * 94
        y0 = BASELINE - 260 - (i % 17) * 105
        length = 120 + (i % 9) * 24
        angle = -0.55 + (i % 6) * 0.12
        ldraw.line(
            [
                (x0, y0),
                (x0 + math.cos(angle) * length, y0 + math.sin(angle) * length),
            ],
            fill=(250, 249, 244, 90),
            width=3,
        )
    line_alpha = Image.composite(line_layer, Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0)), mask)
    img = Image.alpha_composite(img.convert("RGBA"), line_alpha).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Coastline and water.
    draw.line([(0, BASELINE), (WIDTH, BASELINE)], fill=(14, 14, 14), width=10)
    for i in range(34):
        y = BASELINE + 70 + i * 30
        margin = 140 + i * 35
        alpha = max(20, 145 - i * 4)
        colour = (alpha, alpha, alpha)
        draw.line([(margin, y), (WIDTH - margin, y + math.sin(i) * 5)], fill=colour, width=max(1, 5 - i // 9))

    # Labels and leader lines.
    zh_font = font(132)
    en_font = font(86)
    small_font = font(78)
    for lm in LANDMARKS:
        x, y = interp_at_lon(lon, x_m, elev, lm["lon"])
        label_x = x + lm["label_dx"]
        label_y = lm["label_y"]
        dot_y = max(label_y + 520, y - 74)
        draw.line([(label_x, label_y + 320), (x, dot_y)], fill=(80, 80, 80), width=4)
        draw.ellipse((x - 18, dot_y - 18, x + 18, dot_y + 18), fill=(5, 5, 5))
        draw_centred_text(draw, (label_x, label_y), lm["zh"], zh_font)
        draw_centred_text(draw, (label_x, label_y + 150), lm["en"], en_font)
        draw_centred_text(draw, (label_x, label_y + 270), lm["elev"], small_font)

    img.save(OUT / "lantau-labelled-editorial-side-12000.png", quality=95)
    preview = img.copy()
    preview.thumbnail((1600, 700))
    preview.save(OUT / "lantau-labelled-editorial-side-preview.png", quality=95)


def svg_path(points: list[tuple[float, float]]) -> str:
    if not points:
        return ""
    parts = [f"M {points[0][0]:.1f} {points[0][1]:.1f}"]
    for x, y in points[1:]:
        parts.append(f"L {x:.1f} {y:.1f}")
    return " ".join(parts)


def write_svg(lon: np.ndarray, x_m: np.ndarray, elev: np.ndarray, points: list[tuple[float, float]]) -> None:
    top = svg_path(points)
    polygon = f"M 0 {BASELINE} {top[1:]} L {WIDTH} {BASELINE} Z"
    lines = []
    for offset in range(120, 1820, 115):
        ridge = []
        phase = offset * 0.009
        for x, y in points:
            wave = math.sin(x * 0.0028 + phase) * 28 + math.sin(x * 0.0009 + phase) * 42
            ridge.append((x, y + offset + wave))
        lines.append(f'<path d="{svg_path(ridge)}" fill="none" stroke="#f5f4ef" stroke-width="7" opacity="0.74"/>')

    labels = []
    for lm in LANDMARKS:
        x, y = interp_at_lon(lon, x_m, elev, lm["lon"])
        label_x = x + lm["label_dx"]
        label_y = lm["label_y"]
        dot_y = max(label_y + 520, y - 74)
        labels.append(
            f'''<g text-anchor="middle" fill="#151515" font-family="Songti SC, STSong, serif">
  <line x1="{label_x:.1f}" y1="{label_y + 320:.1f}" x2="{x:.1f}" y2="{dot_y:.1f}" stroke="#555" stroke-width="4"/>
  <circle cx="{x:.1f}" cy="{dot_y:.1f}" r="18" fill="#050505"/>
  <text x="{label_x:.1f}" y="{label_y + 112:.1f}" font-size="132">{html.escape(lm["zh"])}</text>
  <text x="{label_x:.1f}" y="{label_y + 236:.1f}" font-size="86">{html.escape(lm["en"])}</text>
  <text x="{label_x:.1f}" y="{label_y + 350:.1f}" font-size="78">{html.escape(lm["elev"])}</text>
</g>'''
        )

    water = []
    for i in range(34):
        y = BASELINE + 70 + i * 30
        margin = 140 + i * 35
        opacity = max(0.12, 0.55 - i * 0.014)
        water.append(
            f'<line x1="{margin}" y1="{y:.1f}" x2="{WIDTH - margin}" y2="{y + math.sin(i) * 5:.1f}" stroke="#222" stroke-width="{max(1, 5 - i // 9)}" opacity="{opacity:.2f}"/>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
<rect width="100%" height="100%" fill="#fcfbf8"/>
<defs>
  <clipPath id="mountain-clip"><path d="{polygon}"/></clipPath>
</defs>
<path d="{polygon}" fill="#121211"/>
<g clip-path="url(#mountain-clip)">
{chr(10).join(lines)}
</g>
<line x1="0" y1="{BASELINE}" x2="{WIDTH}" y2="{BASELINE}" stroke="#0e0e0e" stroke-width="10"/>
<g>{chr(10).join(water)}</g>
{chr(10).join(labels)}
</svg>
'''
    (OUT / "lantau-labelled-editorial-side.svg").write_text(svg, encoding="utf-8")


def main() -> None:
    lon, x_m, elev = load_skyline()
    points = points_from_skyline(x_m, elev)
    draw_art_png(lon, x_m, elev, points)
    write_svg(lon, x_m, elev, points)


if __name__ == "__main__":
    main()
