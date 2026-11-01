# Performance findings: tutormate.ai (2026-11-01)

Method: local Lighthouse 13.6.0, mobile emulation (simulated Slow 4G, 4x CPU), one run per page, plus curl and local file inspection. PageSpeed Insights API was rate limited (no PSI or CrUX field data obtained). All numbers are lab data from a single run, so treat them as directional. Field (CrUX) validation is still needed.

## Scores and metrics

| Metric | Landing (/) | Privacy (/privacy/) | Status |
|---|---|---|---|
| Performance score | 90 | 96 | - |
| FCP | 2.8 s | 2.2 s | - |
| LCP | 2.8 s | 2.2 s | Landing: needs improvement (>2.5 s). Privacy: good |
| TBT (INP proxy) | 0 ms | 0 ms | Good (no INP field data) |
| CLS | 0.0003 | 0 | Good |
| TTFB, Lighthouse (simulated) | 584 ms | 202 ms | Good (<0.8 s) |
| TTFB, curl from dev machine | ~0.15 s | ~0.15 s | Good (Netlify edge, HTTP/2) |
| Speed Index | 3.3 s | 3.0 s | - |
| Transfer weight | 236 KiB (242,104 B) | 142 KiB (145,300 B) | Good |

Main-thread work: landing 0.4 s (script evaluation 194 ms), privacy 0.3 s (script evaluation 195 ms). Both are almost entirely the Tailwind CDN script.

## Culprit analysis

### LCP: Tailwind CDN, not the video. [HIGH]
- LCP element on both pages is a text node (landing: hero `<p>` under the h1; privacy: first `<li>`). It is not the video or poster.
- Landing LCP breakdown: TTFB 584 ms, element render delay 963 ms. Privacy: TTFB 202 ms, render delay 1346 ms. There is no resource load delay or duration because the LCP is text. All the delay is render blocking.
- Lighthouse render-blocking insight: `cdn.tailwindcss.com/3.4.17` blocks for about 1,594 ms (landing) and 1,381 ms (privacy). Google Fonts CSS blocks for about 1,097 ms (landing) but overlaps with Tailwind, so it is not additive.
- The Tailwind script is 126,871 B transferred, 407,279 B uncompressed, with 39 to 45 KiB unused. It is 52% of landing transfer weight and 87% of privacy weight. It takes 194 ms of script evaluation and also must JIT-compile CSS in the browser, which is why FCP equals LCP and nothing paints before it.
- Estimated saving from replacing it with a prebuilt stylesheet (about 10 to 20 KB): roughly 1.4 to 1.6 s of LCP, bringing landing to about 1.2 to 1.5 s. That is an estimate from the Lighthouse insight, not a measured A/B run.

### CLS: not a problem. [LOW]
- Landing CLS is 0.0003, from a single shift on the `h1.font-title`, which is the Nunito swap (the h1 reflows when the font arrives). Negligible, but it is the Google Fonts cost.
- The video does not cause CLS in this run. Lighthouse lists the `<video>` as the shifted element's context, but the only shift score is on the h1 (the video sits below it, 918 px down, and is pushed by the h1 shift). The video has no width/height or aspect-ratio, and the poster loads on its own, so there is latent risk on slow connections. See fix 5.
- Because Tailwind generates all layout CSS at runtime, there is no visible layout shift in lab only because the script is render-blocking. Removing the blocking behavior (for example by adding `async`) would turn this into a real CLS problem. Keep it blocking or precompile.

### Video: cheap on load. [LOW, but a latent risk]
- `preload="metadata"` works: only 53,919 B transferred (range request, 185 ms) at load. It does not touch LCP or CLS. Impact on load weight: 54 KB of 236 KiB (22%).
- Poster: 22,846 B JPG, 540x1168, requested at 238 ms. Not the LCP (it is below the fold at y=918).
- The full file is 3,035,348 B (2.9 MB), 794x1716 H.264, 47.6 s, ~508 kbps, no audio check done. Played to the end it adds 3 MB. Not a load metric problem, but is a data cost for mobile users. Note the video is 794 px wide while it is displayed at ~308 CSS px (about 616 px at 2x), so it is slightly oversized.
- Netlify serves it with `cache-control: public,max-age=0,must-revalidate`, so repeat plays and visits revalidate each time.

