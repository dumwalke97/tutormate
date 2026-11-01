# GEO / AI Search Readiness Audit: tutormate.ai

Audit date: 2026-11-01
Scope: https://tutormate.ai (marketing landing page), /privacy, /app/
Host: Netlify, publish dir `www/` (see `/Users/dustinwalker/Documents/GitHub/tutormate/netlify.toml`)
Method: raw fetch + render (`render_page.py --mode auto`), robots/llms/sitemap probes, iTunes Lookup API, Wikipedia/Wikidata APIs

---

## GEO Readiness Score: 28 / 100

| Dimension | Weight | Score | Weighted | Notes |
|---|---|---|---|---|
| Citability | 25% | 18 | 4.5 | No self-contained answer blocks, no question headings, no stated facts an LLM can lift |
| Structural Readability | 20% | 35 | 7.0 | Clean semantic H1/H2/H3, but no lists, tables, FAQ, or sitemap |
| Multi-Modal Content | 15% | 20 | 3.0 | One demo video with no transcript, captions, or `VideoObject`; 2 images, thin alt text |
| Authority & Brand Signals | 20% | 12 | 2.4 | No org/author entity, no dates, no citations, no Wikidata, severe name collision |
| Technical Accessibility | 20% | 55 | 11.0 | Server-rendered static HTML (good), but no robots.txt, llms.txt, sitemap, canonical, OG, or schema |
| **Total** | | | **27.9 → 28** | |

### Platform-specific estimates

| Platform | Score | Limiting factor |
|---|---|---|
| Google AI Overviews | 25 | Zero structured data, zero corroborating third-party sources, no FAQ surface to match query intent |
| ChatGPT Search | 22 | Nothing extractable as a direct answer; OAI-SearchBot can crawl but finds no quotable passage |
| Perplexity | 30 | Will cite the App Store listing before the site; site has no comparison or pricing prose to quote |
| Bing Copilot | 28 | Bingbot indexes fine, but no entity grounding and no off-site corroboration |

---

## 1. AI Crawler Access (robots.txt is 404)

**Severity: MEDIUM (not blocking, but uncontrolled and missing opportunity)**

`https://tutormate.ai/robots.txt` returns **HTTP 404** (a real 404, `text/html`, 3968 bytes, not a soft 200). Per RFC 9309, an unavailable robots.txt means **full allow**. So nothing is currently blocked:

| Crawler | What it actually governs | Status | Correct? |
|---|---|---|---|
| **OAI-SearchBot** | ChatGPT Search citation/retrieval | Allowed (default) | Yes, keep allowed |
| **Claude-SearchBot** | Claude search citation/retrieval | Allowed (default) | Yes, keep allowed |
| **PerplexityBot** | Perplexity answer citation | Allowed (default) | Yes, keep allowed |
| **Googlebot** | Google Search + AI Overviews inclusion | Allowed (default) | Yes, keep allowed |
| **Bingbot** | Bing index + Copilot grounding | Allowed (default) | Yes, keep allowed |
| **Applebot** | Siri / Spotlight / Safari discoverability | Allowed (default) | Yes, keep allowed. Matters because the iOS app ships through Apple |
| **GPTBot** | OpenAI *model training* only, not ChatGPT Search | Allowed (default) | Business decision. Its status says nothing about ChatGPT Search citability |
| **ClaudeBot** | Anthropic *model training* only, not Claude search | Allowed (default) | Business decision. Claude-SearchBot is what governs Claude citations |
| **Google-Extended** | Gemini/Vertex training and grounding, plus training of models behind Search gen-AI features. Never affects Google Search or AI Overviews inclusion | Allowed (default) | Recommend keeping allowed: it covers Gemini grounding, and TutorMate itself runs on Gemini |
| **Applebot-Extended** | Apple Intelligence *training* only, never Siri/Spotlight/Safari | Allowed (default) | Business decision, no discoverability impact either way |
| **CCBot** | Common Crawl corpus (feeds many training sets and some retrieval pipelines) | Allowed (default) | Recommend keeping allowed while the brand is unknown |

