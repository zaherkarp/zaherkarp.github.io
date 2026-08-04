---
title: "Eight Tools, Eight Models Folders"
description: "Every local LLM app invents its own layout for the same GGUF files, so a collection built with one tool is invisible to the next. A survey of what eight tools actually do on disk, and the case for reading a plain folder you already have."
publishDate: 2026-08-04
draft: true
tags: ["llm", "inference", "developer-tools", "systems"]
lifeweek_topic: "Local model storage"
---

## TL;DR

- A GGUF file is a GGUF file. Every local LLM app can read the same bytes, and almost none of them can read each other's folders.
- Of eight tools surveyed, all eight let you relocate *their* models folder. Only four will read a plain flat folder of `.gguf` files, and only two will read more than one folder at a time.
- The nesting that LM Studio and the Hugging Face cache require re-encodes, in directory names, metadata the GGUF header already carries. It is duplicated information, and it is the reason your collection cannot be shared.
- The ask is small: let me point your app at a folder I already have, read the files where they lie, and treat that folder as read-only.

<style>
.etm-fade { opacity: 0; animation: etm-fade 0.5s ease-out forwards; }
.etm-grow { transform: scaleX(0); transform-origin: left; transform-box: fill-box; animation: etm-grow 0.8s cubic-bezier(0.2,0.7,0.3,1) forwards; }
.etm-pop  { opacity: 0; transform: scale(0.4); transform-origin: center; transform-box: fill-box; animation: etm-pop 0.5s ease-out forwards; }
@keyframes etm-fade { to { opacity: 1; } }
@keyframes etm-grow { to { transform: scaleX(1); } }
@keyframes etm-pop  { to { opacity: 1; transform: scale(1); } }
</style>

## The thing that doesn't work

I have a large collection of GGUF files. It was built with llama.cpp, which has no opinion whatsoever about where models live: you pass `-m /some/path/model.gguf` and it opens the file. That is the entire contract.

Then you try a second tool. LM Studio wants the file under `~/.lmstudio/models/`, nested two levels deep as `publisher/model/file.gguf`. Ollama wants it inside a content-addressed store where every file is named after its SHA-256 digest. Jan wants an `org/repo` directory with a YAML sidecar. Each of these is a perfectly reasonable design in isolation. Together, they mean the same 4.7 GB of bytes has to exist in one shape to be visible to one app and a different shape to be visible to the next.

The folk remedy is symlinks, and I want to be precise about why that is not an answer. It is not that symlinks fail; mine mostly work. It is that they are the wrong layer:

- They are invisible. Six months later you cannot tell, from the app's UI, which models are real files and which are pointers into a collection you might have since reorganized.
- They break silently on move. Rename the parent directory of the real collection and the app shows you a model that does not load.
- They are not portable. On Windows, creating one requires either developer mode or an elevated prompt, which disqualifies the technique for most of the people who would benefit from it.
- Backup and sync tools disagree about them. Some follow the link and store the payload twice, which is exactly the disk cost you were trying to avoid.

Mostly, though: symlinking is the user manually implementing a feature the app should have. You are hand-building an indirection layer because the app assumed it owned the namespace.

## Eight tools, eight layouts

Here is where the same file has to sit for each tool to see it.

