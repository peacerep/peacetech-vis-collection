<script>
  // Horizontal arc diagram: nodes in a row, arcs above, card below.
  // Data, styling and hover behaviour are shared via lib/arcs.js.
  import * as d3 from 'd3';
  import { edges, nodeIds, radius, arcPath, wrapLabel, visById, renderArcDiagram } from '../lib/arcs.js';
  import ArcLegend from './ArcLegend.svelte';
  import ArcCard from './ArcCard.svelte';

  // Left/bottom leave room for labels rotated -45° down-left of each node.
  const MARGIN = { top: 30, right: 20, bottom: 130, left: 130 };

  let width = $state(0);
  let svgEl;
  let cards = $state([]); // hovered node (1 card) or edge (source + target); kept after hover-out

  $effect(() => {
    if (!width) return;
    const x = d3.scalePoint(nodeIds, [MARGIN.left, width - MARGIN.right]);
    const bulge = (e) => (Math.abs(x(e.target) - x(e.source)) / 2) * (1 + 0.3 * e.stack);
    const baseline = MARGIN.top + d3.max(edges, bulge);
    const pos = (id) => [x(id), baseline];

    renderArcDiagram(
      svgEl,
      {
        width,
        height: baseline + MARGIN.bottom,
        pos,
        arc: (e) => arcPath(pos(e.source), pos(e.target), bulge(e), [0, -1]),
        arcLabelOffset: [0, -10],
        arcLabelAnchor: 'middle',
        // Labels rotated -45°, wrapped to two lines centred on the node.
        nodeLabel: (text) =>
          text
            .attr('transform', 'rotate(-45)')
            .attr('text-anchor', 'end')
            .selectAll('tspan')
            .data((id) => wrapLabel(visById.get(id)?.title ?? id).map((line, i, all) => ({ id, line, i, n: all.length })))
            .join('tspan')
            .attr('x', (t) => -radius(t.id) - 6)
            .attr('dy', (t) => (t.i === 0 ? `${0.32 - 0.55 * (t.n - 1)}em` : '1.1em'))
            .text((t) => t.line),
      },
      (c) => (cards = c)
    );
  });
</script>

<div class="arc-wrap" bind:clientWidth={width}>
  <ArcLegend />
  <svg bind:this={svgEl}></svg>
  <!-- One wide card for a node; source and target side by side (summary below) for an edge. -->
  <div class="arc-cards">
    {#each cards as c (c.v.id + c.role)}<ArcCard v={c.v} role={c.role} variant={cards.length > 1 ? 'split' : 'wide'} />{:else}<p class="empty">Hover a node or edge to see details.</p>{/each}
  </div>
</div>

<style>
  .arc-wrap { width: 80vw; margin: 0 auto; }
  svg { display: block; }
  .arc-cards { display: flex; gap: 16px; }
  .arc-cards > :global(*) { flex: 1; min-width: 0; }
</style>
