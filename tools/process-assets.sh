#!/usr/bin/env bash
#
# Asset intake for the Membership Meeting Live Wall. ROADMAP T0.7.
#
# Takes a folder of raw images and turns it into repo-ready assets. Right size,
# right name, right folder. Run it again whenever Jeannette sends more.
#
# Usage:
#   tools/process-assets.sh attendees <input-dir> [-n]
#   tools/process-assets.sh graphs    <input-dir> [-n]
#   tools/process-assets.sh resources <input-dir> [-n]
#   tools/process-assets.sh brand     <input-dir> [-n]
#
#   -n   Dry run. Report what would happen and write nothing.
#
# What each kind does:
#   attendees   400x400 square, center cropped, JPG  -> assets/attendees/{slug}.jpg
#   graphs      max 1600px wide, aspect kept, PNG    -> assets/graphs/{slug}.png
#   resources   max 1600px wide, aspect kept, PNG    -> assets/resources/{slug}.png
#   brand       max 1600px wide, aspect kept, JPG    -> assets/brand/{slug}.jpg
#
# Use `brand` for photographs, never `resources`. PNG is right for a chart and
# badly wrong for a photo, where it can run ten times the size for no gain.
#
# Naming. Files are renamed to a slug: lowercase, hyphens, nothing else.
#   "Mike Akeroyd.JPG"       -> mike-akeroyd.jpg
#   "Akeroyd, Mike.heic"     -> mike-akeroyd.jpg      (Last, First gets flipped)
#   "Jose Pena.jpg"          -> jose-pena.jpg         (accents fold to ASCII)
#   "The Medallion Club.png" -> the-medallion-club.png
#
# Slugs are built in Python, not iconv. macOS stores filenames in decomposed
# Unicode and macOS iconv truncates at the first combining mark, so "Jose Pena"
# with accents came out as "jose" and lost the surname. Do not swap this back.
#
# For attendees, every file is cross-checked against data/roster.json when that
# file exists. Anything that does not match a roster slug is reported, and so is
# any roster entry left without a photo. Nothing is guessed. Nothing is silently
# dropped or silently overwritten.
#
# Uses sips, which ships with macOS. No Homebrew, no npm.

set -uo pipefail

readonly REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly ATTENDEE_PX=400
readonly WIDE_MAX_PX=1600
readonly JPEG_QUALITY=82

# Anything bigger than this gets flagged. A phone on ballroom wifi is loading
# roughly 90 headshots, so a fat file is a real cost, not a rounding error.
readonly WARN_BYTES_ATTENDEE=$((150 * 1024))
readonly WARN_BYTES_WIDE=$((600 * 1024))

DRY_RUN=0
MAP_FILE=""

# ---------------------------------------------------------------- helpers

die() { printf 'Error: %s\n' "$1" >&2; exit 1; }

usage() {
  cat <<'EOF'
Asset intake for the Live Wall.

  tools/process-assets.sh attendees <input-dir> [-n]   400x400 square JPG
  tools/process-assets.sh graphs    <input-dir> [-n]   max 1600px wide PNG
  tools/process-assets.sh resources <input-dir> [-n]   max 1600px wide PNG
  tools/process-assets.sh brand     <input-dir> [-n]   max 1600px wide JPG

  --map=<csv>   Rename map with columns file,slug. Filenames in a real drop are
                things like "20230130-Hinckley-0008_pp.jpg", which slugify to
                nonsense, so the map is how a verified roster gets applied.
                Any file missing from the map is reported and NOT written.

  -n   Dry run. Report what would happen and write nothing.

Files are renamed to a lowercase hyphenated slug. "Last, First" is flipped.
Attendee files are cross-checked against data/roster.json when it exists.
EOF
  exit 1
}

# Lowercase hyphenated slug. Flips "Last, First". Folds accents to ASCII.
readonly SLUG_PY='
import sys, re, unicodedata
s = sys.argv[1]
if "," in s:
    last, _, first = s.partition(",")
    s = first + " " + last
s = s.replace("&", " and ")
s = re.sub("[\u2018\u2019\u02bc\u0027\u0060]", "", s)
s = unicodedata.normalize("NFKD", s)
s = "".join(c for c in s if not unicodedata.combining(c))
s = s.encode("ascii", "ignore").decode()
print(re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower())
'
slugify() { python3 -c "$SLUG_PY" "$1"; }

