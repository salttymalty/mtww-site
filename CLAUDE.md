# Musical Theatre Worldwide — Site Rebuild

## What This Is

The new website for **Musical Theatre Worldwide**, replacing the Squarespace site at musicaltheatreworldwide.com. It's a static site generator: you edit JSON data files, run a build script, and push to GitHub. The site deploys automatically.

**Live preview:** https://salttymalty.github.io/mtww-site/

## How It Works

```
data/*.json  →  python3 build.py  →  output/*.html  →  GitHub Pages (auto-deploy on push)
```

1. Edit data in `data/` (shows, people, site config, resources)
2. Run `python3 build.py` to regenerate all pages
3. `git add . && git commit -m "description" && git push` to deploy

That's it. Changes go live in about a minute after pushing.

## Quick Commands

```bash
python3 build.py              # Build all 20 pages
python3 build.py --check      # See what data is missing
python3 build.py --show X     # Build one show page by id
open output/index.html        # Preview locally before pushing
```

## What's on the Site Right Now

- **6 site pages:** Home, Shows, Licensing, Resources, About, Contact
- **7 show pages:** Just So, Becky Thatcher, Off to Olympus, Pots and Pan, Tut Tut!, Bounce!, The Show Must Go Online
- **5 blog posts** for teachers (choosing a musical, staging Just So, etc.)
- **SEO infrastructure:** Schema.org markup, sitemap.xml, Open Graph tags, meta descriptions
- **Richard Rodgers Award** prominently featured on every page (it wasn't mentioned anywhere on the old site)

The three BBB shows (Tut Tut!, Bounce!, The Show Must Go Online) link out to Beat by Beat's site. The four MTWW shows are the focus.

## Current State (March 2026)

Just So, Becky Thatcher, and Off to Olympus have full show pages with details, FAQs, and curriculum connections. Pots and Pan is a placeholder — needs your input to fill out. All shows still need production photos and audio samples.

Run `python3 build.py --check` anytime to see what's filled in and what's still open.

---

## Open Items (Your Call)

### Pots and Pan

Edit `data/shows.json`, find the `pots-and-pan` entry. Here's what's open:
- `synopsis` — 2-3 sentences about the show
- `music_by` — who composed it?
- `runtime_minutes` — approximate
- `has_intermission` — true or false
- `age_range` — e.g. "4th grade and up"
- `min_age` — number, e.g. 9
- `cast_size` — number of speaking roles
- `cast_notes` — e.g. "25 speaking roles plus flexible chorus"
- `song_count` — number
- `licensing_price` — 299 or 399 or whatever
- `licensing_notes` — e.g. "Unlimited performances within a 2-week calendar period"
- `licensing_includes` — copy from Just So's entry if the same
- `difficulty` — "beginner-friendly", "intermediate", or "intermediate-advanced"
- `faq` — array of `{"q": "...", "a": "..."}` objects (see Just So for examples)
- `curriculum_connections` — array of strings

### Premiere Years & Production History

- **Premiere years** for Becky Thatcher, Off to Olympus, Pots and Pan — `premiere_year` and `premiere_venue` in shows.json
- **Production history** — anything worth noting (cities, countries, number of productions)

### The Full Catalog

7 shows are in `shows.json` so far. Some others we could add:

**With Paul Libman (Northern Sky Theater):**
- A Cabin with a View, Bing! The Cherry Musical, Bringers, Cheeseheads!, Dust and Dreams, Good Knight, Main-Travelled Roads, Muskie Love, Naked Radio, No Bones About It, Strings Attached

**With Denise Wright:**
- Jacob's Pillow, Saint Peter's UmbrElla, TRaIN

**Other:**
- Upon Reflection (with Jon Steinhagen)

**Open question:** Should the Northern Sky/Libman catalog appear on this site? They're not MTWW-licensed, but they could live in an "Other Works" section. Up to you.

### Assets (When Ready)

- **Production photos** — put in `assets/images/`, name them `{show-id}-01.jpg`, `{show-id}-02.jpg`, etc.
- **Audio samples** — put in `assets/audio/`, name them `{show-id}-{song-name}.mp3`
- **Headshots** — for you, GiGi, Paul, and other collaborators. Put in `assets/images/`
- **Testimonials** — quotes from schools, directors, teachers who've done your shows. Even 2-3 would transform the site.

Once assets are in the folders, we'll wire them into the build script.

See ~/decisions/2026-03-08-mtww-vimeo-download-strategy.md for rationale on video download division of labor.

---

## How to Add a New Show

1. Open `data/shows.json`
2. Copy an existing entry (Just So is the most complete)
3. Change the `id` (lowercase, hyphens, e.g. `"no-bones-about-it"`)
4. Fill in what you know, set unknowns to `null`
5. Set `available_on_mtww` to `true` if it's licensed through MTWW, `false` if not
6. Set `status` to `"active"` if complete, `"needs_data"` if partial
7. Run `python3 build.py` — the show appears on the site
8. Commit and push to deploy

## How to Edit Existing Content

All content lives in `data/`. The build script reads it and generates HTML.

- **Show details:** `data/shows.json`
- **People/bios:** `data/people.json`
- **Site config** (nav, tagline, pricing defaults): `data/site.json`
- **Blog posts:** `data/resources.json`

Never edit files in `output/` directly — they get overwritten on every build.

## Project Structure

```
mtww-site/
├── CLAUDE.md          ← You are here
├── BUILD-PLAN.md      ← Full task list (what's done, what's left)
├── build.py           ← Site generator
├── data/
│   ├── shows.json     ← All musicals — THIS IS THE MAIN FILE YOU'LL EDIT
│   ├── people.json    ← Founders + collaborators
│   ├── resources.json ← Blog posts for educators
│   ├── testimonials.json ← Ready for real testimonials when you have them
│   └── site.json      ← Site config (nav, contact, licensing defaults)
├── assets/
│   ├── images/        ← Drop production photos and headshots here
│   └── audio/         ← Drop audio samples here
└── output/            ← Generated HTML (don't edit, run build.py instead)
```

## Constraints

- **No pip dependencies** — stdlib Python 3 only
- **No JavaScript frameworks** — vanilla JS only
- **No purple gradients** — house rule
- CSS custom properties for theming

## Who's Working on This

- **Dave** — Content, show data, creative direction. This is your site.
- **Garen** — Infrastructure, code, deployment. If something breaks after a push, just holler.
- **GiGi** — Feedback and direction as needed.

## How the Site Is Structured

The site leads with philosophy (original musicals written for kids, not Junior versions) and makes it easy for a teacher to browse shows, compare specs, and request a perusal copy. There's a credential bar on key pages, a comparison table (MTWW vs Junior versions), and 5 blog posts targeting search queries teachers actually use.

Beat by Beat Press is the main competitor in this space. The site is designed to highlight what MTWW does differently — but you know that landscape better than anyone. If the framing feels off anywhere, change it.

The thing the site needs most right now is **content that only you can provide** — show details, production history, the stories behind the shows, and eventually photos and audio.
