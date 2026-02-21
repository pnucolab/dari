import { redirect } from '@sveltejs/kit';
import { post, get, patch, del } from '$lib/fetch';
import { fail } from '@sveltejs/kit';

export async function load({ parent, cookies }) {
    const data = await parent();
    const user = data.user;
    if (!user.is_staff) redirect(302, '/');

    const response_1 = await get('users', cookies);
    if (!response_1.ok || response_1.status !== 200)
        return { error: response_1.status };

    const response_2 = await get('guests', cookies);
    if (!response_2.ok || response_2.status !== 200)
        return { error: response_2.status };

    const response_3 = await get('deactivated', cookies);
    if (!response_3.ok || response_3.status !== 200)
        return { error: response_3.status };

    return {
        users: response_1.data,
        guests: response_2.data,
        deactivated: response_3.data,
    };
}

export const actions = {
    user: async ({ request, cookies }) => {
        const queryString = new URLSearchParams(await request.formData()).toString();
        const response = await patch(`user?${queryString}`, {}, cookies); // update

        if (!response.ok || response.status !== 200) {
            return fail(response.status);
        }

        return;
    },
    guest: async ({ request, cookies }) => {
        const queryString = new URLSearchParams(await request.formData()).toString();
        const response = await patch(`user?${queryString}`, {}, cookies); // create or update

        if (!response.ok || response.status !== 200) {
            return fail(response.status);
        }

        return;
    },
    guestnew: async ({ request, cookies }) => {
        const queryString = new URLSearchParams(await request.formData()).toString();
        const response = await post(`guest?${queryString}`, {}, cookies); // create or update

        if (!response.ok || response.status !== 200) {
            return fail(response.status);
        }

        return;
    },
    ldap: async ({ request, cookies }) => {
        const response = await get("ldap", cookies);

        if (!response.ok || response.status !== 200) {
            return fail(response.status);
        }

        return;
    },
    deactivate: async ({ request, cookies }) => {
        const formData = await request.formData();
        formData.append("is_active", "false");
        const queryString = new URLSearchParams(formData).toString();
        const response = await patch(`user?${queryString}`, {}, cookies); // update

        if (!response.ok || response.status !== 200) {
            return fail(response.status);
        }

        return;
    },
    activate: async ({ request, cookies }) => {
        const formData = await request.formData();
        formData.append("is_active", "true");
        const queryString = new URLSearchParams(formData).toString();
        const response = await patch(`user?${queryString}`, {}, cookies);

        if (!response.ok || response.status !== 200) {
            return fail(response.status);
        }

        return;
    },
    delete: async ({ request, cookies }) => {
        const queryString = new URLSearchParams(await request.formData()).toString();
        const response = await del(`user?${queryString}`, {}, cookies);

        if (!response.ok || response.status !== 200) {
            return fail(response.status);
        }

        return;
    },
    transfer: async ({ request, cookies }) => {
        const queryString = new URLSearchParams(await request.formData()).toString();
        const response = await post(`transfer?${queryString}`, {}, cookies);

        if (!response.ok || response.status !== 200) {
            return fail(response.status);
        }

        return;
    }
};