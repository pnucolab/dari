import { redirect } from '@sveltejs/kit';
import { get, post } from '#lib/fetch.js';
import { fail } from '@sveltejs/kit';

export async function load({ parent, cookies }) {
    const data = await parent();
    const user = data.user;
    if (!user.is_staff) redirect(302, '/');

    // current SMTP settings for the "SMTP settings" modal (the password is never returned)
    const response = await get('smtp', cookies);
    const smtp = response.ok && response.status === 200 ? response.data : null;

    return {
        smtp,
        adminEmail: user.email || '',
    };
}

const SMTP_FIELDS = ['smtp_host', 'smtp_port', 'smtp_user', 'smtp_security', 'smtp_from', 'smtp_subject_prefix'];

/**
 * Collects the SMTP fields of the modal's form as the JSON body the backend expects.
 * An empty password keeps the saved one.
 * @param {FormData} formData
 */
function smtpBody(formData) {
    const body = new Map();
    for (const key of SMTP_FIELDS) {
        body.set(key, String(formData.get(key) ?? '').trim());
    }
    const password = String(formData.get('smtp_password') ?? '');
    if (password) {
        body.set('smtp_password', password);
    }
    return body;
}

export const actions = {
    email: async ({ request, cookies }) => {
        const queryString = new URLSearchParams(await request.formData()).toString();
        const response = await post(`emailsend?${queryString}`, {}, cookies);

        if (!response.ok || response.status !== 200) {
            return fail(response.status);
        }

        return;
    },

    // save the SMTP settings
    smtp: async ({ request, cookies }) => {
        const formData = await request.formData();
        const body = smtpBody(formData);
        if (formData.get('smtp_password_clear')) {
            body.delete('smtp_password');
            body.set('smtp_password_clear', true);
        }

        const response = await post('smtp', body, cookies);
        if (!response.ok || response.status !== 200) {
            // reported inside the modal (a plain result, so the browser logs no failed request)
            return { smtp: { action: 'save', error: response.data?.error || 'unknown' } };
        }
        return { smtp: { action: 'save', success: true } };
    },

    // send a test email with the (possibly unsaved) values of the form
    smtptest: async ({ request, cookies }) => {
        const formData = await request.formData();
        const body = smtpBody(formData);
        const to = String(formData.get('to') ?? '').trim();
        if (to) {
            body.set('to', to);
        }

        const response = await post('smtp/test', body, cookies);
        if (!response.ok || response.status !== 200) {
            return {
                smtp: {
                    action: 'test',
                    error: response.data?.error || 'unknown',
                    detail: response.data?.detail || response.error || '',
                },
            };
        }
        return { smtp: { action: 'test', success: true, to: response.data?.to || to } };
    },
};
