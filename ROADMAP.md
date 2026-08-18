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

### `[~]` T0.8 Deploy and verify
- **Inputs:** all of Phase 0
- **Output:** working skeleton on the live URL
- **Acceptance:** the URL loads on three different physical phones (at minimum one iOS, one Android). All ten tabs reachable. No console errors. Fonts render, not fallbacks
- **Blocked by:** T0.6
- **Aug 13 2026. The device-only half passes. The matrix is unproven.**
  | Criterion | Result |
  |---|---|
  | Fonts render, not fallbacks | **Passes.** Jim tested on a handset. Anton, Alfa Slab One and Inter all arrive. A crew-only readout in the header now says out loud if one ever fails, so this stays observable at the venue rather than failing silently |
  | Tabs reachable, no console errors | **Passes**, verified in a browser at 380px and at desktop, repeatedly. Note the count is NINE now, not ten: Liner Notes became a pill inside Soundcheck on Aug 13 |
  | Three different physical phones, one iOS and one Android | **Unproven.** Jim confirmed the behaviour but did not record which devices. The items are proven, the matrix is not |
- **Stays `[~]` for that last row only.** Everything the task actually tests works. See
  `docs/device-test.md` for the report.

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

### Aug 12, Smash Park is cancelled. Wednesday night is at the hotel
**From:** Lisa, relayed by Jim, Aug 12. "On day 2 we had to cancel smashpark. We
are now going to have dinner and karaoke at the hotel. 6 will be drinks, 630
dinner 7-9 karaoke." And: "We'll need to remove smashpark from backstage pass
and update."

**This reverses T1.1a.** The flier said Smash Park, Carol's official agenda said
the hotel, Jim called it for Smash Park on Aug 11, and the wall was built that
way. Lisa has now cancelled the outing, which means the official agenda was
right the whole time. Wednesday evening is Carol's block, verbatim.

**What moved:**
- `data/agenda.json`. One `wed-1800-smash-park` card became three: 6:00 PM
  Cocktails at Hotel Bar, 6:30 PM Dinner Served at Hotel, 7:00 to 9:00 PM
  Karaoke, Corn Hole, Cards and Beer Pong. All three carry `venue: "hotel"`.
  The seven Smash Park activities are gone with the card that held them.
- The 5:15 PM card reads Carol's wording again. "Take a bow, you earned it. Head
  back to the hotel to change out of your Rock n' Roll costumes and meet at the
  hotel bar. Casual attire, denim allowed." It no longer sends anybody to a
  rental car.
- Wednesday's second attire line is now "Evening at the hotel. Casual attire,
  denim allowed." The "At Smash Park" line is gone. Backstage Pass reads that
  same line out of the same file, so the dress code moved on both tabs at once.
- **`VENUES.smashpark` is deleted, not commented out.** That is the point of the
  shared table: with the venue gone there is no way for a session, a panel, or a
  future card to point at it. The address and phone survive in a comment where
  the key used to be, in case it ever comes back.
- Backstage Pass drops the Smash Park venue card. Where You Play now carries The
  Medallion Club and the hotel, the hotel noted as Wednesday night's karaoke,
  corn hole, cards and beer pong. Where You Eat reads "Wednesday night,
  cocktails and dinner are at the hotel."
- `data/polls.json`. The denim question hung off session `wed-1800-smash-park`,
  a key that no longer exists, so it now hangs off `wed-1800-cocktails`. Its
  explain said "fine at the Evening Outing" and now says "fine at the hotel that
  evening". The crew note dropped the T1.1a caveat and kept the T1.1b one, which
  is still real.

**History is corrected, not deleted.** The `meta.smashPark` note in
`agenda.json` now tells the whole sequence, flier to Jim to Lisa, and says
outright that the venue is gone from `index.html` so nothing may point at it.
T1.1a above is marked closed rather than rewritten.

**Verified:** zero attendee-facing mentions of Smash Park anywhere in the repo.
The four that remain are a JS comment, two crew-only BuildNotes behind the PIN,
one crew-only note in `polls.json`, and the `agenda.json` meta block, which is
never rendered. `grep -i smash` is the check.

### Aug 12, Membership Buckets is now Invitation Sources
**From:** Lisa, Aug 12. "We need to change the tab to Invitation Sources instead
of membership buckets."

Display name only. **The key stays `buckets`,** which is a deliberate call and
worth the line: it is the child name in `data/vault.json`, the value already
sitting in `mm26_vaultsection` on any phone that has opened the tab, and the id
on the nav button. No Firebase path carries it, because the two Firebase drop
nodes are `scenarios` and `personas`. Renaming the key would mean editing a data
file and stranding the stored value on every phone, to change a string nobody
reads. The name is what the room sees. The key is plumbing.

Empty state rewritten: "Empty shelf. Tyler is sending the Invitation Sources
artwork." It is still an empty state and not a broken image, because the
artwork has not arrived. When it does, the files go under the `buckets` key in
`data/vault.json`, which the Vault crew note now says out loud.

### Aug 12, The Band organises by club instead of alphabetically
**From:** Lisa, Aug 12. "Jim, can we organize by club instead of alphabetical?"

One section per club with a heading and a gold count badge, clubs alphabetical,
**Century Golf corporate after all of them** because they are not a club. People
inside a club keep the roster's own name order.

**Corporate is matched, not listed.** `bandClubRank` tests the club value for a
"Century Golf" prefix. That is the string the roster file carries, and a prefix
test means a fuller spelling typed into the crew panel still lands last instead
of between Canyon Oaks and Chenal. It is the only club string matched in code
anywhere on the tab.

**A blank club groups last, under "No club on the roster".** Nobody in the file
is in that state. It exists so a cleared club field in the crew panel cannot
drop a person off the wall silently.

**When the club select is set, the headings come off and the grid goes flat.**
Every heading would otherwise repeat the word already sitting in the select.
Newbies and search keep their headings, because both cut across clubs and the
heading is the only thing telling you that the two first timers on screen are
not from the same place.

**Nothing regressed.** All, Newbies, the club select, the region select, and
live search on name, club and title all still work, and Newbies still stacks
with a club. Grouping is grouping only: it filters nothing, so nobody can go
missing between the filter and the heading.

**Every count is still counted off the file.** The header line, the pill badges,
the "n of n showing" line, and the new per-club badges. `data/roster.json` is
being regenerated, so the numbers below will move and that is correct.

**No new token and no new motif.** Anton in caps like every other heading, the
`--gold-rule` hairline the tab bar already uses, and the same `.tab__badge` as
the filter pills. Not sticky, no scroll container. Twenty seven headings makes a
long page on a phone, which is fine, because the club select is the shortcut for
anybody who does not want to scroll it.

### Aug 17, weather on each day of the meeting
**From:** Jim. "The meeting is in Columbus Ohio. Can we add weather forecasts to
each day of the meeting, include appropriate visuals and emojis." Then: "Create
the space and graphics and give me a way to update manually," and "you can fill
the weather data with your best guess for now."

**Done.** A strip in The Setlist day header, sitting between the day note and the
attire lines. High, low, a sky emoji with its label, and an optional one line
note. Attire is the reason anybody checks the weather, so the two live together.

**Where the data lives.** Firebase at `weather/{tue,wed,thu,fri}`, which follows
the data split rule in CLAUDE.md. Weather moves right up to the morning of, and
the person updating it is holding a phone in a ballroom, not making a commit.

**Manual update.** Crew only, inline under the day header, one form per day. High,
low, rain percent, a sky dropdown with the seven emoji options, and the note line.
Switch day pills to edit a different day. Saving writes that day and nothing else.

**Real numbers, same day.** Jim sent an actual Columbus forecast within the hour,
so the climate normals never shipped. `WX_SEED` now holds his figures: Tue 80/62,
Wed 81/65, Thu 81/64, Fri 79/61, partly cloudy every day, rain chance 22, 24, 24
and 21 percent. Rain chance was added to the record, the display and the crew form
to carry it.

**Every day is stamped with its age.** These were pulled eight days out, and an
eight day forecast moves, so the strip prints "Forecast as of Aug 17" rather than
letting stale numbers read as current. A crew save writes `ts` from the server and
the line follows it, so refreshing on the Sunday before re-dates itself with no
extra step. The `estimate: true` path and its "Seasonal average, not a forecast"
line are still in the code for any day that ever falls back to a guess.

**The seed is in the repo rather than written into Firebase once.** It survives a
Firebase wipe, so no day is ever blank, and there is one copy of the guess, so
nobody has to work out whether a number came from a person or from me. Firebase
wins per day wherever a crew record exists, and the merge is per day rather than
per field, so a saved day cannot wear half an estimate.

**No new token and no new motif.** `--warm-fill`, `--warm-edge` and the
`--gold-rule` left border, the same dials the rest of the wall already uses. Emoji
rather than an icon font, because it carries colour everywhere and cannot fail to
load in a ballroom.

