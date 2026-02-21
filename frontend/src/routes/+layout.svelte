<script>
    import "../app.css";

    import { t, locale, locales } from '$lib/translations';
    import {
        Navbar,
        NavBrand,
        Dropdown,
        DropdownItem,
        Avatar,
        NavHamburger,
    } from 'flowbite-svelte';
    import {
        LanguageOutline,
    } from 'flowbite-svelte-icons';
    import { drawerHidden } from '$lib/store';

    /** @type {import('./$types').LayoutData} */
    export let data;

    let user = null;
    $: user = data.user;

    const handleChange = (lang) => {
        locale.set(lang);
        document.cookie = `lang=${lang}; path=/`;
        langDropdownOpen = false;
    };

    let langDropdownOpen = false;
    $: brand = data.brand;
</script>

<svelte:head>
    {#if brand && brand.sitename}
        <title>{brand.sitename} IT Service Portal</title> 
    {/if}
</svelte:head>

{#if brand && brand.sitename}
    <Navbar class="px-2 sm:px-4 py-2.5 sticky w-full z-10 border-b border-slate-300" fluid={true}>
        <div class="fixed top-0 start-0 end-0 h-2" style="background: linear-gradient(90deg, rgba(0,182,0,1) 0%, rgba(0,182,0,1) 66.3%, rgba(0,71,180,1) 66.3%, rgba(0,71,180,1) 100%);"></div>
        <NavHamburger onClick={() => drawerHidden.set(false)} />
        <NavBrand href="/" class="mt-2">
            <div class="flex items-center gap-3 ps-1">
                {#if brand.logo}
                <img src="{brand.logo}" alt="{brand.sitename} IT Service Portal" class="w-10 h-10" />
                {/if}
                <div class="self-center whitespace-nowrap font-semibold dark:text-white pt-2"><span class="absolute text-xs top-5">{brand.sitename}</span>IT Service Portal</div>
            </div>
        </NavBrand>
        <div class="flex items-center gap-4 pe-3 mt-2">
            <LanguageOutline class="w-7 h-7 text-gray-500 lang-menu cursor-pointer focus:outline-none" />
            <Dropdown bind:open={langDropdownOpen} triggeredby=".lang-menu">
                {#each $locales as value}
                <DropdownItem active on:click={() => handleChange(value)}>{$t(`common.${value}`)}</DropdownItem>
                {/each}
            </Dropdown>
            {#if user}
            <Avatar class="cursor-pointer" size="sm" border />
            <Dropdown>
                <DropdownItem href="/profile/">
                    <span class="ms-2">{$t('common.profile')}</span>
                </DropdownItem>
                <DropdownItem href="/logout/">
                    <span class="ms-2">{$t('common.logout')}</span>
                </DropdownItem>
            </Dropdown>
            {/if}
        </div>
    </Navbar>

    <div class="lg:flex w-full">
        <slot></slot>
        <footer class="fixed bottom-0 start-0 w-full bg-white border-t border-slate-300">
            <div class="flex justify-between items-center h-14 px-10">
                <span class="text-xs md:text-sm text-gray-500 dark:text-gray-400">© 2026 Level4. All rights reserved.</span>
                <span class="text-xs md:text-sm text-gray-500 dark:text-gray-400"><a href="/privacy">{$t('common.privacy')}</a></span>
            </div>
        </footer>
    </div>
{:else}
    <slot></slot>
{/if}

<style>
@import url('https://fonts.googleapis.com/css2?family=Noto%20Sans%20KR&display=swap');

:global(body) {
    font-family: 'Noto Sans KR', sans-serif;
    font-size: 1.125rem;
    line-height: 1.75rem;
    color: #374151;
}
:global(main a) {
    color: rgb(37 99 235);
}
:global(main a:hover) {
    text-decoration-line: underline;
}
:global(main h1) {
    margin-bottom: 1rem;
    font-size: 1.5rem;
    font-weight: bold;
    letter-spacing: -0.025em;
    color: #111827;
}

:global(main h2) {
    margin-bottom: 0.75rem;
    font-size: 1.25rem;
    font-weight: bold;
    letter-spacing: -0.025em;
    color: #111827;
}

:global(main ul) {
    list-style: disc;
    margin-left: 2rem;
    margin-bottom: 1.5rem;
    list-style-position: outside;
}

:global(main li) {
    margin-bottom: 0.2rem;
    color: #374151;
}

:global(main p) {
    margin-bottom: 1.5rem;
    color: #374151;
}

:global(section) {
    margin-bottom: 2rem;
}

:global(pre) {
    background-color: #f4f4f4;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 1em;
    overflow-x: auto;
    font-family: 'Courier New', Courier, monospace;
    font-size: 14px;
    line-height: 1.5;
    margin: 1em 2em;
}

:global(code) {
    background-color: #f4f4f4;
    border-radius: 3px;
    font-family: 'Courier New', Courier, monospace;
    font-size: 0.9em;
    padding: 0.2em 0.4em;
}

:global(pre code) {
    background-color: transparent;
    border-radius: 0;
    padding: 0;
    font-size: 1em;
}
</style>

