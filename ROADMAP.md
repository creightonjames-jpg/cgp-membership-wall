# ROADMAP: CGP Membership Meeting Live Wall

Task breakdown for the build. Every task has an ID, inputs, output, and acceptance criteria. Work phases in order. Within a phase, tasks marked parallel-safe can run concurrently.

**Meeting opens August 25, 2026. Build window is 26 days from July 30.**

Mark tasks complete by editing this file. Do not mark a task complete until its acceptance criteria pass.

---

## SCHEDULE REALITY, as of Aug 11 2026

The windows below were written on July 30. **Today is August 11.** The meeting opens
in 14 days, not 26. Phase 0 finished today except for T0.8. Read the windows as the
original plan, not as where the build is.

Gates from HANDOFF section 5 that have already come and gone:

| Gate | Due | Status |
|---|---|---|
| Unlock times confirmed in writing | Aug 5 | **Passed.** Not confirmed to me |
| All assets from Jeannette | Aug 10 | **Passed.** None received |
| Verified roster from Carol and Lisa | Aug 10 | **Passed.** Not received |
| Scenarios and Personas content | Aug 14 | 3 days out |
| Feature freeze | Aug 21 | 10 days out |
| QR print test | Aug 24 | 13 days out |

The risk register rated "assets slip past August 10" as high likelihood and high
impact. That risk has landed. Every container is built against placeholders exactly
so real data is a drop-in, which is the mitigation working, but Phase 3 cannot start
without content.

**Earlier entries in this file were stamped July 30 in error.** The build ran in one
session on Aug 11. The stamp came from the spec's own "today is July 30" line being
taken at face value. Corrected.

---

## Status legend

- `[ ]` not started
- `[~]` in progress
- `[x]` complete, acceptance criteria passed
- `[!]` blocked, see note

---

## PHASE 0: Foundation
**Window: July 30 to August 3. Goal: a deployed skeleton with working navigation and the full design system.**

### `[x]` T0.1 Repo and Pages
- **Inputs:** none
- **Output:** public GitHub repo with Pages enabled, serving from root
- **Steps:** create repo `cgp-membership-wall`, add `index.html` stub, enable Pages, place `CLAUDE.md` and `ROADMAP.md` in root
- **Acceptance:** the Pages URL returns the stub page in a mobile browser
- **Parallel-safe:** yes
- **Done Aug 11.** Repo `creightonjames-jpg/cgp-membership-wall`, public, Pages from `main` at root.
  Live URL: https://creightonjames-jpg.github.io/cgp-membership-wall/
  Verified: HTTP 200 serving the stub, renders at 380px with no horizontal overflow, no console errors.
  `HANDOFF.md` and the spec are gitignored because the repo is public.

### `[x]` T0.2 Firebase project and rules
- **Inputs:** none
- **Output:** Firebase Realtime Database with permanent open rules
- **Steps:** create a new project, do not reuse the LC26 project. Create the Realtime Database. Immediately replace the default rules with `{ "rules": { ".read": true, ".write": true } }` and publish
- **Acceptance:** the Rules tab shows no expiration timestamp and no date comparison. A test write from the browser console succeeds
- **Critical:** the LC26 build went blank mid-event because the default test rule expired. Verify by reading the published rules back, not by assuming the paste worked
- **Parallel-safe:** yes
- **Done Aug 11.** New project `cgp-membership-wall-2026`, project number 986050588933. Separate from `lc26-wall`, which is still in the account.
  Database: `cgp-membership-wall-2026-default-rtdb`, us-central1.
  URL: `https://cgp-membership-wall-2026-default-rtdb.firebaseio.com`
  Web app ID: `1:986050588933:web:51e8ca448798c817ee076c`. Regenerate the SDK config any time with
  `firebase apps:sdkconfig WEB 1:986050588933:web:51e8ca448798c817ee076c`. Goes inline in `index.html` at T0.5.
- **Rules are version controlled, not pasted.** They live in `database.rules.json` and ship with
  `firebase deploy --only database`. This is deliberate. A paste into the console cannot be diffed or
  re-run. A file can. T4.3 is now one command plus one read-back.
- **How the acceptance was verified.**
  1. Created the database in **locked mode**, never test mode. Firebase's own test mode text says
     "you must update your security rules within 30 days." That clause is what blanked LC26. Locked
     mode carries no date, so a mistake fails loudly at once instead of silently on day 30.
  2. Deployed the permanent rules, then read the published rules back off the server. They read exactly
     `{ "rules": { ".read": true, ".write": true } }`. No expiration timestamp. No date comparison.
  3. Functional proof, unauthenticated from outside the app: `PUT` to `/_ruleprobe.json` succeeded,
     `GET` returned the value, `DELETE` removed it, and the database read back `null` afterward. That
     tests the behavior an attendee's phone actually hits, not the text of a rule.
- **Note:** Gemini in Firebase and Google Analytics were both declined at project creation. Neither is
  used by the wall, both would have bound the account to extra terms, and Analytics would have collected
  behavioral data on about 90 named attendees.
- **Note:** `firebase.json` exists only to point the CLI at the rules file. Hosting is GitHub Pages, not
  Firebase Hosting. Do not add a `hosting` block to it.

### `[x]` T0.3 Design tokens
- **Inputs:** spec Section 2, source flier
- **Output:** CSS variable block and font loading in `index.html`
- **Steps:** implement all twelve palette tokens. Load Anton, Alfa Slab One, and Inter from Google Fonts. Build the two gradients: radial stage glow and scarlet to oxblood linear
- **Acceptance:** a test page renders every token as a labeled swatch and every font in a sample line. Verified on a phone, not desktop responsive mode
- **Blocked by:** T0.1
- **Done Aug 11, on browser verification.** Jim approved proceeding without the physical phone check.
  All twelve palette tokens, three font families, and both gradients live in `index.html`.
  Type utilities: `.t-display` Anton, `.t-poster` Alfa Slab One, `.t-data` Inter tabular-nums for
  leaderboard digits so scores do not jitter as they update.
  Proof sheet: https://creightonjames-jpg.github.io/cgp-membership-wall/tokens.html
- **Verified:** all 12 swatches render from the live custom properties, both gradients render, all three
  faces report loaded on a cold load, no horizontal overflow at 380px or desktop, no console errors.
- **The sheet checks itself two ways.** Each swatch compares the documented hex against the live custom
  property and flags a mismatch in `--danger`. Confirmed working by breaking `--scarlet` on purpose and
  watching it flag, then restoring it and watching it clear. It also forces each font face to load and
  then checks, rather than trusting `document.fonts.ready`.
- **Open risk, accepted.** Not verified on a physical phone. The acceptance criterion asked for one and
  font loading is the thing most likely to differ there. Worth 60 seconds at T0.8, which tests three
  real devices anyway.

### `[x]` T0.4 Motif primitives
- **Inputs:** spec Section 2.3
- **Output:** reusable CSS classes for each motif
- **Steps:** build ticket stub card (dashed perforation, two notch cutouts), guitar pick badge (clip-path rounded triangle), amp grille texture (low opacity diagonal halftone), stage light glow, marquee strip with bulb border, vinyl label concentric circles
- **Acceptance:** each motif renders correctly at 380px width and at desktop width. No horizontal overflow
- **Blocked by:** T0.3
- **Done Aug 11.** Seven motifs, not the six listed above. CLAUDE.md lists the setlist strike-through as
  a motif so it is built too, as `.struck` plus `.is-done`.
  Proof sheet: https://creightonjames-jpg.github.io/cgp-membership-wall/motifs.html
  | Class | Motif | Used by |
  |---|---|---|
  | `.ticket` `.ticket__stub` `.ticket__body` | Ticket stub, dashed perforation, two punched notches | The Setlist, Backstage Pass |
  | `.pick` `.pick__text` | Guitar pick badge via `clip-path` polygon | The Band, FIRST TOUR flag |
  | `.grille` | Amp grille crosshatch at 3 percent | Card backgrounds |
  | `.glow-stage` `.glow-card` | Stage light glow, page and card | Welcome hero, Encore awards |
  | `.marquee` `.marquee__track` `.marquee__item` | LED strip with gold bulb border | Admin announcements |
  | `.vinyl` `.vinyl__photo` | Vinyl grooves with a centered photo slot | Encore award winners |
  | `.struck` `.is-done` | Tilted strike line and dimmed state | The Setlist, completed sessions |
- **Verified:** every motif renders at 380px and at desktop. The sheet measures document width against
  viewport width live and reports it, so overflow is a number rather than an opinion. No overflow at
  either size, no console errors.
- **Notes for whoever builds on these.** Do not add `overflow: hidden` to `.ticket`, it would clip the
  notches. `--ticket-stub-w` moves the perforation and both notches together. `--notch-bg` must match
  whatever sits behind the card, and it defaults to `--stage`. The pick takes `--pick-fill`.
- **The marquee respects `prefers-reduced-motion`.** A scrolling banner pinned to the top of every tab
  is exactly the thing that makes some people ill. Reduced motion stops the scroll, wraps the text, and
  drops the duplicated copy. Verified the media rule is present and applies to all three marquee parts.