**Risk of leaving it 404:** no sitemap pointer for any crawler, no explicit signal of intent, and any future accidental host-level block has no counterweight. For a 2-page site competing against entrenched entities, the right posture is explicit full allow.

**Fix (effort: 15 min).** Create `/Users/dustinwalker/Documents/GitHub/tutormate/www/robots.txt`:

```
# tutormate.ai
# AI search and answer engines: explicitly welcome.
User-agent: OAI-SearchBot
Allow: /

User-agent: Claude-SearchBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Applebot
Allow: /

User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

# Training crawlers: allowed while we are building entity recognition.
User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: CCBot
Allow: /

User-agent: *
Allow: /
Disallow: /app/

Sitemap: https://tutormate.ai/sitemap.xml
```

Note the `Disallow: /app/`: `/app/` is the logged-in SPA shell (client-rendered, Tailwind CDN, no meaningful crawlable content). Keeping it out of the index prevents a thin-content page from competing with the landing page. Confirm no public marketing content lives under `/app/` before shipping this line.

---

## 2. llms.txt and RSL 1.0 Licensing

**Severity: MEDIUM**

- `/llms.txt`: **404, missing**
- `/sitemap.xml`: **404, missing**
- RSL 1.0 licensing (`/license.xml`, `rsl` reference in robots.txt): **absent**

llms.txt is not a ranking factor and no major engine commits to honoring it. Its value here is different: it is a single plain-text file that states, in the model's preferred format, exactly what TutorMate is, what it costs, and how it differs from competitors. For a brand with a name collision (see section 4), that disambiguation is worth more than the file's nominal crawler support.

**Fix (effort: 30 min).** Create `/Users/dustinwalker/Documents/GitHub/tutormate/www/llms.txt`:

```markdown
# TutorMate

> TutorMate is an AI study app that checks a student's completed homework and
> explains the reasoning behind each answer, and generates custom practice
> quizzes from a photo of a worksheet or from any typed topic. It is positioned
> as a study partner rather than an answer machine: it tells a student what is
> right, what is wrong, and why, instead of solving problems for them.

Not to be confused with TutorMate by Chapter One (formerly Innovations for
Learning), a separate nonprofit volunteer early-literacy reading program at
tutormate.org. This document describes TutorMate the AI study app at
tutormate.ai, published by Dustin Michael Walker.

## Facts

- Product: TutorMate (web app at tutormate.ai/app, iOS app "TutorMate: AI Homework Helper")
- Publisher: Dustin Michael Walker
- iOS App Store ID: 6793738685, Education category, rated 4+, requires iOS 17 or later
- Price: free to start, Premium is $4.95 per month or $49 per year, same price on web and iOS
- Free tier: first 10 quizzes and assignment checks are free, no credit card required
- Core features: photo-based assignment checking with explanations, custom quiz
  generation from a photo or typed topic, folders that sync across devices
- AI model: Google Gemini API
- Platforms: any modern web browser, plus iOS 17+

## Pages

- [Home](https://tutormate.ai/): what TutorMate does, how it works, pricing
- [Privacy Policy](https://tutormate.ai/privacy): data collection, AI processing, deletion
- [Web app](https://tutormate.ai/app/): the product itself, login required

## How TutorMate differs from similar apps

- Photomath and Gauth and Socratic primarily solve a problem you have not done yet.
  TutorMate primarily grades work you have already done and explains the reasoning.
- Chegg is a subscription homework-answer and expert-help library.
  TutorMate does not host an answer database and does not supply solutions on demand.
- TutorMate generates practice quizzes from the student's own worksheet or notes,
  which problem-solver apps generally do not do.
```

RSL 1.0 is optional and lower priority. If licensing terms matter later, add `License: https://tutormate.ai/license.xml` to robots.txt and publish an RSL document. Not recommended yet: restrictive licensing on an unknown brand reduces the corpus presence you currently need.

---

## 3. Passage-Level Citability

**Severity: HIGH (this is the single biggest gap)**

Trafilatura extracts **961 characters of body text** from the entire homepage. Full extracted content:

