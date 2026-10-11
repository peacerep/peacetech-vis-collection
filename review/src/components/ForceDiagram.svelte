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

  const FONT_SIZE = 11;
  const LINE_HEIGHT = 12.5;
  const ASCENT = 9; // baseline offset of a line's top edge at 11px
  const GAP = 4; // space between a node's edge and its label

  // Does segment a→b cross the box? (Liang–Barsky clipping.)
  function segmentHitsBox([x1, y1], [x2, y2], b) {
    const dx = x2 - x1, dy = y2 - y1;
    let t0 = 0, t1 = 1;
    for (const [p, q] of [[-dx, x1 - b.x0], [dx, b.x1 - x1], [-dy, y1 - b.y0], [dy, b.y1 - y1]]) {
      if (p === 0) { if (q < 0) return false; continue; }
      const t = q / p;
      if (p < 0) t0 = Math.max(t0, t);
      else t1 = Math.min(t1, t);
      if (t0 > t1) return false;
    }
    return true;
  }
  const overlap = (a, b) =>
    Math.max(0, Math.min(a.x1, b.x1) - Math.max(a.x0, b.x0)) * Math.max(0, Math.min(a.y1, b.y1) - Math.max(a.y0, b.y0));

  // Greedy label placement, biggest nodes first: each label tries 8 spots
  // around its node and takes the one overlapping the fewest other nodes,
  // already-placed labels and links (and staying inside the frame). Ties go
  // to the earlier candidate, so labels sit to the right unless that clashes.
  // Returns id → { anchor, x, y (top of first line, relative to node), lines }.
  function placeLabels(pos, r, height) {
    const ctx = document.createElement('canvas').getContext('2d');
    // Measured in bold so a highlighted label still fits its reserved box.
    ctx.font = `700 ${FONT_SIZE}px ${getComputedStyle(svgEl).fontFamily}`;
    const nodeBox = (id) => {
      const [x, y] = pos(id), rr = r(id);
      return { id, x0: x - rr, x1: x + rr, y0: y - rr, y1: y + rr };
    };
    const nodeBoxes = allNodeIds.map(nodeBox);
    const links = edges.map((e) => [e.source, e.target]);
    const placed = [];
    const result = new Map();

    for (const id of d3.sort(allNodeIds, (id) => -radius(id))) {
      const lines = wrapLabel(visById.get(id)?.title ?? id);
      const w = d3.max(lines, (l) => ctx.measureText(l).width);
      const h = LINE_HEIGHT * lines.length;
      const rr = r(id), d = rr * Math.SQRT1_2; // diagonal offset to the circle's edge
      const [nx, ny] = pos(id);
      // [anchor, label x, label top y] relative to the node centre.
      const candidates = [
        ['start', rr + GAP, -h / 2], // right
        ['end', -rr - GAP, -h / 2], // left
        ['start', d + GAP, -d - h], // above right
        ['start', d + GAP, d], // below right
        ['end', -d - GAP, -d - h], // above left
        ['end', -d - GAP, d], // below left
        ['middle', 0, -rr - GAP - h], // above
        ['middle', 0, rr + GAP], // below
      ];
      let best, bestCost = Infinity;
      candidates.forEach(([anchor, x, y], rank) => {
        const x0 = nx + (anchor === 'start' ? x : anchor === 'end' ? x - w : -w / 2);
        const box = { x0, x1: x0 + w, y0: ny + y, y1: ny + y + h };
        let cost = rank * 0.5;
        const outside = Math.max(0, -box.x0) + Math.max(0, box.x1 - width) + Math.max(0, -box.y0) + Math.max(0, box.y1 - height);
        cost += outside * 50;
        for (const n of nodeBoxes) if (n.id !== id) cost += overlap(box, n) * 3;
        for (const p of placed) cost += overlap(box, p) * 5;
        for (const [s, t] of links) if (segmentHitsBox(pos(s), pos(t), box)) cost += 40;
        if (cost < bestCost) (bestCost = cost), (best = { anchor, x, y, lines, box });
      });
      placed.push(best.box);
      result.set(id, best);
    }
    return result;
  }

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
    const labelAt = placeLabels(pos, r, HEIGHT);

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
        arrowSize: 3.5,
        // Labels wrapped to two lines, at the spot placeLabels picked per node.
        nodeLabel: (text) =>
          text
            .attr('text-anchor', (id) => labelAt.get(id).anchor)
            .selectAll('tspan')
            .data((id) => labelAt.get(id).lines.map((line, i) => ({ id, line, i })))
            .join('tspan')
            .attr('x', (t) => labelAt.get(t.id).x)
            .attr('y', (t) => labelAt.get(t.id).y + LINE_HEIGHT * t.i + ASCENT)
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
