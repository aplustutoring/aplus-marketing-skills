#!/usr/bin/env python3
"""
A+ Tutoring weekly bundle Slack delivery.

Posts a header message + four copy-paste-ready derivative messages (each with
its attached image) to a Slack channel. Delivery only. Never publishes anything
to LinkedIn, Facebook, or any other external platform — Danielle / Roman
copy-paste each block manually.

Usage:
    python3 scripts/deliver-to-slack.py --bundle aplus-content/2026-05-15-weekly/
    python3 scripts/deliver-to-slack.py --bundle aplus-content/2026-05-15-weekly/ --post-id 213128099969
    python3 scripts/deliver-to-slack.py --bundle aplus-content/2026-05-15-weekly/ --dry-run
"""
import os
import sys
import json
import argparse
import re
import shutil
import tempfile
from pathlib import Path
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

SLACK_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
HUBSPOT_TOKEN = os.environ.get("HUBSPOT_PRIVATE_APP_TOKEN")
CHANNEL = "#weekly-content-ready"
PORTAL_ID = "6312752"
MAX_IMAGE_BYTES = 5_000_000
LOG_PATH = Path(__file__).parent / "slack-usage.log"

# Map each derivative to its body file + image file + destination platform hint
PIECES = [
    {
        "name": "LinkedIn company post",
        "body_file": "linkedin-company.md",
        "image_file": "graphics/carousel-slide-1-with-logo.png",
        "destination": "linkedin.com/company/aplus-tutoring",
        "publish_window": "Wednesday PM",
    },
    {
        "name": "Roman op-ed",
        "body_file": "roman-oped.md",
        "image_file": "graphics/pull-quote-with-logo.png",
        "destination": "linkedin.com/in/romanslavinsky",
        "publish_window": "Thursday AM",
    },
    {
        "name": "Danielle op-ed",
        "body_file": "danielle-oped.md",
        "image_file": "graphics/pull-quote-s3-with-logo.png",
        "destination": "Danielle's personal LinkedIn",
        "publish_window": "Friday AM",
    },
    {
        "name": "Facebook post (B2C, parents)",
        "body_file": "facebook.md",
        "image_file": "graphics/facebook.png",
        "destination": "facebook.com/aplustutoring",
        "publish_window": "Friday PM",
    },
]


# ---------- Logging ----------

def log(action, status, detail=""):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "status": str(status),
        "detail": str(detail)[:500],
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")


# ---------- Token guidance ----------

SLACK_SETUP_INSTRUCTIONS = """
SLACK_BOT_TOKEN is not set in .env.

To create one (~5 minutes):

1. Open https://api.slack.com/apps and click "Create New App" -> "From scratch".
2. App name: "A+ Tutoring Content Bot" (or anything you like).
   Workspace: pick atutoringworkspace.
3. From the left sidebar, click "OAuth & Permissions".
4. Under "Bot Token Scopes", add:
   - chat:write          (post messages as the bot)
   - files:write         (upload images)
   - chat:write.public   (post to channels the bot has not been invited to)
5. Scroll to the top of the same page and click "Install to Workspace".
   Approve the consent screen.
6. Copy the "Bot User OAuth Token" (starts with xoxb-).
7. Add to /Users/romanslavinsky/Desktop/aplus-marketing-skills/.env:
       SLACK_BOT_TOKEN=xoxb-...
8. In Slack, type in any channel:  /invite @AplusTutoringContentBot
   to add the bot to #weekly-content-ready (or whatever channel you target).
9. Re-run this script.
"""


# ---------- Helpers ----------

def extract_body(md_path):
    """Each derivative file has a frontmatter block (H1 + bold metadata),
    then a `---` line, then the body. Return just the body."""
    text = Path(md_path).read_text()
    parts = text.split("\n---\n", 1)
    body = parts[1].strip() if len(parts) == 2 else text.strip()
    return body


def md_to_slack_mrkdwn(md):
    """Convert a small subset of markdown to Slack mrkdwn.

    Slack mrkdwn rules:
    - bold: *text* (single asterisks)
    - italic: _text_ (underscores)
    - link: <url|text>
    - inline code: `text`
    - no headers; just paragraphs
    """
    text = md
    # **bold** -> *bold*  (do this BEFORE handling lone-asterisk italic)
    text = re.sub(r"\*\*([^*]+)\*\*", r"*\1*", text)
    # Markdown links [label](url) -> Slack <url|label>
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"<\2|\1>", text)
    return text


def ensure_under_size(image_path, max_bytes=MAX_IMAGE_BYTES):
    """If the image is over max_bytes, return a downsized temp copy.
    Otherwise return the original path."""
    src = Path(image_path)
    if src.stat().st_size <= max_bytes:
        return str(src)

    from PIL import Image
    img = Image.open(src)
    scale = 0.8
    tmp_path = Path(tempfile.gettempdir()) / f"slack-{src.name}"
    while True:
        new_size = (max(1, int(img.width * scale)), max(1, int(img.height * scale)))
        resized = img.resize(new_size, Image.LANCZOS)
        resized.save(tmp_path, format="PNG", optimize=True)
        if tmp_path.stat().st_size <= max_bytes or scale < 0.15:
            print(f"  Downsized {src.name} from {src.stat().st_size:,} to "
                  f"{tmp_path.stat().st_size:,} bytes ({new_size[0]}x{new_size[1]})")
            return str(tmp_path)
        scale *= 0.8


