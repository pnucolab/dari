import { get, post } from '#lib/fetch.js';
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
            return fail(400, { error: 'register.error_password_mismatch', error_i18n: true });
        }

        // Validate username format
        if (!/^[a-z][a-z0-9]{0,30}$/.test(username)) {
            return fail(400, { error: 'register.error_username_format', error_i18n: true });
        }

        if (username.startsWith('guest')) {
            return fail(400, { error: 'register.error_username_guest', error_i18n: true });
        }

        const response = await post('register', formdata);

		if (!response.ok || response.status !== 200) {
            // keys of the `register` namespace, except for errors passed through from the backend
            let errorMsg = 'register.error_failed';
            let errorI18n = true;
            if (response.data?.error) {
                if (response.data.error === 'User already exists') {
                    errorMsg = 'register.error_user_exists';
                } else if (response.data.error === 'Linux username already exists') {
                    errorMsg = 'register.error_linux_exists';
                } else {
                    errorMsg = response.data.error;
                    errorI18n = false;
                }
            }
            return fail(response.status || 400, { error: errorMsg, error_i18n: errorI18n });
		}

        return { success: true };
	}
};
