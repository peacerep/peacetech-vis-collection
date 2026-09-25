---
name: proj-summary
description: Write or tighten the description.summary field on metadata/visualisations.json records for the peacerep-collection project — one clean sentence naming the visualisation type, its topic/research focus, and the data it uses. Use when a record's summary is missing, too long, or doesn't say what the visualisation actually analyses.
---

# Write visualisation summaries

Fills `description.summary` in `metadata/visualisations.json`. Schema is authoritative in `metadata/README.md`; project-wide principles (registry-first, flag-don't-guess) are in `CLAUDE.md`.

## What a good summary says

A summary earns its place by answering, in one sentence: **what kind of visualisation is this, analysing what topic, using what data?** Not a restatement of the title, not marketing copy — the analytical content.

- **Vis type** — a plain descriptive term (map, dashboard, network diagram, timeline...), not necessarily the exact `vocabularies.visualisation_types` ID. Base it on what the record already shows (`content.visualisation_types`, if populated) or on actually looking at the live visualisation (`public_link`/`embed_link`) or its repo — not on the thumbnail image, and not a guess from the title alone.
- **Topic/research focus** — the substantive question or subject it's exploring (e.g. "actor involvement in peace and transition processes," not just "peace processes"). This is the part most worth getting right; don't flatten it to a generic phrase.
- **Data used** — name the dataset(s), resolved via `data_coverage.datasets[].dataset_id` against `datasets.json` (use its `short_name` where one exists, e.g. PA-X, Colpus). If `data_coverage.datasets` is empty, don't invent a data source.

**Important rules**: Topic and research focus is a must for summaries. If you cannot specify data used, skip this instead of invent or speculate. If you are not very sure of the vis type, just say "an interactive vis".

## Sourcing the content

1. **Existing summary text present** (from `data.csv` or already in the record): this is your primary source for the topic/research focus — don't discard its domain-specific wording. Reshape it into the vis-type/topic/data structure above and trim to the length limit; preserve exact domain terms (dataset names, methodological terms, entity types) rather than substituting simpler synonyms.
2. **No summary text**: read the live site (`public_link`/`embed_link`) or the project itself (`source_code` README) to write one from scratch, grounded in what the visualisation actually does — not inferred from the title alone.

**Important rules**: Only read the content in the links if existing summary text does not exists and not enough information on the populated metadata.

## Length

Cap at 80 words. Check length before finalizing; trim padding and redundant framing first, domain content last.

