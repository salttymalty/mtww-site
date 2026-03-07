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
import html as html_mod
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent
DATA = ROOT / "data"
OUTPUT = ROOT / "output"


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


def credential_bar():
    """The trust-signal bar that appears across key pages."""
    return """<div class="credential-bar">
  <div class="credential-inner">
    <span class="credential-item"><strong>Two-Time Richard Rodgers Award Winners</strong></span>
    <span class="credential-sep" aria-hidden="true">&middot;</span>
    <span class="credential-item">25+ Original Musicals</span>
    <span class="credential-sep" aria-hidden="true">&middot;</span>
    <span class="credential-item">30 Years of Youth Theater</span>
  </div>
</div>
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
}});
</script>
</body>
</html>
"""


def show_card(show):
    """Render a show as a card for the listing page."""
    meta_parts = []
    if show.get("runtime_minutes"):
        rt = show["runtime_minutes"]
        inter = " + intermission" if show.get("has_intermission") else ""
        meta_parts.append(f"{rt} min{inter}")
    if show.get("cast_size"):
        meta_parts.append(f"{show['cast_size']}+ cast")
    if show.get("age_range"):
        meta_parts.append(show["age_range"])
    if show.get("licensing_price"):
        meta_parts.append(f"${show['licensing_price']}")

    meta_html = '<span class="card-sep" aria-hidden="true">&middot;</span>'.join(
        f'<span>{m}</span>' for m in meta_parts
    ) if meta_parts else ""

    status_badge = ""
    if show["status"] == "needs_data":
        status_badge = '<span class="badge badge-draft">Coming Soon</span>'
    elif show["status"] == "external_license":
        status_badge = '<span class="badge badge-external">Beat by Beat Press</span>'

    # Credits line
    credits = []
    if show.get("music_by"):
        credits.append(f"Music by {show['music_by']}")
    if show.get("book_by") and show["book_by"] != show.get("lyrics_by"):
        credits.append(f"Book by {show['book_by']}")
    if show.get("lyrics_by"):
        credits.append(f"Lyrics by {show['lyrics_by']}")
    credits_html = " &middot; ".join(credits)

    # Link — external shows link out
    href = show.get("external_url", f"{show['id']}.html")
    target = ' target="_blank" rel="noopener"' if show.get("external_url") else ""

    tagline = show.get('tagline', '')
    difficulty = show.get('difficulty', '')
    diff_badge = f'<span class="badge badge-diff">{difficulty}</span>' if difficulty else ""

    return f"""<article class="show-card" data-age="{show.get('min_age', '')}" data-cast="{show.get('cast_size', '')}" data-runtime="{show.get('runtime_minutes', '')}" data-status="{show['status']}">
  <div class="show-card-body">
    <h3><a href="{href}"{target}>{show['title']}</a> {status_badge} {diff_badge}</h3>
    <p class="show-tagline">{tagline}</p>
    <p class="show-meta">{meta_html}</p>
    <p class="show-credits">{credits_html}</p>
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
    active = [s for s in shows if s.get("available_on_mtww")]

    cards = "\n".join(show_card(s) for s in active)

    # Credential items
    cred_items = "\n".join(
        f'      <li>{c}</li>' for c in site.get("credentials", [])
    )

    # Comparison table
    comp = site.get("comparison", {}).get("vs_junior", [])
    comp_rows = ""
    for row in comp:
        mtww_check = '<span class="check" aria-label="Yes">&#10003;</span>' if row.get("mtww") else '<span class="x" aria-label="No">&#10007;</span>'
        junior_check = '<span class="check" aria-label="Yes">&#10003;</span>' if row.get("junior") else '<span class="x" aria-label="No">&#10007;</span>'
        comp_rows += f"""        <tr>
          <td>{row['feature']}</td>
          <td class="center">{mtww_check}</td>
          <td class="center">{junior_check}</td>
          <td class="note">{row.get('note', '')}</td>
        </tr>\n"""

    schema = org_schema()

    html = head(
        "Home",
        "Award-winning original musicals for schools and youth programs. Written for young performers, workshopped at The Actors Garden. From $299.",
        canonical_path="",
        schema=schema
    ) + nav("Home") + credential_bar() + f"""
