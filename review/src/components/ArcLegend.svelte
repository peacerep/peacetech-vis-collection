<script>
  // One swatch per edge name, plus the node encoding. Clicking a name selects
  // it (bound `selected`); clicking it again clears the selection.
  import { edgeNames, color } from '../lib/arcs.js';

  let { selected = $bindable(null) } = $props();
</script>

<div class="arc-legend">
  {#each edgeNames as name}
    <button
      type="button"
      class:active={selected === name}
      class:dimmed={selected && selected !== name}
      aria-pressed={selected === name}
      onclick={() => (selected = selected === name ? null : name)}
    ><i style:background={color.get(name)}></i>{name}</button>
  {/each}
  <span class="dim">● standalone · ■ container · size = no. of links</span>
</div>

<style>
  .arc-legend { display: flex; flex-wrap: wrap; align-items: center; gap: 4px 6px; font-size: 12px; margin-bottom: 8px; }
  .arc-legend button { font: inherit; color: var(--text); background: none; border: 1px solid transparent; border-radius: 4px; padding: 2px 6px; cursor: pointer; }
  .arc-legend button:hover { border-color: var(--border); }
  .arc-legend button.active { border-color: var(--text); font-weight: 600; }
  .arc-legend button.dimmed { opacity: 0.45; }
  .arc-legend .dim { margin-left: 8px; }
  .arc-legend i { display: inline-block; width: 14px; height: 3px; margin-right: 5px; vertical-align: middle; }
</style>