### Google Fonts (Nunito 800). [MEDIUM]
- CSS 1,035 B plus woff2 16,509 B, two extra origins (fonts.googleapis.com, fonts.gstatic.com). Preconnects are present and `display=swap` is set. Cost: about 1.1 s of render blocking from the stylesheet in the throttled run (overlapping Tailwind), and the 0.0003 CLS above. Used only for the `.font-title` headings.

## Asset sizes (/Users/dustinwalker/Documents/GitHub/tutormate/www/Assets/)

| File | Size | Dimensions | Verdict |
|---|---|---|---|
| TutorMateDemo.mp4 | 3,035,348 B (2.9 MB) | 794x1716, 47.6 s, 508 kbps | Re-encode, see fix 4 |
| TutorMateDemoPoster.jpg | 22,722 B | 540x1168 | Fine. Optional WebP/AVIF saves about 8 to 12 KB |
| TutorMateLogoTransparent.png | 10,512 B | 221x199 | Fine. Displayed at 36 px and 128 px, so a 2x WebP or SVG would be about 3 KB. It is fetched twice per load (the favicon request adds 68 B transferred plus a second request) |

Nothing here is critically oversized. Only the video is worth work.

## Other observations
- Static assets use `max-age=0, must-revalidate`. Add long-lived caching for `/Assets/*`.
- Netlify RUM script (`/.netlify/scripts/rum`, 4.3 KB) is injected. Harmless.
- No render-blocking JS besides Tailwind. The inline Capacitor check is trivial.

## Prioritized fixes

1. [HIGH] Replace the Tailwind CDN with a build-time stylesheet on both pages. Run `npx tailwindcss -i in.css -o www/assets/tw.css --minify` using the existing `tailwind.config` theme (navy colors, etc.) and content globs for `www/**/*.html`. Link it with `<link rel="stylesheet">`. Expected: -127 KB transfer, -407 KB parse, -194 ms scripting, LCP about -1.4 to 1.6 s (landing about 1.3 s). The CDN itself warns it is not for production.
2. [MEDIUM] Self-host Nunito 800 (the one woff2, 16.5 KB) with `@font-face { font-display: swap }`, add `<link rel="preload" as="font" type="font/woff2" crossorigin>`, and drop the two Google origins. Removes about 1 s of blocking and the h1 shift. Optionally add `size-adjust` fallback metrics.
3. [MEDIUM] Cache headers in `netlify.toml`: `/Assets/*` with `Cache-Control: public, max-age=31536000, immutable` (rename files with a hash or version when they change), and keep HTML on revalidate.
4. [LOW] Re-encode the video: scale to about 640 px wide, `ffmpeg -i in.mp4 -vf scale=640:-2 -c:v libx264 -crf 28 -preset slow -movflags +faststart -an out.mp4`, or H.265/AV1 or WebM VP9 as extra `<source>`s. Expected 1.2 to 1.8 MB (about 40 to 60% less). The file should have `faststart` so metadata is at the front (confirm with ffprobe, since the 54 KB metadata fetch suggests it already is).
5. [LOW] Add `width="308" height="666"` (or `aspect-ratio`) to the `<video>` so the box is reserved even if the poster is slow. Keep `preload="metadata"` (or `none` with the poster; this would save the 54 KB).
6. [LOW] Logo: convert to SVG or a 72x72 WebP, and use one URL for the favicon and the img so the cache is shared.
7. [INFO] Get field data: rerun `pagespeed_check.py` once the PSI quota resets and check CrUX for INP, since TBT of 0 ms only suggests INP is fine.
