# peacerep-collection

Turning a messy `data.csv` (37 visualisation entries) into structured metadata under `metadata/`, as a starting point for a future database. Schema spec: `metadata/README.md` — that file is the authority on field definitions; don't restate them here.

## Status (keep this updated as work lands)

- [x] Schema reviewed against real CSV rows; link types (`public_link` / `embed_link` / `source_code`) added to `vocabularies.json`
- [x] `organisations.json`, `people.json`, `datasets.json` populated from `data.csv`
- [x] `dataset_colpus` identified: the Colpus coups d'état dataset (Chin, Carter & Wright 2021, ISQ 65(4))
- [x] Open question blocking full confidence in `datasets.json`: `PAX` / `PA-X` merged into one dataset (`dataset_pa_x`) — This is correct.
- [x] `visualisations.json` — all 37 rows populated (content.visualisation_types / views_components / thumbnail.alt_text intentionally left empty per the `populate-visualisations` skill)
- [x] 11 "Vis - PAX" rows with a blank `Data` column linked to `dataset_pa_x` based on URL domain/authorship evidence (not the CSV's `Data` column) — see each record's `notes` for the citation
- [ ] Rows 11, 12, 17, and 23 have no contributor in `data.csv` — flagged in their `notes`, pending a `trace-contributors` pass
- [ ] `tools.json` — not yet populated (still the placeholder example)
- [x] `check-links` run across all 36 rows: `source_code` filled for 21 rows total from confirmed GitHub matches; 13 rows have no confident repo match (Kumu/PowerBI-hosted, or genuinely unmatched) and remain empty. Iframe check found one real discrepancy (South Sudan Perceptions survey, now resolved by the user); two others matched aside from a harmless `?embedded=True` param. `peaceagreements.org/visualizations/` hub cross-checked for missing `public_link`s — 6 added.
- [x] `trace-contributors` run across all 36 rows: roles + affiliation + partner status resolved for 20 people via peacerep.org/about/people/ + vishub.net/people. All ~22 `source_code` repo READMEs checked (raw file) for uncredited contributors. Robert Wilson and Raiman Al-Hamdani added to Yemen Timeline per direct user confirmation — not discoverable via any automated source (that repo has no README at all).

## Global rules

1. **Schema authority is `metadata/README.md`.** Read it for field definitions; don't duplicate them here or re-derive them from scratch each session.
2. **Registry-first.** Before adding a person/org/dataset/tool, check the existing `metadata/*.json` files for a match. Most `data.csv` name variants (e.g. `"Niamh"` → `person_niamh_henry`, `"PAX"`/`"PA-X"` → `dataset_pa_x`) are already resolved — check each entry's `notes` field for the source variants it covers before assuming something is new.
3. **Flag, don't guess.** If a CSV value is ambiguous or needs information the CSV doesn't contain, write a flagged/uncertain note (see `dataset_colpus`'s history, or any dataset with `UNCERTAIN` in `notes`, for the pattern) rather than silently deciding. Never fabricate a value to fill a required field.
4. **Web search scope:**
   - OK: external, publicly verifiable facts — tool websites, well-known public dataset licences/source URLs (e.g. ACLED, UCDP, NELDA, Constitute Project), a GitHub repo's README/contributors when tracing a missing author.
   - Not OK: guessing contributor roles, emails, ORCIDs, or PeaceRep-internal names/identities not documented anywhere public.
   - Resources prioritized:
     - PeaceRep github organisation [https://github.com/peacerep]
     - PA-X database and visualizations [https://www.peaceagreements.org]
     - PeaceRep official website [https://peacerep.org]

## Skills

The recurring passes over `metadata/visualisations.json` are Skills under `.claude/skills/` — each is self-contained (conventions, lookup order, known facts) so it can be re-invoked on its own, in a fresh session, without this file's history:

- **`populate-visualisations`** — turn `data.csv` rows into visualisation records. Use when rows are new or unpopulated.
- **`check-links`** — fill/verify `source_code`, `embed_link`, `public_link`. Use when links need completing or cross-checking.
- **`trace-contributors`** — find and classify contributors, roles, affiliations, partner status. Use when contributor data needs resolving or new contributors need discovering.

Invoke via `/populate-visualisations`, `/check-links`, `/trace-contributors`.

## Review tool

`review/build_review.py` renders `metadata/*.json` into `review/index.html` — a local, static QA page (no upload, opened directly from disk). Regenerate after editing metadata: `python3 review/build_review.py`. Visualisations has three views (Full/Minimal tables + a Grid of cards) and a flagged-only filter. Style convention: dense tables, one row per record — not card grids — is the default; Grid is a deliberate addition, not a replacement.

By default:
- the Review tool full view should hide DESCRIPTION field, enable that feature with the option to show it. 
- no need to show the is_partner and role on the Contributor field.
