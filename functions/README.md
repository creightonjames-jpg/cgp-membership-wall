# Email alerts

Fires an email to Jim, Lisa, and Carol every time a new question lands on
Soundcheck or a new takeaway lands on Liner Notes. ROADMAP: email alerts,
Aug 19 2026.

This is the first server side piece the wall has ever needed. Everything else
is a static file plus a wide open Firebase database, on purpose. An alert that
has to fire even when nobody has the wall open cannot be a browser tab, since a
closed tab runs nothing. That is the whole reason `functions/` exists.

Sends through Gmail SMTP, signed in as Jim's own Gmail account
(`creightonjames@gmail.com`), not through a transactional email API. Resend was
tried first and the code path still resembles it, but Resend's default sender
only delivers to the account that signed up for it. Proven live: a test
question fired the function correctly and Resend rejected the send the moment
the recipient was anyone else, with "You can only send testing emails to your
own email address." Fixing that means verifying a domain, which needs DNS
access on centurygolf.com, which Jim does not have. Gmail SMTP with an app
password sends to anyone today, no DNS, no domain, no IT ticket.

## What you need to do, once

Two things now, since Blaze is already on. Only you can do these, an app
password is tied to your own Google account.

**1. Turn on 2-Step Verification, if it is not already on.**
https://myaccount.google.com/security. Google requires this before it will
issue an app password at all.

**2. Generate an app password.**
https://myaccount.google.com/apppasswords. Name it something like "CGP Wall
Alerts," it shows you a 16 character password once. Hand it to me, or set it
yourself:

```bash
firebase functions:secrets:set GMAIL_APP_PASSWORD
```

It will prompt you to paste it. It never gets written to a file, never gets
committed, and never appears in this repo. Firebase stores it in Secret
Manager and hands it to the function only at run time.

## Deploying

Once the secret is set:

```bash
cd functions && npm install && cd ..
firebase deploy --only functions
```

Editing `functions/index.js` and running the same deploy command updates it in
place, usually under a minute.

## Changing who gets the alert

Edit the `RECIPIENTS` array at the top of `functions/index.js`, then redeploy
with the command above. No secret to touch for this, just the list of
addresses.

## Changing which account sends it

Edit `SENDER` at the top of `functions/index.js` to the new address, generate
a fresh app password for that account, set it as `GMAIL_APP_PASSWORD` (this
replaces the old one, there is only ever one version in use), and redeploy.

## What it does not do

- The email arrives from Jim's own Gmail, not a `@centurygolf.com` address.
  Some inboxes may flag a first message from a personal Gmail sending
  automated mail, though a plain Gmail to Gmail or Gmail to Outlook send
  usually lands fine. If it lands in spam the first time, marking it "not
  spam" once should fix that inbox for the rest of the week.
- No retry, no queue, no dashboard. If Gmail's SMTP is unreachable for the
  exact second a question is posted, that one alert is lost. Given the volume
  and the stakes, that is an acceptable trade for keeping this small enough to
  trust.
- No alert for anything except new questions and new takeaways. Edits, votes,
  and pins do not fire anything.
- The old `RESEND_API_KEY` secret still exists in Secret Manager, unused. It
  costs nothing sitting there and nothing in this repo reads it anymore. Fine
  to leave, fine to delete with `firebase functions:secrets:destroy
  RESEND_API_KEY` if it bothers anyone.
