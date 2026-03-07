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
import shutil
import html as html_mod
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent
DATA = ROOT / "data"
OUTPUT = ROOT / "output"
ASSETS = ROOT / "assets"


def load_json(name):
    with open(DATA / name, "r") as f:
        return json.load(f)


def write_page(filename, content):
    OUTPUT.mkdir(exist_ok=True)
    path = OUTPUT / filename
    path.write_text(content, encoding="utf-8")
    print(f"  wrote {path}")


def esc(text):
    """Escape HTML entities in text."""
    return html_mod.escape(str(text)) if text else ""


# ── HTML helpers ──────────────────────────────────────────────

def head(title, description="", og_image="", canonical_path="", schema=None):
    site = load_json("site.json")
    desc = description or site['description']
    base_url = site['url'].rstrip('/')
    canonical = f'{base_url}/{canonical_path}' if canonical_path else base_url

    og_tags = f"""<meta property="og:title" content="{esc(title)} — {esc(site['name'])}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="{esc(site['name'])}">"""

    if og_image:
        og_tags += f'\n<meta property="og:image" content="{og_image}">'

    schema_block = ""
    if schema:
        schema_json = json.dumps(schema, indent=2)
        schema_block = f'\n<script type="application/ld+json">\n{schema_json}\n</script>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} — {esc(site['name'])}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canonical}">
{og_tags}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Source+Sans+3:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="styles.css">{schema_block}
</head>
<body>
<a href="#main" class="skip-link">Skip to content</a>
"""


def nav(active=""):
    site = load_json("site.json")
    links = []
    for item in site["nav"]:
        cls = ' class="nav-active"' if item["label"].lower() == active.lower() else ""
        links.append(f'    <a href="{item["href"]}"{cls}>{item["label"]}</a>')
    links_html = "\n".join(links)

    return f"""<nav class="site-nav" aria-label="Main navigation">
  <div class="nav-inner">
    <a href="index.html" class="nav-logo">{site['short_name']}</a>
    <button class="nav-toggle" aria-expanded="false" aria-controls="nav-menu" aria-label="Toggle navigation">
      <span class="nav-toggle-bar"></span>
      <span class="nav-toggle-bar"></span>
      <span class="nav-toggle-bar"></span>
    </button>
    <div class="nav-links" id="nav-menu">
{links_html}
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
      <p>Born from <a href="https://theactorsgarden.com">The Actors Garden</a>, Oak Park, Illinois</p>
      <p class="footer-credential">Two-time Richard Rodgers Award winners</p>
    </div>
    <div class="footer-col">
      <p><a href="mailto:{site['email']}">{site['email']}</a></p>
      <p>{site['phone']}</p>
    </div>
    <p class="footer-copy">&copy; {year} {site['name']}</p>
  </div>
</footer>
<script>
// Mobile nav toggle
document.addEventListener('DOMContentLoaded', function() {{
  var toggle = document.querySelector('.nav-toggle');
  var menu = document.getElementById('nav-menu');
  if (toggle && menu) {{
    toggle.addEventListener('click', function() {{
      var expanded = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', !expanded);
      menu.classList.toggle('nav-open');
    }});
  }}

  // FAQ accordion
  var dts = document.querySelectorAll('.faq dt');
  dts.forEach(function(dt) {{
    dt.addEventListener('click', function() {{
      var dd = dt.nextElementSibling;
      var isOpen = dt.classList.contains('faq-open');
      // Close all
      dts.forEach(function(d) {{
        d.classList.remove('faq-open');
        if (d.nextElementSibling) d.nextElementSibling.classList.remove('faq-open');
      }});
      // Toggle this one
      if (!isOpen) {{
        dt.classList.add('faq-open');
        if (dd) dd.classList.add('faq-open');
      }}
    }});
  }});
}});
</script>
</body>
</html>
"""


def show_card(show):
    """Render a show as a comparison-ready card for listing pages."""
    # Status badges
    status_badge = ""
    if show["status"] == "needs_data":
        status_badge = '<span class="badge badge-draft">Coming Soon</span>'
    elif show["status"] == "external_license":
        status_badge = '<span class="badge badge-external">Beat by Beat Press</span>'

    # Difficulty badge
    difficulty = show.get('difficulty', '')
    diff_badge = f'<span class="badge badge-diff">{difficulty.replace("-", " ").title()}</span>' if difficulty else ""

    # Structured metadata
    specs_html = ""
    if show.get("available_on_mtww") and show["status"] != "needs_data":
        spec_pairs = []
        if show.get("age_range"):
            spec_pairs.append(("Ages", show["age_range"]))
        if show.get("cast_size"):
            spec_pairs.append(("Cast", f"{show['cast_size']}+ roles"))
        if show.get("runtime_minutes"):
            inter = " + int." if show.get("has_intermission") else ""
            spec_pairs.append(("Runtime", f"{show['runtime_minutes']} min{inter}"))
        if show.get("difficulty"):
            spec_pairs.append(("Level", show["difficulty"].replace("-", " ").title()))

        if spec_pairs:
            items = "\n".join(
                f'        <dt>{label}</dt><dd>{value}</dd>'
                for label, value in spec_pairs
            )
            specs_html = f'    <dl class="show-specs">\n{items}\n    </dl>'

    # Curriculum tags
    tags_html = ""
    themes = show.get("themes", [])
    if themes and show.get("available_on_mtww"):
        tag_items = "\n".join(f'      <span class="show-tag">{t}</span>' for t in themes[:4])
        tags_html = f'    <div class="show-tags">\n{tag_items}\n    </div>'

    # Credits line
    credits = []
    if show.get("music_by"):
        credits.append(f"Music by {show['music_by']}")
    credits_html = " &middot; ".join(credits)

    # Link — external shows link out
    href = show.get("external_url", f"{show['id']}.html")
    target = ' target="_blank" rel="noopener"' if show.get("external_url") else ""

    tagline = show.get('tagline', '')

    # Card footer with price and CTA
    footer_html = ""
    if show.get("licensing_price") and show.get("available_on_mtww"):
        footer_html = f"""    <div class="show-card-footer">
      <span class="show-price">${show['licensing_price']}</span>
      <a href="{href}" class="show-card-cta">View details &rarr;</a>
    </div>"""

    return f"""<article class="show-card" data-age="{show.get('min_age', '')}" data-cast="{show.get('cast_size', '')}" data-runtime="{show.get('runtime_minutes', '')}" data-status="{show['status']}" data-difficulty="{show.get('difficulty', '')}" data-themes="{','.join(show.get('themes', []))}">
  <div class="show-card-body">
    <h3><a href="{href}"{target}>{show['title']}</a> {status_badge} {diff_badge}</h3>
    <p class="show-tagline">{tagline}</p>
    <p class="show-credits">{credits_html}</p>
{specs_html}
{tags_html}
{footer_html}
  </div>
