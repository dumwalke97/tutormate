#!/usr/bin/env python3
"""Renders the 1200x630 Open Graph preview image.

Kept as a script rather than a committed binary blob so the wording can be
changed without redrawing the image by hand.
"""
import pathlib
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[2]
WWW = ROOT / "www"
W, H = 1200, 630

NAVY = (27, 36, 71)
NAVY_LIGHT = (42, 55, 96)
WHITE = (255, 255, 255)
MUTED = (185, 196, 222)
SKY = (14, 165, 233)

FONT_DIRS = [
    pathlib.Path("/System/Library/Fonts/Supplemental"),
    pathlib.Path("/System/Library/Fonts"),
    pathlib.Path("/Library/Fonts"),
]


def font(names, size):
    for name in names:
        for d in FONT_DIRS:
            if (d / name).exists():
                return ImageFont.truetype(str(d / name), size)
    return ImageFont.load_default(size)


BOLD = ["Avenir Next.ttc", "HelveticaNeue.ttc", "Helvetica.ttc"]
img = Image.new("RGB", (W, H), NAVY)
d = ImageDraw.Draw(img)

# Soft diagonal band so the card is not a flat rectangle.
d.polygon([(0, H), (W, H), (W, int(H * 0.52))], fill=NAVY_LIGHT)

f_title = font(BOLD, 68)
f_sub = font(BOLD, 31)
f_meta = font(BOLD, 25)
f_brand = font(BOLD, 36)

logo_path = WWW / "Assets" / "TutorMateLogoTransparent.png"
x = 84
if logo_path.exists():
    logo = Image.open(logo_path).convert("RGBA")
    side = 78
    logo.thumbnail((side, side), Image.LANCZOS)
    # The source logo is dark on transparent; invert to white for the navy field.
    white = Image.new("RGBA", logo.size, WHITE + (0,))
    white.putalpha(logo.getchannel("A"))
    img.paste(white, (x, 76), white)
    x += logo.size[0] + 22

d.text((x, 88), "TutorMate", font=f_brand, fill=WHITE)

d.text((84, 214), "The AI homework helper", font=f_title, fill=WHITE)
d.text((84, 292), "that checks your work", font=f_title, fill=WHITE)

d.rectangle([(84, 392), (84 + 96, 398)], fill=SKY)

d.text((84, 432),
       "Snap a finished assignment. TutorMate marks every answer",
       font=f_sub, fill=MUTED)
d.text((84, 474),
       "and explains why, then builds a quiz to practice with.",
       font=f_sub, fill=MUTED)

d.text((84, 546), "tutormate.ai    ·    Web and iOS    ·    First 10 checks free",
       font=f_meta, fill=(140, 155, 190))

out = WWW / "Assets" / "og-image.png"
img.save(out, "PNG", optimize=True)
print(f"wrote {out.relative_to(ROOT)}  {out.stat().st_size:,} bytes  {img.size[0]}x{img.size[1]}")