<figure>
<svg viewBox="0 0 760 425" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Eight rows, one per local LLM tool, showing the directory path each one requires for the same GGUF file, Qwen3-8B-Q4_K_M.gguf. llama.cpp and KoboldCpp accept any path. GPT4All uses a flat application data folder. text-generation-webui uses a flat models folder. LM Studio requires two levels of publisher and model nesting. Jan requires org and repo nesting plus a model.yml sidecar. Ollama replaces the filename entirely with a sha256 digest and stores a separate manifest file. The Hugging Face cache nests the file under models--org--repo, a snapshots directory, and a commit hash. In every case the trailing filename is the same; only the wrapper differs." style="width:100%;height:auto;font-family:'et-book',Palatino,Georgia,serif">
  <text x="20" y="24" font-size="11" letter-spacing="1.4" fill="#6a6a6a">ONE FILE, EIGHT LAYOUTS: WHERE EACH TOOL INSISTS Qwen3-8B-Q4_K_M.gguf LIVES</text>
  <g class="etm-fade" style="animation-delay:0.05s">
    <text x="20" y="68" font-size="12" fill="#111">llama.cpp</text>
    <text x="130" y="68" font-size="10" fill="#6a6a6a" font-family="'Courier New',Courier,monospace">~/models/</text>
    <text x="184" y="68" font-size="10" fill="#111" font-family="'Courier New',Courier,monospace">Qwen3-8B-Q4_K_M.gguf</text>
    <text x="316" y="68" font-size="10" font-style="italic" fill="#6a6a6a">or any other path</text>
  </g>
  <g class="etm-fade" style="animation-delay:0.14s">
    <text x="20" y="104" font-size="12" fill="#111">KoboldCpp</text>
    <text x="130" y="104" font-size="10" fill="#6a6a6a" font-family="'Courier New',Courier,monospace">~/models/</text>
    <text x="184" y="104" font-size="10" fill="#111" font-family="'Courier New',Courier,monospace">Qwen3-8B-Q4_K_M.gguf</text>
    <text x="316" y="104" font-size="10" font-style="italic" fill="#6a6a6a">or any other path</text>
  </g>
  <g class="etm-fade" style="animation-delay:0.23s">
    <text x="20" y="140" font-size="12" fill="#111">GPT4All</text>
    <text x="130" y="140" font-size="10" fill="#6a6a6a" font-family="'Courier New',Courier,monospace">~/.local/share/nomic.ai/GPT4All/</text>
    <text x="322" y="140" font-size="10" fill="#111" font-family="'Courier New',Courier,monospace">Qwen3-8B-Q4_K_M.gguf</text>
  </g>
  <g class="etm-fade" style="animation-delay:0.32s">
    <text x="20" y="176" font-size="12" fill="#111">text-gen-webui</text>
    <text x="130" y="176" font-size="10" fill="#6a6a6a" font-family="'Courier New',Courier,monospace">user_data/models/</text>
    <text x="232" y="176" font-size="10" fill="#111" font-family="'Courier New',Courier,monospace">Qwen3-8B-Q4_K_M.gguf</text>
  </g>
  <g class="etm-fade" style="animation-delay:0.41s">
    <text x="20" y="212" font-size="12" fill="#111">LM Studio</text>
    <text x="130" y="212" font-size="10" fill="#6a6a6a" font-family="'Courier New',Courier,monospace">~/.lmstudio/models/Qwen/Qwen3-8B-GGUF/</text>
    <text x="358" y="212" font-size="10" fill="#111" font-family="'Courier New',Courier,monospace">Qwen3-8B-Q4_K_M.gguf</text>
  </g>
  <g class="etm-fade" style="animation-delay:0.50s">
    <text x="20" y="248" font-size="12" fill="#111">Jan</text>
    <text x="130" y="248" font-size="10" fill="#6a6a6a" font-family="'Courier New',Courier,monospace">~/.jan/llamacpp/models/Qwen/Qwen3-8B-GGUF/</text>
    <text x="382" y="248" font-size="10" fill="#111" font-family="'Courier New',Courier,monospace">Qwen3-8B-Q4_K_M.gguf</text>
    <text x="508" y="248" font-size="10" font-style="italic" fill="#6a6a6a">+ model.yml</text>
  </g>
  <g class="etm-fade" style="animation-delay:0.59s">
    <text x="20" y="284" font-size="12" fill="#111">Ollama</text>
    <text x="130" y="284" font-size="10" fill="#6a6a6a" font-family="'Courier New',Courier,monospace">~/.ollama/models/blobs/</text>
    <text x="268" y="284" font-size="10" fill="#7a0000" font-family="'Courier New',Courier,monospace">sha256-3f8e1c9a4b...</text>
    <text x="130" y="302" font-size="10" fill="#6a6a6a" font-family="'Courier New',Courier,monospace">~/.ollama/models/manifests/registry.ollama.ai/library/qwen3/8b</text>
  </g>
  <g class="etm-fade" style="animation-delay:0.68s">
    <text x="20" y="338" font-size="12" fill="#111">Hugging Face</text>
    <text x="130" y="338" font-size="10" fill="#6a6a6a" font-family="'Courier New',Courier,monospace">~/.cache/huggingface/hub/models--Qwen--Qwen3-8B-GGUF/snapshots/9c1f2a/</text>
    <text x="550" y="338" font-size="10" fill="#111" font-family="'Courier New',Courier,monospace">Qwen3-8B-Q4_K_M.gguf</text>
  </g>
  <line x1="20" y1="362" x2="740" y2="362" stroke="#d0d0c8" stroke-width="0.5"/>
  <text class="etm-fade" style="animation-delay:1s" x="20" y="388" font-size="12" font-style="italic" fill="#6a6a6a">The bytes at the end of every one of these paths are identical. Everything to the left of the filename is the tool</text>
  <text class="etm-fade" style="animation-delay:1s" x="20" y="406" font-size="12" font-style="italic" fill="#7a0000">asserting ownership of a file it did not create.</text>
