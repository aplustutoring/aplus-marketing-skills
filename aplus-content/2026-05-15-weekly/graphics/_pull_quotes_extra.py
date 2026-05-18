#!/usr/bin/env python3
"""Generate 2 additional pull-quote graphics matching the style of the
existing pull-quote.png. Run once. Output: pull-quote-s2.png, pull-quote-s3.png.
"""
import json, base64, urllib.request, urllib.error, os, sys, time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path="/Users/romanslavinsky/Desktop/aplus-marketing-skills/.env")
OPENAI = os.environ.get("OPENAI_API_KEY")
OUT = Path("/Users/romanslavinsky/Desktop/aplus-marketing-skills/aplus-content/2026-05-15-weekly/graphics")


def gpt_image_2(name, prompt, out_file):
    url = "https://api.openai.com/v1/images/generations"
    body = json.dumps({
        "model": "gpt-image-2",
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024",
        "quality": "medium",
    }).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI}",
    })
    start = time.time()
    try:
        resp = urllib.request.urlopen(req, timeout=240)
        result = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"{name} FAIL HTTP {e.code}: {e.read().decode()[:400]}")
        return False
    except Exception as e:
        print(f"{name} FAIL {type(e).__name__}: {e}")
        return False
    item = result.get("data", [{}])[0]
    img = base64.b64decode(item["b64_json"])
    (OUT / out_file).write_bytes(img)
    usage = result.get("usage", {})
    print(f"{name}: {out_file} ({len(img):,} bytes, {time.time()-start:.1f}s) usage={usage}")
    return True


# Quote A — for §2 "What does the federal grant withholding actually mean"
prompt_s2 = """A square social media pull quote graphic. Solid background color A+
Orange hex #EF5829. Subtle paper-grain texture at about 5 percent opacity.
Large white Inter Bold sans-serif text, centered vertically, reading exactly:
"Withholding is different from elimination. Congress appropriated the funds.
The dollars exist on paper." Below the quote, in smaller white Inter Regular
text at about 70 percent opacity, centered: "A+ Tutoring blog · May 20, 2026".
A small white A+ Tutoring wordmark in the bottom-right corner. Generous
whitespace. No additional decorative elements. No em dashes. Aspect 1:1
square."""

# Quote B — for §3 "Why this matters for charter directors"
prompt_s3 = """A square social media pull quote graphic. Solid background color A+
Orange hex #EF5829. Subtle paper-grain texture at about 5 percent opacity.
Large white Inter Bold sans-serif text, centered vertically, reading exactly:
"The directors who restructured their funding mix this spring around the
formula grants and state-funded layers will not feel the federal volatility
the same way." Below the quote, in smaller white Inter Regular text at
about 70 percent opacity, centered: "A+ Tutoring blog · May 20, 2026". A
small white A+ Tutoring wordmark in the bottom-right corner. Generous
whitespace. No additional decorative elements. No em dashes. Aspect 1:1
square."""

print("Generating pull-quote-s2.png...")
gpt_image_2("s2", prompt_s2, "pull-quote-s2.png")
print("Generating pull-quote-s3.png...")
gpt_image_2("s3", prompt_s3, "pull-quote-s3.png")
print("Done.")