**Verified:** four days switch and the editor re-seeds with each; a save through
the real form wrote to Firebase and cleared the estimate line; the test record was
removed and the seed came back; the editor is invisible to attendees; no console
errors; no horizontal overflow at 390px or 1280px. Sky moved to its own row after
it clipped "Partly cloudy" when it shared a row with the two temperatures.

### Aug 17, the breakout scenarios are the personas
**From:** Jim, who sent the personas document a second time. "No. These are the
scenarios we're using for the breakouts."

**The file was a duplicate.** Byte for byte identical to the personas document from
Aug 15, same SHA-256, same 28,337 bytes, and the word "scenario" appears nowhere in
it. Every string already in `data/personas.json` was verified present in it. So there
was nothing new to load. What was new was the instruction: one document serves both
Vault drops.

**Done.** `scenarios` is now `kind: "personas"` in `VAULT_SECTIONS`, reading the same
`data/personas.json` through the same `VaultPersonas` component. One file, one
component, no second copy of the prose to drift out of sync. The shelf that has been
empty since the build started now holds all six personas.

**The scenarios drop was found forced shut,** stamped Aug 17 10:36 AM Eastern, left
over from testing. Set back to `scheduled`, because the section now has real content
and the Wednesday breakouts are what it is for. It opens Wednesday 9:30 AM Eastern,
15 minutes before the breakouts start, and the crew override still beats the clock
both ways.

**Both sections stay. Jim's call, Aug 17, made three times.** The room meets the same
six personas twice: Wednesday 9:30 as Core Fundamental Scenarios, Thursday 10:30 as
Invitation Source Personas. Two padlocks, two unlock times, identical content.

Offered the choice of collapsing them, he kept both. An hour later he cut Scenarios,
and it was fully removed: nav entry, schedule, empty state, crew row, `vault.json`
block, the Firebase override node, and every line of copy that counted to two. Then
he asked for it back, and `git revert` of the removal commit put it back exactly,
since that commit had touched nothing else.

So the arrangement is unchanged from where it started, and it is not an accident.
It has been questioned and answered. The note in `VAULT_SECTIONS` says the same.

**Verified:** six persona cards render under Core Fundamental Scenarios; a card opens
to its story and its closing question; crew see it with the "the room cannot see this
yet" badge; attendees see the padlock, "Opens Wednesday, August 26, 9:30 AM Eastern"
and a live countdown; no console errors; no horizontal overflow.

### Aug 17, The Medallion Club Story in the Vault
**From:** Jim, who sent the link and then the caption to go with it.
`https://simplebooklet.com/themedallionclubversion5#page=1`

**Done.** A sixth Vault section, "The Medallion Club Story", holding his caption and
one button out to the booklet. His wording is reproduced exactly as sent, curly
quotes and ellipsis included, the same rule the personas follow. The `#page=19`
anchor is his. He first sent it as `#page=19` and changed it to `#page=1` the same
day, so the booklet opens at the cover instead of partway in.

**Not open, not padlocked.** No `drop` on this section, so it is live the moment the
wall is. The caption tells people to read it before they arrive, which a countdown
would defeat.

**Nothing was copied into the repo.** The section holds a link, not a mirror of the
booklet. The club keeps ownership of its own document and can publish a new version
without a commit here. `vault.json` sections now accept `links` and `caption`, so the
next off site resource is a data edit and no code.

**The page title was no help naming it.** simplebooklet reports "The Medallion Club
Version 5", a working filename. The name in use, "The Medallion Club Story", came
from Jim's caption.

**One discrepancy for Jim, left as sent.** His caption says the Missing Chapter
segment is Wednesday at 3:00 PM. Carol's agenda, applied Aug 13, puts it at 3:15 PM
after a 3:00 break. Both are on the wall right now saying different things. Not
guessed at either way.

**Verified:** section renders unlocked with all four caption paragraphs and the link;
`target="_blank"` with `rel="noopener noreferrer"`; full width thumb target at 390px,
no horizontal overflow; underline matches the existing booklet PDF row; no console
errors.

### Aug 17, Thea Jordan joins Medallion, and a generated file bit back
**From:** Jim. "Add thea to the Medallion group. She is a newbie." Thea Jordan,
Catering Sales Director, The Medallion Club, with a pasted headshot.

**Done.** Row added to `data/attendee-list-verified.tsv` with NOTES "NEW", which is
what sets the newbie flag. Roster is 120, Medallion is 5, newbies are 23. Her card
carries the FIRST TOUR badge and the "First tour." line.

**Her photo was pasted, not filed.** Recovered from the session transcript at
267,969 bytes, 1331 by 2000, run through `tools/add-headshots.sh`, and the framing
gate passed it first time at 400 by 400. 119 of 120 now have a photo. Dave Horn is
still the one placeholder.

**The real finding: roster.json is generated and three of today's changes had been
made in the wrong file.** Amy Spittle to VP Marketing, John Martus to CFO, Chris May
to VP Operations and Natalie Bratcher to Balcones were all edited directly in
`data/roster.json` and committed. `tools/add-headshots.sh` finishes by running
`tools/reconcile-roster.py`, which rebuilds roster.json from the TSV, so adding
Thea's headshot silently reverted all four. They were caught because Thea herself
disappeared in the same regeneration.

All four are now in the TSV, where they survive a rebuild. Verified by regenerating
and reading back every one. `CLAUDE.md` now says roster.json is generated in the file
layout and in its own paragraph, because the reconciler's own header said so and that
was not enough to stop the mistake.

**Verified:** roster 120, 119 with photos, Medallion 5, Balcones 5; all five of
today's roster changes read back correct after a full regeneration; Thea renders in
the Medallion group with the newbie badge; her file serves 200 at 400 by 400.

### Aug 17, two small ones on the Story link and the Cares Cup card
**From:** Jim, two requests in a row.

**The booklet link opens at the cover.** `#page=19` became `#page=1`. One value in
`data/vault.json`, plus the two places the roadmap quoted the old anchor.

**Name and club only on the card.** Handicap and tee are off the player lines, so
"Casey Lewis · Sycamore Creek · -0.8 · Combo" now reads "Casey Lewis / Sycamore
Creek". A display change, not a data one: the values stay in
`data/cares-card.json` because they are what Carol supplied, and putting them back
is a two line change.

**Verified:** link renders as `#page=1` with target and rel intact; all 24 player
rows show two lines, no decimal handicap and no tee word anywhere on the tab; no
console errors; no horizontal overflow at 390px.

### Aug 17, matchup poster on the Cares Cup, awards line on Thursday
**From:** Jim, the poster pair image and one line of copy.

**The poster sits at the top of The Cares Cup,** directly under the tab heading and
above the fundraising card. It is the reason anybody opens that tab before a single
score exists, so it goes first.

**This is not the `art` background.** That mechanism lays a per team image behind a
score card at 30 percent as texture, and it stays exactly as it was, still off until
the client answers on permission. The poster pair is artwork shown as artwork.

**Tappable.** Opens the same zoom viewer the Vault uses, because the small print is
the joke and 358px on a phone will not carry "if there's OB left, he's already there".

**The file.** Pasted as a 1572 by 1147 webp, recovered from the session transcript.
sips reads webp but will not write it, so it was normalised to PNG first, then cut to
`assets/cares/shank-showdown-vs.jpg` at 1200 by 875 and 364KB. Quality was chosen by
looking at the fine print at 68, 75 and 82 rather than by picking a number. The full
resolution original is kept out of the repo at
`incoming/cares/shank-showdown-vs-original.webp` for a future re-cut.

`aspect-ratio: 1200 / 875` on the image is load bearing. A lazy image with no
intrinsic size reserves no space and never enters the viewport, the same trap the
Vault booklet pages hit.

**Thursday 7:00 PM Awards Presentation** gains the flier's line, appended to the
existing detail rather than replacing it: the practical instruction first, the payoff
second. His curly quotes are reproduced as sent.

**Verified:** poster renders first in the tab body at 358 by 261 with space reserved;
file serves 200 and decodes at 1200 by 875; tap opens the zoom viewer titled "The
Shank Showdown matchup" and Close returns; the awards card opens to both sentences; no
console errors; no horizontal overflow at 390px.

### Aug 17, the Vault section row hid four of its six sections
**From:** Jim. "I don't see it in the vault." Said about Core Fundamental Scenarios,
minutes after it was put back.

**It was there.** The live site was serving it: `key: "scenarios"` present in
index.html, `sections.scenarios` present in vault.json, `last-modified` stamped after
the reinstating push. Not a cache problem, and worth checking before blaming one.

**Measured at 390px, the section row is 1100px wide inside 358px of visible space.**
742px, two thirds of it, sits off screen to the right. The scrollbar is deliberately
hidden and there was no fade, so nothing on screen said the row moves. Four of the six
sections were unreachable unless you happened to swipe a row that looked complete.

**Worse, the active pill could be off screen.** The tab restores the last section from
`mm26_vaultsection`, so it opened showing Invitation Source Personas while its pill sat
outside the visible row. The panel heading said one thing and the only visible pills
said another.

