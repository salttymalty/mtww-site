# Musical Theatre Worldwide — Site Rebuild

## What This Is

A data-driven static site for **Musical Theatre Worldwide** (MTWW), the musical licensing company founded by GiGi Hudson (Artistic Director) and Dave Hudson (playwright/lyricist). MTWW publishes original musicals written for young performers, born out of The Actors Garden in Oak Park, IL.

**Current site:** musicaltheatreworldwide.com (Squarespace 7.1) — being replaced by this project.

## Stack

- **Data:** JSON files in `data/` — shows, people, site config
- **Build:** `build.py` — stdlib Python 3, reads JSON, generates HTML to `output/`
- **Style:** `output/styles.css` — CSS custom properties, responsive, no frameworks
- **Deploy:** TBD — likely Cloudflare Pages with git auto-deploy

## Project Structure

```
mtww-site/
├── CLAUDE.md          ← You are here
├── BUILD-PLAN.md      ← Task bucket for the full rebuild
├── build.py           ← Site generator (python3 build.py)
├── data/
│   ├── shows.json     ← All musicals (MTWW + external catalog)
│   ├── people.json    ← Founders + collaborators
│   └── site.json      ← Site config (nav, contact, licensing defaults)
├── templates/         ← (future) HTML template fragments
├── assets/
│   ├── images/        ← Show photos, headshots
│   └── audio/         ← Song samples
└── output/            ← Generated HTML (do not edit directly)
```

## Key Commands

```bash
python3 build.py           # Build all pages
python3 build.py --check   # Data completeness report
python3 build.py --show X  # Build one show page by id
```

## Data Model

### shows.json
Each show has: `id`, `title`, `tagline`, `synopsis`, `source_material`, `book_by`, `music_by`, `lyrics_by`, `runtime_minutes`, `has_intermission`, `age_range`, `min_age`, `cast_size`, `cast_notes`, `song_count`, `licensing_price`, `licensing_notes`, `licensing_includes`, `premiere_year`, `premiere_venue`, `notable_productions`, `available_on_mtww`, `status`, `hero_image`, `audio_samples`

**Status values:** `active` (ready), `needs_data` (waiting on Dave), `external_license` (licensed through Beat by Beat or others)

### people.json
Each person has: `id`, `name`, `role`, `bio`, `is_founder`, `awards`, `collaborators`, `photo`

## Constraints

- **No pip dependencies** — stdlib Python 3 only
- **No JavaScript frameworks** — vanilla JS only
- **12px font floor** — nothing smaller
- **44px touch targets** — minimum for interactive elements
- **No purple gradients**
- CSS custom properties for theming (not hardcoded colors)

## What's Missing (Needs Dave)

- Full catalog — only 7 of 25+ musicals are in `shows.json`
- Show details for Off to Olympus and Pots and Pan (synopsis, cast, runtime, songs)
- Composer for Pots and Pan
- Production photos
- Audio samples
- Headshot photos for founders and collaborators
- Testimonials from schools/programs that have produced the shows
- Whether the Northern Sky/Libman catalog should appear on the site or stay separate

## People Context

- **Dave Hudson** — Garen's father. Playwright with 25+ musicals, two-time Richard Rodgers Award winner.
- **GiGi Hudson** — Garen's mother. Artistic Director of Actors Garden and MTWW.
- **The person rebuilding this site** is learning Claude Code. The project is structured as a teaching exercise with self-contained, progressively challenging tasks.
