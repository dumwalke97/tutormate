#!/usr/bin/env python3
"""Static checks for marketing routes, metadata, internal links, and the iOS CTA.

No network. Run after `npm run build:pages` so generated HTML and sitemap match.
"""
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[2]
WWW = ROOT / "www"
SITE = "https://tutormate.ai"
APP_STORE = "https://apps.apple.com/app/id6793738685"

INDEXABLE = [
    "/",
    "/homework-help/",
    "/quiz-generator/",
    "/vs/photomath/",
    "/about/",
    "/privacy/",
    "/algebra/",
    "/biology/",
    "/written-answers/",
]
GUIDES = ["/algebra/", "/biology/", "/written-answers/"]
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

failures = []


def check(condition, message):
    if not condition:
        failures.append(message)


def page_file(path):
    if path == "/":
        return WWW / "index.html"
    return WWW / path.strip("/") / "index.html"


def read(path):
    file = page_file(path)
    check(file.is_file(), f"missing page file for {path}")
    return file.read_text(encoding="utf-8") if file.is_file() else ""


pages = {path: read(path) for path in INDEXABLE}

for path, html in pages.items():
    canonical = f"{SITE}{path}"
    check(f'<link rel="canonical" href="{canonical}">' in html, f"{path} canonical")
    check("<title>" in html and "</title>" in html, f"{path} title")
    title = re.search(r"<title>(.*?)</title>", html, re.S)
    check(bool(title and title.group(1).strip()), f"{path} empty title")
    check('name="description"' in html, f"{path} description")
    check('name="apple-itunes-app" content="app-id=6793738685"' in html, f"{path} smart banner")
    check("application/ld+json" in html, f"{path} json-ld")
    if path != "/privacy/":
        check('href="/app/"' in html, f"{path} keeps a browser link")
    check("pt=" not in html, f"{path} must not invent an Apple provider token")
    check("gtag/js" not in html and "googletagmanager.com" not in html, f"{path} new tracker")

# Homepage keeps the browser CTA ahead of the App Store CTA in DOM order.
home = pages["/"]
hero = home.split('class="cta-row mt-8"', 1)[-1].split("</div>", 1)[0]
check('data-cta="browser"' in hero and 'data-placement="hero"' in hero, "homepage hero CTAs")
check(hero.find('data-cta="browser"') < hero.find('data-placement="hero"'), "desktop DOM keeps browser before App Store")
check('id="ios-app-link"' in home, "homepage keeps the existing iOS link id")
for guide in GUIDES:
    check(f'href="{guide}"' in home, f"homepage links to {guide}")
check("Educational illustration" not in home or "captured TutorMate response" in home, "homepage labels examples as authored")

for guide in GUIDES:
    html = pages[guide]
    flat = re.sub(r"\s+", " ", html.lower())
    check("Educational illustration" in html, f"{guide} labels the example")
    check("not a screenshot" in flat, f"{guide} denies a fake screenshot")
    check(APP_STORE in html and 'data-placement="section"' in html, f"{guide} section App Store link")
    check('data-placement="nav"' in html and 'data-placement="ios-sticky"' in html, f"{guide} nav and sticky placements")
    check('src="/scripts/store-cta.js"' in html, f"{guide} click hook")
    check('href="/homework-help/"' in html or 'href="/quiz-generator/"' in html, f"{guide} links to a core workflow page")
    for other in GUIDES:
        if other != guide:
            check(f'href="{other}"' in html, f"{guide} links to {other}")
    check("testimonial" not in flat or "not a screenshot, a testimonial" in flat, f"{guide} has no testimonial claim")
    check("5.0" not in html and "stars" not in flat, f"{guide} has no rating claim")
    check("$4.95" in html and "$49" in html, f"{guide} keeps the real price")

