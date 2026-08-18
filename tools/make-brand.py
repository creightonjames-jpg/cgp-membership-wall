#!/usr/bin/env python3
"""Generate the Live Wall brand assets. ROADMAP T0.5.

Writes app icons and the QR code into assets/brand/. Both are static repo
assets, per the data split in CLAUDE.md. Nothing here runs in the browser and
nothing calls out to a third party service at runtime.

    python3 tools/make-brand.py

Needs Pillow. The QR step needs segno:  python3 -m pip install --user segno

Icon is a gold guitar pick on a scarlet stage wash. It reads at home screen
size, which a wordmark does not.

The QR is deliberately DARK MODULES ON A CREAM CARD, not inverted. Plenty of
scanners refuse a light-on-dark code, and this one has to work first try from
a table tent in a dim ballroom.
"""

import os
import sys

try:
    from PIL import Image, ImageDraw
except ImportError:
    sys.exit("Pillow is required. python3 -m pip install --user Pillow")

REPO = os.path.dirname(os.path.abspath(os.path.join(__file__, "..")))
BRAND = os.path.join(REPO, "assets", "brand")

WALL_URL = "https://creightonjames-jpg.github.io/cgp-membership-wall/"

# Every other QR the wall needs, name -> URL. Jim, Aug 18 2026, first one: a
# direct link to the donation slip, ?go=cares-pledge, for texting or posting
# rather than pointing a phone at the main wall QR and tapping through three
# taps to get there.
EXTRA_QR = {
    "qr-cares-pledge": WALL_URL + "?go=cares-pledge"
}

SCARLET = (200, 16, 46)
OXBLOOD = (122, 12, 27)
GOLD = (217, 169, 76)
CREAM = (247, 243, 234)
STAGE = (23, 22, 26)

# Same silhouette as the .pick clip-path in index.html. Percentages of the box.
PICK = [
    (15, 8), (28, 2), (50, 0), (72, 2), (85, 8),
    (95, 25), (98, 42),
    (88, 68), (68, 88), (55, 98), (50, 100),
    (45, 98), (32, 88), (12, 68),
    (2, 42), (5, 25),
]

RENDER = 2048   # draw big, downscale with LANCZOS for clean edges
WASH = 256      # the wash is a smooth radial, so compute it small and scale up


def smooth_closed(points, per_segment=16):
    """Catmull-Rom through a closed loop of control points.

    The CSS .pick uses 16 straight segments, which is invisible at badge size
    but reads as a faceted gemstone at 512px. This rounds it off.
    """
    n = len(points)
    out = []
    for i in range(n):
        p0, p1 = points[(i - 1) % n], points[i]
        p2, p3 = points[(i + 1) % n], points[(i + 2) % n]
        for s in range(per_segment):
            t = s / float(per_segment)
            t2, t3 = t * t, t * t * t
            out.append(tuple(
                0.5 * ((2 * a1)
                       + (-a0 + a2) * t
                       + (2 * a0 - 5 * a1 + 4 * a2 - a3) * t2
                       + (-a0 + 3 * a1 - 3 * a2 + a3) * t3)
                for a0, a1, a2, a3 in zip(p0, p1, p2, p3)
            ))
    return out


def stage_wash(size):
    """Scarlet in the middle falling off to oxblood, like a lit backdrop."""
    img = Image.new("RGB", (size, size), OXBLOOD)
    px = img.load()
    cx = cy = (size - 1) / 2.0
    peak = (size / 2.0) * 1.18
    for y in range(size):
        for x in range(size):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 / peak
            if d > 1.0:
                d = 1.0
            d = d ** 1.35
            px[x, y] = (
                round(SCARLET[0] + (OXBLOOD[0] - SCARLET[0]) * d),
                round(SCARLET[1] + (OXBLOOD[1] - SCARLET[1]) * d),
                round(SCARLET[2] + (OXBLOOD[2] - SCARLET[2]) * d),
            )
    return img


def draw_pick(img, frac=0.60):
    """Gold pick, centered, sized as a fraction of the canvas width."""
    size = img.size[0]
    w = size * frac
    h = w * 1.02                      # a pick is a touch taller than it is wide
    left = (size - w) / 2.0
    top = (size - h) / 2.0
    pts = [(left + (x / 100.0) * w, top + (y / 100.0) * h)
           for x, y in smooth_closed(PICK)]
    ImageDraw.Draw(img).polygon(pts, fill=GOLD)
    return img


def build_icon(out_size, pick_frac=0.60):
    img = stage_wash(WASH).resize((RENDER, RENDER), Image.LANCZOS)
    draw_pick(img, pick_frac)
    return img.resize((out_size, out_size), Image.LANCZOS)


def write_icons():
    os.makedirs(BRAND, exist_ok=True)
    # Maskable icons keep the mark inside the safe circle, so a rounded or
    # circular mask on Android cannot clip the pick.
    targets = [
        ("icon-192.png", 192, 0.56),
        ("icon-512.png", 512, 0.56),
        ("apple-touch-icon.png", 180, 0.62),
        ("favicon-32.png", 32, 0.68),
    ]
    for name, size, frac in targets:
        path = os.path.join(BRAND, name)
        build_icon(size, frac).save(path, "PNG", optimize=True)
        print("  %-24s %4dx%-4d %6d bytes" % (name, size, size, os.path.getsize(path)))


def write_one_qr(stem, url):
    """One QR, SVG and PNG, same dark-on-cream recipe every time. Returns the
    PNG path so the caller can decode-check it."""
    try:
        import segno
    except ImportError:
        print("  segno not installed, skipping %s. "
              "python3 -m pip install --user segno" % stem)
        return None

    # Error correction M is the sane default for a screen and a table tent.
    qr = segno.make(url, error="m")

    svg_path = os.path.join(BRAND, stem + ".svg")
    qr.save(svg_path, kind="svg", scale=10,
            border=3,             # quiet zone, scanners need it
            dark="#17161A",       # dark modules
            light="#F7F3EA")      # on a cream card, never inverted

    png_path = os.path.join(BRAND, stem + ".png")
    qr.save(png_path, kind="png", scale=16, border=3,
            dark="#17161A", light="#F7F3EA")

    print("  %-24s version %s, ecc %s, %d modules, %d bytes"
          % (stem + ".svg", qr.version, qr.error.upper(),
             qr.symbol_size(border=0)[0], os.path.getsize(svg_path)))
    print("  %-24s %d bytes" % (stem + ".png", os.path.getsize(png_path)))
    return png_path


def verify_qr(png_path, expected):
    """Decode our own QR and confirm it points where we think it does.

    A QR that encodes the wrong URL looks completely fine to a human. This is
    the one asset where a silent error means nobody reaches the intended page
    at all.
    """
    try:
        import cv2
    except ImportError:
        print("  NOT VERIFIED. Install opencv-python-headless to decode-check the QR.")
        return

    img = cv2.imread(png_path)
    decoded, _, _ = cv2.QRCodeDetector().detectAndDecode(img)

    if decoded == expected:
        print("  decode check: PASS, round-trips to %s" % decoded)
    else:
        sys.exit("  decode check: FAIL. Expected %r, decoded %r" % (expected, decoded))


def write_qr():
    png_path = write_one_qr("qr-wall", WALL_URL)
    if png_path:
        verify_qr(png_path, WALL_URL)

    for stem, url in EXTRA_QR.items():
        png_path = write_one_qr(stem, url)
        if png_path:
            verify_qr(png_path, url)


if __name__ == "__main__":
    print("Writing brand assets to assets/brand/")
    write_icons()
    write_qr()
    print("Done.")