> Snap a photo of your assignment and get clear, helpful feedback, or turn any topic into a custom quiz to practice for your next test. TutorMate helps you learn it, not just finish it. / No credit card needed to start. / Upload a picture of your worksheet or assignment, or type in a topic you want to study. / TutorMate checks your answers and explains its reasoning, or builds a custom practice quiz in seconds. / Keep everything organized in folders so you can review and practice again before test day. / TutorMate isn't an answer machine. When you upload an assignment, it checks your work and explains what's right, what's off, and why, so you actually understand the material. When you want to practice, it builds a quiz from your notes or any topic you type in. It's a study partner, not a shortcut, which is why students and parents feel good about it. / Start free. Upgrade any time, on the web or in the app.

**Is any of it quotable as a direct answer? One passage, partly.**

The only genuinely citable block is the "Made for students. Trusted by parents." paragraph (88 words). It is self-contained, it names the subject, it makes a falsifiable claim about behavior, and it survives extraction without surrounding context. An LLM asked "is TutorMate a cheating app?" could quote it. That is the entire citable surface of the site.

Everything else fails:

| Problem | Evidence | Severity |
|---|---|---|
| **Pricing is not in prose** | "$4.95" and "/mo" are separate DOM nodes inside pricing cards. Trafilatura drops them entirely: the extracted text contains no price at all. A model reading the stripped page cannot answer "how much does TutorMate cost?" | HIGH |
| **Free tier is undefined** | Site says "Start free" and "No credit card needed to start" but never states the limit. The App Store listing says "first 10 quizzes and assignment checks are free." The site, which is the canonical source, is vaguer than the store listing | HIGH |
| **No question-shaped headings** | Headings are "How it works", "Made for students. Trusted by parents.", "Simple pricing". None match a query a student or parent types | HIGH |
| **No stated subject in step text** | "Upload a picture of your worksheet" does not name TutorMate, so the passage is not extractable standalone | MEDIUM |
| **No statistics, no sources, no citations** | Zero numbers on the page other than prices and step numbers. Nothing for an engine to attribute | MEDIUM |
| **No comparison content** | Nothing distinguishes TutorMate from Photomath, Gauth, Socratic, or Chegg. A model asked to compare has no material | HIGH |
| **Total body text under 200 words** | Below the practical threshold for being selected as a retrieval passage on any competitive query | HIGH |

**Fix: add self-contained answer blocks.** Each should be 130 to 170 words, lead with a direct answer in the first 40 to 60 words, and name "TutorMate" in the first sentence so the passage stands alone. Exact blocks to add are in section 6.

---

## 4. Entity Clarity

**Severity: CRITICAL**

### 4a. Name collision with an established entity

"TutorMate" is already a recognized entity in training corpora, and it is not this product. **TutorMate is the volunteer early-literacy reading program run by Chapter One (formerly Innovations for Learning)**, a nonprofit founded in 1993. It is referenced on the English Wikipedia article for Innovations for Learning, in a National Literacy Trust pilot evaluation, and in Puget Sound Business Journal coverage, and it operates at tutormate.org.

Consequence: when a model is asked "what is TutorMate?", the pre-trained association resolves to a nonprofit reading-tutor program, not an AI homework checker. The app has no Wikidata entity (`wbsearchentities` for "TutorMate" returns **zero results**), so there is nothing to attach a disambiguation to.

This is the highest-leverage finding in the audit. Every other fix is multiplied or nullified by it.

### 4b. Can a model tell what TutorMate is?

