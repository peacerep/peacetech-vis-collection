<script>
  // Generic dense table: the caller supplies headers and a `row` snippet
  // that renders one record's <td>s.
  let { headers, rows, row, flagged = () => false } = $props();
</script>

<div class="table-wrap">
  <table>
    <thead>
      <tr>{#each headers as h}<th>{h}</th>{/each}</tr>
    </thead>
    <tbody>
      {#each rows as r}
        <tr class:row-flagged={flagged(r)}>{@render row(r)}</tr>
      {:else}
        <tr><td colspan={headers.length} class="empty">none</td></tr>
      {/each}
    </tbody>
  </table>
</div>
