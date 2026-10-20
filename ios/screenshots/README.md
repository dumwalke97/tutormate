# App Store screenshots

`template.html` holds all eight iPhone frames; `generate.mjs` renders each one
with headless Chrome and writes it to `out/`.

```bash
node ios/screenshots/generate.mjs
```

No npm dependencies. It needs Google Chrome (or Chromium / Edge) installed.

## Size

Every frame renders at **1320x2868**, the 6.9" iPhone size Apple has required as
the primary iPhone screenshot since 2025. The set that is live on the listing
today was exported at 1242x2688 (the old 6.5" spec) and gets upscaled, which is
why it looks soft on current devices. Do not change `WIDTH` / `HEIGHT` in
`generate.mjs` without checking Apple's current spec.

## Slot order

The frames render in the order they appear in `template.html`, which is the
order they should be uploaded in App Store Connect:

| Slot | File | Job |
|---|---|---|
| 1 | `01_snap_to_quiz` | Split worksheet-to-quiz. Slot 1 does most of the conversion work, so it shows the product working rather than an empty home screen. |
| 2 | `02_check_homework` | Homework checking with explanations. |
| 3 | `03_social_proof` | The real 5.0 rating and the review line "This is a game changing study aid!" |
| 4 | `04_study_not_copy` | Practice with instant feedback, not handed-over answers. |
| 5 | `05_any_topic` | Topic quizzes, 5 to 50 questions. |
| 6 | `06_track_progress` | Results, review, retake. |
| 7 | `07_study_sets` | Saved quizzes in folders. |
| 8 | `08_start_free` | Closing CTA: "Start free. Your first 10 quizzes are on us." |

Slots 1, 3 and 8 are the ones the 2026-10-19 ASO audit called for
(`docs/aso/aso-audit-2026-10-19.md`, opportunities 6, 7 and 8).

## Editing

Frames are plain HTML and CSS. Each is a `<section class="frame"
data-name="NN_slug">`; `generate.mjs` discovers them from that attribute, so
adding a frame means adding a section and nothing else. Open `template.html`
directly in a browser to preview one with `?frame=03`.

The device screens are rebuilt in HTML to match the app's own styling rather
than captured from a simulator, so copy and state can be set per frame. If the
app's UI changes materially, update the frames here to match.