| Question | Answerable from the site? |
|---|---|
| What does it do? | **Yes.** The hero and the "Trusted by parents" paragraph are clear |
| Who makes it? | **No.** The site names no company, person, or legal entity. Footer says "© 2026 TutorMate." The only place the publisher appears is the App Store seller field: "Dustin Michael Walker" |
| What does it cost? | **Only visually.** $4.95/mo and $49/yr render in cards but do not survive text extraction, are not in `Product`/`Offer` schema, and the free-tier limit is never stated |
| How does it differ from Photomath, Gauth, Socratic, Chegg? | **No.** Those names appear nowhere. The "not an answer machine" line implies a contrast but never names what it contrasts with |
| What ages or subjects? | **No.** Nothing about grade level, subject coverage, or whether it handles handwriting, math notation, essays, or diagrams |
| Is it safe for a child? | **Partly.** The privacy policy is genuinely good (names Gemini, Firebase, Netlify, Apple, states no sale of data, documents account deletion) but it is unlinked from any question a parent would ask, and there is no COPPA or age statement in the crawlable marketing copy |
| When was it published or updated? | **No.** No dateline, no `dateModified`, nothing. `publication_date` had to be inferred as 2026-01-01 from the copyright string |

### 4c. Structured data

**Zero.** `structured_data.block_count = 0`. No JSON-LD, no microdata, no RDFa. Also missing: `<link rel="canonical">`, Open Graph tags, and Twitter card tags, so any share of the URL on Reddit, Discord, LinkedIn, or X renders with no title, image, or description, which suppresses exactly the off-site mentions the brand needs.

**Fix (effort: 1 to 2 hours).** Add to `<head>` of `/Users/dustinwalker/Documents/GitHub/tutormate/www/index.html`:

```html
<link rel="canonical" href="https://tutormate.ai/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="TutorMate">
<meta property="og:url" content="https://tutormate.ai/">
<meta property="og:title" content="TutorMate: AI That Checks Your Homework and Explains Why">
<meta property="og:description" content="TutorMate checks completed assignments and explains what is right, what is wrong, and why, and builds custom practice quizzes from a photo. A study partner, not an answer machine. Free to start, $4.95/month or $49/year.">
<meta property="og:image" content="https://tutormate.ai/Assets/og-card.png">
<meta name="twitter:card" content="summary_large_image">
```

