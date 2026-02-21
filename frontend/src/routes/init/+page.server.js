import { post, get } from '$lib/fetch';
import { fail } from '@sveltejs/kit';
import { redirect } from '@sveltejs/kit';

export async function load({ cookies }) {
    // Get brand info to check if system is configured
    const response_brand = await get('brand', cookies);
    let brand = { sitename: null, logo: null };
    if (response_brand.ok && response_brand.status === 200) {
        brand = response_brand.data;
    }

    // If system is already configured, redirect away
    if (brand.sitename) {
        throw redirect(303, '/login');
    }

    // Check if user is logged in
    const response_me = await get('me', cookies);
    const hasUser = response_me.ok && response_me.status === 200;

    return {
        user: hasUser ? response_me.data : null,
        brand
    };
}

/** @type {import('./$types').Actions} */
export const actions = {
    setup: async ({ cookies, request }) => {
        const formdata = await request.formData();

        // Extract admin info
        const username = formdata.get('admin_username');
        const name = formdata.get('admin_name');
        const email = formdata.get('admin_email');
        const password = formdata.get('admin_password');

        // Handle logo
        let logo = '';
        if (formdata.get('logo')) {
            const logoFile = formdata.get('logo');
            if (logoFile.size > 0) {
                if (logoFile.type !== 'image/png' && logoFile.type !== 'image/jpeg' &&
                    logoFile.type !== 'image/gif' && logoFile.type !== 'image/svg+xml') {
                    return fail(422, { error: '로고 파일 형식이 올바르지 않습니다' });
                }
                const arrayBuffer = await logoFile.arrayBuffer();
                const logoData = Buffer.from(arrayBuffer).toString('base64');
                logo = `data:${logoFile.type};base64,${logoData}`;
            }
        }

        // Build init payload
        const payload = new FormData();
        payload.append('username', username);
        payload.append('name', name);
        payload.append('email', email);
        payload.append('password', password);
        payload.append('sitename', formdata.get('sitename') || '');
        payload.append('gid', formdata.get('gid') || '');
        payload.append('shell', formdata.get('shell') || '');
        payload.append('logo', logo);
        payload.append('allowed_email_domains', formdata.get('allowed_email_domains') || '');

        const init_response = await post('init', payload);
        if (!init_response.ok || init_response.status !== 200) {
            let errorMsg = '초기 설정에 실패했습니다';
            if (init_response.data?.error) {
                errorMsg = init_response.data.error;
            }
            return fail(init_response.status || 400, { error: errorMsg });
        }

        // Auto-login
        const response_csrftoken = await get('csrftoken');
        if (response_csrftoken.ok && response_csrftoken.status === 200) {
            cookies.set('csrftoken', response_csrftoken.data.csrftoken, {
                path: '/',
                httpOnly: true,
                sameSite: 'lax',
                secure: process.env.NODE_ENV === 'production',
                maxAge: 60 * 60 * 24 * 365
            });
        }

        const loginFormData = new FormData();
        loginFormData.append('id', username);
        loginFormData.append('pw', password);
        loginFormData.append('agree', 'true');

        const login_response = await post('login', loginFormData, cookies);
        if (login_response.ok && login_response.status === 200) {
            cookies.set('sessionid', login_response.data.sessionid, {
                path: '/',
                httpOnly: true,
                sameSite: 'lax',
                secure: process.env.NODE_ENV === 'production',
                maxAge: 60 * 60 * 24 * 14
            });
        }

        throw redirect(303, '/admin');
    }
};