</article>
"""


# ── Schema.org helpers ────────────────────────────────────────

def org_schema():
    site = load_json("site.json")
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": site["name"],
        "url": site["url"],
        "description": site["description"],
        "telephone": site["phone"],
        "email": site["email"],
        "foundingDate": str(site.get("founded_year", "")),
        "foundingLocation": {
            "@type": "Place",
            "name": site["origin"]
        }
    }


def show_schema(show):
    site = load_json("site.json")
    schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": f"{show['title']} — Musical for Schools",
        "description": show.get("synopsis") or show.get("tagline", ""),
        "brand": {"@type": "Brand", "name": site["name"]},
        "url": f"{site['url']}/{show['id']}.html",
        "category": "Musical Theater Licensing",
    }
    if show.get("licensing_price"):
        schema["offers"] = {
            "@type": "Offer",
            "price": show["licensing_price"],
            "priceCurrency": "USD",
            "availability": "https://schema.org/InStock",
            "description": show.get("licensing_notes", "")
        }
    return schema


def faq_schema(faq_items):
    if not faq_items:
        return None
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": item["q"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": item["a"]
                }
            }
            for item in faq_items
        ]
    }


# ── Page builders ─────────────────────────────────────────────

def build_index():
    site = load_json("site.json")
    shows = load_json("shows.json")
    active = [s for s in shows if s.get("available_on_mtww") and s["status"] == "active"]

    cards = "\n".join(show_card(s) for s in active)

    # Kit items summary
    kit_items = "\n".join(
        f'        <li><span class="kit-check" aria-hidden="true">&#10003;</span> {item}</li>'
        for item in site["licensing_includes_default"]
    )

    # Quick browse cards
    browse_cards = """
      <a href="shows.html#elementary" class="browse-card">
        <span class="browse-card-icon" aria-hidden="true">&#127891;</span>
        <span class="browse-card-label">Elementary</span>
        <span class="browse-card-detail">3rd grade and up</span>
      </a>
      <a href="shows.html#middle" class="browse-card">
        <span class="browse-card-icon" aria-hidden="true">&#127917;</span>
        <span class="browse-card-label">Middle School+</span>
        <span class="browse-card-detail">7th grade and up</span>
      </a>
      <a href="shows.html#literature" class="browse-card">
        <span class="browse-card-icon" aria-hidden="true">&#128218;</span>
        <span class="browse-card-label">Literary Adaptations</span>
        <span class="browse-card-detail">Kipling, Twain, mythology</span>
      </a>
      <a href="shows.html#large-cast" class="browse-card">
        <span class="browse-card-icon" aria-hidden="true">&#127917;</span>
        <span class="browse-card-label">Large Cast</span>
        <span class="browse-card-detail">25+ roles + chorus</span>
      </a>"""

    schema = org_schema()

    html = head(
        "Home",
        "Original musicals for schools and youth programs. Written for young performers, tested on stage. Scripts, scores, and backing tracks from $299.",
        canonical_path="",
        schema=schema
    ) + nav("Home") + f"""
