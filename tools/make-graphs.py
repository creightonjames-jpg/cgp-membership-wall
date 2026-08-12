#!/usr/bin/env python3
"""Render club membership graphs as SVG from the CGPM workbook. ROADMAP T3.2.

The workbook has no images in it. All 95 graphs are native Excel line charts,
but every one carries a cached copy of its own values, so this reads the numbers
straight out of the chart XML and draws its own. Nothing external is needed.

Why redraw rather than export from Excel:
  - consistent dimensions across every club, which the spec requires
  - the wall's palette instead of white Excel chrome
  - SVG, so it stays sharp at any zoom and weighs a few KB
  - legible at 380px, which a shrunken Excel screenshot is not

Designed at the 380px baseline. The viewBox is 380 wide so type renders close to
1:1 on a phone and scales up crisply on a laptop.

Fonts are a system stack, not Inter. An SVG loaded through an img tag cannot
fetch a web font. If the wall inlines the markup instead, Inter applies for free.

    python3 make-graphs.py <workbook.xlsx> <svg-dir> [manifest.json]

The SVGs and the manifest live in different places in this repo. SVGs are static
assets under assets/graphs/. The manifest is data, so it sits with the other
static data files at data/graphs.json. Pass it as the third argument. Left off,
the manifest lands next to the SVGs.
"""

import datetime
import html
import os
import re
import sys
import zipfile

# Palette, straight from the twelve tokens in index.html.
STAGE = "#17161A"
RISER = "#201E24"
SCARLET = "#C8102E"
GOLD = "#D9A94C"
CREAM = "#F7F3EA"
DIM = "#A39B92"
MUTE = "#6E6862"
EDGE = "#332F38"

FONT = "system-ui, -apple-system, 'Helvetica Neue', Arial, sans-serif"

W, H = 380, 240
# PAD_T leaves room for the title, the subtitle, and the legend so none of them
# can land on the plot. Type sizes are set for a 380px phone at default zoom,
# which is the spec's legibility bar, so nothing here goes below 9.5px.
PAD_L, PAD_R, PAD_T, PAD_B = 44, 12, 42, 26
PLOT_W = W - PAD_L - PAD_R
PLOT_H = H - PAD_T - PAD_B

COUNT, MONEY, PERCENT = "count", "money", "percent"


# ----------------------------------------------------------------- parsing

def text_of(fragment):
    return html.unescape(" ".join(re.findall(r"<a:t>([^<]*)</a:t>", fragment)))


def parse_charts(path):
    """Yields dicts for every chart that has usable cached values."""
    z = zipfile.ZipFile(path)
    out = []
    for name in sorted(z.namelist(),
                       key=lambda n: int(re.findall(r"\d+", n)[0]) if re.match(
                           r"xl/charts/chart\d+\.xml$", n) else 0):
        if not re.match(r"xl/charts/chart\d+\.xml$", name):
            continue
        xml = z.read(name).decode("utf-8", "replace")

        titles = re.findall(r"<c:title>.*?</c:title>", xml, re.S)
        title = re.sub(r"\s+", " ", text_of(titles[0]) if titles else "").strip()

        series = []
        for block in re.findall(r"<c:ser>.*?</c:ser>", xml, re.S):
            label = re.findall(r"<c:tx>.*?<c:v>([^<]*)</c:v>", block, re.S)
            vals_block = re.findall(r"<c:val>.*?</c:val>", block, re.S)
            cats_block = re.findall(r"<c:cat>.*?</c:cat>", block, re.S)

            values = []
            if vals_block:
                for raw in re.findall(r"<c:v>([^<]*)</c:v>", vals_block[0]):
                    try:
                        values.append(float(raw))
                    except ValueError:
                        values.append(None)

            cats = re.findall(r"<c:v>([^<]*)</c:v>", cats_block[0]) if cats_block else []

            if values:
                series.append({
                    "label": (label[0].strip() if label else ""),
                    "values": values,
                    "cats": cats,
                })

        if series and title:
            out.append({"file": name, "title": title, "series": series})
    return out