def extract_date(bundle_path):
    """Pull YYYY-MM-DD from the bundle directory name."""
    m = re.search(r"(\d{4}-\d{2}-\d{2})", str(bundle_path))
    if not m:
        return None
    iso = m.group(1)
    try:
        d = datetime.strptime(iso, "%Y-%m-%d")
        return d.strftime("%B %-d, %Y")  # e.g. "May 15, 2026"
    except ValueError:
        return iso


# ---------- Slack API ----------

def slack_call(method, endpoint, **kwargs):
    """Wrapper around requests for slack.com/api with logging.

    Adds Authorization header automatically. Returns parsed JSON response.
    Raises on non-2xx HTTP OR ok:false Slack error.
    """
    url = f"https://slack.com/api/{endpoint}"
    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {SLACK_TOKEN}"
    r = requests.request(method, url, headers=headers, timeout=60, **kwargs)
    try:
        body = r.json()
    except ValueError:
        body = {"raw_text": r.text}
    log(endpoint, r.status_code, body.get("error", "ok") if isinstance(body, dict) else "non-json")
    if r.status_code >= 400 or (isinstance(body, dict) and body.get("ok") is False):
        print(f"\nERROR Slack {endpoint} -> HTTP {r.status_code}: {body}", file=sys.stderr)
        raise RuntimeError(f"Slack API call failed: {endpoint}")
    return body


def auth_test():
    return slack_call("POST", "auth.test")


def post_message(channel, text, blocks=None, thread_ts=None):
    payload = {"channel": channel, "text": text}
    if blocks:
        payload["blocks"] = blocks
    if thread_ts:
        payload["thread_ts"] = thread_ts
    return slack_call("POST", "chat.postMessage", json=payload,
                      headers={"Content-Type": "application/json; charset=utf-8"})


def upload_image_with_text(channel, image_path, initial_comment, thread_ts=None):
    """Upload an image via the modern files API (getUploadURLExternal +
    completeUploadExternal). Posts the file to the channel with
    initial_comment carrying the body text.
    """
    image_path = ensure_under_size(image_path)
    filename = Path(image_path).name
    file_size = Path(image_path).stat().st_size

    # Step 1: get upload URL
    step1 = slack_call(
        "GET",
        "files.getUploadURLExternal",
        params={"filename": filename, "length": file_size},
    )
    upload_url = step1["upload_url"]
    file_id = step1["file_id"]

    # Step 2: POST the file bytes to that upload URL (no auth header here;
    # the URL is pre-signed)
    with open(image_path, "rb") as f:
        r = requests.post(upload_url, files={"file": (filename, f)}, timeout=120)
    log("upload_bytes", r.status_code, filename)
    if r.status_code != 200:
        raise RuntimeError(f"Upload bytes failed: HTTP {r.status_code} {r.text[:300]}")

    # Step 3: complete the upload, sharing to the channel with initial_comment
    complete_payload = {
        "files": json.dumps([{"id": file_id, "title": filename}]),
        "channel_id": channel,
        "initial_comment": initial_comment,
    }
    if thread_ts:
        complete_payload["thread_ts"] = thread_ts
    return slack_call("POST", "files.completeUploadExternal", data=complete_payload)


