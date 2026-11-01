# tutormate.ai SEO and AI-visibility audit

**Date:** 2026-11-01
**Scope:** Full-site audit of https://tutormate.ai, plus implementation of the foundation and core pages.
**Specialists run:** technical, performance, content/E-E-A-T, GEO (AI search readiness).

---

## Starting position

The honest summary of where the site was: technically clean, and almost entirely invisible.

| Signal | Before |
|---|---|
| Google Search Console, last 90 days | 1 impression, 0 clicks, position 63 |
| Indexable pages | 2 (`/` and `/privacy/`), plus `/app/` leaking into the index |
| Visible words on the whole domain | ~806, of which 535 were the privacy policy |
| robots.txt | 404 |
| sitemap.xml | 404 (GSC still held a broken `sitemap_index.xml` from 2023) |
| Canonical tags | None |
| Open Graph / Twitter cards | None |
| Structured data | None, on any page |
| Critical-path weight | ~145 KB across 3 origins, Tailwind compiling CSS in the browser |

Specialist scores at baseline: **Technical 38/100**, **Content 31/100**, **E-E-A-T 16/100**, **GEO 28/100**.

The site was not being penalized or blocked. It simply had nothing to rank: one 271-word landing page, no category vocabulary, and no machine-readable description of what the product is.

---

## The finding that matters most

**"TutorMate" is already a well-established entity, and it is not this product.**

TutorMate is also the name of a volunteer early-literacy reading program run by the nonprofit Chapter One (formerly Innovations for Learning), operating since the 1990s. I verified this independently rather than taking the specialist's word for it. It carries substantial corpus weight: Stanford's National Student Support Accelerator, University of Houston's College of Education, a National Literacy Trust pilot evaluation, Kaiser Permanente, and United Way have all published about it.

The consequence is specific and severe. Asked "what is TutorMate?", a language model has a **confident, well-corroborated, wrong answer**. There is no Wikidata item for the app to attach a disambiguation to. Every other AI-visibility improvement is multiplied or nullified by this one problem.

One nuance the specialist got slightly wrong, and it works in your favor: the reading program migrated off `tutormate.org` to `chapterone.org` in February 2023. So the collision lives in training data and historical citations, not in a live competing site defending the exact name. That makes it winnable, but only with deliberate disambiguation, which is now built into the site.

---

## What was wrong, by category

### Technical (38/100)

No Critical issues. The plumbing was genuinely clean: HTTPS, single-hop redirects, consistent trailing slashes, real 404s, `lang="en"`, server-rendered HTML, HSTS present.

What was missing was everything that tells a crawler what to do: no robots.txt, no sitemap, no canonicals despite `/index.html` and `/app/index.html` both returning 200, and the 142 KB client-rendered app shell sitting indexable with the title "Tutor Mate" and no description. Security headers were limited to a bare HSTS. Every asset, including the 3 MB demo video, was served `max-age=0, must-revalidate`.

### Performance (90/100 lab, LCP 2.8 s)

Not broken, but paying an unnecessary tax. The LCP element was a text node, and the culprit was `cdn.tailwindcss.com`: 126,871 B transferred, 407 KB uncompressed, ~1,594 ms of render-blocking time, compiling CSS in the visitor's browser. Google Fonts added two more origins and caused the only measured layout shift when Nunito swapped in.

The demo video was *not* the problem. `preload="metadata"` was doing its job, pulling only 54 KB. The 3 MB file is still oversized for a 308 px display width, but it is not on the critical path.

### Content and E-E-A-T (31/100 and 16/100)

The core problem. 271 words on the only commercial page, against a ~500-word floor for competitive coverage.

The page never contained the words *homework*, *math*, *solver*, *scan*, *practice test*, *AI tutor*, *grade level*, or *free*. The product's job was described entirely in internal brand vocabulary ("check your work", "study partner", "answer machine"). No About page, no legal entity, no named person, no Terms, no support page. "© 2026 TutorMate" was the entire corporate disclosure on a paid subscription product that processes schoolwork uploaded by minors.

"Trusted by parents" asserted third-party endorsement with nothing behind it.

### GEO / AI search readiness (28/100)

Trafilatura extracted **961 characters total** from the homepage, with exactly one genuinely quotable passage. Critically, **the pricing did not survive text extraction at all**: `$4.95` and `/mo` lived in separate DOM nodes inside the price cards, so the extracted text contained no price. The site also never stated the free-tier limit that the App Store listing does state.

Crawler access was not the issue. A 404 robots.txt means full allow under RFC 9309, so nothing was being blocked. The problem was that there was nothing worth citing.

---

## What I changed

