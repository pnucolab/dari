import { post } from '#lib/fetch.js';
import { fail } from '@sveltejs/kit';

/** @type {import('./$types').Actions} */
export const actions = {
	password: async ({ cookies, request }) => {
		const formdata = await request.formData();
		const old_password = formdata.get('old_password');
		const new_password = formdata.get('new_password');
		const new_password_confirm = formdata.get('new_password_confirm');

		// Validate passwords match
		if (new_password !== new_password_confirm) {
			return fail(400, {
				password_error: 'user.password_error_mismatch',
				password_error_i18n: true
			});
		}

		// Validate password length
		if (new_password.length < 8) {
			return fail(400, {
				password_error: 'user.password_error_length',
				password_error_i18n: true
			});
		}

		const queryString = new URLSearchParams({
			old_password,
			new_password
		}).toString();

		const response = await post(`password?${queryString}`, {}, cookies);

		if (!response.ok || response.status !== 200) {
			// keys of the `user` namespace, except for errors passed through from the backend
			let errorMsg = 'user.password_error_failed';
			let errorI18n = true;
			if (response.status === 401) {
				errorMsg = 'user.password_error_old';
			} else if (response.data?.error) {
				errorMsg = response.data.error;
				errorI18n = false;
			}
			return fail(response.status || 400, {
				password_error: errorMsg,
				password_error_i18n: errorI18n
			});
		}

		return { password_success: true };
	}
};