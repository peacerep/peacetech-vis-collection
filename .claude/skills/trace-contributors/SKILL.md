---
name: trace-contributors
description: Find, verify, and classify contributors (people/organisations) for metadata/visualisations.json records in the peacerep-collection project, cross-referencing peacerep.org/about/people/ and vishub.net/people. Use when visualisation records need contributor roles, affiliations, or partner status resolved, or when new/uncredited contributors need discovering.
---

# Trace and classify contributors

Discovers uncredited contributors and resolves affiliation, role, and collaboration-partner status for people/organisations linked from `metadata/visualisations.json`. Schema is authoritative in `metadata/README.md`; project-wide principles are in `CLAUDE.md`.

**Never remove an existing contributor from a record.** Only add newly-found ones.

## Where `roles` and `is_collaboration_partner` live

Both fields are properties of the **person or organisation record** (`people.json` / `organisations.json`), not of the per-visualisation `contributors` entry. Someone's job function and team status don't change from one visualisation to the next — set them once on the entity, and every visualisation referencing that entity picks it up automatically. Don't add either field to a `contributors[]` entry in `visualisations.json`.

## Discovering uncredited contributors

For each visualisation, check in this priority order:

1. **GitHub commit history** (when `source_code` exists) — the most reliable, structured source, and one that has repeatedly found people the other methods miss. Fetch `https://api.github.com/repos/<org>/<repo>/contributors` for a list of usernames and commit counts. Resolve any unfamiliar username's real identity via `https://api.github.com/users/<username>` — the `name`, `bio`, and `company` fields often give a real name and affiliation directly, with no guessing needed. This has surfaced: a joint-top committer (140 commits) not credited anywhere else on that record, and a person not on `data.csv`, `peacerep.org/about/people/`, or `vishub.net/people` at all, identified purely from their GitHub profile's `company` field. A username with a very low commit count (1-2) and no name/bio on their profile is too weak to attribute confidently — note it as an unidentified minor contributor in the record's `notes` rather than guessing an identity.
2. **`source_code` repo README** — fetch the **raw file** directly:
   `https://raw.githubusercontent.com/<org>/<repo>/main/README.md`, falling back to `/master/README.md` if that 404s. Fetching the rendered GitHub page via WebFetch is unreliable — it frequently fails to surface the README content at all. If the repo has no README (check the file listing via `https://api.github.com/repos/<org>/<repo>/contents/` if unsure), there's nothing to find here.
3. **`public_link` page** — about/credits section, sometimes present. Also worth checking public-facing hub pages (e.g. `peaceagreements.org/visualizations/`) even if not directly the recorded `public_link` — these have surfaced credits (e.g. "designed and developed by X, using data by researchers Y and Z") not present anywhere else.
4. **`embed_link` page** — rarely has attribution; often an unfetchable JS-rendered SPA (Power BI, Streamlit). Low-yield, check last.

**Known limitation:** some contributors are only known through institutional/personal knowledge that was never published anywhere. If all four sources come up empty, say so plainly rather than presenting silence as completeness — the user may know contributors no automated search will ever surface (this has happened before: a repo with no README at all, crediting nobody on any fetchable page, and no commit history to check either).

## Cross-referencing found contributors

Check every contributor (existing and newly found) against two directories:

- **peacerep.org/about/people/** — the full team + consortium roster, organised by institution (University of Edinburgh, Conciliation Resources, University of St Andrews, Newcastle-affiliated researchers under "Affiliates," etc.). This page can have gaps — it's a lookup starting point, not a guaranteed-complete source.
- **vishub.net/people** — visualization-expertise researchers at Edinburgh's VisHub lab, including a named Alumni section (PhD graduates who may no longer be active but are still core-team-status, not partners).

### Affiliation

Set `people.json`'s `affiliation_ids` to the institution the person appears under on peacerep.org/about/people/, or from another confirmed source (a personal bio page) if not listed there.
- People on **vishub.net/people** should be with a UoE affiliation.
- **Affiliation reflects the person's affiliation at the time of the PeaceRep/visualisation work, not their current position.** A GitHub profile or other source may show a more recent, different affiliation (e.g. a VisHub alumna who has since moved to another university) — that's still useful to note, but don't let it override `affiliation_ids`, which should record the project-era institution (e.g. UoE, via VisHub/PeaceRep).

### Role (`people.json`'s `roles` field, vocab: `vocabularies.contributor_roles`)

- Visualization/design expertise evident (VisHub listing, job title, github contribution history, or a "designed by"/"developed by" credit) → `designer/developer`.
- Law / peace-and-conflict / political-science domain expertise evident → `domain_researcher`.
- Don't force a bad fit. If a job title genuinely doesn't match any of the above (true even after considering all evidence), leave `roles: []` and flag the ambiguity in that person's `notes`, quoting their actual title/credit text so the next pass — or the user — has something concrete to resolve it with.

### Partner status (`is_collaboration_partner`, on both `people.json` and `organisations.json`)

- `false` = core PeaceRep team — any consortium institution counts as core, not just the host University of Edinburgh (e.g. a St Andrews-based PeaceRep research lead is still core team, even though St Andrews itself is a partner *institution*). Confirmed full-time PeaceRep staff are `false` even if peacerep.org/about/people/ happens to omit them.
- `true` = external collaborator or partner institution not part of the PeaceRep consortium.
- Absence from peacerep.org/about/people/ is a **prompt to verify**, not sufficient evidence on its own — cross-check vishub.net/people, or ask, before concluding partner status. (This page has been observed to omit at least one confirmed full-time staff member.)
- For **organisations**: the host institution (University of Edinburgh) is `false`; every other named consortium member institution (e.g. University of St Andrews) is `true` even though people who work there via PeaceRep are core team (`false`) — the org and the people affiliated with it can have different partner status.

## Known facts (don't re-derive)

- Universitat Oberta de Catalunya = UOC.
- All PowerBI-embedded dashboards (`embed_link` containing `app.powerbi.com`) should have Niamh Henry as a contributor.
- vier-zwo is not anyone on yemen-timeline github contributor.

## After changes

Run `python3 review/build_review.py` to regenerate the QA page.
