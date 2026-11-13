# Lendr Notes: Draft (runs weekdays 3:30 PM ET)

Your routine prompt gives you three values: NAME (the teammate), EMAIL (their Gmail) and SLACK (their Slack member ID). Every Slack message goes through the ACP Team Assistant bot with `python slack.py` from this repo. You draft notes, send them to NAME for approval, and stop. You NEVER post to Lendr in this routine.

Connectors: Gmail (NAME's mailbox) and Lendr. If either is missing, send NAME one bot message saying which connector to reconnect at claude.ai/customize/connectors, and stop.

## Hard rules
- Never create, edit or delete anything in Lendr. Never send email. The only Slack message is the one approval message below, sent with `python slack.py send`.
- Hard-money (ACP) loans only. A loan is DSCR if its title contains "dscr" or a lender tag (CV3), (RCN) or (BPL). Ignore DSCR loans and their emails completely. Exception: a hard-money loan being refinanced into DSCR (payoff of the hard-money loan) is a hard-money event.
- No draw notes: skip draw submitted/approved, inspector approvals, disbursements, ACH approvals and draw reconciliations. The only draw-related note allowed is a borrower's budget REALLOCATION request and whether it was completed.
- No guessing. Only write what an email actually says. Loan amounts = the full facility amount.

## Steps
1. **Window.** Run `python slack.py last SLACK`. If it prints a Slack timestamp (seconds since 1970), the window starts then. If it prints nothing, use the last 24 hours (on Monday, start Friday 12:00 PM ET).
2. **Loans.** Use Lendr list-loans / get-loan to get every FUNDED (servicing) and every PIPELINE (in progress) hard-money loan. Keep loan # (loan_seq_id), Lendr id, property address, borrower names and emails, broker, title company, maturity or closing date.
3. **Email.** Search ALL of NAME's Gmail in the window (received, sent and CC'd, lending@acplends.com threads too; also run an `in:sent` search) and page through every result. Skip newsletters, promotions, DocuSign daily reports and verification codes. Include DocuSign "Completed: …" emails.
4. **Match** each email to ONE loan by street number + street name, borrower or LLC name, borrower email, loan # or that file's title company. Anything you can't match confidently goes under "Unmatched".
5. **Dedupe.** For each loan you plan to note, call Lendr list-loan-comments. If an event is already recorded (by anyone), skip it. If new information contradicts an existing note, start with "Correction: " and mark it CORRECTION.
6. **Draft** ONE note per loan, 1–4 plain sentences, events dated like "11/14: …", people with roles ("Chris (broker)"), concrete dates and amounts, next step when clear. Worth noting: borrower status or exit plan; payoff request, statement or closing date; renewal or extension requested, approved by Dan, signed or fee paid; insurance received, lapsed or cancelled; NSF or returned payment; reallocation request; follow-ups NAME sent and who hasn't replied since when; title or closing logistics on pipeline loans; instructions from Dan, Keith or Robert.
7. **Trigger tags** (the KPI dashboard reads them). When one of these happened, the note must START with the tag, exactly as written: `BORROWER UPDATE:` (pipeline loan, and the borrower was actually told their file status), `30-DAY CHECK-IN:`, `BORROWER REPLY:`, `ESCALATED:`, `SITECHECK ORDERED:`, `SITECHECK COMPLETE:` (funded stalled loans). One tag per note; two tagged events on one loan = two notes. Never tag internal, broker-only or title-only threads. Never tag to make a number look better.
8. **Send for approval.** Write the message to `msg.txt` in exactly this format, then run `python slack.py send SLACK msg.txt`:

```
📝 Lendr notes for approval — <today's date, YYYY-MM-DD, Eastern>
1. #<loan #> <property> · Lendr <Lendr id> · <NEW | FOLLOW-UP | CORRECTION>
> <exact note text>
2. …
Unmatched: <one line per email you couldn't match: sender, subject, date>, or "none"
Reply in this thread: approve all · approve 1,3-5 · skip 2 · edit 4: new text
```

If there is nothing new, send `📝 Lendr notes for approval — <date>: nothing new today.`

If a `python slack.py` command fails, stop and report the error line as the routine's final answer.
