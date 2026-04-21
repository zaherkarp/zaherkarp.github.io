---
title: "The Slowest Way to Learn Web Design Is the Only Way That Worked for Me"
description: "A personal history of building and rebuilding a website across three eras, from Squarespace drag-and-drop to a pure HTML and CSS rebuild, and what the increasing friction of each step actually taught me."
publishDate: 2026-04-19
tags: [web design, HTML, CSS, Astro, GitHub Pages, learning]
---

# The Slowest Way to Learn Web Design Is the Only Way That Worked for Me

There is a version of this story where I tell you I sat down one weekend, read a few tutorials, and built a website. That is not this story.

This is the version where I spent years doing things the wrong way, got increasingly annoyed by the gap between what I wanted and what I had, and eventually realized that gap was the whole point.

---

## Phase One: The WYSIWYG Years

When I built my first personal site, I used Squarespace. This was the right call. I was not a web developer. I had content I wanted to put somewhere on the internet, and Squarespace let me drag things around until they looked approximately like what I had in my head. WYSIWYG stands for What You See Is What You Get, and for a while, that was enough.

The problem was not Squarespace. The problem was that I had a portfolio of magazine articles -- long-form pieces with bylines, ledes, and narrative structure -- and I needed somewhere to display them. Squarespace had beautiful templates for photographers. It had templates for restaurants and yoga studios and jewelry designers. It had a photo album feature that was genuinely elegant.

So that is what I used. For articles.

I forced my journalism portfolio into a photo album template. I uploaded cover images where product photos were supposed to go. I wrote article summaries in the caption field. It looked acceptable in the way that something always looks acceptable when you are the one who built it and you have stopped being able to see it clearly. Looking back, it was a photo album with words in all the wrong places.

The lesson I should have taken from this experience: I did not understand what the tool was designed for, so I could not use it well. The lesson I actually took: I needed a better template.

---

## Phase Two: A Template I Did Not Understand

Several years passed. I kept the Squarespace site, kept it mostly unchanged, and mostly ignored it.

Then I moved to GitHub Pages with an Astro template, which is a sentence that requires some unpacking if you have not heard those words before. GitHub is where developers store code. GitHub Pages is a feature that lets you turn that code into a live website for free. Astro is a tool that helps you build websites out of reusable components. Think of it like a design system where you define what a navigation bar looks like once, and then every page uses that definition instead of rewriting it from scratch.

The Astro template I picked was clean, fast, and looked professional. I changed the text, swapped in my own content, and published it. The site looked good.

What I did not understand was how any of it worked.

I could not tell you why changing one file affected five pages. I could not tell you what generated the HTML that browsers actually read. When something looked slightly wrong, I would poke at the CSS until it stopped looking wrong, without knowing why the change worked. I had traded a photo album I vaguely understood for a system I did not understand at all, and the output happened to look better.

The gap between using a tool and understanding it is enormous, and comfortable, and very easy to stay inside of.

---

## Phase Three: Burning It Down (Kindly)

I have been rebuilding the site in pure HTML and CSS.

There is no framework, no template, and no tool that abstracts away the underlying decisions. Just the two languages that browsers have understood since the beginning of the web, and me, deciding every single thing explicitly.

This is slow. It is occasionally maddening. And it is the first time I have actually learned anything about design.

When you use a template, the designer has already made a thousand decisions: how much space goes between elements, what happens to the layout when you are on a phone, how text size scales, what color the links turn when you hover over them. You inherit those decisions without having made them. They work, which means you never have to think about them, which means you never develop an opinion about them.

When you write the CSS yourself, you have to have an opinion about everything. You have to decide how much padding goes inside a card component. Then you have to look at it and decide if that was right. Then you usually have to change it. You develop taste by doing this badly many times until you start to do it less badly.

Constraints are often framed as obstacles. I have started thinking about them as the mechanism by which you actually learn something. Squarespace removed the constraint of needing to understand code, and I learned nothing about code. The Astro template removed the constraint of needing to make design decisions, and I learned nothing about design. Pure HTML and CSS remove almost nothing, and the discomfort of that is exactly where the learning lives.

---

## Technical Deep Dives

*The rest of this post gets into the weeds. If you are a non-technical reader, you have the full story above. If you want to understand the tools themselves, keep going.*

---

### 1. Git and GitHub Pages: Version Control as Infrastructure

Git is a system that tracks changes to files over time. Every time you make a meaningful change to your code, you take a snapshot called a commit. Those snapshots form a history you can navigate. You can see what a file looked like three weeks ago, revert a change that broke something, or understand exactly when a bug was introduced.

GitHub is a platform that stores your Git history in the cloud and makes it visible to collaborators or the public.

GitHub Pages is the part that is relevant here. If your GitHub repository is set up correctly and contains a valid website, GitHub will build and serve that site for free at `yourusername.github.io`. There is no server to configure, no hosting bill, and no deployment complexity beyond pushing your code to GitHub. The site updates automatically whenever you push new changes.

The practical workflow looks like this: you write code on your computer, commit the changes with a short description of what you did, push it to GitHub, and within a minute your live site reflects the update. For a personal site with no database and no dynamic content, this is essentially perfect infrastructure.