<main id="main">
  <section class="hero">
    <div class="hero-inner">
      <h1>Find the Right Musical for Your Students</h1>
      <p class="hero-sub">Original musicals written for young performers — tested on stage with real kids at The Actors Garden over 30 years. Complete Production Kits from ${site['licensing_default_price']}.</p>
      <p class="hero-credential">By two-time Richard Rodgers Award winner Dave Hudson</p>
      <div class="hero-ctas">
        <a href="shows.html" class="btn btn-primary">Browse Shows</a>
        <a href="mailto:{site['email']}?subject=Free%20Perusal%20Request" class="btn btn-secondary">Read a Script Free</a>
      </div>
    </div>
  </section>

  <section class="section browse-section" id="browse">
    <h2>Find Shows By</h2>
    <div class="browse-grid">
{browse_cards}
    </div>
  </section>

  <section class="section section-alt" id="featured">
    <h2>Our Shows</h2>
    <p>Each show comes as a complete Production Kit with script, score, lead sheets, backing tracks, and video rights.</p>
    <div class="show-grid">
{cards}
    </div>
    <p class="section-cta"><a href="shows.html">View all shows &rarr;</a></p>
  </section>

  <section class="section" id="production-kit">
    <h2>What You Get: Complete Production Kits</h2>
    <div class="kit-summary">
      <ul class="kit-summary-list">
{kit_items}
      </ul>
      <div class="kit-summary-cta">
        <p class="licensing-price">From ${site['licensing_default_price']}</p>
        <p style="margin-bottom: var(--space-sm); color: var(--color-text-light);">One flat fee. No rentals. No returns.</p>
        <a href="licensing.html" class="btn btn-outline">Full details &rarr;</a>
      </div>
    </div>
  </section>

  <section class="section section-alt" id="why">
    <h2>Why Educators Choose MTWW</h2>
    <div class="value-grid">
      <div class="value-card">
        <h3>Written for Your Students</h3>
        <p>Every role is designed for young performers — age-appropriate content, comfortable vocal ranges, and parts that let kids be kids on stage. Not shortened adult shows.</p>
      </div>
      <div class="value-card">
        <h3>Tested on Stage</h3>
        <p>Every show has been fully produced at The Actors Garden before licensing. The material that doesn't work gets revised. What you receive has been proven with real kids.</p>
      </div>
      <div class="value-card">
        <h3>Connects to Curriculum</h3>
        <p>Kipling, Twain, Greek mythology, J.M. Barrie — shows that pair naturally with what your students are already learning in the classroom.</p>
      </div>
      <div class="value-card">
        <h3>Simple, Fair Pricing</h3>
        <p>One flat fee from ${site['licensing_default_price']}. Keep everything. Copy scripts for your whole cast. Record your production. No surprises.</p>
      </div>
    </div>
  </section>

  <section class="section" id="resources-preview">
    <h2>Resources for Educators</h2>
    <p>Practical guides from 30 years of producing musicals with young performers.</p>
    <div class="resource-preview-grid">
      <a href="how-to-choose-a-school-musical.html" class="resource-link">How to Choose a Musical for Your School</a>
      <a href="why-original-musicals-work-better.html" class="resource-link">Why Original Musicals Work Better for Young Performers</a>
      <a href="musical-theatre-for-elementary-students.html" class="resource-link">Musical Theatre for Elementary Students: What Works</a>
    </div>
    <p class="section-cta"><a href="resources.html">All resources &rarr;</a></p>
  </section>

  <section class="final-cta">
    <h2>Read Any Script Free</h2>
    <p>Tell us which show interests you. We'll send the full script within 24 hours — no commitment, no credit card.</p>
    <a href="mailto:{site['email']}?subject=Free%20Perusal%20Request" class="btn btn-primary btn-lg">Request a Free Perusal</a>
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
    <p>These shows are licensed through other publishers but are part of Dave Hudson's catalog of 25+ musicals.</p>
    <div class="show-grid">
{other_cards}
    </div>
  </section>
"""

    # Filter controls with labeled groups
    filter_html = """    <div class="filter-bar" role="toolbar" aria-label="Filter shows">
      <div class="filter-group">
        <span class="filter-label">Grade:</span>
        <button class="filter-btn filter-active" data-filter="all" data-group="grade">All</button>
        <button class="filter-btn" data-filter="elementary" data-group="grade">Elementary</button>
        <button class="filter-btn" data-filter="middle" data-group="grade">Middle School+</button>
      </div>
      <div class="filter-group">
        <span class="filter-label">Level:</span>
        <button class="filter-btn filter-active" data-filter="all" data-group="level">All</button>
        <button class="filter-btn" data-filter="beginner-friendly" data-group="level">Beginner</button>
        <button class="filter-btn" data-filter="intermediate" data-group="level">Intermediate</button>
        <button class="filter-btn" data-filter="intermediate-advanced" data-group="level">Advanced</button>
      </div>
    </div>"""

    filter_js = """
