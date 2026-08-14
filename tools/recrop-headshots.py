#!/usr/bin/env python3
"""Re-cut badly framed headshots so the face is centred and featured. T3.1.

    python3 tools/recrop-headshots.py --audit     # report framing, write nothing
    python3 tools/recrop-headshots.py --dry-run   # plan the fixes, write nothing
    python3 tools/recrop-headshots.py             # fix them

Why this exists, and why the first attempt failed.

Lisa reported heads cut off and photos zoomed too far. Jim then named two:
Molly Dunn, whose head was missing entirely, and Tom Pyeatt, whose face was 15
percent of the frame and jammed against the top edge. The intake pipeline scales
the short edge to 400 and takes a CENTRED square, which is right for a
head-and-shoulders studio shot and badly wrong for a full-body phone snap, where
the middle of the frame is somebody's waist.

The first fix tried a fixed top bias: always take the crop from near the top.
That made things worse. It cut foreheads on photos that were already tight, and
on EXIF-rotated sources it moved the crop toward the wrong edge. All 143 files
were reverted. The lesson: there is no single offset that suits both a full-body
snap and a tight studio portrait, so stop guessing at geometry.

So this finds the actual face. macOS Vision does the detection through
tools/facefind, the crop is placed relative to the face box, and then, because
the previous attempt shipped a regression, EVERY OUTPUT IS RE-DETECTED AND
CHECKED. A crop that does not come out well is thrown away and the original file
is left alone. The tool cannot make things worse without saying so.

Three more things it will not do:
  - touch a photo whose framing already passes. 115 of 151 are fine
  - resurrect a person who was deliberately removed, see excluded_slugs
  - guess an identity. A source it cannot match confidently is reported
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Pillow is required. python3 -m pip install --user Pillow")

REPO = os.path.dirname(os.path.abspath(os.path.join(__file__, "..")))
OUT_DIR = os.path.join(REPO, "assets", "attendees")
FACEFIND = os.path.join(REPO, "tools", "facefind")
ROSTER = os.path.join(REPO, "data", "roster.json")

SIZE = 400
QUALITY = 82

# Where original, full resolution photos live. The 400x400 files in the repo have
# already thrown away the pixels a wider crop needs, so a re-crop has to start
# from the source.
SOURCE_DIRS = [
    os.path.expanduser("~/Downloads/OneDrive_1_8-11-2026"),
    os.path.expanduser("~/Downloads/OneDrive_1_8-11-2026/Newbies Headshots"),
    os.path.expanduser("~/Downloads"),          # Jim drops named one-offs straight in here
    os.path.join(REPO, "incoming", "headshots", "from-thread"),
    os.path.join(REPO, "incoming", "headshots", "named"),
]
SRC_EXT = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp", ".tif", ".tiff", ".bmp", ".gif"}

# ---------------------------------------------------------------- framing rules
#
# Calibrated against the photos that already look right. Gina Fabrizio, a good
# studio headshot, sits at 42 percent. Anything under 26 reads as a snapshot of a
# room that happens to contain a person.
TARGET_FACE = 0.40      # face height as a share of the finished square
FACE_CENTRE_V = 0.44    # where the face centre sits, top to bottom. Leaves headroom

MIN_FACE = 0.26         # below this the subject is not featured
MAX_FACE = 0.58         # above this it is uncomfortably tight
EDGE_PAD = 6            # px. face box nearer than this to an edge counts as clipped
MAX_OFF_CENTRE = 0.14   # horizontal drift from the middle, as a share of width

# Accepting an output is stricter than flagging an input, so a fix has to be a
# clear improvement rather than merely legal.
#
# The upper bound is waived when the crop already used the whole short edge. Some
# sources ARE tight close-ups: Doug Howe's face fills 59 percent of his original
# and no crop can zoom out past the edge of the file. Holding those to 55 percent
# rejected the very fix they needed, which was moving the box up so his crown
# stopped being cut off. Not clipped and properly placed is the actual goal.
OK_FACE = (0.30, 0.55)
OK_FACE_MAXED = 0.72   # ceiling once we are already as wide as the source allows
OK_OFF_CENTRE = 0.10


def slug(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[‘’ʼ'`]", "", s)
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()


def tokens(s):
    return [t for t in slug(s).split("-") if t and not t.isdigit()]


def excluded_slugs():
    """People deliberately removed, and duplicate files deliberately dropped.

    A rebuild that ignores this list silently resurrects them. It did exactly
    that on the first attempt and put two people back who Jim had removed.
    """
    out = set()
    try:
        d = json.load(open(os.path.join(REPO, "data", "headshots-derived.json"),
                           encoding="utf-8"))
    except Exception:
        return out
    for row in d.get("removed", []):
        if row.get("slug"):
            out.add(row["slug"])
    for row in d.get("resolved_duplicates", []):
        if row.get("dropped"):
            out.add(row["dropped"])
    return out


def facefind(paths):
    """slug-free wrapper over tools/facefind. Returns {path: (w, h, [faces])}."""
    if not paths:
        return {}
    if not os.path.exists(FACEFIND):
        sys.exit("tools/facefind is missing. Build it with:\n"
                 "    swiftc -O tools/facefind.swift -o tools/facefind")
    out = {}
    # argv has limits and this can be 150 files, so go in chunks
    for i in range(0, len(paths), 40):
        chunk = paths[i:i + 40]
        r = subprocess.run([FACEFIND] + chunk, capture_output=True, text=True, timeout=600)
        for line in r.stdout.splitlines():
            line = line.strip()
            if not line.startswith("{"):
                continue
            d = json.loads(line)
            if d.get("error"):
                out[d["path"]] = None
            else:
                out[d["path"]] = (d["width"], d["height"], d["faces"])
    return out


def grade(w, h, faces):
    """Judge one framing. Returns (verdict, detail). verdict 'ok' or a problem."""
    if not faces:
        return "noface", "no face found, head may be cut off"
    f = faces[0]
    frac = f["h"] / float(h)
    top, bot = f["y"], f["y"] + f["h"]
    left, right = f["x"], f["x"] + f["w"]
    cx = (f["x"] + f["w"] / 2.0) / float(w)
    if top < EDGE_PAD or bot > h - EDGE_PAD or left < EDGE_PAD or right > w - EDGE_PAD:
        return "clipped", "face touches the crop edge"
    if frac < MIN_FACE:
        return "small", "face only %.0f%% of the frame" % (frac * 100)
    if frac > MAX_FACE:
        return "tight", "face %.0f%% of the frame" % (frac * 100)
    if abs(cx - 0.5) > MAX_OFF_CENTRE:
        return "offcentre", "face %.0f%% off centre" % (abs(cx - 0.5) * 100)
    return "ok", "face %.0f%% of the frame" % (frac * 100)


def normalized(path):
    """Orientation-corrected RGB copy on disk, plus the PIL image.

    Vision is handed this file rather than the original, so the face box and the
    crop share one coordinate system. Mixing an EXIF-rotated source with an
    unrotated face box is precisely what broke the first attempt.
    """
    try:
        im = Image.open(path)
    except Exception:
        # HEIC has no Pillow decoder without pillow-heif. sips reads it.
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        tmp.close()
        r = subprocess.run(["sips", "-s", "format", "png", path, "--out", tmp.name],
                           capture_output=True, timeout=120)
        if r.returncode != 0 or not os.path.getsize(tmp.name):
            os.unlink(tmp.name)
            raise IOError("cannot decode")
        im = Image.open(tmp.name)
    im = ImageOps.exif_transpose(im).convert("RGB")
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    tmp.close()
    im.save(tmp.name, "PNG")
    return im, tmp.name


def crop_to_face(im, face):
    """Square crop placed on the face, clamped inside the image."""
    W, H = im.size
    fx, fy, fw, fh = face["x"], face["y"], face["w"], face["h"]

    S = fh / TARGET_FACE
    S = min(S, float(min(W, H)))          # never invent pixels outside the frame
    S = max(S, 1.0)

    cx = fx + fw / 2.0
    cy = fy + fh / 2.0
    left = cx - S / 2.0
    top = cy - FACE_CENTRE_V * S

    # Slide inside the frame rather than shrinking, so the face stays the size we
    # asked for even when the subject stands near an edge.
    left = max(0.0, min(left, W - S))
    top = max(0.0, min(top, H - S))

    box = (int(round(left)), int(round(top)),
           int(round(left + S)), int(round(top + S)))
    maxed = S >= float(min(W, H)) - 1.0      # already as wide as the source allows
    return im.crop(box), S, maxed


def build_source_index():
    """filename -> path, for every original photo on disk."""
    idx = []
    for d in SOURCE_DIRS:
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if os.path.splitext(fn)[1].lower() in SRC_EXT:
                idx.append((fn, os.path.join(d, fn)))
    return idx


def roster_names():
    """photo-file stem -> the person's real name, straight from the roster.

    Matching a source photo by the person's actual name beats matching by the
    file stem, because a stem like 'howe' or 'may' carries no first name.
    """
    out = {}
    try:
        r = json.load(open(ROSTER, encoding="utf-8"))
    except Exception:
        return out
    for p in r.get("attendees", []):
        ph = p.get("photo") or ""
        if ph:
            out[os.path.basename(ph)[:-4]] = p.get("name", "")
    return out


def find_sources(stem, name, index):
    """Candidate originals for a photo stem, best first.

    Whole-token matching only. Substrings would let 'may' claim 'Maynard'.

    Ties are returned rather than refused. A tie here is almost always the same
    person shot twice ('Kasey.png' and 'Kasey O'Connor.JPG', or two frames
    from one 2023 studio session), so the caller tries each and keeps whichever
    crops best, and prints which file won so the choice is auditable.

    The tie is only safe because every candidate shares the surname AND we are
    replacing a photo this person already has. It is NOT a way to assign a face
    to somebody who has none: that is what the two Hinckleys taught us, and it is
    why data/roster.json still holds their photo back.
    """
    want_name = tokens(name) if name else []
    want_stem = tokens(stem)

    scored = []
    for fn, path in index:
        have = set(tokens(os.path.splitext(fn)[0]))
        if not have:
            continue
        s = 0
        if want_name:
            hits = [t for t in want_name if t in have]
            # the surname is the discriminator, so require it
            if want_name[-1] in have:
                s = 10 * len(hits)
        if not s and want_stem and want_stem[-1] in have:
            s = 5 * len([t for t in want_stem if t in have])
        if s:
            scored.append((s, fn, path))

    if not scored:
        return [], "no source file matches"

    # Newest file first within a score tie, and the caller now takes the FIRST
    # candidate that grades acceptably rather than the best framed one.
    #
    # This cost Jim a replacement. He sent a new Tyler Busey headshot. It scored
    # identically to the year old "Tyler Busey.png" still sitting in the
    # SharePoint drop, because both filenames carry the same two name tokens. The
    # old caller kept whichever cropped closest to 40 percent face, that happened
    # to be the old photo, and the replacement was silently undone AFTER the
    # intake pipeline had written the right file. A newer file is a newer photo,
    # so on a tie recency wins over framing.
    scored.sort(key=lambda x: (-x[0], -os.path.getmtime(x[2]), x[1]))
    best = scored[0][0]
    top = [x for x in scored if x[0] == best]
    note = "" if len(top) == 1 else "%d sources tied, newest first" % len(top)
    return [(fn, path) for _, fn, path in top], note


def main():
    audit_only = "--audit" in sys.argv
    dry_run = "--dry-run" in sys.argv
    only = [a for a in sys.argv[1:] if not a.startswith("-")]

    skip = excluded_slugs()
    current = sorted(f for f in os.listdir(OUT_DIR) if f.endswith(".jpg"))
    if only:
        current = [f for f in current if f[:-4] in set(only)]

    paths = [os.path.join(OUT_DIR, f) for f in current]
    print("Reading %d headshots in assets/attendees" % len(paths))
    found = facefind(paths)

    graded = {}
    for p in paths:
        stem = os.path.basename(p)[:-4]
        got = found.get(p)
        graded[stem] = ("noface", "unreadable") if not got else grade(*got)

    problems = {k: v for k, v in graded.items() if v[0] != "ok"}
    print("  framing looks right: %d" % (len(graded) - len(problems)))
    print("  needs attention:     %d" % len(problems))

    if audit_only:
        print()
        by = {}
        for stem, (verdict, why) in sorted(problems.items()):
            by.setdefault(verdict, []).append((stem, why))
        for verdict in ("noface", "clipped", "small", "tight", "offcentre"):
            if verdict not in by:
                continue
            print("%s (%d)" % (verdict.upper(), len(by[verdict])))
            for stem, why in by[verdict]:
                print("    %-30s %s" % (stem, why))
            print()
        return

    index = build_source_index()
    names = roster_names()
    print("  original photos on disk: %d\n" % len(index))

    fixed, refused, nosource, kept = [], [], [], []

    for stem in sorted(problems):
        verdict, why = problems[stem]
        if stem in skip:
            continue

        cands, note = find_sources(stem, names.get(stem, ""), index)
        if not cands:
            nosource.append((stem, why, note))
            continue

        best = None          # (distance from target, probe path, reason, source name)
        last_fail = "no candidate produced a usable crop"

        for src_name, src in cands:
            tmp = None
            try:
                im, tmp = normalized(src)
            except Exception as exc:
                last_fail = "cannot decode %s: %s" % (src_name, exc)
                continue
            try:
                det = facefind([tmp]).get(tmp)
                if not det or not det[2]:
                    last_fail = "no face in the source either: %s" % src_name
                    continue

                out_im, S, maxed = crop_to_face(im, det[2][0])
                out_im = out_im.resize((SIZE, SIZE), Image.LANCZOS)

                # Prove it before keeping it. Write to a temp file, re-detect,
                # and only overwrite the real file if the result grades well.
                probe = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
                probe.close()
                out_im.save(probe.name, "JPEG", quality=QUALITY, optimize=True)
                pd = facefind([probe.name]).get(probe.name)

                accept, reason = False, "no face in the result"
                if pd and pd[2]:
                    f = pd[2][0]
                    frac = f["h"] / float(SIZE)
                    cx = (f["x"] + f["w"] / 2.0) / float(SIZE)
                    hi = OK_FACE_MAXED if maxed else OK_FACE[1]
                    if (f["y"] < EDGE_PAD or f["y"] + f["h"] > SIZE - EDGE_PAD
                            or f["x"] < EDGE_PAD or f["x"] + f["w"] > SIZE - EDGE_PAD):
                        reason = "result still clips the face"
                    elif frac < OK_FACE[0] or frac > hi:
                        reason = "result face %.0f%%, outside %d to %d" % (
                            frac * 100, OK_FACE[0] * 100, hi * 100)
                    elif abs(cx - 0.5) > OK_OFF_CENTRE:
                        reason = "result face %.0f%% off centre" % (abs(cx - 0.5) * 100)
                    else:
                        accept = True
                        reason = "face %.0f%% of the frame" % (frac * 100)
                        if maxed and frac > OK_FACE[1]:
                            reason += ", source is a tight close-up"

                if accept:
                    # First acceptable candidate wins, and candidates arrive
                    # newest first. Do not keep hunting for a better framed one:
                    # that is how a fresh replacement lost to an older file.
                    best = (0, probe.name, reason, src_name)
                    break
                else:
                    last_fail = reason
                    os.unlink(probe.name)
            finally:
                im.close()
                if tmp and os.path.exists(tmp):
                    os.unlink(tmp)

        if best is None:
            refused.append((stem, why, last_fail))
            continue

        _, probe_path, reason, src_name = best
        if note:
            src_name = "%s  (%s)" % (src_name, note)
        if dry_run:
            kept.append((stem, why, reason, src_name))
            os.unlink(probe_path)
        else:
            shutil.move(probe_path, os.path.join(OUT_DIR, stem + ".jpg"))
            fixed.append((stem, why, reason, src_name))

    label = "WOULD FIX" if dry_run else "FIXED"
    rows = kept if dry_run else fixed
    print("%s (%d)" % (label, len(rows)))
    for stem, was, now, src in rows:
        print("    %-26s %-30s -> %-24s from %s" % (stem, was, now, src[:34]))
    print()
    if refused:
        print("LEFT ALONE, the re-crop was not an improvement (%d)" % len(refused))
        for stem, was, reason in refused:
            print("    %-26s %-30s %s" % (stem, was, reason))
        print()
    if nosource:
        print("NO USABLE ORIGINAL, still needs a better photo (%d)" % len(nosource))
        for stem, was, reason in nosource:
            print("    %-26s %-30s %s" % (stem, was, reason))
        print()
    print("Re-run with --audit afterwards to confirm the whole set.")


if __name__ == "__main__":
    main()