</svg>
<figcaption>Layouts as documented in August 2026. The Hugging Face snapshot path is itself a symlink into a sibling <code>blobs/</code> directory named by content hash, so that row is really two files too. Ollama's blob digest is truncated here for width.</figcaption>
</figure>

Four archetypes fall out of that:

**Path-based.** llama.cpp and KoboldCpp have no models folder at all. You hand them a file. There is nothing to be incompatible with, which is why they are the only two tools here that can read a collection organized any way you like.

**Flat scan.** GPT4All and text-generation-webui keep a folder, let you move it, and scan it for `.gguf` files. GPT4All's scan is [recursive and origin-agnostic](https://github.com/nomic-ai/gpt4all/blob/main/gpt4all-chat/src/modellist.cpp): it walks subdirectories, accepts any file ending in `.gguf`, and registers it without copying or renaming anything. This is the behavior I want, and it already exists, shipped, in a mainstream app.

**Structured nesting.** LM Studio and Jan require directory names to follow a pattern, because the app reads the model's identity out of the path. LM Studio's docs are explicit that it "aims to preserve the directory structure of models downloaded from Hugging Face."

**Content-addressed store.** Ollama and the Hugging Face hub cache store files under their hashes, with a separate index mapping human names onto digests. Your GGUF is in there, bit-for-bit, under a name you cannot guess.

## The question that matters

The useful question is not *where does this app keep models*. Every app answers that, and every app lets you change the answer. The useful question is *will it read a folder it did not create*.