<script>
document.addEventListener('DOMContentLoaded', function() {
  var cards = document.querySelectorAll('.show-card[data-status="active"], .show-card[data-status="needs_data"]');
  var activeFilters = { grade: 'all', level: 'all' };

  function applyFilters() {
    cards.forEach(function(card) {
      var show = true;
      var age = parseInt(card.getAttribute('data-age'));
      var diff = card.getAttribute('data-difficulty');

      if (activeFilters.grade === 'elementary') {
        show = show && (age && age <= 9);
      } else if (activeFilters.grade === 'middle') {
        show = show && (age && age >= 9);
      }

      if (activeFilters.level !== 'all') {
        show = show && (diff === activeFilters.level);
      }

      card.style.display = show ? '' : 'none';
    });
  }

  document.querySelectorAll('.filter-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      var group = btn.getAttribute('data-group');
      var filter = btn.getAttribute('data-filter');
      activeFilters[group] = filter;

      // Update active state within group
      document.querySelectorAll('.filter-btn[data-group="' + group + '"]').forEach(function(b) {
        b.classList.remove('filter-active');
      });
      btn.classList.add('filter-active');

      applyFilters();
    });
  });

  // Handle hash-based navigation from homepage browse cards
  var hash = window.location.hash.replace('#', '');
  if (hash === 'elementary' || hash === 'middle') {
    activeFilters.grade = hash;
    document.querySelectorAll('.filter-btn[data-group="grade"]').forEach(function(b) {
      b.classList.remove('filter-active');
      if (b.getAttribute('data-filter') === hash) b.classList.add('filter-active');
    });
    applyFilters();
  }
});
</script>"""

    html = head(
        "Our Shows",
        "Browse original musicals for schools and youth programs. Filter by age, cast size, and difficulty. Complete Production Kits from $299.",
        canonical_path="shows.html"
    ) + nav("Our Shows") + f"""
