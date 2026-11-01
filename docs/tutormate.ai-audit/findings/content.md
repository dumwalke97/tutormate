# Content Quality Findings — tutormate.ai

Audit date: 2026-11-01
Analyst: content-quality specialist (Google QRG, current version September 11, 2025)
Source reviewed: local files `www/index.html`, `www/privacy/index.html` (read directly, no fetch)

## Scores

| Metric | Score |
|---|---|
| Content quality (0-100) | **31** |
| E-E-A-T composite | **16 / 100** |
| AI citation readiness | **18 / 100** |
| Readability | Pass (approx. grade 7-8, appropriate for audience) |
| Metadata templating risk | Low (`site_risk: low`, `templated_ratio: 0.0`) |

### E-E-A-T breakdown

| Factor | Weight | Score | Basis |
|---|---|---|---|
| Experience | 20% | 15 | Demo video is the only first-hand artifact. No worked examples, no sample outputs in text, no case studies, no screenshots of real feedback, no teacher/parent/student stories. |
| Expertise | 25% | 10 | No named author, no educator or subject-matter credential anywhere on the site. No explanation of pedagogy or how correctness is verified. |
| Authoritativeness | 25% | 8 | No company or person entity, no About page, no external citations, no press, reviews, ratings, school adoption, or outbound references. Only third-party signal is the App Store link. |
| Trustworthiness | 30% | 25 | Positives: real privacy policy with named subprocessors (Firebase, Gemini, Apple, Netlify), working support email, data-deletion path, children's-privacy section, HTTPS. Negatives: no legal entity named, no Terms of Service, no refund/cancellation policy on the marketing page, no contact route from the landing page, unsubstantiated trust claim. |

Weighted: (0.20x15) + (0.25x10) + (0.25x8) + (0.30x25) = **15.6 → 16**.
*Weights are this skill's internal model, not Google's. Google publishes no numeric E-E-A-T weights; it states only that trust matters most.*

---

## HIGH severity

### H1. Site-wide thin content: two pages, 271 indexable words of marketing copy
The landing page body text is **271 words** including nav, buttons, and footer. Stripped of
chrome and CTAs, substantive prose is roughly **190 words**. The homepage floor for topical
coverage is 500; a page serving simultaneously as homepage, product page, pricing page, and the
only commercial landing page needs materially more. The privacy policy (535 words) is the longest
document on the domain, which means the most substantive page on the site is the one page nobody
searches for.

The whole domain is 2 indexable URLs (plus `/app/`, an app shell titled "Tutor Mate" that is
neither noindexed nor useful as a landing page). There is no content surface for any query other
than the brand name. Expect near-zero non-brand organic traffic regardless of technical SEO work.

*Word count is not a direct ranking factor; the problem here is absence of topical coverage, not length.*

### H2. Zero keyword or entity coverage for how the audience actually searches
The landing page never contains: homework, homework help, math, algebra, geometry, calculus,
chemistry, biology, physics, history, Spanish, essay, step-by-step, solution, solver, scan,
flashcards, practice test, study guide, AI tutor, tutoring, grade, middle school, high school,
college, free. "Quiz" appears 4 times; "study" 4 times.

The product's own primary job to be done (photograph homework, get it checked, see the reasoning)
is described only in the brand's internal vocabulary ("check your work", "study partner", "answer
machine"). No subject entity, no grade-level entity, and no competitor-comparison surface exists,
so the site cannot rank for or be cited on any of the queries that drive this category.

