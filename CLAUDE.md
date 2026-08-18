# CLAUDE.md

Standing instructions for this repository. Read before acting in any session.

---

## The project

A mobile web application serving as the electronic hub for Century Golf Partners' 2026 Private Clubs Membership Meeting, August 25 to 28, 2026, in Columbus, Ohio. Attendees reach it by QR code. The meeting theme is a rock tour and the wall carries that theme throughout.

You are working with Jim Creighton, Director of People Development and Innovation at CGP. The meeting organizers are Carol and Lisa. Assets come from Jeannette Walker.

Reference documents:
- `ROADMAP.md` in this repo. Phased task list with acceptance criteria. Work it in order.
- `CGP_Membership_LiveWall_Spec.docx`. Full feature and UI specification.
- The source flier. Origin of the palette, the voice, the agenda, and all logistics detail.

---

## How to work with Jim

**Plan before executing.** For any structural change, new feature, or bulk operation, state what you are going to do and get a green light. For typos, copy tweaks, and single-value adjustments, just do it.

**Ask instead of assuming.** When scope or content is ambiguous, ask one focused question with two to four concrete options. Do not fill gaps with invented roster entries, club names, financial figures, or attendee data. If real data is missing, use a clearly labeled placeholder and say so.

**Read before you write.** Read any file before editing it. Do not pattern-match from memory when the file is available.

**Never delete without approval.** Confirm what is being removed and wait.

**Verify your own work.** Check syntax and brace balance after every code edit. Run the acceptance criteria in `ROADMAP.md` before marking a task complete. Catch problems before Jim does.

**Report against the roadmap.** When you finish work, say which task IDs moved and whether their acceptance criteria passed.

---

## Voice rules

These apply to every word that ships: interface copy, empty states, confirmations, error messages, commit messages, documentation, and anything written for Jim or the client.

**Required:**
- No em-dashes. Use periods, commas, parentheses, or restructure the sentence.
- Plain verbs. "Use" not "utilize." "Show" not "demonstrate." "Help" not "facilitate."
- Short sentences. Two short beats beat one long one.
- Direct address. Talk to the reader.
- Concrete over abstract. Name the thing.

**Forbidden:**
- Negate-then-assert constructions. "This is not just X, it is Y."
- Decorative tricolons. "Clear, concise, and compelling."
- Filler transitions. "It is worth noting that." "That said." "Ultimately."
- Empty sign-offs. "Hope this helps." "Let me know if you need anything else."

**Interface voice specifically.** The flier set the register: short, dry, a little irreverent, never precious. Working examples from the flier are "Just Birdies, Beer and Broken Dreams," "Take a bow, you earned it," and "We heard the awards presentations were getting a little predictable. Fixed it." Match that. An empty photo gallery reads "No photos yet. Somebody go find the drummer." Keep it short and keep it dry.

**Client terminology.** CGP properties are called clubs, never properties.

---

## Architecture

**Stack**
- React 18 via CDN, single `index.html`, inline Babel transpilation
- Firebase Realtime Database for live state
- GitHub Pages from repo root
- Google Fonts: Anton, Alfa Slab One, Inter

**File layout**
```
/index.html                            app logic
/data/attendee-list-verified.tsv       SOURCE OF TRUTH for who is attending
/data/roster.json                      GENERATED from the tsv. Never hand edit
/data/agenda.json                      session schedule
/assets/attendees/{slug}.jpg           headshots, 400x400
/assets/graphs/{club-slug}.png         per-club membership graphs
/assets/resources/                      Buckets and Core Fundamentals images
/assets/brand/                          logo and textures
/CLAUDE.md
/ROADMAP.md
```

**data/roster.json is generated, not authored.** `tools/reconcile-roster.py` rebuilds
it from `data/attendee-list-verified.tsv`, the list from Carol and Lisa. A title fix,
a club move, or a new attendee goes in the TSV, then rerun the reconciler. Editing
roster.json directly appears to work and then vanishes the next time anybody adds a
headshot, because `tools/add-headshots.sh` runs the reconciler at the end. This
happened on Aug 17: three title changes and a club move were made in roster.json,
committed, and silently reverted an hour later.

**The data split.** This is the rule that keeps the wall fast. Anything created during the meeting goes in Firebase. Anything fixed before the meeting lives in the repo as a static file.

| Content | Location |
|---|---|
| Attendee photos, club graphs, resource images | Repo, static |
| Roster, agenda, logistics | Repo, static |
| Questions, polls, takeaways, reactions, likes | Firebase |
| Live event photos | Firebase, compressed to ~800px |
| Cares Cup scores, Encore content | Firebase |
| Tab visibility, vault unlock state, marquee | Firebase `settings/` |
| Per device vote and like history | Local storage, `mm26_` prefix |
| Videos | YouTube or Vimeo unlisted embeds |

