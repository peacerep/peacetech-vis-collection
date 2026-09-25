<script>
  import { vis, isFlagged } from '../lib/data.js';
  import VisTable from './VisTable.svelte';
  import VisGrid from './VisGrid.svelte';

  const VIEWS = [
    { id: 'table', label: 'Table' },
    { id: 'grid', label: 'Grid' },
    { id: 'grid-compact', label: 'Grid (compact)' },
  ];

  let view = $state('table');
  let flaggedOnly = $state(false);
  let showExcluded = $state(false);
  let columns = $state({ status: true, structure: true, links: true });

  const excludedCount = vis.filter((v) => v.excluded).length;
  const visible = $derived(showExcluded ? vis : vis.filter((v) => !v.excluded));
  const flaggedCount = $derived(visible.filter(isFlagged).length);
  const items = $derived(flaggedOnly ? visible.filter(isFlagged) : visible);
</script>

<div class="vis-toolbar">
  <p class="stats">
    {visible.length} visualisations{#if !showExcluded}{' '}({excludedCount} excluded hidden){/if} &nbsp;·&nbsp; <span class="flag">{flaggedCount} flagged</span>
  </p>
  <div class="vis-controls">
    <div class="seg">
      {#each VIEWS as v}
        <button type="button" class:active={view === v.id} onclick={() => (view = v.id)}>{v.label}</button>
      {/each}
    </div>
    <button type="button" class="pill-toggle" class:active={flaggedOnly} onclick={() => (flaggedOnly = !flaggedOnly)}>
      Flagged only
    </button>
    <button type="button" class="pill-toggle" class:active={showExcluded} onclick={() => (showExcluded = !showExcluded)}>
      Show excluded
    </button>
  </div>
</div>

{#if view === 'table'}
  <VisTable {items} bind:enabled={columns} />
{:else}
  <VisGrid {items} compact={view === 'grid-compact'} />
{/if}
