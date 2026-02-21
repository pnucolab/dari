import { get, post } from '$lib/fetch';

export async function load({ cookies }) {
    const response = await get('defaults', cookies);

    if (!response.ok || response.status !== 200) {
        return fail(422);
    }

    const data = {
        defaults: response.data
    };

    return data;
}

/** @type {import('./$types').Actions} */
export const actions = {
	defaults: async ({ cookies, request }) => {
        let formdata = await request.formData()

        if (formdata.get('logo')) {
            const logo = formdata.get('logo');
            if (logo.size > 0) {
                if (logo.type !== 'image/png' && logo.type !== 'image/jpeg' &&
                    logo.type !== 'image/gif' && logo.type !== 'image/svg+xml') {
                    return fail(422);
                }
                const arrayBuffer = await logo.arrayBuffer();
                const logoData = Buffer.from(arrayBuffer).toString('base64');
                formdata.set('logo', `data:${logo.type};base64,${logoData}`);
            } else {
                formdata.delete('logo');
            }
        }

        const response = await post('defaults', formdata, cookies);

		if (!response.ok || response.status !== 200) {
			return fail(422);
		}
	}
};