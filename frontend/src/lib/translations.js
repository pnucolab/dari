import { defineI18n } from 'sveltekit-i18n/kit';

/** @type {import('sveltekit-i18n').Config} */
export const config = ({
  initLocale: 'ko',
  loaders: [
    {
      locale: 'ko',
      namespace: 'user',
      loader: async () => (
        await import('./locales/user/ko.json')
      ).default,
    },
    {
      locale: 'en',
      namespace: 'user',
      loader: async () => (
        await import('./locales/user/en.json')
      ).default,
    },
    {
      locale: 'ko',
      namespace: 'login',
      routes: ['/login'],
      loader: async () => (
        await import('./locales/login/ko.json')
      ).default,
    },
    {
      locale: 'en',
      namespace: 'login',
      routes: ['/login'],
      loader: async () => (
        await import('./locales/login/en.json')
      ).default,
    },
    {
      locale: 'ko',
      namespace: 'register',
      routes: ['/register', '/verify-email'],
      loader: async () => (
        await import('./locales/register/ko.json')
      ).default,
    },
    {
      locale: 'en',
      namespace: 'register',
      routes: ['/register', '/verify-email'],
      loader: async () => (
        await import('./locales/register/en.json')
      ).default,
    },
    {
      locale: 'ko',
      namespace: 'forgot-password',
      routes: ['/forgot-password'],
      loader: async () => (
        await import('./locales/forgot-password/ko.json')
      ).default,
    },
    {
      locale: 'en',
      namespace: 'forgot-password',
      routes: ['/forgot-password'],
      loader: async () => (
        await import('./locales/forgot-password/en.json')
      ).default,
    },
    {
      locale: 'ko',
      namespace: 'reset-password',
      routes: ['/reset-password'],
      loader: async () => (
        await import('./locales/reset-password/ko.json')
      ).default,
    },
    {
      locale: 'en',
      namespace: 'reset-password',
      routes: ['/reset-password'],
      loader: async () => (
        await import('./locales/reset-password/en.json')
      ).default,
    },
    {
      locale: 'ko',
      namespace: 'admin',
      routes: [/^\/admin(\/|$)/],
      loader: async () => (
        await import('./locales/admin/ko.json')
      ).default,
    },
    {
      locale: 'en',
      namespace: 'admin',
      routes: [/^\/admin(\/|$)/],
      loader: async () => (
        await import('./locales/admin/en.json')
      ).default,
    },
    {
      locale: 'ko',
      namespace: 'init',
      routes: ['/init'],
      loader: async () => (
        await import('./locales/init/ko.json')
      ).default,
    },
    {
      locale: 'en',
      namespace: 'init',
      routes: ['/init'],
      loader: async () => (
        await import('./locales/init/en.json')
      ).default,
    },
    {
      locale: 'ko',
      namespace: 'common',
      loader: async () => (
        await import('./locales/common/ko.json')
      ).default,
    },
    {
      locale: 'en',
      namespace: 'common',
      loader: async () => (
        await import('./locales/common/en.json')
      ).default,
    },
  ]
});

export const { handle, load, use, get } = defineI18n(config, {
  // the `lang` cookie set by the language menu, Korean by default
  preferredLocale: (event) => event.cookies ? (event.cookies.get('lang') || 'ko').toLowerCase() : undefined,
});