And a JSON-LD graph before `</body>`:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://tutormate.ai/#org",
      "name": "TutorMate",
      "alternateName": "TutorMate AI",
      "url": "https://tutormate.ai/",
      "logo": "https://tutormate.ai/Assets/TutorMateLogoTransparent.png",
      "description": "Publisher of TutorMate, an AI study app that checks student homework and generates practice quizzes. Not affiliated with the TutorMate volunteer reading program operated by Chapter One.",
      "founder": { "@type": "Person", "name": "Dustin Michael Walker" },
      "sameAs": ["https://apps.apple.com/app/id6793738685"]
    },
    {
      "@type": "SoftwareApplication",
      "@id": "https://tutormate.ai/#app",
      "name": "TutorMate",
      "alternateName": "TutorMate: AI Homework Helper",
      "applicationCategory": "EducationalApplication",
      "applicationSubCategory": "Homework and study tool",
      "operatingSystem": "Web browser, iOS 17.0 or later",
      "url": "https://tutormate.ai/",
      "downloadUrl": "https://apps.apple.com/app/id6793738685",
      "publisher": { "@id": "https://tutormate.ai/#org" },
      "description": "TutorMate checks a student's completed homework from a photo and explains what is right, what is wrong, and why, and builds custom practice quizzes from a worksheet or any typed topic. It is a study partner rather than an answer machine.",
      "featureList": [
        "Photo-based assignment checking with explanations",
        "Custom quiz generation from a worksheet photo or typed topic",
        "Folders that sync across web and iOS"
      ],
      "offers": [
        {
          "@type": "Offer",
          "name": "TutorMate Premium Monthly",
          "price": "4.95",
          "priceCurrency": "USD",
          "category": "subscription",
          "url": "https://tutormate.ai/app/?plan=monthly"
        },
        {
          "@type": "Offer",
          "name": "TutorMate Premium Annual",
          "price": "49.00",
          "priceCurrency": "USD",
          "category": "subscription",
          "url": "https://tutormate.ai/app/?plan=annual"
        }
      ],
      "isAccessibleForFree": true
    }
  ]
}
</script>
```

Important: do **not** add `AggregateRating` from the 7 App Store ratings. Self-reported review markup on a first-party page with that sample size is a spam-flag risk and carries no persuasive weight.

Add a matching `FAQPage` block once the FAQ content in section 6 ships, and a `VideoObject` for the demo video.

---

## 5. Brand Mention and Corroboration Signals

**Severity: CRITICAL**

Models cite entities they can corroborate from more than one source. TutorMate currently has one.

| Signal | Correlation with AI citation | Status |
|---|---|---|
| YouTube mentions | ~0.737 (strongest known) | **None found.** The demo video is a self-hosted `<video>` on the landing page, not a YouTube upload. This is the single highest-correlation signal and it is being thrown away on a file that no engine indexes |
| Reddit presence | High | **None found** via available sources. No r/homeworkhelp, r/teenagers, r/Parenting, r/edtech, or r/iosapps footprint |
| Wikipedia / Wikidata entity | High | **No Wikidata item** (zero search results). Wikipedia's only "TutorMate" association belongs to Chapter One's reading program, which actively points away from this product |
| LinkedIn | Moderate | **No company page found** |
| Domain Rating / backlinks | ~0.266 (weak) | Effectively zero. No sitemap, no inbound links identified |
| App Store listing | Moderate, and this is the one real asset | **Live and healthy.** "TutorMate: AI Homework Helper", seller Dustin Michael Walker, Education, 4+, 5.0 stars from 7 ratings, v1.2 released 2026-10-21, first released 2026-08-12, `sellerUrl` correctly points to tutormate.ai |
| Product Hunt / AlternativeTo / G2 / Capterra | Moderate for "alternatives to X" queries | **Not listed anywhere found** |

Only about 11% of domains get cited by both ChatGPT and Google AI Overviews, so these off-site placements are not interchangeable with on-site fixes. Both tracks have to run.

**Note on the search-coverage limit of this audit:** general web search engines returned bot-verification challenges rather than results, so the Reddit, YouTube, and LinkedIn findings above are "none found via Wikipedia/Wikidata APIs, the App Store APIs, and direct URL probes" rather than a certified absence. Confirm manually in a browser before acting on the Reddit and YouTube items.

**Fixes, in order of correlation strength:**

1. **Publish the demo video to YouTube** (effort: 1 hour). Title it for the query, not the brand: "How to check your homework with AI and actually understand it (TutorMate demo)". Full description with the pricing facts and the tutormate.ai link. Then embed the YouTube player on the landing page, or keep the self-hosted file for performance and add a `VideoObject` with `embedUrl` pointing at YouTube. Add 3 to 5 more short videos: one per FAQ in section 6.
2. **Create a Wikidata item** (effort: 1 hour). Do not attempt a Wikipedia article, it will not survive notability review at 7 ratings. A Wikidata item for the software, explicitly `different from` the Chapter One reading program, is the cheapest way to break the entity collision. It needs at least one independent source to stick, so sequence it after item 4.
3. **Reddit and community presence** (effort: ongoing). Participate honestly in r/homeworkhelp, r/Parenting, r/teachers, r/edtech with disclosed affiliation. Astroturfing is both a ToS violation and a worse signal than silence once detected.
4. **Directory listings** (effort: 2 hours total). Product Hunt launch, AlternativeTo entry filed as an alternative to Photomath and Gauth and Socratic, G2 and Capterra profiles. These directly feed "best alternatives to Photomath" style queries, which is the highest-intent query class available to this product.
5. **LinkedIn company page** (effort: 30 min). Low effort, establishes the publisher entity.
6. **Name the publisher on the site** (effort: 10 min). Change the footer from "© 2026 TutorMate" to "© 2026 TutorMate. Built by Dustin Michael Walker." with an about link. Models need a `founder` or `publisher` they can see in the crawlable copy, not just in schema.

---

## 6. Questions TutorMate Could Be the Cited Answer For

**Severity: HIGH (this is the content plan)**

These are low-competition, high-intent queries where no incumbent gives a satisfying answer, and where TutorMate's "checks your work, not an answer machine" positioning is the differentiator rather than a marketing line.

### Tier 1: parent-intent, lowest competition, highest fit

1. "Is there a homework app that checks my child's work instead of giving answers?"
2. "What AI homework app is not cheating?"
3. "How can I tell if my kid is using AI to cheat on homework?"
4. "Is Photomath cheating?" / "Is Gauth cheating?"
5. "What is a safe AI study app for a middle schooler?"

### Tier 2: student-intent, practical

6. "How do I check my homework answers before turning it in?"
7. "How do I make a practice quiz from my notes?"
8. "How do I turn a worksheet into a quiz?"
9. "What is the best way to study for a test using AI?"
10. "Why is my answer wrong?" (long-tail, pairs with explanation-focused content)

### Tier 3: comparison, highest commercial intent

11. "TutorMate vs Photomath"
12. "Photomath alternatives that explain the reasoning"
13. "Is Chegg worth it for high school?" (Chegg is priced far above $4.95/mo, a real wedge)
14. "Socratic alternatives" (Socratic's Google-backed status and feature freeze make this a live query)
15. "Cheapest AI homework help app"

### Exact content blocks to add

Add an FAQ section to `/Users/dustinwalker/Documents/GitHub/tutormate/www/index.html` between the "Made for students. Trusted by parents." section and pricing, with question-shaped `<h2>`/`<h3>` headings, and mirror it with `FAQPage` JSON-LD. Each block below is written to be extractable standalone: it names the subject in the first sentence, answers in the first 40 to 60 words, and lands between 130 and 170 words.

---

**H2: Is TutorMate a cheating app?**

> No. TutorMate is built to check work a student has already done, not to do the work for them. When a student uploads a finished assignment, TutorMate marks what is right, flags what is wrong, and explains the reasoning behind each answer, so the student can find their own mistake and fix it.
>
> That is the difference between TutorMate and a solver app. Apps like Photomath, Gauth, and Socratic are designed to produce an answer to a problem you have not attempted yet. TutorMate starts from your attempt. If a student wants to practice instead, TutorMate builds a quiz from their worksheet or any topic they type in, so they get repetition rather than a shortcut.
>
> Teachers and parents can still see a student's original work, because TutorMate never replaces it. It comments on it.

---

**H2: How much does TutorMate cost?**

> TutorMate is free to start, with no credit card required. The first 10 quizzes and assignment checks are free. After that, TutorMate Premium is $4.95 per month or $49 per year, and the price is the same whether you subscribe on the web or through the iOS app. You can cancel at any time.
>
> The annual plan works out to about $4.08 per month, roughly a 17% saving against the monthly price. A single TutorMate subscription covers unlimited assignment checks, unlimited quiz generation, and folder storage that syncs between the web app at tutormate.ai and the iOS app on iPhone and iPad.
>
> iOS subscriptions are billed through your Apple Account and can be managed or cancelled in your device Settings. TutorMate never sees or stores payment details.

---

**H2: How is TutorMate different from Photomath, Gauth, Socratic, and Chegg?**

> TutorMate grades work you have already done and explains why each answer is right or wrong. Photomath, Gauth, and Socratic are built the other way round: you give them a problem you have not solved, and they return the solution with steps. Chegg is a subscription library of answers and expert help, priced well above TutorMate's $4.95 per month.
>
> The practical difference shows up in what a student ends up with. A solver app leaves a student holding an answer. TutorMate leaves a student holding a corrected paper and an explanation of their own mistake, which is what shows up on the test.
>
> TutorMate also generates practice quizzes from a student's own worksheet, notes, or any typed topic, which solver apps generally do not offer at all.

---

**H2: How do I turn a worksheet into a practice quiz?**

> Take a photo of the worksheet with TutorMate, or upload the file, and TutorMate builds a practice quiz from it in a few seconds. You can also skip the photo and type a topic, for example "photosynthesis" or "quadratic equations", and TutorMate generates questions on that topic instead.
>
> Quizzes are interactive. A student answers each question in the app and gets immediate feedback with the reasoning, rather than a score at the end with no explanation. Finished worksheets and quizzes save into folders that sync across the web app and iOS, so the same material can be practised again the night before a test.
>
> This works from a printed handout, a study guide, a page of handwritten notes, or a document file.

---

**H2: Can TutorMate check handwritten homework?**

> Yes. TutorMate reads a photo of a handwritten assignment, not just typed or printed work. Snap the page with a phone, and TutorMate identifies the questions and the student's written answers, then marks each one and explains the reasoning.
>
> This is the normal case rather than an edge case: most homework that needs checking is handwritten on a printed worksheet. For the clearest results, photograph the page flat in good light with the whole sheet in frame.
>
> *(Verify this claim against actual product behavior before publishing, including coverage of math notation, diagrams, and multi-page assignments. An overstated capability claim that gets picked up by an answer engine is harder to retract than it is to avoid. If coverage is partial, state the limits plainly: specificity about limits is itself a citability signal.)*

---

**H2: Who makes TutorMate?**

> TutorMate is built and published by Dustin Michael Walker. It launched on the iOS App Store in August 2026 and is available as a web app at tutormate.ai and as an iPhone and iPad app requiring iOS 17 or later. It is listed in the App Store Education category with a 4+ age rating.
>
> TutorMate's AI runs on Google's Gemini API. Uploaded worksheet images and typed topics are transmitted over encrypted connections and processed to generate quizzes and feedback. TutorMate does not sell personal information and does not use student content for advertising. Accounts, including all saved folders and uploaded images, can be permanently deleted from the app menu.
>
> TutorMate the AI study app is not affiliated with TutorMate, the volunteer early-literacy reading program operated by the nonprofit Chapter One.

---

That last paragraph is the disambiguation anchor. It should appear in crawlable text on the site, in llms.txt, and in the Wikidata description, so all three corroborate each other.

---

## 7. Technical Accessibility

**Severity: LOW to MEDIUM (this is the strongest dimension)**

What works:

- **Server-rendered static HTML.** `is_spa = false`, content is present in the raw fetch with no JavaScript execution needed. Every AI crawler, including those that do not run JS, sees the full copy. This is the single best thing about the current setup
- Clean semantic heading hierarchy: one H1, three H2, three H3, correctly nested
- `<html lang="en">` present
- Fast: static files on Netlify edge, HSTS enabled, no render-blocking content dependency
- `/robots.txt` and other missing paths return a **genuine 404**, not a soft 200
- `/privacy` correctly 301s to `/privacy/`
- Both images carry alt text, though it is thin ("TutorMate", "TutorMate logo")

What does not:

| Issue | Severity | Fix |
|---|---|---|
| No `sitemap.xml` | MEDIUM | Static 3-URL file, 10 min |
| No `<link rel="canonical">` | MEDIUM | One line |
| No Open Graph or Twitter cards | MEDIUM | Shared links render blank, suppressing off-site mentions |
| Demo video has no transcript, captions, or `VideoObject` | MEDIUM | The demo is the richest explanation of the product and it is entirely invisible to text-based retrieval. A transcript below the video converts it into citable text at near-zero cost |
| `/app/` loads Tailwind from CDN and is fully client-rendered | LOW | Fine, it is a logged-in app. Just keep it out of the index |
| Pricing values split across DOM nodes | HIGH (counted under Citability) | Add a prose sentence stating the full pricing, in addition to the cards |
| Thin alt text | LOW | "TutorMate marking a handwritten math worksheet, showing which answers are correct and why" beats "TutorMate" |
| No `dateModified` anywhere | MEDIUM | Add to JSON-LD and a visible "Last updated" line |

**Fix: `/Users/dustinwalker/Documents/GitHub/tutormate/www/sitemap.xml`**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://tutormate.ai/</loc>
    <lastmod>2026-11-01</lastmod>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://tutormate.ai/privacy/</loc>
    <lastmod>2026-07-07</lastmod>
    <priority>0.3</priority>
  </url>
</urlset>
```

