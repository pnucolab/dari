import { post } from '$lib/fetch';
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
				password_error: 'New passwords do not match'
			});
		}

		// Validate password length
		if (new_password.length < 8) {
			return fail(400, {
				password_error: 'Password must be at least 8 characters long'
			});
		}

		const queryString = new URLSearchParams({
			old_password,
			new_password
		}).toString();

		const response = await post(`password?${queryString}`, {}, cookies);

		if (!response.ok || response.status !== 200) {
			let errorMsg = 'Failed to change password';
			if (response.status === 401) {
				errorMsg = 'Invalid old password';
			} else if (response.data?.error) {
				errorMsg = response.data.error;
			}
			return fail(response.status || 400, {
				password_error: errorMsg
			});
		}

		return { password_success: true };
	}
};