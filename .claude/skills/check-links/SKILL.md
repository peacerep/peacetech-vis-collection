---
name: check-links
description: Fill in and verify source_code/embed_link/public_link fields on metadata/visualisations.json records for the peacerep-collection project, using the PeaceRep GitHub org and iframe verification against public-facing pages. Use when visualisation records need their links checked, completed, or cross-verified.
---

# Check and fill links

Fills in missing `source_code` links and verifies `embed_link`/`public_link` consistency on records in `metadata/visualisations.json`. Schema is authoritative in `metadata/README.md`; project-wide principles (registry-first, flag-don't-guess, web search scope — see especially the resource priority list) are in `CLAUDE.md`.

## The one hard rule

**Only edit a link field when it is currently empty.** Never overwrite an existing `source_code`, `embed_link`, or `public_link` value, even if you find something that looks more correct — flag the discrepancy in `notes` instead and let the user decide.

## Step 1 — fill `source_code` from GitHub

For any record with an empty `source_code`:

1. Search the PeaceRep GitHub org (`github.com/orgs/peacerep/repositories`) and relevant personal accounts (e.g. `tvancisin`) for a matching repo.
2. Don't stop at name similarity — verify by fetching the repo's README/description and confirming its content actually matches the visualisation (topic, data source, or an explicit deployment URL like `onrender.com`/`streamlit.app` mentioned in the README).
3. For personal GitHub Pages sites (`username.github.io/repo-name`), the repo is reliably at `github.com/username/repo-name` — this URL convention is strong evidence on its own, but still spot-check the repo exists and its content makes sense.
4. If no confident match exists, leave `source_code` empty. Don't guess from thematic similarity alone (e.g. a dataset name appearing in a repo name is a lead worth checking, not sufficient evidence by itself — verify the repo's actual content/description first).

## Step 2 — verify `embed_link` against `public_link`

For any record that has **both** an `embed_link` and a `public_link`:

1. Fetch the `public_link` page's raw HTML (`curl`, not just WebFetch — WebFetch's HTML-to-markdown conversion can silently drop `<iframe>` tags) and look for an `<iframe src="...">`.
2. Compare that `src` against the recorded `embed_link`:
   - A harmless difference (e.g. an added `?embedded=True` query parameter) is not a real discrepancy — no action needed.
   - A genuinely different URL is a real discrepancy — flag it in `notes` with both URLs, but do **not** overwrite `embed_link` (it's non-empty; see the hard rule above).
3. If no iframe is found via either `curl` or WebFetch, that's inconclusive, not confirmation of absence — many of these pages are JS-rendered SPAs where the iframe is injected client-side and won't appear in the static HTML either tool sees. Don't assert "no iframe exists"; just note nothing was found.

## Step 3 — search public-facing hubs for missing `public_link`

For records with **no** `public_link` at all, check listing/hub pages likely to reference them — e.g. `peaceagreements.org/visualizations/`, `peacerep.org`. For each candidate match:

- Confirm via iframe-src match against the recorded `embed_link` (strongest evidence), or
- A strong, specific title+description match (acceptable when the page doesn't embed directly, e.g. a landing page).

Don't assign a public_link on a weak/generic title match alone. If a credits section on one of these pages names a contributor not currently on the record, that's a legitimate find too — hand it to the `trace-contributors` skill rather than silently adding a person here without cross-referencing role/affiliation.

## After changes

Run `python3 review/build_review.py` to regenerate the QA page.