---

## 8. Top 5 Highest-Impact Changes

| # | Change | Severity | Effort | Why it ranks here |
|---|---|---|---|---|
| 1 | **Add the six FAQ answer blocks from section 6**, with question-shaped headings and `FAQPage` JSON-LD | CRITICAL | 4 to 6 hours | Takes the site from 961 characters of body text with one citable passage to roughly 1,000 words of directly quotable answers aimed at real queries. Nothing else on this list matters if there is no text to cite |
| 2 | **Break the name collision**: add the "not affiliated with the Chapter One reading program" line to the site, llms.txt, and a new Wikidata item, and name Dustin Michael Walker as publisher in visible copy and `Organization` schema | CRITICAL | 2 to 3 hours on-site, plus Wikidata | Right now a model asked "what is TutorMate?" has a confident, well-corroborated, wrong answer. Every citation you earn leaks to a nonprofit literacy program until this is fixed |
| 3 | **Publish the demo video to YouTube** with a query-shaped title and a full description, and add `VideoObject` plus an on-page transcript | HIGH | 2 hours | YouTube mentions carry the strongest observed correlation with AI citations (~0.737). The asset already exists and is currently invisible to every retrieval system |
| 4 | **Ship robots.txt, llms.txt, sitemap.xml, canonical, and Open Graph tags** (exact files in sections 1, 2, 7, 4c) | HIGH | 1.5 hours | Pure plumbing, no copywriting, no product decisions. Opens crawl control, states the entity in the models' preferred format, and makes shared links render, which is a prerequisite for the Reddit and community mentions in change 5 |
| 5 | **Build off-site corroboration**: Product Hunt, AlternativeTo (filed against Photomath, Gauth, Socratic), G2, Capterra, LinkedIn company page, honest disclosed Reddit participation | HIGH | 4 hours initial, then ongoing | Only about 11% of domains are cited by both ChatGPT and Google AI Overviews. Directory listings feed "alternatives to Photomath" queries directly, which is the highest commercial-intent query class this product can win |