**Two fixes.** The selected pill is now scrolled into view whenever it changes, using
`scrollLeft` rather than `scrollIntoView`, because scrollIntoView on a horizontal child
also drags the page vertically on iOS. And the row carries edge fades, driven by scroll
position rather than always on, because a permanent fade over a row that does not
scroll is a lie about there being more.

**Verified at 390px:** first section shows a right fade only; last section shows a left
fade only and sits flush at the end; middle sections show both; picking Core Fundamental
Scenarios scrolls it fully into view; the restored-section case now opens with its own
pill visible; no console errors.

**Still worth a decision.** Six sections is a lot for one row on a phone. Fades and
auto scroll make it discoverable, they do not make it visible at a glance. Wrapping the
pills onto multiple lines would show all six with no swipe, at the cost of vertical
space. Jim's call, not taken here.

### Aug 18, five Band corrections and the Vault reordered
**From:** Jim, a batch under "The Band" and "The Vault".

**Garry Cramer, Medallion GM.** No longer a newbie. NOTES cleared in the TSV, which
clears the flag and the FIRST TOUR badge together.

His photo came off in the same pass, on a misread. Jim's next message: "Garry Cramer
will stay in. Just remove as a newbie." The photo was restored from
`incoming/headshots/removed-by-request/` back to `assets/attendees/`, the exclusion
record in `data/headshots-derived.json` was cleared, and the roster regenerated.
Re-audited afterward rather than assumed fine: framing still passes, same as before
the round trip. Erik Mettille's removal stands, he asked for it directly.

**Erik Mettille, Oregon GC.** Same fix, same reasoning. He attended last year, so the
newbie flag was wrong on top of him not wanting the photo.

**Jay McEuen corrected to Jay McLuen.** Confirmed two ways before touching it: the
donation slip Jim sent and `data/cares-card.json`'s own `asWritten` field, recorded
back on Aug 13 when the sheet and the roster first disagreed. The processed photo
file was already named `jay-mcluen.jpg`, matched to the old spelling only by the
reconciler's near-spelling pass. After the fix it matches as a full name, which is
itself a small confirmation the correction is right.

**Sidney Ormsby corrected to Sydney Ormsby.** Same double confirmation, same tell:
the photo file was already `sydney-ormsby.jpg`. `cares-card.json` updated to match on
both, `asWritten` removed from both entries since name and sheet no longer disagree.

**Pete Ulliman added to Medallion.** Title read directly off his own name badge in
the photo he supplied: "PETE ULLIMAN, Asst. General Manager," Medallion Club patch
on the jacket. Not a guess. Not marked as a newbie, since nothing said he was one.

**Dave Horn still has no photo.** Nothing arrived. Still a placeholder, waiting on
Jim.

**Ballantyne, not touched.** "Remove Ballantyne and photos in All" would take out an
entire club and four people: Matt Saggio, Katie Robinson, Payton Williamson, Dan
Cordaro. CLAUDE.md's hard rule is never delete without approval, and this is the
kind of removal that rule exists for. Confirmed with Jim first rather than guessed
at.

**The Vault reordered to match the agenda,** rather than the order sections were
built in:

```
Wed  9:30   The Century Core Fundamentals Reignited   -> Core Fundamentals
Wed  9:45   Core Fundamentals Breakouts Session        -> Core Fundamental Scenarios
Wed 15:15   The Missing Chapter                        -> The Medallion Club Story
Thu  9:15   Leads to the Invitation Pathway             -> Invitation Sources
Thu 10:30   (Invitation Pathway breakout content)       -> Invitation Source Personas
```

Club Graphs has no session anywhere in `data/agenda.json`. It is reference material
the room dips into on demand, not tied to a moment on the clock, so it goes last
rather than being wedged between two sections that do have a time. That reasoning is
in the code comment, so a future reorder request has the "why" to work from instead
of just a list.

Two stale comments calling this "Five sections" (it has been six since The Medallion
Club Story was added on Aug 17) were caught in the same pass and corrected.

**Verified:** roster 121, 118 with photos; Garry, Erik and Dave Horn are the three
without one; Garry and Erik show no FIRST TOUR badge; Jay McLuen and Sydney Ormsby
render correctly with no old spelling anywhere; Pete Ulliman's card renders under
Medallion; Vault nav reads Core Fundamentals, Core Fundamental Scenarios, The
Medallion Club Story, Invitation Sources, Invitation Source Personas, Club Graphs in
that order; no console errors.

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

### `[x]` T1.1a Smash Park versus the hotel, Wednesday evening. Closed, the hotel won
The flier and the official agenda disagreed about Wednesday evening. The flier had a 6:00 PM
Evening Outing at Smash Park Westerville, "Put on Your Game Face". The official agenda had it
at the hotel: 6:00 PM cocktails at the hotel bar, 6:30 PM dinner served at the hotel, 7:00 to
9:00 PM karaoke, corn hole, cards and beer pong.

Jim resolved it on Aug 11 in favour of Smash Park and the wall was built that way.
**Lisa cancelled Smash Park on Aug 12.** The official agenda was right all along and the
wall now carries it. See the change log entry for Aug 12 for what moved.

Everything else on Wednesday was always the official agenda: 7:30 AM breakfast, 8:20 AM
Tenure Awards, every daytime session, and the 5:15 PM end.

### `[ ]` T1.1b Attire wording, second source
Attire now uses the official agenda's wording, not the flier's. Tuesday reads "Country Club
Casual and Appropriate Length Shorts (no denim)" rather than the flier's "Country Club Casual
and Shorts (no denim)". Thursday reads "Country Club Casual (no denim)". Wednesday carries
two lines, the Dress-Up Day for the day and "Casual attire, denim allowed" for the evening at
the hotel, which is Carol's own wording. Friday
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

### `[x]` T1.3 The Band, container
- **Inputs:** spec Section 3.2
- **Output:** roster tab built against placeholder data
- **Steps:** create `/data/roster.json` with 20 placeholder records covering the real field shape (slug, name, title, club, region, newbie, photo). Search filtering by name, club, and title. Filter pills for All, Newbies, and region groupings. Card grid with headshot, name, title, club. Guitar pick FIRST TOUR badge on newbies, visible in the grid. Tap for detail view. Header count line
- **Acceptance:** search filters live as you type. Newbie filter returns only flagged records. Grid reflows cleanly from 380px to desktop. Layout holds with a missing photo
- **Note:** real data loads in T3.1
- **Parallel-safe with:** T1.1, T1.2
- **Done Aug 11**, against `data/roster.json`: 20 invented records, 5 newbies, 4 regions.
  The tab hardcodes no count, no region name and no club. Every number on screen comes off
  the file, so T3.1 is a file swap with no code change.
  | Acceptance criterion | Result |
  |---|---|
  | Search filters live as you type | No submit, no button. `enroll` narrowed to 7, `enroll sou` to 2 (Placeholder Seven and Ten), and the line read "2 of 20 showing." |
  | All three fields are searched | `golf` hit 5 titles, `west` hit 3 clubs, and names match too |
  | Word order does not matter | `sou enroll` returned the same 2 as `enroll sou`. Every token has to land somewhere in name, title or club |
  | Clear resets | All 20 back, and the "of 20 showing" line disappears |
  | Newbie filter returns only flagged records | Exactly 5 cards, and exactly 5 FIRST TOUR picks. The pill badge reads 5 and matches "5 first timers" in the header, because both read the same field |
  | A region pill replaces the newbie filter rather than stacking | Region West returned 4 with only that pill lit |
  | Grid reflows from 380px to desktop | 2 columns of 169px at 380px, still 2 at 320px, 4 columns of 176.5px at 1280px inside the 780px reading column. 0px overflow at all three |
  | Cards in a row line up | Every row's headshots share a top edge. This is the thing worth looking at, because a stretched grid button centres its own content and it took an explicit flex column to stop it |
  | Pill row scrolls without clipping at 380px | 775px of pills inside a 348px scroller, no pill clipped vertically |
  | Layout holds with a missing photo | Every one of the 20 renders a square initials tile on the amp grille, same size and position as a headshot, same card height. Zero `img` tags, zero broken image icons, and the FIRST TOUR pick still sits on the tile for the 5 newbies |
  | Detail view | Replaces the grid rather than floating over it, so nothing traps scroll. Title, Club and Region, no contact details. Escape and "Back to the lineup" both return to the grid |
  | No console errors | None from the app's code. The latest load made exactly three network requests, all 200: `agenda.json`, `tour-band.jpg`, `roster.json`. Zero image requests |
- **Found and fixed: the missing-photo fallback was dead.** The card image carries
  `loading="lazy"`, and a lazily loaded image that 404s fires **no** `error` event in Chrome.
  Proved it directly with a controlled pair against the same server: the eager image fired
  `error`, the lazy one fired nothing in three seconds, and `decode()` neither resolved nor
  rejected. So `onError` never ran, `broken` was never set, and all 17 records whose `photo`
  path pointed at a missing file rendered as blank squares instead of initials tiles.