**Firebase nodes:** `settings/`, `announcements/`, `questions/`, `polls/`, `takeaways/`, `photos/`, `photoComments/`, `reactions/`, `caresCup/` (scores, fundraising, and `pledges/`), `encore/`, `weather/`

**Local storage keys:** `mm26_voted`, `mm26_reacted`, `mm26_pollvotes`, `mm26_liked`, `mm26_entered`

---

## Hard rules

**Firebase security rules are permanent.** They must read exactly `{ "rules": { ".read": true, ".write": true } }` with no expiration clause and no date comparison. Firebase applies a default test-mode rule that expires after 30 days. On the prior build that rule fired mid-event and the entire wall went blank while the data sat intact behind a denied read. Verify the published rules by reading them back, not by assuming a paste worked.

**No base64 images in Firebase except live event photos.** Roughly 90 headshots and dozens of graphs belong in the repo as static files with Firebase holding paths only.

**No video files in the repo.** GitHub Pages is not a video CDN and the repo has size limits.

**Both photo upload paths ship together.** Camera via `capture="environment"` and library via a second input without the capture attribute. Camera-only was a real limitation on the prior build.

**No fixed-height inner scroll containers outside Display Mode.** Hard pixel heights left dead background filling the bottom of tall phone screens. Let content flow with the page. Viewport-locked heights are for Display Mode only.

**Every local storage key carries the `mm26_` prefix.** Unprefixed keys collide with other CGP walls in the same browser.

**Test on a physical phone.** Desktop responsive mode does not catch camera behavior, maps handoff, tappable phone numbers, or font loading.

---

## Design tokens

```
--stage    #17161A   page background
--riser    #201E24   cards and panels
--input    #2A272E   form fields, inactive pills
--scarlet  #C8102E   primary accent
--oxblood  #8A0E1F   pressed and hover, deep borders
--gold     #D9A94C   awards, trophies, poster moments
--cream    #F7F3EA   body text
--dim      #A39B92   secondary text, metadata
--mute     #6E6862   timestamps, fine print
--edge     #332F38   borders and dividers
--danger   #FF6B4A   destructive admin actions
--glow     rgba(200,16,46,0.12)
```

**Type:** Anton for display, all caps. Inter for body and UI. Alfa Slab One for awards and Encore cards only, used sparingly. Everywhere it reads as a novelty font. On an award card it reads as a trophy plate.

**Motifs:** ticket stub cards, guitar pick badges, amp grille texture, stage light glow, marquee strip, vinyl label, setlist strike-through.

---

## The ten tabs

Themed names only. No plain-English subtitles.

| Tab | Function | Phase |
|---|---|---|
| The Setlist | Agenda with live session tracking | Pre |
| The Band | Attendee roster and directory | Pre |
| Backstage Pass | Venues, travel, logistics, contacts | Pre |
| Soundcheck | Q&A with upvoting and Display Mode | Pre |
| The Vault | Resources, including two timed drops | Pre and During |
| Liner Notes | Key takeaways board | Pre and During |
| Crowd Vote | Live polls, four types | During |
| The Pit | Photo gallery with likes | During |
| The Cares Cup | Shank Showdown II leaderboard | During |
| Encore | Awards, Hall of Fame, Top Videos, Tenure | Post |

---

## The timed drop system

The highest risk feature in the build. Two Vault sections unlock on a clock.

- Core Fundamental Scenarios: Wednesday August 26, 9:30 AM Eastern
- Membership Funnel Personas: Thursday August 27, 10:30 AM Eastern

Requirements:
- Compute the device clock offset against a Firebase server timestamp on load. Do not trust the device clock outright. Attendees fly in from multiple time zones.
- Attendees see locked sections greyed with a padlock, the unlock time, and a live countdown. Visible but locked builds anticipation and prevents confusion.
- Admin always sees unlocked content with a padlock badge indicating the room cannot see it yet.
- Admin override works in both directions and syncs through Firebase to every device. If a session runs ahead, unlock early. If it runs behind, re-lock.
- Reachable in two taps from the gear icon, because it gets used under time pressure.

---

## Definition of done for any task

1. Acceptance criteria in `ROADMAP.md` pass.
2. No console errors.
3. Verified at 380px width and at desktop width.
4. Verified on a physical phone if the feature touches camera, maps, phone links, or fonts.
5. Copy passes the voice rules. No em-dashes.
6. Committed with a clear message and pushed. Confirm the commit landed.
7. Task status updated in `ROADMAP.md`.
