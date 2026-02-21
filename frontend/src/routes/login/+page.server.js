import { get } from '$lib/fetch';
import { redirect } from '@sveltejs/kit';
import { fail } from '@sveltejs/kit';
import { post } from '$lib/fetch';

/** @type {import('./$types').PageServerLoad} */
export async function load({ cookies }) {
    const response_me = await get('me', cookies);

    if (response_me.ok && response_me.status === 200) {
        return redirect(303, '/');
    }

    const response_csrftoken = await get('csrftoken');
    if (!response_csrftoken.ok || response_csrftoken.status !== 200) {
        throw fail(500);
    }

    cookies.set('csrftoken', response_csrftoken.data.csrftoken, {
        path: '/',
        httpOnly: true,
        sameSite: 'lax',
        secure: process.env.NODE_ENV === 'production',
        maxAge: 60 * 60 * 24 * 365
    });

    return;
}

/** @type {import('./$types').Actions} */
export const actions = {
	login: async ({ cookies, request }) => {
        let formdata = await request.formData()
        const response = await post('login', formdata, cookies);

		if (!response.ok || response.status !== 200) {
            const errorCode = response.data?.error || true;
            return fail(response.status || 422, { error: errorCode });
		}

        cookies.set('sessionid', response.data.sessionid, {
            path: '/',
            httpOnly: true,
            sameSite: 'lax',
            secure: process.env.NODE_ENV === 'production',
            maxAge: 60 * 60 * 24 * 14
        });
	}
};