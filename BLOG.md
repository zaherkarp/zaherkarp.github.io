# Blog Publishing Guide

This repository includes GitHub Actions workflows that make publishing blog posts easy and flexible. You can create posts directly through GitHub's web interface or locally.

## 📝 Two Ways to Publish

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
- **Backdating**: Use past date for migrated content (e.g., migrating old posts)

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

## 📁 File Structure

```
src/content/blog/
├── post-one.md
├── post-two.md
└── post-three.md

.github/workflows/
├── deploy.yml                 # Auto-deploy on push to master
├── new-blog-post.yml         # Create new posts
└── publish-blog-post.yml     # Publish draft posts

.blog-post-template.md        # Template for local posts
```

## 🔐 Permissions

All workflows use `contents: write` permission to commit changes. This is automatically granted through GitHub Actions' `GITHUB_TOKEN`.

## ⚙️ Customization

Edit `.blog-post-template.md` or `.github/workflows/new-blog-post.yml` to customize default content structure and formatting.

## 📚 Additional Resources

- [Astro Content Collections](https://docs.astro.build/en/guides/content-collections/)
- [Markdown Guide](https://www.markdownguide.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
