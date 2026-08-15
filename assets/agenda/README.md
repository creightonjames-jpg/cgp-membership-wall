# Agenda artwork

Images that belong to a single session on The Setlist, referenced from
`data/agenda.json` as `graphic` on that session.

## In place

- `shank-showdown.jpg`, the Shank Showdown II matchup poster, on the 12:00 Tuesday
  session. Team Total Consciousness against Spalding's Revenge Team.

## How a graphic gets added

Set `graphic` on the session in `data/agenda.json`:

```json
"graphic": {
  "file": "assets/agenda/whatever.jpg",
  "alt": "What is in the picture, for anyone who cannot see it.",
  "pending": false
}
```

`pending: true` renders a labelled place marker instead, for when the artwork is
promised but has not arrived. Set it to `false` once the file is really there.

**Never point `file` at a file that does not exist yet.** It 404s in every
attendee's console, and a lazily loaded 404 fires no error event, so the page
cannot even detect it. That is what `pending` is for.

## Sizes

Max 1600px wide, under 600KB.

Pick the format for the artwork, not by habit:

- **Photographic or painted**, like the Shank Showdown poster: JPEG. It came in at
  1572px and 3.8MB as a PNG and went to 510KB at quality 86, with the poster type
  still sharp. Palette quantization was tried and rejected, it bands badly across a
  painted sky and still weighed 1MB.
- **Flat colour and type**, like the Core Fundamentals wheel: PNG quantized to a
  256 colour palette. That took it from 1.7MB to 252KB with the text crisper than
  JPEG would leave it.