# Echoes "WIDTH HEIGHT", or nothing if the file is not a readable image.
dimensions() {
  sips -g pixelWidth -g pixelHeight "$1" 2>/dev/null \
    | awk '/pixelWidth/{w=$2} /pixelHeight/{h=$2} END{ if (w && h) print w, h }'
}

human_size() {
  local bytes
  bytes="$(stat -f%z "$1" 2>/dev/null || echo 0)"
  awk -v b="$bytes" 'BEGIN{
    if (b >= 1048576) printf "%.1fMB", b/1048576
    else printf "%dKB", (b+1023)/1024
  }'
}

# Prints a titled bullet list, skipping empty entries. Silent if nothing real.
report_block() {
  local title="$1"; shift
  local -a items=()
  local x
  for x in "$@"; do [[ -n "$x" ]] && items+=("$x"); done
  (( ${#items[@]} )) || return 0
  printf '\n%s\n' "$title"
  printf '  - %s\n' "${items[@]}"
}

# ---------------------------------------------------------------- converters

# 400x400 center-cropped JPG. Scales the SHORT edge to 400 first so the crop
# only ever removes pixels and never pads with background.
convert_attendee() {
  local src="$1" out="$2" w="$3" h="$4" work rc
  work="$(mktemp -t mm26asset).${src##*.}"
  cp "$src" "$work" || { rm -f "$work"; return 1; }

  if (( w <= h )); then
    sips --resampleWidth "$ATTENDEE_PX" "$work" >/dev/null 2>&1 || { rm -f "$work"; return 1; }
  else
    sips --resampleHeight "$ATTENDEE_PX" "$work" >/dev/null 2>&1 || { rm -f "$work"; return 1; }
  fi

  sips -c "$ATTENDEE_PX" "$ATTENDEE_PX" "$work" >/dev/null 2>&1 || { rm -f "$work"; return 1; }
  sips -s format jpeg -s formatOptions "$JPEG_QUALITY" "$work" --out "$out" >/dev/null 2>&1
  rc=$?
  rm -f "$work"
  return $rc
}

# Max 1600px wide, aspect ratio kept, never upscales. Output format follows
# OUT_EXT: png for charts and line art, jpg for photographs.
convert_wide() {
  local src="$1" out="$2" w="$3" work rc
  work="$(mktemp -t mm26asset).${src##*.}"
  cp "$src" "$work" || { rm -f "$work"; return 1; }

  if (( w > WIDE_MAX_PX )); then
    sips --resampleWidth "$WIDE_MAX_PX" "$work" >/dev/null 2>&1 || { rm -f "$work"; return 1; }
  fi

  if [[ "$OUT_EXT" == "jpg" ]]; then
    sips -s format jpeg -s formatOptions "$JPEG_QUALITY" "$work" --out "$out" >/dev/null 2>&1
  else
    sips -s format png "$work" --out "$out" >/dev/null 2>&1
  fi
  rc=$?
  rm -f "$work"
  return $rc
}

# ---------------------------------------------------------------- arguments

KIND=""
INPUT_DIR=""
for arg in "$@"; do
  case "$arg" in
    -n|--dry-run) DRY_RUN=1 ;;
    --map=*)      MAP_FILE="${arg#--map=}" ;;
    -h|--help)    usage ;;
    attendees|graphs|resources|brand)
      [[ -z "$KIND" ]] || die "Only one kind at a time. Got '$KIND' and '$arg'."
      KIND="$arg" ;;
    *)
      [[ -z "$INPUT_DIR" ]] || die "Unexpected argument: $arg"
      INPUT_DIR="$arg" ;;
  esac
done

[[ -n "$KIND" ]]      || usage
[[ -n "$INPUT_DIR" ]] || die "No input folder given."
[[ -d "$INPUT_DIR" ]] || die "Input folder does not exist: $INPUT_DIR"
command -v sips    >/dev/null || die "sips not found. This script needs macOS."
command -v python3 >/dev/null || die "python3 not found. Needed for slug naming."

case "$KIND" in
  attendees) OUT_DIR="$REPO_ROOT/assets/attendees"; OUT_EXT="jpg" ;;
  graphs)    OUT_DIR="$REPO_ROOT/assets/graphs";    OUT_EXT="png" ;;
  resources) OUT_DIR="$REPO_ROOT/assets/resources"; OUT_EXT="png" ;;
  brand)     OUT_DIR="$REPO_ROOT/assets/brand";     OUT_EXT="jpg" ;;
