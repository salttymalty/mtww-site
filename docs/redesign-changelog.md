# MTWW Redesign Changelog

> Date: 2026-03-07
> Session: Full information design audit and in-place redesign

---

## Summary

Redesigned the MTWW site from a publisher-brochure layout to an educator-workflow layout. Same stack, same data model, same deployment. All changes are in `build.py`, `output/styles.css`, and `data/site.json`.

## Files Modified

| File | What Changed |
|------|-------------|
| `build.py` | Rewrote all 8 page builders (index, shows, show detail, about, licensing, contact, resources, resource pages) |
| `output/styles.css` | Added new components, fixed accessibility violations, added reduced-motion support |
| `data/site.json` | Updated nav labels (Shows→Our Shows, What You Get→Production Kits, Resources→For Educators) |

## Files Created

| File | Purpose |
|------|---------|
| `docs/site-redesign-audit.md` | Full IA + usability + accessibility audit |
| `docs/proposed-sitemap.md` | Proposed site map with page purposes |
| `docs/redesign-changelog.md` | This file |

---

## Changes by Category

### Information Architecture

- **Homepage**: Restructured around educator workflow: hero ("Find the Right Musical") → quick-browse by grade/subject/cast → featured shows with comparison-ready cards → production kit summary → educator-centered value props → resources preview → final CTA
- **Navigation labels**: "What You Get" → "Production Kits", "Resources" → "For Educators"
- **Removed credential bar** from all pages (was duplicated mechanically across 4 pages). Credential now woven into hero text on show pages and homepage.
- **Removed comparison table** from homepage (was duplicated on homepage AND licensing page). Now lives only on the licensing page — its canonical location.
- **Resources page**: Grouped by educator need (Choosing a Show, Directing & Staging, Building a Program) instead of flat grid with category badges.

### Homepage (index.html)

- Hero text: "Original Musicals for Young Performers" → "Find the Right Musical for Your Students" (need-first, not identity-first)
- Added quick-browse section with linked cards: Elementary, Middle School+, Literary Adaptations, Large Cast
- Added "What You Get: Complete Production Kits" section with checklist + pricing summary
- Reframed "Why Choose MTWW?" → "Why Educators Choose MTWW" with teacher-centered copy ("Written for Your Students" not "Written for Young Performers")
- Added full-width "Read Any Script Free" final CTA block
- Removed comparison table (moved to licensing page only)

### Shows Page (shows.html)

- **Filter bar**: Added labeled filter groups (Grade: All/Elementary/Middle+ and Level: All/Beginner/Intermediate/Advanced)
- **Hash-based navigation**: Homepage browse cards link to `shows.html#elementary` etc., auto-activating the correct filter
- **Show cards**: Restructured with `<dl class="show-specs">` metadata grid (Ages, Cast, Runtime, Level), theme tags, price display, and "View details" CTA
- Cards now expose enough data for teachers to compare shows without clicking into each one

### Show Detail Pages ({show-id}.html)

- **Reordered sections** for teacher decision flow:
  1. Hero (with inline spec summary: ages, cast, runtime, price)
  2. At-a-glance spec card
  3. Synopsis (moved BEFORE any CTA — teacher needs to know what the show IS first)
  4. "Why This Works for Young Performers" (NEW — auto-generated from show data: casting flexibility, source material, difficulty level, intermission)
  5. Curriculum connections
  6. Details table (credits, premiere, production history)
  7. Production Kit + pricing
  8. FAQ (now collapsible accordion)
  9. "Read the Script Free" CTA (moved to END — after teacher has all info)
  10. Related shows
- **Removed "Battle-Tested" provenance box** from show pages (was marketing copy interrupting information flow)
- **Added show-hero-meta** bar with key specs visible in the hero itself

### Resources Page (resources.html)

- Grouped articles by category: "Choosing a Show" (guides), "Directing & Staging" (directors-guides), "Building a Program" (philosophy)
- Removed category badges from cards (grouping makes them redundant)
- Removed dates from article meta (all were 2026-03-06, looked auto-generated)

### Licensing Page (licensing.html)

- Now the single canonical location for the MTWW vs Junior comparison table (no longer duplicated on homepage)
- Added "Why It Matters" column to comparison table
- Nav label: "What You Get" → "Production Kits"

### Accessibility Fixes

- **Added skip-to-content link** (`<a href="#main" class="skip-link">Skip to content</a>`)
- **Added `id="main"`** to all `<main>` elements
- **Fixed `.badge-diff` font size**: 0.6875rem (11px) → 0.75rem (12px) — was violating 12px floor
- **Fixed `.btn-sm` min-height**: 36px → 44px — was violating touch target minimum
- **Added `prefers-reduced-motion` media query**: disables all transitions/animations for users who prefer reduced motion
- **FAQ accordion**: collapsible with `+`/`−` indicators, proper focus handling

### CSS

New component styles added:
- `.skip-link` — skip-to-content
- `.browse-card`, `.browse-grid` — homepage quick-browse
- `.show-specs`, `.show-tag`, `.show-tags` — structured metadata in show cards
- `.show-card-footer`, `.show-price`, `.show-card-cta` — card footer with price
- `.why-works-grid`, `.why-works-item` — show-specific educator benefits
- `.kit-summary`, `.kit-summary-list`, `.kit-summary-cta` — homepage kit preview
- `.final-cta` — full-width CTA blocks
- `.filter-group`, `.filter-label` — labeled filter groups
- `.resource-group` — grouped resource sections
- `.testimonial-grid`, `.testimonial-card` — testimonial components (ready for data)
- `.hero-credential`, `.show-hero-meta` — hero metadata display
- `.btn-outline` — secondary button for light backgrounds
- `prefers-reduced-motion` — motion safety

### Copy Changes

- Hero: identity-first → need-first ("Find the right musical for your students")
- Value cards: publisher-centered → teacher-centered ("Written for Your Students" not "Written for Young Performers")
- Reduced "battle-tested" repetition (was on homepage, show pages, about page)
- Removed date from article meta (was same date on all articles)
- CTA labels: more specific ("Request a Free Perusal" not just "Read a Script Free")

### What Was NOT Changed

- Data model (shows.json, people.json, resources.json, testimonials.json, site.json structure)
- Build infrastructure (JSON → Python → HTML pipeline)
- Deployment (GitHub Pages via Actions)
- SEO infrastructure (Schema.org, OG tags, sitemap, canonical URLs)
- About page content (same structure, same copy)
- Contact page structure
- Blog post content
- Show data

---

## Verification

21/21 automated checks passed covering:
- Skip link + main landmark
- Homepage structure (hero, browse, kit summary, final CTA, no credential bar, educator-centered copy)
- Show page section ordering (synopsis before CTA, why-works, curriculum before kit)
- Show page features (collapsible FAQ, hero meta specs)
- Resources grouping and nav label
- Shows page filters (difficulty group, hash navigation, specs grid)
- CSS fixes (skip link, reduced motion, badge font fix, button height fix)

---

*Redesign by Garen + Claude, 2026-03-07*