<main id="main">
  <section class="section" id="mtww-shows">
    <h2>Our Shows</h2>
    <p>Every show comes as a complete Production Kit — script, score, lead sheets, backing tracks, and video rights. Read any script free before you commit.</p>
{filter_html}
    <div class="show-grid">
{active_cards}
    </div>
  </section>
{other_section}
</main>
{filter_js}
""" + footer()
    write_page("shows.html", html)


def build_show_page(show):
    """Build an individual show detail page — structured as a teacher decision page."""
    site = load_json("site.json")
    all_shows = load_json("shows.json")
    sections = []

    # ── At-a-glance spec card ──
    specs = []
    if show.get("age_range"):
        specs.append(("Ages", show["age_range"]))
    if show.get("cast_size"):
        specs.append(("Cast", f"{show['cast_size']}+ roles"))
    if show.get("runtime_minutes"):
        inter = " + intermission" if show.get("has_intermission") else ""
        specs.append(("Runtime", f"{show['runtime_minutes']} min{inter}"))
    if show.get("song_count"):
        specs.append(("Songs", str(show["song_count"])))
    if show.get("difficulty"):
        specs.append(("Level", show["difficulty"].replace("-", " ").title()))
    if show.get("licensing_price"):
        specs.append(("License", f"${show['licensing_price']}"))

    if specs:
        spec_cells = "\n".join(
            f'      <div class="spec-item"><span class="spec-label">{label}</span><span class="spec-value">{value}</span></div>'
            for label, value in specs
        )
        sections.append(f"""
  <section class="section">
    <div class="spec-card">
{spec_cells}
    </div>
  </section>""")

    # ── Synopsis (before any CTA — teacher needs to know what the show IS) ──
    if show.get("synopsis"):
        sections.append(f"""
  <section class="section">
    <h2>About the Show</h2>
    <p>{show['synopsis']}</p>
  </section>""")

    # ── Why This Works for Young Performers (show-specific) ──
    why_items = []
    if show.get("cast_size") and show.get("cast_notes"):
        why_items.append(("Flexible casting", show["cast_notes"]))
    if show.get("source_material") and show["source_material"] != "Original":
        why_items.append(("Curriculum-ready source material", f"Based on {show['source_material']} — connects naturally to classroom learning."))
    if show.get("difficulty"):
        diff_labels = {
            "beginner-friendly": "Accessible for new programs and first-time performers.",
            "intermediate": "Appropriate for programs with some musical theater experience.",
            "intermediate-advanced": "Challenging material that rewards experienced performers."
        }
        why_items.append(("Right level of challenge", diff_labels.get(show["difficulty"], "")))
    if show.get("has_intermission") is not None:
        if show["has_intermission"]:
            why_items.append(("Built-in intermission", "Gives young performers and audiences a natural break."))

    if why_items:
        items_html = "\n".join(
            f'      <div class="why-works-item"><strong>{label}</strong> {desc}</div>'
            for label, desc in why_items
        )
        sections.append(f"""
  <section class="section section-alt">
    <h2>Why This Works for Young Performers</h2>
    <div class="why-works-grid">
{items_html}
    </div>
  </section>""")

    # ── Curriculum connections ──
    connections = show.get("curriculum_connections", [])
    if connections:
        items = "\n".join(f"      <li>{c}</li>" for c in connections)
        sections.append(f"""
  <section class="section">
    <h2>Curriculum Connections</h2>
    <p>Pair this show with classroom learning:</p>
    <ul class="curriculum-list">
{items}
    </ul>
  </section>""")

    # ── Credits + Details table ──
    rows = []
    if show.get("book_by"):
        rows.append(f"<tr><th>Book & Lyrics</th><td>{show['book_by']}</td></tr>")
    if show.get("music_by"):
        rows.append(f"<tr><th>Music</th><td>{show['music_by']}</td></tr>")
    if show.get("source_material"):
        rows.append(f"<tr><th>Based On</th><td>{show['source_material']}</td></tr>")
    if show.get("premiere_year"):
        venue = f" — {show['premiere_venue']}" if show.get("premiere_venue") else ""
        rows.append(f"<tr><th>Premiere</th><td>{show['premiere_year']}{venue}</td></tr>")
    if show.get("production_history"):
        rows.append(f"<tr><th>Productions</th><td>{show['production_history']}</td></tr>")

    if rows:
        all_rows = "\n".join(rows)
        sections.append(f"""
  <section class="section section-alt">
    <h2>Details</h2>
    <table class="detail-table">
{all_rows}
    </table>
  </section>""")

    # ── What's in Your Production Kit ──
    if show.get("licensing_price"):
        lic_items = show.get("licensing_includes", site.get("licensing_includes_default", []))
        items_html = "\n".join(f'      <li><span class="kit-check" aria-hidden="true">&#10003;</span> {item}</li>' for item in lic_items)
        sections.append(f"""
  <section class="section" id="production-kit">
    <h2>Your Production Kit</h2>
    <div class="kit-box">
      <ul class="kit-list">
{items_html}
      </ul>
      <div class="kit-price">
        <p class="licensing-price">${show['licensing_price']}</p>
        <p class="kit-terms">{show.get('licensing_notes', '')}</p>
        <a href="mailto:{site['email']}?subject=Order+Production+Kit+%E2%80%94+{show['title'].replace(' ', '+')}" class="btn btn-primary">Order the Production Kit</a>
      </div>
    </div>
  </section>""")

    # ── FAQ (collapsible) ──
    faq_items = show.get("faq", [])
    if faq_items:
        faq_html = "\n".join(
            f"      <dt>{item['q']}</dt>\n      <dd>{item['a']}</dd>"
            for item in faq_items
        )
        sections.append(f"""
  <section class="section section-alt">
    <h2>Frequently Asked Questions</h2>
    <dl class="faq">
{faq_html}
    </dl>
  </section>""")

    # ── Photo gallery (auto-discovered from assets/images/{show-id}/) ──
    gallery_dir = ASSETS / "images" / show["id"]
    if gallery_dir.is_dir():
        photos = sorted(
            p for p in gallery_dir.iterdir()
            if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")
        )
        if photos:
            gallery_items = "\n".join(
                f'      <img src="assets/images/{show["id"]}/{p.name}" alt="{show["title"]} production photo" loading="lazy">'
                for p in photos
            )
            sections.append(f"""
  <section class="section">
    <h2>Production Photos</h2>
    <p class="photo-credit">Photos by Ron Orzel / Foto Ops</p>
    <div class="photo-gallery">
{gallery_items}
    </div>
  </section>""")

    # ── Free perusal CTA (after they know what the show is) ──
    if show.get("available_on_mtww"):
        sections.append(f"""
  <section class="final-cta">
    <h2>Read the Script Free</h2>
    <p>Tell us your name and organization. We'll send the full script within 24 hours — no commitment, no credit card.</p>
    <a href="mailto:{site['email']}?subject=Free+Perusal+%E2%80%94+{show['title'].replace(' ', '+')}" class="btn btn-primary btn-lg">Request Free Perusal</a>
  </section>""")

    # ── Related shows ──
    related_ids = show.get("related_shows", [])
    if related_ids:
        related = [s for s in all_shows if s["id"] in related_ids and s.get("available_on_mtww")]
        if related:
            related_cards = "\n".join(show_card(s) for s in related)
            sections.append(f"""
  <section class="section">
    <h2>You Might Also Like</h2>
    <div class="show-grid">
{related_cards}
    </div>
  </section>""")

    body = "\n".join(sections)

    status_note = ""
    if show["status"] == "needs_data":
        status_note = '<p class="notice">Full details coming soon. <a href="contact.html">Contact us</a> for more information.</p>'

    # Schema: Product + FAQ
    schemas = [show_schema(show)]
    faq_s = faq_schema(faq_items)
    if faq_s:
        schemas.append(faq_s)

    # Meta description
    meta_desc_parts = []
    if show.get("source_material") and show["source_material"] != "Original":
        meta_desc_parts.append(f"Based on {show['source_material']}.")
    if show.get("cast_size") and show.get("age_range"):
        meta_desc_parts.append(f"{show['cast_size']}+ roles, {show['age_range']}.")
    if show.get("runtime_minutes"):
        meta_desc_parts.append(f"{show['runtime_minutes']} min.")
    if show.get("licensing_price"):
        meta_desc_parts.append(f"${show['licensing_price']} flat-rate licensing.")
    meta_desc = f"{show['title']} — musical for schools. " + " ".join(meta_desc_parts)

    # Hero quick-spec summary
    hero_meta_parts = []
    if show.get("age_range"):
        hero_meta_parts.append(f"<span>{show['age_range']}</span>")
    if show.get("cast_size"):
        hero_meta_parts.append(f"<span>{show['cast_size']}+ roles</span>")
    if show.get("runtime_minutes"):
        hero_meta_parts.append(f"<span>{show['runtime_minutes']} min</span>")
    if show.get("licensing_price"):
        hero_meta_parts.append(f"<span>${show['licensing_price']}</span>")
    hero_meta = "\n      ".join(hero_meta_parts)

    html = head(
        f"{show['title']} — Musical for Schools",
        meta_desc,
        canonical_path=f"{show['id']}.html",
        schema=schemas[0]
    ) + nav("Our Shows") + f"""
