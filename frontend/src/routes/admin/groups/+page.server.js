import { redirect } from '@sveltejs/kit';

import { get, post, put, del } from '$lib/fetch';
import { fail } from '@sveltejs/kit';

export async function load({ parent, cookies }) {
    const data = await parent();
    const user = data.user;
    if (!user.is_staff) redirect(302, '/');

    const response = await get('groups', cookies);
    if (!response.ok || response.status !== 200) {
        return {
            error: response.status
        };
    }

    const response2 = await get('groupadmins', cookies);
    if (!response2.ok || response2.status !== 200) {
        return {
            error: response2.status
        };
    }

    return {
        groups: response.data,
        admins: response2.data
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
    },
    groupdel: async ({ request, cookies }) => {
        const queryString = new URLSearchParams(await request.formData()).toString();
        const response = await del(`group?${queryString}`, cookies);

        if (!response.ok || response.status !== 200) {
            return fail(response.status);
        }
        return;
    },
    groupadd: async ({ request, cookies }) => {
        const queryString = new URLSearchParams(await request.formData()).toString();
        const response = await post(`group?${queryString}`, {}, cookies);

        if (!response.ok || response.status !== 200) {
            return fail(response.status);
        }
        return;
    },
    adminpost: async ({ request, cookies }) => {
        const queryString = new URLSearchParams(await request.formData()).toString();
        const response = await post(`groupadmin?${queryString}`, {}, cookies);

        if (!response.ok || response.status !== 200) {
            return fail(response.status);
        }
    },
    admindel: async ({ request, cookies }) => {
        const queryString = new URLSearchParams(await request.formData()).toString();
        const response = await del(`groupadmin?${queryString}`, cookies);

        if (!response.ok || response.status !== 200) {
            return fail(response.status);
        }
    }
};