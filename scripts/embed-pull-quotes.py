#!/usr/bin/env python3
"""
Embed pull-quote graphics inline in an existing HubSpot blog draft.

Uploads pull-quote images (idempotent), fetches the draft's current postBody,
inserts <figure><img></figure> tags after each paragraph containing the anchor
quote text, then PATCHes the draft.

Never publishes. State stays DRAFT regardless of source state.

Usage:
    python3 scripts/embed-pull-quotes.py \\
        --bundle aplus-content/2026-05-15-weekly/ \\
        --post-id 213128099969
    python3 scripts/embed-pull-quotes.py \\
        --bundle aplus-content/2026-05-15-weekly/ \\
        --post-id 213128099969 --dry-run
"""
import os
import sys
import json
import argparse
import re
from pathlib import Path
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get("HUBSPOT_PRIVATE_APP_TOKEN")
PORTAL_ID = "6312752"
BLOG_ID = "12422338726"
HUBSPOT_BASE = "https://api.hubapi.com"
LOG_PATH = Path(__file__).parent / "hubspot-usage.log"

# Pull-quote map: each entry pairs an anchor substring (in the paragraph that
# contains the quote in the blog prose) with the image file to embed after
# that paragraph. The anchor must be a UNIQUE substring of the target
# paragraph so the matcher lands on the right </p> boundary.
PULL_QUOTES = [
    {
        "anchor": "Withholding is different from elimination",
        "file": "pull-quote-s2-with-logo.png",
        "alt": (
            "Pull quote: Withholding is different from elimination. "
            "Congress appropriated the funds. The dollars exist on paper."
        ),
    },
    {
        "anchor": "The directors who restructured their funding mix this spring",
        "file": "pull-quote-s3-with-logo.png",
        "alt": (
            "Pull quote: The directors who restructured their funding mix "
            "this spring around the formula grants and state-funded layers "
            "will not feel the federal volatility the same way."
        ),
    },
    {
        # The verbatim quote appears mid-sentence in the blog prose so its
        # first letter is lowercase ("outcomes"). The graphic capitalizes it
        # because it stands alone there.
        "anchor": "outcomes track operational design, not which federal grant code",
        "file": "pull-quote-with-logo.png",
        "alt": (
            "Pull quote: Outcomes track operational design, not which federal "
            "grant code paid the bill."
        ),
    },
]


def log(action, status, detail=""):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "status": status,
        "detail": str(detail)[:500],
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")


def auth_headers():
    return {"Authorization": f"Bearer {TOKEN}"}


def check_existing_file(filename):
    """Find existing file by exact filename match in HubSpot Files."""
    r = requests.get(
        f"{HUBSPOT_BASE}/files/v3/files",
        headers=auth_headers(),
        params={"name": filename, "limit": 20},
        timeout=30,
    )
    log("check_existing_file", r.status_code, f"filename={filename}")
    if r.status_code != 200:
        return None
    # The HubSpot Files API returns a list; pick the exact-name match
    for result in r.json().get("results", []):
        if result.get("name") == filename.split(".")[0]:
            return result
        # fallback: check filename field if 'name' doesn't match
    # if no exact match, return first result (best-effort)
    results = r.json().get("results", [])
    return results[0] if results else None


def upload_file(image_path):
    """Upload to HubSpot Files. Idempotent by exact filename."""
    filename = Path(image_path).name
    existing = check_existing_file(filename)
    if existing:
        url = existing.get("url")
        print(f"  Reusing existing: {filename} -> {url}")
        log("upload_skipped", 200, f"existing url={url}")
        return url

    with open(image_path, "rb") as f:
        files = {"file": (filename, f, "image/png")}
        data = {
            "options": json.dumps({"access": "PUBLIC_INDEXABLE"}),
            "folderPath": "/aplus-blog-images",
        }
        r = requests.post(
            f"{HUBSPOT_BASE}/files/v3/files",
            headers=auth_headers(),
            files=files,
            data=data,
            timeout=120,
        )
    log("upload_file", r.status_code, r.text[:400])
    if r.status_code not in (200, 201):
        print(f"  ERROR upload {filename} (HTTP {r.status_code}): {r.text[:400]}", file=sys.stderr)
        return None
    url = r.json().get("url")
    print(f"  Uploaded: {filename} -> {url}")
    return url


def get_post(post_id):
    r = requests.get(
        f"{HUBSPOT_BASE}/cms/v3/blogs/posts/{post_id}",
        headers=auth_headers(),
        timeout=30,
    )
    log("get_post", r.status_code, f"post_id={post_id}")
    if r.status_code != 200:
        print(f"ERROR fetching post {post_id}: HTTP {r.status_code}", file=sys.stderr)
        print(r.text[:1500], file=sys.stderr)
        return None
    return r.json()


