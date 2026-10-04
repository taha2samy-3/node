#!/usr/bin/env python3
"""Generate every Secure Runtimes brand asset from one definition.

The mark is a shield cut into three stacked bands (the layers of a container
image) with a check mark knocked out of the top band. The wordmark is set in
Plus Jakarta Sans and converted to outlines, so the SVGs render identically
everywhere (GitHub README, social cards, browsers without the font).

Outputs:
  assets/brand/logo-mark.svg        mark only
  assets/brand/logo-dark.svg        mark + wordmark for dark backgrounds
  assets/brand/logo-light.svg       mark + wordmark for light backgrounds
  assets/brand/banner.svg           README header
  assets/brand/social-preview.png   GitHub social preview (1280x640)
  web/public/favicon.svg, apple-touch-icon.png, icon-192.png, icon-512.png, og-image.png
  web/src/brand/geometry.ts         mark geometry for the dashboard's <LogoMark />

Requirements: fonttools, uharfbuzz, rsvg-convert.
  python assets/brand/generate.py
"""
import os
import subprocess
import urllib.request

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BRAND_DIR = os.path.join(ROOT, "assets", "brand")
PUBLIC_DIR = os.path.join(ROOT, "web", "public")
GEOMETRY_TS = os.path.join(ROOT, "web", "src", "brand", "geometry.ts")

FONT_URL = "https://github.com/google/fonts/raw/main/ofl/plusjakartasans/PlusJakartaSans%5Bwght%5D.ttf"
FONT_CACHE = os.path.join(os.path.expanduser("~"), ".cache", "secure-runtimes-brand", "PlusJakartaSans.ttf")

NAME = ("Secure", "Runtimes")
TAGLINE = "Hardened, signed and scanned container runtimes on Wolfi"
RUNTIMES = ["Node.js", "Python", "Java", "Go", "Bun", "OpenSSL FIPS", "OpenJDK FIPS", "Node.js FIPS"]

# ==========================================
# Palette
# ==========================================
BG_DARK = "#0A0E17"
INK_DARK = "#F8FAFC"       # wordmark on dark backgrounds
MUTED_DARK = "#94A3B8"
ACCENT_DARK = "#00F5A0"
INK_LIGHT = "#0F172A"      # wordmark on light backgrounds
ACCENT_LIGHT = "#059669"
BANDS = [                  # top, middle, bottom band gradients
    ("#7DFFD0", "#00F5A0"),
    ("#00E3A8", "#00C7B4"),
    ("#06B6D4", "#0891B2"),
]

# ==========================================
# Mark geometry (64 x 64)
# ==========================================
SHIELD = ("M30.9 4.4Q32 4 33.1 4.4L53 11.2Q55 11.9 55 14V29.5C55 44.6 45.4 55.9 32 60.5"
          "C18.6 55.9 9 44.6 9 29.5V14Q9 11.9 11 11.2Z")
CHECK = "M25.5 13.5L30 17.5L38.5 9.5"
CHECK_WIDTH = 3.2
CUTS = [(21, 3), (37, 3)]            # (y, height) of the gaps between bands
# Favicon sizes (16-32px) need wider gaps and a heavier check to stay legible
SMALL_CUTS = [(20.25, 4.5), (36.25, 4.5)]
SMALL_CHECK_WIDTH = 4.6
BAND_SPANS = [(0, 22.5), (22.5, 38.5), (38.5, 64)]


def mark_svg(prefix="sr", x=0, y=0, size=64, small=False):
    """The mark as an SVG fragment placed at (x, y) with the given size."""
    scale = size / 64
    cut_list, check_width = (SMALL_CUTS, SMALL_CHECK_WIDTH) if small else (CUTS, CHECK_WIDTH)
    defs = []
    for i, (start, end) in enumerate(BANDS):
        top, bottom = BAND_SPANS[i]
        defs.append(
            f'<linearGradient id="{prefix}-band{i}" x1="9" y1="{top}" x2="55" y2="{bottom}" gradientUnits="userSpaceOnUse">'
            f'<stop offset="0" stop-color="{start}"/><stop offset="1" stop-color="{end}"/></linearGradient>'
        )
    cuts = "".join(f'<rect x="0" y="{cy}" width="64" height="{h}" fill="#000"/>' for cy, h in cut_list)
    defs.append(
        f'<mask id="{prefix}-cut" maskUnits="userSpaceOnUse" x="0" y="0" width="64" height="64">'
        f'<rect width="64" height="64" fill="#fff"/>{cuts}'
        f'<path d="{CHECK}" fill="none" stroke="#000" stroke-width="{check_width}" stroke-linecap="round" stroke-linejoin="round"/></mask>'
        f'<clipPath id="{prefix}-shield"><path d="{SHIELD}"/></clipPath>'
    )
    bands = "".join(
        f'<rect x="0" y="{top}" width="64" height="{bottom - top}" fill="url(#{prefix}-band{i})"/>'
        for i, (top, bottom) in enumerate(BAND_SPANS)
    )
    return (
        f'<defs>{"".join(defs)}</defs>'
        f'<g transform="translate({x} {y}) scale({scale})">'
        f'<g clip-path="url(#{prefix}-shield)" mask="url(#{prefix}-cut)">{bands}</g></g>'
    )


