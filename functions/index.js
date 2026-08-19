/**
 * Email alerts for the Live Wall. ROADMAP: email alerts, Aug 19 2026.
 *
 * Two triggers, both the same shape: something new lands in Firebase, this
 * fires on Google's servers (not in anybody's browser, so it works even if
 * nobody has the wall open), and an email goes out through Gmail's SMTP,
 * signed in as Jim's own Gmail account.
 *
 * This is the first server side piece the wall has ever needed. Everything
 * else in this repo is a static file plus a wide open Firebase database, on
 * purpose, per CLAUDE.md's data split. An email that fires with nobody
 * watching a screen cannot be client side JavaScript, since a browser tab
 * that is not open cannot run anything. That is the one job this file exists
 * to do, and nothing else lives here.
 *
 * Gmail SMTP, not a transactional email API, and this was a real course
 * correction, not the first plan. Resend was tried first and it works, but
 * its default sender only delivers to the account that signed up for it,
 * proven live: a test question fired the function correctly and Resend
 * rejected it with "You can only send testing emails to your own email
 * address" the moment the recipient was anyone else. Fixing that properly
 * means verifying a domain, which means DNS access on centurygolf.com, which
 * Jim does not have and could not get before the meeting. Gmail SMTP with an
 * app password sends to anyone today, no DNS, no domain, no IT ticket.
 *
 * v1 functions on purpose, not v2. A v2 Realtime Database trigger has to be
 * deployed to the same region as the database instance, which means knowing
 * that region ahead of time or a deploy that fails opaquely. v1 attaches to
 * the project's default database with no region to get wrong. This project
 * has one function, running a handful of times a day, at the very most,
 * during one week in August. Simple and correct beats fashionable here.
 *
 * Deploy: firebase deploy --only functions
 * Needs the GMAIL_APP_PASSWORD secret set first: see functions/README.md.
 */

const functions = require("firebase-functions/v1");
const nodemailer = require("nodemailer");

const RECIPIENTS = [
  "jcreighton@centurygolf.com",
  "lhenrichsen@balconescountryclub.com",
  "cruskowski@centurygolf.com",
  "ddarville@centurygolf.com"
];

/* The Gmail account sending the mail. An app password is scoped to this one
 * account, so the sender and the secret are a pair: change one and the other
 * has to follow, which is why they are named together here rather than in
 * two unrelated corners of the file. */
const SENDER = "creightonjames@gmail.com";

function transport(appPassword) {
  return nodemailer.createTransport({
    service: "gmail",
    auth: { user: SENDER, pass: appPassword }
  });
}

async function sendMail(appPassword, subject, html) {
  await transport(appPassword).sendMail({
    from: "CGP Live Wall <" + SENDER + ">",
    to: RECIPIENTS,
    subject: subject,
    html: html
  });
}

/* Plain text into safe HTML. The wall itself never runs user text through
 * innerHTML either, same reasoning applies here: this is an email client
 * rendering someone else's typed words. */
function esc(s) {
  return String(s == null ? "" : s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

/* Who posted it, in the same words the wall itself would show. Nothing extra
 * to decide here: an anonymous question already has an empty name and club
 * in the record by the time it reaches Firebase (the submit form blanks both
 * before writing, index.html scWhere/scWho do the same thing on display), so
 * reading the fields straight through cannot leak an identity the wall
 * itself would have hidden. */
function whoLine(name, club, anonymous) {
  if (anonymous) return "Anonymous";
  const n = name && name.trim() ? name.trim() : "Someone";
  const c = club && club.trim() ? club.trim() : "";
  return c ? n + " (" + c + ")" : n;
}

exports.onNewQuestion = functions
  .runWith({ secrets: ["GMAIL_APP_PASSWORD"] })
  .database.ref("/questions/{id}")
  .onCreate(async (snap) => {
    const q = snap.val() || {};
    const who = whoLine(q.name, q.club, q.anonymous === true);
    const category = q.category ? esc(q.category) : "Other";

    const subject = "New Soundcheck question from " + (q.anonymous ? "Anonymous" : (q.name || "Someone"));
    const html =
      "<p><strong>" + esc(who) + "</strong> asked, category " + category + ":</p>" +
      "<blockquote style=\"margin:0;padding:12px 16px;background:#f4f1ea;" +
      "border-left:3px solid #d9a94c;font-size:16px;line-height:1.5;\">" +
      esc(q.text) + "</blockquote>" +
      "<p style=\"color:#666;font-size:13px;\">Posted on Soundcheck, The Live Wall.</p>";

    await sendMail(process.env.GMAIL_APP_PASSWORD, subject, html);
  });

exports.onNewTakeaway = functions
  .runWith({ secrets: ["GMAIL_APP_PASSWORD"] })
  .database.ref("/takeaways/{id}")
  .onCreate(async (snap) => {
    const t = snap.val() || {};
    const who = whoLine(t.name, t.club, false);

    const subject = "New Liner Notes takeaway from " + (t.name || "Someone");
    const html =
      "<p><strong>" + esc(who) + "</strong> posted a takeaway:</p>" +
      "<blockquote style=\"margin:0;padding:12px 16px;background:#f4f1ea;" +
      "border-left:3px solid #d9a94c;font-size:16px;line-height:1.5;\">" +
      esc(t.text) + "</blockquote>" +
      "<p style=\"color:#666;font-size:13px;\">Posted on Liner Notes, The Live Wall.</p>";

    await sendMail(process.env.GMAIL_APP_PASSWORD, subject, html);
  });