<main>
  <section class="hero">
    <div class="hero-inner">
      <h1>Original Musicals for Young Performers</h1>
      <p class="hero-tagline">{site['tagline']}</p>
      <p class="hero-sub">Every show is workshopped, produced, and perfected at The Actors Garden before being offered for licensing. What you get has been proven on stage with real kids.</p>
      <div class="hero-ctas">
        <a href="shows.html" class="btn btn-primary">Browse Our Shows</a>
        <a href="licensing.html" class="btn btn-secondary">How Licensing Works</a>
      </div>
    </div>
  </section>

  <section class="section" id="featured">
    <h2>Our Shows</h2>
    <p>Available for licensing from ${site['licensing_default_price']}. Every show includes the complete script, piano/vocal score, lead sheets, and backing tracks.</p>
    <div class="show-grid">
{cards}
    </div>
    <p class="section-cta"><a href="shows.html">View all shows &rarr;</a></p>
  </section>

  <section class="section section-alt" id="why">
    <h2>Why Choose MTWW?</h2>
    <div class="value-grid">
      <div class="value-card">
        <h3>Written for Young Performers</h3>
        <p>Not shortened adult shows. Every musical is originally written for young actors, with age-appropriate content, comfortable vocal ranges, and roles designed for developing performers.</p>
      </div>
      <div class="value-card">
        <h3>Proven on Stage</h3>
        <p>Every show is workshopped and produced at The Actors Garden before licensing. What you receive has been tested, revised, and perfected with real kids over 30 years.</p>
      </div>
      <div class="value-card">
        <h3>Simple, Fair Licensing</h3>
        <p>From ${site['licensing_default_price']} for everything: script, score, lead sheets, backing tracks. No per-script rental. No returns required. No surprises.</p>
      </div>
      <div class="value-card">
        <h3>Award-Winning Writers</h3>
        <p>Head playwright Dave Hudson is a two-time winner of the Richard Rodgers Award for new musicals — the most prestigious award in musical theatre writing.</p>
      </div>
    </div>
  </section>

  <section class="section" id="compare">
    <h2>MTWW vs. Junior Versions</h2>
    <p>Most school musicals are shortened versions of adult shows. MTWW shows are built from the ground up for young performers.</p>
    <div class="table-wrap">
      <table class="compare-table">
        <thead>
          <tr>
            <th>Feature</th>
            <th class="center">MTWW</th>
            <th class="center">Junior Versions</th>
            <th>Why It Matters</th>
          </tr>
        </thead>
        <tbody>
{comp_rows}        </tbody>
      </table>
    </div>
  </section>

  <section class="section section-alt" id="resources-preview">
    <h2>Resources for Educators</h2>
    <p>Guides, tips, and perspective from 30 years of producing youth musicals.</p>
    <div class="resource-preview-grid">
      <a href="how-to-choose-a-school-musical.html" class="resource-link">How to Choose a Musical for Your School</a>
      <a href="why-original-musicals-work-better.html" class="resource-link">Why Original Musicals Work Better for Young Performers</a>
      <a href="musical-theatre-for-elementary-students.html" class="resource-link">Musical Theatre for Elementary Students: What Works</a>
    </div>
    <p class="section-cta"><a href="resources.html">All resources &rarr;</a></p>
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

    # Filter controls
    filter_js = """
<script>
document.addEventListener('DOMContentLoaded', function() {
  var filters = document.querySelectorAll('.filter-btn');
  var cards = document.querySelectorAll('.show-card[data-status="active"], .show-card[data-status="needs_data"]');

  filters.forEach(function(btn) {
    btn.addEventListener('click', function() {
      filters.forEach(function(b) { b.classList.remove('filter-active'); });
      btn.classList.add('filter-active');

      var filter = btn.getAttribute('data-filter');
      cards.forEach(function(card) {
        if (filter === 'all') {
          card.style.display = '';
        } else if (filter === 'elementary') {
          var age = parseInt(card.getAttribute('data-age'));
          card.style.display = (age && age <= 9) ? '' : 'none';
        } else if (filter === 'middle') {
          var age = parseInt(card.getAttribute('data-age'));
          card.style.display = (age && age >= 9 && age <= 13) ? '' : 'none';
        } else if (filter === 'short') {
          var rt = parseInt(card.getAttribute('data-runtime'));
          card.style.display = (rt && rt <= 60) ? '' : 'none';
        }
      });
    });
  });
});
</script>"""

    html = head(
        "Our Shows",
        "Browse original musicals for schools and youth programs. Filter by age, cast size, and runtime. From $299.",
        canonical_path="shows.html"
    ) + nav("Shows") + credential_bar() + f"""
<main>
  <section class="section" id="mtww-shows">
    <h2>MTWW Shows</h2>
    <p>Available for licensing directly from Musical Theatre Worldwide. Every show includes the complete script, score, lead sheets, and backing tracks.</p>
    <div class="filter-bar" role="toolbar" aria-label="Filter shows">
      <button class="filter-btn filter-active" data-filter="all">All Shows</button>
      <button class="filter-btn" data-filter="elementary">Elementary</button>
      <button class="filter-btn" data-filter="middle">Middle School+</button>
    </div>
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
    """Build an individual show detail page following the audit template."""
    site = load_json("site.json")
    all_shows = load_json("shows.json")
    sections = []

    # ── Spec card (scannable at-a-glance) ──
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

    # ── Primary CTA ──
    sections.append("""
  <section class="section cta-section">
    <a href="contact.html?subject=Perusal+Request" class="btn btn-primary btn-lg">Request a Perusal Copy</a>
    <p class="cta-hint">Read the full script before you commit. Free for educators.</p>
  </section>""")

    # ── Synopsis ──
    if show.get("synopsis"):
        sections.append(f"""
  <section class="section">
    <h2>About the Show</h2>
    <p>{show['synopsis']}</p>
  </section>""")

    # ── Credits + Details table ──
    rows = []
    if show.get("book_by"):
        rows.append(f"<tr><th>Book & Lyrics</th><td>{show['book_by']}</td></tr>")
    if show.get("music_by"):
        rows.append(f"<tr><th>Music</th><td>{show['music_by']}</td></tr>")
    if show.get("source_material"):
        rows.append(f"<tr><th>Based On</th><td>{show['source_material']}</td></tr>")
    if show.get("cast_notes"):
        rows.append(f"<tr><th>Cast Notes</th><td>{show['cast_notes']}</td></tr>")
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

    # ── Licensing box ──
    if show.get("licensing_price"):
        lic_items = show.get("licensing_includes", site.get("licensing_includes_default", []))
        items_html = "\n".join(f"      <li>{item}</li>" for item in lic_items)
        sections.append(f"""
  <section class="section section-alt" id="licensing">
    <h2>Licensing</h2>
    <div class="licensing-box">
      <p class="licensing-price">${show['licensing_price']}</p>
      <p>{show.get('licensing_notes', '')}</p>
      <ul>
{items_html}
      </ul>
      <a href="contact.html?subject=License+{show['title'].replace(' ', '+')}" class="btn btn-primary">License This Show</a>
    </div>
  </section>""")

    # ── FAQ ──
    faq_items = show.get("faq", [])
    if faq_items:
        faq_html = "\n".join(
            f"      <dt>{item['q']}</dt>\n      <dd>{item['a']}</dd>"
            for item in faq_items
        )
        sections.append(f"""
  <section class="section">
    <h2>Frequently Asked Questions</h2>
    <dl class="faq">
{faq_html}
    </dl>
  </section>""")

    # ── Related shows ──
    related_ids = show.get("related_shows", [])
    if related_ids:
        related = [s for s in all_shows if s["id"] in related_ids and s.get("available_on_mtww")]
        if related:
            related_cards = "\n".join(show_card(s) for s in related)
            sections.append(f"""
  <section class="section section-alt">
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

    # Build description for meta
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

    html = head(
        f"{show['title']} — Musical for Schools",
        meta_desc,
        canonical_path=f"{show['id']}.html",
        schema=schemas[0]
    ) + nav("Shows") + f"""
<main>
  <section class="show-hero">
    <h1>{show['title']}</h1>
    <p class="show-hero-tagline">{show.get('tagline', '')}</p>
    <p class="show-hero-credential">By two-time Richard Rodgers Award winner Dave Hudson</p>
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
    ) + nav("About") + credential_bar() + f"""
