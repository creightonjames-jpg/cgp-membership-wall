#!/usr/bin/env python3
"""Build data/roster.json by cross referencing the verified attendee list against
the headshots on disk. ROADMAP T3.1.

    python3 tools/reconcile-roster.py             # report and write roster.json
    python3 tools/reconcile-roster.py --report    # report only, write nothing

Inputs, both in the repo so this is reproducible:
    data/attendee-list-verified.tsv   the list from Carol and Lisa
    assets/attendees/*.jpg            the processed headshots

When a correction comes in, add a line to OVERRIDE or NOT_THE_SAME below and run
this again. Do not hand edit data/roster.json: it gets overwritten.

Matching is layered, strongest first, and anything weaker than a confident match
is reported rather than guessed:
    1. exact full name slug
    2. exact surname slug        the 2023 studio batch is named by surname
    3. exact first name slug     the Employee Wall PDFs are named by first name
    4. surname plus first initial
    5. one or two characters different on the full slug
"""

import csv
import json
import os
import re
import sys
import unicodedata

REPO = os.path.dirname(os.path.abspath(os.path.join(__file__, "..")))
TSV = os.path.join(REPO, "data", "attendee-list-verified.tsv")
SHOTS = os.path.join(REPO, "assets", "attendees")
OUT = os.path.join(REPO, "data", "roster.json")

# "First Last" as it appears in the verified list -> the photo file's slug.
# For photos whose filename no rule can reach, and for confirmed name changes.
OVERRIDE = {
    "eric temena":     "eric-temena-west",        # Eric Temena-PGA WEST.jpg
    "erinn kaucher":   "kaucher-erinn-2-pp-web",  # Kaucher_Erinn, surname first
    "cyndi melfi":     "melfi-0001",              # Melfi 0001.JPG
    "chelsea petrick": "chelsea-pariseau",        # name change, confirmed by Jim
}

# Rows in the list that are the same human as another row. Keyed by the row to
# drop, valued by the row to keep, so a title clash gets decided once.
SAME_PERSON = {}

# Clubs are written a few ways in the list. Map to the spelling the workbook uses
# so the graph picker and the roster filter agree.
CLUB_FIX = {
    "Oregon": "Oregon GC",
    "Prescott": "Prescott Lakes",
    "PGA West": "PGA WEST",
    "Toledo Country Club": "Toledo CC",
    "Spring Creek Ranch": "Spring Creek",
}

# Answered. Kept so nobody re-opens them or "helpfully" matches them later.
RESOLVED = [
    {"q": "Is aubrey-de-matthaeis the same person as Aubrey Gillespie?",
     "a": "NO. Jim, Aug 12 2026: there are two Aubreys. Different people. "
          "aubrey-de-matthaeis is not on the attendee list and stays parked. "
          "Aubrey Gillespie still needs her own photo. Do NOT match these."},
    {"q": "Is chelsea-pariseau the same person as Chelsea Petrick?",
     "a": "YES. Jim, Aug 12 2026, name change. Applied via OVERRIDE."},
]

OPEN_QUESTIONS = [
    {"q": "The list carries James Hinckley as Principal and Jim Hinckley as "
          "Partner. Same person, two rows, two titles. Which title is right?",
     "effect": "Both are in the roster, one with the photo and one without."},
]


