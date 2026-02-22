import { redirect } from '@sveltejs/kit';

import { get } from '$lib/fetch';
import { fail } from '@sveltejs/kit';

export async function load({ parent, cookies }) {
	const data = await parent();
    const user = data.user;
    if (!user.is_staff) redirect(302, '/');
}

export const actions = {
	logs: async ({ request, cookies }) => {
		const formData = await request.formData();
		const page = formData.get('page') || 1;
		const per_page = formData.get('per_page') || 20;
		const response = await get(`logs?all=true&page=${page}&per_page=${per_page}`, cookies);

		if (!response.ok || response.status !== 200) {
			return fail(response.status);
		}

		return {
			servers: JSON.stringify(response.data),
		};
	}
};