<main>
  <section class="section">
    <h2>About Musical Theatre Worldwide</h2>
    <p>Musical Theatre Worldwide was born from The Actors Garden in Oak Park, Illinois — a children's theater program that has been developing young performers since 1996.</p>
    <p>Artistic Director GiGi Hudson identified a gap in the market: most musicals available for schools were "Junior" versions — shortened, simplified adaptations of adult shows. The roles, humor, and emotional complexity were designed for grown-ups, then cut down. Kids deserved better.</p>
    <p>Playwright Dave Hudson began writing original works specifically for young performers. Every show is workshopped, produced, and revised at The Actors Garden, where real kids test every scene, every song, and every joke. By the time a show is offered for licensing, it has been proven on stage — not just on paper.</p>
    <p>The result: a catalog of 25+ original musicals that have been performed coast to coast across the United States and internationally in Scotland and Thailand.</p>
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
    <p>This means something specific: when you license a MTWW show, you're not getting a script that was workshopped in a reading room. You're getting a show that has been fully produced — cast, rehearsed, staged, performed, revised, and performed again — with real kids, in a real theater, in front of real audiences.</p>
    <p>That workshopping process is our quality guarantee.</p>
  </section>
</main>
""" + footer()
    write_page("about.html", html)


def build_licensing():
    site = load_json("site.json")
    items = "\n".join(f"    <li>{item}</li>" for item in site["licensing_includes_default"])

    # Comparison table
    comp = site.get("comparison", {}).get("vs_junior", [])
    comp_rows = ""
    for row in comp:
        mtww = '<span class="check" aria-label="Yes">&#10003;</span>' if row.get("mtww") else '<span class="x" aria-label="No">&#10007;</span>'
        junior = '<span class="check" aria-label="Yes">&#10003;</span>' if row.get("junior") else '<span class="x" aria-label="No">&#10007;</span>'
        comp_rows += f"        <tr><td>{row['feature']}</td><td class='center'>{mtww}</td><td class='center'>{junior}</td></tr>\n"

    html = head(
        "How Licensing Works",
        f"License a MTWW musical for ${site['licensing_default_price']}. Includes script, score, lead sheets, and backing tracks. No rentals, no surprises.",
        canonical_path="licensing.html"
    ) + nav("Licensing") + credential_bar() + f"""