<main id="main">
  <section class="show-hero">
    <h1>{show['title']}</h1>
    <p class="show-hero-tagline">{show.get('tagline', '')}</p>
    <p class="show-hero-credential">By two-time Richard Rodgers Award winner Dave Hudson</p>
    <div class="show-hero-meta">
      {hero_meta}
    </div>
    {status_note}
  </section>
{body}
</main>
""" + footer()

    # If there's a FAQ schema, inject it as a second script tag
    if faq_s:
        faq_tag = f'<script type="application/ld+json">\n{json.dumps(faq_s, indent=2)}\n</script>'
        html = html.replace('</head>', f'{faq_tag}\n</head>')

    write_page(f"{show['id']}.html", html)


def build_about():
    site = load_json("site.json")
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

    html = head(
        "About MTWW",
        "The story behind Musical Theatre Worldwide. Two-time Richard Rodgers Award winners, 30 years of youth theater in Oak Park, IL.",
        canonical_path="about.html",
        schema=org_schema()
    ) + nav("About") + f"""
<main id="main">
  <section class="section">
    <h2>About Musical Theatre Worldwide</h2>
    <p>Musical Theatre Worldwide was born from The Actors Garden in Oak Park, Illinois — a children's theater program that has been developing young performers since 1996.</p>
    <p>Artistic Director GiGi Hudson identified a gap in the market: most musicals available for schools were "Junior" versions — shortened, simplified adaptations of adult shows. The roles, humor, and emotional complexity were designed for grown-ups, then cut down. Kids deserved better.</p>
    <p>Playwright Dave Hudson began writing original works specifically for young performers. Every show is workshopped, produced, and revised at The Actors Garden, where real kids test every scene, every song, and every joke. By the time a show is offered for licensing, it has been proven on stage — not just on paper.</p>
    <p>The result: a catalog of 25+ original musicals that have been performed across the United States and internationally in Scotland and Thailand.</p>
  </section>

  <section class="section section-alt" id="awards">
    <h2>Awards & Recognition</h2>
    <div class="award-feature">
      <h3>Richard Rodgers Award</h3>
      <p>Dave Hudson and composer Paul Libman are two-time winners of the <strong>Richard Rodgers Award for new musicals</strong>, administered by the American Academy of Arts and Letters. This is the most prestigious award in musical theatre writing.</p>
      <ul class="award-list">
        <li>2005 — <em>Dust and Dreams</em> (based on Carl Sandburg)</li>
        <li>2007 — <em>Main-Travelled Roads</em> (based on Hamlin Garland)</li>
      </ul>
      <p>Dave has also received multiple selections for the Stages Festival of New Musicals and the Madison Rep Festival of New Plays.</p>
    </div>
  </section>

  <section class="section" id="founders">
    <h2>Founders</h2>
    <div class="people-grid">
{founder_html}
    </div>
  </section>

  <section class="section section-alt" id="collaborators">
    <h2>Collaborators</h2>
    <p>Dave Hudson has written musicals with composers across the country. Here are the collaborators whose work appears in the MTWW catalog.</p>
    <div class="people-grid">
{collab_html}
    </div>
  </section>

  <section class="section" id="actors-garden">
    <h2>The Actors Garden Connection</h2>
    <p>The Actors Garden is a children's theater education program in Oak Park, Illinois, founded in 1996 by GiGi and Dave Hudson. For over 30 years, AG has been the creative laboratory where every MTWW musical is developed.</p>
    <p>When you license a MTWW show, you're getting a show that has been fully produced — cast, rehearsed, staged, performed, revised, and performed again — with real kids, in a real theater, in front of real audiences. That workshopping process is our quality guarantee.</p>
  </section>
</main>
""" + footer()
    write_page("about.html", html)


def build_licensing():
    site = load_json("site.json")
    items = "\n".join(f'    <li><span class="kit-check" aria-hidden="true">&#10003;</span> {item}</li>' for item in site["licensing_includes_default"])

    # Comparison table — single canonical location
    comp = site.get("comparison", {}).get("vs_junior", [])
    comp_rows = ""
    for row in comp:
        mtww = '<span class="check" aria-label="Yes">&#10003;</span>' if row.get("mtww") else '<span class="x" aria-label="No">&#10007;</span>'
        junior = '<span class="check" aria-label="Yes">&#10003;</span>' if row.get("junior") else '<span class="x" aria-label="No">&#10007;</span>'
        note = f'<td class="note">{row.get("note", "")}</td>' if row.get("note") else '<td></td>'
        comp_rows += f"        <tr><td>{row['feature']}</td><td class='center'>{mtww}</td><td class='center'>{junior}</td>{note}</tr>\n"

    html = head(
        "Production Kits — What You Get",
        f"MTWW Production Kits from ${site['licensing_default_price']}. Script, score, lead sheets, backing tracks, and video rights included. No rentals, no surprises.",
        canonical_path="licensing.html"
    ) + nav("Production Kits") + f"""
