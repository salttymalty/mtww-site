# MTWW Site Redesign Audit

> Date: 2026-03-07
> Scope: Full information design + usability audit of the MTWW static site
> Audience: Drama teachers, youth program directors, school administrators

---

## Current State

- 20 pages generated from `build.py` (6 site + 7 show + 5 resource + sitemap + robots)
- 7 shows in catalog (3 complete MTWW, 1 needs data, 3 external via BBB)
- 5 blog posts targeting teacher search queries
- SEO infrastructure complete (Schema.org, OG tags, sitemap, canonical URLs)
- GitHub Pages deployment working
- No images, audio, or real testimonials yet
- Responsive down to 480px with hamburger nav

## What's Working

1. **Data-driven architecture.** JSON files + Python builder is clean, maintainable, and appropriate. No reason to change the stack.
2. **SEO foundation.** Schema.org Product/FAQ/Org markup, sitemaps, canonical URLs, keyword-rich meta descriptions — solid.
3. **Show data model.** `shows.json` has the right fields for teacher decision-making. The structure supports comparison, filtering, and detail pages.
4. **Blog content.** 5 articles targeting real teacher search queries. Good content, well-written.
5. **CSS tokens.** OKLCH palette, semantic variables, warm-tinted shadows, proper spacing scale.
6. **Accessibility basics.** Focus-visible states, aria-labels, 44px touch targets (mostly), mobile hamburger with aria-expanded.

## Information Architecture Issues

### 1. Site is organized around MTWW, not around teachers

The current IA tells the MTWW story: who we are, what we offer, why we're different. Teachers visiting the site have a different set of questions:

- Is this right for my students? (age, difficulty, content)
- How many students can I cast?
- How long is it?
- What do students learn?
- What comes in the kit? What does it cost?
- Can I read it before committing?

The site answers all of these — but you have to dig. Teacher questions should be answerable within 10 seconds of landing on the right page.

### 2. Homepage doesn't serve educator workflow

Teachers arriving at the homepage need to quickly navigate to a show that fits their program. The current homepage leads with a philosophical hero ("Original Musicals for Young Performers"), then "Our Shows" cards, then "Why Choose MTWW?" value cards, then a comparison table, then resource links.

Missing from homepage:
- **Quick-browse by need** (by grade, by cast size, by subject area)
- **Featured shows with enough metadata to compare** (age, cast, runtime visible in cards)
- **What's in a Production Kit** summary (teachers need this early — it's the product)
- **Trust signals** (testimonials placeholder, credential bar could be richer)
- **A clear "find the right show" path** rather than just "browse our shows"

### 3. Shows page: cards lack comparison density

Show cards display: title, tagline, meta (runtime, cast, age, price), credits. But:
- Curriculum connections aren't visible at card level
- Difficulty badge is small and easily missed
- No themes or subject-area tags visible
- No way to compare shows side-by-side without clicking into each one
- Filter bar is too limited (All/Elementary/Middle School+) — missing difficulty, cast size, subject area

### 4. Show pages: sections are in suboptimal order

Current order: Spec card → Perusal CTA → Synopsis → Battle-Tested box → Details table → Curriculum → Kit/Price → FAQ → Related shows.

Issues:
- **Perusal CTA comes before synopsis.** Teacher needs to know WHAT the show is before being asked to read the script.
- **"Battle-Tested" provenance box** is marketing copy, not decision information. It interrupts the flow between synopsis and practical details.
- **Curriculum connections are buried** below details table. For teachers choosing between shows for a specific unit, this is primary decision data.
- **No "Why This Works for Young Performers"** section that speaks to the specific strengths of THIS show (not generic MTWW benefits).
- **No learning outcomes** distinct from curriculum connections. Teachers need to articulate educational value to administrators.

### 5. Resources page is flat

5 articles in a single grid with category labels. No hierarchy, no grouping, no progressive disclosure. For 5 articles this is fine, but the structure doesn't scale and doesn't help teachers find what they need.

Categories exist in data (`guides`, `philosophy`, `directors-guides`) but aren't used for navigation or grouping.

### 6. Licensing page duplicates homepage content

The comparison table (MTWW vs Junior) appears on both the homepage AND the licensing page. The FAQ on the licensing page largely restates what show pages already say. This page should be the definitive reference for "what do I get and how does it work" — not a repeat of the homepage pitch.

### 7. Redundant credential bar

The credential bar appears on Home, Shows, Licensing/What You Get, and About pages with identical content. By the third page, it's wallpaper. The credential should be woven into the pages where it matters, not stamped across the top mechanically.

## Design / CSS Issues

### Violations

- `.badge-diff` font-size is `0.6875rem` = **11px** — violates 12px floor
- `.btn-sm` min-height is `36px` — violates 44px touch target minimum

### Opportunities

- Show cards could use a more structured layout (left-aligned metadata list instead of inline dots)
- Spec card on show pages works well but would benefit from subtle icons
- No skip-to-content link (accessibility)
- Hero `.show-hero-sub` at `opacity: 0.65` may fail WCAG contrast — needs verification
- No `prefers-reduced-motion` media query for hover transforms

## Content / Copy Issues

1. **"Battle-tested" is overused.** Appears in hero, show pages, about page, value cards. Loses meaning through repetition.
2. **Publisher voice vs. teacher voice.** Copy leads with "we" and "our" rather than "you" and "your students." Teacher-centered copy converts better.
3. **"Award-Winning Original Musicals for Young Performers"** is accurate but generic. Every publisher claims their shows are "award-winning."
4. **Blog post dates are all 2026-03-06.** Looks auto-generated. Consider removing dates or staggering them.
5. **No clear "how to get started" path** from the homepage — the CTA is "Browse Our Shows" which is browsing, not a workflow.

## Recommended Changes (Summary)

### Information Architecture
- Restructure homepage around educator workflow: need → browse → evaluate → act
- Add quick-browse section (by grade level, by subject, by cast size)
- Make show cards comparison-friendly (expose more metadata)
- Reorder show page sections for teacher decision-making
- Group resources by educator need, not by internal category
- Consolidate licensing information — remove duplication

### Show Pages (Reorder)
1. Hero with title, tagline, credential, quick-spec summary
2. At-a-glance spec card
3. Synopsis
4. Why this works for young performers (show-specific)
5. Curriculum connections + learning outcomes
6. What's in your Production Kit + pricing
7. FAQ (collapsible)
8. Perusal CTA (after they know what it is)
9. Related shows

### Shows Page
- Richer filter bar (grade level, difficulty, subject area)
- Denser cards with visible curriculum tags and difficulty
- Optional: comparison table view for side-by-side evaluation

### Homepage
- Hero: clear value prop + immediate path to shows
- Quick-browse by grade/need
- Featured shows with comparison-ready cards
- What's in a Production Kit (brief)
- Why educators choose MTWW (reframed from teacher perspective)
- Educator resources preview
- Testimonials section (ready for data)
- Clear CTA: "Read any script free"

### Design Fixes
- Fix 11px badge font (→ 12px)
- Fix 36px button min-height (→ 44px)
- Add skip-to-content link
- Add prefers-reduced-motion
- Improve credential bar usage (contextual, not mechanical)

---

*Audit by Garen + Claude, 2026-03-07*
