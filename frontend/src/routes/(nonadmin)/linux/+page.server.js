import { get } from '$lib/fetch';

/** @type {import('./$types').PageServerLoad} */
export async function load({ cookies }) {
	let servers = [];
	const response = await get('myservers', cookies);
	if (response.ok && response.status === 200) {
		servers = response.data;
	}

	return {
		servers
	};
}
