---
name: aplus-brand-check
description: Quality assurance layer for all A+ Tutoring content before it hits the approval queue or publishes. Catches banned words, AI fingerprints (em dashes, "leverage/delve/harness"), voice violations, brand inconsistencies, missing voice differentiation between paired Roman/Danielle op-eds, and profanity. Use as the final step in any content generation workflow before content is reviewed by Danielle or published.
---

# A+ Brand Check Agent

## Purpose

Run automated QA on every piece of A+ content before it reaches the human approval gate. Catch failures the writer agents miss. This is the last line of defense before content goes to Danielle for review.

If brand-check fails a piece of content, the content is sent back to the writer agent for revision before reaching Danielle. Danielle should never see content that fails brand-check.

## When to apply

Run brand-check on EVERY piece of generated content before:
- Adding to the approval queue for Danielle
- Publishing to LinkedIn, Facebook, Instagram, or website
- Sharing as Roman or Danielle's personal commentary
- Sending to an external recipient (school admin, charter director, parent)

Apply specifically to:
- Company LinkedIn posts (A+ Tutoring page)
- Roman voice op-eds
- Danielle voice op-eds
- Facebook posts (B2C)
- Instagram captions and stories
- Blog posts
- Case study drafts
- Email outreach to schools
- Any AI-generated text content

## Failure categories

Content fails brand-check if ANY of the following are present.

### Critical failures (auto-reject, return to writer)

1. **Em dashes** (.). Any em dash anywhere. Replace with periods, colons, or rephrase.

2. **Banned phrase: "all students."** This phrase is explicitly forbidden across all A+ content. It is bland, performative, and signals corporate fake-care.

3. **AI-detection vocabulary** (any of these words):
   - leverage / leveraging / leveraged
   - delve / delving / delved
   - harness / harnessing / harnessed
   - foster / fostering / fostered (when used in the corporate-virtue sense)
   - fundamentally
   - streamline / streamlining / streamlined
   - utilize / utilizing / utilized (use "use")
   - facilitate / facilitating / facilitated (use "help" or "make easier")
   - elevate / elevating / elevated (when used as corporate fluff)
   - revolutionize / revolutionizing / revolutionized
   - empower / empowering / empowered (when used as corporate fluff)
   - unlock / unlocking / unlocked (when paired with "potential")

4. **Profanity.** Any profanity in published content. Roman uses it in conversation; it never appears in social posts. Hard rule.

5. **Generic LinkedIn corporate fluff:**
   - "Game-changer"
   - "Best-in-class"
   - "Industry-leading"
   - "Cutting-edge"
   - "Synergy"
   - "Stakeholder ecosystem"
   - "Transform / transformation" (when used as corporate buzzword)
   - "Move the needle" used by anyone other than Danielle's voice (it's her phrase)

6. **Rule-of-three lists.** Three short parallel phrases in a row are an AI fingerprint (e.g., "faster, better, stronger" or "we listen, we adapt, we deliver"). If a rule-of-three appears, restructure.

### Voice-specific failures

When the content is tagged as Roman voice OR Danielle voice, additional checks apply.

#### Roman voice failures
- Uses any of Danielle's signature phrases: "the funding is already there," "passed along year after year," "listening to understand, not to respond," "real classroom experience," "roundtable approach"
- Opens with a story or scene (Roman opens with claims, not stories)
- Closes on "this is who I'm writing for" (that's Danielle's close)
- Sounds preachy or moralistic (Roman is combative, not preachy)
- Sounds like a victim of the system (Roman is a builder pushing through it)
- Generic founder-bro energy ("When I started this company...", "After years of building...")
- Lists virtues of A+ (Roman doesn't list what A+ does well . he says what's wrong with everyone else)

