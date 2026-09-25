<script>
  // Structure kind on the first line, qualities (single-/multi-view, template) on the second.
  import { structureLabels } from '../lib/data.js';
  import Val from './Val.svelte';

  let { v } = $props();
  const s = $derived(structureLabels(v));
</script>

<div><Val value={s.kind} /></div>
{#if s.qualities}<div class="dim">{s.qualities}</div>{/if}
