import { env } from '$env/dynamic/private';

/** @type {import('./$types').RequestHandler} */
export async function GET() {
	const BASE_URL = env.API_BASE_URL || 'http://backend:8080/api/';
	const url = new URL('vpn/profile', BASE_URL);

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