**Also worth doing, below the top 5:** state the 10-free-items limit on the site so the canonical source is not vaguer than the App Store listing; put pricing in a prose sentence as well as cards; improve alt text; add a visible "Last updated" dateline.

---

## 9. Structured Findings (for audit-data.json)

```json
{
  "category": "AI Search Readiness",
  "score": 28,
  "dimensions": {
    "citability": 18,
    "structural_readability": 35,
    "multi_modal": 20,
    "authority_brand": 12,
    "technical_accessibility": 55
  },
  "platform_scores": {
    "google_aio": 25,
    "chatgpt": 22,
    "perplexity": 30,
    "bing_copilot": 28
  },
  "crawler_access": {
    "robots_txt": "404_missing_defaults_to_full_allow",
    "OAI-SearchBot": "allowed_by_default",
    "Claude-SearchBot": "allowed_by_default",
    "PerplexityBot": "allowed_by_default",
    "Googlebot": "allowed_by_default",
    "Bingbot": "allowed_by_default",
    "Applebot": "allowed_by_default",
    "GPTBot": "allowed_by_default",
    "ClaudeBot": "allowed_by_default",
    "Google-Extended": "allowed_by_default",
    "Applebot-Extended": "allowed_by_default",
    "CCBot": "allowed_by_default"
  },
  "llms_txt": "missing",
  "sitemap_xml": "missing",
  "rsl_licensing": "absent",
  "canonical": "missing",
  "open_graph": "missing",
  "structured_data_blocks": 0,
  "is_spa": false,
  "server_rendered": true,
  "body_text_chars": 961,
  "citable_passages": 1,
  "brand_signals": {
    "wikipedia_entity": "none_for_this_product_collision_with_chapter_one_tutormate",
    "wikidata_entity": "none",
    "youtube": "none_found",
    "reddit": "none_found",
    "linkedin": "none_found",
    "app_store": "live_5.0_stars_7_ratings_v1.2_2026-10-21"
  },
  "entity_risks": [
    "name_collision_with_chapter_one_tutormate_literacy_program",
    "no_named_publisher_in_crawlable_copy",
    "pricing_not_in_extractable_text",
    "free_tier_limit_unstated_on_site",
    "no_competitor_comparison_content"
  ],
  "critical_findings": 2,
  "high_findings": 3,
  "medium_findings": 4,
  "low_findings": 2
}
```