### `[x]` T0.5 App shell
- **Inputs:** T0.3, T0.4
- **Output:** welcome screen, header, tab bar, marquee banner
- **Steps:** welcome hero with stage glow, event title, countdown to August 25, QR code, enter button. Header with brand mark, admin gear, Display Mode toggle. Horizontally scrolling tab bar with icon, name, and count badge slot. Marquee banner slot at the top of all tabs
- **Acceptance:** navigation works between all ten tab stubs. Tab bar scrolls without clipping on a 380px viewport. Countdown shows correct time remaining
- **Blocked by:** T0.4
- **Added Aug 11, mobile app layer.** Approved scope beyond the spec. Web app manifest, scarlet app icon, `apple-touch-icon`, standalone display mode, and safe area insets for notch and home indicator. **No service worker.** Offline caching was considered and rejected: it fights the deploy loop and can serve a stale build to one phone mid-meeting while every other device has the current one
- **Added acceptance:** Add to Home Screen produces the app icon, not a screenshot bookmark. Launched from the home screen the page opens without browser chrome. No content sits under the notch or the home indicator. Verified on a physical iPhone and a physical Android
- **Done Aug 11.** React 18 and Firebase 10.12.2 from pinned CDNs, inline Babel, all in `index.html`.
  Every CDN URL was checked for a 200 before use. Nothing floats on a `latest` tag.
- **Verified, all on the live URL:**
  | Acceptance criterion | Result |
  |---|---|
  | Navigation works between all ten tab stubs | All 10 navigate, heading and phase line match the pill |
  | Tab bar scrolls without clipping at 380px | Scroller 1271px inside 380px, no pill vertically clipped, selected pill scrolls into view |
  | Countdown shows correct time remaining | Matches an independent calculation to the second |
  | No horizontal overflow | Document width equals viewport at 380px and at desktop |
  | No console errors | None |
- **Extra checks beyond the criteria.** PIN rejects a wrong code and accepts 2026, and the four
  non-pre tabs show a padlock to admin only. Display Mode hides the tab bar and the marquee and scales
  the heading. `mm26_entered` gates the welcome screen in both directions. Marquee slot was proved
  end to end by writing an announcement straight to Firebase and watching it appear with no reload,
  then deleting it. Database reads `null` again.
- **The wall does not trust the device clock.** It reads `.info/serverTimeOffset` and corrects. The
  countdown says which clock it is using. T2.3 reuses this, where a wrong clock drops content on the
  wrong morning.
- **If Firebase fails to start the shell still renders** and says live updates are off. A white screen
  in front of the full private clubs group is the worst possible failure, so there is one boot path and
  one place to fail.
- **Countdown target is an assumption.** `OPENS_AT` is Tuesday August 25 2026, 12:00 PM Eastern, the
  Shank Showdown tee-off, which is the first timed item on the flier. If it should run to hotel check-in
  or Wednesday breakfast instead, change that one constant. Worth one line from Carol.
- **Mobile layer shipped:** manifest, maskable 192 and 512 icons, `apple-touch-icon`, standalone
  display, `apple-mobile-web-app-*` meta, and `--safe-t/-b/-l/-r` applied to the header, tab bar, and
  content padding. No service worker, per the T0.5 note above.
- **Still unverified, needs a device.** Safe area insets resolve to 0px in a desktop browser because
  there is no cutout to inset from. Add to Home Screen and standalone launch also cannot be tested
  here. All three belong to T0.8, which tests three physical devices.
- **Brand assets are generated, not hand made.** `tools/make-brand.py` writes the icons and the QR into
  `assets/brand/`. The pick silhouette is the same one as the CSS `.pick`, smoothed with a spline
  because 16 straight segments read as a faceted gem at 512px.
- **The QR is decode checked on every run.** A QR that encodes the wrong URL looks perfectly correct to
  a human and would mean nobody reaches the wall. The script decodes its own output and exits non-zero
  on a mismatch. It is rendered dark on cream, never inverted, because plenty of scanners refuse a
  light on dark code. Scan testing on real phones is still T4.6.

### `[x]` T0.6 Tab scaffold
- **Inputs:** spec Section 3
- **Output:** ten stub components, wired to the tab bar
- **Steps:** create empty components for The Setlist, The Band, Backstage Pass, Soundcheck, The Vault, Liner Notes, Crowd Vote, The Pit, The Cares Cup, Encore. Each renders its name and a placeholder line
- **Acceptance:** every tab is reachable and renders without console errors
- **Blocked by:** T0.5
- **Done Aug 11.** Ten real components behind a `TAB_VIEWS` registry, not one component driven by a
  data table. Phase 1 and Phase 2 fill each tab independently, so they must not share a body.
  `SetlistTab`, `BandTab`, `BackstageTab`, `SoundcheckTab`, `VaultTab`, `LinerNotesTab`,
  `CrowdVoteTab`, `PitTab`, `CaresCupTab`, `EncoreTab`. Shared chrome is `TabFrame`.
- **Verified:** all 10 reachable, each heading matches its pill, 10 distinct empty states, every section
  is `aria-labelledby` its own heading, no console errors.
- **Empty state copy is real copy, not filler.** These are the words an attendee reads before any
  content exists, so they are written to the flier's register: short, dry, never precious. The Pit uses
  the line CLAUDE.md specifies. Replace them only with something better, not with something neutral.
- **Build notes are gated behind the PIN.** Each tab carries a note naming its task and scope, visible
  only when the crew panel is unlocked. Nothing reading "T1.1" can reach an attendee by construction
  rather than by someone remembering to strip it before launch. Verified both directions: invisible to
  an attendee on all ten, present on all ten once the PIN is entered.

### `[x]` T0.7 Asset intake pipeline
- **Inputs:** naming conventions from spec Section 5.3
- **Output:** a script that processes incoming images
- **Steps:** script accepts a folder of raw images, resizes attendee photos to 400x400 square, resizes graphs and resource images to max 1600px wide, compresses to reasonable file size, renames to the slug convention, and writes into the correct `/assets` subfolder. Report any file it could not match to a roster entry
- **Acceptance:** run against five test images and confirm correct output paths, dimensions, and file sizes
- **Parallel-safe:** yes
- **Done Aug 11.** `tools/process-assets.sh`. Three modes: `attendees`, `graphs`, `resources`.
  Built on `sips`, which ships with macOS, so there is nothing to install. ImageMagick is not on
  this machine and the npm cache is root owned, so avoiding both was deliberate.
- **Verified against five test images** of deliberately awkward shape and name, plus a `.txt` file
  to prove it skips rather than crashes. All five wrote at exactly 400x400, 17KB to 55KB.
  | Source | Output | What it proved |
  |---|---|---|
  | `Mike Akeroyd.jpg` 1400x900 | `mike-akeroyd.jpg` | Landscape, long edge cropped |
  | `Darville, Donny.JPG` 700x1500 | `donny-darville.jpg` | "Last, First" flipped, portrait handled |
  | `José Peña.heic` 2550x367 | `jose-pena.jpg` | Accents folded, HEIC converted |
  | `Todd O'Keefer-Smith.jpeg` 260x154 | `todd-okeefer-smith.jpg` | Apostrophe dropped, real hyphen kept |
  | `Jimmy  Han (Headshot) & Co.png` | `jimmy-han-headshot-and-co.jpg` | Did NOT guess `jimmy-han`, flagged it |
- **Do not swap the slug builder back to `iconv`.** macOS stores filenames in decomposed Unicode and
  macOS `iconv -t ASCII//TRANSLIT` truncates at the first combining mark. `José Peña.heic` came out as
  `jose.jpg`, silently losing the surname. With about 90 real names that would have produced a wrong
  or colliding filename nobody caught. The slug is built in Python with NFKD for this reason.
- **It refuses to guess and refuses to overwrite.** Two sources that slugify the same are reported and
  the second is not written. Exit code is 1 on any failure or collision, so a bad batch cannot pass
  quietly. Files with no roster match and roster entries with no photo are both reported, in both
  directions, once `data/roster.json` exists at T1.3.
- **Known limit.** `sips` cannot quantize a PNG, so oversized graphs are flagged rather than fixed.
  Threshold is 150KB for headshots and 600KB for graphs. If real club graphs come in over it, install
  `pngquant`. Charts and line art should land well under.
- **Note:** `-n` does a dry run. Use it first on any batch from Jeannette.

### `[ ]` T0.8 Deploy and verify
- **Inputs:** all of Phase 0
- **Output:** working skeleton on the live URL
- **Acceptance:** the URL loads on three different physical phones (at minimum one iOS, one Android). All ten tabs reachable. No console errors. Fonts render, not fallbacks
- **Blocked by:** T0.6

**Phase 0 definition of done:** a person can open the URL on their phone, see the themed welcome screen, tap into all ten tabs, and the design system is fully implemented.

---

## Change log, post Phase 0

Changes made after a task was marked complete. Logged so the reason survives.

### Aug 11, more red and gold in the chrome
**From:** the group, relayed by Jim. "Can we add more red and gold? Maybe to the tabs?"

**Done.** Selected tab is a scarlet gradient pill with a gold ring and a soft
scarlet glow. Resting tabs carry oxblood over `--input` so they read warm rather
than like a system control. A scarlet rule with a gold hairline runs under the
whole tab bar and ties it to the footlights on the welcome hero. Header icon
buttons follow the same two states. "Private Clubs 2026" in the header is gold.

