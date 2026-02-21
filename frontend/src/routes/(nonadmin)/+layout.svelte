<script>
    import "../../app.css";

    import { redirect } from '@sveltejs/kit';
    import { t } from '$lib/translations';
    import { page } from '$app/stores';
    import { onMount } from 'svelte';
    import {
        Sidebar,
        SidebarGroup,
        SidebarItem,
        SidebarWrapper,
        Drawer,
        CloseButton,
    } from 'flowbite-svelte';
    import {
        ChartPieOutline,
        GlobeOutline,
        TerminalOutline,
        UsersGroupOutline,
        AdjustmentsHorizontalOutline,
    } from 'flowbite-svelte-icons';
    import { sineIn } from 'svelte/easing';
    import { drawerHidden } from '$lib/store';

    /** @type {import('./$types').LayoutData} */
    export let data;

    let user = null;
    $: user = data.user;

    $: if (!user) {
        redirect(302, '/login/');
    }

    $: activeUrl = $page.url.pathname;

    let transitionParams = {
		x: -320,
		duration: 0,
		easing: sineIn
	};

    let breakPoint = 768;
	let width;
    let activateClickOutside = true;
    let backdrop = false;
	$: if (width >= breakPoint) {
		$drawerHidden = false;
		activateClickOutside = false;
        backdrop = false;
        transitionParams.duration = 0;
	} else {
		$drawerHidden = true;
		activateClickOutside = true;
        backdrop = true;
        transitionParams.duration = 200;
	}
	onMount(() => {
		if (width >= breakPoint) {
            $drawerHidden = false;
            activateClickOutside = false;
            backdrop = false;
            transitionParams.duration = 0;
        } else {
            $drawerHidden = true;
            activateClickOutside = true;
            backdrop = true;
            transitionParams.duration = 200;
        }
	});
	const toggleSide = () => {
		if (width < breakPoint) {
			$drawerHidden = !($drawerHidden);
		}
	};
</script>

<svelte:window bind:innerWidth={width} />
<Drawer transitionType="fly" {transitionParams} {backdrop} bind:hidden={$drawerHidden} bind:activateClickOutside class="fixed top-0 bottom-0 md:top-16 md:bottom-14 w-64 m-0 p-0 z-50 md:z-0" id="sidebar">
    <Sidebar asideClass="w-64" class="border-r border-slate-300 h-full" {activeUrl}>
        <div class="flex items-end md:hidden">
            <CloseButton on:click={toggleSide} class="" />
        </div>
        <SidebarWrapper class="bg-white">
            <SidebarGroup>
                <SidebarItem on:click={toggleSide} href="/" active={activeUrl === '/'} label="{$t('user.dashboard')}">
                    <svelte:fragment slot="icon">
                        <ChartPieOutline class="w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
                    </svelte:fragment>
                </SidebarItem>
                <SidebarItem on:click={toggleSide} href="/vpn" active={activeUrl === '/vpn'} label="{$t('user.vpn')}">
                    <svelte:fragment slot="icon">
                        <GlobeOutline class="w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
                    </svelte:fragment>
                </SidebarItem>
                <SidebarItem on:click={toggleSide} href="/linux" active={activeUrl === '/linux'} label="{$t('user.linux')}">
                    <svelte:fragment slot="icon">
                        <TerminalOutline class="w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
                    </svelte:fragment>
                </SidebarItem>
                {#if user.is_staff | user.profile.is_groupadmin}
                    <hr class="my-4" />
                {/if}
                {#if user.is_staff}
                    <SidebarItem on:click={toggleSide} href="/admin" active={activeUrl === '/admin'} label="관리자 페이지">
                        <svelte:fragment slot="icon">
                            <AdjustmentsHorizontalOutline class="w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
                        </svelte:fragment>
                    </SidebarItem>
                {/if}
                {#if user.profile.is_groupadmin}
                    <SidebarItem on:click={toggleSide} href="/group" active={activeUrl === '/group'} label="그룹 관리">
                        <svelte:fragment slot="icon">
                            <UsersGroupOutline class="w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
                        </svelte:fragment>
                    </SidebarItem>
                {/if}
                <!--
                <SidebarItem href="/a100" active={activeUrl === '/a100'} label="A100 서버">
                    <svelte:fragment slot="icon">
                        <TerminalOutline class="w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
                    </svelte:fragment>
                </SidebarItem>
                <SidebarItem href="/nextcloud" active={activeUrl === '/nextcloud'} label="웹하드 (NextCloud)">
                    <svelte:fragment slot="icon">
                        <CloudArrowUpOutline class="w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
                    </svelte:fragment>
                </SidebarItem>
                <SidebarItem href="/web" active={activeUrl === '/web'} label="웹 호스팅">
                    <svelte:fragment slot="icon">
                        <CloudArrowUpOutline class="w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
                    </svelte:fragment>
                </SidebarItem>
                -->
            </SidebarGroup>
        </SidebarWrapper>
    </Sidebar>
</Drawer>
<main class="fixed start-0 md:start-64 top-16 bottom-14 right-0 overflow-y-auto">
    <slot></slot>
</main>