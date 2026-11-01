# TutorMate iOS: ranking in the App Store and in AI models

**Date:** 2026-11-01
**Supersedes nothing.** This extends `aso-audit-2026-10-19.md`; that document's rubric scoring and ready-to-paste copy still stand.
**Why it exists:** the prior audit scored the listing. It did not cover how the app gets recommended by language models, which is a different mechanism with different inputs.

---

## Part 1: What changed since 2026-10-19

| Item | Then | Now |
|---|---|---|
| Version | 1.1, awaiting review | **1.2 live** since 2026-10-21 |
| Minimum iOS | **26.2** (blocked nearly every device) | **17.0**, 130 supported devices |
| Title | TutorMate: AI Study Quiz Maker | TutorMate: AI Homework Helper (29/30) |
| Subtitle | Scan Homework, Check Answers | Snap worksheets, get quizzes (28/30) |
| Ratings | 5.0 from 6 | 5.0 from 7 |
| Release notes | "Bug fixes and performance improvements" | Written in product voice, names the iOS 17 fix |
| Smart App Banner | Missing | **Added 2026-11-01** (`4a78dc9`) |

**The single biggest win already landed.** The iOS 26.2 deployment target was excluding almost every device from installing. That is fixed and live. Every ranking lever below only matters because that gate is now open.

Two prior findings are now resolved: the generic release notes, and the Smart App Banner.

### Still outstanding from the prior audit, unchanged

1. **The 6.9" screenshots were never uploaded.** All 8 frames exist at the correct 1320×2868 in `TutorMate-ios/AppStoreScreenshots/ProductPage-v3/6.9in/`, generated 2026-10-20. I inspected them: strong contrast, readable captions, and they fix all three issues the audit raised (slot 1 is now a worksheet-to-quiz split, slot 3 is new social proof, slot 8 closes on "Start Free"). They are good. They are not live. This is the highest-value unshipped asset you have.
2. **Keyword field** needs rebuilding against the new title and subtitle. The audit's v2 field collides with "worksheets" and "Helper". Corrected field is in that document.
3. **Title still leads with the brand** (criterion 1.3, 5 points). `TutorMate: AI H` spends Apple's most heavily weighted 15 characters on a term with no search volume at 7 ratings.
4. **Brand dispute** on the lookalike "TutorMate AI" listing (id 6788593253).
5. **No localizations**, **no iPad set**, **no developer responses** to the reviews.
6. **Seller name** still reads DUSTIN MICHAEL WALKER.

One minor new note: screenshot slot 3 has a large empty band between the headline and the 5.0 figure. It reads as unfinished at full size. Worth tightening before upload, though not worth delaying the upload over.

---

## Part 2: Getting returned in AI model results

This is a different problem from ASO, and the 155-point rubric does not measure any part of it.

### The mechanism, stated plainly

**Language models do not browse the App Store.** They do not have a ranking algorithm you can optimize against, and they cannot see your keyword field, your screenshots, or your conversion rate. When someone asks an assistant "what's a good app to check my kid's homework?", the answer is assembled from two sources:

1. **What the model absorbed during training**, which is overwhelmingly the open web: listicles, forum threads, review sites, news coverage, YouTube transcripts, Wikipedia.
2. **What a live retrieval step surfaces**, if the assistant has search. That is ordinary web search, which again favors the open web over store listings.

The practical consequence is counterintuitive: **almost nothing you do in App Store Connect affects whether an AI recommends your app.** Your listing is a conversion surface for people who already found you. It is close to invisible as a citation source.

So the work splits cleanly:

- **App Store ranking** is won in App Store Connect: metadata, assets, ratings, conversion.
- **AI recommendation** is won on the open web: your own site, and third-party corroboration.

### Where TutorMate actually stands

Bluntly: a model asked for homework-app recommendations today has no reason to name TutorMate, and one strong reason not to.

**The reason not to** is the entity collision documented in the SEO audit. "TutorMate" is a long-running volunteer literacy program run by the nonprofit Chapter One, with coverage from Stanford, University of Houston, the National Literacy Trust and Kaiser Permanente. That is a dense, well-corroborated cluster of training data. Your app, launched August 2026 with 7 ratings, has essentially none. Asked "what is TutorMate?", the model answers confidently and wrongly, and the wrong answer is not even an app.

**The reason to have no opinion** is simple absence. No Wikidata item. No AlternativeTo entry. No Product Hunt launch. No G2 or Capterra listing. No YouTube presence. No Reddit footprint. You are not in any of the corpora that "best homework apps" answers are assembled from.

### What actually moves this, in order

