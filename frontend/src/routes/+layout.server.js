import { get } from '$lib/fetch';
import { loadTranslations } from '$lib/translations';
import { redirect, error } from '@sveltejs/kit';
import { fail } from '@sveltejs/kit';

/** @type {import('./$types').LayoutServerLoad} */
export async function load({ url, cookies }) {
    let rtn = {};

    const { pathname } = url;

    let locale = (cookies.get('lang') || 'ko').toLowerCase();
    await loadTranslations(locale, pathname);

    rtn.i18n = { locale, route: pathname };

    const response_brand = await get('brand', cookies);
    let brand = { sitename: null, logo: null };
    if (response_brand.ok && response_brand.status === 200) {
        brand = response_brand.data;
    }
    rtn.brand = brand;

    // Allow access to init, login, register, and privacy pages without authentication
    if (url.pathname === '/init' || url.pathname === '/login' || url.pathname === '/register' || url.pathname === '/verify-email' || url.pathname === '/privacy' || url.pathname === '/forgot-password' || url.pathname === '/reset-password') {
        // For init page, redirect to it if no users exist yet
        if (url.pathname !== '/init') {
            const response_me = await get('me', cookies);
            if (!response_me.ok || response_me.status === 401) {
                // Check if this is a fresh system (no users)
                // If brand.sitename is null and no user is logged in, redirect to init
                if (!rtn.brand.sitename) {
                    return redirect(303, '/init');
                }
            }
        }
        return rtn;
    }

    const response_me = await get('me', cookies);

    if (!response_me.ok || response_me.status !== 200) {
        // No user logged in - check if system needs initialization
        if (!rtn.brand.sitename) {
            return redirect(303, '/init');
        }
        return redirect(303, '/login');
    }

    let user = response_me.data;
    rtn.user = user;

    if (!rtn.brand.sitename) {
        if (user.is_staff && url.pathname !== '/init')
            return redirect(303, '/init');
        else if (!user.is_staff)
            return fail(500);
    }

    return rtn;
}
