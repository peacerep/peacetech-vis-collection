
# Visualisation Metadata Schema

This folder contains JSON metadata for documenting visualisations.

The schema is based on the visualisation metadata structure where each visualisation has a title, description, data coverage, contributors, tools, links, thumbnail, timestamps, and content information.

Reusable entities such as people, organisations, datasets, and tools are stored separately and referenced from `visualisations.json` by ID.

---

## Folder structure

```text
metadata/
  visualisations.json
  people.json
  organisations.json
  datasets.json
  tools.json
  vocabularies.json
  README.md
```

---

## Table of contents

- [Visualisation Metadata Schema](#visualisation-metadata-schema)
  - [Folder structure](#folder-structure)
  - [Table of contents](#table-of-contents)
  - [Files overview](#files-overview)
  - [Core design principles](#core-design-principles)
    - [Use IDs for references](#use-ids-for-references)
    - [Store reusable information once](#store-reusable-information-once)
    - [Collaboration partner status and role are properties of the entity](#collaboration-partner-status-and-role-are-properties-of-the-entity)
  - [ID naming conventions](#id-naming-conventions)
- [File specifications](#file-specifications)
  - [`visualisations.json`](#visualisationsjson)
    - [Description](#description)
    - [Top-level structure](#top-level-structure)
    - [Visualisation record fields](#visualisation-record-fields)
  - [`people.json`](#peoplejson)
    - [Description](#description-1)
    - [Top-level structure](#top-level-structure-1)
    - [Person record fields](#person-record-fields)
  - [`organisations.json`](#organisationsjson)
    - [Description](#description-2)
    - [Top-level structure](#top-level-structure-2)
    - [Organisation record fields](#organisation-record-fields)
  - [`datasets.json`](#datasetsjson)
    - [Description](#description-3)
    - [Top-level structure](#top-level-structure-3)
    - [Dataset record fields](#dataset-record-fields)
  - [`tools.json`](#toolsjson)
    - [Description](#description-4)
    - [Top-level structure](#top-level-structure-4)
    - [Tool record fields](#tool-record-fields)
  - [`vocabularies.json`](#vocabulariesjson)
    - [Description](#description-5)
    - [Top-level structure](#top-level-structure-5)
    - [Vocabulary item fields](#vocabulary-item-fields)
- [Notes on dates](#notes-on-dates)
- [Notes on empty values](#notes-on-empty-values)
- [Validation checklist](#validation-checklist)
- [Recommended workflow](#recommended-workflow)


## Files overview

| File | Description |
|---|---|
| `visualisations.json` | Main metadata records for each visualisation. |
| `people.json` | Reusable records for people. |
| `organisations.json` | Reusable records for organisations, institutions, labs, centres, funders, and partners. |
| `datasets.json` | Reusable records for datasets, dataset versions, and dataset fields. |
| `tools.json` | Reusable records for software, platforms, and tools. |
| `vocabularies.json` | Controlled terms used across the metadata system. |
| `README.md` | Documentation for the metadata structure. |

---

## Core design principles

### Use IDs for references

Records should reference each other by stable IDs, not by names.

For example:

- visualisations reference people using `entity_id`;
- visualisations reference datasets using `dataset_id`;
- visualisations reference tools using `tool_id`;
- people reference organisations using `affiliation_ids`.

This avoids problems caused by duplicate names, spelling differences, or name changes.

### Store reusable information once

People, organisations, datasets, and tools should be defined once in their own files.

Visualisation-specific information should stay in `visualisations.json`.

For example:

- a person’s name belongs in `people.json`;
- that person’s role in a specific visualisation belongs in `visualisations.json`;
- a dataset’s fields belong in `datasets.json`;
- the way a dataset is used in a visualisation belongs in `visualisations.json`.

### Collaboration partner status and role are properties of the entity

`is_collaboration_partner` and `roles` are stored on the person or organisation record itself (`people.json` / `organisations.json`), not per visualisation.

Whether someone is core PeaceRep team versus an external collaborator/partner institution, and whether their contribution is as a visualisation designer, developer, domain researcher, etc., doesn't change from one visualisation to the next — these are properties of who they are, not of which visualisation they contributed to.

---

## ID naming conventions

Use lowercase `snake_case`.

| Entity | Prefix | Example |
|---|---|---|
| Visualisation | `vis_` | `vis_peace_agreements_001` |
| Person | `person_` | `person_jane_smith` |
| Organisation | `org_` | `org_university_of_edinburgh` |
| Dataset | `dataset_` | `dataset_peace_agreements` |
| Dataset version | `version_` | `version_2025_12` |
| Dataset field | `field_` | `field_date_signed` |
| Tool | `tool_` | `tool_d3` |
| View | `view_` | `view_map` |
| Component | `component_` | `component_country_filter` |

---

# File specifications

---

## `visualisations.json`

### Description

Main metadata file for visualisations.

Each visualisation record describes what the visualisation is, what data it uses, who contributed to it, what tools were used, and what views/components it contains.

### Top-level structure

| Field | Type | Required | Description |
|---|---|---:|---|
| `schema_version` | string | yes | Version of the metadata schema. |
| `visualisations` | array | yes | List of visualisation records. |

### Visualisation record fields

| Field | Type | Required | Description |
|---|---|---:|---|
| `id` | string | yes | Unique visualisation ID. |
| `title` | string | yes | Display title of the visualisation. |
| `description` | object | yes | Descriptive metadata. |
| `description.summary` | string | yes | Short summary of the visualisation. |
| `description.keywords` | array | recommended | Concepts or keywords associated with the visualisation. |
| `description.research_questions` | array | recommended | Research question or questions the visualisation helps address. |
| `description.audiences` | array | recommended | Intended audiences. Uses IDs from `vocabularies.audiences`. |
| `data_coverage` | object | recommended | Metadata about datasets and dimensions covered. |
| `data_coverage.datasets` | array | recommended | Dataset references used by the visualisation. |
| `data_coverage.datasets[].dataset_id` | string | yes | References a dataset in `datasets.json`. |
| `data_coverage.datasets[].version_id` | string | recommended | References a dataset version in `datasets.json`. |
| `data_coverage.datasets[].field_ids` | array | recommended | References dataset fields in `datasets.json`. |
| `data_coverage.datasets[].usage_note` | string | optional | Description of how the dataset is used in the visualisation. |
| `data_coverage.dimensions` | array | recommended | Dimension coverage such as time, space, activity, actor, or relational data. |
| `data_coverage.dimensions[].id` | string | yes | Dimension ID from `vocabularies.dimensions`. |
| `data_coverage.dimensions[].is_covered` | boolean | yes | Whether the dimension is represented. |
| `data_coverage.dimensions[].description` | string | optional | Explanation of how the dimension is represented. |
| `data_coverage.dimensions[].related_fields` | array | optional | Dataset fields related to this dimension. |
| `contributors` | array | recommended | People or organisations involved in the visualisation. |
| `contributors[].entity_type` | string | yes | Either `person` or `organisation`. |
| `contributors[].entity_id` | string | yes | References `people.json` or `organisations.json`. |
| `tools` | array | recommended | Tools used to create the visualisation. |
| `tools[].tool_id` | string | yes | References a tool in `tools.json`. |
| `tools[].version` | string | optional | Tool version used for this visualisation. |
| `tools[].purpose` | string | optional | How the tool was used. |
| `links` | array | recommended | Related links. |
| `links[].type` | string | yes | Link type from `vocabularies.link_types`. |
| `links[].url` | string | yes | URL. |
| `links[].label` | string | optional | Human-readable link label. |
| `thumbnail` | object | recommended | Thumbnail image metadata. |
| `thumbnail.url` | string | recommended | Thumbnail image path or URL. |
| `thumbnail.alt_text` | string | recommended | Accessibility description of the thumbnail. |
| `thumbnail.credit` | string | optional | Thumbnail credit. |
| `timestamps` | object | yes | Created and updated dates. |
| `timestamps.created_at` | string | yes | Creation date. |
| `timestamps.updated_at` | string | yes | Last updated date. |
| `content` | object | recommended | Metadata about visualisation content, views, components, and visualisation type. |
| `content.visualisation_types` | array | recommended | Overall visualisation types. Uses IDs from `vocabularies.visualisation_types`. |
| `content.views_components` | array | optional | Views and components included in the visualisation. |
| `content.views_components[].id` | string | yes | Unique view/component ID. |
| `content.views_components[].name` | string | yes | Display name of the view/component. |
| `content.views_components[].kind` | string | yes | Either `view` or `component`. |
| `content.views_components[].description` | string | optional | Description of the view/component. |
| `content.views_components[].visualisation_types` | array | optional | Visualisation types used by this view/component. |
| `content.views_components[].component_type` | string | optional | Component type from `vocabularies.component_types`. |
| `content.views_components[].interaction_types` | array | optional | Interaction types from `vocabularies.interaction_types`. |
| `content.views_components[].related_dimensions` | array | optional | Related dimension IDs. |
| `content.views_components[].related_dataset_ids` | array | optional | Related dataset IDs. |
| `status` | string | recommended | Record status from `vocabularies.status`. |
| `notes` | string | optional | Internal notes. |

---

## `people.json`

### Description

Reusable registry of people.

Project-specific roles should not be stored here. Roles belong in `visualisations.json`.

### Top-level structure

| Field | Type | Required | Description |
|---|---|---:|---|
| `schema_version` | string | yes | Version of the metadata schema. |
| `people` | array | yes | List of people. |

### Person record fields

| Field | Type | Required | Description |
|---|---|---:|---|
| `id` | string | yes | Unique person ID. |
| `display_name` | string | yes | Preferred display name. |
| `given_name` | string | optional | Given or first name. |
| `family_name` | string | optional | Family or last name. |
| `affiliation_ids` | array | optional | Organisation IDs from `organisations.json`. |
| `is_collaboration_partner` | boolean | yes | Whether this person is an external collaboration partner, as opposed to core PeaceRep team. |
| `roles` | array | recommended | This person's contribution roles. Uses IDs from `vocabularies.contributor_roles`. |
| `notes` | string | optional | Internal notes. |

---

## `organisations.json`

### Description

Reusable registry of organisations, institutions, labs, centres, funders, partners, and project groups.

### Top-level structure

| Field | Type | Required | Description |
|---|---|---:|---|
| `schema_version` | string | yes | Version of the metadata schema. |
| `organisations` | array | yes | List of organisations. |

### Organisation record fields

| Field | Type | Required | Description |
|---|---|---:|---|
| `id` | string | yes | Unique organisation ID. |
| `name` | string | yes | Full organisation name. |
| `short_name` | string | optional | Abbreviation or short name. |
| `type` | string | recommended | Organisation type from `vocabularies.organisation_types`. |
| `url` | string | optional | Website URL. |
| `country` | string | optional | Country. |
| `is_collaboration_partner` | boolean | yes | Whether this organisation is an external partner institution, as opposed to PeaceRep's host institution. |
| `notes` | string | optional | Internal notes. |

---

## `datasets.json`

### Description

Reusable registry of datasets.

Dataset records include dataset identity, source information, versions, and fields.

### Top-level structure

| Field | Type | Required | Description |
|---|---|---:|---|
| `schema_version` | string | yes | Version of the metadata schema. |
| `datasets` | array | yes | List of datasets. |

### Dataset record fields

| Field | Type | Required | Description |
|---|---|---:|---|
| `id` | string | yes | Unique dataset ID. |
| `name` | string | yes | Dataset name. |
| `short_name` | string | optional | Dataset abbreviation. |
| `description` | string | recommended | Short description of the dataset. |
| `publisher_organisation_id` | string | optional | Publisher organisation ID from `organisations.json`. |
| `source_url` | string | optional | Dataset source URL. |
| `licence` | string | optional | Dataset licence. |
| `citation` | string | optional | Citation text. |
| `versions` | array | recommended | Dataset versions or releases. |
| `versions[].id` | string | yes | Unique version ID. |
| `versions[].label` | string | yes | Human-readable version label. |
| `versions[].release_date` | string | optional | Release date. |
| `versions[].download_url` | string | optional | Download URL. |
| `versions[].accessed_at` | string | optional | Date the dataset version was accessed. |
| `versions[].notes` | string | optional | Version-specific notes. |
| `fields` | array | recommended | Dataset fields or columns. |
| `fields[].id` | string | yes | Unique field ID. |
| `fields[].name` | string | yes | Original field or column name. |
| `fields[].label` | string | optional | Human-readable field label. |
| `fields[].description` | string | optional | Field description. |
| `fields[].data_type` | string | recommended | Data type from `vocabularies.field_data_types`. |
| `notes` | string | optional | Internal notes. |

---

## `tools.json`

### Description

Reusable registry of tools, software, platforms, libraries, and services.

Tool version and tool purpose for a specific visualisation should be stored in `visualisations.json`.

### Top-level structure

| Field | Type | Required | Description |
|---|---|---:|---|
| `schema_version` | string | yes | Version of the metadata schema. |
| `tools` | array | yes | List of tools. |

### Tool record fields

| Field | Type | Required | Description |
|---|---|---:|---|
| `id` | string | yes | Unique tool ID. |
| `name` | string | yes | Tool name. |
| `type` | string | recommended | Tool type from `vocabularies.tool_types`. |
| `description` | string | optional | Short description of the tool. |
| `website` | string | optional | Tool website. |
| `notes` | string | optional | Internal notes. |

---

## `vocabularies.json`

### Description

Controlled vocabulary file.

This file defines approved values for fields that should remain consistent across records.

For example, use one approved value such as `policy_makers` instead of several variations such as `policy maker`, `policy-makers`, or `policymakers`.

### Top-level structure

| Field | Type | Required | Description |
|---|---|---:|---|
| `schema_version` | string | yes | Version of the metadata schema. |
| `dimensions` | array | recommended | Controlled terms for data dimensions. |
| `audiences` | array | recommended | Controlled terms for intended audiences. |
| `contributor_roles` | array | recommended | Controlled terms for contributor roles. |
| `visualisation_types` | array | recommended | Controlled terms for visualisation types. |
| `component_types` | array | recommended | Controlled terms for view/component types. |
| `interaction_types` | array | recommended | Controlled terms for interaction types. |
| `link_types` | array | recommended | Controlled terms for link types. |
| `field_data_types` | array | recommended | Controlled terms for dataset field data types. |
| `organisation_types` | array | recommended | Controlled terms for organisation types. |
| `tool_types` | array | recommended | Controlled terms for tool types. |
| `status` | array | recommended | Controlled terms for visualisation status. |

### Vocabulary item fields

Most vocabulary arrays should use this structure:

| Field | Type | Required | Description |
|---|---|---:|---|
| `id` | string | yes | Stable controlled value ID. |
| `label` | string | yes | Human-readable label. |
| `description` | string | optional | Description of the term. |

---

# Notes on dates

Use ISO date format.
Recommended date-only format: `YYYY-MM-DD`

If time is needed, use ISO datetime format: `YYYY-MM-DDTHH:mm:ssZ`


---

# Notes on empty values

Use empty arrays for repeatable fields: `"keywords": []`

Use empty strings for optional text fields:`"notes": ""`


Avoid inconsistent placeholders such as:

```text
N/A
none
unknown
-
```

---

# Notes on link types

Each visualisation typically has up to three distinct links, corresponding to the three primary `vocabularies.link_types` values:

| Type | Meaning |
|---|---|
| `public_link` | The live, public-facing page intended for general audiences (e.g. a PeaceRep/PAX website page hosting the visualisation). |
| `embed_link` | A standalone or iframe-embeddable link to the visualisation itself. This may be the same URL as `public_link` when the visualisation is not embedded elsewhere, or a distinct embeddable URL when it is. |
| `source_code` | The code base for the visualisation (e.g. a GitHub repository). |

Other `link_types` values (`live_demo`, `documentation`, `publication`, `dataset`, `project_page`, `video_demo`) remain available for cases that don't fit the three primary types above — for example, `live_demo` for a demo that is not the visualisation's primary public page.

If a link value is not a URL (e.g. a reference to an attached file, or a note pointing to another document), do not store it under `links`; keep it in `notes` instead until a real URL is available.

---

# Validation checklist

Before committing metadata, check:

- [ ] Every visualisation ID is unique.
- [ ] Every person ID is unique.
- [ ] Every organisation ID is unique.
- [ ] Every dataset ID is unique.
- [ ] Every tool ID is unique.
- [ ] Every person contributor references an existing person ID.
- [ ] Every organisation contributor references an existing organisation ID.
- [ ] Every dataset reference points to an existing dataset ID.
- [ ] Every dataset version reference exists inside the referenced dataset.
- [ ] Every dataset field reference exists inside the referenced dataset.
- [ ] Every tool reference points to an existing tool ID.
- [ ] Every audience value exists in `vocabularies.audiences`.
- [ ] Every role value exists in `vocabularies.contributor_roles`.
- [ ] Every dimension value exists in `vocabularies.dimensions`.
- [ ] Every visualisation type exists in `vocabularies.visualisation_types`.
- [ ] Every link type exists in `vocabularies.link_types`.
- [ ] Every status value exists in `vocabularies.status`.
- [ ] `created_at` and `updated_at` use ISO date format.
- [ ] Thumbnail has useful `alt_text`.

---

# Recommended workflow

1. Add or check organisations in `organisations.json`.
2. Add or check people in `people.json`.
3. Add or check datasets, versions, and fields in `datasets.json`.
4. Add or check tools in `tools.json`.
5. Add or check controlled terms in `vocabularies.json`.
6. Add the visualisation record in `visualisations.json`.
7. Validate that all referenced IDs exist.
