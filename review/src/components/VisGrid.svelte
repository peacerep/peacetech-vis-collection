<script>
  // Card grid. `compact` drops Alt Text and dataset usage notes, and lists
  // Views/Components by name only.
  import { label, isFlagged, thumbSrc, toolNames, statusText } from '../lib/data.js';
  import Val from './Val.svelte';
  import Lists from './Lists.svelte';
  import Structure from './Structure.svelte';

  let { items, compact = false } = $props();
</script>

<div class="cardgrid-multi">
  {#each items as v (v.id)}
    <article class="gridcard" class:row-flagged={isFlagged(v)}>
      {#if thumbSrc(v)}
        <img class="thumb" src={thumbSrc(v)} alt="" loading="lazy" />
      {:else}
        <div class="thumb thumb-empty">—</div>
      {/if}
      <div class="gridcard-body">
        <h3>{v.title}</h3>
        <div class="gf"><div class="gfl">ID</div><div class="gfv"><code>{v.id}</code></div></div>
        {@render text('Status', statusText(v))}
        <div class="gf"><div class="gfl">Structure</div><div class="gfv"><Structure {v} /></div></div>
        {@render text('Summary', v.description.summary)}
        {@render text('Keywords', v.description.keywords)}
        {@render text('Research Qs', v.description.research_questions)}
        {@render text('Audiences', v.description.audiences)}
        {@render list('Datasets', 'datasets', v.data_coverage.datasets)}
        {@render list('Dimensions', 'dimensions', v.data_coverage.dimensions)}
        {@render list('Contributors', 'contributors', v.contributors)}
        {@render text('Tools', toolNames(v))}
        {@render list('Links', 'links', v.links)}
        {@render text('Vis Types', v.content.visualisation_types.map((t) => label.visType.get(t) ?? t))}
        {@render list('Views/Components', compact ? 'view-names' : 'views', v.content.views_components)}
        {#if !compact}{@render text('Alt Text', v.thumbnail.alt_text)}{/if}
        {@render text('Credit', v.thumbnail.credit)}
        {@render text('Created', v.timestamps.created_at)}
        {@render text('Updated', v.timestamps.updated_at)}
        {@render text('Notes', v.notes)}
      </div>
    </article>
  {/each}
</div>

{#snippet text(name, value)}
  <div class="gf"><div class="gfl">{name}</div><div class="gfv"><Val {value} /></div></div>
{/snippet}

{#snippet list(name, kind, items)}
  <div class="gf">
    <div class="gfl">{name}</div>
    <div class="gfv"><Lists {kind} {items} showNote={!compact} /></div>
  </div>
{/snippet}
