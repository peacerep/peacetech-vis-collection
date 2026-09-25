<script>
  import { vocab } from '../lib/data.js';
  import Val from './Val.svelte';

  const KEYS = ['dimensions', 'audiences', 'contributor_roles', 'visualisation_types', 'structure_kinds', 'structure_qualities', 'edge_types', 'edge_names', 'link_types', 'status'];
</script>

{#each KEYS as key}
  <p>
    <strong>{key.replaceAll('_', ' ')}:</strong>
    <Val value={(vocab[key] ?? []).map((i) => i.label)} />
  </p>
{/each}
