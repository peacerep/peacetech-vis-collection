// Shared data + D3 rendering for the arc diagrams (horizontal and vertical).
// Each layout only supplies geometry; styling and hover behaviour live here.
import * as d3 from 'd3';
import relJson from '../../../metadata/relationships.json';
import { vis, label } from './data.js';

export const edges = relJson.edges;
export const visById = new Map(vis.map((v) => [v.id, v]));

// Nodes = every visualisation id mentioned in an edge, in first-seen order.
export const nodeIds = [...new Set(edges.flatMap((e) => [e.source, e.target]))];

// Node size = number of edges touching it; shape = square for containers, else circle.
const degree = d3.rollup(edges.flatMap((e) => [e.source, e.target]), (v) => v.length, (id) => id);
const radiusScale = d3.scaleSqrt([1, d3.max(degree.values())], [4, 11]);
export const radius = (id) => radiusScale(degree.get(id));
const symbol = (id) =>
  d3.symbol(
    visById.get(id)?.structure?.kind === 'container' ? d3.symbolSquare : d3.symbolCircle,
    Math.PI * radius(id) ** 2
  )();

// Colour: structural → greens, design → purples, one shade per edge name.
export const namesOf = (type) => [...new Set(edges.filter((e) => e.type === type).map((e) => e.name))];
const shades = (names, interp) =>
  names.map((n, i) => [n, interp(0.5 + (0.4 * i) / Math.max(1, names.length - 1))]);
export const color = new Map([
  ...shades(namesOf('structural'), d3.interpolateGreens),
  ...shades(namesOf('design'), d3.interpolatePurples),
]);
const markerId = (name) => `arrow-${name.replace(/\W+/g, '-')}`;

// Parallel edges between the same pair get a stack index → drawn as taller arcs.
const pairCount = new Map();
for (const e of edges) {
  const key = [e.source, e.target].sort().join('|');
  e.stack = pairCount.get(key) ?? 0;
  pairCount.set(key, e.stack + 1);
}

// Elliptical half-arc from a to b (both on the same axis), bulging by `bulge`
// towards unit vector `side` (e.g. [0, -1] = up). Split at its apex so the
// direction arrow can sit there as a marker-mid.
export function arcPath(a, b, bulge, [nx, ny]) {
  const [dx, dy] = [b[0] - a[0], b[1] - a[1]];
  const half = Math.hypot(dx, dy) / 2;
  const apex = [(a[0] + b[0]) / 2 + nx * bulge, (a[1] + b[1]) / 2 + ny * bulge];
  const angle = (Math.atan2(dy, dx) * 180) / Math.PI;
  const sweep = dx * ny - dy * nx < 0 ? 1 : 0; // clockwise when the bulge is on a→b's left
  const seg = ([x, y]) => `A${half},${bulge} ${angle} 0 ${sweep} ${x},${y}`;
  return { d: `M${a} ${seg(apex)} ${seg(b)}`, apex };
}

// Split long titles into lines at the space nearest the middle.
export function wrapLabel(text, maxChars = 22) {
  if (text.length <= maxChars) return [text];
  const mid = text.length / 2;
  const spaces = [...text.matchAll(/ /g)].map((m) => m.index);
  if (!spaces.length) return [text];
  const cut = spaces.reduce((a, b) => (Math.abs(b - mid) < Math.abs(a - mid) ? b : a));
  return [text.slice(0, cut), text.slice(cut + 1)];
}

/**
 * Draw the diagram into `svgEl`.
 * layout: { width, height, pos(id) → [x, y], arc(e) → { d, apex },
 *           arcLabelOffset: [dx, dy], arcLabelAnchor, nodeLabel(textSelection) }
 * onSelect(cards) fires on hover with the cards to show: [{ v }] for a node,
 * [{ v, role: 'Source' }, { v, role: 'Target' }] for an edge.
 */
