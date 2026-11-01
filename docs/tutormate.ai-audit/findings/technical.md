# Technical SEO findings: https://tutormate.ai
Audited 2026-11-01. Live checks via curl plus review of /www source, /netlify.toml.
Technical score: 38/100

Category status: Crawlability FAIL | Indexability FAIL | Security PARTIAL | URL structure PASS (minor) | Mobile PASS | CWV risk FAIL | Structured data FAIL | JS rendering PARTIAL (landing OK, /app/ CSR) | IndexNow N/A until sitemap exists

## Verified as stated
- /robots.txt, /sitemap.xml, /llms.txt: all HTTP 404. sitemap_discovery.py finds no sitemap at any common path.
- Landing page: no canonical, no Open Graph, no Twitter tags, no JSON-LD. Same for /privacy/ and /app/.
- netlify.toml contains only [build] publish="www", functions="Netlify/Functions". No [[headers]], no [[redirects]], no _headers or _redirects file.

## Critical
None (the site is live, 200s, HTTPS). Items below are the largest gaps.

## High
1. No robots.txt. Crawlers get a 404 HTML page; no sitemap pointer, no control over /app/ or /.netlify/functions/. Fix: create /www/robots.txt:
   User-agent: *
   Disallow: /.netlify/
   Sitemap: https://tutormate.ai/sitemap.xml
   Do NOT Disallow /app/: a blocked page cannot be crawled, so Google never sees its noindex and may still index the bare URL. Use noindex (item 3) instead.
2. No sitemap.xml. Fix: create /www/sitemap.xml listing https://tutormate.ai/ and https://tutormate.ai/privacy/ (trailing slash, apex, https; add lastmod). Submit in Google Search Console and Bing Webmaster Tools.
3. /app/ is indexable and should not be. It is a 142 KB single-page app with title "Tutor Mate" (differs from brand "TutorMate"), no description, no content for crawlers, and it is linked from the landing page CTAs, including parameter variants /app/?plan=monthly and /app/?plan=annual (duplicate URLs). Fix: add `<meta name="robots" content="noindex, follow">` to /www/app/index.html, and as backup a header in netlify.toml:
   [[headers]]
     for = "/app/*"
     [headers.values]
       X-Robots-Tag = "noindex"
   Also add `for = "/app"` equivalent if needed. Keep it crawlable (not Disallowed) until it drops from the index.
4. No canonical tags on any page. / is reachable as /, /index.html (200, duplicate), and with query strings; /app/ also at /app/index.html (200). Fix: add `<link rel="canonical" href="https://tutormate.ai/">` to the landing page, `https://tutormate.ai/privacy/` to privacy, and `https://tutormate.ai/app/` to app (or noindex only). Optionally 301 /index.html to / in netlify.toml:
   [[redirects]]
     from = "/index.html"
     to = "/"
     status = 301
     force = true
5. Render-blocking runtime Tailwind: `<script src="https://cdn.tailwindcss.com">` (landing line 19, privacy line 8, app line 8) is a synchronous script in head that compiles CSS in the browser. Tailwind itself says the Play CDN is not for production. Impact: delayed FCP/LCP, a flash of unstyled content and layout shift risk (CLS), extra third-party DNS/TLS, and a main-thread cost that hurts INP on the heavy app. Fix: build static CSS (npx tailwindcss -i in.css -o www/assets/tw.css --minify, with the navy palette in tailwind.config.js, content globbing www/**/*.html), link it with `<link rel="stylesheet">`, and remove both CDN script and inline tailwind.config. The /app/ page also loads mammoth and marked from jsdelivr synchronously in head: add `defer` (or load mammoth only on docx upload).
6. No Open Graph / Twitter Card tags. Links shared in iMessage, Slack, social show no preview. Fix in landing head: og:type=website, og:site_name=TutorMate, og:title, og:description, og:url=https://tutormate.ai/, og:image (absolute URL, 1200x630 PNG/JPG; the current 512-ish logo and the poster are not suitable), twitter:card=summary_large_image. Add basic OG to /privacy/ too.
7. No structured data. Fix: add JSON-LD to the landing page: Organization (name, url, logo absolute URL), WebSite, and SoftwareApplication/MobileApplication (applicationCategory EducationalApplication, operatingSystem iOS/Web, offers for monthly and annual plans matching the pricing section, link to the App Store id6793738685). Validate with Rich Results Test.