esac

# ---------------------------------------------------------------- roster

declare -a ROSTER_SLUGS=()
ROSTER_FILE="$REPO_ROOT/data/roster.json"
ROSTER_LOADED=0

if [[ "$KIND" == "attendees" && -f "$ROSTER_FILE" ]]; then
  while IFS= read -r slug; do
    [[ -n "$slug" ]] && ROSTER_SLUGS+=("$slug")
  done < <(python3 -c '
import json, sys
try:
    data = json.load(open(sys.argv[1]))
except Exception as e:
    sys.stderr.write("Could not parse roster.json: %s\n" % e)
    sys.exit(0)
records = data if isinstance(data, list) else data.get("attendees", [])
for r in records:
    if isinstance(r, dict) and r.get("slug"):
        print(r["slug"])
' "$ROSTER_FILE")
  ROSTER_LOADED=1
fi

in_roster() {
  local needle="$1" s
  (( ${#ROSTER_SLUGS[@]} )) || return 1
  for s in "${ROSTER_SLUGS[@]}"; do
    [[ "$s" == "$needle" ]] && return 0
  done
  return 1
}

# ---------------------------------------------------------------- run

printf '\nAsset intake: %s\n' "$KIND"
printf '  from: %s\n' "$INPUT_DIR"
printf '    to: %s\n' "${OUT_DIR#"$REPO_ROOT"/}"
(( DRY_RUN )) && printf '  mode: DRY RUN, nothing will be written\n'
if [[ "$KIND" == "attendees" ]]; then
  if (( ROSTER_LOADED )); then
    printf 'roster: %d entries loaded for cross-check\n' "${#ROSTER_SLUGS[@]}"
  else
    printf 'roster: data/roster.json not found, skipping cross-check\n'
  fi
fi
printf '\n'

(( DRY_RUN )) || mkdir -p "$OUT_DIR"

declare -a DONE_SLUGS=() UNMATCHED=() FAILED=() UPSCALED=() SKIPPED=() COLLIDED=() OVERSIZED=() UNMAPPED=()
count=0

while IFS= read -r src; do
  base="$(basename "$src")"
  stem="${base%.*}"
  ext="$(printf '%s' "${base##*.}" | tr '[:upper:]' '[:lower:]')"

  case "$ext" in
    jpg|jpeg|jpe|jfif|png|heic|heif|tif|tiff|gif|bmp|webp) ;;
    *) SKIPPED+=("$base (unsupported type .$ext)"); continue ;;
  esac

  # Some files carry a doubled extension, "Walsh Trujillo.jpeg.JPG". Without
  # this the slug comes out as walsh-trujillo-jpeg.
  inner="$(printf '%s' "${stem##*.}" | tr '[:upper:]' '[:lower:]')"
  case "$inner" in
    jpg|jpeg|jpe|jfif|png|heic|heif|tif|tiff|gif|bmp|webp) stem="${stem%.*}" ;;
  esac

  slug="$(slugify "$stem")"

  # A rename map wins over slugifying. Real drops are named things like
  # "20230130-Hinckley-0008_pp.jpg", which slugifies to garbage. Supply
  # --map with columns file,slug and nothing is guessed.
  if [[ -n "$MAP_FILE" ]]; then
    mapped="$(python3 -c '
import csv, sys
want = sys.argv[2]
try:
    with open(sys.argv[1], newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if (row.get("file") or "").strip() == want:
                print((row.get("slug") or "").strip())
                break
except Exception:
    pass
' "$MAP_FILE" "$base")"
    if [[ -n "$mapped" ]]; then
      slug="$mapped"
    else
      UNMAPPED+=("$base")
      continue
    fi
  fi
  if [[ -z "$slug" ]]; then
    SKIPPED+=("$base (name produced an empty slug)")
    continue
  fi

  read -r w h <<<"$(dimensions "$src")"
  if [[ -z "${w:-}" || -z "${h:-}" ]]; then
    FAILED+=("$base (could not read dimensions, file may be corrupt)")
    continue
  fi

  # Two source files landing on one slug would silently overwrite. Refuse.
  collision=0
  if (( ${#DONE_SLUGS[@]} )); then
    for seen in "${DONE_SLUGS[@]}"; do
      if [[ "$seen" == "$slug" ]]; then
        COLLIDED+=("$base wants $slug.$OUT_EXT, already written this run. NOT written")
        collision=1
        break
      fi
    done
  fi
  (( collision )) && continue

  out="$OUT_DIR/$slug.$OUT_EXT"

  if [[ "$KIND" == "attendees" ]]; then
    short=$(( w < h ? w : h ))
    if (( short < ATTENDEE_PX )); then
      UPSCALED+=("$base is ${w}x${h}, short edge ${short}px is under ${ATTENDEE_PX}. Will look soft")
    fi
    if (( ROSTER_LOADED )) && ! in_roster "$slug"; then
      UNMATCHED+=("$base -> $slug")
    fi
  fi

  if (( DRY_RUN )); then
    printf '  would write  %-34s  from %s (%sx%s)\n' "$slug.$OUT_EXT" "$base" "$w" "$h"
    DONE_SLUGS+=("$slug")
    count=$((count + 1))
    continue
  fi

  ok=1
  if [[ "$KIND" == "attendees" ]]; then
    convert_attendee "$src" "$out" "$w" "$h" || ok=0
  else
    convert_wide "$src" "$out" "$w" || ok=0
  fi

  if (( ! ok )) || [[ ! -s "$out" ]]; then
    FAILED+=("$base (conversion failed)")
    rm -f "$out"
    continue
  fi

  read -r ow oh <<<"$(dimensions "$out")"
  out_bytes="$(stat -f%z "$out" 2>/dev/null || echo 0)"
  if [[ "$KIND" == "attendees" ]]; then
    warn_at=$WARN_BYTES_ATTENDEE
  else
    warn_at=$WARN_BYTES_WIDE
  fi
  if (( out_bytes > warn_at )); then
    OVERSIZED+=("$slug.$OUT_EXT is $(human_size "$out"), over the $(( warn_at / 1024 ))KB guide")
  fi

  printf '  %-34s  %5sx%-6s %8s   from %s (%sx%s)\n' \
    "$slug.$OUT_EXT" "$ow" "$oh" "$(human_size "$out")" "$base" "$w" "$h"

  DONE_SLUGS+=("$slug")
  count=$((count + 1))
done < <(find "$INPUT_DIR" -maxdepth 1 -type f ! -name '.*' | sort)

# ---------------------------------------------------------------- report

printf '\n%s\n' "----------------------------------------------------------------"
if (( DRY_RUN )); then
  printf '%d file(s) would be written. Nothing changed.\n' "$count"
else
  printf '%d file(s) written to %s\n' "$count" "${OUT_DIR#"$REPO_ROOT"/}"
fi

report_block "Could not process. These need a look:"       "${FAILED[@]:-}"
report_block "Skipped:"                                     "${SKIPPED[@]:-}"
report_block "Name collisions. Rename the source and rerun:" "${COLLIDED[@]:-}"
report_block "Upscaled from a small source:"                 "${UPSCALED[@]:-}"
report_block "Bigger than the size guide. sips cannot shrink a PNG much, so if
  these are photographs ask for line art, and if they are already line art
  install pngquant and rerun:"                               "${OVERSIZED[@]:-}"
report_block "Not in the rename map, so NOT written. Add them or drop --map:" "${UNMAPPED[@]:-}"
report_block "No matching roster entry. Check the spelling:" "${UNMATCHED[@]:-}"

# Roster entries still without a photo, counting files already in the repo.
if [[ "$KIND" == "attendees" ]] && (( ROSTER_LOADED )); then
  declare -a MISSING=()
  for slug in "${ROSTER_SLUGS[@]}"; do
    [[ -s "$OUT_DIR/$slug.jpg" ]] || MISSING+=("$slug")
  done
  report_block "On the roster with no photo. Needs one or a placeholder:" "${MISSING[@]:-}"
  if (( ${#MISSING[@]} == 0 )) && (( ${#UNMATCHED[@]} == 0 )); then
    printf '\nEvery roster entry has a photo and every photo has a roster entry.\n'
  fi
fi

printf '\n'
if (( ${#FAILED[@]} )) || (( ${#COLLIDED[@]} )); then
  exit 1
fi
exit 0