<figure>
<svg viewBox="0 0 760 440" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="A dot matrix of eight local LLM tools against five capabilities. Every one of the eight tools lets you point it at a folder of your choosing. Only llama.cpp, KoboldCpp, GPT4All and text-generation-webui accept a flat folder of GGUF files. Those four plus LM Studio will find files you placed there yourself; Jan, Ollama and Hugging Face will not. All except Ollama and Hugging Face keep the filename human readable. Only llama.cpp and KoboldCpp can work with more than one folder at a time." style="width:100%;height:auto;font-family:'et-book',Palatino,Georgia,serif">
  <text x="20" y="22" font-size="11" letter-spacing="1.4" fill="#6a6a6a">WILL IT READ A FOLDER IT DID NOT CREATE?</text>
  <text x="250" y="58" font-size="10" fill="#6a6a6a" text-anchor="middle">Point it at</text>
  <text x="250" y="71" font-size="10" fill="#6a6a6a" text-anchor="middle">a folder</text>
  <text x="250" y="84" font-size="10" fill="#6a6a6a" text-anchor="middle">you choose</text>
  <text x="360" y="58" font-size="10" fill="#7a0000" text-anchor="middle">A flat folder</text>
  <text x="360" y="71" font-size="10" fill="#7a0000" text-anchor="middle">of .gguf files</text>
  <text x="360" y="84" font-size="10" fill="#7a0000" text-anchor="middle">works</text>
  <text x="470" y="58" font-size="10" fill="#6a6a6a" text-anchor="middle">Finds files</text>
  <text x="470" y="71" font-size="10" fill="#6a6a6a" text-anchor="middle">you put</text>
  <text x="470" y="84" font-size="10" fill="#6a6a6a" text-anchor="middle">there yourself</text>
  <text x="580" y="58" font-size="10" fill="#6a6a6a" text-anchor="middle">Filename stays</text>
  <text x="580" y="71" font-size="10" fill="#6a6a6a" text-anchor="middle">human</text>
  <text x="580" y="84" font-size="10" fill="#6a6a6a" text-anchor="middle">readable</text>
  <text x="690" y="58" font-size="10" fill="#6a6a6a" text-anchor="middle">More than</text>
  <text x="690" y="71" font-size="10" fill="#6a6a6a" text-anchor="middle">one folder</text>
  <text x="690" y="84" font-size="10" fill="#6a6a6a" text-anchor="middle">at a time</text>
  <line x1="20" y1="96" x2="740" y2="96" stroke="#d0d0c8" stroke-width="1"/>
  <text x="20" y="124" font-size="12" fill="#111">llama.cpp</text>
  <circle class="etm-pop" style="animation-delay:0.05s" cx="250" cy="120" r="5" fill="#111"/>
  <circle class="etm-pop" style="animation-delay:0.09s" cx="360" cy="120" r="5" fill="#111"/>
  <circle class="etm-pop" style="animation-delay:0.13s" cx="470" cy="120" r="5" fill="#111"/>
  <circle class="etm-pop" style="animation-delay:0.17s" cx="580" cy="120" r="5" fill="#111"/>
  <circle class="etm-pop" style="animation-delay:0.21s" cx="690" cy="120" r="5" fill="#111"/>
  <text x="20" y="158" font-size="12" fill="#111">KoboldCpp</text>
  <circle class="etm-pop" style="animation-delay:0.10s" cx="250" cy="154" r="5" fill="#111"/>
  <circle class="etm-pop" style="animation-delay:0.14s" cx="360" cy="154" r="5" fill="#111"/>
  <circle class="etm-pop" style="animation-delay:0.18s" cx="470" cy="154" r="5" fill="#111"/>
  <circle class="etm-pop" style="animation-delay:0.22s" cx="580" cy="154" r="5" fill="#111"/>
  <circle class="etm-pop" style="animation-delay:0.26s" cx="690" cy="154" r="5" fill="#111"/>
  <text x="20" y="192" font-size="12" fill="#111">GPT4All</text>
  <circle class="etm-pop" style="animation-delay:0.15s" cx="250" cy="188" r="5" fill="#111"/>
  <circle class="etm-pop" style="animation-delay:0.19s" cx="360" cy="188" r="5" fill="#111"/>
  <circle class="etm-pop" style="animation-delay:0.23s" cx="470" cy="188" r="5" fill="#111"/>
  <circle class="etm-pop" style="animation-delay:0.27s" cx="580" cy="188" r="5" fill="#111"/>
  <circle class="etm-pop" style="animation-delay:0.31s" cx="690" cy="188" r="5" fill="none" stroke="#6a6a6a" stroke-width="1.2"/>
  <text x="20" y="226" font-size="12" fill="#111">text-gen-webui</text>
  <circle class="etm-pop" style="animation-delay:0.20s" cx="250" cy="222" r="5" fill="#111"/>
  <circle class="etm-pop" style="animation-delay:0.24s" cx="360" cy="222" r="5" fill="#111"/>
  <circle class="etm-pop" style="animation-delay:0.28s" cx="470" cy="222" r="5" fill="#111"/>
  <circle class="etm-pop" style="animation-delay:0.32s" cx="580" cy="222" r="5" fill="#111"/>
  <circle class="etm-pop" style="animation-delay:0.36s" cx="690" cy="222" r="5" fill="none" stroke="#6a6a6a" stroke-width="1.2"/>
  <text x="20" y="260" font-size="12" fill="#111">LM Studio</text>
  <circle class="etm-pop" style="animation-delay:0.25s" cx="250" cy="256" r="5" fill="#111"/>
  <circle class="etm-pop" style="animation-delay:0.29s" cx="360" cy="256" r="5" fill="none" stroke="#6a6a6a" stroke-width="1.2"/>
  <circle class="etm-pop" style="animation-delay:0.33s" cx="470" cy="256" r="5" fill="#111"/>
  <circle class="etm-pop" style="animation-delay:0.37s" cx="580" cy="256" r="5" fill="#111"/>
  <circle class="etm-pop" style="animation-delay:0.41s" cx="690" cy="256" r="5" fill="none" stroke="#6a6a6a" stroke-width="1.2"/>
  <text x="20" y="294" font-size="12" fill="#111">Jan</text>
  <circle class="etm-pop" style="animation-delay:0.30s" cx="250" cy="290" r="5" fill="#111"/>
  <circle class="etm-pop" style="animation-delay:0.34s" cx="360" cy="290" r="5" fill="none" stroke="#6a6a6a" stroke-width="1.2"/>
  <circle class="etm-pop" style="animation-delay:0.38s" cx="470" cy="290" r="5" fill="none" stroke="#6a6a6a" stroke-width="1.2"/>
  <circle class="etm-pop" style="animation-delay:0.42s" cx="580" cy="290" r="5" fill="#111"/>
  <circle class="etm-pop" style="animation-delay:0.46s" cx="690" cy="290" r="5" fill="none" stroke="#6a6a6a" stroke-width="1.2"/>
  <text x="20" y="328" font-size="12" fill="#111">Ollama</text>
  <circle class="etm-pop" style="animation-delay:0.35s" cx="250" cy="324" r="5" fill="#111"/>
  <circle class="etm-pop" style="animation-delay:0.39s" cx="360" cy="324" r="5" fill="none" stroke="#6a6a6a" stroke-width="1.2"/>
  <circle class="etm-pop" style="animation-delay:0.43s" cx="470" cy="324" r="5" fill="none" stroke="#6a6a6a" stroke-width="1.2"/>
  <circle class="etm-pop" style="animation-delay:0.47s" cx="580" cy="324" r="5" fill="none" stroke="#6a6a6a" stroke-width="1.2"/>
  <circle class="etm-pop" style="animation-delay:0.51s" cx="690" cy="324" r="5" fill="none" stroke="#6a6a6a" stroke-width="1.2"/>
  <text x="20" y="362" font-size="12" fill="#111">Hugging Face</text>
  <circle class="etm-pop" style="animation-delay:0.40s" cx="250" cy="358" r="5" fill="#111"/>
  <circle class="etm-pop" style="animation-delay:0.44s" cx="360" cy="358" r="5" fill="none" stroke="#6a6a6a" stroke-width="1.2"/>
  <circle class="etm-pop" style="animation-delay:0.48s" cx="470" cy="358" r="5" fill="none" stroke="#6a6a6a" stroke-width="1.2"/>
  <circle class="etm-pop" style="animation-delay:0.52s" cx="580" cy="358" r="5" fill="none" stroke="#6a6a6a" stroke-width="1.2"/>
  <circle class="etm-pop" style="animation-delay:0.56s" cx="690" cy="358" r="5" fill="none" stroke="#6a6a6a" stroke-width="1.2"/>
  <line x1="20" y1="380" x2="740" y2="380" stroke="#d0d0c8" stroke-width="0.5"/>
  <text class="etm-fade" style="animation-delay:0.9s" x="20" y="404" font-size="12" font-style="italic" fill="#6a6a6a">Every tool lets you move its folder. Half of them will not read yours.</text>
  <text class="etm-fade" style="animation-delay:1.1s" x="20" y="424" font-size="12" font-style="italic" fill="#6a6a6a">Filled means yes. Checked against each project's documentation and, for GPT4All, its source, in August 2026.</text>
