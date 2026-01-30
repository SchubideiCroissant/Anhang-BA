import { defineConfig } from 'vite';
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  base: './', // Erzeugt relative Pfade für die EXE
  plugins: [tailwindcss(),],
  root: '.', // index.html Ort
  build: {
    outDir: 'dist'
  }
});
