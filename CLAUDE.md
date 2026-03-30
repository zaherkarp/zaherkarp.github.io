# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A personal portfolio and blog site for a healthcare data engineering professional. Built with Astro 5, React 19, and Tailwind CSS v4. All site content is centralized in a single configuration file (`src/config.ts`). The site includes a blog with 60+ markdown posts, an interactive career trajectory tool (SkillSprout), and auto-deploys to GitHub Pages.

## Tech Stack

- **Astro 5**: Static site generator with file-based routing and content collections
- **React 19**: Used for interactive components (SkillSprout demo) via `@astrojs/react`
- **Tailwind CSS v4**: Utility-first CSS via `@tailwindcss/vite` plugin
- **TypeScript**: Strict mode (`astro/tsconfigs/strict`)
- **Tabler Icons**: Inline SVGs for all icons
- **KaTeX / Mermaid**: Math and diagrams in blog posts (loaded via CDN)

## Development Commands

```bash
npm run dev       # Start development server
npm run build     # Build for production (outputs to dist/)
npm run preview   # Preview production build
```

No linting or testing framework is configured. Validate changes with `npm run build`.

## Project Structure

```
src/
├── components/         # Astro (.astro) and React (.tsx/.jsx) components
│   ├── Header.astro, Hero.astro, About.astro, Projects.astro
│   ├── Experience.astro, Education.astro, Publications.astro
│   ├── Presentations.astro, Contact.astro, Footer.astro
│   ├── LatestPosts.astro, Now.astro, GitHubActivity.astro
│   ├── BaseHead.astro          # SEO meta tags, Open Graph, JSON-LD
│   ├── ThemeToggle.astro       # Dark/light mode with localStorage
│   ├── SkillSproutDemo.tsx     # Main React interactive component
│   └── LifeInWeeks.jsx
├── pages/
│   ├── index.astro             # Single-page portfolio (imports all section components)
│   ├── blog/
│   │   ├── index.astro         # Blog listing page
│   │   └── [...slug].astro     # Dynamic blog post template
│   ├── skillsprout/index.astro # SkillSprout page shell
│   └── life-in-weeks.astro
├── content/
│   ├── blog/                   # 60+ markdown posts with YAML frontmatter
│   └── config.ts               # Astro content collection schema
├── data/
│   ├── onet-full.json          # O*NET 28.3 database (1,016 occupations)
│   ├── onet-occupations.ts     # Compiled O*NET data for SkillSprout
│   └── skillsprout-test-cases.ts
├── lib/
│   ├── skillsprout-engine.ts   # IDF-weighted Jaccard matching algorithm
│   └── skillsprout-api.ts      # Session state management for SkillSprout
├── styles/
│   ├── global.css              # CSS custom properties, dark mode, Tailwind import
│   └── blog.css                # Blog typography and layout
└── config.ts                   # SINGLE SOURCE OF TRUTH for all site content
```

Other key files:
- `astro.config.mjs` — Astro config: site URL, React + sitemap integrations, Tailwind vite plugin
- `.github/workflows/deploy.yml` — Auto-deploy to GitHub Pages on push to master
- `.github/workflows/new-blog-post.yml` — Create blog posts via GitHub Actions
- `.github/workflows/publish-blog-post.yml` — Publish draft posts via GitHub Actions
- `scripts/process-onet.mjs` — O*NET data pipeline script
- `docs/skillsprout.md` — SkillSprout architecture documentation

## Architecture

### Single Configuration File (`src/config.ts`)

All content is managed through `siteConfig`:
- **Basic info**: name, fullName, title, metaTitle, description, accentColor
- **Color palettes**: light and dark theme colors (accent, text, border, background)
- **Social links**: email, linkedin, github, researchGate, tableau, blog (all optional)
- **aboutMe**: bio string
- **skillCategories**: array of {name, color, skills[]}
- **publications**: array of {title, journal, authors, year, link, semanticScholarId, skills, citations}
- **projects**: array of {name, description, link, skills, citations?}
- **experience**: array of {company, title, dateRange, context?, bullets}
- **presentations**: array of {title, venue, date, description?, link?}
- **education**: array of {school, degree, dateRange, achievements}

### Key Architectural Decisions

1. **Single Configuration File**: All content in `src/config.ts` — components import `siteConfig` directly
2. **Conditional Rendering**: Sections auto-hide if their config data is empty/missing
3. **Component Independence**: Each section is self-contained; reads from config
4. **Theme System**: Light/dark mode via `data-theme` attribute + CSS custom properties + localStorage
5. **Islands Architecture**: React only loads on pages that need interactivity (SkillSprout uses `client:load`)
6. **Email Masking**: Email addresses assembled from parts in JavaScript to prevent scraping

### Blog System

- Uses Astro Content Collections with Zod schema validation
- Frontmatter: `title`, `description`, `publishDate`, `draft` (optional), `tags` (optional)
- Posts sorted by `publishDate` descending; drafts filtered from listing
- Supports KaTeX math (`$...$` and `$$...$$`) and Mermaid diagrams
- JSON-LD Article schema on each post for SEO
- Blog posts can be created/published via GitHub Actions workflows

### SkillSprout (Career Trajectory Engine)

Fully client-side React app — no data leaves the browser:
- `src/lib/skillsprout-engine.ts`: IDF-weighted Jaccard similarity matching
- `src/lib/skillsprout-api.ts`: Session state, pagination, category filtering
- `src/data/onet-full.json`: 1,016 occupations with 65 skill/knowledge dimensions
- `src/data/skillsprout-test-cases.ts`: 55+ test cases
- Categories: Ready Now (≥55% overlap, ≤0 zone delta), Trainable (30-54%), Long-Term Reskill (<30%)

### SEO & Metadata

- `BaseHead.astro`: Canonical URLs, Open Graph, Twitter Cards
- JSON-LD schemas (Person on homepage, Article on blog posts)
- Auto-generated sitemap via `@astrojs/sitemap`
- `robots.txt` in `public/`

### Publications & Citations

- `Publications.astro` fetches live citation counts from Semantic Scholar API at build time
- Uses `Promise.allSettled()` for resilience (falls back to config values)

## CI/CD

- **Deploy**: Push to `master` → GitHub Actions builds with Node 20 → deploys to GitHub Pages
- **Blog workflows**: Create/publish posts via manual GitHub Actions dispatch
- Site URL: `https://zaherkarp.com`

## Working with Components

1. Components read from `siteConfig` (imported from `src/config.ts`)
2. Use Tailwind utility classes; mobile-first responsive design
3. Maintain the IBM Plex Mono monospace font aesthetic
4. Use Tabler Icons (inline SVGs) for consistency
5. Dark mode: use CSS custom properties or `[data-theme="dark"]` selectors
6. Astro components (`.astro`) for static content; React (`.tsx`) only when interactivity is needed