## Medium
8. Security headers mostly absent. Present: strict-transport-security max-age=31536000 only. Missing: includeSubDomains/preload, Content-Security-Policy, X-Content-Type-Options, X-Frame-Options or frame-ancestors, Referrer-Policy, Permissions-Policy. /app/ handles uploads and Stripe checkout so clickjacking and XSS hardening matter. Fix in netlify.toml:
   [[headers]]
     for = "/*"
     [headers.values]
       Strict-Transport-Security = "max-age=63072000; includeSubDomains; preload"
       X-Content-Type-Options = "nosniff"
       X-Frame-Options = "DENY"
       Referrer-Policy = "strict-origin-when-cross-origin"
       Permissions-Policy = "camera=(self), microphone=(), geolocation=()"
   Roll out CSP in Content-Security-Policy-Report-Only first; the app uses inline scripts, cdn.tailwindcss.com, jsdelivr, Google Fonts, Stripe, so removing the Tailwind CDN (item 5) makes a strict CSP feasible. Check the app's camera use before restricting Permissions-Policy. Only add preload once every subdomain is HTTPS.
9. Caching: all assets, including the 3.0 MB TutorMateDemo.mp4, return cache-control: public,max-age=0,must-revalidate. Repeat visits revalidate everything. Fix: headers for /Assets/* with `Cache-Control = "public, max-age=31536000, immutable"` (rename files with a version/hash when changed) or at least max-age=86400. HTML can stay must-revalidate.
10. LCP/CLS risks on landing: hero logo and video poster images have no width/height attributes (img lines 85, 101); the poster is 22 KB but the logo PNG is 10 KB used at h-9 and w-32, fine; add explicit width/height to prevent shift. Nunito font loaded from Google Fonts as a render-blocking stylesheet: use `display=swap` in the URL (currently absent) or self-host a woff2 subset. Video is preload="metadata" (good).
11. Thin on-page content for search: the landing page has a single H1 and short sections; the title "TutorMate: Check Your Work. Study Smarter." and description are acceptable (~41 and ~150 chars). /privacy/ has no meta description, and /app/ has none either. Fix: add a description to /privacy/ (or noindex it; privacy pages seldom need ranking).
12. Brand inconsistency: app title "Tutor Mate", privacy "Privacy Policy — TutorMate" (contains an em dash), landing "TutorMate". Fix: standardise on "TutorMate".

## Low
13. Trailing slash/URL consistency: server redirects /privacy to /privacy/ and /app to /app/ with 301 (Netlify pretty URLs), so behavior is consistent, but the landing footer links to "/privacy" (line 308), costing a redirect hop. Fix: link to /privacy/. The native-shell redirect script uses 'app/index.html' (relative, would expose /app/index.html duplicate); change to '/app/'.
14. www vs apex: GOOD. https://www.tutormate.ai/ gives 301 to https://tutormate.ai/; http gives a single 301 to https. One hop each, no chains. Keep apex as canonical and sitemap host.
15. 404 handling: nonexistent URLs return a real HTTP 404 (good) using Netlify's default page. Add a branded /www/404.html with a link home.
16. Favicon is only a single PNG at /Assets/ (capital A path). Add apple-touch-icon (180x180), a /favicon.ico, and a web manifest. Prefer lowercase asset paths.
17. Image alt: hero logo `alt="TutorMate logo"` is fine; video lacks captions/track and a text transcript. Add a `<track kind="captions">` for accessibility and extra indexable text.
18. Video SEO: optionally add VideoObject JSON-LD for the demo (thumbnailUrl, contentUrl, uploadDate, duration).
19. llms.txt is a 404. Optional and not a ranking factor; a short /www/llms.txt describing the product and key URLs is cheap. Low priority.
20. IndexNow: after a sitemap exists, add a key file in /www and ping https://api.indexnow.org/indexnow on deploy (Bing, Yandex, Naver). Optional for a 2-page site.

## Verified good
- HTTPS with HTTP/2, HSTS present, http and www both redirect in one hop.
- Viewport meta present on all three pages (landing and app use viewport-fit=cover); lang="en" set.
- Landing page content is server-rendered HTML (no JS needed to read it); only /app/ is CSR, which is fine if it is noindexed.
- Real 404 status codes; no redirect chains found.

## Suggested single patch (netlify.toml additions)
Add the [[headers]] blocks from items 3, 8, 9 and the redirect from item 4, then add robots.txt, sitemap.xml, canonical/OG/JSON-LD tags, and the static Tailwind build. Expected effect: all High items closed and a score of roughly 80+.