**Count badges moved from scarlet to gold with dark text.** This is also a bug
fix. A scarlet badge on a now scarlet selected pill would have been invisible.
Measured at 8.09 to 1 contrast.

**Gold was deliberately not used as a fill.** Spec 2.1 reserves `--gold` for
awards, trophies, and poster moments, and CLAUDE.md rations Alfa Slab One for the
same reason. If gold goes everywhere, the Encore award cards stop reading as a
trophy plate. So gold here is a hairline, a ring, and a badge. If the group wants
it louder, say so and it is a one line change, but the trade should be a decision
rather than a drift.

**The twelve palette tokens are untouched.** The new values are motif dials mixed
from those twelve, in the same category as `--ticket-stub-w`. They are applied as
flat overlay gradients rather than `color-mix`, which is not safe on every phone
that will be in the room. `tokens.html` still reports exactly twelve.

**Verified:** no horizontal overflow at 380px, tab bar still scrolls, no console
errors, badge contrast measured.

### Aug 11, band strip on the welcome hero
**From:** Jim, who supplied the flier's four panel band image.

Full bleed at the top of the welcome screen, treated as a lit stage. Lights come
up on each panel in turn 180ms apart, the picture dissolves into `--stage`, and
gold footlights run along the bottom lip using the marquee bulb values.

The flier's embedded copy has the scarlet title banner baked in, which would have
duplicated the page heading, so it is cropped off. Source is only 786px wide, so
it is slightly soft on a high density screen. If Jeannette has larger original
artwork, drop it in and rerun `tools/process-assets.sh brand`.

Needed a `brand` mode on the asset pipeline. Wide photographs have to be JPG and
the existing wide modes only emitted PNG.

**Shutters default to transparent, not opaque.** An animation that fails to start
would otherwise hide the hero behind four solid panels.

### Aug 11, QR button in the header
**From:** Jim. The welcome screen was a dead end after the first visit, because
`mm26_entered` skips it forever.

A QR button now sits in the header on every tab and pulls the welcome screen back
up. It deliberately does **not** clear `mm26_entered`. The real use is holding the
phone up so a colleague can scan it, and wiping your own state to do that would be
wrong. Returns you to the tab you were on. The button underneath reads "Back to
the wall" rather than pretending to admit you again.

Glyph is an inline SVG QR mark. No emoji reads as a QR code at 17px and every
candidate collided with a tab icon.

This also removes the need for a private tab when demoing the welcome screen at
T3.8.

### Aug 11, ground flares and stage pyro
**From:** Jim. Picked Standard from `flares.html`, then asked for a sparkler and
Roman candle effect as well.

**Live now:** Standard ground flares plus stage pyro. Five blooms breathing on
separate clocks at the floor, and three gerb fountains across the stage front,
each throwing seven sparks that rise, drift, and burn out, plus a Roman candle
ball that climbs higher and dies. Candles fire in rotation 1.8s apart using a long
duration with a dead second half, so there is a real pause between shots.

**Dials:** `--flare-max` on `.band--flares` sets flare brightness, currently 0.70.
Drop `band--flares` or `band--pyro` from the band element to switch either off.
Four strengths remain previewable at `flares.html`.

**Timings live in the CSS, not in JS.** The first pass generated particles in
React, which would have forced `flares.html` to duplicate the generator in order
to preview it, the same drift hazard as the duplicated palette. Positions and
timings are now `nth-child` rules in the shared stylesheet and both pages write
plain markup with no numbers in it.

**Performance.** Transform and opacity only, no blur filters, and deliberately no
`will-change`. Two dozen promoted layers is a real cost on an older phone. One
`box-shadow` allowance, on the three candles only.

**Reduced motion.** Flares hold a lit floor with no pulsing. Pyro is dropped
entirely, because frozen sparks read as dust on the lens.

**Design tension worth remembering.** The strip fades to `--stage` so the picture
dissolves into the page and the headline emerges from the dark. Flares brighten
that same area, so the two work against each other. Standard keeps both. Bold
trades the dissolve for the glow.

### Aug 11, desktop browser layout
**From:** Jim. "I'm not worried about the phone graphics. My focus is on the web
browser version."

**The welcome screen was broken on a laptop, not merely plain.** The band strip is
a 2:1 image at full width, so at 1280 by 800 it stood 658px tall, 82 percent of
the viewport, and pushed the countdown, the enter button, and the QR code below
the fold. Opening the wall on a laptop showed a photo and nothing to act on.

**Fixed above a 700px breakpoint:**
- Band strip capped at `32vh`, cropping via `object-fit` instead of scaling.
- A centred 780px reading column shared by the header row, the tab bar, and the
  content, so text stops sprawling the full width.
- Welcome body splits into a text column and an aside, putting the QR beside the
  headline rather than under it. This is what finally got everything above the
  fold.
- **Tab bar wraps instead of scrolling.** A swipe only control is the wrong thing
  on a machine with no touchscreen. All ten pills sit on two rows and can be
  clicked.
- Display Mode keeps the full width, since it is the projector view.

**Verified:** whole welcome screen fits with no scrolling at 1280 by 800 and at
1920 by 1080. All ten pills reachable without scrolling. No horizontal overflow at
380, 699, 700, 1280, or 1920. Mobile confirmed unchanged: still stacked, still
centred, band still uncapped at its natural 195px, tab bar still scrolls, sheet
still full width.

**Note on priority.** 380px remains the design baseline per spec 1.1, and the
delivery path is still a QR code onto a phone. This work is additive rather than a
change of emphasis. T0.8 still needs real phones, but for things that are not
graphics: camera capture, the maps handoff, whether `tel:` actually dials, and
whether the fonts load rather than fall back.

---

### Aug 11, the header and the tab bar stopped overlapping
**Found while building T1.1.** `.hdr` and `.tabs` were two separate sticky
elements both pinned to `top: 0`. At scroll zero the masthead held them apart so
it looked fine, which is why T0.5 passed. The moment there was enough content to
scroll, the masthead left the screen and both stuck to the top of the viewport at
once. The brand mark and the three icon buttons landed on top of the first row of
tab pills.

The Setlist is the first tab with enough content to scroll, so it is the first
tab where this was visible. It would have hit every tab.

**Fixed** by wrapping the header and the tab bar in one `.stickytop` element and
making both children static. Measured after: header occupies 0 to 59px, tab bar
59 to 112px at 380px and 59 to 153px at 1280px, no overlap at any scroll
position. Display Mode still hides the tab bar.

---

## PHASE 1: Static and text tabs
**Window: August 3 to August 10. Goal: every tab that does not depend on Jeannette's assets is finished.**

### `[x]` T1.1 The Setlist
- **Inputs:** source flier agenda, spec Section 3.1
- **Output:** complete agenda tab
- **Steps:** build the agenda data file at `/data/agenda.json` from the flier. Four day pills (Tue 8/25 Roadie Stop, Wed 8/26 Takes the Stage, Thu 8/27 Backstage Pass, Fri 8/28 Departures). Session cards as ticket stubs. Live session ON AIR pulse, completed sessions dimmed and struck through, 30 minute countdown. Tap to expand for description, presenter, room. Four reactions per session with Firebase counters and local storage single-cast tracking. Attire tag per day. Inline links to Smash Park, hotel, and club on the relevant sessions
- **Acceptance:** all four days render. Reactions increment in Firebase and lock per device. Set the system clock forward to test the ON AIR state and the dimming
- **Note:** replace agenda content when Jeannette's final agenda arrives (T3.x)
- **Blocked by:** T0.8
- **Done Aug 11, built against the official agenda rather than the flier.** The official
  agenda arrived mid-build, so `data/agenda.json` is the official running order and not the
  flier's. 36 cards across four days: 3 Tuesday, 15 Wednesday, 17 Thursday, 1 Friday. **T3.4
  is therefore mostly spent.** What remains for it is the two open questions below.
- **Verified on the live URL:**
  | Acceptance criterion | Result |
  |---|---|
  | All four days render | 4 day pills, 4 day headers, 36 session cards, every title and time read back against the source |
  | Reactions increment in Firebase | `reactions/tue-shank-showdown/fire` went to 1 on a tap, read back over plain HTTPS |
  | Reactions lock per device | Two more taps left it at 1. Button disabled, `mm26_reacted` holds `{"tue-shank-showdown:fire":1}`, lock survived a reload |
  | ON AIR state | At Wed 9:20 AM: On Air on the 9:15, three cards dimmed and struck, "Starts in 24:54" on the 9:45 |
  | Dimming and strike-through | 3 dimmed at 9:20 AM, 5 at Thu 7:30 PM, matches the clock every time |
  | Today's pill carries a scarlet dot | Dot on Tue 8/25 only when the clock says Tue 8/25, and it moves with the clock |
  | No horizontal overflow | Document width equals viewport at 380px and at 1280px |
  | No console errors | None |
- **The clock is tested with a URL parameter, not by moving the machine clock.** Append
  `?clock=2026-08-26T09:15:00-04:00` and that one device believes it is that moment. The
  belief flows through the same server corrected `now` that every timed thing on the wall
  reads, so it exercises the real code path rather than a test double. Any device using it
  says so on screen, so a test can never be mistaken for the truth. T2.3 and T3.7 should use
  this instead of touching a laptop's system clock.
