<script>
  // A value, or a muted "—" when it's empty. Arrays are comma-joined.
  let { value } = $props();
  const text = $derived(Array.isArray(value) ? value.join(', ') : value);
</script>

{#if text === null || text === undefined || text === ''}<span class="dash">—</span>{:else}{text}{/if}