algebra = pages["/algebra/"]
check("x = 7" in algebra and "x = 17/3" in algebra, "algebra example keeps both results")
check("3(7 - 2) = 15" in algebra or "3(7 - 2) = 3(5) = 15" in algebra, "algebra check step")
check("within 0.01" in algebra, "algebra states the numeric tolerance")

biology = pages["/biology/"]
check("thylakoid membrane" in biology.lower(), "biology light reactions location")
check("chloroplast" in biology.lower() and "mitochondri" in biology.lower(), "biology organelle distinction")
check("10th Grade Biology Photosynthesis" in biology, "biology cites the real quiz placeholder")
check("exactly four" in biology, "biology states the four-choice quiz shape")

written = pages["/written-answers/"]
check("primary source" in written.lower(), "written-answer example")
check("secondary source" in written.lower(), "written-answer correction")
check("within 0.01" in written, "written page distinguishes numeric matching")

# Cross links from the older money pages.
check('href="/algebra/"' in pages["/homework-help/"], "homework-help links to algebra")
check('href="/biology/"' in pages["/quiz-generator/"], "quiz generator links to biology")
check('href="/written-answers/"' in pages["/vs/photomath/"], "comparison links to written answers")

llms = (WWW / "llms.txt").read_text(encoding="utf-8")
for guide in GUIDES:
    check(f"{SITE}{guide}" in llms, f"llms.txt lists {guide}")

robots = (WWW / "robots.txt").read_text(encoding="utf-8")
check("Sitemap: https://tutormate.ai/sitemap.xml" in robots, "robots sitemap")

sitemap = ET.parse(WWW / "sitemap.xml")
locs = sorted(node.text for node in sitemap.findall("sm:url/sm:loc", NS))
expected = sorted(f"{SITE}{path}" for path in INDEXABLE)
check(locs == expected, f"sitemap URLs {locs} != {expected}")

css = (ROOT / "src" / "tailwind.css").read_text(encoding="utf-8")
check("html.is-ios .cta-row .btn-store" in css and "order: -1" in css, "iOS CSS promotes the App Store button")
check(".nav-browser-btn" in css, "iOS CSS keeps a browser control")
built_css = (WWW / "styles" / "tailwind.css").read_text(encoding="utf-8")
inline_rule = built_css.find("html.is-ios .nav-browser-text{display:inline}")
narrow_rule = built_css.find("max-width:389px")
check(inline_rule > 0 and narrow_rule > inline_rule, "narrow iOS nav rule overrides the wider iOS nav link")

hook = (WWW / "scripts" / "store-cta.js").read_text(encoding="utf-8")
check("page_path" in hook and "placement" in hook, "click hook fields")
check("tutormate:app-store-click" in hook, "click hook event name")
check("homework" not in hook.split("docs/analytics", 1)[-1] or "does not read" in hook, "hook does not describe collecting homework")
check("innerText" not in hook and "textContent" not in hook, "hook does not read page text")
check("pt=" not in hook, "hook does not invent a provider token")
check("googletagmanager" not in hook, "hook does not load a tracker")

app = (WWW / "app" / "index.html").read_text(encoding="utf-8", errors="replace")
check("firebase-analytics" not in app, "app still has no analytics SDK; the doc must not claim otherwise")
check("10th Grade Biology Photosynthesis" in app, "biology page stays tied to the product placeholder")

doc = (ROOT / "docs" / "analytics" / "app-store-clicks.md").read_text(encoding="utf-8")
check("VITE_FIREBASE_MEASUREMENT_ID" in doc, "analytics doc names the existing env var")
check("does not claim that clicks are being recorded" in doc, "analytics doc does not claim tracking works")
check("pt" in doc and "PROVIDER_TOKEN" in doc, "analytics doc explains the missing provider token")

if failures:
    print(f"{len(failures)} check(s) failed:")
    for item in failures:
        print(f"  - {item}")
    sys.exit(1)

print(f"ok: {len(INDEXABLE)} indexable pages, sitemap, CTA hook, and guide examples")
