# TutorMate SEO action plan

What is done, and what only you can do. Ordered by impact.

---

## Phase 0: Deploy (blocks everything else)

Nothing in Phase 1 can happen until this ships. The new files are a 404 in production right now.

```bash
npm run build:css && npm run build:pages
```

Then commit and deploy. Verify after deploy that these return 200:
`/robots.txt`, `/sitemap.xml`, `/llms.txt`, `/about/`, `/homework-help/`, `/quiz-generator/`, `/vs/photomath/`.

**Watch for:** Netlify now runs a build command for the first time. If the build fails, the deploy fails. The CSS is committed, so the site will not break, but check the deploy log.

---

## Phase 1: Tell Google (week 1, about 30 minutes)

### 1. Submit the new sitemap
Search Console → Sitemaps → submit `sitemap.xml`. I did not do this for you because the file 404s until you deploy.

### 2. Remove the stale sitemap
GSC is still holding `sitemap_index.xml`, last downloaded **2023-08-06**, status "Has errors", 1 error and 7 warnings. It predates your ownership of the domain and is feeding Google garbage. Delete it in the Sitemaps panel. I did not do this because deleting from your Search Console is your call.

### 3. Request indexing
URL Inspection → Request Indexing, for each of the four new pages and the updated homepage.

### 4. Bing Webmaster Tools
If you have not claimed the domain, do. Bing feeds ChatGPT search and Copilot, which matters for the AI-visibility goal. Import from GSC is the fast path.

---

## Phase 2: Break the name collision (weeks 1 to 3)

**This is the highest-leverage work remaining, and it is almost entirely off-site.** The on-site half is done; a model reading tutormate.ai now gets the right answer. The problem is that models mostly are not reading tutormate.ai, they are recalling the Chapter One reading program.

### 1. Create a Wikidata item
There is currently no Wikidata item for the app, so there is nothing to attach a disambiguation to. Create one for "TutorMate (software)" with:
- `instance of`: mobile app / web application
- `different from`: the Chapter One TutorMate program
- `developer`: Walker Intelligence Group
- `official website`: https://tutormate.ai

Wikidata is disproportionately influential in how models resolve entities. This is the single highest-value hour in the plan.

### 2. Get listed where comparisons live
- **AlternativeTo**, filed specifically against Photomath, Socratic, Gauth and Chegg
- **Product Hunt** launch
- **G2** and **Capterra** under education software

These are the pages models cite when asked "alternatives to X". You cannot be the answer to "Photomath alternatives" if you are not on the lists.

### 3. Always pair the name
In every off-site bio, listing and profile, write "TutorMate, the AI homework checker" rather than "TutorMate". You are training the association.

---

## Phase 3: Put the demo video where it can be found (week 2, ~2 hours)

Your demo video is the clearest explanation of the product you have, and it is a self-hosted MP4 with no transcript and no captions. It is invisible to every retrieval system on earth.

1. Upload it to **YouTube** with a query-shaped title, something like "How to check your homework with AI (without cheating)".
2. Write a full description with the free-tier limit and pricing in plain text.
3. **Add a transcript to `/homework-help/`.** This is the part that matters for SEO: it converts your best explanation into indexable, citable text.
4. Add captions for accessibility.

The `VideoObject` schema is already in place and will pick up a YouTube `embedUrl` when you have one.

---

## Phase 4: Fix the two non-SEO things I found (week 2)

1. **Privacy policy: add Stripe.** It names Apple as the payment processor, but `Netlify/Functions/` shows Stripe handling web payments, and Stripe is not listed as a service provider. This is a factual gap in a legal document. Yours to correct.
2. **Gitignore `node_modules/`.** It is currently committed. Unrelated to SEO, but it will keep causing noise.

Optional: align the App Store seller name with Walker Intelligence Group.

---

## Phase 5: Content, ongoing

The four new pages cover the highest-intent queries. The next tier, in priority order:

| Page | Why |
|---|---|
| `/for-parents/` | The least-contested intent. No incumbent answers "is there an app that checks my child's work instead of giving answers?" well. This is your wedge. |
| `/vs/chegg/` | Chegg prices far above $4.95/mo. A real, defensible price argument. |
| `/vs/socratic/` and `/vs/gauth/` | Completes the comparison set models reach for. |
| `/terms/` and `/support/` | Trust signals you currently lack entirely for a paid product. |
| Subject hubs (math, algebra, chemistry, biology, Spanish) | Only once the above exist. Thin subject pages at scale are an index-bloat risk, not a win. |

Write these the way the existing pages are written: question-shaped headings, the answer in the first 40 to 60 words, concrete facts rather than brand vocabulary. That structure is what makes a passage citable.

---

## Phase 6: Measure (ongoing)

Re-check in Search Console at **4 weeks** and **12 weeks**. Expect impressions before clicks and clicks before positions.

Realistic expectation: you are starting from 1 impression in 90 days on a domain with essentially no authority. The foundation work removes the reasons you *could not* rank. It does not by itself create demand. Phases 2 and 3, the off-site work, are what convert a technically sound site into a cited one, and they are the ones that need you rather than the repo.

Re-run the audit with `/seo-audit https://tutormate.ai` once Phase 1 and 2 are done.

---

## Reference: what was built

| File | Purpose |
|---|---|
| `www/robots.txt` | Crawl directives, AI crawlers explicitly allowed |
| `www/sitemap.xml` | Generated, noindex-aware |
| `www/llms.txt` | AI-reader summary, leads with the disambiguation |
| `www/about/`, `www/homework-help/`, `www/quiz-generator/`, `www/vs/photomath/` | New pages |
| `www/styles/tailwind.css` | Built CSS, replaces the 127 KB CDN script |
| `www/fonts/nunito-800.woff2` | Self-hosted font |
| `www/Assets/og-image.png` | 1200x630 social preview |
| `scripts/seo/build_pages.py` | Generates the marketing pages from one shared shell |
| `scripts/seo/build_sitemap.py` | Generates the sitemap from the filesystem |
| `scripts/seo/build_og_image.py` | Renders the OG image |
| `tailwind.config.js`, `src/tailwind.css` | Build inputs |
| `netlify.toml` | Build command, redirects, security and cache headers |

Rebuild everything with:

```bash
npm run build:css && npm run build:pages
```
