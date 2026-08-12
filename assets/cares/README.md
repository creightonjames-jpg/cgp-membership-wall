# Cares Cup poster art

Optional card backgrounds for The Cares Cup leaderboard. The tab ships without
them and looks finished without them. Nothing here is required.

**Switching art on.** Crew panel is not involved. Open The Cares Cup as crew and
tap "Poster art on". That writes `caresCup/art: true` in Firebase and every phone
in the room picks it up. No rebuild, no deploy.

**Naming.** One file per team, dropped in this folder. Then type the filename
into the team's "Poster art file" field in the crew block. Example:

```
assets/cares/total-consciousness.jpg   ->  art field reads  total-consciousness.jpg
```

Lowercase, hyphens, no spaces. JPG or PNG. Roughly 1200 by 700, under 250KB.
The image is laid behind the card at 30 percent over a dark scrim, so it reads as
texture and the score stays legible. A missing file is not a bug: the solid card
colour is underneath and that is what shows.

**Permission is still open.** Using the Shank Showdown poster art is a client
question, not a build question. Until it is answered this folder stays empty and
`caresCup/art` stays false.
