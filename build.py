#!/usr/bin/env python3
"""
MTWW Site Builder
Reads JSON data files and generates static HTML pages.

Usage:
    python3 build.py              # Build all pages
    python3 build.py --show X     # Build one show page
    python3 build.py --check      # Data completeness report
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent
DATA = ROOT / "data"
OUTPUT = ROOT / "output"
TEMPLATES = ROOT / "templates"


def load_json(name):
    with open(DATA / name, "r") as f:
        return json.load(f)


def write_page(filename, html):
    OUTPUT.mkdir(exist_ok=True)
    path = OUTPUT / filename
    path.write_text(html, encoding="utf-8")
    print(f"  wrote {path}")


# ── HTML helpers ──────────────────────────────────────────────

def head(title, description=""):
    site = load_json("site.json")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — {site['name']}</title>
<meta name="description" content="{description or site['description']}">
<link rel="stylesheet" href="styles.css">
</head>
<body>
"""


def nav():
    site = load_json("site.json")
    links = "\n".join(
        f'    <a href="{item["href"]}">{item["label"]}</a>'
        for item in site["nav"]
    )
    return f"""<nav class="site-nav">
  <div class="nav-inner">
    <a href="index.html" class="nav-logo">{site['short_name']}</a>
    <div class="nav-links">
{links}
    </div>
  </div>
</nav>
"""


def footer():
    site = load_json("site.json")
    year = datetime.now().year
    return f"""<footer class="site-footer">
  <div class="footer-inner">
    <div class="footer-col">
      <p class="footer-name">{site['name']}</p>
      <p>Born from <a href="https://actorsgarden.com">The Actors Garden</a>, Oak Park, Illinois</p>
    </div>
    <div class="footer-col">
      <p><a href="mailto:{site['email']}">{site['email']}</a></p>
      <p>{site['phone']}</p>
    </div>
    <p class="footer-copy">&copy; {year} {site['name']}</p>
  </div>
</footer>
</body>
</html>
"""


def show_card(show):
    """Render a show as a card for the listing page."""
    meta_parts = []
    if show.get("runtime_minutes"):
        rt = show["runtime_minutes"]
        meta_parts.append(f"{rt} min")
    if show.get("cast_size"):
        meta_parts.append(f"{show['cast_size']}+ cast")
    if show.get("age_range"):
        meta_parts.append(show["age_range"])
    if show.get("song_count"):
        meta_parts.append(f"{show['song_count']} songs")

    meta_html = " &middot; ".join(meta_parts) if meta_parts else ""
    status_badge = ""
    if show["status"] == "needs_data":
        status_badge = '<span class="badge badge-draft">Coming Soon</span>'

    credits = []
    if show.get("music_by"):
        credits.append(f"Music by {show['music_by']}")
    if show.get("book_by"):
        credits.append(f"Book & Lyrics by {show['book_by']}")
    credits_html = "<br>".join(credits)

    return f"""<article class="show-card">
  <div class="show-card-body">
    <h3><a href="{show['id']}.html">{show['title']}</a> {status_badge}</h3>
    <p class="show-tagline">{show.get('tagline', '')}</p>
    <p class="show-credits">{credits_html}</p>
    <p class="show-meta">{meta_html}</p>
  </div>
</article>
"""


# ── Page builders ─────────────────────────────────────────────

def build_index():
    site = load_json("site.json")
    shows = load_json("shows.json")
    active = [s for s in shows if s.get("available_on_mtww")]

    cards = "\n".join(show_card(s) for s in active)

    html = head("Home") + nav() + f"""
<main>
  <section class="hero">
    <div class="hero-inner">
      <h1>{site['name']}</h1>
      <p class="hero-tagline">{site['tagline']}</p>
      <p class="hero-sub">{site['description']}</p>
      <a href="shows.html" class="btn btn-primary">Browse Our Shows</a>
      <a href="licensing.html" class="btn btn-secondary">How Licensing Works</a>
    </div>
  </section>

  <section class="section" id="featured">
    <h2>Our Shows</h2>
    <div class="show-grid">
{cards}
    </div>
  </section>

  <section class="section section-alt" id="why">
    <h2>Why MTWW?</h2>
    <div class="value-grid">
      <div class="value-card">
        <h3>Written for Young Performers</h3>
        <p>Not shortened adult shows. Every musical is originally written to get the most out of young actors, with age-appropriate content and roles designed for developing performers.</p>
      </div>
      <div class="value-card">
        <h3>Battle-Tested</h3>
        <p>Every show is workshopped, produced, and revised at The Actors Garden before being offered for licensing. What you get has been proven on stage with real kids.</p>
      </div>
      <div class="value-card">
        <h3>Everything Included</h3>
        <p>$299 gets you the complete package: script, piano/vocal score, lead sheets, and backing tracks. No rental fees, no per-script charges, no surprises.</p>
      </div>
    </div>
  </section>
</main>
""" + footer()
    write_page("index.html", html)


