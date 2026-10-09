<script>
  // Card for a hovered/clicked edge: relation name (in its colour), type,
  // source → target titles, and its tooltip text from relationships.json.
  import { color, visById, edgeTooltip } from '../lib/arcs.js';

  let { e } = $props();
  const title = (id) => visById.get(id)?.title ?? id;
  const text = $derived(edgeTooltip(e));
</script>

<div class="gridcard edge-card" style:border-left-color={color.get(e.name)}>
  <div class="edge-head">
    <span class="edge-name" style:color={color.get(e.name)}>{e.name}</span>
    <!-- <span class="tag-type tag-structure">{e.type}</span> -->
  </div>
  <!-- <div class="edge-ends">{title(e.source)} <span class="dim">→</span> {title(e.target)}</div> -->
  {#if text}<p class="edge-text">{text}</p>{:else}<p class="edge-text dim">No description yet.</p>{/if}
</div>

<style>
  .edge-card { padding: 10px 12px; border-left-width: 4px; }
  .edge-head { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
  .edge-name { font-weight: 700; font-size: 14px; }
  /* .tag-structure { background: var(--border); color: var(--text); } */
  /* .edge-ends { font-size: 12.5px; } */
  .edge-text { margin: 6px 0 0; font-size: 12.5px; }
</style>
