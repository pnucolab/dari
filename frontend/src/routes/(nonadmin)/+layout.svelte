<script>
    import "../../app.css";

    import { redirect } from '@sveltejs/kit';
    import { get } from '#lib/translations.js';
    import Sidebar from '#lib/components/ui/Sidebar.svelte';
    import SidebarItem from '#lib/components/ui/SidebarItem.svelte';

    /** @type {{ data: import('./$types').LayoutData, children: import('svelte').Snippet }} */
    let { data, children } = $props();

    const i18n = get();

    let user = $derived(data.user);

    $effect(() => {
        if (!user) {
            redirect(302, '/login/');
        }
    });
</script>

<Sidebar>
    <ul class="space-y-2">
        <SidebarItem href="/" icon="chart-pie" label={i18n.t('user.dashboard')} />
        <SidebarItem href="/vpn" icon="globe" label={i18n.t('user.vpn')} />
        <SidebarItem href="/linux" icon="terminal" label={i18n.t('user.linux')} />
        {#if user.is_staff | user.profile.is_groupadmin}
            <hr class="my-4" />
        {/if}
        {#if user.is_staff}
            <SidebarItem href="/admin" icon="adjustments-horizontal" label={i18n.t('common.admin_page')} />
        {/if}
        {#if user.profile.is_groupadmin}
            <SidebarItem href="/group" icon="users-group" label={i18n.t('common.group_manage')} />
        {/if}
    </ul>
</Sidebar>
<main class="fixed start-0 md:start-64 top-16 bottom-14 right-0 overflow-y-auto">
    {@render children()}
</main>