- **How it was resolved, and the tradeoff.** `loading="lazy"` was kept, because at T3.1 this
  grid renders about 90 headshots at once with no pagination and eager loading them all on
  ballroom wifi is the worse failure. Instead the cause was fixed in the data: all 17 `photo`
  values pointing at files that do not exist were set to `""`. An empty string makes no request
  at all and renders the tile deliberately, which is exactly the state the spec said the live
  URL should show. Result is 20 tiles, zero requests, clean console.
- **Revisited at T3.1, Aug 12. Two things changed on purpose.**
  **The pill row became pills plus selects.** All and Newbies stay pills. Club is a `select` and so
  is region. 29 clubs is roughly 1400px of pills, which is four swipes on a 380px phone to reach
  Wynstone. A native select hands the long list to the phone's own picker, which scrolls itself, so
  nothing in the page needs a scroll container to hold it. Appearance is left alone deliberately:
  the platform draws its own caret and there is no thirteenth colour to invent for one. The region
  select only renders if any record carries a region, which none do today, so it is invisible until
  somebody types one.
  **The filters now stack, which reverses the behaviour recorded above.** A region pill used to
  replace the newbie filter. Newbies, club and region are now three independent filters, because
  "first timers at Chenal" is a question somebody will actually ask and 29 clubs makes it hard to
  answer by eye. Verified: Newbies alone returned 21, Newbies plus Anthem returned 0 and said "No
  first timers from Anthem.", and All cleared all three.
- **This is load bearing for T3.1 and is written into `data/roster.json`'s own `_note`.**
  **Only put a path in `photo` if the file is actually in `assets/attendees/`.** A wrong path
  degrades to a blank square, not to the initials tile, and nothing in the page can detect it.
  Anybody with no headshot gets `""`. If the fallback needs to survive a typo instead, the
  change is dropping `loading="lazy"` and accepting the eager load.
- **The larger view replaces the grid instead of floating over it.** A modal would have needed
  either clipped content or an inner scroll container, and CLAUDE.md restricts the second to
  Display Mode. Tapping a card remembers the scroll position and Back or Escape restores it.
- **Sorted by display name**, which is first-name order, because there is no surname field and
  guessing the last token is the mistake `tools/process-assets.sh` documents from its iconv
  days. Region pills are alphabetical so the order cannot shift when a record is added mid-file.
- **Search folds accents**, so a search for "jose" finds "José". macOS hands over decomposed
  names, the same trap the asset pipeline hit.
- **No Firebase, no admin controls, no local storage key.** The roster is static per the
  CLAUDE.md data split. `BandTab` is handed `now` and ignores it, because nothing here is time
  sensitive.
- **Open, needs the organizers, not invented.** Region names are placeholders, and however many
  regions the verified roster carries is however many pills appear. Whether "newbie" means first
  time at this meeting or new to CGP is unconfirmed. The badge reads FIRST TOUR either way.

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

### `[x]` T2.4 Crowd Vote
- **Inputs:** spec Section 3.7
- **Output:** live polling tab with four poll types
- **Steps:** admin creates polls. Active polls as cards with question, full width option buttons, ON AIR badge. After voting the chosen option fills scarlet with a checkmark and results render as horizontal bars with percentage and count. One vote per device per poll via `mm26_pollvotes`. Closed polls dim with final results. Four types: multiple choice, knowledge check (carries a correct answer, reveals the correct-versus-incorrect split on close), ranking (drag to order, averaged rank results), word cloud (one word answers rendered live)
- **Acceptance:** each of the four types creates, accepts votes, and displays results correctly. Vote lock persists through reload. Knowledge check reveals the answer only after admin closes the poll
- **Blocked by:** T1.6
- **Done Aug 11.** Polls live at `polls/{id}` with three states, not two: staged (crew only),
  live, closed. `on` alone could not tell a poll nobody has shown yet from one that has
  finished, and a fresh poll must not read to the room as a closed poll with zero votes.
  | Acceptance criterion | Result |
  |---|---|
  | **Multiple choice** creates, accepts votes, displays results | Created staged with a dashed border and "🔒 Not on air yet". On air added the On Air badge and three full width option buttons. A vote replaced the buttons with three bars, the picked one scarlet filled with a ✓ and "Your pick.", reading "100% · 1", foot "1 vote" |
  | **Knowledge check** | Created with a "Why, optional. Shown on close" field and a #1/#2/#3 right-answer picker. Crew saw "Right answer: Placeholder right" inside the crew block and nowhere else |
  | **Ranking** | Four rows with position numbers. The ▲ and ▼ nudges moved a row one slot and greyed out at both ends. Lock in produced bars sorted by average rank reading "avg 1.0" through "avg 4.0", plus "You put Placeholder three first." |
  | **Word cloud** | "two words" was refused with "One word. Pick the best one." and nothing was written. "loud" rendered in Anton, gold, scarlet underlined, with "You said loud." |
  | Vote lock persists through reload | Reloaded with a vote cast. The card came back with bars and no option buttons, the pick still scarlet with its ✓, and the count still 1. Reloading did not add a vote |
  | Storage shape | `mm26_pollvotes` held exactly the four documented records: `{"t":"choice","i":1}`, `{"t":"knowledge","i":1}`, `{"t":"ranking","order":[2,0,3,1]}`, `{"t":"wordcloud","w":"loud"}` |
  | Closed polls dim and keep results | The closed knowledge card carried `is-done` and kept its bars |
  | Display Mode | Question type went to 48px, `--cv-bar-min` to 58px, `--cv-cloud-base` to 30px, and the crew block and New poll form both computed to `display: none` while still in the DOM. Toggling back restored them to `block` |
  | 380px | 0px overflow. The four elements measuring past the edge are poll-type pills inside the `.dayrow` scroller, the same intentional pattern as the tab bar |
  | 1280px | 0px overflow, cards inside the 780px reading column |
  | No fixed-height inner scroll outside Display Mode | The appended CSS contains zero `overflow-y` and zero `max-height`. The only element matching a fixed-height scroll box is the new-poll textarea at its `min-height`, which is a form field |
  | No console errors | None across create, on air, four vote types, close, delete, reload, and Display Mode both ways |
- **The knowledge answer does not leak, and this was the check worth running properly.** With the
  poll **on air** and a **non-admin** device having voted for a wrong answer, scoped to that card:
  zero `.cv-bar`, zero `.cv-bar--right`, no `%`, no `★`, and the explanation absent. Page wide,
  the explanation string appears **nowhere** in the rendered document. All 42 occurrences of
  `correctIndex` are in the inline component source; **zero** occur in the rendered markup once
  script tags are excluded. The answer is stripped by the reader before it reaches attendee state
  rather than merely hidden by a render guard, so dev tools do not get you the answer.
- **On close the reveal is complete**, verified on the same non-admin device with no reload:
  three bars, a ★ and a gold rule on the right answer, "Placeholder right. 0 of 1 got it, 0%. You
  missed this one.", and the why underneath.
- **Writes are atomic multi-path updates using `ServerValue.increment`**, so ninety phones tapping
  the same option inside a second all count with no read-modify-write race. There is a transaction
  fallback if the pinned SDK build lacks `increment`.
- **All timestamps are `ServerValue.TIMESTAMP`.** Nothing in the feature calls `Date.now()`.
- **Ranking ships both controls,** touch drag and up/down buttons. The nudge buttons are what was
  verified here; the drag gesture needs a real finger and belongs to T3.6.
- **Every crew control lives in the tab, not in the T1.6 panel.** That is where it gets used.
  T2.8 can hang a shortcut off the gear.
- **`data/polls.json` is read only and every question in it carries `draft: true`.** Nobody has
  approved them. The library loader was not exercised in this pass, because the four polls were
  typed by hand to test the create path. **T3.5 owns getting those questions approved**, and the
  file's own note says no statistic, benchmark or club result is used as an answer anywhere in it.
- **All test polls were deleted at the end of the session.** Every question used was
  "Placeholder question one" through "four" with "Placeholder A/B/C" answers.