def build_shows():
    shows = load_json("shows.json")
    active = [s for s in shows if s.get("available_on_mtww")]
    other = [s for s in shows if not s.get("available_on_mtww")]

    active_cards = "\n".join(show_card(s) for s in active)
    other_cards = "\n".join(show_card(s) for s in other)

    other_section = ""
    if other:
        other_section = f"""
  <section class="section section-alt" id="other-works">
    <h2>Other Works by Dave Hudson</h2>
    <p>These shows are licensed through other publishers but are part of Dave Hudson's catalog.</p>
    <div class="show-grid">
{other_cards}
    </div>
  </section>
"""

    html = head("Shows", "Browse our catalog of original musicals for schools and youth programs.") + nav() + f"""
<main>
  <section class="section" id="mtww-shows">
    <h2>MTWW Shows</h2>
    <p>Available for licensing directly from Musical Theatre Worldwide.</p>
    <div class="show-grid">
{active_cards}
    </div>
  </section>
{other_section}
</main>
""" + footer()
    write_page("shows.html", html)


def build_show_page(show):
    """Build an individual show detail page."""
    sections = []

    # Synopsis
    if show.get("synopsis"):
        sections.append(f"""
  <section class="section">
    <h2>About the Show</h2>
    <p>{show['synopsis']}</p>
  </section>""")

    # Details table
    rows = []
    if show.get("runtime_minutes"):
        inter = " + intermission" if show.get("has_intermission") else ""
        rows.append(f"<tr><th>Runtime</th><td>{show['runtime_minutes']} minutes{inter}</td></tr>")
    if show.get("age_range"):
        rows.append(f"<tr><th>Recommended Age</th><td>{show['age_range']}</td></tr>")
    if show.get("cast_size"):
        rows.append(f"<tr><th>Cast Size</th><td>{show['cast_size']}+ roles</td></tr>")
    if show.get("cast_notes"):
        rows.append(f"<tr><th>Cast Notes</th><td>{show['cast_notes']}</td></tr>")
    if show.get("song_count"):
        rows.append(f"<tr><th>Songs</th><td>{show['song_count']}</td></tr>")
    if show.get("source_material"):
        rows.append(f"<tr><th>Based On</th><td>{show['source_material']}</td></tr>")

    # Credits
    credits = []
    if show.get("book_by"):
        credits.append(f"<tr><th>Book & Lyrics</th><td>{show['book_by']}</td></tr>")
    if show.get("music_by"):
        credits.append(f"<tr><th>Music</th><td>{show['music_by']}</td></tr>")

    if rows or credits:
        all_rows = "\n".join(credits + rows)
        sections.append(f"""
  <section class="section">
    <h2>Details</h2>
    <table class="detail-table">
{all_rows}
    </table>
  </section>""")

    # Licensing
    if show.get("licensing_price"):
        items = "\n".join(f"      <li>{item}</li>" for item in show.get("licensing_includes", []))
        sections.append(f"""
  <section class="section section-alt" id="licensing">
    <h2>Licensing</h2>
    <div class="licensing-box">
      <p class="licensing-price">${show['licensing_price']}</p>
      <p>{show.get('licensing_notes', '')}</p>
      <ul>
{items}
      </ul>
      <a href="contact.html" class="btn btn-primary">Request a Perusal Copy</a>
    </div>
  </section>""")

    body = "\n".join(sections)
    status_note = ""
    if show["status"] == "needs_data":
        status_note = '<p class="notice">Full details coming soon. Contact us for more information.</p>'

    html = head(show["title"], show.get("tagline", "")) + nav() + f"""
<main>
  <section class="show-hero">
    <h1>{show['title']}</h1>
    <p class="show-hero-tagline">{show.get('tagline', '')}</p>
    {status_note}
  </section>
{body}
</main>
""" + footer()
    write_page(f"{show['id']}.html", html)


def build_about():
    people = load_json("people.json")
    founders = [p for p in people if p.get("is_founder")]
    collaborators = [p for p in people if not p.get("is_founder")]

    def person_card(p):
        bio = p.get("bio") or "<em>Bio coming soon.</em>"
        awards = ""
        if p.get("awards"):
            items = "\n".join(f"        <li>{a}</li>" for a in p["awards"])
            awards = f"\n      <ul class='award-list'>\n{items}\n      </ul>"
        return f"""    <div class="person-card">
      <h3>{p['name']}</h3>
      <p class="person-role">{p['role']}</p>
      <p>{bio}</p>{awards}
    </div>"""

    founder_html = "\n".join(person_card(p) for p in founders)
    collab_html = "\n".join(person_card(p) for p in collaborators)

    html = head("About MTWW", "The story behind Musical Theatre Worldwide.") + nav() + f"""
<main>
  <section class="section">
    <h2>About Musical Theatre Worldwide</h2>
    <p>Musical Theatre Worldwide was born from The Actors Garden in Oak Park, Illinois. Artistic Director GiGi Hudson identified a gap: existing "Junior" shows, though fun, weren't originally written for youth and were often just shortened versions of adult shows. Playwright Dave Hudson began crafting original works specifically designed for young performers.</p>
    <p>Every MTWW show is workshopped, produced, and revised at The Actors Garden, leading to polished, perfected performances before being offered for licensing.</p>
  </section>

  <section class="section" id="founders">
    <h2>Founders</h2>
    <div class="people-grid">
{founder_html}
    </div>
  </section>

  <section class="section section-alt" id="collaborators">
    <h2>Collaborators</h2>
    <div class="people-grid">
{collab_html}
    </div>
  </section>
</main>
""" + footer()
    write_page("about.html", html)