# ==========================================
# Text to outlines
# ==========================================
class Typesetter:
    def __init__(self, path):
        self.blob = hb.Blob.from_file_path(path)
        self.source = path
        self.instances = {}

    def _instance(self, weight):
        if weight not in self.instances:
            self.instances[weight] = instantiateVariableFont(TTFont(self.source), {"wght": weight})
        return self.instances[weight]

    def outline(self, text, weight, size, x=0.0, baseline=0.0):
        """SVG path data for text at the given weight/size, plus its advance width."""
        font = hb.Font(hb.Face(self.blob))
        font.set_variations({"wght": weight})
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(font, buf, {"kern": True, "liga": True})

        static = self._instance(weight)
        glyph_set = static.getGlyphSet()
        order = static.getGlyphOrder()
        scale = size / static["head"].unitsPerEm
        pen = SVGPathPen(glyph_set)
        cursor = 0
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            gx = x + (cursor + pos.x_offset) * scale
            gy = baseline - pos.y_offset * scale
            glyph_set[order[info.codepoint]].draw(TransformPen(pen, (scale, 0, 0, -scale, gx, gy)))
            cursor += pos.x_advance
        return pen.getCommands(), cursor * scale

    def width(self, text, weight, size):
        return self.outline(text, weight, size)[1]


def svg(width, height, body, title):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'role="img" aria-label="{title}"><title>{title}</title>{body}</svg>\n'
    )


def wordmark(ts, x, baseline, size, ink, accent):
    first, first_w = ts.outline(NAME[0], 800, size, x, baseline)
    space = ts.width(" ", 800, size) * 0.8
    second, second_w = ts.outline(NAME[1], 800, size, x + first_w + space, baseline)
    body = f'<path d="{first}" fill="{ink}"/><path d="{second}" fill="{accent}"/>'
    return body, first_w + space + second_w


def horizontal_logo(ts, ink, accent):
    size = 36
    cap = 0.745 * size
    text, text_w = wordmark(ts, 64 + 16, 32 + cap / 2, size, ink, accent)
    width = round(64 + 16 + text_w + 6)
    return svg(width, 64, mark_svg("sr") + text, "Secure Runtimes")


def chips(ts, labels, x, y, size, height, gap, fill, stroke, ink):
    parts, cursor = [], x
    for label in labels:
        d, w = ts.outline(label, 600, size, 0, 0)
        pad = height * 0.55
        chip_w = w + 2 * pad
        baseline = y + height / 2 + 0.745 * size / 2
        parts.append(
            f'<rect x="{cursor:.1f}" y="{y}" width="{chip_w:.1f}" height="{height}" rx="{height / 2}" fill="{fill}" stroke="{stroke}"/>'
            f'<path d="{d}" fill="{ink}" transform="translate({cursor + pad:.1f} {baseline:.1f})"/>'
        )
        cursor += chip_w + gap
    return "".join(parts), cursor - gap - x


def backdrop(width, height, glow_x, glow_y, glow_r):
    """Dark background with a soft brand glow and a faint grid."""
    return (
        f'<defs><radialGradient id="glow" cx="{glow_x}" cy="{glow_y}" r="{glow_r}" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="{ACCENT_DARK}" stop-opacity=".16"/><stop offset="1" stop-color="{ACCENT_DARK}" stop-opacity="0"/></radialGradient>'
        f'<pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">'
        f'<path d="M32 0H0V32" fill="none" stroke="#FFFFFF" stroke-opacity=".035"/></pattern></defs>'
        f'<rect width="{width}" height="{height}" fill="{BG_DARK}"/>'
        f'<rect width="{width}" height="{height}" fill="url(#grid)"/>'
        f'<rect width="{width}" height="{height}" fill="url(#glow)"/>'
    )


def banner(ts):
    width, height = 1280, 320
    mark_size = 128
    title_size = 64
    cap = 0.745 * title_size
    text_x = 96 + mark_size + 40
    title, _ = wordmark(ts, text_x, 140 + cap / 2 - 10, title_size, INK_DARK, ACCENT_DARK)
    tagline, _ = ts.outline(TAGLINE, 500, 26, text_x, 196)
    chip_row, _ = chips(ts, RUNTIMES, text_x, 222, 15, 30, 8, "#111827", "#1F2937", "#CBD5E1")
    body = (
        backdrop(width, height, 160, 160, 420)
        + mark_svg("sr", 96, (height - mark_size) / 2, mark_size)
        + title
        + f'<path d="{tagline}" fill="{MUTED_DARK}"/>'
        + chip_row
    )
    return svg(width, height, body, "Secure Runtimes")


