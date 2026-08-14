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

# ------------------------------------------------------- per photo tuning
#
# Jim reviewed the whole roster on Aug 13 2026 and named these by hand. Run with
# --tune to apply them. Keyed by PHOTO FILE STEM, not by roster slug, because the
# 2023 studio batch is filed by surname: Gene Miller is miller.jpg.
#
#   face    target face height as a share of the crop. LOWER is a wider shot
#   centre  where the face centre sits top to bottom. HIGHER leaves more room
#           above the head, which is the actual fix for a clipped crown
#
# Both dials matter and they are not interchangeable. Eight of the fourteen "zoom
# out" sources are already cropped to the full width of the file, so there is no
# zoom left to give. On those the crown is recovered by sliding the window up,
# which is what centre does. Vision's face box runs forehead to chin and excludes
# hair, so the crown always sits above the box and headroom is what protects it.
FRAME_TUNE = {
    # Top of the head was cut. Wider where the source allows, more headroom always.
    "katie-robinson":     {"face": 0.34, "centre": 0.52},
    "todd-leonard":       {"face": 0.34, "centre": 0.52},
    "mary-fina":          {"face": 0.34, "centre": 0.52},
    "domenic-provenzano": {"face": 0.34, "centre": 0.52},
    "crystal-daniel":     {"face": 0.34, "centre": 0.52},
    "kristina-karoll":    {"face": 0.34, "centre": 0.52},
    "chelsea-pariseau":   {"face": 0.34, "centre": 0.52},
    "anai-romero":        {"face": 0.34, "centre": 0.52},
    # "romine" was here. Jim replaced Dawne Romine's photo entirely on Aug 13, and
    # the new one sits at the standard 40 percent with her crown fully in frame, so
    # the zoom-out dial that fixed the OLD photo would now just crop her loose for
    # no reason. Removed rather than left to fire on a photo it was not written for.
    "stromme":            {"face": 0.34, "centre": 0.52},
    "miller":             {"face": 0.34, "centre": 0.52},
    "howe":               {"face": 0.34, "centre": 0.52},
    "jeannette-walker":   {"face": 0.34, "centre": 0.52},
    "james-hinckley":     {"face": 0.34, "centre": 0.52},
    "todd-keefer":        {"face": 0.34, "centre": 0.52},

    # Face read too small in the grid. Tighter crop, standard headroom.
    "kevin-paluch":       {"face": 0.47, "centre": 0.45},
    "spittle":            {"face": 0.47, "centre": 0.45},
    "han":                {"face": 0.47, "centre": 0.45},
    "darville":           {"face": 0.47, "centre": 0.45},
}

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

# Hamming distance out of 1024 between the FACE in the repo and the face in a
# candidate source, see face_print. Measured, not guessed.
#
# Same person, verified by eye:      22, 59, 60, 98, 164
# Different person, same surname:    400 (Bryan Miller), 507 (Dave Miller)
#
# miller.jpg is Gene Miller and the folder holds three Millers, so this is the
# case that decides the number. 250 sits 86 above the worst real match and 150
# below the nearest wrong one. Raising it toward 400 is how you put Dave Miller's
# face on Gene Miller's card.
SAME_FACE_MAX = 250

# Sources confirmed BY EYE, for the cases where the face hash is too strict.
#
# Keyed by photo stem, valued by the exact source filename. Checked one at a time
# by opening both images and comparing them, not by nudging SAME_FACE_MAX until
# the number went green. Raising the threshold to admit these would also admit
# Dave Miller at 400, which is the whole thing this guard exists to stop.
#
#   domenic-provenzano  distance 301. Same photo beyond any doubt: same grey
#     jacket, same glasses, same hedge and mountain background. The hash misfires
#     because the file in the repo is a tight face crop out of a 3549x4968
#     original, so the two faces differ in sharpness more than in shape.
CONFIRMED_SOURCE = {
    "domenic-provenzano": "Domenic Provenzano.jpg",
}


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


