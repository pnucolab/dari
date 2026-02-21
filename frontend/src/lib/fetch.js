import { env } from '$env/dynamic/private';

const BASE_URL = env.API_BASE_URL || 'http://backend:8080/api/';

async function send({ method, path, data, cookies }) {
    const url = new URL(path, BASE_URL);

    let headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    if (cookies) {
        let cookie_strings = [];
        cookies.getAll().forEach(cookie => {
            cookie_strings.push(`${cookie.name}=${cookie.value}`);
            if (cookie.name === 'csrftoken') {
                headers['X-CSRFToken'] = cookie.value;
            }
        });
        headers['Cookie'] = cookie_strings.join('; ');
    }

    const options = {
        method,
        headers,
    };

    if (data && data.forEach) {
        var object = {};
        data.forEach((value, key) => object[key] = value);
        options.body = JSON.stringify(object);
    }

    try {
        const response = await fetch(url, options);
        const contentType = response.headers.get('content-type');
        
        let responseData;
        if (contentType && contentType.includes('application/json')) {
            responseData = await response.json();
        } else {
            responseData = await response.text();
        }

        return { ok: response.ok, status: response.status, data: responseData };
    } catch (error) {
        console.error('Fetch error:', error);
        return { ok: false, error: error.message };
    }
}

export function get(path, cookies) {
    return send({ method: 'GET', path, cookies });
}

export function del(path, cookies) {
    return send({ method: 'DELETE', path, cookies });
}

export function post(path, data, cookies) {
    return send({ method: 'POST', path, data, cookies });
}

export function put(path, data, cookies) {
    return send({ method: 'PUT', path, data, cookies });
}

export function patch(path, data, cookies) {
    return send({ method: 'PATCH', path, data, cookies });
}