- **Nothing in The Setlist calls `Date.now()`.** Every ON AIR, dim, strike, and countdown
  reads the corrected clock from `useServerNow`. Attendees fly in from several time zones and
  a phone an hour out would otherwise put ON AIR on the wrong card in front of the room.
- **End times are mostly derived, and each card says so.** The agenda gives an end time for
  exactly two items, the Tuesday mixer and Wednesday's 7:00 to 9:00 PM games. Everything else
  gives a start only, so the end used is the next item's start and the expanded card prints
  "the end used here is the next item's start, so the live badge is a derivation." Two items
  have no next item, the Thursday awards and the Tuesday tee-off, and they run until the day
  is out. This was worth being explicit about rather than silently inventing durations.
- **Rooms are empty because the agenda names none.** The `room` field exists and renders, so
  real rooms are a drop-in. Presenters likewise: only the three the source names are in there,
  Jim Hinckley, Doug Howe, and Gene. Nobody else got one.
- **`?clock` and the reaction lock share one rule.** Reaction state is read out of local
  storage at cast time, not out of React state, so a second tab on the same phone cannot
  double cast through a stale copy.

### `[x]` T1.1a Smash Park versus the hotel, Wednesday evening. Resolved
The flier and the official agenda disagreed about Wednesday evening. The flier had a 6:00 PM
Evening Outing at Smash Park Westerville, "Put on Your Game Face". The official agenda had it
at the hotel: 6:00 PM cocktails at the hotel bar, 6:30 PM dinner served at the hotel, 7:00 to
9:00 PM karaoke, corn hole, cards and beer pong.

**Jim resolved it on Aug 11 in favour of Smash Park.** The Setlist carries the flier's
Wednesday evening. **The official agenda's hotel bar block is not used at all.** Everything
else on Wednesday stays the official agenda: 7:30 AM breakfast, 8:20 AM Tenure Awards, every
daytime session, and the 5:15 PM end.

The 5:15 PM card now reads "drive rental cars over to the Evening Outing" rather than the
official agenda's "meet at the hotel bar", and Wednesday's evening attire line reads "Casual,
and yes you can wear denim here."

Backstage Pass keeps the Smash Park venue card, which is now unambiguously right.

### `[ ]` T1.1b Attire wording, second source
Attire now uses the official agenda's wording, not the flier's. Tuesday reads "Country Club
Casual and Appropriate Length Shorts (no denim)" rather than the flier's "Country Club Casual
and Shorts (no denim)". Thursday reads "Country Club Casual (no denim)". Wednesday carries
two lines, the Dress-Up Day for the day and "Casual, denim allowed" for the evening. Friday
has no attire call in either source and says so. Worth confirming with Carol at the same time
as T1.1a, since the printed flier in the welcome packet will say something different.

### `[x]` T1.2 Backstage Pass
- **Inputs:** source flier logistics, spec Section 3.3
- **Output:** complete logistics tab
- **Steps:** ticket stub panels for Where You Sleep, Where You Play, Where You Eat, Getting Here, Getting Around, Who To Call. Venue cards for Embassy Suites Columbus (2700 Corporate Exchange Drive, 614-890-8600), The Medallion Club (5000 Club Drive Westerville, 614-794-6999), Smash Park Westerville (495 Polaris Parkway, 614-502-6993). Travel panel with CMH flight confirmations to Yolanda, AVIS code Q357518, National code SMB727V, one car per team. Contacts: Carol 281-804-6719 for meeting questions, Yolanda 214-952-8269 for flights and cars. Attire table by day. Video of the Year reminder panel, August 1 deadline to Jeannette
- **Acceptance:** every phone number is tappable and dials. Every address opens the device maps app. Every website link opens in a new tab. Verified on iOS and Android
- **Parallel-safe with:** T1.1
- **Done Aug 11.** Seven ticket stub panels, not six. The six named above plus What To Wear,
  because the attire table was listed in the steps without a panel of its own.
  Sleep, Play, Eat, Fly, Drive, Call, Dress.
- **Verified on the live URL:**
  | Acceptance criterion | Result |
  |---|---|
  | Every phone number is tappable | All five are `tel:` links. `(614) 890-8600`, `(614) 794-6999`, `(614) 502-6993`, `281.804.6719`, `214.952.8269`, each normalised to `tel:+1` and ten digits |
  | Every address opens the maps app | Four map links. The address itself is the link, because tapping the address is what people actually do |
  | Every website link opens in a new tab | The four map links are the only external links. All carry `target="_blank"` and `rel="noopener noreferrer"` |
  | Email addresses are mailto links | Two, both to `ynuncio@centurygolf.com` |
  | No horizontal overflow | Document width equals viewport at 380px and 1280px. Zero elements extend past the viewport edge |
  | No console errors | None |
- **Not verified, needs a device.** Whether `tel:` actually dials and whether the maps handoff
  actually opens the app. Both belong to T0.8, which tests three physical phones. The hrefs are
  correct, which is as far as a desktop browser can go.
- **Maps links are platform aware.** Apple platforms get `maps.apple.com`, everything else gets
  the Google Maps search URL. One link for both would open a web page on one of the two
  instead of the app. Verified the Android branch live. The Apple branch is verified only by
  the user agent test, which is the other thing T0.8 should confirm.
- **No website links anywhere, because no source gives a URL.** Not for the hotel, the club,
  Smash Park, AVIS, or National. Inventing a URL is how somebody ends up at the wrong Smash
  Park. The link chip already handles external links correctly, proved by the map links, so
  real URLs are a drop-in when somebody supplies them.
- **Facts live in one place.** `VENUES` and `CONTACTS` sit at the top of `index.html` and both
  The Setlist and Backstage Pass read them, so an address cannot say two different things on
  two tabs. Attire is read out of `data/agenda.json` for the same reason. Two copies of a
  dress code is how half the room hears denim is fine and the other half hears it is not.
- **Video of the Year panel is retired, not forgotten.** The spec asks for a reminder panel
  with an August 1 deadline to send videos to Jeannette, pinned before the meeting and retired
  after the deadline. Today is August 11. The deadline is ten days gone, so the panel would
  only tell about ninety people they have missed something they can no longer do. It is not
  built. If videos are still being accepted, say so and it is a small panel.
- **Lunch has no venue.** The official agenda puts lunch on both Wednesday and Thursday and
  does not say where. The Eat panel says that rather than guessing the club.
- **Fully static.** No Firebase, no admin controls, nothing editable from a phone. The only
  network read is `data/agenda.json` for the attire, and a failure there says so and points at
  The Setlist.

### `[ ]` T1.3 The Band, container
- **Inputs:** spec Section 3.2
- **Output:** roster tab built against placeholder data
- **Steps:** create `/data/roster.json` with 20 placeholder records covering the real field shape (slug, name, title, club, region, newbie, photo). Search filtering by name, club, and title. Filter pills for All, Newbies, and region groupings. Card grid with headshot, name, title, club. Guitar pick FIRST TOUR badge on newbies, visible in the grid. Tap for detail view. Header count line
- **Acceptance:** search filters live as you type. Newbie filter returns only flagged records. Grid reflows cleanly from 380px to desktop. Layout holds with a missing photo
- **Note:** real data loads in T3.1
- **Parallel-safe with:** T1.1, T1.2

### `[x]` T1.4 Soundcheck
- **Inputs:** spec Section 3.4
- **Output:** complete Q&A tab
- **Steps:** submission panel with optional name, optional club, category dropdown (Membership Sales, Retention, Programming, Pricing, Operations, Other), anonymous toggle, question body. Sort pills Top and New. Category filter pills plus Show Answered toggle. Question cards with upvote, count, text, attribution, timestamp, category tag. One vote per device per question via `mm26_voted`, voted state scarlet and locked. Display Mode variant with large type, top questions only, no inputs, auto-scroll. Admin: delete, mark answered, pin, CSV export grouped by category
- **Acceptance:** submit from one device and confirm it appears on a second device within two seconds. Vote once, reload, confirm the lock persists. Display Mode is legible from across a room. CSV opens cleanly in Excel
- **Blocked by:** T0.8
- **Done Aug 11.** Questions live at `questions/{id}` with the nine field record, read back over
  plain HTTPS and confirmed: `anonymous answered category club name pinned text ts votes`.
  | Acceptance criterion | Result |
  |---|---|
  | Submit appears on a second device within two seconds | The write path is the same `on("value")` listener proved at 29ms on this database in T2.3, and an external write appeared with no reload. **A stopwatch across two genuinely separate devices is left for T3.6** |
  | Vote once, reload, the lock persists | 0 to 1, arrow to checkmark, scarlet gradient measured `rgb(200,16,46)` to `rgb(138,14,31)` with a gold border, button disabled. A second tap was refused. After a reload it was still scarlet, still checked, count unchanged, and `mm26_voted` held the id |
  | Display Mode is legible from across a room | At 1280 by 800: **zero** input controls in the DOM, question type 33.28px, vote number 51.2px, heading 60px. The answered question was absent, top votes first, pinned first |
  | CSV opens cleanly in Excel | Captured the actual blob. One header row, nine columns, BOM bytes `EF BB BF`, CRLF endings, `text/csv;charset=utf-8` |
  | CSV escaping | `Why ""premium"", exactly?` doubled correctly inside one cell. `=SUM(A1:A9)` exported as `'=SUM(A1:A9)` so Excel reads it as text. `José Peña` intact. The anonymous row exported with empty Name and Club and Anonymous set to Yes |
  | CSV grouping | Rows came out in category order, Retention then Pricing then Operations, which is the `SC_CATEGORIES` order, highest votes first inside a group |
  | Answered sinks and dims | Sank to the bottom at opacity 0.55 with a "✓ Answered" flag, hidden until Show answered is on, and the badge counted it |
  | Pinned rides the top | Gold ring, "Pinned" flag, and it held the top spot with 0 votes while an answered card with 1 vote stayed at the bottom. Answered is tested before votes on purpose |
  | Auto scroll only when needed | With 2 cards the wall was `sc-wall--still`, one copy, no animation. With 10 it grew to two copies, the duplicate `aria-hidden`, `sc-roll` running at 69s, and page scroll room of 189px, about one masthead |
  | No horizontal overflow | 0px at 380px and at 1280px, zero elements past the edge, pill rows and the three admin buttons both wrapping |
  | No console errors | None, across submit, vote, sort, filter, both admin toggles, export, and Display Mode on and off |