def slug(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[‘’ʼ'`]", "", s)
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()


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


def load_rows():
    rows = []
    with open(TSV, encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            first = (r.get("First") or "").strip()
            last = (r.get("Last") or "").strip()
            if not first and not last:
                continue
            rows.append({
                "club": (r.get("Club") or "").strip(),
                "title": re.sub(r"\s+", " ", (r.get("Title") or "")).strip(),
                "first": first,
                "last": last,
                "notes": re.sub(r"\s+", " ", (r.get("NOTES") or "")).strip(),
            })
    return rows


def main():
    report_only = "--report" in sys.argv

    photos = sorted(f[:-4] for f in os.listdir(SHOTS) if f.endswith(".jpg"))
    unused = set(photos)

    rows = load_rows()
    excluded = [r for r in rows if "NOT ATTENDING" in r["notes"].upper()]
    tba = [r for r in rows if r["first"].upper() == "TBA"]

    attending = [r for r in rows
                 if "NOT ATTENDING" not in r["notes"].upper()
                 and r["first"].upper() != "TBA"]

    # collapse rows that are literally the same name, keeping the fuller title
    seen, people, collapsed = {}, [], []
    for r in attending:
        k = slug(r["first"] + " " + r["last"])
        k = SAME_PERSON.get(k, k)
        if k in seen:
            collapsed.append(r)
            if len(r["title"]) > len(seen[k]["title"]):
                seen[k]["title"] = r["title"]
            continue
        seen[k] = r
        people.append(r)

    out, unmatched, how_counts = [], [], {}
    for r in people:
        full = slug(r["first"] + " " + r["last"])
        sur, fir = slug(r["last"]), slug(r["first"])
        key = (r["first"].strip() + " " + r["last"].strip()).lower()
        key = re.sub(r"\s+", " ", key)

        hit, how = None, ""
        if key in OVERRIDE and OVERRIDE[key] in unused:
            hit, how = OVERRIDE[key], "override"
        if not hit:
            for cand, label in ((full, "full name"), (sur, "surname"), (fir, "first name")):
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
            best, bd = None, 99
            for p in sorted(unused):
                d = lev(p, full)
                if d < bd:
                    best, bd = p, d
            if best and bd <= 2:
                hit, how = best, "near spelling"

        if hit:
            unused.discard(hit)
            how_counts[how] = how_counts.get(how, 0) + 1
        else:
            unmatched.append(r["first"] + " " + r["last"])

        out.append({
            "slug": full,
            "name": re.sub(r"\s+", " ", (r["first"] + " " + r["last"]).strip()),
            "title": r["title"],
            "club": CLUB_FIX.get(r["club"].strip(), r["club"].strip()),
            "region": "",
            "newbie": r["notes"].upper().startswith("NEW"),
            "photo": ("assets/attendees/%s.jpg" % hit) if hit else "",
            "note": "" if r["notes"].upper().startswith("NEW") else r["notes"],
            "needsReview": not hit,
        })

    counts = {
        "people": len(out),
        "withPhoto": len([p for p in out if p["photo"]]),
        "withoutPhoto": len([p for p in out if not p["photo"]]),
        "newbie": len([p for p in out if p["newbie"]]),
        "clubs": len({p["club"] for p in out}),
    }

    print("verified list rows: %d" % len(rows))
    print("  excluded, not attending: %d" % len(excluded))
    print("  excluded, name is TBA:   %d" % len(tba))
    print("  collapsed as duplicates: %d" % len(collapsed))
    print("headshots on disk: %d" % len(photos))
    print()
    print("roster: %s" % json.dumps(counts))
    print("matched by: %s" % json.dumps(how_counts))
    print()
    print("attending with no photo (%d):" % len(unmatched))
    for n in unmatched:
        print("    %s" % n)
    print()
    print("photos not on the list (%d), left on disk and out of the roster:" % len(unused))
    for p in sorted(unused):
        print("    %s" % p)

    if report_only:
        print("\n--report given, nothing written.")
        return

    doc = {
        "_note": ("VERIFIED against data/attendee-list-verified.tsv. Club, title, "
                  "first and last come from that list. The NEW column became the "
                  "newbie flag. Generated by tools/reconcile-roster.py, so do not "
                  "hand edit this file: add to OVERRIDE in that script and re-run. "
                  "Crew panel edits live in Firebase under roster/{slug} and "
                  "override this file at runtime. T3.1."),
        "_counts": counts,
        "_openQuestions": OPEN_QUESTIONS,
        "_resolved": RESOLVED,
        "_photosOnDiskNotOnTheList": sorted(unused),
        "attendees": out,
    }
    json.dump(doc, open(OUT, "w", encoding="utf-8"), indent=2)
    print("\nwrote %s" % os.path.relpath(OUT, REPO))


if __name__ == "__main__":
    main()
