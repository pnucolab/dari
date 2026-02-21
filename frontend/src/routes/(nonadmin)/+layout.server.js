import { get } from '$lib/fetch';
import { loadTranslations } from '$lib/translations';
import { redirect } from '@sveltejs/kit';

/** @type {import('./$types').LayoutServerLoad} */
export async function load({ url, cookies }) {
    const response_me = await get('me', cookies);

    if (!response_me.ok || response_me.status !== 200) {
        throw redirect(301, '/login/');
    }

    let user = response_me.data;

    const response_brand = await get('brand', cookies);
    
    let brand = { sitename: null, logo: null };
    if (response_brand.ok && response_brand.status === 200) {
        brand = response_brand.data;
    }

    const { pathname, search } = url;
    const route = `${pathname}${search}`;

    let locale = (cookies.get('lang') || 'ko').toLowerCase();
    await loadTranslations(locale, route);

    return {
        user: user,
        brand: brand,
        i18n: { locale, route },
    };
}
