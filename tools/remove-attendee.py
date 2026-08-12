#!/usr/bin/env python3
"""Remove attendees from the roster and delete their headshots. T3.1 upkeep.

    python3 tools/remove-attendee.py <slug> [<slug> ...] [--why "reason"]

Refuses a slug that does not exist rather than silently doing nothing, and
records every removal in data/headshots-derived.json so the decision survives.
"""
import json, os, sys

def main():
    args = sys.argv[1:]
    why = ""
    if "--why" in args:
        i = args.index("--why")
        why = args[i + 1] if len(args) > i + 1 else ""
        args = args[:i]
    if not args:
        sys.exit(__doc__)

    roster = json.load(open("data/roster.json", encoding="utf-8"))
    have = {p["slug"] for p in roster["attendees"]}
    missing = [s for s in args if s not in have]
    if missing:
        sys.exit("Not in the roster, nothing removed: %s" % ", ".join(missing))

    roster["attendees"] = [p for p in roster["attendees"] if p["slug"] not in args]
    roster["_counts"] = {
        "people": len(roster["attendees"]),
        "newbie": len([p for p in roster["attendees"] if p["newbie"]]),
        "withClub": len([p for p in roster["attendees"] if p["club"]]),
        "needsReview": len([p for p in roster["attendees"] if p["needsReview"]]),
    }
    json.dump(roster, open("data/roster.json", "w", encoding="utf-8"), indent=2)

    for s in args:
        p = os.path.join("assets", "attendees", s + ".jpg")
        if os.path.exists(p):
            os.remove(p)
            print("  deleted %s" % p)
        else:
            print("  no photo on disk for %s" % s)

    d = json.load(open("data/headshots-derived.json", encoding="utf-8"))
    d["people"] = [p for p in d["people"] if p["slug"] not in args]
    d["photos_loaded"] = len(d["people"])
    d.setdefault("removed", []).extend(
        {"slug": s, "why": why or "removed on request"} for s in args)
    json.dump(d, open("data/headshots-derived.json", "w", encoding="utf-8"), indent=2)

    print("  roster now %d" % roster["_counts"]["people"])
    print("  counts %s" % json.dumps(roster["_counts"]))

if __name__ == "__main__":
    main()
