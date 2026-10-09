<script>
  // Checklist for the relationship-labelling study: one row per ordered A → B
  // pair from relationships.json. Tick which pairs go into the study and edit
  // the expected label(s); picks are kept in this browser and exported as CSV.
  import { edges, visById } from '../lib/arcs.js';
  import { thumbSrc } from '../lib/data.js';

  const STORE_KEY = 'study-pairs-v2';

  // Group edges by ordered pair, keeping first-seen order.
  const pairs = [];
  const byKey = new Map();
  for (const e of edges) {
    const key = `${e.source}→${e.target}`;
    if (!byKey.has(key)) {
      const p = { key, source: e.source, target: e.target, labels: [] };
      byKey.set(key, p);
      pairs.push(p);
    }
    byKey.get(key).labels.push(e.name);
  }

  // Defaults: nothing included; labels text pre-filled from relationships.json.
  const defaults = () =>
    Object.fromEntries(pairs.map((p) => [p.key, { include: false, labels: p.labels.join('; ') }]));

  function load() {
    const base = defaults();
    try {
      const saved = JSON.parse(localStorage.getItem(STORE_KEY) ?? '{}');
      for (const k of Object.keys(base)) if (saved[k]) base[k] = { ...base[k], ...saved[k] };
    } catch {}
    return base;
  }

  let picks = $state(load());
  let includedOnly = $state(false);

  $effect(() => {
    const json = JSON.stringify(picks);
    try { localStorage.setItem(STORE_KEY, json); } catch {}
  });

  const rows = $derived(includedOnly ? pairs.filter((p) => picks[p.key].include) : pairs);
  const includedCount = $derived(pairs.filter((p) => picks[p.key].include).length);

  // Differs from what relationships.json says → highlight so edits stand out.
  const changed = (p) => picks[p.key].labels.trim() !== p.labels.join('; ');

  function reset() {
    if (confirm('Reset all ticks and labels to the relationships.json defaults?')) picks = defaults();
  }

  const title = (id) => visById.get(id)?.title ?? id;
  const link = (id) => {
    const ls = visById.get(id)?.links ?? [];
    return (ls.find((l) => l.type === 'public_link') ?? ls[0])?.url;
  };

  // Qualtrics card template (stacked rows, inline styles). Images point at a
  // placeholder naming the mini-fig file, to swap for its Qualtrics Graphics Library URL.
  const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);
  function cardHtml(id, letter, colour) {
    const v = visById.get(id);
    const url = link(id);
    const img = v?.thumbnail?.url ? `QUALTRICS_IMAGE_URL_FOR_${v.thumbnail.url}` : 'QUALTRICS_IMAGE_URL';
    return `<table style="width: 100%; border-collapse: collapse; margin: 0 0 10px; border: 1px solid #e0e0dd;">
  <tr>
    <td style="width: 150px; padding: 8px; vertical-align: top;">
      <img src="${esc(img)}" alt="Screenshot of visualisation ${letter}" style="width: 150px; height: 100px; object-fit: cover; display: block;" />
    </td>
    <td style="padding: 8px 12px; vertical-align: top;">
      <p style="margin: 0 0 4px; font-size: 16px;"><strong style="color: ${colour};">${letter}</strong> · <strong>${esc(title(id))}</strong></p>
      <p style="margin: 0 0 6px; font-size: 14px; color: #444444;">${esc(v?.description?.summary)}</p>${
        url ? `\n      <a href="${esc(url)}" target="_blank" rel="noopener" style="font-size: 13px;">Open visualisation ${letter} ↗</a>` : ''
      }
    </td>
  </tr>
</table>`;
  }
  const pairHtml = (p) => `${cardHtml(p.source, 'A', '#1f6fd1')}\n\n${cardHtml(p.target, 'B', '#b5401f')}`;

  let copied = $state('');
  async function copyHtml(p) {
    try {
      await navigator.clipboard.writeText(pairHtml(p));
      copied = p.key;
      setTimeout(() => copied === p.key && (copied = ''), 1500);
    } catch {
      alert('Clipboard not available — use Export Qualtrics HTML instead.');
    }
  }

  function download(text, name, type) {
    const a = Object.assign(document.createElement('a'), { href: URL.createObjectURL(new Blob([text], { type })), download: name });
    a.click();
    URL.revokeObjectURL(a.href);
  }

  function exportHtml() {
    const chosen = pairs.filter((p) => picks[p.key].include);
    const blocks = chosen.map(
      (p, i) => `<!-- ===== Pair ${i + 1}/${chosen.length}: ${p.source} → ${p.target} ===== -->\n${pairHtml(p)}`
    );
    download(blocks.join('\n\n\n'), 'study_pairs_qualtrics.html', 'text/html');
  }

  function exportCsv() {
    const q = (s) => `"${String(s ?? '').replaceAll('"', '""')}"`;
    const header = ['source_id', 'source_title', 'target_id', 'target_title', 'labels', 'original_labels'];
    const lines = pairs
      .filter((p) => picks[p.key].include)
      .map((p) =>
        [p.source, title(p.source), p.target, title(p.target), picks[p.key].labels, p.labels.join('; ')]
          .map(q)
          .join(',')
      );
    download([header.join(','), ...lines].join('\n'), 'study_pairs.csv', 'text/csv');
  }
