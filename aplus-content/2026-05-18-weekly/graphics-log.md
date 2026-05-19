# Graphics Generation Log — May 18, 2026

**Skill:** ai-image-generator (community, jezweb/claude-skills)
**Models:** Gemini 3.1 Flash Image (`gemini-3.1-flash-image-preview`), GPT Image 2 (`gpt-image-2`)
**Batch script:** [graphics/_batch.py](graphics/_batch.py)
**Logo composite script:** [graphics/_composite_logo.py](graphics/_composite_logo.py)
**Raw results:** [graphics/_results.json](graphics/_results.json)

---

## Summary

7 graphics generated this week + 5 logo composites:

| # | Asset | Provider | Size | Quality | Output | Est cost |
|---|---|---|---|---|---|---|
| 1 | Hero (home-office Dashboard review scene) | Gemini 3.1 | 16:9 | preview | [hero.png](graphics/hero.png) | ~$0.035 |
| 2 | Featured social card | GPT Image 2 | 1536×1024 | medium | [social-card-with-logo.png](graphics/social-card-with-logo.png) | ~$0.045 |
| 3 | LinkedIn carousel slide 1 | GPT Image 2 | 1024×1536 | medium | [carousel-slide-1-with-logo.png](graphics/carousel-slide-1-with-logo.png) | ~$0.045 |
| 4 | Main pull-quote (§6 verbatim) | GPT Image 2 | 1024×1024 | medium | [pull-quote-with-logo.png](graphics/pull-quote-with-logo.png) | ~$0.053 |
| 5 | Facebook post image (B2C kitchen) | Gemini 3.1 | 16:9 | preview | [facebook.png](graphics/facebook.png) | ~$0.035 |
| 6 | Inline pull-quote §2 | GPT Image 2 | 1024×1024 | medium | [pull-quote-s2-with-logo.png](graphics/pull-quote-s2-with-logo.png) | ~$0.053 |
| 7 | Inline pull-quote §3 | GPT Image 2 | 1024×1024 | medium | [pull-quote-s3-with-logo.png](graphics/pull-quote-s3-with-logo.png) | ~$0.053 |
| 8 | Inline pull-quote §6 (copy of #4) | n/a | 1024×1024 | n/a | [pull-quote-s6-with-logo.png](graphics/pull-quote-s6-with-logo.png) | $0 (file copy) |
| | | | | | **Total** | **~$0.32** |

---

## v1.1 homeschool spec compliance (visual checks)

| Asset | Setting | Result |
|---|---|---|
| Hero | Home office (bookshelf, family photo, doorway to hallway, plant, "November 2026" wall calendar with "BOARD MTG" annotation) | ✅ Unmistakably home, NOT a school office |
| Social card | Flat design, no human subjects | ✅ N/A |
| Carousel slide 1 | Flat design, no human subjects | ✅ N/A |
| Pull-quotes | Flat design, no human subjects | ✅ N/A |
| Facebook | Kitchen, parent + middle-school child collaborating, golden hour light, refrigerator + cabinets + plants visible | ✅ Unmistakably home, NOT a school setting |

---

## Text-overlay brand checks (rendered text on each design graphic)

| Asset | Text content | Em dashes | AI vocab | Banned | Result |
|---|---|---|---|---|---|
| Social card | "2026 CA Dashboard" / "CSI designations land this fall. Charter LEAs: lock your plan now." | 0 | 0 | 0 | ✅ |
| Carousel slide 1 | "The 2026 California School Dashboard arrives this fall. If you wait for the designation letter to start planning, you are already behind." / "Swipe to see what charter LEAs should do this spring." | 0 | 0 | 0 | ✅ |
| Pull-quote main + §6 | "A charter LEA with documented outcomes already has a CSI plan. They just need to submit it." | 0 | 0 | 0 | ✅ |
| Pull-quote §2 | "A charter executive director cannot look at the 2025 Dashboard alone and conclude the school is safe." | 0 | 0 | 0 | ✅ |
| Pull-quote §3 | "A charter director who waits for the designation letter to begin the procurement process is already a month behind the calendar." | 0 | 0 | 0 | ✅ |

---

## Logo composite verification

The chroma-key + alpha_composite pattern from May 15 was reused. Sampled background colors per image to handle Gemini/GPT Image 2 rendering variance:

| Asset | Sampled bg | Brand-spec bg | Drift |
|---|---|---|---|
| Social card | RGB(14, 47, 76) | #1A3A52 = RGB(26, 58, 82) | Slight darker (acceptable; sampled fill avoids visible patch) |
| Carousel slide 1 | RGB(9, 43, 75) | #1A3A52 | Slight darker |
| Pull-quote main | RGB(242, 71, 18) | #EF5829 = RGB(239, 88, 41) | Slight redder |
| Pull-quote §2 | RGB(241, 67, 8) | #EF5829 | Slight redder |
| Pull-quote §3 | RGB(244, 73, 9) | #EF5829 | Slight redder |

White-recolored logo variant used on all orange backgrounds; two-color variant on the navy backgrounds.

---

## What goes where in this week's distribution

| Asset | Where it goes |
|---|---|
| hero.png | HubSpot blog post featured image |
| social-card-with-logo.png | OG share card for the blog URL |
| carousel-slide-1-with-logo.png | LinkedIn carousel slide 1 (the hook for the company post) |
| pull-quote-with-logo.png | Standalone Instagram + LinkedIn mid-week share |
| pull-quote-s2-with-logo.png | Inline embed in blog body after §2 |
| pull-quote-s3-with-logo.png | Inline embed in blog body after §3 |
| pull-quote-s6-with-logo.png | Inline embed in blog body after §6 |
| facebook.png | Facebook post image (parent-facing) |
