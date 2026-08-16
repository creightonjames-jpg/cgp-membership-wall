# Physical phone test

ROADMAP T0.8 and T3.6.

Live URL: https://creightonjames-jpg.github.io/cgp-membership-wall/

## Result

**The six device-only items were tested by Jim on Aug 13 2026. Five passed. The
sixth was not reported on.**

These are the things a desktop browser physically cannot prove, which is why they
needed a handset at all. Everything else on the wall has been checked in a browser
at 380px and at desktop width.

| # | Item | Result |
|---|---|---|
| 1 | Camera upload in The Pit, `capture="environment"` opens the camera | **Passed** |
| 2 | Library upload, the second input with no capture attribute | **Passed** |
| 3 | Tappable phone numbers, hotel and club, dialer pre-filled | **Passed** |
| 4 | Maps handoff, Apple Maps on iOS and Google Maps on Android | **Passed** |
| 5 | Fonts, Anton, Alfa Slab One and Inter arriving rather than falling back | **Passed** |
| 6 | Lazy image loading on cellular, 119 headshots and 28 booklet pages | Not reported |

## Still open, and worth being precise about it

**Which devices.** Jim confirmed the five items but did not say which handsets. T0.8
asks for three phones with at least one iOS and one Android, and T3.6 adds a tablet.
So the items are proven, the matrix is not.

**Cellular.** T3.6 asks for a pass on cellular data, not only wifi. That matters more
now than when it was written: the wall carries roughly 10MB of images, 5.4MB of
headshots and 4.4MB of booklet pages, all lazily loaded. Item 6 above is the same
question from the other side.

**Item 6 specifically.** Nobody has watched the lazy images load on a real handset.
It cannot be checked from here at all: the automated browser reports
`document.visibilityState` as hidden and Chrome refuses to trigger lazy loading for a
hidden page. The crew font check in the header will now say out loud if a font failed,
so item 5 stays observable at the venue, but lazy loading has no such readout.

## Anything else, quickly

Not device-dependent, and all verified in a browser at both widths rather than on a
phone:

- The Setlist, day pills, cards with detail open, cards without have no dropdown
- The Band, 119 cards, search and club filter, Century Golf first in Jim's order
- Backstage Pass
- Soundcheck, both pills, Questions and Liner Notes
- The Vault, Core Fundamentals booklet, Club Graphs, locked sections show countdowns
- Crowd Vote, The Pit, The Cares Cup, Encore, whichever the crew have switched on

## Report

Anything that failed, with the device and whether it was wifi or cellular:

```
Aug 13 2026, Jim: items 1 to 5 tested and passed. Devices not recorded.
```
