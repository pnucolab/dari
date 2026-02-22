import { post } from '$lib/fetch';
import { fail } from '@sveltejs/kit';

/** @type {import('./$types').Actions} */
export const actions = {
	default: async ({ request, cookies }) => {
		const formData = await request.formData();
		const response = await post('forgot-password', formData, cookies);

		if (!response.ok) {
			return fail(response.status || 500, { error: true });
		}

		return { success: true };
	}
};