#### Danielle voice failures
- Uses any of Roman's signature phrases: "schools are misrun, not underfunded," "broken system," "the kids who need it most are the ones who get failed first," "stop pretending"
- Combative or attacking tone (that's Roman's lane, not hers)
- Hard sell language: "Don't miss out," "Limited spots," "Act now," "Schedule today"
- Pitchy closings or CTAs (Danielle closes on human observations, not asks)
- Repeats credentials in every post (Master's, K-8 credential should land once, then move to the work)
- Strips specific data (her drafts should include specific numbers when discussing programs: 32 students, 81%, 78 points, 21 students, etc.)

### Differentiation failures (when Roman + Danielle op-eds are paired)

When a company post has BOTH a Roman op-ed AND a Danielle op-ed in the same package, run paired-differentiation check:

1. **Same opening claim or framing?** Fail.
2. **Same closing line or parallel sentence structure in close?** Fail.
3. **Both could be re-attributed to the other voice without anyone noticing?** Fail.
4. **Both lead with the same evidence or data point?** Fail.
5. **Both use the same metaphor, analogy, or anchor concept?** Fail.

If any paired-differentiation failure occurs, send BOTH drafts back with instructions on which one needs to change. Default to changing the one that drifted from its lane.

### Brand kit failures

When content is for a specific channel, check brand-kit alignment.

#### B2C content (Facebook, Instagram, parent emails)
- Uses educator jargon (LTEL, MTSS, Title III, reclassification) inappropriately for parent audience
- Doesn't address parents directly ("your child," "your family")
- Tone is institutional/cold rather than warm

#### B2B content (LinkedIn, case studies, school-facing)
- Uses parent-relatable framing where it should be educator-peer voice
- Lacks data or specifics where they're available
- Treats school admins as prospects rather than colleagues
- Doesn't acknowledge system-level constraints schools operate within

### Image / visual failures (when content includes visuals)

- Stock photos that obviously look like stock photos
- Chalkboards (cliché tutoring imagery)
- Pencil/apple emoji clichés
- Comic Sans or decorative fonts
- More than 3 brand colors in one composition
- Wrong color lead for audience (orange-led for B2B is wrong; navy-led for B2C is wrong)
- Missing logo on materials that require it (case studies, pitch decks, hero LinkedIn graphics)

## Output format

Brand-check produces one of three outputs:

### PASS

```
✅ BRAND CHECK PASSED

Content: [first 50 chars of content]
Channel: [LinkedIn company / Roman LI / Danielle LI / Facebook / Instagram / etc.]
Voice: [N/A / Roman / Danielle / Paola / Company]
Word count: [N]
Reading time: [X seconds]

Ready for approval queue.
```

### FAIL . single issue

```
❌ BRAND CHECK FAILED

Content: [first 50 chars]
Channel: [...]
Voice: [...]

Issue: [Critical / Voice-specific / Differentiation / Brand kit / Visual]
Specific failure: [Exact rule violated]
Location in content: [quote the offending text]
Recommended fix: [How to fix it]

Returning to writer for revision.
```

### FAIL . multiple issues

```
❌ BRAND CHECK FAILED . MULTIPLE ISSUES

Content: [first 50 chars]
Channel: [...]
Voice: [...]

Issues found:
1. [Category]: [Failure] . [Quote] . [Fix]
2. [Category]: [Failure] . [Quote] . [Fix]
3. ...

Returning to writer for revision. Address all issues before resubmitting.
```

## Severity-based handling

Not all failures are equal:

- **Critical (em dashes, banned words, profanity)** → auto-reject, return to writer
- **Voice failures** → return to writer with specific fix
- **Differentiation failures** → flag both drafts, recommend which to change
- **Brand kit failures** → return to writer with channel-specific guidance
- **Visual failures** → flag for human visual reviewer (graphics often need human eye)

## What brand-check does NOT do

- Does NOT make creative judgments about whether a take is good
- Does NOT decide whether a topic is worth posting (that's `aplus-research`)
- Does NOT replace Danielle's final approval gate
- Does NOT catch factual errors (that's a different layer)
- Does NOT handle tone calibration (e.g., "this is too negative for the moment") . that's human judgment

The agent is a rule-checker, not a judgment layer. Pass everything that doesn't violate explicit rules; let humans handle taste and timing.

## Iteration protocol

If the same writer agent fails brand-check 3 times in a row on similar issues, log the pattern. The relevant SKILL.md (roman-voice, danielle-voice, etc.) likely needs updating to prevent the recurring failure rather than catching it post-hoc each time.

## Coordination with other skills

- Receives content from: company post writer, `roman-voice`, `danielle-voice`, `aplus-case-study`, any blog/email writer
- Sends approved content to: human approval queue (Slack channel for Danielle)
- Sends failed content to: original writer agent for revision
- Reads rules from: every voice and brand kit SKILL.md (rules are sourced from those files; this skill is the enforcement layer)

## Frequency

- Runs on EVERY piece of generated content
- Should be a mandatory step in every content generation workflow
- Cannot be skipped . bypassing brand-check is the failure mode that erodes brand consistency over time

## Related skills

- `roman-voice` . source of Roman-specific rules
- `danielle-voice` . source of Danielle-specific rules
- `aplus-b2c-brand-kit` . source of B2C visual and tone rules
- `aplus-b2b-brand-kit` . source of B2B visual and tone rules
- `aplus-research` . research output also runs through brand-check before becoming writing input
- `aplus-case-study` . case study drafts run through brand-check before review

## Version

v1.0 . Created May 8, 2026
Foundation: Banned words list, AI fingerprint patterns, and voice rules from roman-voice v1.1 and danielle-voice v1.1
