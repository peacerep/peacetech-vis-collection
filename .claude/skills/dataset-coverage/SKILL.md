---
name: dataset-coverage
description: Check dataset coverage
---

# Check dataset coverage

For each visualization, it can read-in multiple datasets.
We have largely two groups of data, one group is PA-X related data, which centers around PA-X as peace agreement dataset, but there're related data like PA-X local that only include local agreements, and PA-X Gender which is a sub dataset of the PA-X. Marked with an agreement Id (AgtId), all agreement has a set of metadata and then would be codes for different topics. Sub datasets would definitely have different topic codes, but the same agreement Id would have consistent set of agreement metadata.
The other group is external dataset that are related in the same domain and may be used in visualizations. Some are well-maintained databases with clear codebook and their organisation info, some are standalone data files developed in specific projects by specific people. Not all of them are up-to-date or complete, this requires extra attention in indentifying which are represented.

## Dataset knowledge

### PA-X related datasets:
- **PA-X** PA-X is a database containing 2257 peace agreements, found in more than 170 peace processes between 1990 and the end of 2025, now with 113 new agreements.
- **PA-X Gender** PA-X Gender contains all the peace agreements between 1990 and the end of 2025 which have provisions on women, girls, gender or sexual violence. This dataset contains additional variables related to women and peace agreements. This release adds 30 new agreements from the 10th release of the main PA-X database. PA-X Gender has its separate codebook on detailed gender topics, but share the metadata attributes with the main PA-X.
- **PA-X Local** PA-X Local contains all agreements included on the main PA-X database that deal in some way with local issues, involve local actors, and deal with forms of local/communal violent conflict. Agreements span the 1990 to the end of 2025, with global coverage, forming a collection of 396 local agreements, 29 of which are new in this release of PA-X Local.
- **PAA-X** contains the non-local actors/signatories recorded from each peace agreement in the PA-X dataset's `party` and `third parties` metadata field. Actor ID may link to external resources like UCDP and ACLED actor IDs.

### External datasets:
(1) that closely collaborate with PeaceRep:
- Amnesties contains 320 amnesties that are introduced during ongoing conflict, as part of peace negotiations, or in post-conflict periods from 1990-2023 in all world regions. The Amnesties units are not peace agreements, and follow its own code book. It does not have direct links to the PA-X dataset other than `country`, `year`.
- MEND contains mediation and mediation-related events involving external third-party actors. The MEND data shares peace agreement ID if the event resulted in a peace agreement being signed.

(2) completely different organisations but are represented in some PeaceRep visualisations:
- UCDP track and publish data on organised violence and the oldest ongoing data collection project for civil war. This research organisation defines `conflicts` with their actors, fatalities recorded. They also have different subdatasets like conflict data, georefrenced events data, dyadic data, violence data. PA-X agreements recorded UCDP conflict ID and agreement ID where applicable.
- ACLED publish data on conflicts and political violence. It also provides election trackers, regional analysis, and conflict tracking tools mainly targeting policy makers.

## Differentiate between `views/components` with `type`
A type of visualization is a genre thing, like dashboard, like scrollytelling, like interactive vis. 
And a view or component is the chart type which is a lower level concept, which can include a map, a bar chart, a chord network, etc. 
When going through the views, do not stop when you hit the type. For example, when you identify it is a scrollytelling, it should be in the overall type, then you need to continue looking for what specific visualization is within the scrollytelling. 

**Use the specific term you found, not the nearest existing one.** When a chart type doesn't have an exact match in `vocabularies.visualisation_types`, add the specific term (e.g. `beeswarm`) instead of mapping it to the closest existing entry (e.g. `scatterplot`). Don't pre-consolidate — that loses information now for no benefit later. Consolidating near-duplicate terms is a deliberate separate pass, done once there's enough vocabulary to see what's actually worth merging.

## Check the `.datasets` folder first

In `.datasets` folder, I have full data for `PA-X`, `PA-X Gender`, `PA-X Local`, `PA-X Amenities`, `Covid Ceasefire`, `VaxxPax`, `IGO Capacity`. Add these datasets into `dataset.json` — many are already in the list but complete their `fields` based on these files. For description and publisher information, use [https://www.peaceagreements.org/downloads/]. If a visualisation's dataset is covered here, you don't need to read its repository just to identify or field-list the dataset — only go to the repo/website (below) for the views/components and any dataset the `.datasets` folder doesn't cover.

## For visualisations with a source code link

1. **Locate the data read-in.** Find where the repository reads in each dataset, and note the data version.
2. **Identify the dataset(s).** If new, add to `dataset.json` and link it in `visualisation.json`. If it looks like a near-duplicate of an existing dataset (same shape, different version or scope), flag it to me rather than merging — for now, add it as a separate entry in `dataset.json`.
3. **Fill dataset fields — only if not already covered by `.datasets`.** If the dataset isn't one of the files in `.datasets`, fill in `fields` in `dataset.json` from the data file you just found.
4. **Record the genre, then identify each view/component and its fields, from the same code.** Record the overall genre in `content.visualisation_types` first (dashboard, scrollytelling, etc.) — that is not the end point. Go from the tool perspective — visualization libraries usually have `marks` or a clear import that shows what views are built. Find the code snippets where the tool is invoked, and for each concrete view/component add an entry to `views_components` with its own chart-level `visualisation_types` (map, bar chart, network, etc. — not the genre), then note which data fields feed it. `views/components` and `fields` should each be a unique list — no duplicates.

## For visualisations without a source code link

1. **Read the `public-link` page**, then the `embed-link` (the visualisation itself), for any description of the dataset(s) used.
2. **Record the genre, identify the tool, then infer each view from it.** Record the overall genre in `content.visualisation_types` first (dashboard, scrollytelling, etc.), then don't stop there — find each concrete view/component within it and add it to `views_components` with its own chart-level `visualisation_types`. Some tools are single-purpose and make this easy — e.g. https://timeline.knightlab.com is only for timelines, and Kumu is only for networks; a dashboard or scrollytelling tool needs this per-view breakdown instead. Note what fields are used to generate each view.
3. **For dashboards (hardest case):** cross-reference the dashboard's visible axis/legend labels against the known dataset's field list rather than trying to inspect the tool's internals.

## Complete the dataset metadata

When you've identified a new dataset, fill in `dataset.json`'s metadata. Read what you can get from the data file or the project webpage for `fields`, `descriptions`, and `publisher`. If there's anything you can't find, use web search to fill the gap. When in doubt, leave a note rather than guessing.
