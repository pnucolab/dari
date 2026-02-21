import { redirect } from '@sveltejs/kit';

import { get, post, put, del } from '$lib/fetch';
import { fail } from '@sveltejs/kit';

export async function load({ parent, cookies }) {
    const data = await parent();
    const user = data.user;
    if (!user.profile.is_groupadmin) redirect(302, '/');

    const response = await get('groups', cookies);
    if (!response.ok || response.status !== 200) {
        return {
            error: response.status
        };
    }

    return {
        groups: response.data
    };
}

export const actions = {
    groupmod: async ({ request, cookies }) => {
        const queryString = new URLSearchParams(await request.formData()).toString();
        const response = await put(`group?${queryString}`, {}, cookies);
        if (!response.ok || response.status !== 200) {
            return fail(response.status);
        }
        return;
    }
};