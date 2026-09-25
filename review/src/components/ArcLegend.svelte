<script>
  // One swatch per edge name, grouped by type, plus the node encoding.
  import { namesOf, color } from '../lib/arcs.js';
</script>

<div class="arc-legend">
  {#each ['structural', 'design'] as type}
    <span class="dim">{type}:</span>
    {#each namesOf(type) as name}
      <span><i style:background={color.get(name)}></i>{name}</span>
    {/each}
  {/each}
  <span class="dim">● standalone · ■ container · size = no. of links</span>
</div>

<style>
  .arc-legend { display: flex; flex-wrap: wrap; gap: 4px 14px; font-size: 12px; margin-bottom: 8px; }
  .arc-legend i { display: inline-block; width: 14px; height: 3px; margin-right: 5px; vertical-align: middle; }
</style>