<main id="main">
  <section class="section">
    <h2>What's in a Production Kit</h2>
    <p>Every MTWW show comes as a complete Production Kit — everything you need to rehearse, perform, and share your production. No rental fees, no per-script charges, no surprise costs.</p>

    <div class="kit-box">
      <ul class="kit-list">
{items}
      </ul>
      <p class="licensing-price">From ${site['licensing_default_price']}</p>
    </div>
  </section>

  <section class="section section-alt">
    <h2>How It Works</h2>
    <ol class="steps-list">
      <li><strong>Browse shows</strong> — Find a musical that fits your program's age range, cast size, and timeline.</li>
      <li><strong>Read the script free</strong> — Email us and we'll send you the full script within 24 hours. No commitment.</li>
      <li><strong>Order your Production Kit</strong> — Pay once and receive everything as printable PDFs and downloadable audio.</li>
      <li><strong>Produce it</strong> — Copy scripts for your cast. Record your production. Upload to YouTube. No restrictions within your license period.</li>
    </ol>
    <a href="mailto:{site['email']}?subject=Free%20Perusal%20Request" class="btn btn-primary">Read a Script Free</a>
  </section>

  <section class="section">
    <h2>MTWW vs. Traditional Publishers</h2>
    <p>Most school musical publishers use a rental model with per-performance fees and mandatory material returns. Here's how MTWW compares:</p>
    <div class="table-wrap">
      <table class="compare-table">
        <thead>
          <tr><th>Feature</th><th class="center">MTWW</th><th class="center">Junior Versions</th><th>Why It Matters</th></tr>
        </thead>
        <tbody>
{comp_rows}        </tbody>
      </table>
    </div>
  </section>

  <section class="section section-alt">
    <h2>Frequently Asked Questions</h2>
    <dl class="faq">
      <dt>What's in the Production Kit?</dt>
      <dd>Complete script (printable, unlimited copies), piano/vocal score, vocal lead sheets for every song, backing tracks for rehearsal and performance, and video recording + YouTube rights. No rental fees. You keep everything.</dd>

      <dt>Can we modify the show for our program?</dt>
      <dd>Contact us to discuss. Our shows are designed to be flexible with cast sizes and we're happy to work with you on adaptations.</dd>

      <dt>How long does the license last?</dt>
      <dd>License terms vary by show — typically unlimited performances within a calendar year or a 2-week performance period. See individual show pages for details.</dd>

      <dt>Can we record and share our production?</dt>
      <dd>Yes. Every Production Kit includes video recording and YouTube rights. Record your production, share it with families, post it online. No extra fees.</dd>

      <dt>Do we need to return any materials?</dt>
      <dd>No. Everything is delivered as digital files that you keep. No scripts to mail back, no rental returns.</dd>

      <dt>Can we read the script before ordering?</dt>
      <dd>Absolutely. Email us and we'll send a free perusal copy of any show within 24 hours. No commitment, no credit card.</dd>
    </dl>
  </section>
</main>
""" + footer()
    write_page("licensing.html", html)


def build_contact():
    site = load_json("site.json")

    html = head(
        "Contact",
        "Get in touch with Musical Theatre Worldwide. Request a perusal copy, ask about licensing, or learn more about our shows.",
        canonical_path="contact.html"
    ) + nav("Contact") + f"""
<main id="main">
  <section class="section">
    <h2>Get in Touch</h2>
    <div class="contact-grid">
      <div class="contact-card">
        <h3>Read a Script Free</h3>
        <p>Tell us which show and your organization name. We'll send you the full script within 24 hours — no commitment, no credit card.</p>
        <a href="mailto:{site['email']}?subject=Free%20Perusal%20Request" class="btn btn-primary">Request a Free Perusal</a>
      </div>
      <div class="contact-card">
        <h3>Order a Production Kit</h3>
        <p>Ready to go? Questions about Production Kits, pricing, or anything else?</p>
        <p><a href="mailto:{site['email']}">{site['email']}</a></p>
        <p>{site['phone']}</p>
      </div>
      <div class="contact-card">
        <h3>The Actors Garden</h3>
        <p>Looking for our youth theater program in Oak Park, Illinois?</p>
        <p><a href="https://theactorsgarden.com">Visit The Actors Garden &rarr;</a></p>
      </div>
    </div>
  </section>
</main>
""" + footer()
    write_page("contact.html", html)


def build_resources():
    """Build the resources/blog listing page with grouping by category."""
    resources = load_json("resources.json")

    # Group by category
    groups = {}
    group_labels = {
        "guides": "Choosing a Show",
        "directors-guides": "Directing & Staging",
        "philosophy": "Building a Program"
    }
    group_order = ["guides", "directors-guides", "philosophy"]

    for r in resources:
        cat = r.get("category", "guides")
        if cat not in groups:
            groups[cat] = []
        groups[cat].append(r)

    sections_html = ""
    for cat in group_order:
        if cat not in groups:
            continue
        label = group_labels.get(cat, cat.replace("-", " ").title())
        cards = []
        for r in groups[cat]:
            cards.append(f"""    <article class="resource-card">
      <h3><a href="{r['slug']}.html">{r['title']}</a></h3>
      <p>{r['description']}</p>
    </article>""")
        cards_html = "\n".join(cards)
        sections_html += f"""
    <div class="resource-group">
      <h3>{label}</h3>
      <div class="resource-grid">
{cards_html}
      </div>
    </div>
"""

    html = head(
        "For Educators",
        "Guides, staging tips, and perspective from 30 years of producing youth musicals. Free resources for drama teachers and program directors.",
        canonical_path="resources.html"
    ) + nav("For Educators") + f"""
<main id="main">
  <section class="section">
    <h2>For Educators</h2>
    <p>Practical guides from 30 years of producing musicals with young performers at The Actors Garden.</p>
{sections_html}
  </section>
