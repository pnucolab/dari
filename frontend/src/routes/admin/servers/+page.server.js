import { redirect } from '@sveltejs/kit';

import { post, get, del } from '$lib/fetch';
import { fail } from '@sveltejs/kit';

export async function load({ parent, cookies }) {
	const data = await parent();
    const user = data.user;
    if (!user.is_staff) redirect(302, '/');
}

export const actions = {
	groups: async ({ cookies }) => {
		const response = await get('groups', cookies);

		if (!response.ok || response.status !== 200) {
			return fail(response.status);
		}

		return {
			servers: JSON.stringify(response.data),
		};
	},
	servers: async ({ cookies }) => {
		const response = await get('servers', cookies);

		if (!response.ok || response.status !== 200) {
			return fail(response.status);
		}

		return {
			servers: JSON.stringify(response.data),
		};
	},
	stats: async ({ cookies }) => {
		const response = await get('servers/stats', cookies);

		if (!response.ok || response.status !== 200) {
			return fail(response.status);
		}

		return {
			servers: JSON.stringify(response.data),
		};
	},
	server: async ({ request, cookies }) => {
		const queryString = new URLSearchParams(await request.formData()).toString();
		const response = await post(`server?${queryString}`, {}, cookies);

		if (!response.ok || response.status !== 200) {
			return fail(response.status);
		}

		return;
	},
	serverdelete: async ({ request, cookies }) => {
		const queryString = new URLSearchParams(await request.formData()).toString();
		const response = await del(`server?${queryString}`, cookies);

		if (!response.ok || response.status !== 200) {
			return fail(response.status);
		}

		return;
	},
};