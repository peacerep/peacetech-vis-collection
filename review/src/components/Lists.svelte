<script>
  // The bullet lists shared by the table and the card grid.
  // kind: datasets | dimensions | contributors | links | views | view-names
  import { label, contributor, datasetRef } from '../lib/data.js';
  import Val from './Val.svelte';

  let { kind, items = [], showNote = true } = $props();
</script>

{#if items.length === 0}
  <Val />
{:else}
  <ul class="tight">
    {#each items as item}
      <li>
        {#if kind === 'datasets'}
          {@const d = datasetRef(item)}
          {#if d.missing}
            <span class="flag">{d.name}</span>
          {:else}
            {d.name}
            {#if d.version}
              {#if d.version.missing}<span class="flag">{d.version.label}</span>{:else}<code>{d.version.label}</code>{/if}
            {/if}
            {#if d.uncertain}<span class="flag">⚠</span>{/if}
            {#if showNote && item.usage_note}<span class="dim">— {item.usage_note}</span>{/if}
          {/if}
        {:else if kind === 'dimensions'}
          {label.dimension.get(item.id) ?? item.id}
          <span class="dim">({item.is_covered ? 'covered' : 'not covered'})</span>
          {#if item.description}<span class="dim">— {item.description}</span>{/if}
        {:else if kind === 'contributors'}
          {@const c = contributor(item)}
          <span class:flag={c.missing}>{c.name}</span>
          {#if item.entity_type !== 'person'}<span class="tag-type">org</span>{/if}
        {:else if kind === 'links'}
          <span class="tag-type">{label.linkType.get(item.type) ?? item.type}</span>
          <a href={item.url} target="_blank" rel="noopener">{item.url}</a>
          {#if item.label}<span class="dim">({item.label})</span>{/if}
        {:else if kind === 'views'}
          <strong>{item.name}</strong>
          <span class="dim">({item.kind}, types: <Val value={item.visualisation_types} />)</span>
          — <Val value={item.description} />
        {:else if kind === 'view-names'}
          {item.name}
        {/if}
      </li>
    {/each}
  </ul>
{/if}