</script>

<div class="vis-toolbar">
  <p class="stats">
    {pairs.length} pairs &nbsp;·&nbsp; {includedCount} included &nbsp;·&nbsp;
    <span class="dim">ticks are saved in this browser only</span>
  </p>
  <div class="vis-controls">
    <button type="button" class="pill-toggle" class:active={includedOnly} onclick={() => (includedOnly = !includedOnly)}>Included only</button>
    <button type="button" class="pill-toggle" onclick={exportCsv}>Export CSV</button>
    <button type="button" class="pill-toggle" onclick={exportHtml}>Export Qualtrics HTML</button>
    <button type="button" class="pill-toggle" onclick={reset}>Reset</button>
  </div>
</div>

<div class="table-wrap">
  <table class="pairs-table">
    <thead>
      <tr>
        <th>#</th>
        <th>Include</th>
        <th>Visualisation A</th>
        <th></th>
        <th>Visualisation B</th>
        <th>Labels</th>
        <th>Qualtrics</th>
      </tr>
    </thead>
    <tbody>
      {#each rows as p, i (p.key)}
        <tr>
          <td class="dim">{i + 1}</td>
          <td class="tick"><input type="checkbox" bind:checked={picks[p.key].include} /></td>
          {@render visCell(p.source)}
          <td class="arrow">→</td>
          {@render visCell(p.target)}
          <td class:changed={changed(p)} title={changed(p) ? `Differs from relationships.json: ${p.labels.join('; ')}` : ''}>
            <textarea rows="2" bind:value={picks[p.key].labels} placeholder="labels…"></textarea>
          </td>
          <td><button type="button" class="pill-toggle" onclick={() => copyHtml(p)}>{copied === p.key ? 'Copied ✓' : 'Copy HTML'}</button></td>
        </tr>
      {/each}
    </tbody>
  </table>
</div>

{#snippet visCell(id)}
  {@const v = visById.get(id)}
  {@const src = v && thumbSrc(v)}
  <td class="vis">
    {#if src}<img class="thumb" src={src} alt={v.thumbnail.alt_text} />{:else}<div class="thumb thumb-empty">no image</div>{/if}
    <div>
      <div class="cell-title">{#if link(id)}<a href={link(id)} target="_blank" rel="noreferrer">{title(id)}</a>{:else}{title(id)}{/if}</div>
      <div class="cell-id"><code>{id}</code></div>
    </div>
  </td>
{/snippet}

<style>
  .vis { display: flex; gap: 8px; min-width: 230px; }
  .vis .thumb { flex: none; }
  .arrow { font-size: 18px; color: var(--muted); text-align: center; }
  .tick { text-align: center; vertical-align: middle; }
  .tick input { width: 16px; height: 16px; cursor: pointer; }
  td.changed { background: var(--accent-bg); }
  textarea { width: 160px; font: inherit; font-size: 12px; background: var(--bg); color: var(--text); border: 1px solid var(--border); border-radius: 4px; resize: vertical; }
</style>