The harder thing to internalize about Git is that it changes how you think about working. Because nothing is ever lost (every version of every file is recoverable), you can experiment without anxiety. You can try something, decide it is wrong, and go back. This sounds minor. In practice it removes a kind of friction that quietly slows down learning.

---

### 2. How Astro Works: Components and Static Generation

Astro is a static site generator, which means it produces plain HTML files as output. Browsers read HTML. Everything else (JavaScript frameworks, component systems, templating languages) is a tool for generating that HTML more efficiently or managing complexity as a site grows.

The core concept in Astro is the component. A component is a reusable piece of UI: a navigation bar, a footer, a card that displays an article's title and summary. You define it once in its own file, and every page that needs it simply imports it. If you want to change the navigation bar across your entire site, you change one file.

Astro components have a specific structure. At the top of the file is a "frontmatter" block (fenced with three dashes) where you write JavaScript to fetch data, define variables, and import other components. Below that is the HTML template that uses those variables. The component file looks roughly like this:

```astro
---
// This block runs at build time, not in the browser.
// Define variables and import other components here.
const title = "My Site";
import Navigation from './Navigation.astro';
---

<html>
  <head><title>{title}</title></head>
  <body>
    <Navigation />
    <slot /> <!-- Child page content gets inserted here -->
  </body>
</html>
```

When you run `astro build`, Astro processes every page, evaluates the frontmatter blocks, fills in the template variables, and writes out plain HTML files. The resulting site has no runtime JavaScript dependency unless you explicitly add one. Pages load fast because there is nothing to run -- just HTML and CSS for the browser to render.

The gap I fell into with my Astro template was not understanding the build step. The files in my repository were not the files the browser was reading. Astro was transforming them. Once that distinction clicked, the entire system became legible.

---

### 3. The Gap Between a Template and Understanding It

Templates solve a real problem: they let you have a professional-looking site without spending months learning the underlying tools. For many people and many use cases, that is exactly the right tradeoff.

The cost is that templates make poor teachers.

A good template handles responsive layout, accessibility, performance, and cross-browser compatibility without surfacing any of that to you. You see a site that works. You do not see the dozen CSS rules that make it work on a phone, or the semantic HTML choices that make screen readers function correctly, or the image optimization logic that keeps it fast. The decisions are invisible because they have already been made.

The specific trap is that when you need to change something (and you always eventually need to change something), you are modifying a system you do not understand. You find the property that controls the thing you want to change, tweak it until it looks right, and move on. What you do not do is understand why your change worked, what else it affected, or whether you introduced a subtle problem elsewhere.

Two things helped me close this gap. The first was reading the template code with the explicit goal of understanding it rather than modifying it, treating it as something to learn from rather than just a starting point to customize. The second was building something small from scratch alongside the template, so I had to make every decision explicitly. The contrast between "the template does this automatically" and "I have to write this myself" is instructive. You start to see the template as a set of choices rather than a fixed reality.

---

### 4. CSS Fundamentals: Box Model, Layout, Specificity

CSS is the language that controls how HTML looks. Every element on a page (a paragraph, a button, an image) is a box. CSS determines the size of that box, its position relative to other boxes, and what it looks like.

**The box model** is the fundamental structure. Every HTML element has content at its center, surrounded by padding (space inside the box, between content and the border), then a border, then margin (space outside the box, between it and neighboring elements). When an element looks the wrong size or sits in an unexpected position, the box model is usually involved. A common gotcha: by default, `width` in CSS refers to the content area alone, not including padding or border. Switching to `box-sizing: border-box` makes `width` refer to the whole box instead. Nearly every project does this.

```css
/* Applied globally so every element uses the same sizing model */
*, *::before, *::after {
  box-sizing: border-box;
}
```

**Layout** used to be painful. For many years, web developers used floats and creative workarounds to build multi-column layouts. Modern CSS has two much better tools: Flexbox and CSS Grid. Flexbox is for one-dimensional layout, which means arranging elements along a single axis (a row of navigation items, a column of cards). Grid is for two-dimensional layout, which means defining a full page structure with a header, sidebar, main content area, and footer. They are often used together. Grid handles the large structure; Flexbox handles the arrangement of items within each section.

```css
/* Grid for overall page structure */
body {
  display: grid;
  grid-template-areas:
    "header"
    "main"
    "footer";
}

/* Flexbox for navigation items within the header */
nav {
  display: flex;
  gap: 1rem;
  align-items: center;
}
```

**Specificity** is how the browser resolves conflicts when multiple CSS rules target the same element. Every rule carries a specificity score based on what kind of selector it uses. An ID selector (`#header`) outweighs a class selector (`.header`), which outweighs a tag selector (`header`). When two rules conflict, higher specificity wins regardless of which rule appears later in the file.

This causes problems when you are working with a template or inherited code. You try to override a style, your rule seems correct, but nothing changes. Usually the rule you are fighting has higher specificity. The brute-force solution is `!important`, which overrides everything. The correct solution is understanding why the conflict exists and writing a more specific selector or restructuring the CSS. The brute-force solution tends to compound problems over time.

Building from scratch forced me to understand specificity because I could see every rule that applied to every element. There were no inherited conflicts I had not introduced myself. That constraint -- no safety net, no pre-written styles to lean on -- is exactly why it worked as a learning environment.