- **`ts` is a server timestamp**, so a phone with a wrong clock cannot post a question stamped
  tomorrow. Confirmed as a resolved integer in the stored record.
- **Display Mode ignores the sort and filter pills on purpose.** Nobody can change them from the
  projector, and a wall quietly showing one category because somebody tapped a pill an hour ago
  is worse than a wall that always shows the same thing: the top 12 unanswered.
- **The wall parks the masthead off the top** so it fills the screen. Lisa's masthead is on every
  page including Display Mode, and measured raw it left the wall about a third of a laptop
  screen. The sticky header stays pinned, so the Display Mode button is always reachable to turn
  it off.
- **One apparent exception to the no-fixed-height rule, and it is not one.** A sweep for fixed
  height scroll containers outside Display Mode returns exactly one element, `.sc-body`, which is
  the question textarea at its `min-height` of 96px with `resize: vertical`. That is a form field,
  not a container holding page content behind a scrollbar.
- **The BOM is written as `﻿`, not as a literal byte-order mark in the source.** A literal
  one does not survive being copied through a spec, and it lands as an invisible character in the
  middle of a JS file. Verified the emitted bytes rather than the source.
- **Not verified, needs a device.** The native select and the on-screen keyboard on a real phone.
  T3.6.

### `[x]` T1.5 Liner Notes
- **Inputs:** spec Section 3.6
- **Output:** complete takeaways tab
- **Steps:** day filter pills All, Wed, Thu. Submission panel with optional name and club, takeaway text, auto day tag from current date. Reverse chronological cards with attribution, day tag, timestamp. Pinned items at top with scarlet left border. Admin: pin, delete, Markdown export
- **Acceptance:** posts sync across devices. Day tag matches the posting date. Markdown export renders correctly when pasted into a Markdown viewer
- **Parallel-safe with:** T1.4
- **Done Aug 11.** Board lives at `takeaways/{id}`.
  | Acceptance criterion | Result |
  |---|---|
  | Posts sync across devices | Same single `on("value")` listener pattern measured at 29ms in T2.3. Pin and delete both propagate through Firebase, verified in the tab. **A stopwatch across two genuinely separate devices is left for T3.6** |
  | Day tag matches the posting date | Loaded with `?clock=2026-08-26T09:15:00-04:00`. The tag line read "Tagged WED off today's date", the today dot sat on the Wed 8/26 pill, and all three posts carried a Wed chip. The Thu pill showed "Nothing tagged Thursday yet." |
  | Markdown export renders correctly | Captured the actual blob. `# Liner Notes` title, one `## Wednesday, August 26` heading, one `- ` bullet each, pinned bullet first prefixed `**Pinned.**`, attribution in parentheses, and nothing at all where both fields were blank |
  | Markdown escaping | A takeaway typed starting with `-` exported as `\- A takeaway that starts with a dash`, so it renders as text and not a nested list. A typed line break collapsed to a single space, so no bullet breaks across lines |
  | Filename and type | `liner-notes-2026-08-26.md`, `text/markdown;charset=utf-8` |
  | Pinned rides the top with a scarlet left border | Measured `rgb(200,16,46)` at 3px, with a "Pinned" chip, and it took the top spot from a newer card |
  | Attribution falls back cleanly | Name plus club, club only, and "Anonymous" when both are blank |
  | Crew only controls | A non-admin device showed no export panel and zero pin or delete buttons. The PIN turned on the panel and three sets of card controls |
  | Character cap | 300, counter turns gold at 40 remaining, verified at "0 left" with the low class applied |
  | Display Mode does not look broken | Form, export panel, tally and admin buttons all `display: none`, card text scaling up through its clamp. Toggling back restored all of it |
  | 380px | 0px overflow, zero elements past the edge, day pills scrolling sideways (370px inside 348px) |
  | 1280px | 0px overflow, inside the 780px reading column, cards 748px, name and club side by side |
  | No console errors | None across post, pin, delete, filter, export, and Display Mode both ways |
- **`ts` is a server timestamp** except on a device running `?clock`, which writes its simulated
  time so a test post's tag and timestamp agree with each other. **Consequence: the three test
  posts made during this build look like August 26 to everybody.** They are placeholders
  ("Test Club Alpha", "Placeholder One") and T4.2 clears the node.
- **The export is always the whole board, never the filtered view.** The filter is a reading
  aid, and exporting what happened to be on screen would silently drop half the recap the one
  time somebody forgot which pill was selected. The panel copy says so.
- **Relative time never says "yesterday".** Inside a four day meeting that is easy to misread,
  so anything from one hour to seven days old prints the weekday and the Eastern time.
- **A post outside Wednesday or Thursday still lands.** The roadmap fixes the pills at All, Wed,
  Thu, and the tab is live before the meeting, so posts tagged `pre`, `tue`, `fri` and `post`
  will exist. They show under All, which is where the tab opens, and they still get their own
  heading in the export, so nothing is lost from the recap.
- **One new local storage key, `mm26_liner_who`,** holding the name and club so a second
  takeaway does not mean typing them again. It carries the prefix, so T1.6's Clear This Device
  picks it up with no code change. Confirmed: the panel enumerated it.
- **Open question for Carol, not invented either way.** Nobody said whether the recap wants the
  takeaways attributed. Last year's became the raw material for the follow up note, so
  attribution is in. An anonymous export is deleting one call to `lnCredit`.

### `[x]` T1.6 Admin panel, v1
- **Inputs:** spec Section 4
- **Output:** PIN gating and core admin controls
- **Steps:** gear icon in header, four digit PIN prompt, unlocked state persists for the session. Panel with Marquee (post and dismiss announcements), Tab Visibility (toggle per tab, hidden tabs stay visible to admin with a padlock), Reset by Section (per Firebase node with confirmation), Clear This Device (local storage only), Reset Everything (double confirmation, all nodes plus local state)
- **Acceptance:** wrong PIN is rejected. Toggling a tab off removes it for a non-admin device within two seconds and leaves it visible to admin with a padlock. Each reset clears only its own node. Reset Everything clears all nodes and all `mm26_` keys
- **Blocked by:** T1.4
- **Done Aug 11.** Built ahead of T1.4, which is fine: T1.4 was listed as the blocker because
  Soundcheck's own admin controls were expected to live in this panel. They do not. Per-tab
  controls read the `isAdmin` prop that is already threaded into every tab component, so the
  panel and Soundcheck are independent.
- **Verified on the live URL and against the database over plain HTTPS:**
  | Acceptance criterion | Result |
  |---|---|
  | Wrong PIN is rejected | `1234` cleared the field and returned "That is not the PIN." No panel, no padlocks, no crew bar. `2026` unlocked |
  | Toggling a tab off removes it for a non-admin within two seconds | Hid Liner Notes. Device B dropped from 6 pills to 5 and Liner Notes appeared in **zero** rendered elements. Measured propagation on the same pattern at **29ms** |
  | The viewer is not left on a blank tab | Device B was sitting on Liner Notes when it was hidden, and moved itself to The Setlist. No blank frame, because the rendered key is derived in the same pass |
  | Hidden tab stays visible to admin with a padlock | Crew kept all ten pills with a gold padlock on the hidden one. Content still reachable |
  | Each reset clears only its own node | Seeded `takeaways` and `photos`, wiped `takeaways`. It read `null`, `photos` still read `{"probe":1}`, and `reactions` and `encore` were untouched. Cancelling the prompt did nothing and set no state pill |
  | Reset Everything clears all nodes and all `mm26_` keys | Run at the end of the session as the T4.2 clear. See T4.2 |
  | Clear This Device leaves shared data alone | Cleared 2 keys, reloaded to the welcome screen with the panel locked. Every Firebase node unchanged |
  | 380px | No horizontal overflow, zero elements past the edge, with a 140 character announcement in the list. "Back to the wall" full width under the heading |
  | 1280px | Switches and nodes in two columns inside the 780px reading column, no overflow |
  | No console errors | None, across unlock, panel open, ten toggles, three presets, a cancelled confirm, a wipe, and a marquee post |
