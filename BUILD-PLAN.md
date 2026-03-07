# MTWW Site Rebuild — Build Plan

> A task bucket for someone learning Claude Code by rebuilding musicaltheatreworldwide.com.
> Each task is self-contained and progressively more challenging.
> The site is data-driven: edit JSON, run `python3 build.py`, see results.

## Current State

- **12 pages generating** from `build.py` (5 site pages + 7 show pages)
- **7 shows** in `data/shows.json` (2 need data, 3 are external-license)
- **7 people** in `data/people.json` (most need bios)
- **Stylesheet** in place with OKLCH tokens, responsive grid, theater palette
- **No images, no audio, no deployment** yet

Run `python3 build.py --check` anytime to see what data is missing.

---

## Phase 1: Learn the Pattern (Data → Build → HTML)

These tasks teach the core workflow: edit a JSON file, run the build script, see the change.

### 1.1 — Add a missing show to shows.json
**What:** Pick a musical from the full catalog (see below) and add it to `data/shows.json`.
**How:** Copy an existing entry, change the fields, run `python3 build.py`.
**Learn:** JSON structure, the data model, how the build script reads data.
**Verify:** The show appears on `shows.html` and has its own detail page.

### 1.2 — Fill in Off to Olympus details
**What:** Get details from Dave (or research) for Off to Olympus — synopsis, cast size, runtime, etc.
**How:** Edit the `off-to-olympus` entry in `shows.json`, change `status` from `needs_data` to `active`.
**Learn:** How status fields control rendering (the "Coming Soon" badge disappears).

### 1.3 — Add a testimonial
**What:** Create `data/testimonials.json` with at least one school/program testimonial.
**How:** Design the JSON structure, then modify `build.py` to read it and add a testimonials section to `index.html`.
**Learn:** How to extend the data model and modify the build script.

### 1.4 — Run the data completeness check
**What:** Run `python3 build.py --check` and read the report.
**How:** Just run it. Then fill in one or two missing fields.
**Learn:** How data quality tools work. This is a pattern used across the ecosystem.

---

## Phase 2: Design & CSS (Visual Polish)

### 2.1 — Choose a display font
**What:** The site currently uses Georgia as a fallback. Pick a Google Font for `--font-display`.
**How:** Edit the `:root` tokens in `styles.css`, add a `<link>` to the Google Fonts stylesheet in `build.py`'s `head()` function.
**Options to consider:** Playfair Display, Cormorant, Vollkorn, Lora.
**Learn:** CSS custom properties, how tokens cascade through the whole site.

### 2.2 — Add show hero images
**What:** Add a hero image area to show detail pages.
**How:** Put images in `assets/images/`, add `hero_image` paths to `shows.json`, modify `build_show_page()` in `build.py`.
**Learn:** How the build script templates content, image paths in static sites.

