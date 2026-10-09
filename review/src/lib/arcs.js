// Shared data + D3 rendering for the arc diagrams (horizontal and vertical).
// Each layout only supplies geometry; styling and hover behaviour live here.
import * as d3 from 'd3';
import relJson from '../../../metadata/relationships.json';
import { vis, label, thumbSrc } from './data.js';

export const edges = relJson.edges;
export const visById = new Map(vis.map((v) => [v.id, v]));

// Nodes = every visualisation id mentioned in an edge, in first-seen order.
export const nodeIds = [...new Set(edges.flatMap((e) => [e.source, e.target]))];
// Every non-excluded visualisation: the connected nodes first, then the
// unconnected ones (used by the force view, where they float freely).
export const allNodeIds = [
  ...nodeIds,
  ...vis.filter((v) => !v.excluded && !nodeIds.includes(v.id)).map((v) => v.id),
];

// Node size = number of edges touching it; shape = square for containers, else circle.
const degree = d3.rollup(edges.flatMap((e) => [e.source, e.target]), (v) => v.length, (id) => id);
// Unconnected nodes (degree 0) clamp to the smallest size.
const radiusScale = d3.scaleSqrt([1, d3.max(degree.values())], [4, 11]).clamp(true);
export const radius = (id) => radiusScale(degree.get(id) ?? 0);
// Radius multiplier for thumbnail nodes: up to `max`, with the largest node's
// diameter spanning at most `overlap` × the node spacing `step` — neighbours may
// overlap (Edge Maps style); smaller nodes are drawn on top.
export const nodeScaleFor = (step, max = 3.6, overlap = 2) =>
  Math.max(1, Math.min(max, (overlap * step) / (2 * radiusScale.range()[1])));
const symbol = (id, scale = 1) =>
  d3.symbol(
    visById.get(id)?.structure?.kind === 'container' ? d3.symbolSquare : d3.symbolCircle,
    Math.PI * (radius(id) * scale) ** 2
  )();

// Colour: one categorical hue per edge name
const SLOTS = 9;
const counts = d3.rollup(edges, (v) => v.length, (e) => e.name);
export const edgeNames = [...counts.keys()].sort((a, b) => counts.get(b) - counts.get(a));
if (edgeNames.length > SLOTS) console.warn(`${edgeNames.length} edge names but only ${SLOTS} colours`);
export const color = new Map(edgeNames.map((n, i) => [n, `var(--edge-${(i % SLOTS) + 1})`]));
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