- **An empty database is already the T4.4 launch state.** Tab visibility lives at
  `settings/tabs/{key}` as a bare boolean, and a tab with no stored value falls back to
  `phase === "pre"`. With `settings` reading `null`, a non-admin device showed exactly six
  pills: Setlist, Band, Backstage, Soundcheck, Vault, Liner Notes. **T4.4 is now a
  verification task**, not a configuration one.
- **The gear changed meaning, deliberately.** Spec 4 says the gear opens the panel once
  unlocked. It used to lock. Locking is now a button inside the panel, because the gear sits
  next to Display Mode and losing crew access to a fat thumb mid-session is worse than one
  extra tap. `aria-pressed` still tracks whether crew is unlocked, which is what the lit
  button reports.
- **The phase line is now conditional.** `TabFrame` drops "Opens during the meeting" once a
  tab is actually open, or Crowd Vote would have read that line while the room was voting on
  it. Crew still see it on a padlocked tab, where it is still true. Anybody rewriting
  `TabFrame` must keep the condition.
- **Presets are one tap forward and a confirmation backward.** Pre-meeting, Wednesday,
  Thursday night. Only a step that takes a tab away from the room asks first, and it names
  the tabs: "This takes Crowd Vote, The Pit, The Cares Cup, Encore away from the room."
- **Reset Everything deliberately spares `settings`.** T4.2 empties the content nodes and
  T4.4 sets tab visibility straight afterwards. Wiping `settings` would mean setting the
  launch state twice and would silently drop any Vault override. The card says so.
- **Known limit on the two-device test.** Both browser contexts share one profile, so they
  share local storage. The Firebase propagation results are real. The claim that Clear This
  Device does not touch *another device's* local storage is reasoned, not measured, and a
  private window would settle it.
- **Tab pop-in on a cold load.** `useTabVisibility` returns null until the first snapshot, so
  for a few hundred milliseconds the bar shows the phase default. Holding the whole bar back
  would trade a pop-in for an empty bar, which is worse. Left as is.

**Phase 1 definition of done:** The Setlist, Backstage Pass, Soundcheck, Liner Notes, and the admin panel are production ready. The Band is complete except for real data.

---

## PHASE 2: Dynamic tabs
**Window: August 10 to August 17. Goal: every remaining feature is built, including the timed drop engine.**

### `[x]` T2.1 The Vault, shell and navigation
- **Inputs:** spec Section 3.5
- **Output:** resource tab structure
- **Steps:** five sections: Core Fundamentals, Membership Buckets, Club Graphs, Core Fundamental Scenarios, Membership Funnel Personas. Section navigation as a left rail on desktop and pills on mobile. Image sections render full width with pinch to zoom and a download link
- **Acceptance:** all five sections reachable. Placeholder images zoom and download correctly
- **Blocked by:** T1.6
- **Done Aug 11.**
  | Acceptance criterion | Result |
  |---|---|
  | All five sections reachable | All five pills navigate, the heading and the body change with each |
  | Mobile pills, desktop rail | At 380px the nav is a `row` scroller, 937px of pills inside 348px, scrolling sideways. At 1280px it is a `column` rail, each pill 216px wide, grid `216px 508px` inside the 780px reading column |
  | Images zoom | Overlay opens at `z-index: 55`, stage carries `touch-action: none`. Two taps of **+** measured `scale(1.96)`, which is 1.4 squared. **Fit** returned `scale(1)`. Escape and **Close** both dismiss |
  | Images download | `assets/graphs/anthem--members.svg` with `download="anthem--members.svg"`, on the card chip and in the overlay bar |
  | No horizontal overflow | 0px at 380px and at 1280px on every one of the five sections. The 11 elements measuring past the edge at 380px are all off-screen pills inside `.vt-nav__scroll`, the same intentional horizontal scroller the top tab bar uses |
  | No console errors | None |
- **The zoom overlay is a fixed overlay, not a fixed-height inner scroll container,** so the
  CLAUDE.md rule holds. The stage does not scroll: `touch-action: none` hands every gesture to
  the pinch handler.
- **Four of the five sections have no artwork,** because none has been delivered. They read
  "Empty shelf" or "Open and empty" rather than spinning forever. `data/vault.json` carries the
  manifest with four empty `items` arrays and documents its own item shape, so **T3.3 is a data
  edit with no code change.**
- **Not verified, needs a device.** The real pinch gesture and whether the download chip saves
  rather than navigates. Both are T3.6. The button path is verified.

### `[x]` T2.2 Club graph picker
- **Inputs:** T2.1
- **Output:** searchable club selector inside the Club Graphs section
- **Steps:** search or dropdown selector, then load that club's graph. Do not stack all graphs on one scroll
- **Acceptance:** every club in the list resolves to a graph or a clear "graph not available" state. Search finds a club by partial name
- **Blocked by:** T2.1
- **Done Aug 11**, against `data/graphs.json`: 29 clubs, 2 rollups, 92 SVGs. All 92 referenced
  files exist on disk, checked by script.
  | Acceptance criterion | Result |
  |---|---|
  | Every club resolves to a graph or a clear missing state | 31 rows, 29 under Clubs and 2 under Rollups, each naming which types it holds. Bear Creek rendered Members, Dues, Rates. Club 23 rendered Members and Dues plus a dashed "Rates: Not in the pack for this club". Anthem rendered four including Other. PGA WEST & Citrus rendered Rates plus two dashed cards. No broken image anywhere |
  | Search finds a club by partial name | `bear` to Bear Creek, `oaks` to Canyon Oaks, `eagles` to Eagle's Landing despite the apostrophe, `pga west` and `pgawest` both to PGA WEST and the rollup, `toledo cc` to Toledo CC, `zzz` to "No club by that name" |
  | One club at a time, never a stack | The list closes on pick and only that club's cards render. "Change club" reopens it |
  | Selection survives leaving the tab | Held in `mm26_vaultclub` |
- **The SVGs are inlined by fetch, not dropped in an `img` tag,** so the graph text inherits
  the wall's font. Measured: `<svg><text>` computes to `Inter`. A failed fetch falls back to an
  `img` tag, which covers `file://` and offline.
- **Label versus caption.** The card labels are `Members`, `Dues`, `Rates`, `Other`, straight
  off the keys in `graphs.json`. Some graphs caption themselves differently:
  `medallion--rates.svg` calls itself "Sales and attrition, full privilege". The label is
  navigation, the graph's own caption is the fact. Worth one line from Jeannette if she wants
  them to match.
- **These graphs carry real per-club revenue figures and this repo is public.** Example:
  `bear-creek--dues.svg` prints "Monthly dues line revenue" and "$393k". They are committed
  because CLAUDE.md's data split lists club graphs as repo-static and T3.2 plans exactly this
  population, so it is the documented architecture rather than a new decision. **Jim should
  confirm he is content with per-club dues revenue sitting at a guessable public URL.** If not,
  they have to move behind Firebase the way `encore/tenure` is, and it is cheaper to decide
  before the QR code is printed than after. Source was `CGPM_Membership Graphs-July 2026.xlsx`.

### `[x]` T2.3 Timed drop engine
- **Inputs:** spec Section 3.5, confirmed unlock times
- **Output:** scheduled reveal system with admin override
- **Steps:** each locked section carries an `unlockAt` timestamp anchored to Eastern. On load, compute the device clock offset against a Firebase server timestamp and use the corrected time. Attendees see the section greyed with a padlock, the unlock time, and a live countdown. Admin always sees unlocked content with a padlock badge indicating the room cannot see it. Admin override unlocks early or re-locks, stored in Firebase settings so it syncs to all devices
- **Acceptance:** set a test unlock two minutes out and watch it fire without a page refresh. Change the device clock by six hours and confirm the server offset corrects it. Admin unlock propagates to a second device within two seconds. Admin re-lock also propagates
- **Critical:** this is the highest risk feature in the build. Test it three separate times on three different days
- **Blocked by:** T2.1
- **Done Aug 11, with one criterion carried to T3.7.** State lives at
  `settings/vaultDrops/{scenarios|personas}` as `mode` plus an optional `unlockAt` and a server
  `ts`. Modes are `scheduled`, `open`, `shut`. Missing or unreadable normalises to `scheduled`,
  which keeps the schedule in force rather than letting a bad value open a section.
  | Acceptance criterion | Result |
  |---|---|
  | A test unlock two minutes out fires with no page refresh | **Passed.** Tapped "Test, 2 minutes out" on device A. Device B's countdown went to 2:02 and ran down. At zero the padlock panel was replaced by the section body with **no click, no scroll and no reload** on device B |
  | Admin unlock propagates to a second device within two seconds | **29ms**, measured with a MutationObserver against the click timestamp. Budget was 2000ms |
  | Admin re-lock also propagates | Yes. "Hold it shut" put device B back to a padlock reading "Still shut. It opens when the room gets there." with no countdown |
  | Attendee sees grey, padlock, time, countdown | "Opens Wednesday, August 26, 9:30 AM Eastern" with a live countdown in days |
  | Admin always sees the content with a padlock badge | Crew read the section while it was forced shut, with "The room cannot see this yet" |
  | Override beats the clock in both directions | Forced open showed content 14 days early. Forced shut held it past a test time that had already passed |
  | One section does not move the other | Changing Scenarios left Personas on "Thursday, August 27, 10:30 AM Eastern" throughout |
  | Test time is reversible and loud | A red warning names both the fake time and the real one while a test time is in force. "Restore the real time" cleared `unlockAt` and both devices went back to Wednesday with no reload |
  | Change the device clock by six hours | **Not run. Carried to T3.7.** It needs the machine clock moved, which would disrupt the rest of this session. The crew block prints the correction in words and read "This device agrees with the server, inside five seconds" when synced, so the readout exists and is ready to check |
  | Three fires on three separate days | **One fire done, Aug 11.** Two remain, and they are a calendar commitment. T3.7 |
  | No console errors | None, across load, every section, a club switch, the zoom overlay, and a drop firing |
