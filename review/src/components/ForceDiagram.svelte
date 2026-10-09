<script>
  // Force-directed network of the same relationships: positions come from a
  // d3-force simulation (run to rest up front), edges are straight links.
  // Data, styling and hover behaviour are shared via lib/arcs.js.
  import * as d3 from 'd3';
  import { edges, allNodeIds, radius, arcPath, wrapLabel, visById, renderArcDiagram } from '../lib/arcs.js';
  import ArcLegend from './ArcLegend.svelte';
  import ArcCard from './ArcCard.svelte';
  import EdgeCard from './EdgeCard.svelte';

  // Sizes are tuned for an 860px-tall canvas and shrink proportionally below it.
  const DESIGN_HEIGHT = 860;
  const MIN_HEIGHT = 480;
  const PAD = 40; // keep nodes inside the frame; labels get extra room on the right
  const LABEL_ROOM = 140;
  const NODE_SCALE = 4.4; // bigger nodes so the thumbnails read

  let width = $state(0);
  let viewportHeight = $state(0);
  let svgEl;
  let cards = $state([]); // hovered node (1 card) or edge (source + target); kept after hover-out
  let edge = $state(null); // hovered/clicked edge, shown in its own card above the node cards
  let edgeName = $state(null); // legend selection: highlights every edge of that name
  let diagram = $state.raw(null);

  $effect(() => {
    if (!width || !viewportHeight) return;
    // Fill what's left of the viewport below the SVG's top edge, minus the
    // page's bottom padding, so the whole view fits without scrolling.
    const top = svgEl.getBoundingClientRect().top + window.scrollY;
    const bottom = parseFloat(getComputedStyle(document.body).paddingBottom) || 0;
    const HEIGHT = Math.max(MIN_HEIGHT, Math.floor(viewportHeight - top - bottom - 4));
    const k = Math.min(1, HEIGHT / DESIGN_HEIGHT);
    const scale = NODE_SCALE * k;
    const r = (id) => radius(id) * scale;

    const nodes = allNodeIds.map((id) => ({ id }));
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
        n.x = Math.max(PAD, Math.min(width - LABEL_ROOM, n.x));
        n.y = Math.max(PAD, Math.min(HEIGHT - PAD, n.y));
      }
    }
    // The forces settle into a fixed-size cluster regardless of canvas size;
    // stretch it so it fills the frame (inset by node radius so nothing clips).
    const inset = d3.max(nodes, (n) => r(n.id));
    const fit = (key, lo, hi) => {
      const [min, max] = d3.extent(nodes, (n) => n[key]);
      const s = d3.scaleLinear([min, max], [lo, hi]);
      for (const n of nodes) n[key] = max > min ? s(n[key]) : (lo + hi) / 2;
    };
    fit('x', PAD + inset, width - LABEL_ROOM - inset);
    fit('y', PAD + inset, HEIGHT - PAD - inset);
    const at = new Map(nodes.map((n) => [n.id, [n.x, n.y]]));
    const pos = (id) => at.get(id);

    diagram = renderArcDiagram(
      svgEl,
      {
        width,
        height: HEIGHT,
        pos,
        nodeIds: allNodeIds,
        nodeScale: scale,
        thumbnails: true,
        // Straight link; extra edges between the same pair curve out so they
        // don't overlap (a zero-radius arc is drawn as a straight line).
        arc: (e) => {
          const a = pos(e.source), b = pos(e.target);
          const len = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1;
          const normal = [(b[1] - a[1]) / len, -(b[0] - a[0]) / len];
          return arcPath(a, b, len * 0.15 * e.stack, normal);
        },
        arcLabelOffset: [0, -8],
        arcLabelAnchor: 'middle',
        // Labels to the right of each node, wrapped to two lines.
        nodeLabel: (text) =>
          text
            .selectAll('tspan')
            .data((id) => wrapLabel(visById.get(id)?.title ?? id).map((line, i, all) => ({ id, line, i, n: all.length })))
            .join('tspan')
            .attr('x', (t) => r(t.id) + 5)
            .attr('dy', (t) => (t.i === 0 ? `${0.32 - 0.55 * (t.n - 1)}em` : '1.1em'))
            .text((t) => t.line),
      },
      (c, e) => ((cards = c), (edge = e))
    );
  });

  // Re-applied after every redraw (diagram changes) and on legend clicks.
  $effect(() => diagram?.setEdgeName(edgeName));
</script>

<svelte:window bind:innerHeight={viewportHeight} />

<!-- Network on the left (2/3), hover cards stacked on the right (1/3), centred vertically. -->
<div class="force-wrap">
  <div bind:clientWidth={width}>
    <ArcLegend bind:selected={edgeName} />
    <svg bind:this={svgEl}></svg>
  </div>
  <div class="force-cards">
    {#if edge}<EdgeCard e={edge} />{/if}
    {#each cards as c (c.v.id + c.role)}<ArcCard v={c.v} role={c.role} variant="split" />{:else}<p class="empty">Hover a node or edge to see details.</p>{/each}
  </div>
</div>

<style>
  .force-wrap { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }
  .force-wrap > * { min-width: 0; }
  svg { display: block; }
  .force-cards { display: flex; flex-direction: column; justify-content: center; gap: 12px; }
</style>