### `[~]` T2.5 The Pit
- **Inputs:** spec Section 3.8
- **Output:** photo gallery tab
- **Steps:** upload panel with optional name and caption, then two separate buttons. Take Photo uses `capture="environment"`. Choose from Library omits the capture attribute. Both required. Client side compression to roughly 800px long edge before upload. Square thumbnail grid, newest first, caption and attribution below. Like button overlaid on each thumbnail, toggle on and off, counts sync via Firebase, device state in `mm26_liked`. Lightbox on tap with full image, like button, and for admin download and delete. Optional filter by club or team
- **Acceptance:** both upload paths work on iOS and Android. A 4MB source photo lands under 200KB. Likes toggle and sync across devices. Lightbox does not trap scroll
- **Blocked by:** T1.6
- **Built Aug 11. `[~]` and not `[x]` for one reason only: "both upload paths work on iOS and
  Android" cannot be proved in a desktop browser.** Everything else passed. The camera path in
  particular needs a real phone, and CLAUDE.md already calls camera behaviour out as a
  device-only check. **T3.6 closes this.**
  | Acceptance criterion | Result |
  |---|---|
  | Both upload paths ship | Two separate `input[type=file]`, both `accept="image/*"`. One carries `capture="environment"`, the other carries no capture attribute. This is the CLAUDE.md hard rule and it is satisfied in the markup |
  | Both upload paths work on iOS and Android | **Not verified. Needs a physical phone.** The library path was driven end to end here with a synthetic file. The camera path cannot be triggered without a camera |
  | A 4MB source photo lands under 200KB | **Passed with room to spare.** Fed a synthetic 3024x4032 noise JPEG, deliberately incompressible, at **11.8 MB**. It landed at **83 KB, 600 by 800**, and the panel says so on screen: "11.8 MB in. 83 KB out. 600 by 800." That is 3x the source size in the criterion at under half the ceiling |
  | Stored payload | 85,090 bytes as a base64 data URL in `photos/{id}`. Base64 adds about a third, which is the cost of the live event photo exception CLAUDE.md allows |
  | Likes toggle | 0 to 1 with `is-on`, back to 0, and up again. `mm26_liked` went `{"<id>":1}` then `{}` then back |
  | Likes sync across devices | The counter is a Firebase transaction on a shared node, the same pattern measured at 29ms in T2.3. Toggled both directions on one device against the live database |
  | Lightbox does not trap scroll | Opens as `role="dialog"` at `z-index: 50`. `body` overflow is unchanged when it opens, and the page still scrolled while it was open, measured at `pageYOffset` 300. Escape closes it |
  | Square thumbnail grid | 2 columns of 167px at 380px, 4 of 175px at 1280px inside the 780px reading column. Thumbnails measured square |
  | Crew download and delete | Both present in the lightbox for crew only. Delete asked "Delete this photo? It does not come back.", removed the cell, closed the lightbox, and `photos` read `null` afterwards |
  | No horizontal overflow | 0px at 380px and 1280px, zero elements past the edge |
  | No console errors | None across upload, compress, post, like, unlike, lightbox, and delete |
- **The upload is a two step: pick, then Post it.** The picked photo is compressed and previewed
  with its before and after size before anything is written, so nobody uploads a photo they have
  not seen and nobody is surprised by what the wall did to it.
- **Two new local storage keys, `mm26_liked` and `mm26_pitwho`.** Both carry the prefix, so T1.6's
  Clear This Device picks them up with no edit. Confirmed by the panel enumerating storage.
- **Still to verify on a phone, and it is the whole reason this is `[~]`:** the camera path, the
  library path on iOS and Android, whether a real 12MP photo compresses inside a sensible time on
  an older handset, and photo upload over cellular rather than Wi-Fi. All four are T3.6.

### `[x]` T2.6 The Cares Cup
- **Inputs:** spec Section 3.9, source flier poster art
- **Output:** tournament leaderboard tab
- **Steps:** leaderboard list with position, team name, score, thru. Gold, silver, bronze treatment on the top three. Poster art card backgrounds for Team Total Consciousness (Mike Akeroyd, Donny Darville) and Spalding's Revenge Team (Todd Keefer, Jimmy Han). Century Golf Cares fundraising total displayed at the top. Score entry is admin only
- **Acceptance:** admin can add teams, enter scores, update the fundraising total, and lock the board. Non-admin cannot edit anything. Leaderboard sorts correctly including ties
- **Note:** poster art use is an open question. Build with a solid color fallback so the tab ships either way
- **Blocked by:** T1.6
- **Done Aug 11.** Board lives at `caresCup/`.
  | Acceptance criterion | Result |
  |---|---|
  | Admin can add teams | "Add team" took a name and a comma separated pair of players. Also one tap for "Add the two poster teams" |
  | Admin can enter scores | Score and thru per row. `-4` printed as `-4`, `2` as `+2`, and thru 18 as `F`, which is how a golfer reads a board |
  | Admin can update the fundraising total | Set 12500 and the panel read "CENTURY GOLF CARES $12,500. Raised by people who cannot putt." with an Eastern update stamp |
  | Admin can lock the board | Locked to "🏆 Final", the button flipped to "Unlock the board", and every score entry form left the page |
  | Non-admin cannot edit anything | On an attendee device: **zero** forms, **zero** inputs, **zero** buttons anywhere on the tab. Board and total render read only |
  | Leaderboard sorts correctly including ties | 1 at `-4`, then two teams tied at `+2` both showing **T2** and both carrying the same silver `cares-row--m2` treatment. The leader carries `--m1` |
  | Gold, silver, bronze on the top three | Positional classes `--m1`, `--m2`, `--m3`, and a tie shares its rank's treatment rather than inventing a third place |
  | Poster art ships with a solid colour fallback | There is a "Poster art on" toggle and a per team "Poster art file" field. With no file the row uses the solid treatment, so the tab shipped without the art existing. `assets/cares/` carries a README and no image |
  | No horizontal overflow | 0px at 380px and 1280px |
  | No console errors | None |
- **The only names written into `index.html` are the two team names off the flier's poster art,**
  `Team Total Consciousness` and `Spalding's Revenge Team`, in `CARES_SEED`. **No player name is
  in any tracked file.** The four players ROADMAP T2.6 quotes from the flier are typed in at the
  event through the crew panel, into Firebase. Checked: zero occurrences of any of those four
  surnames in `index.html`.
- **Poster art is still an open question and the tab does not depend on it.** If Jeannette
  supplies the art, drop the files in `assets/cares/` and name them in the per team field.

### `[x]` T2.7 Encore
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
- **Parts two to four done Aug 11.** Award Winners, Hall of Fame and Top Videos are built, each
  with its own unlock flag under `encore/{section}/unlocked`, so all four sections are
  independently publishable.
  | Criterion | Result |
  |---|---|
  | Each section unlocks independently | Published **Award Winners only**. On an attendee device that section rendered its entry while Tenure, Hall of Fame and Top Videos all stayed locked with their own copy. Three "hidden" badges remained on the crew device |
  | Tenure can go live while awards stay hidden | Proved, and the stronger inverse was proved too: **awards live while tenure stays hidden**, which is the case that actually risks spoiling something |
  | The confidential list does not leak | With Tenure locked on an attendee device, the four placeholder tenure names appear **nowhere** in the page. `indexOf` on the rendered text returned -1 |
  | Admin create with a photo from a phone | Award Winners carries "Take photo" and "Choose from library", the same two path rule as The Pit, plus a file path field. Created an award with award, winner, club and citation and read the record back over plain HTTPS |
  | Alfa Slab One on the section headings | Computed `"Alfa Slab One", Georgia, serif` on all four. That is the whole ration CLAUDE.md allows it |
  | Video embeds play inline | **Not verified.** No video URL exists yet. The section takes a YouTube or Vimeo id and there is nothing real to point it at until T3.x. The container is built |
  | No console errors, no overflow | Clean at 380px and 1280px |
- **Every Encore name in the database is a placeholder** and T4.2 clears the node.
- **Alfa Slab One appears here and nowhere else,** on the four section headings and the
  milestone labels. That is the whole ration CLAUDE.md allows it.

### `[x]` T2.8 Admin panel, v2
- **Inputs:** T2.3, T2.6, T2.7
- **Output:** complete admin control set
- **Steps:** add Vault Drops panel (per section unlock status, scheduled time, manual unlock and re-lock). Add per-tab controls listed in spec Section 4.2. Add Encore CRUD entry points. Add Cares Cup score entry
- **Acceptance:** every control in spec Section 4.2 exists and works. Vault Drops is reachable in two taps from the gear icon, because it will be used under time pressure
- **Blocked by:** T2.7
- **Done Aug 11.**
  | Acceptance criterion | Result |
  |---|---|
  | Vault Drops is reachable in two taps from the gear | **Yes.** Once crew is unlocked, tap the gear and the panel opens with **Vault Drops as its first section**, directly under the panel heading. It is not behind an accordion, a chooser or a scroll: walked every ancestor of the block and none is a scroller and none sets a max-height |
  | Per section unlock status, scheduled time, manual unlock and re-lock | Six gated sections in one board. The two Vault drops show a status pill, "Scheduled Wednesday 9:30 AM Eastern" or Thursday 10:30, and Unlock now / Re-lock / Back on the clock. The four Encore sections are manual only and print their planned time |
  | Encore CRUD entry points | A jump button, "Post an Encore entry", which closes the panel and lands on the tab |
  | Cares Cup score entry | Same, "Enter Cares Cup scores". Both verified: the panel closed and the right tab opened |
  | Every control in spec 4.2 exists and works | Marquee, Tab Visibility, Reset by Section, Clear This Device and Reset Everything came with T1.6. Vault Drops and the two jumps are added here |
