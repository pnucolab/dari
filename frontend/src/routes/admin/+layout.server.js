import { get } from '$lib/fetch';
import { loadTranslations } from '$lib/translations';
import { redirect, error } from '@sveltejs/kit';

/** @type {import('./$types').LayoutServerLoad} */
export async function load({ parent }) {
    const data = await parent();
    if (!data.user.is_staff) {
        throw error(404, 'Not Found');
    }
    return data;
}
