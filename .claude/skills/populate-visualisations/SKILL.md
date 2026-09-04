---
name: populate-visualisations
description: Turn data.csv rows into records in metadata/visualisations.json for the peacerep-collection project, using the existing people/organisation/dataset registries. Use when new or unpopulated data.csv rows need to become visualisation metadata records.
---

# Populate visualisations.json

Turns rows of `data.csv` into records in `metadata/visualisations.json`. Schema is authoritative in `metadata/README.md` — read it first if unfamiliar with the field structure. Project-wide principles (registry-first, flag-don't-guess, web search scope) are in `CLAUDE.md` — follow those too.

## Batch discipline

Never populate more than ~8 rows in one pass. If this is the first time populating a fresh batch of rows (e.g. `data.csv` was extended), pilot on 5 rows first, stop, and get explicit confirmation the output is right before continuing — judgment calls made early (naming conventions, how ambiguous fields get handled) set the pattern for everything after.

After every batch: run `python3 review/build_review.py` to regenerate the QA page, and spot-check it.

## Field-by-field conventions

- **`id`**: `vis_<slug>` derived from the title.
- **`title` / `description.summary`**: copied verbatim from the CSV's Title/Description columns. If Description is genuinely empty, leave `summary: ""` — do not fabricate a sentence from the title. A thin-but-present description (e.g. a parenthetical aside) is still copied verbatim; it's a legitimate finding about the source data, not something to improve.
- **`description.keywords` / `research_questions` / `audiences`**: leave empty. These are editorial/curatorial judgments, not something to infer from the CSV.
- **`data_coverage.datasets`**: parse the CSV's Data column. Registry-first — check `metadata/datasets.json` for an existing match (including name variants recorded in each dataset's `notes`) before creating a new entry. If the Data column is blank, do not assume a dataset from thematic context or authorship alone (e.g. "this is probably PA-X because the same author usually uses PA-X") — only link a dataset when there's real textual evidence (an explicit name in the title/description, a matching URL domain like `pax.peaceagreements.org`, or shared authorship with an already-confirmed row of the same tool suite), and cite that evidence in the record's `notes`.
- **`data_coverage.dimensions`**: infer `id`/`is_covered` from the CSV's Title/Description text only — never from thumbnails (see rule below). Always leave `description: ""` on each dimension entry; don't write inferred explanatory text there.
- **`contributors`**: parse the CSV's Author field. Registry-first against `people.json` — resolve name variants (e.g. a bare first name that appears in full elsewhere in the CSV) rather than creating duplicates; check each person's `notes` for recorded aliases before assuming a name is new. Drop non-name tokens (stray years, "and Partners," generic collective terms) rather than fabricating a person record for them. Do **not** set `roles` or `is_collaboration_partner` here — those live on the person/organisation record in `people.json`/`organisations.json` (see the `trace-contributors` skill), not per-contributor.
- **`tools`**: leave empty. Tool population is a separate pass, not covered by this skill.
- **`links`**: from the Embed Link / Live-Public-Facing-Link CSV columns. Only keep actual URLs — if a cell has surrounding descriptive prose, cut it rather than turning it into a `label`; if a cell is prose with no URL at all (e.g. "see attached file," "see a tracker profile"), don't create a link entry for it. Classify by content, not just column: the Embed Link column usually maps to `embed_link`, but if its URL is actually a GitHub repo, classify it as `source_code` instead. The Live/Public-Facing column maps to `public_link`.
- **`thumbnail.url`**: copied verbatim from the CSV's Thumbnails column (filenames already match `mini-fig/`) — do not prepend the `mini-fig/` folder name to the stored path.
- **`thumbnail.alt_text` / `thumbnail.credit`**: leave empty (`""`). **Do not open or read thumbnail images at all** — visualisation type/alt-text inference from thumbnails is handled by a separate workflow outside this project.
- **`content.visualisation_types` / `content.views_components`**: leave empty (`[]`) — same reason as alt_text above.
- **`timestamps.created_at` / `updated_at`**: set to the date this record is drafted. `data.csv` has no real creation date for any row — this is a known, permanent limitation. Don't flag it per record; it's already documented here.
- **`status`**: required on every record. Values come from `vocabularies.status`: `experimental`, `outdated`, `up-to-date`, `archived`, `deprecated`, `excluded`. Default to `experimental` unless the user gives a specific reason for another value — never infer `archived`/`deprecated`/`excluded` on your own judgment.
- **`notes`**: only for something that genuinely can't be resolved from `data.csv` (a vocabulary gap, an unverifiable claim, an inferred dataset link per above) — one clean sentence, not a restatement of these conventions. Leave `""` when there's nothing to flag.

## Validation before calling a batch done

Every ID unique; every `dataset_id`/`version_id`/`entity_id`/link `type` reference resolves against the registries and `vocabularies.json`; every `status` value is a real vocab ID.