def classify(title):
    """Returns (club, kind, unit, short_label)."""
    t = re.sub(r"\s+", " ", title).strip()

    if "Membership Trends" in t or "# of Full Privilege Members" in t:
        club = t.split(" - ")[0]
        return club, "members", COUNT, "Full privilege members"

    if "Monthly Dues" in t:
        club = t.split(" - ")[0]
        return club, "dues", MONEY, "Monthly dues line revenue"

    if "Attrition Rates" in t:
        # The workbook is inconsistent here. Most read "{Club} Sales & Attrition
        # Rates", but five drop the word Sales and read "{Club} & Attrition
        # Rates", which naively parses the club as "Bear Creek &". Split on the
        # part that is always present, then peel off whatever connector is left.
        left = re.split(r"Attrition Rates", t)[0]
        left = re.sub(r"\s*(?:Sales)?\s*(?:&|and)\s*$", "", left, flags=re.I)
        left = re.sub(r"\s*Sales\s*$", "", left, flags=re.I)
        return left.strip(), "rates", PERCENT, "Sales and attrition, full privilege"

    club = t.split(" - ")[0]
    return club, "other", COUNT, t


# The same club is titled two ways across chart families. Map the variants onto
# one identity so the T2.2 picker cannot end up with two entries for one club.
ALIASES = {
    "huntington": "huntington-club",
}

# Genuinely a two club comparison, not a club. Kept, but not counted as a club.
COMBINED = {"pga-west-and-citrus"}

# Roll-ups rather than clubs.
NOT_A_CLUB = {"all-clubs"}


def slugify(s):
    s = re.sub(r"[‘’ʼ'`]", "", s)   # Eagle's -> Eagles
    s = s.replace("&", " and ")
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()
    return ALIASES.get(s, s)


# ---------------------------------------------------------------- helpers

def excel_date(serial):
    try:
        n = int(float(serial))
    except (TypeError, ValueError):
        return None
    if n < 3000:            # already a plain year like 2021
        return None
    return datetime.date(1899, 12, 30) + datetime.timedelta(days=n)


def fmt_money(v):
    a = abs(v)
    if a >= 1_000_000:
        return "$%.1fM" % (v / 1_000_000.0)
    if a >= 1_000:
        return "$%.0fk" % (v / 1_000.0)
    return "$%.0f" % v


def fmt_count(v):
    return "{:,.0f}".format(v)


def fmt_pct(v):
    return "%.0f%%" % (v * 100)


FORMATTERS = {MONEY: fmt_money, COUNT: fmt_count, PERCENT: fmt_pct}


def nice_ticks(lo, hi, want=4):
    """Rounded axis ticks that bracket the data."""
    if hi == lo:
        hi = lo + (abs(lo) or 1) * 0.1
    span = hi - lo
    raw = span / max(1, want - 1)
    mag = 10 ** int(("%e" % raw).split("e")[1])
    for mult in (1, 2, 2.5, 5, 10):
        step = mag * mult
        if step >= raw:
            break
    start = step * int(lo / step)
    if start > lo:
        start -= step
    ticks = []
    v = start
    while v < hi - step * 1e-9:
        ticks.append(v)
        v += step
    ticks.append(v)
    # The top tick MUST sit at or above the data maximum. Getting this wrong let
    # a scarlet line run straight off the top of the card.
    while ticks[-1] < hi:
        ticks.append(ticks[-1] + step)
    return ticks


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# ---------------------------------------------------------------- drawing

