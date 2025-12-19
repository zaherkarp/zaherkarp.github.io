# Blog Publishing Guide

This repository includes GitHub Actions workflows that make publishing blog posts easy and flexible. You can create posts directly through GitHub's web interface or locally.

## 📝 Three Ways to Publish

### 1. **Create New Post via GitHub Actions** (Easiest)

Perfect for quick posts without touching your local environment.

1. Go to **Actions** tab in GitHub
2. Select **"Create New Blog Post"** workflow
3. Click **"Run workflow"**
4. Fill in the form:
   - **Title**: Your blog post title
   - **Filename**: URL-friendly slug (e.g., `my-awesome-post`)
   - **Description**: Brief summary
   - **Tags**: Comma-separated (e.g., `tech, tutorial, javascript`)
   - **Publish now**: Check to publish immediately, uncheck to save as draft
5. Click **"Run workflow"**

The post will be created at `src/content/blog/your-filename.md` and committed to the `master` branch.

### 2. **Create Post Locally**

For more control and longer writing sessions.

1. Copy the template:
   ```bash
   cp .blog-post-template.md src/content/blog/my-new-post.md
   ```

2. Edit the frontmatter and content:
   ```markdown
   ---
   title: "My Awesome Post"
   description: "A great post about something interesting"
   publishDate: 2025-12-19
   draft: true
   tags: ["tech", "tutorial"]
   ---

   Your content here...
   ```

3. Commit and push:
   ```bash
   git add src/content/blog/my-new-post.md
   git commit -m "Add new blog post: My Awesome Post"
   git push
   ```

4. **To publish the draft**, use the "Publish Blog Post" workflow (see below)

### 3. **Schedule Future Posts**

Write posts in advance and have them automatically publish on a specific date.

1. Create a post (via Actions or locally) with:
   - `draft: true`
   - `publishDate: 2025-12-25` (future date)

2. The **Auto-Publish Scheduled Posts** workflow runs daily at 9 AM UTC
3. It automatically publishes any draft posts whose `publishDate` has arrived

You can also manually trigger this workflow anytime from the Actions tab.

## 🚀 GitHub Actions Workflows

### 1. **Create New Blog Post**

**Location**: `.github/workflows/new-blog-post.yml`

Creates a new blog post from a template directly in GitHub.

**Inputs**:
- `title`: Blog post title (required)
- `filename`: Slug for the URL (required)
- `description`: Short description (optional)
- `tags`: Comma-separated tags (optional)
- `publish_now`: Publish immediately vs. save as draft (default: false)

**Usage**:
- Actions tab → "Create New Blog Post" → "Run workflow"

### 2. **Publish Blog Post**

**Location**: `.github/workflows/publish-blog-post.yml`

Publishes a draft post by removing `draft: true` from the frontmatter.

**Inputs**:
- `post_filename`: Filename without `.md` extension (required)
- `update_date`: Update publishDate to today (default: false)

**Usage**:
- Actions tab → "Publish Blog Post" → "Run workflow"
- Enter filename: `my-draft-post` (without `.md`)

### 3. **Auto-Publish Scheduled Posts**

**Location**: `.github/workflows/auto-publish-scheduled.yml`

Automatically publishes draft posts when their publishDate arrives.

**Schedule**: Daily at 9 AM UTC (cron: `0 9 * * *`)

**Manual Trigger**: Actions tab → "Auto-Publish Scheduled Posts" → "Run workflow"

**How it works**:
- Scans all draft posts in `src/content/blog/`
- Compares their `publishDate` with today's date
- Publishes posts where `publishDate <= today`
- Commits changes and triggers deployment

## 📋 Blog Post Format

### Frontmatter Fields

```yaml
---
title: "Post Title"           # Required: Display title
description: "Brief summary"  # Required: For listings and SEO
publishDate: 2025-12-19      # Required: YYYY-MM-DD format
draft: true                   # Optional: true = hidden, false/omitted = published
tags: ["tech", "tutorial"]    # Optional: Array of tags
---
```

### Content

- Use standard Markdown formatting
- Supports headings, lists, links, images, code blocks
- Images can be placed in `public/` folder
- Reference images as `/image-name.jpg`

## 🔄 Deployment Pipeline

All workflows that modify blog posts automatically trigger deployment:

1. Workflow commits changes to `master` branch
2. Push triggers the **Deploy to GitHub Pages** workflow
3. Site rebuilds with Astro
4. New version deploys to GitHub Pages

**Deployment time**: Usually 2-3 minutes after commit

## 💡 Tips & Best Practices

### Filenames

- Use lowercase letters only
- Separate words with hyphens
- Be descriptive but concise
- Examples:
  - ✅ `intro-to-astro.md`
  - ✅ `my-2025-goals.md`
  - ❌ `Post 1.md`
  - ❌ `MyBlogPost.md`

### Draft Workflow

1. **Write**: Create with `draft: true`
2. **Review**: Preview locally with `npm run dev`
3. **Schedule**: Set future `publishDate` for automatic publishing
4. **Publish**: Use workflow or manually remove `draft: true`

### Tags

- Keep tags lowercase
- Use general categories: `tech`, `tutorial`, `personal`, `travel`
- Be consistent across posts
- Don't create too many unique tags

### Publish Dates

- **Immediate**: Use today's date + `draft: false` (or omit draft)
- **Scheduled**: Use future date + `draft: true`, auto-publishes when date arrives
- **Backdating**: Use past date for migrated content

## 🐛 Troubleshooting

### Post Not Appearing

1. Check `draft: true` in frontmatter → remove or set to `false`
2. Verify frontmatter syntax (valid YAML)
3. Check deployment workflow completed successfully
4. Wait 2-3 minutes for deployment

### Workflow Failed

1. Check Actions tab for error details
2. Common issues:
   - Invalid filename (spaces, special characters)
   - File already exists (for new post workflow)
   - File doesn't exist (for publish workflow)
   - Invalid YAML in frontmatter

### Scheduled Post Didn't Publish

1. Check `publishDate` format is `YYYY-MM-DD`
2. Verify `draft: true` is set
3. Workflow runs at 9 AM UTC (check your timezone)
4. Manually trigger "Auto-Publish Scheduled Posts" workflow

## 📁 File Structure

```
src/content/blog/
├── post-one.md
├── post-two.md
└── post-three.md

.github/workflows/
├── deploy.yml                    # Auto-deploy on push to master
├── new-blog-post.yml            # Create new posts
├── publish-blog-post.yml        # Publish draft posts
└── auto-publish-scheduled.yml   # Auto-publish scheduled posts

.blog-post-template.md           # Template for local posts
```

## 🔐 Permissions

All workflows use `contents: write` permission to commit changes. This is automatically granted through GitHub Actions' `GITHUB_TOKEN`.

## ⚙️ Customization

### Change Auto-Publish Schedule

Edit `.github/workflows/auto-publish-scheduled.yml`:

```yaml
schedule:
  - cron: '0 9 * * *'  # Change time/frequency
```

Cron examples:
- `0 0 * * *` - Midnight UTC daily
- `0 */6 * * *` - Every 6 hours
- `0 9 * * 1` - 9 AM UTC every Monday

### Modify Template

Edit `.blog-post-template.md` or `.github/workflows/new-blog-post.yml` to customize default content structure.

## 📚 Additional Resources

- [Astro Content Collections](https://docs.astro.build/en/guides/content-collections/)
- [Markdown Guide](https://www.markdownguide.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Cron Expression Generator](https://crontab.guru/)
