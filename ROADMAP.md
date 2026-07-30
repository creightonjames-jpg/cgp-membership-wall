# ROADMAP: CGP Membership Meeting Live Wall

Task breakdown for the build. Every task has an ID, inputs, output, and acceptance criteria. Work phases in order. Within a phase, tasks marked parallel-safe can run concurrently.

**Meeting opens August 25, 2026. Build window is 26 days from July 30.**

Mark tasks complete by editing this file. Do not mark a task complete until its acceptance criteria pass.

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
- **Done July 30.** Repo `creightonjames-jpg/cgp-membership-wall`, public, Pages from `main` at root.
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
- **Done July 30.** New project `cgp-membership-wall-2026`, project number 986050588933. Separate from `lc26-wall`, which is still in the account.
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

### `[ ]` T0.3 Design tokens
- **Inputs:** spec Section 2, source flier
- **Output:** CSS variable block and font loading in `index.html`
- **Steps:** implement all twelve palette tokens. Load Anton, Alfa Slab One, and Inter from Google Fonts. Build the two gradients: radial stage glow and scarlet to oxblood linear
- **Acceptance:** a test page renders every token as a labeled swatch and every font in a sample line. Verified on a phone, not desktop responsive mode
- **Blocked by:** T0.1

### `[ ]` T0.4 Motif primitives
- **Inputs:** spec Section 2.3
- **Output:** reusable CSS classes for each motif
- **Steps:** build ticket stub card (dashed perforation, two notch cutouts), guitar pick badge (clip-path rounded triangle), amp grille texture (low opacity diagonal halftone), stage light glow, marquee strip with bulb border, vinyl label concentric circles
- **Acceptance:** each motif renders correctly at 380px width and at desktop width. No horizontal overflow
- **Blocked by:** T0.3

### `[ ]` T0.5 App shell
- **Inputs:** T0.3, T0.4
- **Output:** welcome screen, header, tab bar, marquee banner
- **Steps:** welcome hero with stage glow, event title, countdown to August 25, QR code, enter button. Header with brand mark, admin gear, Display Mode toggle. Horizontally scrolling tab bar with icon, name, and count badge slot. Marquee banner slot at the top of all tabs
- **Acceptance:** navigation works between all ten tab stubs. Tab bar scrolls without clipping on a 380px viewport. Countdown shows correct time remaining
- **Blocked by:** T0.4
- **Added July 30, mobile app layer.** Approved scope beyond the spec. Web app manifest, scarlet app icon, `apple-touch-icon`, standalone display mode, and safe area insets for notch and home indicator. **No service worker.** Offline caching was considered and rejected: it fights the deploy loop and can serve a stale build to one phone mid-meeting while every other device has the current one
- **Added acceptance:** Add to Home Screen produces the app icon, not a screenshot bookmark. Launched from the home screen the page opens without browser chrome. No content sits under the notch or the home indicator. Verified on a physical iPhone and a physical Android

### `[ ]` T0.6 Tab scaffold
- **Inputs:** spec Section 3
- **Output:** ten stub components, wired to the tab bar
- **Steps:** create empty components for The Setlist, The Band, Backstage Pass, Soundcheck, The Vault, Liner Notes, Crowd Vote, The Pit, The Cares Cup, Encore. Each renders its name and a placeholder line
- **Acceptance:** every tab is reachable and renders without console errors
- **Blocked by:** T0.5

### `[ ]` T0.7 Asset intake pipeline
- **Inputs:** naming conventions from spec Section 5.3
- **Output:** a script that processes incoming images
- **Steps:** script accepts a folder of raw images, resizes attendee photos to 400x400 square, resizes graphs and resource images to max 1600px wide, compresses to reasonable file size, renames to the slug convention, and writes into the correct `/assets` subfolder. Report any file it could not match to a roster entry
- **Acceptance:** run against five test images and confirm correct output paths, dimensions, and file sizes
- **Parallel-safe:** yes

### `[ ]` T0.8 Deploy and verify
- **Inputs:** all of Phase 0
- **Output:** working skeleton on the live URL
- **Acceptance:** the URL loads on three different physical phones (at minimum one iOS, one Android). All ten tabs reachable. No console errors. Fonts render, not fallbacks
- **Blocked by:** T0.6

