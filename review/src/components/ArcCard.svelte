<script>
  // Card for a hovered visualisation: thumbnail, title, tags, links, summary.
  // variant 'wide'  → thumbnail | details | summary, all in one row;
  //         'split' → thumbnail | details, summary underneath (for narrower cards).
  // `role` ('Source' / 'Target') marks the card's end of a hovered edge.
  import { thumbSrc, label } from '../lib/data.js';
  import { statusTags, structureTags } from '../lib/arcs.js';

  let { v, role = '', variant = 'wide' } = $props();
  const src = $derived(thumbSrc(v));
</script>

<div class="gridcard arc-card {variant}">
  {#if src}<img class="thumb" src={src} alt={v.thumbnail.alt_text} />{:else}<div class="thumb thumb-empty">no image</div>{/if}
  <div class="arc-card-meta">
    {#if role}<div class="arc-role">{role}</div>{/if}
    <div class="cell-title">{v.title}</div>
    <div class="cell-id"><code>{v.id}</code></div>
    <div class="arc-tags">
      {#each statusTags(v) as t}<span class="tag-type">{t}</span>{/each}
      {#each structureTags(v) as t}<span class="tag-type tag-structure">{t}</span>{/each}
    </div>
    <div class="arc-links">
      {#each v.links as l, i}
        {#if i}<span class="dim"> · </span>{/if}<a href={l.url} target="_blank" rel="noreferrer">{label.linkType.get(l.type) ?? l.type}</a>
      {/each}
    </div>
  </div>
  <p class="arc-card-summary">{v.description?.summary || '—'}</p>
</div>

<style>
  .arc-card { padding: 12px; gap: 12px 16px; }
  .arc-card-meta { min-width: 0; }
  .arc-role { font-size: 10.5px; text-transform: uppercase; letter-spacing: .04em; color: var(--muted); margin-bottom: 2px; }
  .arc-tags { display: flex; flex-wrap: wrap; gap: 4px; margin: 8px 0; }
  .tag-structure { background: var(--border); color: var(--text); }
  .arc-links { font-size: 12.5px; }
  .arc-card-summary { margin: 0; color: var(--muted); }

  .wide { display: flex; }
  .wide .thumb { width: 200px; height: 130px; flex: none; }
  .wide .arc-card-meta, .wide .arc-card-summary { flex: 1; }

  .split { display: grid; grid-template-columns: 140px 1fr; }
  .split .thumb { width: 100%; height: 90px; }
  .split .arc-card-summary { grid-column: 1 / -1; }
</style>