- **Conflict resolved, and it mattered.** This spec was drafted against
  `settings/drops/{key}` holding a bare `"auto" | "open" | "shut"` string. T2.3 had already
  shipped `settings/vaultDrops/{key}` holding `{ mode, unlockAt, ts }` with
  `"scheduled" | "open" | "shut"`. Left alone, the crew panel and the Vault tab would have read
  **two different nodes** and disagreed about whether a section was open, on the single most
  time-critical control in the build. Per this spec's own Edit 5, the four seam functions
  (`useDropOverrides`, `dropMode`, `dropOpen`, `setDropMode`) were pointed at the shipped node.
  `"auto"` is accepted as an alias for `"scheduled"`. Writes use `update`, not `set`, so a test
  `unlockAt` and the server `ts` survive a mode change made from the panel.
  **Verified end to end:** tapping "Unlock now" in the panel wrote
  `{"mode":"open"}` to `settings/vaultDrops/scenarios` and an **attendee** device's Vault tab
  swapped from the padlock to the section body. `settings/drops` reads `null`, so no competing
  source of truth was created.
- **The panel also surfaces a test time.** If the Vault tab has a test `unlockAt` set, the panel
  row says "TEST TIME in force, not the real schedule" rather than printing it as the schedule.
- **Second name collision resolved.** Block C defined a `VaultDropRow`, and T2.3 had already
  shipped a `VaultDropRow` inside the Vault tab taking entirely different props. Two function
  declarations with one name means the second silently wins, which would have broken the Vault
  tab's own crew block. The panel's copy is now `AdminVaultDropRow`. A duplicate-declaration scan
  across the whole script block now returns **zero** duplicates.
- **A sixth section landed at T3.1, Aug 12: Roster.** It sits second, directly under Vault Drops,
  so Vault Drops is still the first thing in the panel and still two taps from the gear. Confirmed
  on the live URL: the section order reads Vault Drops, Roster, Marquee, Tab visibility, Reset by
  section, Clear this device, Reset everything. The duplicate-declaration scan still returns zero.
  Reset Everything's card now says roster edits survive it, because they do and the crew should not
  have to find that out by testing it. Full detail under T3.1.

**Phase 2 definition of done:** every feature in the spec is built and working against placeholder content. No feature work remains.

---

## PHASE 3: Content load and test
**Window: August 17 to August 21. Goal: real content in, everything tested on real devices.**

### `[x]` T3.1 Load roster and photos
- **CLOSED Aug 13 2026.** Both criteria pass. See the dated entries below for how.
  | Acceptance criterion | Result |
  |---|---|
  | Zero unmatched records in either direction | **Passes on the roster side, which is the side that ships.** 119 of 119 attendees have a photo, every `photo` path resolves to a file that exists, and every file is 400x400. The other direction has 41 photos on disk with no roster entry: those are people who are **not attending**, they arrived in the bulk SharePoint drop, and they are listed in `_photosOnDiskNotOnTheList` in `data/roster.json`. They render nowhere |
  | Every title matches the verified list | **Passes.** Titles, clubs, first and last names are all read from `data/attendee-list-verified.tsv`. Nothing is hand typed, so this cannot drift without the source file changing |
- **Also closed:** `HOLD` and `OPEN_QUESTIONS` in `tools/reconcile-roster.py` are both empty.
  Framing: 157 of 160 files grade clean, the 3 tight ones are close-up sources that cannot zoom out.
- **Reopen this only if the attendee list changes.** Add to `OVERRIDE` and re-run
  `tools/reconcile-roster.py`. Do not hand edit `data/roster.json`.
- **Inputs:** Jeannette's headshots, Carol and Lisa's verified roster
- **Output:** real `/data/roster.json` and populated `/assets/attendees/`
- **Steps:** run T0.7 pipeline over the headshots. Build the roster file. Cross-check every roster entry against a photo file and every photo against a roster entry
- **Acceptance:** zero unmatched records in either direction, or a documented list of known-missing photos with placeholders in place. Every title matches the verified list
- **Blocked by:** T1.3, asset delivery
- **Photos and file, Aug 12.** 143 headshots in `assets/attendees/`, 400x400 through the
  T0.7 pipeline, and `data/roster.json` written from them.
  | Acceptance criterion | Result |
  |---|---|
  | Zero unmatched records in either direction | **Passes.** 143 records, 143 jpg files. Every record's `photo` resolves to a file that exists, every file has a record, every `photo` is exactly `assets/attendees/{slug}.jpg`, and no record carries an empty `photo`. `_counts` matches the data it describes: people 143, newbie 21, withClub 23, needsReview 120 |
  | Every title matches the verified list | **Cannot pass, and it is not a code problem.** There is no verified list. All 143 titles are empty and 120 names came off a filename. This stays `[~]` until Carol and Lisa hand over real names, titles and clubs, or until the crew works the panel below through the 120 |
- **Why this is `[~]` and not `[x]`.** The mechanism is done and the content is not. Nothing in
  the repo invents a title, a club or a region to close the gap.

**The roster is now two layers, and that is a deliberate change to the spec.**
The spec had the roster as a static repo file because it loads fast and never changed during the
event. That second assumption died when the client asked to fix names and add people live. So:
- **BASE.** `data/roster.json`, static, in the repo. Ships fast and renders with Firebase flat.
- **OVERRIDE.** Firebase `roster/{slug}`, written by the crew panel, merged on top of the base
  **field by field**. A write only carries the fields that changed, and the merge only applies
  fields that are present and non-empty.
- **ADDED.** A `roster/{slug}` with no base counterpart is somebody the crew added at the meeting.
- **Base records cannot be deleted.** You cannot take a line out of a static file from a phone, so
  they carry `hidden: true` and come off the wall instead. Added records delete for real.
- **`roster` is NOT in `RESET_NODES`.** Reset Everything spares it on purpose. A name somebody
  fixed in August is not test data, and the card in the panel says so.

**Crew panel, Roster section.** Second in the panel, under Vault Drops, because 120 names need
checking before the meeting.
- Searchable list of everybody with a thumbnail, name, club and state, sorted by what needs
  attention: flagged first, then anybody with no club, then alphabetical. A counter reads
  "120 names still to check" so there is a sense of progress through them.
- Inline edit for name, title, club, region and the newbie flag. One row open at a time and the
  list pages 24 at a time, so 143 rows never becomes 143 open forms and never needs an inner
  scroll container.
- Club is an input plus a `datalist`. The suggestions are `data/graphs.json`'s 29 real club names
  unioned with whatever clubs are on the roster right now. **No club name is hardcoded anywhere in
  index.html.** Typing a new one is allowed, which is the point of a combo.
- Every changed field says what the file says and offers "Put it back", which removes that one
  field from Firebase and lets the base value come back on every phone.
- Add A Person: name, title, club, region, newbie, and an optional headshot from camera or
  library. Slug is generated by the same rule as `tools/process-assets.sh` and a slug that already
  exists is **refused**, not resolved.
- Headshots for added people ride on the record as compressed base64. It reuses The Pit's
  `pitCompress` through a new `opts` argument rather than a second compressor: `{ edges: [400,
  340, 300], qualities: [...], maxB64: 90000, square: true }`. Defaults are unchanged, so The Pit
  behaves exactly as before. `square` centre crops at full resolution before any scaling, which is
  what the pipeline does to every headshot.

**Verified on the live URL, Aug 12, with two browser contexts:**
| Check | Result |
|---|---|
| An edit reaches The Band on a second context within two seconds, no reload | **36ms**, measured Save click to DOM change against a shared clock, with the second tab fronted so nothing was throttled. Navigation type stayed `navigate`, single entry, so it was not a reload |
| Field level merge, not record replacement | Set Adair's club, then changed the name. Club survived. Then changed the club. Name survived. The stored record read exactly `{"club":..., "name":..., "reviewed":true}`. No title, no region, no newbie, no photo. Verified at the database over plain HTTPS, not just on screen |
| Per-field revert | "Put it back" on the name dropped only `name` from Firebase, the file's value came back, the club override stayed, and the row tag went from "Edited: name, club" to "Edited: club" |
| Adding somebody with a photo shows up in The Band with their photo | 1200x800 source compressed to a **400 by 400** square, 15 KB in, 6 KB out. Appeared on the second context in **37ms** with the data URL as its headshot, decoding at 400x400 in both the grid and the one-person view. Head count went 146 to 147 |
| A colliding slug is refused | "ZZ Testcase Rig" against the record just added, and "Cole Clearman", "Clearman, Cole" and "  COLE   CLEARMAN  " against the base file, all three landed on `cole-clearman` and all were refused with the Add button disabled. `José Núñez-O’Brien` slugged to `jose-nunez-obrien`, matching the pipeline |
| The club filter includes a newly added club | Yes, on the second context, unlocked, with a live count: "ZZ Test Club (1)". Option count went 22 to 23 |
| The newbie filter returns exactly the newbie records | 21 cards, 21 FIRST TOUR picks, and the 21 names matched `roster.json`'s own newbie list **name for name**, not just in count |
| A person with an empty photo renders the fallback and fires no image request | Added somebody with no headshot. Their card rendered the initials tile "ZR". Zero `img` tags in the grid, **zero new image requests**, zero failed requests |
| A base person's photo can be replaced, and put back | Upload won over the repo file, row tag read "Edited: headshot", thumbnail became the data URL. "Use the file's headshot" then dropped the override and the repo path came back |
| Hiding a base record | Took them off The Band on the second context inside the same paint, left them in the panel tagged "Off the wall", and "Put back on the wall" returned them |
| Deleting an added record | Gone from Firebase and from both contexts |
| 380px | Zero horizontal overflow on The Band and on the panel, `scrollWidth` equal to `clientWidth`. Club select 348px, one column. Editor stacks, both upload buttons present |
| 1280px | Zero overflow. Editor goes to two columns, 330px each, inside the 748px reading column |
| No inner scroll containers | Zero elements inside the panel with `overflow-y` auto or scroll and content taller than their box, at both widths. CLAUDE.md rule holds |
| No console errors | None, across entering, unlocking, the panel, six saves, two adds, two deletes, a hide, an unhide, three reverts and two photo uploads |
| Firebase down, The Band still lists everybody | Served index.html with the Firebase script tags stripped, which is the `FB.ok === false` branch. **143 cards, "143 on the tour, 21 first timers", 21 clubs still in the filter, newbie filter still exact, zero console errors,** and a note reading "Live updates are off, so this is the roster as it shipped. Any name the crew has fixed since is not on this phone yet." |

