// Loads metadata/*.json and builds the lookups every component reads from.
// Components only display; all id → name resolution lives here.
import visJson from '../../../metadata/visualisations.json';
import peopleJson from '../../../metadata/people.json';
import orgsJson from '../../../metadata/organisations.json';
import datasetsJson from '../../../metadata/datasets.json';
import toolsJson from '../../../metadata/tools.json';
import vocab from '../../../metadata/vocabularies.json';

export { vocab };
export const vis = visJson.visualisations;
export const people = peopleJson.people;
export const orgs = orgsJson.organisations;
export const datasets = datasetsJson.datasets;
export const tools = toolsJson.tools.filter((t) => t.id !== 'tool_example');

const byId = (items) => new Map(items.map((x) => [x.id, x]));
const labels = (key) => new Map(vocab[key].map((x) => [x.id, x.label]));

const peopleById = byId(people);
const orgsById = byId(orgs);
const datasetsById = byId(datasets);
const toolsById = byId(toolsJson.tools);

export const label = {
  linkType: labels('link_types'),
  dimension: labels('dimensions'),
  visType: labels('visualisation_types'),
  status: labels('status'),
  role: labels('contributor_roles'),
  structureKind: labels('structure_kinds'),
  structureQuality: labels('structure_qualities'),
};

export const isUncertain = (d) => (d?.notes || '').includes('UNCERTAIN');

export const isFlagged = (v) =>
  Boolean(v.notes) ||
  v.data_coverage.datasets.some((d) => isUncertain(datasetsById.get(d.dataset_id)));

// e.g. "Promoted, Excluded"; '' when there's no status and not excluded.
export const statusText = (v) =>
  [...(v.status ?? []).map((s) => label.status.get(s) ?? s), ...(v.excluded ? ['Excluded'] : [])].join(', ');

// e.g. { kind: "Standalone vis", qualities: "Multi-view, Template" }; empty strings when unclassified.
export function structureLabels(v) {
  const { kind = '', qualities = [] } = v.structure ?? {};
  return {
    kind: label.structureKind.get(kind) ?? kind,
    qualities: qualities.map((x) => label.structureQuality.get(x) ?? x).join(', '),
  };
}

export const thumbSrc = (v) =>
  v.thumbnail?.url ? import.meta.env.BASE_URL + v.thumbnail.url : null;

export const toolNames = (v) =>
  v.tools.map((t) => toolsById.get(t.tool_id)?.name ?? `missing tool: ${t.tool_id}`);

export const orgName = (id) => {
  const o = orgsById.get(id);
  return o ? o.short_name || o.name || id : `missing org: ${id}`;
};

// Each resolver returns { name, missing } so the view can flag broken refs.
export function contributor(c) {
  if (c.entity_type === 'person') {
    const p = peopleById.get(c.entity_id);
    return p ? { name: p.display_name } : { name: `missing person: ${c.entity_id}`, missing: true };
  }
  const o = orgsById.get(c.entity_id);
  return o
    ? { name: o.name || o.short_name || o.id }
    : { name: `missing organisation: ${c.entity_id}`, missing: true };
}

export function datasetRef(ref) {
  const d = datasetsById.get(ref.dataset_id);
  if (!d) return { name: `missing dataset: ${ref.dataset_id}`, missing: true };
  let version = null;
  if (ref.version_id) {
    const v = d.versions.find((x) => x.id === ref.version_id);
    version = v ? { label: v.label } : { label: `unknown version ${ref.version_id}`, missing: true };
  }
  return { name: d.short_name || d.name, version, uncertain: isUncertain(d) };
}
