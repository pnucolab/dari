import { writable } from 'svelte/store';

export let store = {};
export const drawerHidden = writable(false);