# MTWW Site Rebuild — Build Plan

> Updated: 2026-03-06
> A task bucket for the MTWW site rebuild.

## Current State

- **20 pages generating** from `build.py` (6 site pages + 7 show pages + 5 resource pages + sitemap + robots)
- **7 shows** in `data/shows.json` (3 fully active, 1 needs data, 3 external-license)
- **7 people** in `data/people.json`
- **5 blog posts** in `data/resources.json`
- **Stylesheet** with Playfair Display + Source Sans 3, OKLCH tokens, responsive grid, mobile hamburger
- **SEO infrastructure:** Schema.org JSON-LD, Open Graph tags, canonical URLs, sitemap.xml, robots.txt
- **GitHub Pages deployment** via Actions on push to main
- **No images or audio yet** — empty asset directories

Run `python3 build.py --check` anytime to see what data is missing.

---

## Completed

### Phase 1: Learn the Pattern
- [x] 1.1 — Initial shows.json with 7 shows
- [x] 1.2 — Off to Olympus details filled from Squarespace audit (runtime, cast, songs, price, FAQ)
- [x] 1.3 — Testimonials data structure (`data/testimonials.json`) — awaiting real testimonials
- [x] 1.4 — Data completeness check with expanded field list

### Phase 2: Design & CSS
- [x] 2.1 — Display font: Playfair Display (via Google Fonts)
- [x] 2.2 — Show hero images: structure ready, awaiting assets
- [x] 2.3 — Color palette: warm burgundy/cream theater palette with OKLCH tokens
- [x] 2.4 — Hover/focus states on all interactive elements (`:focus-visible` on all buttons and links)

### Phase 3: New Pages & Features
- [x] 3.1 — Resources page (5 blog posts for educators)
- [x] 3.2 — Audio samples: structure ready in shows.json, awaiting audio files
- [x] 3.3 — Show filtering on Shows page (All/Elementary/Middle School+)
- [x] 3.4 — External shows section ("Other Works by Dave Hudson")

### Phase 4: SEO & Metadata
- [x] 4.1 — Open Graph tags on all pages
- [x] 4.2 — Schema.org JSON-LD (Product, Organization, FAQPage)
- [x] 4.3 — Sitemap.xml generator
- [x] 4.4 — Canonical URLs on all pages
- [x] 4.5 — Keyword-rich meta descriptions per page
- [x] 4.6 — robots.txt

### Phase 5: Deployment
- [x] 5.1 — Git repo initialized
- [x] 5.2 — GitHub Pages deployment workflow
- [ ] 5.3 — Domain migration plan (Squarespace → GitHub Pages)
- [ ] 5.4 — Contact form without backend (currently mailto links)

### Additional (from Audit)
- [x] Credential bar (Richard Rodgers Award) on key pages
- [x] Show spec cards (scannable at-a-glance grid)
- [x] Show FAQ sections per show
- [x] Show cross-linking ("You Might Also Like")
- [x] Curriculum connections per show
- [x] MTWW vs Junior comparison table
- [x] Mobile hamburger navigation
- [x] Blog posts targeting teacher search queries
- [x] Implementation specs doc (`mtww-site-updates-2026.md`)

---

## Remaining Work

### Needs Dave/GiGi
- [ ] Pots and Pan: all details (synopsis, cast, runtime, songs, price, composer)
- [ ] Premiere years for Becky Thatcher, Off to Olympus, Pots and Pan
- [ ] Production photos for all shows
- [ ] Audio samples for all shows
- [ ] Headshot photos for founders/collaborators
- [ ] Testimonials from schools/programs
- [ ] Whether Northern Sky/Libman catalog should appear
- [ ] ~4-8 additional musicals from Dave's catalog
- [ ] SoundSlice practice tracks (requires Demucs pipeline)

### Technical (Garen)
- [ ] Domain migration: DNS from Squarespace to GitHub Pages
- [ ] Contact form: Formspree or Cloudflare Workers
- [ ] PayHip integration: buy buttons linking to checkout
- [ ] Newsletter signup: email collection form
- [ ] Production photo galleries (lightbox JS)
- [ ] Analytics: Cloudflare Web Analytics or Plausible
- [ ] More blog posts (5 additional topics identified)
- [ ] Write 5 more resource articles for long-tail SEO

---

## Quick Reference

```bash
# Build everything
python3 build.py

# Check data gaps
python3 build.py --check

# Build one show
python3 build.py --show just-so

# Preview locally
open output/index.html
```