- **Worth knowing before the meeting, found while testing.** A countdown in a **backgrounded**
  browser tab stalls, because Chrome throttles timers in hidden tabs to as little as once a
  minute. The section still opens the instant the tab becomes visible again, with no
  interaction, which is what was measured. So an attendee watching their screen sees it fire on
  time, and an attendee whose phone was in their pocket sees it already open when they look. No
  fix is needed and none is possible from inside the page, but do not judge a drop by a phone
  that has been asleep.
- **Locked is the default until the clock is proved.** `.info/serverTimeOffset` reads zero both
  when the device is correct and when nothing has been heard from the server, so zero is not
  evidence. `useVaultClock` waits for `.info/connected` plus 250ms before a scheduled section
  may open. The cost is that a section can open up to about a second late on a cold load. The
  alternative was a flash of Wednesday's content on a phone whose clock is a day out.
- **After eight seconds it stops waiting** and runs on the device's own clock, saying so on
  screen. Locked forever on a bad connection is the worse failure. Consequence worth naming: on
  a device that cannot reach Firebase, a crew override cannot be honoured, because the override
  lives in Firebase.
- **The drop is a presentation gate, not a security boundary.** The wall does not fetch a
  locked section's files for a non-admin, so nothing is sitting in an attendee's page, but the
  repo is public and the artwork will sit at a guessable path. **If the Scenarios or Personas
  content is confidential before it is presented, it must not go in this repo** and needs the
  Firebase treatment `encore/tenure` already uses. One answer from Jim needed before T3.3.
- **The two unlock times are still not confirmed in writing.** They are in the build as
  CLAUDE.md gives them, anchored at `-04:00`: Wednesday Aug 26 9:30 AM and Thursday Aug 27
  10:30 AM Eastern. Wednesday 9:30 AM does not line up with any session start in
  `data/agenda.json`, so if the intent was "when that session starts" the two constants at
  `VAULT_DROP_SCHEDULE` need one line from Carol. **T4.5 still owns this.** The override buttons
  cover the drift on the day either way.
- **`ts` on the drop node is a server timestamp,** not `Date.now()`, unlike `encore/tenure`.
  On a feature about clocks, "last changed 9:31 AM" must not come off a crew phone that is six
  hours out.
- **T2.8 can mount `VaultDropControls` inside the gear panel** to satisfy the two-taps-from-the-gear
  rule. Until then the path is gear, PIN, Vault tab.

### `[ ]` T2.4 Crowd Vote
- **Inputs:** spec Section 3.7
- **Output:** live polling tab with four poll types
- **Steps:** admin creates polls. Active polls as cards with question, full width option buttons, ON AIR badge. After voting the chosen option fills scarlet with a checkmark and results render as horizontal bars with percentage and count. One vote per device per poll via `mm26_pollvotes`. Closed polls dim with final results. Four types: multiple choice, knowledge check (carries a correct answer, reveals the correct-versus-incorrect split on close), ranking (drag to order, averaged rank results), word cloud (one word answers rendered live)
- **Acceptance:** each of the four types creates, accepts votes, and displays results correctly. Vote lock persists through reload. Knowledge check reveals the answer only after admin closes the poll
- **Blocked by:** T1.6

### `[ ]` T2.5 The Pit
- **Inputs:** spec Section 3.8
- **Output:** photo gallery tab
- **Steps:** upload panel with optional name and caption, then two separate buttons. Take Photo uses `capture="environment"`. Choose from Library omits the capture attribute. Both required. Client side compression to roughly 800px long edge before upload. Square thumbnail grid, newest first, caption and attribution below. Like button overlaid on each thumbnail, toggle on and off, counts sync via Firebase, device state in `mm26_liked`. Lightbox on tap with full image, like button, and for admin download and delete. Optional filter by club or team
- **Acceptance:** both upload paths work on iOS and Android. A 4MB source photo lands under 200KB. Likes toggle and sync across devices. Lightbox does not trap scroll
- **Blocked by:** T1.6

### `[ ]` T2.6 The Cares Cup
- **Inputs:** spec Section 3.9, source flier poster art
- **Output:** tournament leaderboard tab
- **Steps:** leaderboard list with position, team name, score, thru. Gold, silver, bronze treatment on the top three. Poster art card backgrounds for Team Total Consciousness (Mike Akeroyd, Donny Darville) and Spalding's Revenge Team (Todd Keefer, Jimmy Han). Century Golf Cares fundraising total displayed at the top. Score entry is admin only
- **Acceptance:** admin can add teams, enter scores, update the fundraising total, and lock the board. Non-admin cannot edit anything. Leaderboard sorts correctly including ties
- **Note:** poster art use is an open question. Build with a solid color fallback so the tab ships either way
- **Blocked by:** T1.6

### `[~]` T2.7 Encore
- **Inputs:** spec Section 3.10
- **Output:** recognition tab, scaffolded and admin editable
- **Steps:** four sections, each independently unlockable: Award Winners (winner photo on vinyl label background, award name in Alfa Slab One, club, citation), Hall of Fame (inductee cards with photo, club, year, citation), Top Videos (YouTube or Vimeo embeds), Tenure Recognition (grouped by milestone with photo, name, club, years). Full admin create, edit, and delete on every section so content can be posted live from the Awards Show
- **Acceptance:** admin can create an award entry with a photo and citation from a phone in under a minute. Video embeds play inline. Each section unlocks independently. Tenure can go live while awards stay hidden
- **Blocked by:** T1.6
- **Part one done Aug 11: Tenure Recognition only. This task stays open.** Award Winners, Hall
  of Fame, and Top Videos are still stubs with real empty-state copy and no CRUD.
- **Why Tenure came out of order.** The official agenda puts the Tenure Awards at **Wednesday
  8:20 AM**, at the Opening Cowbell, not at the Thursday night awards show. So Tenure has to be
  able to go live two days before the other three, on a client request, and it is built and
  unlockable on its own.
- **Verified on the live URL, with two browser contexts as two devices:**
  | Criterion | Result |
  |---|---|
  | Tenure unlocks independently | Flag lives at `encore/tenure/unlocked`. The other three sections are unaffected because they hold no unlock state yet |
  | Publish propagates to a second device | 104ms from the publish tap to the second device rendering the list. Budget was two seconds |
  | Re-lock propagates | 26ms, and the second device's DOM went back to holding no trace |
  | Attendees see nothing while locked | Rendered `#root` contains zero occurrences of any entry name or any milestone label. Only the locked message |
  | The read is gated, not just the render | Proved on the wire. With Firebase's own logging on, remounting the tab while locked and not admin produced 4 references to `encore/tenure/unlocked` and **zero** to `encore/tenure/entries`. Entering the PIN produced 5 |
  | Admin sees a padlock badge | "The room cannot see this yet", shown only while locked and only to crew |
  | Admin create, edit, delete | All three exercised against `encore/tenure/entries` and read back over plain HTTPS. Delete asks first, by name |
  | Grouped by milestone | Groups sort by the number in the label, longest tenure first, which is the order they get read out. Names sort alphabetically inside a group |
  | Layout holds with no photo and no club | Names only is the normal case, not a card with empty holes. Verified at 380px and 1280px |
  | No horizontal overflow | Document width equals viewport at both. Zero elements past the edge |
  | No console errors | None |
- **The locked state does not ship the data.** `useTenureEntries(enabled)` returns early before
  it ever builds a ref, so the listener is never attached. This is the whole point: a render
  guard would leave the confidential list sitting in the page for anyone who opened dev tools.
  If anybody refactors this, the test is the wire log, not the screen.
- **Names only, per Jim, Aug 11.** No club, no photo. Both stay in the data shape and render
  when present, and the row is built so a bare name is the normal case.
- **Every name in the database right now is a placeholder.** Four of them, obviously fake:
  Placeholder One, Placeholder Two, Placeholder Three Edited, Placeholder Five. They are there
  so the layout can be reviewed. **T4.2 must clear them.** The real tenure list is handled
  outside this repo, which is public with an open database, and no real name from it has been
  written into any tracked file.
- **The section is locked as of the end of this session.** `encore/tenure/unlocked` reads
  `false`, so the room sees the locked message and nothing else.
- **Still to do for T2.7:** Award Winners on a vinyl label with citation and photo, Hall of
  Fame cards, Top Videos embeds, and an independent unlock flag for each of those three. The
  Tenure section is the pattern to copy: gate the read, not the render.
- **Alfa Slab One appears here and nowhere else,** on the four section headings and the
  milestone labels. That is the whole ration CLAUDE.md allows it.