def build_licensing():
    site = load_json("site.json")
    items = "\n".join(f"    <li>{item}</li>" for item in site["licensing_includes_default"])

    html = head("Licensing", "How to license a MTWW musical for your school or program.") + nav() + f"""
<main>
  <section class="section">
    <h2>How Licensing Works</h2>
    <p>Licensing a Musical Theatre Worldwide show is simple and affordable.</p>

    <div class="licensing-box">
      <p class="licensing-price">${site['licensing_default_price']}</p>
      <p>Each licensed show comes complete with everything you need:</p>
      <ul>
{items}
      </ul>
    </div>
  </section>

  <section class="section section-alt">
    <h2>Getting Started</h2>
    <ol class="steps-list">
      <li><strong>Browse our shows</strong> — Find a musical that fits your program.</li>
      <li><strong>Request a perusal copy</strong> — Read the script before you commit.</li>
      <li><strong>License the show</strong> — Pay once and get everything you need.</li>
      <li><strong>Produce it</strong> — Rehearse and perform with full materials.</li>
    </ol>
    <a href="contact.html" class="btn btn-primary">Request a Perusal Copy</a>
  </section>

  <section class="section">
    <h2>Frequently Asked Questions</h2>
    <dl class="faq">
      <dt>What's included in the licensing fee?</dt>
      <dd>Script, piano/vocal score, vocal lead sheets, and backing tracks — all as printable PDFs and downloadable audio. No rental fees or per-script charges.</dd>

      <dt>Can we modify the show for our program?</dt>
      <dd>Contact us to discuss. Our shows are designed to be flexible with cast sizes and we're happy to work with you.</dd>

      <dt>How long does the license last?</dt>
      <dd>License terms vary by show. Most cover unlimited performances within a defined period. See individual show pages for details.</dd>

      <dt>Do you offer discounts for multiple shows?</dt>
      <dd>Contact us — we're happy to discuss packages for programs licensing more than one show.</dd>
    </dl>
  </section>
</main>
""" + footer()
    write_page("licensing.html", html)


def build_contact():
    site = load_json("site.json")

    html = head("Contact", "Get in touch with Musical Theatre Worldwide.") + nav() + f"""
<main>
  <section class="section">
    <h2>Get in Touch</h2>
    <div class="contact-grid">
      <div class="contact-card">
        <h3>General Inquiries</h3>
        <p><a href="mailto:{site['email']}">{site['email']}</a></p>
        <p>{site['phone']}</p>
      </div>
      <div class="contact-card">
        <h3>Request a Perusal Copy</h3>
        <p>Want to read a script before licensing? Email us with the show title and your organization name, and we'll send you a perusal copy.</p>
        <a href="mailto:{site['email']}?subject=Perusal%20Request" class="btn btn-primary">Request a Perusal</a>
      </div>
    </div>
  </section>
</main>
""" + footer()
    write_page("contact.html", html)


# ── Data check ────────────────────────────────────────────────

def check_data():
    """Report data completeness for all shows."""
    shows = load_json("shows.json")
    key_fields = [
        "synopsis", "runtime_minutes", "age_range", "cast_size",
        "song_count", "licensing_price", "music_by", "premiere_year"
    ]

    print("\n  DATA COMPLETENESS REPORT")
    print("  " + "=" * 50)

    for show in shows:
        missing = [f for f in key_fields if not show.get(f)]
        total = len(key_fields)
        filled = total - len(missing)
        pct = int(filled / total * 100)
        bar = "#" * (filled * 3) + "." * ((total - filled) * 3)

        status = show.get("status", "?")
        print(f"\n  {show['title']}")
        print(f"  [{bar}] {pct}% ({filled}/{total})")
        print(f"  Status: {status}")
        if missing:
            print(f"  Missing: {', '.join(missing)}")

    print("\n  " + "=" * 50)
    all_missing = sum(1 for s in shows if s["status"] == "needs_data")
    print(f"  {len(shows)} shows total, {all_missing} need data from Dave\n")


# ── Main ──────────────────────────────────────────────────────

def build_all():
    print("\nBuilding MTWW site...")
    shows = load_json("shows.json")

    build_index()
    build_shows()
    build_about()
    build_licensing()
    build_contact()

    for show in shows:
        build_show_page(show)

    print(f"\nDone. {len(shows)} show pages + 5 site pages → output/\n")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check_data()
    elif "--show" in sys.argv:
        idx = sys.argv.index("--show")
        show_id = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else None
        if show_id:
            shows = load_json("shows.json")
            match = [s for s in shows if s["id"] == show_id]
            if match:
                build_show_page(match[0])
            else:
                print(f"No show with id '{show_id}'")
        else:
            print("Usage: python3 build.py --show <show-id>")
    else:
        build_all()