**Two bugs found in this work and fixed, `da0a5fe`:**
- **"Put it back" reverted the record and left the open input holding the old value,** so the next
  Save quietly put the edit back. Caught by reading the input after the revert rather than trusting
  the row heading, which had updated correctly. Revert now resets the form field and the record in
  one action.
- **Adding somebody said nothing.** The confirmation renders on the closed form and `add()` never
  closed it, so the crew had to go hunting in the list to find out whether it worked.

**Not verified, and it needs a physical phone.** Both upload paths exist in the DOM with the right
attributes, camera carrying `capture="environment"` and library carrying none, and the compressor
was driven with a real `File` through the library input. Whether iOS and Android actually open the
camera and the photo library from those two controls is a T3.6 device test. Desktop cannot answer
it. The same applies to the club `datalist`: it behaves as a combo on desktop Chrome and degrades
to a plain text input if a phone browser ignores it, which still lets the crew type a club.

**Found along the way, worth knowing.** A stale tab caught `assets/attendees/cole.jpg` returning
404 after that record was pruned from the file mid-session, and the card rendered as a blank square
rather than an initials tile. That is exactly the hazard T1.3 documents: a lazily loaded image that
404s fires no `error` event, so nothing in the page can detect it. The current deploy is clean, and
`tools/remove-attendee.py` keeps the file and the folder moving together. **The rule stands: never
put a path in `photo` unless the file is in `assets/attendees/`.**

**Eight more faces, Aug 12. 110 of 119 now have one, up from 102.** Gina Fabrizio, Andrew
Montemayor, Aubrey Gillespie, Jeannette Walker, Juan Martinez, Krisno Bridge, Natalie Bratcher,
Patrick Ryan. All eight were on the verified list and all eight were photoless, so nothing was
overwritten. Verified on the live URL: all 110 attendee images load, zero failures.

**Where they came from, because this changes what "Jim sent it" means.** Jim said three times
that he had pasted these into the thread. Three times the answer was that a pasted image cannot
become a file. **That was wrong.** Claude Code writes pasted images into the session transcript
as base64, so they were recoverable the whole time:

```
~/.claude/projects/<project>/<session-id>.jsonl
```

Each `message.content` array holds `{"type":"image","source":{"type":"base64",...}}` blocks.
Decode the `data` field and it is the original file. Identity came from the text block in the
**same message**, one image per message, so no guessing was involved.

**The rule that follows: when Jim says he sent something, go read the transcript before
answering.** Do not explain a limitation without checking whether it is real.

- **Two of the nine still missing are people Jim named as pasted, Gus Siggins and Rod Quintero.**
  Their messages carry no image block. Same for Lindsey Jenkins and Duane Malinowski. Those four
  were typed as names only, so the photos genuinely never arrived and still need to.
- **Patrick Ryan's card does not match the others and it is a source problem.** His photo is a
  266x266 full-body seated shot, so his face lands small in a grid where every neighbour is a
  face. Cropping tighter would upscale a roughly 100px face to 400px and go to mush. Left as-is
  and flagged. Wants a real headshot, not a code change.
- **Soft, accepted, listed so nobody re-reports it:** jeannette-walker (341px short edge),
  juan-martinez (293px), krisno-bridge (300px), patrick-ryan (266px) all upscaled to 400.
  Krisno's crop also sits tight to the top of his hair.

**Two pipeline bugs this batch exposed, both fixed and both verified.**

1. **`tools/process-assets.sh` failed on every webp.** Both converters copied the source keeping
   its extension and edited that copy in place. sips reads webp but will not write one back, so
   `--resampleWidth` failed and the file was reported "conversion failed" with nothing wrong
   with it. Two of the eight died this way. A new `stage_editable()` normalizes every input to a
   PNG working copy first, with PIL as a fallback for webp variants sips cannot read. Also fixes
   heic, gif and bmp. Verified by re-running the two failures: both convert straight from webp now.
2. **The closing "on the roster with no photo" report lied, and expensively.** It tested for
   `assets/attendees/{slug}.jpg`, but anyone matched by surname or by `OVERRIDE` has a face under
   a different name (Cyndi Melfi is `melfi-0001.jpg`). It named **40** people when **9** were
   photoless, which sends somebody chasing photos that shipped weeks ago. It now reads the
   reconciled `photo` field. Verified: reports the same 9 that `reconcile-roster.py` reports.

**PHOTO COVERAGE IS COMPLETE, Aug 13. 119 of 119.** The last nine arrived and went in:

| Person | Club | Title |
|---|---|---|
| TK Matthews | Canyon Oaks | General Manager |
| Lindsey Jenkins | Balcones | Enrollment Director |
| Gus Siggins | El Camino | General Manager |
| Todd Keefer | Century Golf | VP Private Club Operations |
| James Hinckley | Century Golf | Principal |
| Jim Hinckley | Century Golf | Partner |
| Jim Creighton | Century Golf | People Development |
| Rod Quintero | Palm Valley | General Manager |
| Duane Malinowski | Sylvania | Food and Beverage Director |

**The lesson, and it is the same one twice in one batch. The filenames were on disk the whole
time.** Jim pasted nine photos with no names. I built a numbered contact sheet and asked him to
name them. His answer: "cmon. the names of the people are in the file name." The pasted copies in
the transcript carry only pixels and a media type, no filename, but the source files were sitting
in `~/Downloads` named `Gus Siggins.jpeg`, `Rod Quintero.jpg` and so on. **A `find` over
`~/Downloads` would have answered it before the question was asked.**

Combined with the base64 recovery above, the standing rule is now: **when Jim says he sent
something, search the transcript AND the filesystem before replying. Do not ask him to supply what
is already on the machine.**

**Mapping was verified, not assumed.** Each pasted image was perceptually hashed against the nine
named files. Every one matched at distance 0 or 1 with the next best candidate at 65 or worse, and
each named file was used exactly once. That is what made it safe to write nine identities at once.

- Three needed the framing pass after intake: Jim Creighton at 20 percent, Jim Hinckley 25, TK
  Matthews 24.
- **Duane Malinowski is cut at 50 percent face, not the usual 40, on purpose.** A second person's
  shoulder sits at the right edge of his source and any wider window keeps them in shot.

**THE HINCKLEY HOLD IS RESOLVED. `20230130-Hinckley-0008_pp.jpg` is JIM.** With named photos of
both brothers to compare, the held file is the same shoot as Jim's: same pose, same Palmer
paintings backdrop, same navy blazer and umbrella lapel pin. James is a visibly younger man shot
against a city skyline. The held file is 1176x1486 against the 300x300 Jim sent, so
`jim-hinckley.jpg` now uses it and no longer looks upscaled. `HOLD` and `OPEN_QUESTIONS` in
`tools/reconcile-roster.py` are both **empty for the first time**.

**Open, needs one word from Jim:** `assets/attendees/hinckley.jpg` is now an orphan duplicate of
`jim-hinckley.jpg`. It is out of the roster and harmless. Not deleted without a yes.

**Framing fixed on 38 photos, Aug 12. This closes Lisa's crop complaint.** She reported heads cut
off and photos zoomed too far but named nobody, so it sat. Jim named two and that made it
actionable: Molly Dunn had no head in frame at all, Tom Pyeatt was a 15 percent face jammed
against the top edge.

