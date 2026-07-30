import { defineConfig } from 'vite';
import tailwindcss from '@tailwindcss/vite';
import yaml from '@rollup/plugin-yaml';

export default defineConfig({
  base: './',
  plugins: [
    yaml(),
    tailwindcss()
  ],
  server: {
    host: '0.0.0.0',
    port: 3000,
    allowedHosts: 'all'
  }
});