**1. Create the Wikidata item.** Highest leverage, roughly an hour, no code.

Wikidata is disproportionately influential in how models resolve entities, and it is the only place you can make a machine-readable claim that your app is *different from* the literacy program. Create "TutorMate (software)" with `instance of: mobile app`, `developer: Walker Intelligence Group`, `official website: https://tutormate.ai`, `operating system: iOS`, and critically a `different from` statement pointing at the Chapter One program.

Without this, every other effort fights the collision. With it, you have an anchor that disambiguation can hang from.

**2. Get into the comparison corpora.** This is where "alternatives to X" answers come from.

- **AlternativeTo**, filed specifically against Photomath, Socratic, Gauth and Chegg
- **Product Hunt** launch
- **G2** and **Capterra** under education software
- **App listicle outreach**: the "best homework apps for students" roundups that get scraped into training data

You cannot be the answer to "Photomath alternatives" if you are absent from every list of Photomath alternatives. This is unglamorous directory work and it is the single most mechanical path to being cited.

**3. Put the demo video on YouTube with a transcript.** YouTube presence correlates strongly with AI citation, and your clearest product explanation is currently a self-hosted MP4 that no retrieval system can read. Upload it, write a real description, and put the transcript on `/homework-help/`. The transcript is the part that matters: it converts your best explanation into indexable text.

**4. Earn genuine third-party writeups.** Teacher blogs, parenting sites, education newsletters, study-skills YouTubers. One substantive independent review is worth more to a model than ten self-published pages, because corroboration across independent sources is exactly what distinguishes a real entity from a marketing claim.

**5. Keep the website as the canonical answer.** Already done as of 2026-11-01. `tutormate.ai` now carries `SoftwareApplication` schema with the App Store `installUrl`, plain-prose pricing, a disambiguation statement, and `llms.txt`. When a model does retrieve your site, it now gets correct, structured, quotable answers. That was not true two days ago.

### What does not work, and is worth not wasting effort on

- **Stuffing the App Store description with AI-friendly phrasing.** Models are not reading it.
- **"llms.txt for your app."** There is no such surface. The store listing is Apple's.
- **Asking an assistant whether it recommends you, then treating the answer as a metric.** Responses vary per session and per user, and a model that says "yes" once has told you nothing measurable.
- **Paying for AI-visibility services** that promise placement in model answers. No such placement exists to sell.

### Honest expectations

Training data moves slowly. Even if you did every item above this week, the models that have already been trained will not know about it. You are influencing the *next* training runs and today's retrieval step, in that order. Retrieval responds in weeks; training recall responds in quarters or longer.

The realistic sequence is: fix the entity (Wikidata), get into the directories, earn a few independent writeups, and let retrieval start finding you. Expect the collision to persist in model recall for a long time regardless, which is why pairing the name with the category ("TutorMate, the AI homework checker") in every off-site bio matters more than it looks.

---

## Part 3: Priority order, both tracks combined

Ranked for installs, not for rubric score.

| # | Action | Track | Effort | Why here |
|---|---|---|---|---|
| 1 | Upload the 6.9" screenshots | ASO | Low (assets exist) | Done work sitting unshipped. Conversion on all traffic. |
| 2 | Rebuild the keyword field | ASO | Low | Free, same day, no release needed. Currently collides with the new title. |
| 3 | Create the Wikidata item | AI | Low | Unblocks every other AI effort. |
| 4 | Reply to all 7 reviews | ASO | Low | Public, permanent, 15 minutes. |
| 5 | AlternativeTo, Product Hunt, G2, Capterra | AI | Medium | The comparison corpora. |
| 6 | Brand dispute on the lookalike listing | ASO | Low | Stops brand-search leakage. |
| 7 | In-app review prompt (ships in 1.3) | Both | Done, uncommitted | 7 ratings caps criteria 3.4 and 3.5 permanently. |
| 8 | YouTube + transcript | AI | Medium | Converts your best asset into indexable text. |
| 9 | Title test: lead with the category | ASO | Low | Recovers criterion 1.3. Validate with PPO. |
| 10 | Localizations | ASO | Medium | Cheapest keyword surface Apple offers. |
| 11 | Preview video | ASO | High | 20 rubric points, uncertain install impact. The prior audit's caution still applies: do it after traffic exists. |
| 12 | Icon redesign | ASO | High | Slowest payback. Needs PPO to validate. |

**The through-line:** items 1, 2, 4 and 6 are all low-effort work that is either already done or needs no release. Those should ship this week. Item 3 is an hour that unblocks an entire track. Everything expensive sits below everything cheap, deliberately.