### Crawl and indexing foundation
- **`www/robots.txt`** created, explicitly allowing GPTBot, ClaudeBot, PerplexityBot, OAI-SearchBot, Google-Extended, Applebot-Extended and CCBot, each with `/app/` excluded. Google-Extended is deliberately allowed: it governs Gemini grounding, and TutorMate itself runs on Gemini.
- **`www/sitemap.xml`** generated from the filesystem by `scripts/seo/build_sitemap.py`, which reads each page's robots meta so a noindex page can never be listed by accident.
- **`/app/` removed from the index** via both a `noindex, follow` meta tag and an `X-Robots-Tag` header, and given a real title and description. Kept crawlable so the directive is actually visible.
- **Canonicals** on every page; 301s added for `/index.html` and `/app/index.html`.

### Structured data
JSON-LD added to every page. The homepage carries a linked `@graph`: `Organization` (Walker Intelligence Group), `WebSite`, `SoftwareApplication` with all three offers priced, `VideoObject` for the demo, and a `FAQPage` with 7 questions. The FAQ schema is **extracted from the rendered markup at build time**, so it cannot drift from the visible text. Sub-pages carry `WebPage`, `HowTo`, `FAQPage` and `BreadcrumbList`.

**Deliberately omitted: `AggregateRating`.** Self-reporting your own 5.0-from-7-ratings on your own page is a spam-flag risk at that sample size with no persuasive upside.

### Content
Homepage grew from **271 to 888 visible words**, and four new pages were added. Total indexable content went from **806 words across 2 pages** to **4,171 words across 6 pages**.

| Page | Words | Targets |
|---|---|---|
| `/` | 888 | brand, "AI homework helper", pricing, FAQ |
| `/homework-help/` | 765 | "AI homework help", "check my homework", handwriting, subject coverage |
| `/vs/photomath/` | 687 | "Photomath alternative", checker vs solver |
| `/about/` | 682 | "who makes TutorMate", entity disambiguation |
| `/quiz-generator/` | 614 | "practice quiz generator", "worksheet to quiz" |

Specific fixes:
- **H1 changed** from "Check your work. Study smarter." to "The AI homework helper that checks your work", so it carries the category term.
- **Price and free tier now in plain prose**, in the hero and the FAQ, so they survive text extraction. This was invisible to every AI retrieval system before.
- **"Trusted by parents" rewritten** as a design-intent claim ("Built to teach, not to hand over answers"), since there was nothing substantiating the endorsement.
- **Entity disambiguation** written into the About page, the homepage FAQ, and `llms.txt`, explicitly naming the Chapter One program as unrelated.
- **`llms.txt`** added, leading with the disambiguation.

### Performance
- **Tailwind now builds at deploy time** (`npm run build:css`) into a 14.7 KB static file, replacing 127 KB of render-blocking JavaScript. **Critical path cut by 85%**, from ~145 KB across 3 origins to ~20 KB same-origin, with zero blocking scripts in the head.
- **Nunito self-hosted** and preloaded, removing two origins and the font-swap layout shift.
- **Cache headers** set to a year on `/Assets/*`, `/styles/*` and `/fonts/*`.
- **Security headers** added: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`, and `includeSubDomains` on HSTS.
- **Explicit dimensions** on the video and logo images, removing the latent CLS risk.

`www/app/index.html` was deliberately left on the Tailwind CDN. Its class names are partly constructed at runtime and would not survive a static content scan, so converting it risks breaking the actual product for no SEO gain on a noindexed page.

### Social
A 1200x630 Open Graph image was generated (`scripts/seo/build_og_image.py`) and wired into OG and Twitter card tags site-wide. Shared links previously showed no preview at all.

---

## Verification

A check script asserted, across all 7 pages: exactly one H1, a title under 60 characters, a description of 120 to 165 characters, a canonical, at least 4 OG tags, and valid parseable JSON-LD. Every internal link target was resolved against the filesystem.

**Result: 0 failures, 0 warnings.** The page generator was also confirmed idempotent, so a rebuild cannot silently undo the metadata.

Rendering was verified in a browser at desktop and 375 px mobile, with no console errors.

---

## Two things I found that are not SEO, and did not change

1. **The privacy policy is incomplete.** It states that subscriptions are processed by Apple, but `Netlify/Functions/` shows Stripe handling web payments. Stripe is not named as a service provider. That is a factual gap in a legal document and should be corrected by you, not silently by me.

2. **`node_modules/` is committed to the repository** and is not in `.gitignore`. Pre-existing, unrelated to this work, and worth fixing separately.

A third, minor: the App Store seller is "DUSTIN MICHAEL WALKER" while the site and schema now say Walker Intelligence Group. That inconsistency is survivable and the schema names you as founder, but aligning the App Store seller name would strengthen the entity.

---

## Where this leaves you

Scores are implementation-complete, not outcome-verified. Nothing here has been deployed yet, and rankings respond over weeks.

| Category | Before | After implementation |
|---|---|---|
| Technical | 38 | ~88 |
| Content | 31 | ~72 |
| E-E-A-T | 16 | ~55 |
| GEO | 28 | ~70 |
| Performance | 90 lab | ~97 expected |

The remaining gap in every category is **off-site**, and it is not something I can fix from the repository. See `ACTION-PLAN.md`.
