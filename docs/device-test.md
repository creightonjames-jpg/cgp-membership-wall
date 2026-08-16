# Physical phone test

ROADMAP T0.8 and T3.6. About twenty minutes per device.

Live URL: https://creightonjames-jpg.github.io/cgp-membership-wall/

**Why this cannot be skipped or done on a laptop.** Six things on this wall only
behave truthfully on a real handset. Everything else has been checked in a desktop
browser at 380px and at desktop width, so this list is deliberately short and it is
all the stuff a browser on a Mac physically cannot do.

## Devices

At minimum one iOS and one Android. A tablet if you have one. Do one pass on wifi
and one on cellular, because the booklet is 4.4MB and the headshots are another 5.4MB.

| Device | OS and browser | Who | Date |
|---|---|---|---|
| | | | |
| | | | |
| | | | |

## The six things

Tick each one, and write what happened if it is not a clean pass.

### 1. Camera upload, The Pit

- [ ] "Take a photo" opens the CAMERA, not a file browser
- [ ] The photo uploads and appears in the gallery
- [ ] "Choose from library" opens the photo library
- [ ] That photo uploads too

Both paths have to work. Camera-only was a real limitation on the previous build,
which is why there are two separate inputs.

### 2. Tappable phone numbers

- [ ] Backstage Pass, the hotel number opens the dialer with (614) 890-8600 in it
- [ ] The Medallion Club number opens the dialer with (614) 794-6999 in it

Nothing should need copying and pasting.

### 3. Maps handoff

- [ ] Tapping a venue pin offers Maps, not a web page in the browser
- [ ] The pin lands on the right address, not the middle of Columbus

### 4. Fonts

- [ ] Headings look like a rock poster, heavy condensed caps, not plain system text
- [ ] Award and Encore cards use the slab font
- [ ] Body text is Inter, not Times or the system default

If a heading looks ordinary, Anton did not load. Note whether you were on wifi or
cellular, because that is usually the difference.

### 5. Lazy loading, on cellular

- [ ] The Band: scrolling through 119 cards loads photos smoothly, no long blank gaps
- [ ] The Vault, Core Fundamentals: the 28 booklet pages load as you scroll
- [ ] The booklet download link opens the PDF in the phone's own viewer

This one is genuinely unverified. The automated browser reports itself hidden, and
Chrome refuses to trigger lazy loading for a hidden page, so nobody has watched
these load on a real device yet.

### 6. The QR code and the notch

- [ ] Scanning the printed QR lands on the welcome screen
- [ ] "Get your wristband" gets you into the wall
- [ ] Nothing is hidden behind the notch or the home bar, in portrait or landscape
- [ ] No sideways scrolling on any tab

## Everything else, quickly

Walk the nine tabs and confirm nothing is obviously broken:

- [ ] The Setlist, day pills switch, a card with detail opens, one without has no dropdown
- [ ] The Band, search and the club filter both work
- [ ] Backstage Pass
- [ ] Soundcheck, both pills, post a question and post a takeaway
- [ ] The Vault, Core Fundamentals and Club Graphs. Locked sections show a countdown
- [ ] Crowd Vote, The Pit, The Cares Cup, Encore, if the crew has switched them on

## Report

Anything that failed, with the device and whether you were on wifi or cellular:

```
```
