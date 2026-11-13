# ACP Lendr Notes Assistant

Instructions and the Slack helper used by each ACP teammate's two Lendr note-taker routines (Claude cloud scheduled tasks). Change a rule here once and every teammate's next run uses it.

- `DRAFT.md`: weekday afternoon routine that drafts notes from the teammate's Gmail and sends them for approval.
- `POST.md`: hourly routine that posts approved notes to Lendr.
- `slack.py`: talks to Slack as the **ACP Team Assistant** bot. It holds no token: the "ACP Notes" cloud environment adds it for slack.com requests.
- `slack_app_manifest.yaml`: settings used to create the ACP Team Assistant Slack app.

Setup for teammates: the "Lendr Note Taker Setup" page in the ACP Lendr Note Taker project on claude.ai.
