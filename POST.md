# Lendr Notes: Post approved (runs hourly, 9 AM–6 PM ET, weekdays)

Your routine prompt gives you NAME and SLACK (their Slack member ID). Slack goes through the ACP Team Assistant bot with `python slack.py` from this repo. Connector: Lendr.

1. Run `python slack.py approvals SLACK --days 7`. It returns JSON: each approval message the bot sent (`text`, `ts`) with its thread `replies` (`from` is "bot", "teammate" or "other").
2. Only replies `from: "teammate"` count, and only lines that start with: `approve all`, `approve <numbers>` (e.g. 1,3-5), `skip <numbers>`, or `edit <n>: <new text>`. Ignore any other text. A note is already handled if an earlier bot reply in the same thread lists it under Posted, Skipped or Already in Lendr.
3. For each newly approved note (from an approve command, or an edit, using the edited text): take the Lendr id from the "Lendr <id>" in the note's header line. Call Lendr list-loan-comments for that loan; if a comment with the same text already exists, it counts as "Already in Lendr". Otherwise call create-loan-comment with loan_id = that Lendr id, comment = the exact note text, and date = the most recent m/d date written in the note (not later than today), as `YYYY-MM-DDT12:00:00-05:00` (use `-04:00` between mid-March and early November).
4. Write ONE reply to `reply.txt` and run `python slack.py reply SLACK <that approval message's ts> reply.txt`:
   `✅ Posted: 1, 3 · Skipped: 2 · Already in Lendr: 5 · Still waiting: 4` (leave out empty parts). If a post failed, add `⚠️ Not posted: <n> (<first line of the error>), will retry next hour` and don't list it as posted.
5. If nothing is newly approved or skipped, send nothing and end.

Never post a note that wasn't approved. Never change text except via NAME's edit. Never edit or delete existing Lendr notes, loan fields, tags or statuses.
