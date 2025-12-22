## Built With
- **[Astro](https://astro.build/)** - static site generator for modern web apps
- Template thanks to [Ryan Fitzgerald](https://ryanfitzgerald.github.io/devportfolio/).
- **[Tailwind CSS v4](https://tailwindcss.com/)** - utility-first CSS framework
- **[Tabler Icons](https://tabler.io/icons)** - free and open source icons
- **TypeScript** - for type-safe configuration
- **GoatCounter** - for analytics

## Updating the Template

### Configuration

The template is designed to be easily customizable through the `src/config.ts` file.

## Project Structure

```
devportfolio/
├── public/
│   └── favicon.svg          # Site favicon
├── src/
│   ├── components/          # Astro components
│   │   ├── About.astro      # About section
│   │   ├── Education.astro  # Education section
│   │   ├── Experience.astro # Work experience section
│   │   ├── Footer.astro     # Site footer
│   │   ├── Header.astro     # Navigation header
│   │   ├── Hero.astro       # Hero/intro section
│   │   └── Projects.astro   # Projects showcase
│   ├── pages/
│   │   └── index.astro      # Main page layout
│   ├── styles/
│   │   └── global.css       # Global styles
│   └── config.ts            # Site configuration
├── astro.config.mjs         # Astro configuration
├── package.json             # Project dependencies
├── tailwind.config.js       # Tailwind configuration
└── tsconfig.json            # TypeScript configuration
```

## Blog Publishing Workflows

This site includes two GitHub Actions workflows for managing blog posts:

### Creating New Blog Posts

**Option 1: Use the "Create Blog Post" Workflow**

1. Go to **Actions** → **Create New Blog Post**
2. Click **Run workflow**
3. Fill in the form:
   - **Title**: Your blog post title
   - **Filename**: URL-friendly slug (e.g., `my-awesome-post`)
   - **Description**: Short description for metadata
   - **Tags**: Comma-separated tags (e.g., `tech, tutorial, javascript`)
   - **Publish now**: Check to publish immediately, uncheck to save as draft
4. The workflow will create the file, commit, and push to master

**Option 2: Create Manually**

Create a markdown file in `src/content/blog/your-post-name.md`:

```markdown
---
title: "Your Post Title"
description: "A short description"
publishDate: 2025-12-21
draft: true  # Optional: include this to save as draft
tags: ["tag1", "tag2"]  # Optional
---

Your blog post content here...
```

### Publishing Draft Posts

**For posts with `draft: true` in the frontmatter:**

1. Go to **Actions** → **Publish Blog Post**
2. Click **Run workflow**
3. Enter the **filename** (without `.md` extension)
4. Optionally check **Update date** to set publishDate to today
5. The workflow will:
   - Remove the `draft: true` line
   - Update the publish date (if requested)
   - Commit and push the changes
   - Trigger site deployment

**How Draft vs Published Works:**

- **Draft posts** (with `draft: true`) are filtered out and **won't appear** on your site
- **Published posts** (without `draft: true` or after running Publish workflow) **will appear** on your site
- Posts created manually without `draft: true` are **immediately published** when merged
- You can use drafts to preview and edit posts before making them public

### Workflow Files

- `.github/workflows/new-blog-post.yml` - Creates new blog posts from inputs
- `.github/workflows/publish-blog-post.yml` - Publishes draft posts by removing `draft: true`

## Local Development

If you'd like to run it locally:

```
git clone https://github.com/RyanFitzgerald/devportfolio.git
cd devportfolio
npm install
```

After that, start up the Astro dev server with:

```
npm run dev
```

## Deployment

The template can be deployed to any static hosting service easily (and in most cases, completely free). Here are some options:

- To deploy with Netlify, [click here](https://docs.astro.build/en/guides/deploy/netlify/).
- To deploy with Vercel, [click here](https://docs.astro.build/en/guides/deploy/vercel/).
- To deploy with GitHub Pages, [click here](https://docs.astro.build/en/guides/deploy/github/).
- To deploy with Cloudflare Pages, [click here](https://docs.astro.build/en/guides/deploy/cloudflare/).
- To deploy with Render, [click here](https://docs.astro.build/en/guides/deploy/render/).

Want to deploy somewhere else? Find more guides [here](https://docs.astro.build/en/guides/deploy/).

## Changelog

To view the changelog, see CHANGELOG.md.

## License

This project is fully and completely MIT. See LICENSE.md.
