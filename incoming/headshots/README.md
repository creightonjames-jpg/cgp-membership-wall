# Drop headshots here

Save the image file into this folder named after the person, exactly as they
appear on the attendee list:

    Gina Fabrizio.jpg
    Gus Siggins.png

Any of jpg, jpeg, png, heic, jfif, jp2, tif or webp is fine. Any size, any
orientation. Then say the word and they get processed to 400x400, filed into
assets/attendees/, and matched against the roster in one command.

The raw originals in this folder are gitignored on purpose. Only the processed
400x400 versions are committed.

Names that still need a photo are listed in data/roster.json under any record
with an empty "photo".
