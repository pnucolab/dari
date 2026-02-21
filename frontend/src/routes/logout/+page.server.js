import { get } from '$lib/fetch';
import { redirect } from '@sveltejs/kit';
import { fail } from '@sveltejs/kit';

/** @type {import('./$types').PageServerLoad} */
export async function load({ cookies }) {
    const response_me = await get('logout', cookies);

    if (!response_me.ok || response_me.status !== 200) {
        return fail(response_me.status);
    }

    cookies.delete('sessionid', {
        path: '/',
        httpOnly: true,
        sameSite: 'lax',
        secure: process.env.NODE_ENV === 'production'
    });

    return redirect(301, '/login');
}