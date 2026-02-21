import { post, get } from '$lib/fetch';
import { fail } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';

/** @type {import('./$types').PageServerLoad} */
export async function load({ url, cookies }) {
	const protocol = url.protocol;
	const host = url.host;
	const profileUrl = `${protocol}//${host}/api/vpn/profile`;

	let servers = [];
	const response = await get('myservers', cookies);
	if (response.ok && response.status === 200) {
		servers = response.data;
	}

	return {
		profileUrl,
		servers
	};
}

/** @type {import('./$types').Actions} */
export const actions = {
	vpn: async ({ cookies }) => {
		const response = await post('qr', {}, cookies);

		if (!response.ok || response.status !== 200) {
			return fail(422, { error: true });
		}

		return {
			qr: response.data.qr
		};
	}
};