### H3. "Trusted by parents" is an unsubstantiated trust claim
The H2 "Made for students. Trusted by parents." and the closing "which is why students *and*
parents feel good about it" assert third-party endorsement with nothing behind it: no parent
testimonial, no review count, no App Store rating, no named reviewer, no number. Under the QRG
this is the archetype of a reputation claim a rater cannot verify, and it sits on the page with
the weakest trust footprint on the site. Either substantiate it (quoted parent reviews with first
name and grade level, App Store star rating and review count, a stated number of families) or
rewrite it as a product claim about design intent ("Built so parents can see the reasoning, not
just the answer").

### H4. No entity: no About page, no company, no named human
There is no legal entity, founder, team, mailing address, or author anywhere on the marketing
page. "© 2026 TutorMate" is the entire corporate disclosure. For a paid subscription product
handling minors' uploaded schoolwork, this is the single largest trust gap, and it also blocks
`Organization` entity recognition and any knowledge-panel or AI-answer attribution.

### H5. No FAQ or question-shaped content: AI citation readiness 18/100
No page contains a question heading, a definition sentence, a comparison table, a bulleted spec
list, or any structured data (no JSON-LD at all; no `SoftwareApplication`, `Offer`, `FAQPage`, or
`Organization`). The only extractable facts on the whole site are the two prices, and even those
appear as visual price cards (`$4.95` + `/mo` in separate elements) rather than as quotable
sentences. An LLM asked "how much does TutorMate cost", "is TutorMate free", "does TutorMate work
on Android", or "TutorMate vs Photomath" has nothing on the domain to cite.

---

## MEDIUM severity

### M1. Heading structure is shallow and carries no topical signal
Current outline:

- H1 "Check your work. Study smarter." — brandless, keywordless, and does not name the product or category
- H2 "How it works" → H3 "1. Snap a photo" / H3 "2. Get feedback or a quiz" / H3 "3. Save your progress"
- H2 "Made for students. Trusted by parents."
- H2 "Simple pricing"

The hierarchy is valid (no skipped levels) but three of four H2s are generic labels reused across
millions of SaaS pages. The H1 does not contain "TutorMate" or any category term. Recommended H1:
"TutorMate: AI homework help that checks your work and explains the reasoning". Headings should be
restated as the questions users ask ("How does TutorMate check my homework?", "What subjects does
TutorMate cover?", "How much does TutorMate cost?").

### M2. Generic, specificity-free copy reads as low-effort AI/boilerplate output
Per the QRG's low-quality-AI markers, the page shows generic phrasing with no concrete detail:
"clear, helpful feedback", "any topic", "in seconds", "actually understand the material", "a study
partner, not a shortcut". Nowhere does the page state which subjects are supported, which grade
levels, whether handwriting is read, how many questions a quiz contains, what happens when the
photo is unclear, what the free tier includes, or what model powers it (the privacy policy
discloses Gemini; the marketing page does not). One real worked example (a photographed algebra
problem with TutorMate's actual feedback shown as text) would do more for E-E-A-T than any copy
rewrite.

### M3. "Start free" / "No credit card needed" is undefined
Two CTAs promise a free start with no stated limit (number of free checks or quizzes, duration,
feature caps). Vague free-tier claims are both a conversion leak and a trust/transparency flag,
and they are also the exact fact AI assistants are asked for ("is TutorMate free?").

### M4. Cross-platform availability is ambiguous
"Same price whether you're on the web or on iOS" implies iOS-only native support, but Android is
never mentioned and the web app's device support is never stated. Queries like "is TutorMate on
Android" have no answer on the domain.

### M5. No freshness or update signals on the commercial page
The landing page carries no dated content, no changelog, no "last updated", and no publication
date. The only date on the domain is the privacy policy's effective date (July 7, 2026) and the
footer copyright. With no blog or release notes, the site emits zero recency signal.

### M6. Missing legal/support surface expected of a paid subscription
No Terms of Service, no refund or cancellation policy page, no contact page, no support page. The
cancellation path exists only inside the privacy policy's deletion section. Support email appears
only on the privacy page, not in the landing-page footer.

---

## LOW severity

- **L1. Title tag wastes its most valuable slot.** "TutorMate: Check Your Work. Study Smarter." (42 chars) spends none of its remaining ~18 characters on a category term. Suggested: "TutorMate: AI Homework Help & Quiz Maker for Students".
- **L2. Meta description is good but non-templated and under-length** (138 chars, passes the templating heuristic cleanly: no title echo, no brand suffix, no stock CTA). Could add the price or the free start.
- **L3. One over-long sentence.** The students/parents paragraph contains a 44-word sentence; otherwise readability is appropriate for a student/parent audience.
- **L4. Branding inconsistency.** `/app/index.html` is titled "Tutor Mate" (two words) against "TutorMate" everywhere else, and that page is indexable with no description.
- **L5. Video has no transcript or captions.** `TutorMateDemo.mp4` carries the clearest product explanation on the site and none of it is machine-readable text. A transcript below the player converts the demo into indexable, citable content.
- **L6. Privacy policy is genuinely strong** and is the site's best trust asset: named subprocessors, explicit "we do not sell", AI-processing disclosure, deletion path, children's-privacy section. Worth linking from the landing page body, not just the footer.

---

## Pages worth creating, with target queries

Priority order. Each is a distinct content surface the site does not currently have.

| Priority | Page | Min words | Primary target queries |
|---|---|---|---|
| 1 | `/about` | 500-600 | tutormate.ai, who makes TutorMate, is TutorMate legit, is TutorMate safe for kids |
| 2 | Expand homepage to 700-900 words + FAQ block | 700+ | AI homework help, homework checker app, app that checks your homework, AI study app |
| 3 | `/homework-help` (service page) | 800+ | ai homework helper, check my homework, homework help app, scan homework get answers explained, step by step homework help |
| 4 | `/quiz-generator` (service page) | 800+ | ai quiz generator from notes, make a practice quiz from my notes, practice test generator, ai flashcard/quiz maker for studying |
| 5 | `/pricing` (own URL, out of the homepage anchor) | 500+ | TutorMate price, TutorMate cost, is TutorMate free, TutorMate subscription, TutorMate cancel |
| 6 | `/vs/photomath`, `/vs/gauth`, `/vs/socratic`, `/vs/chegg`, `/vs/quizlet` | 800+ each | photomath alternative, gauth vs photomath, free alternative to chegg, socratic app replacement, quizlet alternative for practice quizzes (see `seo-competitor-pages` for comparison-page standards) |
| 7 | Subject hubs: `/math`, `/algebra`, `/geometry`, `/chemistry`, `/biology`, `/spanish` | 600-800 each | algebra homework help, geometry homework checker, chemistry practice quiz generator, biology practice test maker (if generated at scale, defer to `seo-programmatic`) |
| 8 | `/for-parents` | 600+ | is AI homework help cheating, homework app that doesn't just give answers, best study app for my teenager, parental controls study app |
| 9 | `/terms` and `/support` (or `/contact`) | n/a | trust/compliance, not search |
| 10 | `/blog` with 1,500+ word posts | 1,500 each | how to study for a test, is using AI for homework cheating, how to make a practice quiz from class notes, best way to check math homework |

### Structured data to add (feeds both rich results and AI citation)
`Organization` (with founder/legal name once H4 is fixed), `SoftwareApplication` with `offers`
(both price points, `priceCurrency: USD`), `FAQPage` on the homepage and each service page, and
`BreadcrumbList` once the site has depth. Also add `robots.txt` and `sitemap.xml` (neither exists
in `www/`) and noindex `/app/`.

### Quotable facts to write as plain sentences (currently absent)
"TutorMate costs $4.95 per month or $49 per year." / "TutorMate is available as a web app and on
iOS." / "TutorMate uses Google's Gemini API to check work and generate quizzes." / "TutorMate
shows the reasoning behind each correction rather than only the final answer." / A stated free-tier
limit. Each of these is a sentence an AI assistant can lift verbatim; today none exists on the site.