</main>
""" + footer()
    write_page("resources.html", html)


def build_resource_page(resource):
    """Build an individual resource/blog page."""
    all_shows = load_json("shows.json")

    # Convert content_paragraphs to HTML
    content_parts = []
    for para in resource.get("content_paragraphs", []):
        if para.startswith("## "):
            content_parts.append(f"<h2>{para[3:]}</h2>")
        elif para.startswith("**") and para.endswith("**"):
            content_parts.append(f"<p><strong>{para[2:-2]}</strong></p>")
        elif para.startswith("- "):
            content_parts.append(f"<li>{para[2:]}</li>")
        else:
            import re
            processed = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', para)
            content_parts.append(f"<p>{processed}</p>")

    # Wrap consecutive <li> items in <ul>
    final_parts = []
    in_list = False
    for part in content_parts:
        if part.startswith("<li>"):
            if not in_list:
                final_parts.append("<ul>")
                in_list = True
            final_parts.append(part)
        else:
            if in_list:
                final_parts.append("</ul>")
                in_list = False
            final_parts.append(part)
    if in_list:
        final_parts.append("</ul>")

    content_html = "\n    ".join(final_parts)

    # Related shows
    related_ids = resource.get("related_shows", [])
    related_section = ""
    if related_ids:
        related = [s for s in all_shows if s["id"] in related_ids and s.get("available_on_mtww")]
        if related:
            related_cards = "\n".join(show_card(s) for s in related)
            related_section = f"""
  <section class="section section-alt">
    <h2>Related Shows</h2>
    <div class="show-grid">
{related_cards}
    </div>
  </section>"""

    html = head(
        resource["title"],
        resource["description"],
        canonical_path=f"{resource['slug']}.html"
    ) + nav("For Educators") + f"""
<main id="main">
  <article class="section article-content">
    <h1>{resource['title']}</h1>
    <p class="article-meta">Musical Theatre Worldwide</p>
    {content_html}
  </article>
{related_section}
  <section class="section">
    <p class="section-cta"><a href="resources.html">&larr; All resources</a></p>
  </section>
</main>
""" + footer()
    write_page(f"{resource['slug']}.html", html)


def build_sitemap():
    """Generate sitemap.xml."""
    site = load_json("site.json")
    shows = load_json("shows.json")
    resources = load_json("resources.json")
    base = site["url"].rstrip("/")

    urls = [
        (f"{base}/", "1.0", "weekly"),
        (f"{base}/shows.html", "0.9", "weekly"),
        (f"{base}/licensing.html", "0.8", "monthly"),
        (f"{base}/resources.html", "0.8", "weekly"),
        (f"{base}/about.html", "0.7", "monthly"),
        (f"{base}/contact.html", "0.6", "monthly"),
    ]

    for show in shows:
        if show.get("available_on_mtww"):
            urls.append((f"{base}/{show['id']}.html", "0.8", "monthly"))
        else:
            urls.append((f"{base}/{show['id']}.html", "0.5", "monthly"))

    for r in resources:
        urls.append((f"{base}/{r['slug']}.html", "0.7", "monthly"))

    today = datetime.now().strftime("%Y-%m-%d")
    entries = "\n".join(
        f"""  <url>
    <loc>{url}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{priority}</priority>
  </url>""" for url, priority, freq in urls
    )

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{entries}
</urlset>
"""
    write_page("sitemap.xml", xml)


def build_robots():
    site = load_json("site.json")
    txt = f"""User-agent: *
Allow: /

Sitemap: {site['url']}/sitemap.xml
"""
    write_page("robots.txt", txt)


# ── Data check ────────────────────────────────────────────────

def check_data():
    """Report data completeness for all shows."""
    shows = load_json("shows.json")
    key_fields = [
        "synopsis", "runtime_minutes", "age_range", "cast_size",
        "song_count", "licensing_price", "music_by", "premiere_year",
        "faq", "difficulty", "themes", "curriculum_connections"
    ]

    print("\n  DATA COMPLETENESS REPORT")
    print("  " + "=" * 50)

    for show in shows:
        missing = []
        for f in key_fields:
            val = show.get(f)
            if val is None or val == [] or val == "":
                missing.append(f)

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
    resources = load_json("resources.json")

    build_index()
    build_shows()
    build_about()
    build_licensing()
    build_contact()
    build_resources()

    for show in shows:
        build_show_page(show)

    for resource in resources:
        build_resource_page(resource)

    build_sitemap()
    build_robots()

    # Copy image assets into output so GitHub Pages can serve them
    src_images = ASSETS / "images"
    dst_images = OUTPUT / "assets" / "images"
    if src_images.is_dir():
        if dst_images.exists():
            shutil.rmtree(dst_images)
        shutil.copytree(src_images, dst_images)
        n_images = sum(1 for _ in dst_images.rglob("*") if _.is_file())
        print(f"  copied {n_images} images → output/assets/images/")

    n_shows = len(shows)
    n_resources = len(resources)
    total = n_shows + n_resources + 6 + 2  # 6 site pages + sitemap + robots
    print(f"\nDone. {total} files → output/")
    print(f"  {n_shows} show pages + {n_resources} resource pages + 6 site pages + sitemap + robots\n")


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