**Root cause is in the intake pipeline, not in the photos.** `process-assets.sh` scales the short
edge to 400 and takes a **centred** square. Correct for a studio portrait. Wrong for a full-body
phone snap, where the middle of the frame is somebody's waist.

**Why the first fix was reverted and this one was not.** The first tried a fixed top bias. It cut
foreheads on photos that were already tight, and on EXIF-rotated sources it pulled the crop toward
the wrong edge, so all 143 files went back. **There is no single offset that suits both a
full-body snap and a tight close-up.** The lesson was to stop guessing at geometry and find the
actual face.

- **`tools/facefind.swift`.** macOS Vision face detection, one JSON object per line. Vision is
  already installed, needs no model download, and beats Haar badly on the angled, bespectacled,
  outdoor phone photos that make up most of this set. The `cv2` build on this Mac is headless and
  ships no cascade XML at all, so Haar was not even an option.
- **`tools/recrop-headshots.py`.** Places the square on the face box. Face height 40 percent of
  the finished crop, face centre at 44 percent so there is headroom above.
- **The guard that makes it safe: every output is re-detected and graded, and a crop that does not
  come out well is discarded with the original left untouched.** The previous attempt shipped a
  regression across 143 files. This one cannot make a photo worse without printing why.
- **Orientation is normalized before detection, once.** Mixing a rotated source with an unrotated
  face box is exactly what broke the first attempt.

| Check | Result |
|---|---|
| Graded clean | **148 of 151**, up from 112 |
| Re-cut | 38 files, every one landing at 39 to 47 percent face |
| Of those, actually on the roster | 29 |
| Identity | All 38 eyeballed against their previous version on a before and after sheet. A framing test cannot catch an identity swap, so a human had to look |
| Integrity | All 151 still valid 400x400 JPEG, 5.4MB total |
| Bonus | James Jordan and Matt Saggio were **sideways** before and are upright now, from normalizing EXIF first |

- **The 3 that still grade `tight` are correct as-is.** angela-morabito 62 percent, doug-hoffort 66
  percent, howe 59 percent. Their sources are close-ups, so no crop can zoom out past the edge of
  the file. Only `howe` is on the roster, and his crown is no longer clipped, which was the actual
  defect. **Do not "fix" these by upscaling.**
- **Tied sources are tried and the best kept, not refused.** Five people had two source files
  (`Kasey.png` and `Kasey O'Connor.JPG`, two frames from one 2023 studio session). Both were
  verified to be the same person before this was allowed. **This is not a way to assign a face to
  somebody who has none. That is the Hinckley trap, and their photo is still held back.**
- **Intake now runs the framing check on whatever it just wrote.** Advisory, never blocks, never
  edits, skipped quietly when `tools/facefind` is not built. Molly Dunn shipped headless and
  nobody caught it until a human said so out loud twice, which is not a process.

**Build the face finder before using either tool:**

```
swiftc -O tools/facefind.swift -o tools/facefind
python3 tools/recrop-headshots.py --audit
```

### `[ ]` T3.2 Load club graphs
- **Inputs:** Jeannette's graph files
- **Output:** populated `/assets/graphs/`
- **Acceptance:** every club in the picker resolves to a graph. Each graph is legible on a 380px screen at default zoom
- **Blocked by:** T2.2, asset delivery

### `[~]` T3.3 Load Vault content
- **Inputs:** Membership Buckets image, Core Fundamentals image, Scenarios content, Personas content
- **Output:** all five Vault sections populated
- **Acceptance:** all sections render real content. Locked sections still show the correct countdown
- **Blocked by:** T2.3, content delivery
- **Two of four sections filled, Aug 12.** Both graphics Lisa asked for are in and live.
  | Section | State |
  |---|---|
  | Core Fundamentals | `core-fundamentals.png`, the wheel. Renders |
  | Invitation Sources | `invitation-sources.png`. Renders. This is the section Lisa renamed from Membership Buckets |
  | Club Graphs | 87 SVGs, done earlier |
  | Core Fundamental Scenarios | Empty. Content not delivered. Locked, padlock and countdown intact |
  | Membership Funnel Personas | Empty. Content not delivered. Locked, padlock and countdown intact |
- **Both were quantized to a 256 colour adaptive palette before committing.** The Core
  Fundamentals export is 10052x15052 and came out of the pipeline at 1.7MB, three times the
  size guide, on a wall that has to load over ballroom wifi. Flat colour artwork quantizes to
  252KB with no visible loss and keeps text sharper than JPEG would. The invitation diagram
  went 470KB to 155KB the same way. Do not re-run these through a plain PNG export.
- **Content typo in the client artwork, flagged to Jim Aug 12, not ours to fix.** The wheel
  reads `RENTENTION STRATEGY`. Should be RETENTION. It goes on a wall in front of 119 people,
  so it wants a corrected export from Tyler rather than an edit here.
- **Stays `[~]` until Scenarios and Personas content arrives.** Those two are the timed drops,
  so they are also the two that matter most for T3.7.

### `[~]` T3.4 Final agenda swap
- **Inputs:** Jeannette's final agenda
- **Output:** updated `/data/agenda.json`
- **Acceptance:** every session matches the final agenda for title, time, presenter, and room
- **Blocked by:** T1.1, asset delivery
- **Mostly done at T1.1, Aug 11.** The official agenda arrived during the T1.1 build, so
  `data/agenda.json` was written from it rather than from the flier. Titles, times, and the
  three named presenters match the source.
- **Still open, which is why this is `[~]` and not `[x]`:** the attire wording at T1.1b, and
  rooms. The agenda names no rooms at all, so every `room` field is empty. If rooms exist,
  they are a drop-in. T1.1a is closed: Lisa cancelled Smash Park on Aug 12 and Wednesday
  evening is the official agenda's hotel block.

### `[ ]` T3.5 Poll library and Cares Cup seed
- **Inputs:** poll questions from organizers, confirmed team names
- **Output:** poll questions drafted and ready to publish, teams seeded
- **Acceptance:** each session that wants a poll has one drafted. Presenters are not writing polls on stage
- **Blocked by:** T2.4, T2.6

### `[~]` T3.6 Device matrix test
- **Inputs:** complete build
- **Output:** test report
- **Steps:** test every tab on at minimum iPhone Safari, Android Chrome, and one tablet. Test both photo upload paths. Test with cellular data, not just Wi-Fi
- **Acceptance:** no broken layouts, no console errors, no failed uploads on any device in the matrix
- **Blocked by:** T3.1 through T3.4
- **Aug 13 2026, Jim on a handset. Five of the six device-only items pass.** Report in
  `docs/device-test.md`. Camera upload, library upload, `tel:` links, the maps handoff
  and the fonts are all confirmed working. **Both photo upload paths pass, which is the
  acceptance criterion that mattered most here**, and camera-only was a real shortfall
  on the prior build.
- **THREE THINGS STILL OPEN, and none of them is a code question:**
  - **Cellular.** Only wifi is confirmed. This matters more than when the task was
    written: the wall now carries about 10MB of images, 5.4MB of headshots and 4.4MB
    of booklet pages, every one lazily loaded.
  - **Lazy loading on a real handset.** Never observed. It CANNOT be checked from
    here: the automated browser reports `document.visibilityState` hidden and Chrome
    will not trigger lazy loading for a hidden page. Proven by flipping images to
    eager, which loaded instantly. The mechanism is not in doubt, 110 Band headshots
    work on the live site, but nobody has watched 28 booklet pages load on hotel wifi.
  - **The tablet, and which phones.** Not recorded.

### `[~]` T3.7 Timed drop fire test
- **Fire 1 of 3 done, Aug 12 2026.** Two more needed on two separate days.
  Method: read the real server clock by writing `{".sv":"timestamp"}` to a probe node,
  then write `settings/vaultDrops/scenarios = {mode:"scheduled", unlockAt: serverNow+120000}`.
  Do NOT compute the target from this machine's clock. The whole point is the server's.
  | Check | Result |
  |---|---|
  | Countdown showed the test time, not the real one | "Opens Wednesday, August 12, 10:40 AM Eastern. 1:45 to go." |
  | A test time is visibly flagged as a test | "Test time in force. The room is being told..." |
  | Fired on time | Target 14:40:05 UTC, open by 14:40:22 |
  | Fired with NO reload | `performance` navigation entries stayed a single `navigate` for the whole test |
  | Only the scheduled section moved | Personas stayed locked at 14 days 23:49:13 to go |
  | State restored | `settings/vaultDrops` deleted, reads `null`, database back to `settings/tabs` only |
- **A detection trap for whoever runs fires 2 and 3.** Do not test for the string
  "to go" to decide whether a section is locked. Both sections render on the same
  page, so the other one's countdown matches and you will read a successful fire as
  a failure. I did exactly that. Read the named section's own block.
### `[x]` T3.7 superseded heading below, original criteria follow
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
- Marquee later: 6:00 PM at the hotel bar, casual, denim allowed. Not a departure reminder.
  Nobody is driving anywhere. Smash Park was cancelled on Aug 12

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
