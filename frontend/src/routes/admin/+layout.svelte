<script>
    import "../../app.css";

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
        ServerOutline,
        UserOutline,
        UsersGroupOutline,
        EnvelopeOutline,
        AdjustmentsHorizontalOutline,
        ArrowLeftOutline,
        FolderOutline,
        ClipboardListOutline,
    } from 'flowbite-svelte-icons';
    import { sineIn } from 'svelte/easing';
    import { drawerHidden } from '$lib/store';

    /** @type {import('./$types').LayoutData} */
    export let data;

    let user = null;
    $: user = data.user;
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
                <SidebarItem href="/admin/logs" active={activeUrl === '/logs'} label="접속 기록">
                    <svelte:fragment slot="icon">
                        <ClipboardListOutline class="w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
                    </svelte:fragment>
                </SidebarItem>
            </SidebarGroup>
            <hr class="my-2 border-gray-200 dark:border-gray-700" />
            <SidebarGroup>
                <SidebarItem href="/admin/users" active={activeUrl === '/users'} label="사용자 관리">
                    <svelte:fragment slot="icon">
                        <UserOutline class="w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
                    </svelte:fragment>
                </SidebarItem>
                <SidebarItem href="/admin/groups" active={activeUrl === '/groups'} label="그룹 관리">
                    <svelte:fragment slot="icon">
                        <UsersGroupOutline class="w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
                    </svelte:fragment>
                </SidebarItem>
                <SidebarItem href="/admin/servers" active={activeUrl === '/servers'} label="서버 관리">
                    <svelte:fragment slot="icon">
                        <ServerOutline class="w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
                    </svelte:fragment>
                </SidebarItem>
                <SidebarItem href="/admin/nfsshares" active={activeUrl === '/nfsshares'} label="공유 폴더 관리">
                    <svelte:fragment slot="icon">
                        <FolderOutline class="w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
                    </svelte:fragment>
                </SidebarItem>
            </SidebarGroup>
            <hr class="my-2 border-gray-200 dark:border-gray-700" />
            <SidebarGroup>
                <SidebarItem href="/admin/settings" active={activeUrl === '/settings'} label="기본 설정">
                    <svelte:fragment slot="icon">
                        <AdjustmentsHorizontalOutline class="w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
                    </svelte:fragment>
                </SidebarItem>
                <SidebarItem href="/admin/email" active={activeUrl === '/email'} label="이메일 전송">
                    <svelte:fragment slot="icon">
                        <EnvelopeOutline class="w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
                    </svelte:fragment>
                </SidebarItem>
            </SidebarGroup>
            <hr class="my-2 border-gray-200 dark:border-gray-700" />
            <SidebarGroup>
                <SidebarItem href="/" label="돌아가기">
                    <svelte:fragment slot="icon">
                        <ArrowLeftOutline class="w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
                    </svelte:fragment>
                </SidebarItem>
            </SidebarGroup>
        </SidebarWrapper>
    </Sidebar>
</Drawer>

<main class="fixed start-0 md:start-64 top-16 bottom-14 right-0 overflow-y-auto">
    <slot></slot>
</main>