// Edge tooltip text: [source] / [target] placeholders become the visualisation titles.
export const edgeTooltip = (e) =>
  (e.tooltip ?? '')
    .replaceAll('[source]', visById.get(e.source)?.title ?? e.source)
    .replaceAll('[target]', visById.get(e.target)?.title ?? e.target);

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
 *           arcLabelOffset: [dx, dy], arcLabelAnchor, nodeLabel(textSelection),
 *           nodeScale?: radius multiplier, thumbnails?: fill nodes with their mini-fig image,
 *           nodeIds?: nodes to draw (default: those with an edge) }
 * onSelect(cards, edge) fires on hover/click with the cards to show: [{ v }]
 * for a node (edge = null), [{ v, role: 'Source' }, { v, role: 'Target' }]
 * plus the edge itself for an edge.
 * Clicking a node/edge pins its highlight (hover is paused while pinned);
 * clicking it again or the empty background unpins.
 * Returns { setEdgeName(name | null) }: highlights every edge of that name
 * (e.g. from a legend click) as the resting view; it also clears any pin.
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
    .style('fill', ([, c]) => c);

  const arcs = svg
    .append('g')
    .attr('fill', 'none')
    .selectAll('path')
    .data(edges)
    .join('path')
    .attr('d', (e) => geo.get(e).d)
    .style('stroke', (e) => color.get(e.name))
    .attr('marker-mid', (e) => `url(#${markerId(e.name)})`);
  // Invisible wide copies of the arcs on top take the pointer events, so thin
  // arcs are easy to hover and click.
  const arcHits = svg
    .append('g')
    .attr('fill', 'none')
    .selectAll('path')
    .data(edges)
    .join('path')
    .attr('d', (e) => geo.get(e).d)
    .attr('stroke', 'transparent')
    .attr('stroke-width', 10)
    .style('cursor', 'pointer');

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
  arcLabels.append('text').text((e) => e.name).attr('dy', '0.32em').style('fill', (e) => color.get(e.name));

  // Nodes: symbol at its position, largest first so smaller (possibly
  // overlapping) nodes stay visible on top; the layout decides label placement.
  const byRadius = d3.sort(layout.nodeIds ?? nodeIds, (id) => -radius(id));
  const nodes = svg
    .append('g')
    .selectAll('g')
    .data(byRadius)
    .join('g')
    .attr('transform', (id) => `translate(${layout.pos(id)})`)
    .style('cursor', 'pointer');
  const k = layout.nodeScale ?? 1;
  const shape = (id) => symbol(id, k);
  if (layout.thumbnails) {
    // Image clipped to the node's shape, with an outline; no thumbnail → solid fill.
    const clipId = (id) => `clip-${svgEl.dataset.clip ??= Math.random().toString(36).slice(2)}-${id}`;
    const withImg = nodes.filter((id) => thumbSrc(visById.get(id)));
    withImg.append('clipPath').attr('id', clipId).append('path').attr('d', shape);
    withImg
      .append('image')
      .attr('href', (id) => thumbSrc(visById.get(id)))
      .attr('x', (id) => -radius(id) * k)
      .attr('y', (id) => -radius(id) * k)
      .attr('width', (id) => 2 * radius(id) * k)
      .attr('height', (id) => 2 * radius(id) * k)
      .attr('preserveAspectRatio', 'xMidYMid slice')
      .attr('clip-path', (id) => `url(#${clipId(id)})`);
    nodes
      .append('path')
      .attr('d', shape)
      .attr('fill', (id) => (thumbSrc(visById.get(id)) ? 'none' : 'var(--text)'))
      .attr('stroke', 'var(--text)')
      .attr('stroke-width', 1.5);
  } else {
    nodes.append('path').attr('d', shape).attr('fill', 'var(--text)');
  }
  // Labels in their own layer above every node, with a background halo so
  // they stay legible where they cross overlapping thumbnails.
  const labelGroups = svg
    .append('g')
    .selectAll('g')
    .data(byRadius)
    .join('g')
    .attr('transform', (id) => `translate(${layout.pos(id)})`)
    .style('cursor', 'pointer');
  const nodeLabels = labelGroups
    .append('text')
    .attr('font-size', 11)
    .attr('stroke', 'var(--bg)')
    .attr('stroke-width', 3)
    .attr('stroke-linejoin', 'round')
    .attr('paint-order', 'stroke')
    .call(layout.nodeLabel);

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
    // Emphasised nodes (and their labels) come to the front; with a
    // selection, nodes not touching a highlighted edge fade back.
    const linked = new Set(ids);
    if (hit) for (const e of edges) if (hit(e)) linked.add(e.source).add(e.target);
    nodes.attr('opacity', (id) => (!hit || linked.has(id) ? 1 : 0.3));
    // Hovered node(s) raised last, so a linked neighbour never covers the
    // node under the cursor (which would fire mouseleave and flicker).
    nodes.filter((id) => linked.has(id) && !ids.includes(id)).raise();
    nodes.filter((id) => ids.includes(id)).raise();
    labelGroups.filter((id) => ids.includes(id)).raise();
    if (!hit) {
      nodes.sort((a, b) => radius(b) - radius(a));
      labelGroups.sort((a, b) => radius(b) - radius(a));
    }
  }
  // Resting view that hover-out returns to: a clicked (pinned) node/edge,
  // else the legend's edge name, else nothing emphasised.
  let legend = null;
  let pinned = null;
  const rest = () => (pinned ? highlight(pinned.hit, pinned.ids) : highlight(legend));
  rest();

  // A "view" is what hovering or clicking a node/edge shows.
  const card = (id, role) => ({ v: visById.get(id), role });
  const nodeView = (id) => ({ key: id, hit: (e) => e.source === id || e.target === id, ids: [id], cards: [card(id)], edge: null });
  const edgeView = (d) => ({ key: d, hit: (e) => e === d, ids: [d.source, d.target], cards: [card(d.source, 'Source'), card(d.target, 'Target')], edge: d });
  function preview(view) {
    highlight(view.hit, view.ids);
    onSelect(view.cards, view.edge);
  }
  // Click pins the view; clicking the pinned element again unpins it.
  function pin(event, view) {
    event.stopPropagation();
    pinned = pinned?.key === view.key ? null : view;
    pinned ? (rest(), onSelect(view.cards, view.edge)) : preview(view);
  }
  svg.on('click', () => {
    if (pinned) (pinned = null), rest();
  });

  // Hover previews (cards kept after hover-out) unless something is pinned.
  for (const sel of [nodes, labelGroups]) sel
    .on('mouseenter', (_, id) => pinned || preview(nodeView(id)))
    .on('mouseleave', () => pinned || rest())
    .on('click', (ev, id) => pin(ev, nodeView(id)));
  arcHits
    .on('mouseenter', (_, d) => pinned || preview(edgeView(d)))
    .on('mouseleave', () => pinned || rest())
    .on('click', (ev, d) => pin(ev, edgeView(d)));

  return {
    setEdgeName(name) {
      legend = name ? (e) => e.name === name : null;
      pinned = null;
      rest();
    },
  };
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
