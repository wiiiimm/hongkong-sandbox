import { defineConfig } from 'tsup';

export default defineConfig((options) => ({
  entry: {
    index: 'src/index.ts', // server-safe: config + utils + middleware
    client: 'src/client.ts', // 'use client': provider + hooks
  },
  format: ['cjs', 'esm'],
  dts: true,
  splitting: false,
  sourcemap: true,
  clean: !options.watch,
  external: ['react', 'react-dom', 'next'],
  minify: process.env.NODE_ENV === 'production',
  // IMPORTANT: tree-shaking strips the "use client" directive from client.*,
  // which breaks the provider at runtime. Keep it off.
  treeshake: false,
}));
