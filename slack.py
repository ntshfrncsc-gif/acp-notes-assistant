"""slack.py: the ACP Team Assistant bot's Slack helper for the Lendr note-taker routines.

Runs inside a Claude cloud routine. It never holds the bot token: the "ACP Notes" cloud
environment stores the token as a network secret for slack.com, and the environment's
proxy adds the Authorization header to every request to slack.com on its way out.
(For a local test, set SLACK_BOT_TOKEN and the script sends the header itself.)

    python slack.py send <SLACK_USER_ID> <message.txt>           -> prints the message ts
    python slack.py last <SLACK_USER_ID>                         -> ts of the latest approval message, or ""
    python slack.py approvals <SLACK_USER_ID> [--days 7]         -> JSON: approval messages + their thread replies
    python slack.py reply <SLACK_USER_ID> <thread_ts> <reply.txt> -> posts a reply in that thread

Only the bot's own DM with that person is ever read or written.
"""
import json, os, sys, time, urllib.error, urllib.parse, urllib.request

API = "https://slack.com/api/"
HEADER = "📝 Lendr notes for approval"


def call(method, params, post=False):
    headers = {"Content-Type": "application/json; charset=utf-8"} if post else {}
    if os.environ.get("SLACK_BOT_TOKEN"):                       # local testing only
        headers["Authorization"] = "Bearer " + os.environ["SLACK_BOT_TOKEN"]
    if post:
        req = urllib.request.Request(API + method, data=json.dumps(params).encode(), headers=headers)
    else:
        req = urllib.request.Request(API + method + "?" + urllib.parse.urlencode(params), headers=headers)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 3:
                time.sleep(int(e.headers.get("Retry-After", "3")))
                continue
            raise SystemExit(f"Slack {method}: HTTP {e.code} (is slack.com allowed in the cloud environment?)")
        except urllib.error.URLError as e:
            raise SystemExit(f"Slack {method}: can't reach slack.com ({e.reason}). "
                             "Check that the routine uses the ACP Notes environment.")
        if data.get("ok"):
            return data
        err = data.get("error")
        if err in ("not_authed", "invalid_auth"):
            raise SystemExit(f"Slack {method}: {err}: the bot token isn't attached. "
                             "Check the ACP Notes environment's slack.com secret.")
        raise SystemExit(f"Slack {method}: {err}")
    raise SystemExit(f"Slack {method}: rate limited")


def dm(user):
    return call("conversations.open", {"users": user}, post=True)["channel"]["id"]


def history(channel, oldest):
    msgs, cursor = [], None
    while True:
        p = {"channel": channel, "oldest": oldest, "limit": 200}
        if cursor:
            p["cursor"] = cursor
        r = call("conversations.history", p)
        msgs += r.get("messages", [])
        cursor = (r.get("response_metadata") or {}).get("next_cursor")
        if not cursor:
            return sorted(msgs, key=lambda m: float(m["ts"]))


def replies(channel, ts):
    out, cursor = [], None
    while True:
        p = {"channel": channel, "ts": ts, "limit": 200}
        if cursor:
            p["cursor"] = cursor
        r = call("conversations.replies", p)
        out += [m for m in r.get("messages", []) if m["ts"] != ts]
        cursor = (r.get("response_metadata") or {}).get("next_cursor")
        if not cursor:
            return out


def approval_msgs(channel, days):
    oldest = f"{time.time() - days * 86400:.6f}"
    return [m for m in history(channel, oldest)
            if m.get("bot_id") and (m.get("text") or "").startswith(HEADER)]


def chunks(text, size=3800):
    """Split long messages on line breaks so Slack never truncates a note."""
    out, buf = [], ""
    for line in text.splitlines(keepends=True):
        if buf and len(buf) + len(line) > size:
            out.append(buf)
            buf = ""
        buf += line
    return out + ([buf] if buf else [])


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    cmd, user = sys.argv[1], sys.argv[2].strip().upper()
    channel = dm(user)
    if cmd == "send":
        text = open(sys.argv[3], encoding="utf-8").read().strip()
        parts = chunks(text)
        first = call("chat.postMessage", {"channel": channel, "text": parts[0], "unfurl_links": False}, post=True)["ts"]
        for extra in parts[1:]:                                  # overflow goes in the same thread
            call("chat.postMessage", {"channel": channel, "thread_ts": first, "text": extra,
                                      "unfurl_links": False}, post=True)
        print(first)
    elif cmd == "last":
        msgs = approval_msgs(channel, 14)
        print(msgs[-1]["ts"] if msgs else "")
    elif cmd == "approvals":
        days = int(sys.argv[sys.argv.index("--days") + 1]) if "--days" in sys.argv else 7
        out = []
        for m in approval_msgs(channel, days):
            out.append({"ts": m["ts"], "text": m.get("text", ""),
                        "replies": [{"ts": r["ts"], "from": "bot" if r.get("bot_id") else
                                     ("teammate" if r.get("user") == user else "other"),
                                     "text": r.get("text", "")} for r in replies(channel, m["ts"])]})
        print(json.dumps(out, indent=1, ensure_ascii=False))
    elif cmd == "reply":
        text = open(sys.argv[4], encoding="utf-8").read().strip()
        call("chat.postMessage", {"channel": channel, "thread_ts": sys.argv[3], "text": text,
                                  "unfurl_links": False}, post=True)
        print("ok")
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
