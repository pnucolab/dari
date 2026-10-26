import adapter from '@sveltejs/adapter-node';
import { sveltekit } from '@sveltejs/kit/vite';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';
import tailwindcss from '@tailwindcss/vite';
import { mdsvex } from 'mdsvex';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [
		tailwindcss(),
		sveltekit({
			preprocess: [
				vitePreprocess(),
				mdsvex({ extensions: ['.svx', '.md'] }),
			],
			extensions: ['.svelte', '.svx', '.md'],
			adapter: adapter(),
		})
	]
});
