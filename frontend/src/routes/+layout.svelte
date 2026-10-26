<script>
    import "../app.css";

    import { use } from '#lib/translations.js';
    import Dropdown from '#lib/components/ui/Dropdown.svelte';
    import DropdownItem from '#lib/components/ui/DropdownItem.svelte';
    import Icon from '#lib/components/ui/Icon.svelte';
    import { drawerHidden } from '#lib/store.js';

    /** @type {{ data: import('./$types').LayoutData, children: import('svelte').Snippet }} */
    let { data, children } = $props();

    const i18n = use(() => data);

    let user = $derived(data.user);

    const handleChange = (lang) => {
        i18n.setLocale(lang);
        document.cookie = `lang=${lang}; path=/`;
        langDropdownOpen = false;
    };

    let langDropdownOpen = $state(false);
    let brand = $derived(data.brand);
    let sitename = $derived(i18n.locale === 'en' && brand?.sitename_en ? brand.sitename_en : brand?.sitename);
</script>

<svelte:head>
    {#if brand && brand.sitename}
        <title>{sitename} IT Service Portal</title> 
    {/if}
</svelte:head>

{#if brand && brand.sitename}
    <!--
        Fixed height (h-16, the border included): the sidebar and the page area of
        the layouts below start at top-16, exactly at the navbar's bottom edge.
    -->
    <nav class="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-slate-300 px-2 pt-2 sm:px-4">
        <div class="fixed top-0 start-0 end-0 h-2" style="background: linear-gradient(90deg, {brand.bar_color1} 0%, {brand.bar_color1} {brand.bar_ratio}%, {brand.bar_color2} {brand.bar_ratio}%, {brand.bar_color2} 100%);"></div>
        <div class="flex items-center">
            <button
                type="button"
                class="ms-1 me-1 rounded-lg p-1.5 hover:bg-gray-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-gray-400 md:hidden"
                aria-label={i18n.t('common.menu')}
                onclick={() => drawerHidden.set(false)}
            >
                <Icon name="menu" class="w-6 h-6" />
            </button>
            <a href="/" class="flex items-center gap-3 ps-1">
                {#if brand.logo}
                <img src={brand.logo} alt="{sitename} IT Service Portal" class="w-10 h-10" />
                {/if}
                <div class="self-center whitespace-nowrap font-semibold pt-2"><span class="absolute text-xs top-5">{sitename}</span>IT Service Portal</div>
            </a>
        </div>
        <div class="flex items-center gap-4 pe-3">
            <Dropdown bind:open={langDropdownOpen} label={i18n.t('common.language')} triggerClass="lang-menu rounded-lg text-gray-500 hover:text-gray-700">
                {#snippet trigger()}<Icon name="language" class="w-7 h-7" />{/snippet}
                {#each i18n.locales as value}
                <DropdownItem onclick={() => handleChange(value)}>{i18n.t(`common.${value}`)}</DropdownItem>
                {/each}
            </Dropdown>
            {#if user}
            <Dropdown label={i18n.t('common.account_menu')} triggerClass="rounded-full">
                {#snippet trigger()}
                    <span class="flex h-8 w-8 items-center justify-center rounded-full bg-gray-100 p-1 text-gray-600 ring-2 ring-gray-300">
                        <Icon name="avatar" class="h-full w-full rounded-full" />
                    </span>
                {/snippet}
                <DropdownItem href="/profile/">
                    <span class="ms-2">{i18n.t('common.profile')}</span>
                </DropdownItem>
                <DropdownItem href="/logout/">
                    <span class="ms-2">{i18n.t('common.logout')}</span>
                </DropdownItem>
            </Dropdown>
            {/if}
        </div>
    </nav>

    <div class="lg:flex w-full">
        {@render children()}
        <footer class="fixed bottom-0 start-0 w-full bg-white border-t border-slate-300">
            <div class="flex justify-between items-center h-14 px-10">
                <span class="text-xs md:text-sm text-gray-500">© 2026 Level4. All rights reserved.</span>
                <span class="text-xs md:text-sm text-gray-500"><a href="/privacy">{i18n.t('common.privacy')}</a></span>
            </div>
        </footer>
    </div>
{:else}
    {@render children()}
{/if}

<style>
@import url('https://fonts.googleapis.com/css2?family=Noto%20Sans%20KR&display=swap');
</style>