export function renderArcDiagram(svgEl, layout, onSelect) {
  const svg = d3.select(svgEl).attr('width', layout.width).attr('height', layout.height);
  svg.selectAll('*').remove();
  const geo = new Map(edges.map((e) => [e, layout.arc(e)]));

  // One arrowhead marker per edge name, so it takes the arc's colour.
  svg
    .append('defs')
    .selectAll('marker')
    .data([...color])
    .join('marker')
    .attr('id', ([name]) => markerId(name))
    .attr('viewBox', '0 -5 10 10')
    .attr('refX', 5)
    .attr('markerWidth', 6)
    .attr('markerHeight', 6)
    .attr('orient', 'auto')
    .append('path')
    .attr('d', 'M0,-5L10,0L0,5Z')
    .attr('fill', ([, c]) => c);

  const arcs = svg
    .append('g')
    .attr('fill', 'none')
    .selectAll('path')
    .data(edges)
    .join('path')
    .attr('d', (e) => geo.get(e).d)
    .attr('stroke', (e) => color.get(e.name))
    .attr('marker-mid', (e) => `url(#${markerId(e.name)})`);
  arcs.filter((e) => e.tooltip).append('title').text((e) => e.tooltip);

  // Arc labels at each apex, hidden until hovered. Drawn twice: a bold
  // background-coloured copy underneath acts as a halo behind the coloured text.
  const [ldx, ldy] = layout.arcLabelOffset;
  const arcLabels = svg
    .append('g')
    .attr('text-anchor', layout.arcLabelAnchor)
    .attr('font-size', 11)
    .attr('pointer-events', 'none')
    .selectAll('g')
    .data(edges)
    .join('g')
    .attr('transform', (e) => `translate(${geo.get(e).apex[0] + ldx},${geo.get(e).apex[1] + ldy})`);
  arcLabels.append('text').text((e) => e.name).attr('dy', '0.32em').attr('fill', 'var(--bg)').attr('stroke', 'var(--bg)').attr('stroke-width', 4).attr('font-weight', 700);
  arcLabels.append('text').text((e) => e.name).attr('dy', '0.32em').attr('fill', (e) => color.get(e.name));

  // Nodes: symbol at its position; the layout decides label placement.
  const nodes = svg
    .append('g')
    .selectAll('g')
    .data(nodeIds)
    .join('g')
    .attr('transform', (id) => `translate(${layout.pos(id)})`)
    .style('cursor', 'pointer');
  nodes.append('path').attr('d', symbol).attr('fill', 'var(--text)');
  const nodeLabels = nodes.append('text').attr('font-size', 11).call(layout.nodeLabel);

  // Shared highlight state: `hit` picks the emphasised edges (null = reset),
  // `nodeIds` the emphasised labels.
  function highlight(hit, ids = []) {
    arcs
      .attr('stroke-opacity', (e) => (!hit ? 0.8 : hit(e) ? 1 : 0.1))
      .attr('stroke-width', (e) => (hit?.(e) ? 3.5 : 2));
    arcLabels.attr('display', (e) => (hit?.(e) ? null : 'none'));
    nodeLabels
      .attr('fill', (id) => (ids.includes(id) ? 'var(--text)' : 'var(--muted)'))
      .attr('font-weight', (id) => (ids.includes(id) ? 700 : null));
  }
  highlight(null);

  // Hover swaps the cards; hover-out resets the drawing but keeps the cards.
  const card = (id, role) => ({ v: visById.get(id), role });
  nodes
    .on('mouseenter', (_, id) => {
      highlight((e) => e.source === id || e.target === id, [id]);
      onSelect([card(id)]);
    })
    .on('mouseleave', () => highlight(null));
  arcs
    .on('mouseenter', (_, d) => {
      highlight((e) => e === d, [d.source, d.target]);
      onSelect([card(d.source, 'Source'), card(d.target, 'Target')]);
    })
    .on('mouseleave', () => highlight(null));
}

// Card tags: status (+ Excluded), then structure kind and qualities.
export const statusTags = (v) => [
  ...(v.status ?? []).map((s) => label.status.get(s) ?? s),
  ...(v.excluded ? ['Excluded'] : []),
];
export const structureTags = (v) => {
  const { kind = '', qualities = [] } = v.structure ?? {};
  return [
    kind && (label.structureKind.get(kind) ?? kind),
    ...qualities.map((q) => label.structureQuality.get(q) ?? q),
  ].filter(Boolean);
};