</svg>
<figcaption>The first column is unanimous and nearly useless: relocating an app's private store does not let a second app read it. Note that llama.cpp and KoboldCpp score full marks by having no folder concept at all, which is less a design achievement than an absence of one. The interesting rows are GPT4All and text-generation-webui, which do keep a managed folder and still read whatever you put in it.</figcaption>
</figure>

## Why the nesting exists, and why it is redundant

LM Studio needs `publisher/model/file.gguf` because it reads the model's identity from the path. That is a real requirement given the design: the UI has to show you a publisher and a model name, and the directory is where it gets them.

But a GGUF file is not an opaque blob. The format opens with a key-value metadata block, and that block already carries the fields in question: `general.architecture`, `general.name`, the parameter count, the quantization type, the context length, the tokenizer. That is the whole point of the format. The `Q4_K_M` in the filename is not the source of truth about the quantization; it is a courtesy copy of something recorded inside the file.

So the directory structure is a second, weaker copy of metadata the file already carries, in a place where it cannot be validated and where it collides with everyone else's second copy. Read the header instead and the nesting requirement evaporates. This is not a hypothetical: reading GGUF metadata is a few hundred bytes at the front of the file, it is what every one of these tools already does at load time to size the KV cache, and GPT4All does exactly this to populate its model list from arbitrary files.

