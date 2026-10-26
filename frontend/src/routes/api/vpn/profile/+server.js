import { API_BASE_URL } from '$app/env/private';

/** @type {import('./$types').RequestHandler} */
export async function GET() {
	const url = new URL('vpn/profile', API_BASE_URL);

	try {
		const response = await fetch(url);

		if (!response.ok) {
			return new Response('VPN profile not available', { status: response.status });
		}

		const content = await response.arrayBuffer();

		return new Response(content, {
			status: 200,
			headers: {
				'Content-Type': 'application/x-openvpn-profile',
				'Content-Disposition': 'attachment; filename="client.ovpn"'
			}
		});
	} catch (error) {
		console.error('Error proxying VPN profile:', error);
		return new Response('Internal server error', { status: 500 });
	}
}