**Phase 0 definition of done:** a person can open the URL on their phone, see the themed welcome screen, tap into all ten tabs, and the design system is fully implemented.

---

## PHASE 1: Static and text tabs
**Window: August 3 to August 10. Goal: every tab that does not depend on Jeannette's assets is finished.**

### `[ ]` T1.1 The Setlist
- **Inputs:** source flier agenda, spec Section 3.1
- **Output:** complete agenda tab
- **Steps:** build the agenda data file at `/data/agenda.json` from the flier. Four day pills (Tue 8/25 Roadie Stop, Wed 8/26 Takes the Stage, Thu 8/27 Backstage Pass, Fri 8/28 Departures). Session cards as ticket stubs. Live session ON AIR pulse, completed sessions dimmed and struck through, 30 minute countdown. Tap to expand for description, presenter, room. Four reactions per session with Firebase counters and local storage single-cast tracking. Attire tag per day. Inline links to Smash Park, hotel, and club on the relevant sessions
- **Acceptance:** all four days render. Reactions increment in Firebase and lock per device. Set the system clock forward to test the ON AIR state and the dimming
- **Note:** replace agenda content when Jeannette's final agenda arrives (T3.x)
- **Blocked by:** T0.8

### `[ ]` T1.2 Backstage Pass
- **Inputs:** source flier logistics, spec Section 3.3
- **Output:** complete logistics tab
- **Steps:** ticket stub panels for Where You Sleep, Where You Play, Where You Eat, Getting Here, Getting Around, Who To Call. Venue cards for Embassy Suites Columbus (2700 Corporate Exchange Drive, 614-890-8600), The Medallion Club (5000 Club Drive Westerville, 614-794-6999), Smash Park Westerville (495 Polaris Parkway, 614-502-6993). Travel panel with CMH flight confirmations to Yolanda, AVIS code Q357518, National code SMB727V, one car per team. Contacts: Carol 281-804-6719 for meeting questions, Yolanda 214-952-8269 for flights and cars. Attire table by day. Video of the Year reminder panel, August 1 deadline to Jeannette
- **Acceptance:** every phone number is tappable and dials. Every address opens the device maps app. Every website link opens in a new tab. Verified on iOS and Android
- **Parallel-safe with:** T1.1

### `[ ]` T1.3 The Band, container
- **Inputs:** spec Section 3.2
- **Output:** roster tab built against placeholder data
- **Steps:** create `/data/roster.json` with 20 placeholder records covering the real field shape (slug, name, title, club, region, newbie, photo). Search filtering by name, club, and title. Filter pills for All, Newbies, and region groupings. Card grid with headshot, name, title, club. Guitar pick FIRST TOUR badge on newbies, visible in the grid. Tap for detail view. Header count line
- **Acceptance:** search filters live as you type. Newbie filter returns only flagged records. Grid reflows cleanly from 380px to desktop. Layout holds with a missing photo
- **Note:** real data loads in T3.1
- **Parallel-safe with:** T1.1, T1.2

### `[ ]` T1.4 Soundcheck
- **Inputs:** spec Section 3.4
- **Output:** complete Q&A tab
- **Steps:** submission panel with optional name, optional club, category dropdown (Membership Sales, Retention, Programming, Pricing, Operations, Other), anonymous toggle, question body. Sort pills Top and New. Category filter pills plus Show Answered toggle. Question cards with upvote, count, text, attribution, timestamp, category tag. One vote per device per question via `mm26_voted`, voted state scarlet and locked. Display Mode variant with large type, top questions only, no inputs, auto-scroll. Admin: delete, mark answered, pin, CSV export grouped by category
- **Acceptance:** submit from one device and confirm it appears on a second device within two seconds. Vote once, reload, confirm the lock persists. Display Mode is legible from across a room. CSV opens cleanly in Excel
- **Blocked by:** T0.8

### `[ ]` T1.5 Liner Notes
- **Inputs:** spec Section 3.6
- **Output:** complete takeaways tab
- **Steps:** day filter pills All, Wed, Thu. Submission panel with optional name and club, takeaway text, auto day tag from current date. Reverse chronological cards with attribution, day tag, timestamp. Pinned items at top with scarlet left border. Admin: pin, delete, Markdown export
- **Acceptance:** posts sync across devices. Day tag matches the posting date. Markdown export renders correctly when pasted into a Markdown viewer
- **Parallel-safe with:** T1.4

