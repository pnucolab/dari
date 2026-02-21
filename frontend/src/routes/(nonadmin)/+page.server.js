import { get } from '$lib/fetch';
import { fail } from '@sveltejs/kit';

export const actions = {
	logs: async ({ cookies }) => {
		const response = await get(`logs?all=true`, cookies);

		if (!response.ok || response.status !== 200) {
			return fail(response.status);
		}

		return {
			servers: JSON.stringify(response.data),
		};
	}
};