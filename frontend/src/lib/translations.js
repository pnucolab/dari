import i18n from 'sveltekit-i18n';

/** @type {import('sveltekit-i18n').Config} */
const config = ({
  loaders: [
    {
      locale: 'ko',
      key: 'user',
      loader: async () => (
        await import('./locales/user/ko.json')
      ).default,
    },
    {
      locale: 'en',
      key: 'user',
      loader: async () => (
        await import('./locales/user/en.json')
      ).default,
    },
    {
      locale: 'ko',
      key: 'login',
      routes: ['/login'],
      loader: async () => (
        await import('./locales/login/ko.json')
      ).default,
    },
    {
      locale: 'en',
      key: 'login',
      routes: ['/login'],
      loader: async () => (
        await import('./locales/login/en.json')
      ).default,
    },
    {
      locale: 'ko',
      key: 'register',
      routes: ['/register', '/verify-email'],
      loader: async () => (
        await import('./locales/register/ko.json')
      ).default,
    },
    {
      locale: 'en',
      key: 'register',
      routes: ['/register', '/verify-email'],
      loader: async () => (
        await import('./locales/register/en.json')
      ).default,
    },
    {
      locale: 'ko',
      key: 'common',
      loader: async () => (
        await import('./locales/common/ko.json')
      ).default,
    },
    {
      locale: 'en',
      key: 'common',
      loader: async () => (
        await import('./locales/common/en.json')
      ).default,
    },
  ]
});

export const { t, locale, locales, loading, loadTranslations, addTranslations, setLocale, setRoute } = new i18n(config);