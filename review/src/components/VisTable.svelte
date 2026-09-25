<script>
  import { label, isFlagged, thumbSrc, toolNames, statusText } from '../lib/data.js';
  import Val from './Val.svelte';
  import Lists from './Lists.svelte';
  import Structure from './Structure.svelte';

  // `enabled` is bound from the parent so toggles survive switching views.
  let { items, enabled = $bindable({}) } = $props();

  // Columns marked `always` can't be hidden; the rest are switched on/off via
  // the checkboxes above the table (defaults are set in Visualisations.svelte).
  const COLUMNS = [
    { key: 'thumb', label: 'Thumb', always: true },
    { key: 'title', label: 'Title', always: true },
    { key: 'description', label: 'Description' },
    { key: 'status', label: 'Status' },
    { key: 'structure', label: 'Structure' },
    { key: 'datasets', label: 'Datasets' },
    { key: 'dimensions', label: 'Dimensions' },
    { key: 'contributors', label: 'Contributors' },
    { key: 'tools', label: 'Tools' },
    { key: 'links', label: 'Links' },
    { key: 'vis_types', label: 'Vis Types' },
    { key: 'views_components', label: 'Views/Components' },
    { key: 'alt_text', label: 'Alt Text' },
    { key: 'credit', label: 'Credit' },
    { key: 'created', label: 'Created' },
    { key: 'updated', label: 'Updated' },
    { key: 'notes', label: 'Notes' },
  ];

  const shown = $derived(COLUMNS.filter((c) => c.always || enabled[c.key]));
</script>

<div class="col-toggles">
  {#each COLUMNS.filter((c) => !c.always) as col}
    <label class="col-toggle-label">
      <input type="checkbox" bind:checked={enabled[col.key]} /> {col.label}
    </label>
  {/each}
</div>

<div class="table-wrap">
  <table class="vis-table">
    <thead>
      <tr>{#each shown as col}<th data-col={col.key}>{col.label}</th>{/each}</tr>
    </thead>
    <tbody>
      {#each items as v (v.id)}
        <tr class:row-flagged={isFlagged(v)}>
          {#each shown as col}
            <td data-col={col.key}>{@render cell(v, col.key)}</td>
          {/each}
        </tr>
      {:else}
        <tr><td colspan={shown.length} class="empty">none</td></tr>
      {/each}
    </tbody>
  </table>
</div>

{#snippet cell(v, key)}
  {#if key === 'thumb'}
    {#if thumbSrc(v)}
      <img class="thumb thumb-sm" src={thumbSrc(v)} alt="" loading="lazy" />
    {:else}
      <div class="thumb thumb-sm thumb-empty">—</div>
    {/if}
  {:else if key === 'title'}
    <div class="cell-title">{v.title}</div>
    <div class="cell-id"><code>{v.id}</code></div>
  {:else if key === 'description'}
    {@const d = v.description}
    {#if d.summary}<div class="desc-summary">{d.summary}</div>{/if}
    {#if d.keywords.length}<div class="dim">Keywords: {d.keywords.join(', ')}</div>{/if}
    {#if d.research_questions.length}<div class="dim">Research Qs: {d.research_questions.join(', ')}</div>{/if}
    {#if d.audiences.length}<div class="dim">Audiences: {d.audiences.join(', ')}</div>{/if}
    {#if !d.summary && !d.keywords.length && !d.research_questions.length && !d.audiences.length}<Val />{/if}
  {:else if key === 'status'}
    <Val value={statusText(v)} />
  {:else if key === 'structure'}
    <Structure {v} />
  {:else if key === 'datasets'}
    <Lists kind="datasets" items={v.data_coverage.datasets} />
  {:else if key === 'dimensions'}
    <Lists kind="dimensions" items={v.data_coverage.dimensions} />
  {:else if key === 'contributors'}
    <Lists kind="contributors" items={v.contributors} />
  {:else if key === 'tools'}
    <Val value={toolNames(v)} />
  {:else if key === 'links'}
    <Lists kind="links" items={v.links} />
  {:else if key === 'vis_types'}
    <Val value={v.content.visualisation_types.map((t) => label.visType.get(t) ?? t)} />
  {:else if key === 'views_components'}
    <Lists kind="views" items={v.content.views_components} />
  {:else if key === 'alt_text'}
    <Val value={v.thumbnail.alt_text} />
  {:else if key === 'credit'}
    <Val value={v.thumbnail.credit} />
  {:else if key === 'created'}
    <Val value={v.timestamps.created_at} />
  {:else if key === 'updated'}
    <Val value={v.timestamps.updated_at} />
  {:else if key === 'notes'}
    <Val value={v.notes} />
  {/if}
{/snippet}
