---
name: trace-tools
description: Find, verify, and classify tools used in developing the visualizations for metadata/visualisations.json records in the peacerep-collection project.
---

# Trace and classify tools

Discover used tools used in developing the visualisations. Tool means commercial applications that host and made the visualization, libraries and frameworks used in the start-from-scratch projects served on github pages. 
Things you need to read or edit: `visualisation.json` and `tools.json`.
Schema is authoritative in `metadata/README.md`; project-wide principles are in `CLAUDE.md`.

## Rethink the tool types
D3, p5 should be a vis-library. 
Svelte and Streamlit are front-end-frameworks.
Map stuff are gis-tools.
Render and github pages are hosting-services.
Powerbi and kumu are commercial-vis-tools.


## Infer from links
From embed links you would find tools like powerbi or kumu. If you have identify those as commercial tools, add them in the `tool.json` list and assign to `visualisation.json`. And that may be enough you do not need to go to other links. 
Exception: for links with a `onrender` keyword, add onrender as one of the tool link, but this is a server service, you still need to go the Github codebase.

## Go through Github repository codebase
For embed links that you cannot identify a commercial tool from, next go to github links.
Read the codebase structure, if it is native html/jss, read the header of `index.html` and find what library the project is using for visualization and structure. Things like d3, p5 should be noted. 
If the codebase structure clearly stated there is a framework being used, identify the framework like `svelte` or `vue`. This is a tool. Then go to the config file and read what kind of visualization library is being used for this project.

**Don't stop at `package.json`.** Not every library is an npm dependency — some are vendored directly as a pre-built bundle and loaded via a plain `<script>` tag, which won't appear in `package.json` at all. This has been missed before: `peacerep/actor-network` uses NetPanorama, vendored as `public/bundle.js` (its own source starts with `var NetPanoramaTemplateViewer`) and loaded from `public/index.html` — invisible to a `package.json`-only check. For a Vue/framework project, also check the `public/` folder specifically: its `index.html` (the real HTML entry point, separate from any root `index.html`), and any unusually-named bundled `.js` files sitting next to it — peek at the first few hundred bytes of any such bundle for an identifying variable name or license comment. A `templates/`-style data folder full of JSON specs is also a hint that a declarative viz grammar/template library (like NetPanorama) is in play.

## Libraries that do not need to be included.
- Trivial libraries like for icons, for image exports and tweaking, should be not included as part of the tools.
