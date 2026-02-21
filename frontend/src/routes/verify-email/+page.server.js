import { get } from '$lib/fetch';

/** @type {import('./$types').PageServerLoad} */
export async function load({ url }) {
    const key = url.searchParams.get('key');
    if (!key) {
        return { verified: false };
    }

    const response = await get(`verify-email?key=${key}`);
    return { verified: response.ok };
}
