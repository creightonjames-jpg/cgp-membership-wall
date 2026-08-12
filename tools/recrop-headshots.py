#!/usr/bin/env python3
"""Re-cut every headshot to 400x400 with the crop biased to the top. T3.1.

    python3 tools/recrop-headshots.py <source-folder> <map.csv> [<map2.csv> ...]

Why this exists. The first pass scaled the short edge to 400 and then took a
CENTRED square. On a portrait that throws away equal amounts of top and bottom,
and Lisa reported the result: "several photos need to be adjusted as heads are
cut off or zoomed in too far." She is right. A 296x640 source loses 54 percent of
its height to a centred crop, and on a headshot the head is not in the middle.

Two fixes:

1. The vertical crop is taken from near the TOP, not the centre. At most
   TOP_BIAS of the scaled height comes off the top and the rest off the bottom,
   so head and shoulders survive and the discard lands on the torso.
2. EXIF orientation is applied before anything else. Phone photos carry a
   rotation flag, and sips honoured it inconsistently across formats. A sideways
   headshot is worse than a tight one.

Landscape sources still crop horizontally from the centre, which is correct: in a
wide studio shot the subject is already centred.

Nothing is upscaled beyond what the 400px square needs, and the JPEG quality
matches the pipeline so file sizes stay in the same band.
"""

import csv
import json
import os
import subprocess
import sys
import tempfile

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Pillow is required. python3 -m pip install --user Pillow")

REPO = os.path.dirname(os.path.abspath(os.path.join(__file__, "..")))
OUT_DIR = os.path.join(REPO, "assets", "attendees")

SIZE = 400
QUALITY = 82

# The most of the scaled height that may be taken off the top. Keep this small.
# At 0.10 a very tall portrait keeps the head and loses the legs, which is what a
# headshot wants. Raising it starts cutting foreheads again.
TOP_BIAS = 0.10


def excluded_slugs():
    """People deliberately removed, and duplicate files deliberately dropped.

    A rebuild that ignores this list silently resurrects them. It did exactly
    that on the first run and put two people back who the client had removed.
    """
    out = set()
    p = os.path.join(REPO, "data", "headshots-derived.json")
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception:
        return out
    for row in d.get("removed", []):
        if row.get("slug"):
            out.add(row["slug"])
    for row in d.get("resolved_duplicates", []):
        if row.get("dropped"):
            out.add(row["dropped"])
    return out


def open_image(path):
    """PIL, falling back to a sips conversion for formats it cannot read.

    Pillow has no HEIC decoder without pillow-heif, and iPhone photos are HEIC.
    sips reads them, so convert to a temp JPEG and hand that over.
    """
    try:
        return Image.open(path), None
    except Exception:
        tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        tmp.close()
        r = subprocess.run(["sips", "-s", "format", "jpeg", path, "--out", tmp.name],
                           capture_output=True, timeout=90)
        if r.returncode != 0 or not os.path.getsize(tmp.name):
            os.unlink(tmp.name)
            raise
        return Image.open(tmp.name), tmp.name


def load_maps(paths):
    """file basename -> slug, later maps win."""
    m = {}
    for p in paths:
        with open(p, newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                f = (row.get("file") or "").strip()
                s = (row.get("slug") or "").strip()
                if f and s:
                    m[f] = s
    return m


def square_400(im):
    """Scale so the short edge is 400, then crop a 400 square, top biased."""
    im = ImageOps.exif_transpose(im)          # before any measurement
    if im.mode not in ("RGB", "L"):
        im = im.convert("RGB")
    elif im.mode == "L":
        im = im.convert("RGB")

    w, h = im.size
    scale = SIZE / float(min(w, h))
    nw, nh = max(SIZE, int(round(w * scale))), max(SIZE, int(round(h * scale)))
    im = im.resize((nw, nh), Image.LANCZOS)

    if nh > nw:                                # portrait, crop vertically
        overflow = nh - SIZE
        top = int(min(overflow, round(nh * TOP_BIAS)))
        left = (nw - SIZE) // 2
    else:                                      # landscape or square
        top = (nh - SIZE) // 2
        left = (nw - SIZE) // 2

    return im.crop((left, top, left + SIZE, top + SIZE)), (w, h)


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    src, maps = sys.argv[1], sys.argv[2:]
    name_to_slug = load_maps(maps)
    skip = excluded_slugs()

    wrote, skipped, moved, refused = 0, [], [], []
    for fn in sorted(os.listdir(src)):
        slug = name_to_slug.get(fn)
        if not slug:
            continue
        if slug in skip:
            refused.append(slug)
            continue
        path = os.path.join(src, fn)
        tmp = None
        try:
            im, tmp = open_image(path)
            try:
                out, orig = square_400(im)
            finally:
                im.close()
        except Exception as exc:
            skipped.append((fn, str(exc)[:60]))
            continue
        finally:
            if tmp and os.path.exists(tmp):
                os.unlink(tmp)

        dest = os.path.join(OUT_DIR, slug + ".jpg")
        out.save(dest, "JPEG", quality=QUALITY, optimize=True)
        wrote += 1

        w, h = orig
        ratio = max(w, h) / float(min(w, h))
        if h > w and ratio > 1.25:
            moved.append((slug, "%dx%d" % (w, h), round(ratio, 2)))

    # belt and braces: a stale file on disk is as bad as a resurrected one
    for slug in sorted(skip):
        stale = os.path.join(OUT_DIR, slug + ".jpg")
        if os.path.exists(stale):
            os.remove(stale)
            print("deleted stale file for a removed person: %s" % slug)

    print("re-cut: %d" % wrote)
    print("refused, removed earlier on purpose: %d  %s"
          % (len(refused), ", ".join(sorted(set(refused))) or "none"))
    print("skipped: %d" % len(skipped))
    for fn, why in skipped[:10]:
        print("    %-44s %s" % (fn[:44], why))
    print()
    print("tall portraits that materially changed (%d), these are the ones Lisa"
          " was looking at:" % len(moved))
    for slug, dims, ratio in sorted(moved, key=lambda x: -x[2])[:16]:
        print("    %-26s %-12s ratio %s" % (slug, dims, ratio))


if __name__ == "__main__":
    main()