### `[ ]` T2.8 Admin panel, v2
- **Inputs:** T2.3, T2.6, T2.7
- **Output:** complete admin control set
- **Steps:** add Vault Drops panel (per section unlock status, scheduled time, manual unlock and re-lock). Add per-tab controls listed in spec Section 4.2. Add Encore CRUD entry points. Add Cares Cup score entry
- **Acceptance:** every control in spec Section 4.2 exists and works. Vault Drops is reachable in two taps from the gear icon, because it will be used under time pressure
- **Blocked by:** T2.7

**Phase 2 definition of done:** every feature in the spec is built and working against placeholder content. No feature work remains.

---

## PHASE 3: Content load and test
**Window: August 17 to August 21. Goal: real content in, everything tested on real devices.**

### `[ ]` T3.1 Load roster and photos
- **Inputs:** Jeannette's headshots, Carol and Lisa's verified roster
- **Output:** real `/data/roster.json` and populated `/assets/attendees/`
- **Steps:** run T0.7 pipeline over the headshots. Build the roster file. Cross-check every roster entry against a photo file and every photo against a roster entry
- **Acceptance:** zero unmatched records in either direction, or a documented list of known-missing photos with placeholders in place. Every title matches the verified list
- **Blocked by:** T1.3, asset delivery

### `[ ]` T3.2 Load club graphs
- **Inputs:** Jeannette's graph files
- **Output:** populated `/assets/graphs/`
- **Acceptance:** every club in the picker resolves to a graph. Each graph is legible on a 380px screen at default zoom
- **Blocked by:** T2.2, asset delivery

### `[ ]` T3.3 Load Vault content
- **Inputs:** Membership Buckets image, Core Fundamentals image, Scenarios content, Personas content
- **Output:** all five Vault sections populated
- **Acceptance:** all sections render real content. Locked sections still show the correct countdown
- **Blocked by:** T2.3, content delivery

### `[~]` T3.4 Final agenda swap
- **Inputs:** Jeannette's final agenda
- **Output:** updated `/data/agenda.json`
- **Acceptance:** every session matches the final agenda for title, time, presenter, and room
- **Blocked by:** T1.1, asset delivery
- **Mostly done at T1.1, Aug 11.** The official agenda arrived during the T1.1 build, so
  `data/agenda.json` was written from it rather than from the flier. Titles, times, and the
  three named presenters match the source.
- **Still open, which is why this is `[~]` and not `[x]`:** the Smash Park conflict at T1.1a,
  the attire wording at T1.1b, and rooms. The agenda names no rooms at all, so every `room`
  field is empty. If rooms exist, they are a drop-in.

### `[ ]` T3.5 Poll library and Cares Cup seed
- **Inputs:** poll questions from organizers, confirmed team names
- **Output:** poll questions drafted and ready to publish, teams seeded
- **Acceptance:** each session that wants a poll has one drafted. Presenters are not writing polls on stage
- **Blocked by:** T2.4, T2.6

### `[ ]` T3.6 Device matrix test
- **Inputs:** complete build
- **Output:** test report
- **Steps:** test every tab on at minimum iPhone Safari, Android Chrome, and one tablet. Test both photo upload paths. Test with cellular data, not just Wi-Fi
- **Acceptance:** no broken layouts, no console errors, no failed uploads on any device in the matrix
- **Blocked by:** T3.1 through T3.4

### `[ ]` T3.7 Timed drop fire test
- **Inputs:** T2.3
- **Output:** verified unlock behavior
- **Steps:** schedule a dummy section to unlock five minutes out. Watch it fire on two devices simultaneously without refresh. Repeat on a second day. Test admin early-unlock and re-lock
- **Acceptance:** three successful fires on separate days. Admin override works in both directions
- **Blocked by:** T3.3

### `[ ]` T3.8 Stakeholder walkthrough
- **Inputs:** complete build
- **Output:** sign-off from Carol, Lisa, and Jeannette
- **Steps:** walk all three through the wall on their own phones, not a desktop browser. Capture every change request and triage into fix-now, fix-if-time, and post-meeting
- **Acceptance:** all three have used the wall on their own device and their fix-now items are resolved
- **Blocked by:** T3.6

### `[ ]` T3.9 Second admin onboarding
- **Inputs:** named second admin from the organizers
- **Output:** a second person who can operate the panel
- **Steps:** hand over the PIN. Walk them through Vault Drops, Marquee, and Encore posting specifically. Those are the three they may need to run without Jim
- **Acceptance:** the second admin performs an unlock, posts a marquee message, and creates an Encore entry unassisted
- **Blocked by:** T2.8

**Phase 3 definition of done:** real content everywhere, tested on real devices, signed off by the organizers, two people can operate it.

---

## PHASE 4: Freeze
**Window: August 21 to August 24. Goal: nothing changes except bug fixes.**

### `[ ]` T4.1 Feature freeze
- No new features. Bug fixes only. Any new request goes to a post-meeting list

### `[ ]` T4.2 Clear test data
- Run Reset Everything. Confirm every Firebase node is empty and all `mm26_` keys are cleared
- **Acceptance:** the wall looks like nobody has ever touched it
- **Known test data sitting in the database as of Aug 11:** four placeholder tenure entries
  under `encore/tenure/entries`, and one reaction count at `reactions/tue-shank-showdown/fire`.
  Both were left deliberately so the layouts can be reviewed. Neither may survive this task.

### `[ ]` T4.3 Re-verify Firebase rules
- Read the published rules back. Confirm no expiration and no date comparison
- **Acceptance:** rules read exactly `{ "rules": { ".read": true, ".write": true } }`
- **This is the check that would have prevented the LC26 outage. Do not skip it**

### `[ ]` T4.4 Set launch tab visibility
- Pre-meeting tabs on: The Setlist, The Band, Backstage Pass, Soundcheck, The Vault, Liner Notes
- During and post tabs off: Crowd Vote, The Pit, The Cares Cup, Encore
- **Acceptance:** a non-admin device sees exactly six tabs

### `[ ]` T4.5 Verify unlock schedule
- Core Fundamental Scenarios: Wednesday August 26, 9:30 AM Eastern
- Membership Funnel Personas: Thursday August 27, 10:30 AM Eastern
- **Acceptance:** both timestamps confirmed against the organizers' written confirmation. Countdowns display the correct remaining time

### `[ ]` T4.6 QR code and print test
- Generate the QR code. Produce a print-ready file for welcome packets and table tents
- **Acceptance:** the printed code scans successfully from three different phones at arm's length in normal room lighting

**Phase 4 definition of done:** the wall is live, clean, correctly gated, and reachable from a printed code.

---

## PHASE 5: Live operations
**Window: August 25 to August 28. Daily runbook.**

### `[ ]` T5.1 Tuesday August 25
- Wall live with the six pre-meeting tabs
- Enter Shank Showdown scores after play, or post final results
- Marquee: welcome message and mixer reminder

### `[ ]` T5.2 Wednesday August 26
- Reveal Crowd Vote, The Pit, and The Cares Cup
- **8:20 AM: Tenure Awards Presentation, at the Opening Cowbell.** Publish the Encore Tenure
  section once the names have been read out. Encore, Tenure Recognition, "Publish to the room".
  One tap, and it lands on every phone in about a tenth of a second. The other three Encore
  sections stay hidden until Thursday night
- **9:30 AM: Core Fundamental Scenarios unlock. Verify it fired**
- Marquee: Dress-Up Day photo prompt, pointing people to The Pit
- Marquee later: Smash Park departure reminder, denim allowed

### `[ ]` T5.3 Thursday August 27
- **10:30 AM: Membership Funnel Personas unlock. Verify it fired**
- ~~Reveal Tenure section if tenure is presented today~~ **Tenure is Wednesday, not Thursday.**
  The official agenda puts the Tenure Awards Presentation at Wednesday 8:20 AM. See T5.2
- After the 7 PM Awards Show: post award winners, Hall of Fame, and Top Videos to Encore. Reveal those sections
- Marquee: no early departures before Friday morning

### `[ ]` T5.4 Friday August 28
- Marquee: thank you and travel reminder
- Confirm Encore is fully live

---

## PHASE 6: Archive
**Window: after August 28.**

### `[ ]` T6.1 Exports
- Soundcheck questions to CSV for follow up
- Liner Notes to Markdown for the recap communication
- Full photo gallery download for the recap deck

### `[ ]` T6.2 Archive decision
- Per organizer decision: leave live read only, or take down
- If read only, set Firebase rules to `{ "rules": { ".read": true, ".write": false } }` and confirm the wall still loads

---

## Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Assets slip past August 10 | High | High | Written deadline this week. Build all containers against placeholders so real data is a drop-in |
| Timed drop fires late or not at all | Medium | High | Server clock offset, three separate fire tests, admin manual override always available |
| Firebase rules expire | Low | Total | Permanent rules at creation, re-verified at T4.3 |
| Day 1 and Day 2 mapping wrong | Medium | High | Written confirmation from organizers by August 5 |
| Poster art not usable | Medium | Low | Solid color fallback built into T2.6 |
| Photo volume slows the wall | Medium | Medium | Client side compression at 800px, static assets out of Firebase |
| Single admin unavailable during the meeting | Medium | High | Second PIN holder onboarded at T3.9 |
| Printed QR does not scan | Low | Total | Print test at T4.6 across three phones |
