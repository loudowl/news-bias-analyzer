"""
Flask web server — serves the latest report at / and archived reports at /archive/<stem>.
Injects a paginated archive nav into every page.
"""

import math
from datetime import datetime
from pathlib import Path

from flask import Flask, abort, request

app = Flask(__name__)

ARCHIVE_DIR = Path(__file__).parent / "archive"
PAGE_SIZE = 10

_NAV_CSS = """
<style>
.archive-nav {
  max-width: 1100px;
  margin: 2rem auto;
  padding: 1.5rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
}
.archive-nav h3 {
  color: var(--accent);
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  margin-bottom: 1rem;
}
.archive-links {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.archive-link {
  background: var(--surface2);
  border: 1px solid var(--border);
  color: var(--muted);
  padding: 0.3rem 0.85rem;
  border-radius: 4px;
  text-decoration: none;
  font-size: 0.82rem;
  transition: border-color 0.15s, color 0.15s;
}
.archive-link:hover,
.archive-link.active {
  border-color: var(--accent);
  color: var(--accent);
}
.archive-pagination {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.82rem;
  margin-top: 0.25rem;
}
.page-btn {
  background: var(--surface2);
  border: 1px solid var(--border);
  color: var(--accent);
  padding: 0.3rem 0.85rem;
  border-radius: 4px;
  text-decoration: none;
}
.page-btn:hover { background: var(--bg); }
.page-info { color: var(--muted); }
</style>
"""


def _list_reports():
    if not ARCHIVE_DIR.exists():
        return []
    return sorted(ARCHIVE_DIR.glob("*.html"), reverse=True)


def _label(stem: str) -> str:
    try:
        dt = datetime.strptime(stem, "%Y-%m-%d_%H-%M")
        return dt.strftime("%b %d, %Y · %I:%M %p")
    except ValueError:
        return stem


def _inject_nav(html: str, current_stem: str, base_path: str, page: int) -> str:
    reports = _list_reports()
    if not reports:
        return html

    total_pages = max(1, math.ceil(len(reports) / PAGE_SIZE))
    page = max(1, min(page, total_pages))
    page_reports = reports[(page - 1) * PAGE_SIZE : page * PAGE_SIZE]

    links = []
    for r in page_reports:
        active = " active" if r.stem == current_stem else ""
        links.append(
            f'<a href="/archive/{r.stem}" class="archive-link{active}">{_label(r.stem)}</a>'
        )

    count = len(reports)
    prev_btn = (
        f'<a href="{base_path}?page={page - 1}" class="page-btn">← Newer</a>'
        if page > 1 else ""
    )
    next_btn = (
        f'<a href="{base_path}?page={page + 1}" class="page-btn">Older →</a>'
        if page < total_pages else ""
    )

    nav = (
        f'\n<div class="archive-nav">'
        f'<h3>Archive &mdash; {count} report{"s" if count != 1 else ""}</h3>'
        f'<div class="archive-links">{"".join(links)}</div>'
        f'<div class="archive-pagination">{prev_btn}'
        f'<span class="page-info">Page {page} of {total_pages}</span>'
        f'{next_btn}</div>'
        f'</div>\n'
    )

    return html.replace("</body>", _NAV_CSS + nav + "</body>", 1)


@app.route("/")
def index():
    reports = _list_reports()
    if not reports:
        return (
            "<p style='font-family:sans-serif;padding:2rem'>"
            "No reports yet — run <code>python main.py</code> to generate one.</p>"
        ), 404
    page = request.args.get("page", 1, type=int)
    html = reports[0].read_text(encoding="utf-8")
    return _inject_nav(html, reports[0].stem, "/", page)


@app.route("/archive/<stem>")
def archive_report(stem):
    path = ARCHIVE_DIR / f"{stem}.html"
    if not path.exists():
        abort(404)
    page = request.args.get("page", 1, type=int)
    html = path.read_text(encoding="utf-8")
    return _inject_nav(html, stem, f"/archive/{stem}", page)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
