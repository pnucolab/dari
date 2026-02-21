import adapter from '@sveltejs/adapter-node';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';
import { mdsvex } from 'mdsvex';

export default {
	preprocess: [
		vitePreprocess(),
		mdsvex({ extensions: ['.svx', '.md'] }),
	],
	extensions: ['.svelte', '.svx', '.md'],
	kit: {
		adapter: adapter(),
	}
};