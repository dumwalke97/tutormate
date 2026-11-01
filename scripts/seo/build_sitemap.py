#!/usr/bin/env python3
"""Builds sitemap.xml from the indexable pages actually present in www/.

Driven by the filesystem rather than a hand-kept list, so a new page cannot be
left out and a deleted one cannot linger as a 404 in the sitemap.
"""
import datetime
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
WWW = ROOT / "www"
SITE = "https://tutormate.ai"

# Relative priority within the site. Absent pages are skipped; pages found but
# not listed here fall back to 0.5 so nothing is silently dropped.
PRIORITY = {
    "/": ("1.0", "weekly"),
    "/homework-help/": ("0.9", "monthly"),
    "/quiz-generator/": ("0.9", "monthly"),
    "/vs/photomath/": ("0.8", "monthly"),
    "/about/": ("0.7", "monthly"),
    "/privacy/": ("0.3", "yearly"),
}


def url_path(html: pathlib.Path) -> str:
    rel = html.relative_to(WWW).parent.as_posix()
    return "/" if rel == "." else f"/{rel}/"


def is_indexable(html: pathlib.Path) -> bool:
    text = html.read_text(errors="replace")
    return not re.search(r'<meta\s+name="robots"[^>]*noindex', text, re.I)


entries = []
for html in sorted(WWW.rglob("index.html")):
    path = url_path(html)
    if not is_indexable(html):
        print(f"  skipped (noindex): {path}")
        continue
    priority, freq = PRIORITY.get(path, ("0.5", "monthly"))
    lastmod = datetime.date.fromtimestamp(html.stat().st_mtime).isoformat()
    entries.append((path, lastmod, freq, priority))

body = "\n".join(
    f"""  <url>
    <loc>{SITE}{path}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{priority}</priority>
  </url>"""
    for path, lastmod, freq, priority in entries
)

(WWW / "sitemap.xml").write_text(
    f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{body}
</urlset>
"""
)
print(f"sitemap.xml written with {len(entries)} URLs")
for path, *_ in entries:
    print(f"  {path}")
