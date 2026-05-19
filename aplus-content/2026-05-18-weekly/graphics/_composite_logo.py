#!/usr/bin/env python3
"""Composite the real A+ Tutoring logo onto May 18 text graphics.

Reuses the chroma-key + alpha_composite pattern from the May 15 bundle.
Two-color logo on navy backgrounds; white-recolored variant on orange.
"""
from PIL import Image, ImageDraw
from pathlib import Path

LOGO = Path("/Users/romanslavinsky/Desktop/logo.png")
GFX = Path("/Users/romanslavinsky/Desktop/aplus-marketing-skills/aplus-content/2026-05-18-weekly/graphics")


def chroma_keyed_logo():
    raw = Image.open(LOGO).convert("RGBA")
    corners = [raw.getpixel((0, 0)), raw.getpixel((raw.width - 1, 0)),
               raw.getpixel((0, raw.height - 1)), raw.getpixel((raw.width - 1, raw.height - 1))]
    if max(p[3] for p in corners) == 0:
        return raw
    px = raw.load()
    threshold = 240
    for y in range(raw.height):
        for x in range(raw.width):
            r, g, b, a = px[x, y]
            if r >= threshold and g >= threshold and b >= threshold:
                px[x, y] = (r, g, b, 0)
    return raw


def white_variant(rgba_logo):
    out = rgba_logo.copy()
    px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = px[x, y]
            if a > 0:
                px[x, y] = (255, 255, 255, a)
    return out


def composite(source_name, output_name, erase_box, logo_anchor, logo_width, sample_xy, logo_rgba):
    src = GFX / source_name
    out = GFX / output_name
    print(f"=== {source_name} -> {output_name} ===")
    base = Image.open(src).convert("RGBA")
    bg = base.getpixel(sample_xy)
    print(f"  bg sample {sample_xy}: RGBA{bg}")
    ImageDraw.Draw(base).rectangle(erase_box, fill=bg)
    logo_resized = logo_rgba.resize((logo_width, logo_width), Image.LANCZOS)
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    layer.paste(logo_resized, logo_anchor, logo_resized)
    result = Image.alpha_composite(base, layer)
    result.save(out, "PNG")
    print(f"  wrote {out.name}")


LOGO_2COLOR = chroma_keyed_logo()
LOGO_WHITE = white_variant(LOGO_2COLOR)

# Social card (navy bg)
composite("social-card.png", "social-card-with-logo.png",
          erase_box=(1320, 800, 1520, 1010), logo_anchor=(1360, 830), logo_width=160,
          sample_xy=(50, 50), logo_rgba=LOGO_2COLOR)

# Carousel slide (navy bg)
composite("carousel-slide-1.png", "carousel-slide-1-with-logo.png",
          erase_box=(0, 10, 320, 240), logo_anchor=(30, 40), logo_width=110,
          sample_xy=(500, 1500), logo_rgba=LOGO_2COLOR)

# Main pull-quote (orange bg) — used for §6 inline AND standalone share
composite("pull-quote.png", "pull-quote-with-logo.png",
          erase_box=(820, 820, 1020, 1020), logo_anchor=(890, 890), logo_width=100,
          sample_xy=(20, 20), logo_rgba=LOGO_WHITE)

# Inline pull-quote §2 (orange bg)
composite("pull-quote-s2.png", "pull-quote-s2-with-logo.png",
          erase_box=(820, 820, 1020, 1020), logo_anchor=(890, 890), logo_width=100,
          sample_xy=(20, 20), logo_rgba=LOGO_WHITE)

# Inline pull-quote §3 (orange bg)
composite("pull-quote-s3.png", "pull-quote-s3-with-logo.png",
          erase_box=(820, 820, 1020, 1020), logo_anchor=(890, 890), logo_width=100,
          sample_xy=(20, 20), logo_rgba=LOGO_WHITE)

# Inline pull-quote §6 (same as main) — copy the already-composited version
import shutil
shutil.copy(GFX / "pull-quote-with-logo.png", GFX / "pull-quote-s6-with-logo.png")
print("=== pull-quote-s6-with-logo.png copied from pull-quote-with-logo.png ===")

print("\nDone.")