The folder structure was never load-bearing. It was a shortcut taken before anyone expected users to have collections.

## The cost

<figure>
<svg viewBox="0 0 760 330" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Horizontal bar chart of storage cost as a multiple of one collection. One shared folder costs one times. Two apps that each keep a private copy cost two times. Three apps cost three times. As an illustration, a 400 gigabyte collection admitted to three apps that copy becomes 1.2 terabytes." style="width:100%;height:auto;font-family:'et-book',Palatino,Georgia,serif">
  <text x="20" y="24" font-size="11" letter-spacing="1.4" fill="#6a6a6a">DISK COST OF ONE COLLECTION, AS A MULTIPLE</text>
  <text x="20" y="82" font-size="12" fill="#111">One shared folder</text>
  <rect class="etm-grow" style="animation-delay:0.1s" x="230" y="62" width="150" height="26" fill="#6a6a6a"/>
  <text class="etm-fade" style="animation-delay:0.7s" x="392" y="82" font-size="13" fill="#6a6a6a">1&#215;</text>
  <text x="20" y="142" font-size="12" fill="#111">Two apps that copy</text>
  <rect class="etm-grow" style="animation-delay:0.25s" x="230" y="122" width="300" height="26" fill="#6a6a6a"/>
  <text class="etm-fade" style="animation-delay:0.8s" x="542" y="142" font-size="13" fill="#6a6a6a">2&#215;</text>
  <text x="20" y="202" font-size="12" fill="#111">Three apps that copy</text>
  <rect class="etm-grow" style="animation-delay:0.4s" x="230" y="182" width="450" height="26" fill="#7a0000"/>
  <text class="etm-fade" style="animation-delay:0.9s" x="692" y="202" font-size="13" font-style="italic" fill="#7a0000">3&#215;</text>
  <line x1="20" y1="238" x2="740" y2="238" stroke="#d0d0c8" stroke-width="0.5"/>
  <text class="etm-fade" style="animation-delay:1.1s" x="20" y="262" font-size="12" font-style="italic" fill="#6a6a6a">Illustration: a 400 GB collection admitted to three copying apps occupies 1.2 TB. The multiple is the claim here;</text>
  <text class="etm-fade" style="animation-delay:1.1s" x="20" y="280" font-size="12" font-style="italic" fill="#6a6a6a">the 400 GB is a stand-in for whatever yours is.</text>
  <text class="etm-fade" style="animation-delay:1.3s" x="20" y="306" font-size="12" font-style="italic" fill="#6a6a6a">Whether you pay it can depend on which drive the collection sits on. See below.</text>
