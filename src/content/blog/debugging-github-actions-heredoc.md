---
title: "Debugging GitHub Actions: The Heredoc Horror Story"
description: "A deep dive into debugging a GitHub Actions workflow where heredoc syntax clashed with YAML parsing, leading to five different errors and one elegant solution."
publishDate: 2025-12-21
tags: ["github-actions", "yaml", "bash", "debugging"]
---

I recently spent way too long debugging a GitHub Actions workflow that seemed simple: create a blog post file with frontmatter. The workflow would accept inputs like title, description, and tags, then generate a markdown file. What could go wrong?

Everything, apparently.

## The Setup

The workflow used `workflow_dispatch` to accept user inputs and create a new blog post file:

```yaml
- name: Create Blog Post
  env:
    TITLE: ${{ inputs.title }}
    DESCRIPTION: ${{ inputs.description }}
    TAGS: ${{ inputs.tags }}
  run: |
    POST_FILE="src/content/blog/${{ inputs.filename }}.md"

    # Create the blog post file
    cat > "$POST_FILE" << 'EOF'
    ---
    title: "${{ inputs.title }}"
    description: "${{ inputs.description }}"
    publishDate: $(date +%Y-%m-%d)
    ---

    Write your blog post content here...
    EOF
```

Simple, right? Wrong.

## Error #1: The Heredoc Delimiter Mystery

The first error I encountered was cryptic:

```
warning: here-document at line 34 delimited by end-of-file (wanted `EOF')
```

Bash was complaining that it couldn't find the `EOF` delimiter. But it was right there on line 99! What was happening?

**The Root Cause:** The single quotes in `<< 'EOF'` were preventing variable substitution. But more importantly, they were also causing bash to treat the entire heredoc as a literal string, including any shell syntax that might interfere with finding the delimiter.

**The Fix Attempt:** Remove the single quotes and use environment variables:

```yaml
cat > "$POST_FILE" <<EOF
---
title: "$TITLE"
description: "$DESCRIPTION"
publishDate: $TODAY
EOF
```

This should work, right?

## Error #2: The Same Error Again

Nope. Still got:

```
warning: here-document at line 34 delimited by end-of-file (wanted `EOF')
```

**The Root Cause:** In GitHub Actions YAML, when you use `run: |`, everything in that block must be properly indented. The script commands were indented with spaces, but the heredoc content wasn't. This created a situation where bash couldn't properly parse the block because the indentation levels were inconsistent with the YAML structure.

The `EOF` was at column 0, but bash expected it to be part of the indented script block.

## Error #3: The Tab Character Trap

"Okay," I thought, "I'll use `<<-` which allows tabs before the delimiter!"

```yaml
cat > "$POST_FILE" <<-END_OF_POST
	---
	title: "$TITLE"
	description: "$DESCRIPTION"
	---
	END_OF_POST
```

New error:

```
found character '\t' that cannot start any token
  in ".github/workflows/new-blog-post.yml", line 82, column 1
```

**The Root Cause:** YAML forbids tab characters entirely. The `<<-` syntax in bash allows you to indent the heredoc content with tabs, which is great for shell scripts. But in a YAML file? Syntax error.

The YAML parser saw those tabs and immediately rejected the entire file, preventing the workflow from even showing up in the GitHub Actions interface.

## Error #4: The Document Separator

"Fine," I said, "I'll just not indent the heredoc content:"

```yaml
cat > "$POST_FILE" <<EOF
---
title: "$TITLE"
description: "$DESCRIPTION"
---
EOF
```

New error:

```
expected a single document in the stream
  in ".github/workflows/new-blog-post.yml", line 1, column 1
but found another document
  in ".github/workflows/new-blog-post.yml", line 82, column 1
```

**The Root Cause:** In YAML, `---` at the beginning of a line (column 0) is the document separator. The YAML parser thought I was starting a new YAML document in the middle of my workflow file!

The heredoc content's `---` frontmatter delimiter was being interpreted as a YAML document separator, not as content within a bash string.

## Error #5: The Indented Delimiter Problem

"What if I indent the heredoc content to avoid the `---` problem?"

```yaml
cat > "$POST_FILE" <<EOF
          ---
          title: "$TITLE"
          ---
EOF
```

**The Problem:** Now `EOF` at column 0 won't be recognized as the delimiter by bash, because heredoc delimiters must start at the same column as the content or be unindented when using `<<-`.

I was stuck in a catch-22:
- Unindented content → YAML document separator error
- Indented content → Bash can't find the delimiter
- Tabs → YAML syntax error
- `<<-` with tabs → YAML syntax error

## The Solution: Abandon Heredoc

The final, working solution was to abandon heredoc entirely and use bash brace grouping with echo statements:

```yaml
- name: Create Blog Post
  env:
    TITLE: ${{ inputs.title }}
    DESCRIPTION: ${{ inputs.description }}
    TAGS: ${{ inputs.tags }}
  run: |
    POST_FILE="src/content/blog/${{ inputs.filename }}.md"

    # Create the blog post file
    {
      echo "---"
      echo "title: \"$TITLE\""
      echo "description: \"$DESCRIPTION\""
      echo "publishDate: $TODAY"
      [ -n "$DRAFT_LINE" ] && echo "$DRAFT_LINE"
      [ -n "$TAGS_LINE" ] && echo "$TAGS_LINE"
      echo "---"
      echo ""
      echo "Write your blog post content here..."
    } > "$POST_FILE"
```

**Why This Works:**

1. **No special delimiters** - No `EOF` or `END_OF_POST` that bash needs to find
2. **Consistent indentation** - All lines use spaces, matching YAML's requirements
3. **No YAML special characters at column 0** - The `---` is inside an echo string, not a YAML line
4. **Variable substitution works** - Environment variables expand normally in echo statements
5. **Conditional content** - Easy to include/exclude lines with `[ -n "$VAR" ] && echo`

## Key Takeaways

1. **Heredoc in GitHub Actions YAML is a minefield** - The intersection of YAML's indentation rules, bash's heredoc parsing, and YAML's special characters creates multiple failure modes.

2. **YAML forbids tabs** - This eliminates the `<<-` solution that would normally work in shell scripts.

3. **`---` at column 0 is special in YAML** - Even inside a `run:` block's string content, YAML parsers get confused.

4. **Test YAML validity** - Use `python3 -c "import yaml; yaml.safe_load(open('file.yml'))"` to catch YAML syntax errors before pushing.

5. **Sometimes the simple solution is best** - Echo statements are more verbose but far more reliable than heredoc in this context.

## When to Use Each Approach

**Use heredoc in regular shell scripts:**
```bash
cat > file.txt <<EOF
Content here
EOF
```

**Use echo/printf in GitHub Actions YAML:**
```yaml
run: |
  {
    echo "line 1"
    echo "line 2"
  } > file.txt
```

**Use a separate template file if you need complex multi-line content:**
```yaml
run: |
  cp templates/blog-post-template.md "$POST_FILE"
  sed -i "s/{{TITLE}}/$TITLE/g" "$POST_FILE"
```

The moral of the story? When debugging shell scripts in YAML, remember: you're not just fighting bash parsing, you're fighting YAML's parser too. Choose your battles wisely, and sometimes the least clever solution is the best one.
