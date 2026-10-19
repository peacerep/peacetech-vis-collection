<script>
  // Checklist for the relationship-labelling study: one row per ordered A → B
  // pair from relationships.json, sorted by label. Tick which pairs go into the
  // study and set a confidence level and slot; picks are kept in this browser
  // and exported as CSV.
  import { edges, visById, color, edgeTooltip } from '../lib/arcs.js';
  import { thumbSrc } from '../lib/data.js';

  const STORE_KEY = 'study-pairs-v2';

  // Group edges by ordered pair, keeping first-seen order.
  const pairs = [];
  const byKey = new Map();
  for (const e of edges) {
    const key = `${e.source}→${e.target}`;
    if (!byKey.has(key)) {
      const p = { key, source: e.source, target: e.target, labels: [], notes: [] };
      byKey.set(key, p);
      pairs.push(p);
    }
    byKey.get(key).labels.push(e.name);
    // Edge tooltip with [source]/[target] replaced by the visualisation titles.
    if (e.tooltip) byKey.get(key).notes.push(edgeTooltip(e));
  }
  pairs.sort((a, b) => a.labels.join('; ').localeCompare(b.labels.join('; ')));

  const CONFIDENCE = ['high', 'medium', 'low'];

  // Defaults: nothing included, no confidence or slot set.
  const defaults = () =>
    Object.fromEntries(pairs.map((p) => [p.key, { include: false, confidence: '', slot: '' }]));

  function load() {
    const base = defaults();
    try {
      const saved = JSON.parse(localStorage.getItem(STORE_KEY) ?? '{}');
      for (const k of Object.keys(base))
        if (saved[k]) base[k] = { include: !!saved[k].include, confidence: saved[k].confidence ?? '', slot: saved[k].slot ?? '' };
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

  function reset() {
    if (confirm('Reset all ticks, confidence levels and slots?')) picks = defaults();
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

  // `copied` = key of the button just used, so it can show a tick briefly.
  let copied = $state('');
  async function copy(text, key, fallback) {
    try {
      await navigator.clipboard.writeText(text);
      copied = key;
      setTimeout(() => copied === key && (copied = ''), 1500);
    } catch {
      alert(`Clipboard not available — ${fallback}`);
    }
  }
  const copyHtml = (p) => copy(pairHtml(p), `${p.key}:html`, 'use Export Qualtrics HTML instead.');
  const notesText = (p) => p.notes.join('\n');
  const copyNotes = (p) => copy(notesText(p), `${p.key}:notes`, 'use Export CSV instead.');

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
    const header = ['source_id', 'source_title', 'target_id', 'target_title', 'labels', 'notes', 'confidence', 'slot'];
    const lines = pairs
      .filter((p) => picks[p.key].include)
      .map((p) =>
        [p.source, title(p.source), p.target, title(p.target), p.labels.join('; '), notesText(p), picks[p.key].confidence, picks[p.key].slot]
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
        <th>Confidence</th>
        <th>Slot</th>
        <th>Copy notes</th>
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
          <td class="labels">
            {#each p.labels as l}<span class="tag-type" style:color={color.get(l)} style:border-color={color.get(l)}>{l}</span>{/each}
          </td>
          <td>
            <select bind:value={picks[p.key].confidence}>
              <option value="">–</option>
              {#each CONFIDENCE as c}<option value={c}>{c}</option>{/each}
            </select>
          </td>
          <td><input class="slot" type="text" bind:value={picks[p.key].slot} placeholder="slot…" /></td>
          <td>
            {#if p.notes.length}<button type="button" class="pill-toggle" title={notesText(p)} onclick={() => copyNotes(p)}>{copied === `${p.key}:notes` ? 'Copied ✓' : 'Copy'}</button>{:else}<span class="dim">no tooltip</span>{/if}
          </td>
          <td><button type="button" class="pill-toggle" onclick={() => copyHtml(p)}>{copied === `${p.key}:html` ? 'Copied ✓' : 'Copy HTML'}</button></td>
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
  .labels { min-width: 110px; }
  .labels .tag-type { display: inline-block; margin: 0 4px 4px 0; background: none; border: 1px solid; white-space: nowrap; }
  select, .slot { font: inherit; font-size: 12px; background: var(--bg); color: var(--text); border: 1px solid var(--border); border-radius: 4px; padding: 2px 4px; }
  .slot { width: 80px; }
</style>