</svg>
<figcaption>Storage cost as a multiple of the collection, not an absolute. Tools that reference files in place (llama.cpp, KoboldCpp, GPT4All, text-generation-webui, and Jan's import) stay at 1&#215; regardless of how many of them you run.</figcaption>
</figure>

The Ollama case is worth spelling out, because it is the one where the cost is invisible at the moment you incur it. Importing a local GGUF with `ollama create` and a `FROM ./model.gguf` line will hard-link the file when the source and Ollama's store are on the same filesystem, costing nothing. Put your collection on an external drive, which is exactly what people with large collections do, and the same command falls back to a full copy. Same command, same output, silently double the disk. There is a [long-standing issue](https://github.com/ollama/ollama/issues/1450) asking for hard links and another asking for copy-on-write via `cp --reflink`, which would fix the same-filesystem case more thoroughly but not the cross-device one.

## The proposal

<figure>
<svg viewBox="0 0 760 350" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="A two-column comparison. On the left, today: three apps each keep a private store with its own copy of the collection. On the right, the proposal: one plain models folder that all three apps read in place, with no copies. Below, four rules: point it at any folder, read files where they lie, read identity from the GGUF header not the path, and treat the folder as read-only." style="width:100%;height:auto;font-family:'et-book',Palatino,Georgia,serif">
  <text x="185" y="28" font-size="11" letter-spacing="1.2" fill="#6a6a6a" text-anchor="middle">TODAY</text>
  <text x="565" y="28" font-size="11" letter-spacing="1.2" fill="#6a6a6a" text-anchor="middle">WHAT I AM ASKING FOR</text>
  <line x1="375" y1="44" x2="375" y2="238" stroke="#d0d0c8" stroke-width="1"/>
  <g class="etm-fade" style="animation-delay:0.1s">
    <text x="30" y="82" font-size="12" fill="#111">LM Studio</text>
    <rect x="150" y="66" width="120" height="22" fill="none" stroke="#6a6a6a" stroke-width="1"/>
    <text x="210" y="82" font-size="10" font-style="italic" fill="#6a6a6a" text-anchor="middle">its own copy</text>
  </g>
  <g class="etm-fade" style="animation-delay:0.25s">
    <text x="30" y="132" font-size="12" fill="#111">Ollama</text>
    <rect x="150" y="116" width="120" height="22" fill="none" stroke="#6a6a6a" stroke-width="1"/>
    <text x="210" y="132" font-size="10" font-style="italic" fill="#6a6a6a" text-anchor="middle">its own copy</text>
  </g>
  <g class="etm-fade" style="animation-delay:0.4s">
    <text x="30" y="182" font-size="12" fill="#111">Jan</text>
    <rect x="150" y="166" width="120" height="22" fill="none" stroke="#6a6a6a" stroke-width="1"/>
    <text x="210" y="182" font-size="10" font-style="italic" fill="#6a6a6a" text-anchor="middle">its own copy</text>
  </g>
  <text class="etm-fade" style="animation-delay:0.55s" x="30" y="222" font-size="12" font-style="italic" fill="#6a6a6a">one collection, stored three times</text>
  <g class="etm-fade" style="animation-delay:0.7s">
    <text x="400" y="82" font-size="12" fill="#111">LM Studio</text>
    <line x1="480" y1="78" x2="565" y2="105" stroke="#6a6a6a" stroke-width="1.2"/>
    <polygon points="565,105 556,101 556,109" fill="#6a6a6a"/>
    <text x="400" y="132" font-size="12" fill="#111">Ollama</text>
    <line x1="480" y1="128" x2="565" y2="128" stroke="#6a6a6a" stroke-width="1.2"/>
    <polygon points="565,128 556,124 556,132" fill="#6a6a6a"/>
    <text x="400" y="182" font-size="12" fill="#111">Jan</text>
    <line x1="480" y1="178" x2="565" y2="151" stroke="#6a6a6a" stroke-width="1.2"/>
    <polygon points="565,151 556,147 556,155" fill="#6a6a6a"/>
  </g>
  <g class="etm-fade" style="animation-delay:0.95s">
    <rect x="570" y="98" width="150" height="60" fill="none" stroke="#7a0000" stroke-width="1.5"/>
    <text x="645" y="124" font-size="12" fill="#7a0000" text-anchor="middle">~/models/</text>
    <text x="645" y="142" font-size="10" font-style="italic" fill="#6a6a6a" text-anchor="middle">read-only, in place</text>
  </g>
  <text class="etm-fade" style="animation-delay:1.05s" x="400" y="222" font-size="12" font-style="italic" fill="#6a6a6a">one collection, read where it already is</text>
  <line x1="20" y1="248" x2="740" y2="248" stroke="#d0d0c8" stroke-width="0.5"/>
  <text class="etm-fade" style="animation-delay:1.2s" x="20" y="274" font-size="12" font-style="italic" fill="#6a6a6a">1. Let me name one or more folders. Scan them for .gguf, recursively, and do not care how they are arranged.</text>
  <text class="etm-fade" style="animation-delay:1.3s" x="20" y="292" font-size="12" font-style="italic" fill="#6a6a6a">2. Read the file where it lies. Never copy, move, or rename it.</text>
  <text class="etm-fade" style="animation-delay:1.4s" x="20" y="310" font-size="12" font-style="italic" fill="#6a6a6a">3. Take the model's identity from the GGUF header, not from the directory name.</text>
  <text class="etm-fade" style="animation-delay:1.5s" x="20" y="328" font-size="12" font-style="italic" fill="#6a6a6a">4. Treat the folder as read-only. Keep your own state in your own config.</text>
</svg>
<figcaption>The fourth rule is the one that makes the other three safe. A shared library only works if every reader agrees not to write to it, which means prompt templates, sampling defaults, and per-model settings live in the app's own configuration, keyed by file path or content hash.</figcaption>
</figure>

Rule four deserves the emphasis. The reason apps own their models folder is not really the layout; it is that they want somewhere to keep per-model state, and the folder is a convenient place to put it. Jan's `model.yml` sidecar and Ollama's manifest layers are both this. The fix is not to ban sidecars but to make them optional and ignorable: write them if you like, next to the file, namespaced to your app, and tolerate finding four other apps' sidecars in the same directory without complaint.

## What this would actually take

I want to be fair about the range of effort here, because "just read a folder" is easy to say from outside the codebase.

For GPT4All and text-generation-webui: nothing. They do it today. The only gap is that neither accepts more than one root, which is a settings-and-a-loop change.

For LM Studio and Jan: moderate. Both already have the pieces, since both must parse GGUF headers to load a model at all. What changes is where identity comes from, and the UI has to tolerate a model whose publisher is unknown because it came from a folder rather than a repo path.

For Ollama and the Hugging Face cache: genuinely more work, and I do not think either should throw out what it has. Content-addressed storage is not a mistake. It gives you deduplication across models that share layers, integrity verification for free, atomic pulls that cannot leave a half-written file visible, and a clean garbage-collection story. Those are real properties, and a plain folder has none of them.

The ask for those two is narrower: support a read-only external library *alongside* the managed store. Keep the blob store for everything you download. Add a list of user folders you scan and serve directly, without importing. Ollama is already 90% of the way there, since `ollama create` with a local `FROM` can hard-link rather than copy; the remaining distance is making that a first-class "watch this folder" feature instead of a per-model command that quietly doubles your disk when the drive is external.

## Prior art, and why nothing happened

This has been proposed before. In February 2024 someone posted [a proposal for a unified local directory for LLM models](https://news.ycombinator.com/item?id=39329888) to Hacker News, making essentially this argument: pick a standard location on each OS, treat it like `Documents`, let every tool find models already on disk. It got four points and no discussion.

That is the actual state of the problem. It is not technically contested, it is not expensive to fix for most of the tools involved, and nobody owns it. Each app's models folder is correct from inside that app and wrong from anywhere else, and there is no forum where "anywhere else" has standing.

The nearest thing to a precedent is the one everybody has already accepted: OpenAI-compatible HTTP endpoints. No standards body issued that. It became a convention because enough implementations shipped it that not having it was a bug. A shared models folder can happen the same way, and it needs about the same number of implementations, which is to say two or three.

There is a version of this argument I care about beyond my own inconvenience. Once you are running local models anywhere near regulated data, a single read-only library is easier to reason about than four opaque per-app stores: you can hash it, inventory it, diff it against what you think you have, and answer "what weights are on this machine" without knowing the internals of every app installed. Four private content-addressed stores make that a research project. One folder makes it `ls`.

Until then: symlinks, and the quiet knowledge that they will break the next time I reorganize.
