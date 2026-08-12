#!/usr/bin/env bash
# Process a drop of new headshots and re-match the roster. ROADMAP T3.1.
#
#   tools/add-headshots.sh [folder]      default: incoming/headshots
#
# Files must be named "First Last.ext" exactly as the person appears on the
# verified attendee list. The slug the pipeline derives has to match the slug
# the reconciler derives, or the photo lands on disk attached to nobody.
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
DROP="${1:-incoming/headshots}"

shopt -s nullglob
found=("$DROP"/*.[jJ][pP][gG] "$DROP"/*.[jJ][pP][eE][gG] "$DROP"/*.[pP][nN][gG] \
       "$DROP"/*.[hH][eE][iI][cC] "$DROP"/*.[jJ][fF][iI][fF] "$DROP"/*.[jJ][pP]2 \
       "$DROP"/*.[wW][eE][bB][pP] "$DROP"/*.[tT][iI][fF] "$DROP"/*.[tT][iI][fF][fF])
if (( ${#found[@]} == 0 )); then
  echo "Nothing to process in $DROP. Drop files named \"First Last.jpg\" and rerun."
  exit 0
fi
echo "Found ${#found[@]} file(s) in $DROP"
./tools/process-assets.sh attendees "$DROP" || exit 1
echo
echo "Re-matching the roster:"
python3 tools/reconcile-roster.py | sed -n '1,12p'
