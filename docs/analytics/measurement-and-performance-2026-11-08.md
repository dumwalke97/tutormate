# Measurement readiness and homepage weight

Recorded 2026-11-08 after merge commit `d5f4e3a210505e743ea10a310888b90905048942` was on `main`. This does not wire analytics. Search Console and Apple campaign attribution were not available.

## Why click tracking is still off

The marketing pages do not load Google Analytics, Firebase Analytics, or any other new tracker. `www/scripts/store-cta.js` calls `gtag` only when some other script has already defined it, and it sends only `page_path` and `placement`. See `docs/analytics/app-store-clicks.md`.

What is actually in the repo:

- `www/app/index.html` copies `firebaseMeasurementId` from the Netlify env var `VITE_FIREBASE_MEASUREMENT_ID` into the Firebase config. It never imports `firebase-analytics` and never calls `getAnalytics` or `logEvent`. The measurement ID is not committed.
- The privacy policy names Google Firebase, Google Gemini, Apple, and Netlify. It does not name an analytics product, cookies used for measurement, or a consent choice.
- There is no cookie-consent UI.
- The policy says the product is for a general audience and is not directed at children under 13. The app is still a study tool that students use, and uploaded schoolwork is sent to Gemini. Adding a marketing tracker before the policy names it, and before a non-essential measurement choice exists, would go past what the site currently discloses.

Do not invent a measurement ID or an Apple provider token (`pt`). When both exist and the privacy policy covers them, the existing `app_store_click` event is the one to record. Until then the hook stays inert.

Production HTML also includes a script Netlify injects at `/.netlify/scripts/rum`. On 2026-11-08 the live homepage matched `www/index.html` from the merge commit except for that injected tag, which set `data-netlify-deploy-branch="main"` and `data-netlify-deploy-context="production"`. That script is not in this repo, and it is not the App Store click event. It is not a substitute for the measurement ID above.

## Homepage transfer, before the video change

Provenance:

- Page: `https://tutormate.ai/`
- Chrome: Google Chrome 156.0.8078.47, headless, `--window-size=1280,900`, `--virtual-time-budget=6000`, fresh user-data-dir, no click
- Log: Chrome `--log-net-log`, then the sum of `URL_REQUEST_JOB_BYTES_READ` `byte_count` values grouped by URL
- Separate full-file sizes: Python `urllib.request` GET, three samples each, from this environment on 2026-11-08

Bytes Chrome read on that idle load:

| URL | Bytes read |
|---|---:|
| `/Assets/TutorMateDemo.mp4` | 278,500 |
| `/` | 47,641 |
| `/Assets/TutorMateDemoPoster.jpg` | 22,722 |
| `/styles/tailwind.css` | 21,589 |
| `/Assets/TutorMateLogoTransparent.png` | 21,024 |
| `/fonts/nunito-800.woff2` | 16,508 |
| `/.netlify/scripts/rum` | 15,221 |
| `/scripts/store-cta.js` | 3,320 |

The mp4 file itself is 3,035,348 bytes. `preload="metadata"` still caused Chrome to read 278,500 bytes before play, which was larger than the HTML, CSS, font, poster, and logo combined. Full-file GETs of the mp4 from this network finished in 121–196 ms; that time is not a phone network. The byte count is the reason for the change.

After setting `preload="none"` and repeating the same Chrome netlog against the local page (`http://127.0.0.1:8765/`, same Chrome version and flags, no click), the mp4 URL was not requested. The poster, CSS, font, and logo still loaded. The video element keeps `src="/Assets/TutorMateDemo.mp4"` and the existing play button, so playback still uses that file.
