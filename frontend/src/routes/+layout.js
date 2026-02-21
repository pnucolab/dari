import { setLocale, setRoute } from '$lib/translations';

/** @type {import('./$types').LayoutLoad} */
export async function load({ data }) {
    if (data && data.i18n) {
        const { locale, route } = data.i18n;

        await setRoute(route);
        await setLocale(locale);
    }
    return {...data};
}