### `[ ]` T1.6 Admin panel, v1
- **Inputs:** spec Section 4
- **Output:** PIN gating and core admin controls
- **Steps:** gear icon in header, four digit PIN prompt, unlocked state persists for the session. Panel with Marquee (post and dismiss announcements), Tab Visibility (toggle per tab, hidden tabs stay visible to admin with a padlock), Reset by Section (per Firebase node with confirmation), Clear This Device (local storage only), Reset Everything (double confirmation, all nodes plus local state)
- **Acceptance:** wrong PIN is rejected. Toggling a tab off removes it for a non-admin device within two seconds and leaves it visible to admin with a padlock. Each reset clears only its own node. Reset Everything clears all nodes and all `mm26_` keys
- **Blocked by:** T1.4

**Phase 1 definition of done:** The Setlist, Backstage Pass, Soundcheck, Liner Notes, and the admin panel are production ready. The Band is complete except for real data.

---

## PHASE 2: Dynamic tabs
**Window: August 10 to August 17. Goal: every remaining feature is built, including the timed drop engine.**

### `[ ]` T2.1 The Vault, shell and navigation
- **Inputs:** spec Section 3.5
- **Output:** resource tab structure
- **Steps:** five sections: Core Fundamentals, Membership Buckets, Club Graphs, Core Fundamental Scenarios, Membership Funnel Personas. Section navigation as a left rail on desktop and pills on mobile. Image sections render full width with pinch to zoom and a download link
- **Acceptance:** all five sections reachable. Placeholder images zoom and download correctly
- **Blocked by:** T1.6

### `[ ]` T2.2 Club graph picker
- **Inputs:** T2.1
- **Output:** searchable club selector inside the Club Graphs section
- **Steps:** search or dropdown selector, then load that club's graph. Do not stack all graphs on one scroll
- **Acceptance:** every club in the list resolves to a graph or a clear "graph not available" state. Search finds a club by partial name
- **Blocked by:** T2.1

### `[ ]` T2.3 Timed drop engine
- **Inputs:** spec Section 3.5, confirmed unlock times
- **Output:** scheduled reveal system with admin override
- **Steps:** each locked section carries an `unlockAt` timestamp anchored to Eastern. On load, compute the device clock offset against a Firebase server timestamp and use the corrected time. Attendees see the section greyed with a padlock, the unlock time, and a live countdown. Admin always sees unlocked content with a padlock badge indicating the room cannot see it. Admin override unlocks early or re-locks, stored in Firebase settings so it syncs to all devices
- **Acceptance:** set a test unlock two minutes out and watch it fire without a page refresh. Change the device clock by six hours and confirm the server offset corrects it. Admin unlock propagates to a second device within two seconds. Admin re-lock also propagates
- **Critical:** this is the highest risk feature in the build. Test it three separate times on three different days
- **Blocked by:** T2.1

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

### `[ ]` T2.7 Encore
- **Inputs:** spec Section 3.10
- **Output:** recognition tab, scaffolded and admin editable
- **Steps:** four sections, each independently unlockable: Award Winners (winner photo on vinyl label background, award name in Alfa Slab One, club, citation), Hall of Fame (inductee cards with photo, club, year, citation), Top Videos (YouTube or Vimeo embeds), Tenure Recognition (grouped by milestone with photo, name, club, years). Full admin create, edit, and delete on every section so content can be posted live from the Awards Show
- **Acceptance:** admin can create an award entry with a photo and citation from a phone in under a minute. Video embeds play inline. Each section unlocks independently. Tenure can go live while awards stay hidden
- **Blocked by:** T1.6

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

### `[ ]` T3.4 Final agenda swap
- **Inputs:** Jeannette's final agenda
- **Output:** updated `/data/agenda.json`
- **Acceptance:** every session matches the final agenda for title, time, presenter, and room
- **Blocked by:** T1.1, asset delivery

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
- **9:30 AM: Core Fundamental Scenarios unlock. Verify it fired**
- Marquee: Dress-Up Day photo prompt, pointing people to The Pit
- Marquee later: Smash Park departure reminder, denim allowed

### `[ ]` T5.3 Thursday August 27
- **10:30 AM: Membership Funnel Personas unlock. Verify it fired**
- Reveal Tenure section if tenure is presented today
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