def resolve_channel_id(channel_name):
    """Resolve a channel name or ID to a channel_id usable by the files API.

    Accepts:
    - A bare channel ID (e.g., 'C0B4K9K0162' or 'G0...') — returned as-is
    - A channel name (e.g., '#weekly-content-ready' or 'weekly-content-ready') —
      looked up via conversations.list, then verified via chat.postMessage
      probe if list lookup returns nothing (Slack cache lag fallback).
    """
    # Detect channel ID form: starts with C, G, or D and is 9-11 chars all-caps
    if re.fullmatch(r"[CGD][A-Z0-9]{8,10}", channel_name):
        return channel_name

    name = channel_name.lstrip("#")
    cursor = None
    while True:
        params = {"limit": 200, "exclude_archived": True,
                  "types": "public_channel,private_channel"}
        if cursor:
            params["cursor"] = cursor
        body = slack_call("GET", "conversations.list", params=params)
        for ch in body.get("channels", []):
            if ch.get("name") == name:
                return ch["id"]
        cursor = body.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break

    # Fallback: probe via chat.postMessage. Slack accepts the channel name
    # directly. The response includes the channel_id even if conversations.list
    # didn't return it yet due to cache lag.
    probe = slack_call(
        "POST",
        "chat.postMessage",
        json={"channel": f"#{name}", "text": ":mag: aplus bot lookup probe (auto-deletes if possible)"},
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    channel_id = probe.get("channel")
    if channel_id:
        # Try to clean up the probe message immediately
        ts = probe.get("ts")
        if ts:
            try:
                slack_call("POST", "chat.delete",
                           json={"channel": channel_id, "ts": ts},
                           headers={"Content-Type": "application/json; charset=utf-8"})
            except Exception:
                pass  # delete is best-effort; the probe message is harmless
        return channel_id

    raise RuntimeError(f"Channel {channel_name} not found by the bot. "
                       f"Make sure the bot is invited to that channel.")


# ---------- Main ----------

def main():
    parser = argparse.ArgumentParser(
        description="Deliver an A+ weekly bundle to a Slack channel for review and copy-paste."
    )
    parser.add_argument("--bundle", required=True, help="Weekly bundle directory")
    parser.add_argument("--post-id", help="HubSpot post_id (e.g. 213128099969) for the draft link in the header. Optional.")
    parser.add_argument("--channel", default=CHANNEL, help=f"Slack channel name (default: {CHANNEL})")
    parser.add_argument("--dry-run", action="store_true", help="Validate inputs and preview body text without calling Slack")
    args = parser.parse_args()

    bundle = Path(args.bundle)
    if not bundle.is_dir():
        print(f"ERROR: bundle dir not found: {bundle}", file=sys.stderr)
        return 1

    # Verify all derivative files and images exist
    missing = []
    for p in PIECES:
        if not (bundle / p["body_file"]).exists():
            missing.append(bundle / p["body_file"])
        if not (bundle / p["image_file"]).exists():
            missing.append(bundle / p["image_file"])
    if missing:
        print("ERROR: missing files:", file=sys.stderr)
        for m in missing:
            print(f"  - {m}", file=sys.stderr)
        return 1

    # Token check
    if not SLACK_TOKEN:
        if args.dry_run:
            print("NOTE: SLACK_BOT_TOKEN not set, dry-run continues anyway.")
        else:
            print(SLACK_SETUP_INSTRUCTIONS, file=sys.stderr)
            return 1

    date_str = extract_date(bundle) or "?"
    print(f"=== Bundle: {bundle} ({date_str}) ===")

    # Build the header text + blocks
    header_lines = [f":package: *Weekly content bundle ready  -  {date_str}*"]
    if args.post_id:
        url = f"https://app.hubspot.com/blog/{PORTAL_ID}/edit/{args.post_id}"
        header_lines.append(f":memo: HubSpot blog draft: <{url}|Review and publish>")
    else:
        header_lines.append(":memo: HubSpot blog draft: (no --post-id provided)")
    header_lines.append("")
    header_lines.append(f":pushpin: {len(PIECES)} social derivatives below. Copy each block, paste into the destination platform.")
    header_text = "\n".join(header_lines)

    # Preview each derivative
    print("\n=== Derivatives ===")
    for p in PIECES:
        body = md_to_slack_mrkdwn(extract_body(bundle / p["body_file"]))
        img = bundle / p["image_file"]
        print(f"- {p['name']}  ({len(body)} chars,  {img.stat().st_size:,} bytes,  -> {p['destination']})")

    if args.dry_run:
        print("\n=== DRY RUN  -  no Slack calls ===")
        print("\nHeader preview:")
        print(header_text)
        print("\nFirst derivative preview (LinkedIn company post):")
        print("-" * 60)
        body0 = md_to_slack_mrkdwn(extract_body(bundle / PIECES[0]["body_file"]))
        print(f":clipboard: *Copy this  ->  {PIECES[0]['name']}*  _({PIECES[0]['publish_window']})_")
        print(f"_Paste to: `{PIECES[0]['destination']}`_")
        print()
        print(body0[:400] + ("..." if len(body0) > 400 else ""))
        print("-" * 60)
        return 0

    # Auth check
    print("\nVerifying Slack token...")
    me = auth_test()
    print(f"  Authed as bot: {me.get('user')} in workspace: {me.get('team')}")

    # Resolve channel ID once (files API needs the ID, not the name)
    print(f"Resolving channel {args.channel}...")
    channel_id = resolve_channel_id(args.channel)
    print(f"  Channel ID: {channel_id}")

    # Post header
    print("\nPosting header message...")
    header_blocks = [
        {"type": "section", "text": {"type": "mrkdwn", "text": header_text}},
        {"type": "divider"},
    ]
    header_resp = post_message(channel_id, header_text, blocks=header_blocks)
    header_ts = header_resp.get("ts")
    print(f"  Header ts: {header_ts}")

    # Post each derivative as a thread reply: image + initial_comment
    for p in PIECES:
        print(f"\nDelivering: {p['name']}")
        body = md_to_slack_mrkdwn(extract_body(bundle / p["body_file"]))
        img = bundle / p["image_file"]

        # Compose the initial_comment that accompanies the uploaded image
        comment_lines = [
            f":clipboard: *Copy this  ->  {p['name']}*  _({p['publish_window']})_",
            f"_Paste to: `{p['destination']}`_",
            "",
            body,
        ]
        comment = "\n".join(comment_lines)

        upload_image_with_text(channel_id, str(img), comment, thread_ts=header_ts)
        print(f"  Posted: {img.name} + {len(body)} chars of body")

    print("\nDone. Open the channel in Slack to review.")
    log("delivery_complete", "ok", f"channel={args.channel} bundle={bundle}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