def social_card(ts, width=1280, height=640):
    mark_size = 160
    title_size = 84
    cap = 0.745 * title_size
    _, title_w = wordmark(ts, 0, 0, title_size, INK_DARK, ACCENT_DARK)
    title_x = (width - title_w) / 2
    title, _ = wordmark(ts, title_x, 330 + cap, title_size, INK_DARK, ACCENT_DARK)
    tag_w = ts.width(TAGLINE, 500, 30)
    tagline, _ = ts.outline(TAGLINE, 500, 30, (width - tag_w) / 2, 470)
    _, chips_w = chips(ts, RUNTIMES, 0, 0, 18, 38, 10, "#111827", "#1F2937", "#CBD5E1")
    chip_row, _ = chips(ts, RUNTIMES, (width - chips_w) / 2, 520, 18, 38, 10, "#111827", "#1F2937", "#CBD5E1")
    body = (
        backdrop(width, height, width / 2, 200, 520)
        + mark_svg("sr", (width - mark_size) / 2, 120, mark_size)
        + title
        + f'<path d="{tagline}" fill="{MUTED_DARK}"/>'
        + chip_row
    )
    return svg(width, height, body, "Secure Runtimes")


def app_icon(size):
    """Mark centered on the dark brand background (used for touch and PWA icons)."""
    mark_size = size * 0.62
    offset = (size - mark_size) / 2
    body = f'<rect width="{size}" height="{size}" fill="{BG_DARK}"/>' + mark_svg("sr", offset, offset + size * 0.01, mark_size)
    return svg(size, size, body, "Secure Runtimes")


def geometry_ts():
    bands = ",\n".join(
        f"  {{ from: '{start}', to: '{end}', top: {top}, bottom: {bottom} }}"
        for (start, end), (top, bottom) in zip(BANDS, BAND_SPANS)
    )
    cuts = ", ".join(f"{{ y: {y}, height: {h} }}" for y, h in CUTS)
    return f"""// Generated by assets/brand/generate.py. Edit the generator, not this file.
export const SHIELD_PATH = '{SHIELD}';
export const CHECK_PATH = '{CHECK}';
export const CHECK_WIDTH = {CHECK_WIDTH};
export const CUTS = [{cuts}];
export const BANDS = [
{bands}
];
"""


# ==========================================
# Output
# ==========================================
def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"wrote {os.path.relpath(path, ROOT)}")


def rasterize(svg_path, png_path, width, height):
    subprocess.run(["rsvg-convert", "-w", str(width), "-h", str(height), "-o", png_path, svg_path], check=True)
    print(f"wrote {os.path.relpath(png_path, ROOT)}")


def main():
    if not os.path.exists(FONT_CACHE):
        os.makedirs(os.path.dirname(FONT_CACHE), exist_ok=True)
        urllib.request.urlretrieve(FONT_URL, FONT_CACHE)
    ts = Typesetter(FONT_CACHE)

    mark = svg(64, 64, mark_svg("sr"), "Secure Runtimes")
    write(os.path.join(BRAND_DIR, "logo-mark.svg"), mark)
    write(os.path.join(PUBLIC_DIR, "favicon.svg"), svg(64, 64, mark_svg("sr", small=True), "Secure Runtimes"))
    write(os.path.join(BRAND_DIR, "logo-dark.svg"), horizontal_logo(ts, INK_DARK, ACCENT_DARK))
    write(os.path.join(BRAND_DIR, "logo-light.svg"), horizontal_logo(ts, INK_LIGHT, ACCENT_LIGHT))
    write(os.path.join(BRAND_DIR, "banner.svg"), banner(ts))
    write(GEOMETRY_TS, geometry_ts())

    tmp = os.path.join(BRAND_DIR, ".build")
    os.makedirs(tmp, exist_ok=True)
    card = os.path.join(tmp, "social.svg")
    write(card, social_card(ts))
    rasterize(card, os.path.join(BRAND_DIR, "social-preview.png"), 1280, 640)
    rasterize(card, os.path.join(PUBLIC_DIR, "og-image.png"), 1280, 640)
    for name, size in (("apple-touch-icon.png", 180), ("icon-192.png", 192), ("icon-512.png", 512)):
        icon = os.path.join(tmp, f"icon-{size}.svg")
        write(icon, app_icon(size))
        rasterize(icon, os.path.join(PUBLIC_DIR, name), size, size)
    for leftover in os.listdir(tmp):
        os.remove(os.path.join(tmp, leftover))
    os.rmdir(tmp)


if __name__ == "__main__":
    main()
