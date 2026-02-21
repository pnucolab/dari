import { redirect } from '@sveltejs/kit';
import { post } from '$lib/fetch';
import { fail } from '@sveltejs/kit';

export async function load({ parent }) {
    const data = await parent();
    const user = data.user;
    if (!user.is_staff) redirect(302, '/');
    return {};
}

export const actions = {
    email: async ({ request, cookies }) => {
        const queryString = new URLSearchParams(await request.formData()).toString();
        const response = await post(`emailsend?${queryString}`, {}, cookies);

        if (!response.ok || response.status !== 200) {
            return fail(response.status);
        }

        return;
    }
};