### 2.3 — Refine the color palette
**What:** The current palette is warm burgundy/cream. Explore alternatives or refine.
**How:** Edit the OKLCH values in `:root`. Use oklch.com to experiment.
**Learn:** OKLCH color space (perceptually uniform — changing lightness doesn't shift hue).

### 2.4 — Add hover/focus states to all interactive elements
**What:** Ensure every link, button, and card has visible hover and focus states.
**How:** Add `:focus-visible` rules to `styles.css`.
**Learn:** Accessibility basics, keyboard navigation, the 44px touch target rule.

---

## Phase 3: New Pages & Features

### 3.1 — Build a "For Directors" resource page
**What:** A page that helps school directors understand what makes MTWW shows different.
**How:** Add the page to `site.json` nav, write a new `build_directors()` function in `build.py`.
**Learn:** Adding a new page to a data-driven static site.

### 3.2 — Add audio samples to show pages
**What:** Some shows have sample songs. Add `<audio>` players to show detail pages.
**How:** Put audio files in `assets/audio/`, add `audio_samples` entries to `shows.json`, modify `build_show_page()`.
**Learn:** HTML `<audio>` element, media hosting considerations.

### 3.3 — Add filtering to the Shows page
**What:** Let visitors filter shows by age range or cast size.
**How:** Add a small vanilla JS script that reads data attributes on show cards and shows/hides them.
**Learn:** Progressive enhancement (page works without JS, filter is a bonus).

### 3.4 — Build a "Dave Hudson: Full Catalog" page
**What:** A page showing ALL of Dave's musicals (not just MTWW-licensed ones), organized by collaborator.
**How:** Add a `catalog_section` field to shows, group by collaborator in a new build function.
**Learn:** Data transformation, grouping, rendering structured data.

---

## Phase 4: SEO & Metadata

### 4.1 — Add Open Graph tags
**What:** When someone shares a show page on social media, it should show title, description, and image.
**How:** Add `<meta property="og:*">` tags in the `head()` function, pulling from show data.
**Learn:** Social media metadata, how crawlers read pages.

### 4.2 — Add Schema.org structured data
**What:** Help Google understand that these are creative works available for licensing.
**How:** Add `<script type="application/ld+json">` blocks with `CreativeWork` schema.
**Learn:** Structured data, JSON-LD, Schema.org vocabulary.

### 4.3 — Add a sitemap.xml generator
**What:** Generate a `sitemap.xml` that lists all pages.
**How:** Add a `build_sitemap()` function to `build.py`.
**Learn:** XML generation, SEO infrastructure.

---

## Phase 5: Deployment

### 5.1 — Initialize a git repo
**What:** Version-control the project.
**How:** `git init`, create a `.gitignore` (ignore `output/` or not — your choice), make an initial commit.
**Learn:** Git basics, what to track vs. what to generate.

### 5.2 — Deploy to Cloudflare Pages
**What:** Get the site live on a preview URL.
**How:** Push to GitHub, connect Cloudflare Pages, set `output/` as the publish directory.
**Learn:** Static site deployment, CI/CD basics.

### 5.3 — Domain migration plan
**What:** Document how to point `musicaltheatreworldwide.com` from Squarespace to Cloudflare.
**How:** Write a migration checklist: DNS records, SSL, redirects for old Squarespace URLs.
**Learn:** DNS, domain management, migration planning.

### 5.4 — Add a contact form without a backend
**What:** Replace the mailto link with a real form.
**How:** Use Formspree, Cloudflare Workers, or similar service.
**Learn:** Serverless form handling, third-party integrations.

---

## Phase 6: Stretch Goals

### 6.1 — Integrate PayHip for licensing purchases
**What:** The current site uses PayHip. Add buy buttons that link to PayHip checkout.
**How:** Add `payhip_url` to `shows.json`, render buy buttons on show pages.

### 6.2 — Add a newsletter signup
**What:** Email collection for show announcements.
**How:** Embed a form that connects to their email service.

### 6.3 — Production photo gallery
**What:** A lightbox-style gallery on each show page.
**How:** Vanilla JS lightbox, images organized by show in `assets/images/`.

### 6.4 — Privacy-respecting analytics
**What:** Add Cloudflare Web Analytics or Plausible.
**How:** One `<script>` tag in the footer. No cookies, no tracking.

---

## Dave's Full Catalog (Research Summary)

Shows we found online but that aren't yet in `shows.json`:

### With Paul Libman (Northern Sky Theater)
- A Cabin with a View (E.M. Forster, 2006)
- Bing! The Cherry Musical (Chekhov/Door County, 2011)
- Bringers (Sandburg, Richard Rodgers Award 2005)
- Cheeseheads! The Musical (original, 2009)
- Dust and Dreams (Sandburg, Richard Rodgers Award 2005)
- Good Knight (status unclear)
- Main-Travelled Roads (Hamlin Garland, Richard Rodgers Award 2007)
- Muskie Love (Much Ado About Nothing, 2004)
- Naked Radio (original, 2017)
- No Bones About It (Romeo & Juliet, 2015)
- Strings Attached (Comedy of Errors, 2014)

### With Denise Wright
- Jacob's Pillow (2008)
- Saint Peter's UmbrElla (2005)
- TRaIN (2004, workshopped in Glasgow)

### Other
- Upon Reflection (with Jon Steinhagen, 2003)

**~4-8 musicals still unaccounted for.** Ask Dave directly.

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