def crop_to_face(im, face, target=TARGET_FACE, centre=FACE_CENTRE_V):
    """Square crop placed on the face, clamped inside the image.

    target and centre come from FRAME_TUNE when a photo has been hand tuned,
    otherwise from the module defaults.
    """
    W, H = im.size
    fx, fy, fw, fh = face["x"], face["y"], face["w"], face["h"]

    S = fh / target
    S = min(S, float(min(W, H)))          # never invent pixels outside the frame
    S = max(S, 1.0)

    cx = fx + fw / 2.0
    cy = fy + fh / 2.0
    left = cx - S / 2.0
    top = cy - centre * S

    # Slide inside the frame rather than shrinking, so the face stays the size we
    # asked for even when the subject stands near an edge.
    left = max(0.0, min(left, W - S))
    top = max(0.0, min(top, H - S))

    box = (int(round(left)), int(round(top)),
           int(round(left + S)), int(round(top + S)))
    maxed = S >= float(min(W, H)) - 1.0      # already as wide as the source allows
    return im.crop(box), S, maxed


def ahash(path, n=16):
    """Average hash. Cheap, and enough to tell one shoot from another."""
    im = Image.open(path).convert("L").resize((n, n), Image.LANCZOS)
    px = list(im.getdata())
    avg = sum(px) / float(len(px))
    return [1 if v > avg else 0 for v in px]


def hamming(a, b):
    return sum(1 for x, y in zip(a, b) if x != y)


def face_print(path):
    """Hash of just the FACE, normalised, so framing does not enter into it.

    The first attempt at this hashed the whole frame and was measuring the wrong
    thing. Files that had already been through the face aware re-crop matched
    their source at distance 0, and files still carrying the ORIGINAL centred crop
    scored 60 to 120 against the very same photo, purely because the two crops
    frame differently. That is a framing signal, not an identity signal.

    Cutting both sides down to the detected face box removes framing from the
    comparison entirely. Same person in the same shot matches tightly whatever the
    crop around them was.
    """
    tmp = None
    try:
        im, tmp = normalized(path)
    except Exception:
        return None
    try:
        det = facefind([tmp]).get(tmp)
        if not det or not det[2]:
            return None
        f = det[2][0]
        # a little context around the box, so hair and jaw line count too
        pad = 0.18 * f["h"]
        box = (max(0, int(f["x"] - pad)), max(0, int(f["y"] - pad)),
               min(im.width, int(f["x"] + f["w"] + pad)),
               min(im.height, int(f["y"] + f["h"] + pad)))
        if box[2] - box[0] < 8 or box[3] - box[1] < 8:
            return None
        face = im.crop(box).convert("L").resize((32, 32), Image.LANCZOS)
        px = list(face.getdata())
        avg = sum(px) / float(len(px))
        return [1 if v > avg else 0 for v in px]
    finally:
        im.close()
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)


def pick_matching_source(stem, cands, existing, verbose=False):
    """Of several same surname candidates, the one showing the SAME FACE.

    Re-tuning an existing photo must not change WHICH photo it is. Name matching
    alone cannot promise that. Gene Miller's file is miller.jpg, and the sources
    on disk include both a 2023 studio frame of him and a completely different
    person's "Dave Miller.jpg". Scoring on the surname picks either, and the
    newest-first tie break picks Dave.

    Returns (name, path, distance), or (None, None, closest) when nothing is close
    enough, in which case the caller leaves the photo alone and says so.
    """
    if stem in CONFIRMED_SOURCE:
        wanted = CONFIRMED_SOURCE[stem]
        for src_name, src in cands:
            if src_name == wanted:
                return src_name, src, "eye"
        return None, None, "confirmed source %r is not on disk" % wanted

    want = face_print(existing)
    if want is None:
        return None, None, None

    scored = []
    for src_name, src in cands:
        got = face_print(src)
        if got is None:
            continue
        scored.append((hamming(want, got), src_name, src))

    scored.sort()
    if verbose:
        for d, n, _p in scored:
            print("        candidate %-42s face distance %d" % (n[:42], d))
    if not scored:
        return None, None, None
    if scored[0][0] > SAME_FACE_MAX:
        return None, None, scored[0][0]
    return scored[0][1], scored[0][2], scored[0][0]


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