def insert_figure_after_paragraph(html, anchor, image_url, alt_text):
    """Find the </p> that closes the paragraph containing `anchor`, then
    insert a <figure> with the image right after it.

    Returns (new_html, success_bool).
    """
    figure_html = (
        '<figure style="margin: 2.5em auto; text-align: center; max-width: 640px;">'
        f'<img src="{image_url}" alt="{alt_text}" '
        'style="max-width: 100%; height: auto; display: block; margin: 0 auto;" />'
        "</figure>"
    )

    pos = html.find(anchor)
    if pos == -1:
        return html, False
    end_pos = html.find("</p>", pos)
    if end_pos == -1:
        return html, False
    insert_pos = end_pos + len("</p>")
    new_html = html[:insert_pos] + "\n" + figure_html + html[insert_pos:]
    return new_html, True


def patch_post(post_id, post_body):
    """PATCH the post with just the updated postBody. State is not changed."""
    payload = {"postBody": post_body}
    r = requests.patch(
        f"{HUBSPOT_BASE}/cms/v3/blogs/posts/{post_id}",
        headers={**auth_headers(), "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    log("patch_post", r.status_code, f"post_id={post_id}, body_len={len(post_body)}")
    if r.status_code not in (200, 201):
        print(f"ERROR patching post (HTTP {r.status_code}):", file=sys.stderr)
        print(r.text[:1500], file=sys.stderr)
        return False
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Embed pull-quote graphics into an existing HubSpot blog draft"
    )
    parser.add_argument("--bundle", required=True, help="Weekly bundle dir")
    parser.add_argument("--post-id", required=True, help="HubSpot post ID to PATCH")
    parser.add_argument("--dry-run", action="store_true", help="No HubSpot writes")
    args = parser.parse_args()

    if not TOKEN:
        print("ERROR: HUBSPOT_PRIVATE_APP_TOKEN not set", file=sys.stderr)
        return 1

    bundle = Path(args.bundle)
    if not bundle.is_dir():
        print(f"ERROR: bundle dir not found: {bundle}", file=sys.stderr)
        return 1

    # Verify the pull-quote image files exist locally
    for pq in PULL_QUOTES:
        p = bundle / "graphics" / pq["file"]
        if not p.exists():
            print(f"ERROR: missing pull-quote image: {p}", file=sys.stderr)
            return 1
    print("Pull-quote source files present.")

    # Phase 1: fetch the existing draft so we know its current postBody
    print(f"\nFetching post {args.post_id}...")
    post = get_post(args.post_id)
    if not post:
        return 1
    current_body = post.get("postBody", "")
    current_state = post.get("state", "?")
    print(f"  State: {current_state}")
    print(f"  postBody length: {len(current_body):,} chars")

    # Phase 2: upload images (idempotent) or get existing URLs
    print("\nUploading / locating pull-quote images...")
    if args.dry_run:
        print("  DRY RUN — skipping uploads. Using placeholder URLs.")
        image_urls = {pq["file"]: f"https://example.com/{pq['file']}" for pq in PULL_QUOTES}
    else:
        image_urls = {}
        for pq in PULL_QUOTES:
            local_path = bundle / "graphics" / pq["file"]
            url = upload_file(local_path)
            if not url:
                print(f"ERROR: upload returned no URL for {pq['file']}", file=sys.stderr)
                return 1
            image_urls[pq["file"]] = url

    # Phase 3: insert figure tags into the current postBody
    print("\nInserting <figure> tags...")
    new_body = current_body
    inserted = []
    for pq in PULL_QUOTES:
        url = image_urls[pq["file"]]
        new_body, ok = insert_figure_after_paragraph(new_body, pq["anchor"], url, pq["alt"])
        if ok:
            print(f"  ✓ inserted after anchor: '{pq['anchor'][:60]}...'")
            inserted.append(pq["file"])
        else:
            print(f"  ✗ NOT FOUND anchor: '{pq['anchor'][:60]}...'", file=sys.stderr)

    if len(inserted) != len(PULL_QUOTES):
        print(f"\nERROR: expected {len(PULL_QUOTES)} insertions, got {len(inserted)}", file=sys.stderr)
        print("Aborting before PATCH to avoid a partial state.", file=sys.stderr)
        return 1

    print(f"\nNew postBody length: {len(new_body):,} chars (was {len(current_body):,}, delta +{len(new_body) - len(current_body):,})")

    # Phase 4: PATCH
    if args.dry_run:
        print("\nDRY RUN — skipping PATCH. Would send PATCH /cms/v3/blogs/posts/{post_id}")
        return 0

    print(f"\nPATCHing post {args.post_id}...")
    if not patch_post(args.post_id, new_body):
        return 1

    edit_url = f"https://app.hubspot.com/blog/{PORTAL_ID}/edit/{args.post_id}"
    print(f"\nDraft updated. Edit URL: {edit_url}")
    log("embed_complete", 200, f"post_id={args.post_id}, inserted={len(inserted)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
