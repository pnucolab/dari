import { get, post } from '$lib/fetch';
import { fail } from '@sveltejs/kit';

export async function load() {
    const res = await get('allowed-email-domains');
    return { allowed_email_domains: res.data?.allowed_email_domains || '' };
}

/** @type {import('./$types').Actions} */
export const actions = {
	register: async ({ request }) => {
        let formdata = await request.formData();
        const username = formdata.get('username');
        const name = formdata.get('name');
        const email = formdata.get('email');
        const password = formdata.get('password');
        const password_confirm = formdata.get('password_confirm');

        // Validate passwords match
        if (password !== password_confirm) {
            return fail(400, { error: 'Passwords do not match' });
        }

        // Validate username format
        if (!/^[a-z][a-z0-9]{0,30}$/.test(username)) {
            return fail(400, { error: 'Invalid username format. Must start with a letter, contain only lowercase letters and numbers, and be 1-31 characters long.' });
        }

        if (username.startsWith('guest')) {
            return fail(400, { error: 'Username cannot start with "guest"' });
        }

        const response = await post('register', formdata);

		if (!response.ok || response.status !== 200) {
            let errorMsg = 'Registration failed';
            if (response.data?.error) {
                if (response.data.error === 'User already exists') {
                    errorMsg = 'Username already exists';
                } else if (response.data.error === 'Linux username already exists') {
                    errorMsg = 'Linux username already exists';
                } else {
                    errorMsg = response.data.error;
                }
            }
            return fail(response.status || 400, { error: errorMsg });
		}

        return { success: true };
	}
};
