// Resize the full-size images in ../mini-fig into small WebP thumbnails in
// .thumbs/ (gitignored), which Vite serves as its public dir. Originals are
// untouched. Runs before `dev` and `build`; unchanged images are skipped.
import { readdir, mkdir, stat, rm } from 'node:fs/promises';
import { join, parse } from 'node:path';
import { fileURLToPath } from 'node:url';
import sharp from 'sharp';

const root = fileURLToPath(new URL('..', import.meta.url));
const SRC = join(root, '../mini-fig');
const OUT = join(root, '.thumbs');
const WIDTH = 480; // ≥2× the largest on-screen size (200px card image)
const IMAGE = /\.(png|jpe?g|webp|gif|tiff?)$/i;

const mtime = (p) => stat(p).then((s) => s.mtimeMs, () => 0);

await mkdir(OUT, { recursive: true });
const sources = (await readdir(SRC)).filter((f) => IMAGE.test(f));
const wanted = new Set(sources.map((f) => `${parse(f).name}.webp`));

let made = 0;
for (const f of sources) {
  const src = join(SRC, f);
  const out = join(OUT, `${parse(f).name}.webp`);
  if ((await mtime(out)) >= (await mtime(src))) continue;
  await sharp(src).resize({ width: WIDTH, withoutEnlargement: true }).webp({ quality: 80 }).toFile(out);
  made++;
}
// Drop thumbnails whose original was removed.
for (const f of await readdir(OUT)) if (!wanted.has(f)) await rm(join(OUT, f));

console.log(`thumbs: ${made} generated, ${sources.length - made} up to date → ${OUT}`);
