import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

// Thumbnails are served straight from ../mini-fig, and metadata JSON is
// imported from ../metadata — edits to either reload the dev page.
export default defineConfig({
  plugins: [svelte()],
  publicDir: '../mini-fig',
  server: { fs: { allow: ['..'] } },
});
