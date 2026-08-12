#!/usr/bin/env python3
"""Cross reference the verified attendee list against the loaded headshots.

Reports only. Writes nothing. Run this, read it, then apply.

Matching is layered, strongest first, and anything below a confident match is
reported for a human rather than guessed:
  1. exact  first-last  slug
  2. exact  surname     slug   (the 2023 studio batch is named by surname)
  3. exact  firstname   slug   (the Employee Wall PDFs are named by first name)
  4. surname matches and first initial matches
  5. one or two character difference on the full slug, reported as FUZZY
"""

import csv
import os
import re
import sys
import unicodedata

REPO = ("/Users/creighton_macbook_2/Documents/Claude Code/Projects/"
        "Membership Live Wall 2026")
TSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "attendees.tsv")


def slug(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[‘’ʼ'`]", "", s)
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()
    return s


def lev(a, b):
    if abs(len(a) - len(b)) > 3:
        return 99
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def main():
    photos = sorted(f[:-4] for f in os.listdir(os.path.join(REPO, "assets", "attendees"))
                    if f.endswith(".jpg"))
    unused = set(photos)

    rows = []
    with open(TSV, encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            first = (r.get("First") or "").strip()
            last = (r.get("Last") or "").strip()
            if not first and not last:
                continue
            rows.append({
                "club": (r.get("Club") or "").strip(),
                "title": (r.get("Title") or "").strip(),
                "first": first,
                "last": last,
                "notes": (r.get("NOTES") or "").strip(),
            })

    # duplicates inside the client's own list
    seen = {}
    dupes = []
    for r in rows:
        k = slug(r["first"] + " " + r["last"])
        if k in seen:
            dupes.append((k, seen[k], r))
        else:
            seen[k] = r

    attending = [r for r in rows if "NOT ATTENDING" not in r["notes"].upper()]
    skipped = [r for r in rows if "NOT ATTENDING" in r["notes"].upper()]

    matched, nophoto, fuzzy = [], [], []
    for r in attending:
        if r["first"].upper() == "TBA":
            nophoto.append((r, "name is TBA in the list"))
            continue
        full = slug(r["first"] + " " + r["last"])
        sur = slug(r["last"])
        fir = slug(r["first"])
        hit = None
        how = ""
        for cand, label in ((full, "full name"), (sur, "surname only"), (fir, "first name only")):
            if cand in unused:
                hit, how = cand, label
                break
        if not hit:
            for p in sorted(unused):
                parts = p.split("-")
                if parts[-1] == sur and parts[0][:1] == fir[:1]:
                    hit, how = p, "surname plus initial"
                    break
        if not hit:
            best, bestd = None, 99
            for p in sorted(unused):
                d = lev(p, full)
                if d < bestd:
                    best, bestd = p, d
            if best and bestd <= 2:
                hit, how = best, "FUZZY distance %d" % bestd
                fuzzy.append((r, best, bestd))
        if hit:
            unused.discard(hit)
            matched.append((r, hit, how))
        else:
            nophoto.append((r, "no photo found"))

    print("=" * 72)
    print("VERIFIED LIST: %d rows, %d attending, %d marked not attending"
          % (len(rows), len(attending), len(skipped)))
    print("HEADSHOTS ON DISK: %d" % len(photos))
    print("=" * 72)
    print()
    print("MATCHED: %d" % len(matched))
    byhow = {}
    for r, p, how in matched:
        byhow.setdefault(how.split(" distance")[0], 0)
        byhow[how.split(" distance")[0]] += 1
    for k, v in sorted(byhow.items()):
        print("    %-22s %d" % (k, v))
    print()

    if fuzzy:
        print("NEEDS A HUMAN, matched only by near spelling: %d" % len(fuzzy))
        for r, p, d in fuzzy:
            print("    %-26s -> photo %-26s (%d char diff)"
                  % (r["first"] + " " + r["last"], p, d))
        print()

    print("ATTENDING WITH NO PHOTO: %d" % len(nophoto))
    for r, why in nophoto:
        print("    %-26s %-22s %s" % (r["first"] + " " + r["last"], r["club"], why))
    print()

    print("PHOTOS WITH NOBODY ON THE LIST: %d" % len(unused))
    for p in sorted(unused):
        print("    %s" % p)
    print()

    if dupes:
        print("DUPLICATE ROWS IN THE CLIENT LIST: %d" % len(dupes))
        for k, a, b in dupes:
            print("    %-24s  %s / %s  and  %s / %s"
                  % (k, a["title"], a["club"], b["title"], b["club"]))
        print()

    print("NOT ATTENDING, will be removed: %d" % len(skipped))
    for r in skipped:
        print("    %-26s %-22s %s" % (r["first"] + " " + r["last"], r["club"], r["notes"]))
    print()
    newbies = [r for r, p, h in matched if r["notes"].upper().startswith("NEW")]
    print("NEW in the notes column, so newbie: %d matched" % len(newbies))


if __name__ == "__main__":
    main()
