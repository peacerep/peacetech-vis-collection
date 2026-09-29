import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

// Thumbnails are small WebP copies of ../mini-fig, generated into .thumbs by
// scripts/thumbs.js (runs before dev/build). Metadata JSON is imported from
// ../metadata — edits reload the dev page.
export default defineConfig({
  plugins: [svelte()],
  publicDir: '.thumbs',
  server: { fs: { allow: ['..'] } },
});
