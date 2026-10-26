import { defineEnvVars } from '@sveltejs/kit/env';

export const variables = defineEnvVars({
	API_BASE_URL: {
		description: 'Base URL of the backend API',
		schema: (value) => value || 'http://backend:8080/api/',
	},
});
