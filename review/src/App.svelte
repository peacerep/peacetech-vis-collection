<script>
  import { people, orgs, datasets, tools, label, orgName, isUncertain } from './lib/data.js';
  import Val from './components/Val.svelte';
  import Visualisations from './components/Visualisations.svelte';
  import SimpleTable from './components/SimpleTable.svelte';
  import Vocab from './components/Vocab.svelte';
  import ArcDiagram from './components/ArcDiagram.svelte';
  // Vertical arc diagram hidden for now — re-enable with the tab and branch below.
  // import ArcDiagramVertical from './components/ArcDiagramVertical.svelte';

  const TABS = [
    { id: 'vis', label: 'Visualisations' },
    { id: 'rel', label: 'Relationships' },
    // { id: 'rel-v', label: 'Relationships (vertical)' },
    { id: 'people', label: 'People' },
    { id: 'orgs', label: 'Organisations' },
    { id: 'datasets', label: 'Datasets' },
    { id: 'tools', label: 'Tools' },
    { id: 'vocab', label: 'Vocabularies' },
  ];

  let tab = $state('vis');
</script>

<h1>PeaceRep Programe - Visualisation Collection</h1>
<p class="sub">
  This repository collect and organise visualisation projects created within PeaceRep program from 2019 to 2026.
</p>

<nav>
  {#each TABS as t}
    <button class:active={tab === t.id} onclick={() => (tab = t.id)}>{t.label}</button>
  {/each}
</nav>

{#if tab === 'vis'}
  <Visualisations />
{:else if tab === 'rel'}
  <ArcDiagram />
<!-- Vertical arc diagram hidden for now:
{:else if tab === 'rel-v'}
  <ArcDiagramVertical />
-->
{:else if tab === 'people'}
  <SimpleTable headers={['Name', 'ID', 'Given', 'Family', 'Affiliation', 'Roles', 'Partner', 'Notes']} rows={people}>
    {#snippet row(p)}
      <td><strong>{p.display_name}</strong></td>
      <td><code>{p.id}</code></td>
      <td><Val value={p.given_name} /></td>
      <td><Val value={p.family_name} /></td>
      <td><Val value={(p.affiliation_ids ?? []).map(orgName)} /></td>
      <td><Val value={(p.roles ?? []).map((r) => label.role.get(r) ?? r)} /></td>
      <td>{p.is_collaboration_partner ? 'yes' : 'no'}</td>
      <td><Val value={p.notes} /></td>
    {/snippet}
  </SimpleTable>
{:else if tab === 'orgs'}
  <SimpleTable headers={['Name', 'ID', 'Short', 'Type', 'URL', 'Country', 'Partner', 'Notes']} rows={orgs}>
    {#snippet row(o)}
      <td><strong>{#if o.name}{o.name}{:else}<span class="flag">unconfirmed</span>{/if}</strong></td>
      <td><code>{o.id}</code></td>
      <td><Val value={o.short_name} /></td>
      <td><Val value={o.type} /></td>
      <td><Val value={o.url} /></td>
      <td><Val value={o.country} /></td>
      <td>{o.is_collaboration_partner ? 'yes' : 'no'}</td>
      <td><Val value={o.notes} /></td>
    {/snippet}
  </SimpleTable>
{:else if tab === 'datasets'}
  <SimpleTable
    headers={['Name', 'ID', 'Short', 'Description', 'Publisher', 'Source URL', 'Licence', 'Citation', 'Versions', 'Fields', 'Notes']}
    rows={datasets}
    flagged={isUncertain}
  >
    {#snippet row(d)}
      <td><strong>{d.name}</strong></td>
      <td><code>{d.id}</code></td>
      <td><Val value={d.short_name} /></td>
      <td><Val value={d.description} /></td>
      <td><Val value={d.publisher_organisation_id} /></td>
      <td><Val value={d.source_url} /></td>
      <td><Val value={d.licence} /></td>
      <td><Val value={d.citation} /></td>
      <td>
        {#if d.versions.length}
          <ul class="tight">
            {#each d.versions as v}
              <li>
                <code>{v.label}</code>
                <span class="dim">release: <Val value={v.release_date} /> · accessed: <Val value={v.accessed_at} /> · <Val value={v.notes} /></span>
              </li>
            {/each}
          </ul>
        {:else}<Val />{/if}
      </td>
      <td>
        {#if d.fields.length}
          <ul class="tight">
            {#each d.fields as f}<li>{f.name} <span class="dim">(<Val value={f.data_type} />)</span></li>{/each}
          </ul>
        {:else}<Val />{/if}
      </td>
      <td><Val value={d.notes} /></td>
    {/snippet}
  </SimpleTable>
{:else if tab === 'tools'}
  {#if tools.length}
    <SimpleTable headers={['Name', 'ID', 'Type', 'Description', 'Website', 'Notes']} rows={tools}>
      {#snippet row(t)}
        <td><strong>{t.name}</strong></td>
        <td><code>{t.id}</code></td>
        <td><Val value={t.type} /></td>
        <td><Val value={t.description} /></td>
        <td><Val value={t.website} /></td>
        <td><Val value={t.notes} /></td>
      {/snippet}
    </SimpleTable>
  {:else}
    <p class="empty">tools.json not yet populated.</p>
  {/if}
{:else if tab === 'vocab'}
  <Vocab />
{/if}