def tune(dry_run, only):
    """Apply FRAME_TUNE to the photos Jim named. Same photo, new framing."""
    stems = [s for s in FRAME_TUNE if not only or s in set(only)]
    index = build_source_index()
    names = roster_names()
    skip = excluded_slugs()

    print("Tuning %d photo(s)%s\n" % (len(stems), " (dry run)" if dry_run else ""))
    print("%-22s %-34s %-5s %-13s %s"
          % ("PHOTO", "SOURCE", "MATCH", "FACE WAS", "FACE NOW"))
    print("-" * 96)

    done, refused = [], []
    for stem in sorted(stems):
        dest = os.path.join(OUT_DIR, stem + ".jpg")
        if stem in skip or not os.path.exists(dest):
            refused.append((stem, "no such photo in the repo"))
            continue

        before = facefind([dest]).get(dest)
        before_frac = (before[2][0]["h"] / float(before[1])) if (before and before[2]) else None

        cands, _note = find_sources(stem, names.get(stem, ""), index)
        if not cands:
            refused.append((stem, "no source file on disk"))
            continue

        src_name, src, dist = pick_matching_source(stem, cands, dest)
        if not src:
            refused.append((stem, "no source matches the current photo, closest %s. "
                                  "NOT touched, this is the Gene Miller guard"
                            % (dist if dist is not None else "n/a")))
            continue

        dials = FRAME_TUNE[stem]
        tmp = None
        try:
            im, tmp = normalized(src)
            det = facefind([tmp]).get(tmp)
            if not det or not det[2]:
                refused.append((stem, "no face in the source"))
                continue
            out, _S, maxed = crop_to_face(im, det[2][0],
                                          target=dials["face"], centre=dials["centre"])
            out = out.resize((SIZE, SIZE), Image.LANCZOS)

            probe = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
            probe.close()
            out.save(probe.name, "JPEG", quality=QUALITY, optimize=True)
            pd = facefind([probe.name]).get(probe.name)

            ok, why, frac = False, "no face in the result", None
            if pd and pd[2]:
                f = pd[2][0]
                frac = f["h"] / float(SIZE)
                hi = OK_FACE_MAXED if maxed else OK_FACE[1]
                cx = (f["x"] + f["w"] / 2.0) / float(SIZE)
                if f["y"] < EDGE_PAD or f["y"] + f["h"] > SIZE - EDGE_PAD:
                    why = "result clips the face vertically"
                elif frac < OK_FACE[0] or frac > hi:
                    why = "result face %.0f%%, outside %d to %d" % (
                        frac * 100, OK_FACE[0] * 100, hi * 100)
                elif abs(cx - 0.5) > OK_OFF_CENTRE:
                    why = "result face %.0f%% off centre" % (abs(cx - 0.5) * 100)
                else:
                    ok, why = True, ""

            if not ok:
                refused.append((stem, why))
                os.unlink(probe.name)
                continue

            print("%-22s %-34s %-5s %-13s %.0f%%%s"
                  % (stem, src_name[:34], dist,
                     ("%.0f%%" % (before_frac * 100)) if before_frac else "no face",
                     frac * 100, "  (source maxed)" if maxed else ""))
            if dry_run:
                os.unlink(probe.name)
            else:
                shutil.move(probe.name, dest)
            done.append(stem)
        finally:
            im.close()
            if tmp and os.path.exists(tmp):
                os.unlink(tmp)

    print("\n%s: %d" % ("would tune" if dry_run else "tuned", len(done)))
    if refused:
        print("\nLEFT ALONE (%d)" % len(refused))
        for stem, why in refused:
            print("    %-22s %s" % (stem, why))


def main():
    audit_only = "--audit" in sys.argv
    dry_run = "--dry-run" in sys.argv
    only = [a for a in sys.argv[1:] if not a.startswith("-")]

    if "--tune" in sys.argv:
        tune(dry_run, only)
        return

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
