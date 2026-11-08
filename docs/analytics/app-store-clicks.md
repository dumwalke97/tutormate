# App Store click measurement

This is the external setup still required. The website does not claim that clicks are being recorded. The privacy and performance notes for 2026-11-08 are in `docs/analytics/measurement-and-performance-2026-11-08.md`. Do not load a tracker from this hook until that note's conditions are met.

## What the site does now

The App Store download is the primary button in the nav, the homepage hero, and the section at the bottom of each guide, on desktop as well as on iPhone. The browser link stays on the page as the secondary action. A short bar is added only on iPhone and iPad. Marketing pages load `/scripts/store-cta.js`. When someone clicks an App Store link that has a `data-placement` attribute, the script:

1. Dispatches a `tutormate:app-store-click` event on `document`.
2. If `window.gtag` is already a function, calls it with event name `app_store_click`.

The only fields sent are:

- `page_path` — the path of the current page, such as `/algebra/`
- `placement` — `nav`, `hero`, `section`, or `ios-sticky`

The script does not read homework, quiz text, form fields, or any other page content. It does not load Google, Firebase, or any other analytics script. Dismissing the iPhone bar stores `tutormate-ios-bar-dismissed=1` in `sessionStorage` only, so the bar stays closed for that tab.

## Why this is not live analytics

`www/app/index.html` requests `/.netlify/functions/config`, which can return `firebaseMeasurementId` from the Netlify environment variable `VITE_FIREBASE_MEASUREMENT_ID`. That value is copied into the Firebase config object. The app never imports `firebase-analytics`, and it never calls `getAnalytics` or `logEvent`. Marketing pages do not call the config function at all.

There is no Plausible, PostHog, or other analytics snippet on the marketing pages. No Apple provider token (`pt`) appears anywhere in this repository.

## To record the clicks in GA4 or Firebase

Use the measurement ID that is already in Netlify as `VITE_FIREBASE_MEASUREMENT_ID`. Do not invent one. Confirm in Firebase console that the ID belongs to this TutorMate project and that the web stream's domain includes `tutormate.ai`.

Then load that project's analytics on the marketing pages only, and map the existing event:

- Event name: `app_store_click`
- Parameters: `page_path`, `placement`

Leave homework text out of the event. A listener for `tutormate:app-store-click` is enough if you would rather forward the event from your own snippet:

```js
document.addEventListener('tutormate:app-store-click', function (event) {
  // event.detail.page_path and event.detail.placement only
});
```

Until that snippet exists, `gtag` is undefined and the call is skipped. The custom event still fires for anything you attach later.

## Apple campaign links

Campaign attribution on the App Store requires a provider token from App Store Connect (Analytics → Campaigns). The link shape is:

`https://apps.apple.com/app/id6793738685?pt=PROVIDER_TOKEN&ct=CAMPAIGN&mt=8`

`pt` is required. `ct` is the campaign name you choose, and `mt=8` means an app. This repo does not contain a provider token, so the links stay as:

`https://apps.apple.com/app/id6793738685`

That URL was checked on 2026-11-08. It redirects to `https://apps.apple.com/us/app/tutormate-ai-homework-helper/id6793738685`. Do not add `pt`, `ct`, or an affiliate token until the real provider token is copied from App Store Connect into a public config value in this repo.

The Smart App Banner remains `app-id=6793738685` with no campaign parameters. Apple can still report Smart App Banner installs separately in App Analytics. That reporting is Apple's, and it is not something this repository can confirm.