<main>
  <section class="section">
    <h2>How Licensing Works</h2>
    <p>Licensing a Musical Theatre Worldwide show is simple and affordable. No rental fees, no per-script charges, no surprise costs.</p>

    <div class="licensing-box">
      <p class="licensing-price">From ${site['licensing_default_price']}</p>
      <p>Each licensed show comes complete with everything you need:</p>
      <ul>
{items}
      </ul>
    </div>
  </section>

  <section class="section section-alt">
    <h2>Getting Started</h2>
    <ol class="steps-list">
      <li><strong>Browse our shows</strong> — Find a musical that fits your program's age range, cast size, and timeline.</li>
      <li><strong>Request a perusal copy</strong> — Read the full script before you commit. Free for educators.</li>
      <li><strong>License the show</strong> — Pay once and receive everything as printable PDFs and downloadable audio.</li>
      <li><strong>Produce it</strong> — Rehearse and perform with complete materials. Copy scripts for your cast. Record your production. No restrictions on how you use the materials within your license period.</li>
    </ol>
    <a href="contact.html" class="btn btn-primary">Request a Perusal Copy</a>
  </section>

  <section class="section">
    <h2>MTWW vs. Traditional Publishers</h2>
    <p>Most school musical publishers (MTI, TRW, Concord) use a rental model with per-performance fees and mandatory material returns. Here's how MTWW compares:</p>
    <div class="table-wrap">
      <table class="compare-table">
        <thead>
          <tr><th>Feature</th><th class="center">MTWW</th><th class="center">Junior Versions</th></tr>
        </thead>
        <tbody>
{comp_rows}        </tbody>
      </table>
    </div>
  </section>

  <section class="section section-alt">
    <h2>Frequently Asked Questions</h2>
    <dl class="faq">
      <dt>What's included in the licensing fee?</dt>
      <dd>Script, piano/vocal score, vocal lead sheets, and backing tracks — all as printable PDFs and downloadable audio. No rental fees or per-script charges. You keep everything.</dd>

      <dt>Can we modify the show for our program?</dt>
      <dd>Contact us to discuss. Our shows are designed to be flexible with cast sizes and we're happy to work with you on adaptations.</dd>

      <dt>How long does the license last?</dt>
      <dd>License terms vary by show — typically unlimited performances within a calendar year or a 2-week performance period. See individual show pages for details.</dd>

      <dt>Can we record and share our production?</dt>
      <dd>Yes. MTWW licenses include video and YouTube rights for your production. Record it, share it with families, post it online.</dd>

      <dt>Do we need to return any materials?</dt>
      <dd>No. Everything is delivered as digital files that you keep. No scripts to mail back, no rental returns.</dd>

      <dt>Do you offer discounts for multiple shows?</dt>
      <dd>Contact us — we're happy to discuss packages for programs licensing more than one show.</dd>
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
<main>
  <section class="section">
    <h2>Get in Touch</h2>
    <div class="contact-grid">
      <div class="contact-card">
        <h3>Request a Perusal Copy</h3>
        <p>Want to read a script before licensing? Tell us which show and your organization name, and we'll send you a free perusal copy.</p>
        <a href="mailto:{site['email']}?subject=Perusal%20Request" class="btn btn-primary">Request a Perusal</a>
      </div>
      <div class="contact-card">
        <h3>General Inquiries</h3>
        <p>Questions about licensing, our shows, or anything else? We'd love to hear from you.</p>
        <p><a href="mailto:{site['email']}">{site['email']}</a></p>
        <p>{site['phone']}</p>
      </div>
      <div class="contact-card">
        <h3>About The Actors Garden</h3>
        <p>Looking for information about our youth theater program in Oak Park, Illinois?</p>
        <p><a href="https://theactorsgarden.com">Visit The Actors Garden &rarr;</a></p>
      </div>
    </div>
  </section>
