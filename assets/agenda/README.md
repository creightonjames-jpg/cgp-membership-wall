# Agenda artwork

Images that belong to a single session on The Setlist, referenced from
`data/agenda.json` as `graphic` on that session.

## Waiting on

- `shank-showdown.png` — the Shank Showdown II tournament graphic, for the 12:00
  Tuesday session. Until it lands, the card shows a labelled place marker. When it
  arrives, put it here and set `graphic.pending` to `false` on
  `tue-shank-showdown`. Nothing else needs changing.

## Sizes

Run it through the pipeline rather than dropping a raw export in:

    bash tools/process-assets.sh resources <folder>

Max 1600px wide, under 600KB. A tournament graphic is usually flat colour and
type, so if it comes out heavy, quantize it to a 256 colour palette rather than
saving it as JPEG. That is what the Core Fundamentals wheel needed: 1.7MB to
252KB with the text still sharp.
