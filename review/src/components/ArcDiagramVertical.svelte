<script>
  // Vertical arc diagram: nodes in a column, arcs bulging right, card on the right.
  // Data, styling and hover behaviour are shared via lib/arcs.js.
  import * as d3 from 'd3';
  import { edges, nodeIds, radius, arcPath, visById, renderArcDiagram } from '../lib/arcs.js';
  import ArcLegend from './ArcLegend.svelte';
  import ArcCard from './ArcCard.svelte';

  // Right = room for arc labels at the apex; left is sized to the widest node label.
  const MARGIN = { top: 20, right: 130, bottom: 20 };
  const PAGE_GAP = 24; // space kept below the diagram at the bottom of the viewport
  const MIN_ROW = 28; // node spacing never shrinks below this on short screens

  let svgEl;
  let innerHeight = $state(0);
  let svgHeight = $state(0); // card panel is capped to this
  let cards = $state([]); // hovered node (1 card) or edge (source + target); kept after hover-out

  // Widest node label, measured in bold (hover state) so highlighted labels fit too.
  function labelWidth() {
    const ctx = document.createElement('canvas').getContext('2d');
    ctx.font = `bold 11px ${getComputedStyle(svgEl).fontFamily}`;
    return d3.max(nodeIds, (id) => ctx.measureText(visById.get(id)?.title ?? id).width + radius(id));
  }

  $effect(() => {
    const left = labelWidth() + 16;
    // Fill the viewport from the SVG's top edge down, less a small gap.
    const top = svgEl.getBoundingClientRect().top + window.scrollY;
    const height = Math.max(innerHeight - top - PAGE_GAP, MIN_ROW * (nodeIds.length - 1) + MARGIN.top + MARGIN.bottom);
    svgHeight = height;
    const y = d3.scalePoint(nodeIds, [MARGIN.top, height - MARGIN.bottom]);
    const bulge = (e) => (Math.abs(y(e.target) - y(e.source)) / 2) * (1 + 0.3 * e.stack);
    const pos = (id) => [left, y(id)];

    renderArcDiagram(
      svgEl,
      {
        width: left + d3.max(edges, bulge) + MARGIN.right,
        height,
        pos,
        arc: (e) => arcPath(pos(e.source), pos(e.target), bulge(e), [1, 0]),
        arcLabelOffset: [8, 0],
        arcLabelAnchor: 'start',
        // Plain horizontal labels to the left of each node.
        nodeLabel: (text) =>
          text
            .attr('text-anchor', 'end')
            .attr('x', (id) => -radius(id) - 8)
            .attr('dy', '0.32em')
            .text((id) => visById.get(id)?.title ?? id),
      },
      (c) => (cards = c)
    );
  });
</script>

<svelte:window bind:innerHeight />

<div class="arc-wrap">
  <ArcLegend />
  <div class="arc-row">
    <svg bind:this={svgEl}></svg>
    <!-- Card panel: as tall as the diagram at most, so the page never scrolls.
         One card for a node, source above target for an edge. -->
    <aside style:max-height="{svgHeight}px">
      {#each cards as c (c.v.id + c.role)}<ArcCard v={c.v} role={c.role} variant="split" />{:else}<p class="empty">Hover a node or edge to see details.</p>{/each}
    </aside>
  </div>
</div>

<style>
  .arc-wrap { width: 80vw; margin: 0 auto; }
  .arc-row { display: flex; gap: 24px; align-items: flex-start; }
  svg { display: block; flex: none; }
  aside { flex: 1; min-width: 320px; max-width: 560px; margin-left: auto; display: flex; flex-direction: column; gap: 12px; overflow: hidden; }
</style>
