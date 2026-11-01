<script>
  // Force-directed network on randomly generated data, with the same encoding
  // as the Relationships (force-directed) view: edge colour = relationship
  // name (legend shared via lib/arcs.js), arrow at each edge's midpoint for
  // direction, node size = number of links, square = container, circle =
  // standalone. No thumbnails, no labels; "Regenerate" draws a new network.
  import * as d3 from 'd3';
  import { untrack } from 'svelte';
  import { edgeNames, color, arcPath } from '../lib/arcs.js';
  import ArcLegend from './ArcLegend.svelte';

  const DESIGN_HEIGHT = 860;
  const MIN_HEIGHT = 480;
  const PAD = 40;
  const NODE_COUNT = 36;
  const EDGE_COUNT = 36;
  const FLOATING = 8; // nodes kept out of every link, so they float freely
  const CONTAINER_SHARE = 0.2;
  const NODE_SCALE = 2.4;

  let width = $state(0);
  let viewportHeight = $state(0);
  let svgEl;
  let seed = $state(Math.floor(Math.random() * 1e9));
  let edgeName = $state(null); // legend selection

  const markerId = (name) => `rand-arrow-${name.replace(/\W+/g, '-')}`;

  // Random nodes and edges from a seeded generator, so a redraw (e.g. on resize)
  // keeps the same network until "Regenerate" is pressed.
  function generate(seed) {
    const rand = d3.randomLcg(seed);
    const int = (n) => Math.floor(rand() * n);
    const nodes = d3.range(NODE_COUNT).map((i) => ({ id: `n${i}`, container: rand() < CONTAINER_SHARE }));
    const edges = [];
    while (edges.length < EDGE_COUNT) {
      const s = int(NODE_COUNT - FLOATING), t = int(NODE_COUNT - FLOATING);
      if (s !== t) edges.push({ source: `n${s}`, target: `n${t}`, name: edgeNames[int(edgeNames.length)] });
    }
    // Parallel edges between the same pair get a stack index → drawn curved.
    const pairCount = new Map();
    for (const e of edges) {
      const key = [e.source, e.target].sort().join('|');
      e.stack = pairCount.get(key) ?? 0;
      pairCount.set(key, e.stack + 1);
    }
    return { nodes, edges };
  }

  let highlight = () => {};

  $effect(() => {
    if (!width || !viewportHeight) return;
    const top = svgEl.getBoundingClientRect().top + window.scrollY;
    const bottom = parseFloat(getComputedStyle(document.body).paddingBottom) || 0;
    const HEIGHT = Math.max(MIN_HEIGHT, Math.floor(viewportHeight - top - bottom - 4));
    const k = Math.min(1, HEIGHT / DESIGN_HEIGHT);

    const { nodes, edges } = generate(seed);
    const degree = d3.rollup(edges.flatMap((e) => [e.source, e.target]), (v) => v.length, (id) => id);
    const rScale = d3.scaleSqrt([1, d3.max(degree.values())], [4, 11]).clamp(true);
    const r = (id) => rScale(degree.get(id) ?? 0) * NODE_SCALE * k;

    // Same forces as the force-directed view, run to rest up front.
    const links = edges.map((e) => ({ source: e.source, target: e.target }));
    const sim = d3
      .forceSimulation(nodes)
      .force('link', d3.forceLink(links).id((n) => n.id).distance(170 * k))
      .force('charge', d3.forceManyBody().strength(-500 * k))
      .force('x', d3.forceX(width / 2).strength(0.06))
      .force('y', d3.forceY(HEIGHT / 2).strength(0.1))
      .force('collide', d3.forceCollide((n) => r(n.id) + 30 * k))
      .stop();
    for (let i = 0; i < 400; i++) {
      sim.tick();
      for (const n of nodes) {
        n.x = Math.max(PAD, Math.min(width - PAD, n.x));
        n.y = Math.max(PAD, Math.min(HEIGHT - PAD, n.y));
      }
    }
    const inset = d3.max(nodes, (n) => r(n.id));
    const fit = (key, lo, hi) => {
      const [min, max] = d3.extent(nodes, (n) => n[key]);
      const s = d3.scaleLinear([min, max], [lo, hi]);
      for (const n of nodes) n[key] = max > min ? s(n[key]) : (lo + hi) / 2;
    };
    fit('x', PAD + inset, width - PAD - inset);
    fit('y', PAD + inset, HEIGHT - PAD - inset);
    const pos = new Map(nodes.map((n) => [n.id, [n.x, n.y]]));

    const svg = d3.select(svgEl).attr('width', width).attr('height', HEIGHT);
    svg.selectAll('*').remove();

    svg
      .append('defs')
      .selectAll('marker')
      .data([...color])
      .join('marker')
      .attr('id', ([name]) => markerId(name))
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 5)
      .attr('markerWidth', 3.5)
      .attr('markerHeight', 3.5)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5Z')
      .style('fill', ([, c]) => c);

    // Straight links; extra edges between the same pair curve out.
    const geo = (e) => {
      const a = pos.get(e.source), b = pos.get(e.target);
      const len = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1;
      return arcPath(a, b, len * 0.15 * e.stack, [(b[1] - a[1]) / len, -(b[0] - a[0]) / len]).d;
    };
    const arcs = svg
      .append('g')
      .attr('fill', 'none')
      .selectAll('path')
      .data(edges)
      .join('path')
      .attr('d', geo)
      .style('stroke', (e) => color.get(e.name))
      .attr('marker-mid', (e) => `url(#${markerId(e.name)})`);

    const symbol = (n) => d3.symbol(n.container ? d3.symbolSquare : d3.symbolCircle, Math.PI * r(n.id) ** 2)();
    const nodeSel = svg
      .append('g')
      .selectAll('path')
      .data(d3.sort(nodes, (n) => -r(n.id)))
      .join('path')
      .attr('transform', (n) => `translate(${n.x},${n.y})`)
      .attr('d', symbol)
      .attr('fill', 'var(--card)')
      .attr('stroke', 'var(--text)')
      .attr('stroke-width', 1.5)
      .style('cursor', 'pointer');

    // Same emphasis rules as the force view: hovered node or legend name
    // brings its edges forward and fades everything else.
    highlight = (hit) => {
      const linked = new Set();
      if (hit) for (const e of edges) if (hit(e)) linked.add(e.source).add(e.target);
      arcs
        .attr('stroke-opacity', (e) => (!hit ? 0.8 : hit(e) ? 1 : 0.1))
        .attr('stroke-width', (e) => (hit?.(e) ? 3.5 : 2));
      nodeSel.attr('opacity', (n) => (!hit || linked.has(n.id) ? 1 : 0.3));
    };
    // untrack: reading the legend selection here must not trigger a full redraw.
    const rest = () => untrack(() => highlight(edgeName ? (e) => e.name === edgeName : null));
    nodeSel
      .on('mouseenter', (_, n) => highlight((e) => e.source === n.id || e.target === n.id))
      .on('mouseleave', rest);
    rest();
  });

  // Re-applied on legend clicks without redrawing the layout.
  $effect(() => {
    const name = edgeName;
    highlight(name ? (e) => e.name === name : null);
  });
</script>

<svelte:window bind:innerHeight={viewportHeight} />

<div bind:clientWidth={width}>
  <div class="rand-bar">
    <ArcLegend bind:selected={edgeName} />
    <button type="button" class="pill-toggle" onclick={() => (seed = Math.floor(Math.random() * 1e9))}>Regenerate</button>
  </div>
  <svg bind:this={svgEl}></svg>
</div>

<style>
  .rand-bar { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }
  svg { display: block; }
</style>
