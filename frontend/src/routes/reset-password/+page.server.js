import { post } from '$lib/fetch';
import { fail } from '@sveltejs/kit';

/** @type {import('./$types').PageServerLoad} */
export async function load({ url }) {
    const uid = url.searchParams.get('uid');
    const token = url.searchParams.get('token');
    return { uid, token };
}

/** @type {import('./$types').Actions} */
export const actions = {
	default: async ({ request, cookies }) => {
		const formData = await request.formData();
		const response = await post('reset-password', formData, cookies);

		if (!response.ok) {
			return fail(response.status || 500, { error: true });
		}

		return { success: true };
	}
};