def render(chart, club, kind, unit, subtitle):
    series = [s for s in chart["series"] if any(v is not None for v in s["values"])]
    if not series:
        return None

    fmt = FORMATTERS[unit]
    flat = [v for s in series for v in s["values"] if v is not None]
    lo, hi = min(flat), max(flat)
    if unit in (MONEY, COUNT):
        lo = min(0, lo)                 # counts and money read against zero
    ticks = nice_ticks(lo, hi)
    ylo, yhi = ticks[0], ticks[-1]

    n = max(len(s["values"]) for s in series)

    def px(i):
        return PAD_L if n == 1 else PAD_L + (PLOT_W * i / float(n - 1))

    def py(v):
        if yhi == ylo:
            return PAD_T + PLOT_H / 2.0
        return PAD_T + PLOT_H * (1 - (v - ylo) / float(yhi - ylo))

    parts = []
    add = parts.append

    add('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
        'width="%d" height="%d" role="img" aria-label="%s, %s">'
        % (W, H, W, H, esc(club), esc(subtitle)))
    add('<rect width="%d" height="%d" rx="10" fill="%s" stroke="%s"/>'
        % (W, H, RISER, EDGE))

    # headings
    add('<text x="12" y="18" fill="%s" font-family="%s" font-size="13.5" '
        'font-weight="700">%s</text>' % (CREAM, FONT, esc(club)))
    add('<text x="12" y="31" fill="%s" font-family="%s" font-size="9.5">%s</text>'
        % (MUTE, FONT, esc(subtitle)))

    # y gridlines and labels
    for t in ticks:
        y = py(t)
        add('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" '
            'stroke-width="1"/>' % (PAD_L, y, W - PAD_R, y, EDGE))
        add('<text x="%d" y="%.1f" fill="%s" font-family="%s" font-size="10" '
            'text-anchor="end">%s</text>'
            % (PAD_L - 6, y + 3.5, DIM, FONT, esc(fmt(t))))

    # x labels. Dates get years only, and only a few of them.
    cats = series[0]["cats"]
    marks = []
    if cats:
        dates = [excel_date(c) for c in cats]
        if any(dates):
            seen = set()
            for i, d in enumerate(dates):
                if d and d.year not in seen and d.month <= 2:
                    seen.add(d.year)
                    marks.append((i, str(d.year)))
            if len(marks) > 6:
                keep = max(1, len(marks) // 5)
                marks = [m for j, m in enumerate(marks) if j % keep == 0]
        else:
            step = max(1, len(cats) // 6)
            marks = [(i, cats[i]) for i in range(0, len(cats), step)]

    for i, label in marks:
        if i >= n:
            continue
        x = px(i)
        add('<text x="%.1f" y="%d" fill="%s" font-family="%s" font-size="10" '
            'text-anchor="middle">%s</text>'
            % (x, H - 9, MUTE, FONT, esc(str(label))))

    colors = [SCARLET, GOLD]

    # single series gets a soft fill so the shape reads at a glance
    if len(series) == 1:
        pts = [(px(i), py(v)) for i, v in enumerate(series[0]["values"])
               if v is not None]
        if len(pts) > 1:
            area = "M%.1f,%.1f " % (pts[0][0], PAD_T + PLOT_H)
            area += " ".join("L%.1f,%.1f" % p for p in pts)
            area += " L%.1f,%.1f Z" % (pts[-1][0], PAD_T + PLOT_H)
            add('<path d="%s" fill="%s" opacity="0.14"/>' % (area, SCARLET))

    for si, s in enumerate(series):
        pts = [(px(i), py(v)) for i, v in enumerate(s["values"]) if v is not None]
        if len(pts) < 2:
            continue
        d = "M" + " L".join("%.1f,%.1f" % p for p in pts)
        add('<path d="%s" fill="none" stroke="%s" stroke-width="2" '
            'stroke-linejoin="round" stroke-linecap="round"/>'
            % (d, colors[si % len(colors)]))
        # last point marker plus its value
        lx, ly = pts[-1]
        add('<circle cx="%.1f" cy="%.1f" r="2.6" fill="%s"/>'
            % (lx, ly, colors[si % len(colors)]))

    # Legend for two series, latest value callout for one. Both sit top right,
    # measured from the right edge so they cannot run into the title.
    if len(series) > 1:
        labels = [(s["label"] or "series") for s in series]
        widths = [11 + 4 + int(len(t) * 5.4) for t in labels]
        x = W - PAD_R - sum(widths) - 12 * (len(labels) - 1)
        for si, t in enumerate(labels):
            add('<rect x="%.1f" y="14" width="11" height="3" rx="1.5" fill="%s"/>'
                % (x, colors[si % len(colors)]))
            add('<text x="%.1f" y="19" fill="%s" font-family="%s" '
                'font-size="10">%s</text>' % (x + 15, DIM, FONT, esc(t)))
            x += widths[si] + 12
    else:
        last = [v for v in series[0]["values"] if v is not None][-1]
        add('<text x="%d" y="19" fill="%s" font-family="%s" font-size="14" '
            'font-weight="700" text-anchor="end">%s</text>'
            % (W - PAD_R, GOLD, FONT, esc(fmt(last))))

    add("</svg>")
    return "\n".join(parts)


# ------------------------------------------------------------------- main

def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    workbook, outdir = sys.argv[1], sys.argv[2]
    manifest_path = sys.argv[3] if len(sys.argv) > 3 \
        else os.path.join(outdir, "graphs.json")
    # Where the browser will look for the SVGs, relative to the site root. Given
    # explicitly rather than guessed off the filesystem path.
    web_dir = sys.argv[4] if len(sys.argv) > 4 else os.path.basename(outdir.rstrip("/"))
    os.makedirs(outdir, exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(manifest_path)), exist_ok=True)

    charts = parse_charts(workbook)
    written, skipped, entries = [], [], {}

    for c in charts:
        club, kind, unit, subtitle = classify(c["title"])
        if not club:
            skipped.append((c["title"], "no club in title"))
            continue
        svg = render(c, club, kind, unit, subtitle)
        if svg is None:
            skipped.append((c["title"], "no usable values"))
            continue
        slug = slugify(club)
        name = "%s--%s.svg" % (slug, kind)
        with open(os.path.join(outdir, name), "w", encoding="utf-8") as fh:
            fh.write(svg)
        written.append(name)
        e = entries.setdefault(slug, {"name": club, "graphs": {}})
        e["graphs"][kind] = name
        # Prefer the longest spelling as the display name, so "Huntington Club"
        # wins over "Huntington".
        if len(club) > len(e["name"]):
            e["name"] = club

    clubs = {k: v for k, v in entries.items()
             if k not in NOT_A_CLUB and k not in COMBINED}

    # Manifest for the T2.2 club picker, so it never has to guess a filename.
    # `dir` is where the SVGs sit as the browser sees them, relative to the site
    # root, because the manifest no longer has to live beside the files. The
    # picker joins dir and a filename. It never builds a path from a slug.
    import json
    manifest = {
        "generated_from": os.path.basename(workbook),
        "dir": web_dir,
        "clubs": [
            {"slug": k, "name": entries[k]["name"], "graphs": entries[k]["graphs"]}
            for k in sorted(clubs, key=lambda s: entries[s]["name"].lower())
        ],
        "rollups": [
            {"slug": k, "name": entries[k]["name"], "graphs": entries[k]["graphs"]}
            for k in sorted(NOT_A_CLUB | COMBINED) if k in entries
        ],
    }
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")

    print("charts in workbook: %d" % len(charts))
    print("svg written:        %d" % len(written))
    print("svg dir:            %s" % outdir)
    print("manifest:           %s" % manifest_path)
    print("web dir in manifest: %s" % web_dir)
    print("skipped:            %d" % len(skipped))
    print("clubs:              %d" % len(clubs))
    print("roll-ups:           %d  (%s)"
          % (len(manifest["rollups"]), ", ".join(r["slug"] for r in manifest["rollups"])))
    print()
    incomplete = {k: v["graphs"] for k, v in entries.items() if len(v["graphs"]) < 3}
    if incomplete:
        print("missing one or more of the three graph types:")
        for k in sorted(incomplete):
            have = set(incomplete[k])
            print("  %-24s has %-22s missing %s"
                  % (k, ", ".join(sorted(have)),
                     ", ".join(sorted({"members", "dues", "rates"} - have))))
    if skipped:
        print()
        for t, why in skipped[:12]:
            print("  skipped %-52s %s" % (t[:52], why))


if __name__ == "__main__":
    main()