</main>
""" + footer()
    write_page("contact.html", html)


def build_resources():
    """Build the resources/blog listing page."""
    resources = load_json("resources.json")

    cards = []
    for r in resources:
        cards.append(f"""    <article class="resource-card">
      <span class="resource-category">{r.get('category', '').replace('-', ' ').title()}</span>
      <h3><a href="{r['slug']}.html">{r['title']}</a></h3>
      <p>{r['description']}</p>
    </article>""")

    cards_html = "\n".join(cards)

    html = head(
        "Resources for Educators",
        "Guides, staging tips, and perspective from 30 years of producing youth musicals. Free resources for drama teachers and program directors.",
        canonical_path="resources.html"
    ) + nav("Resources") + f"""
<main>
  <section class="section">
    <h2>Resources for Educators</h2>
    <p>Practical guides and perspective from 30 years of producing musicals with young performers at The Actors Garden.</p>
    <div class="resource-grid">
{cards_html}
    </div>
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
            # Collect consecutive list items
            content_parts.append(f"<li>{para[2:]}</li>")
        else:
            # Convert inline markdown bold
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
    ) + nav("Resources") + f"""
<main>
  <article class="section article-content">
    <h1>{resource['title']}</h1>
    <p class="article-meta">Musical Theatre Worldwide &middot; {resource.get('date', '')}</p>
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
