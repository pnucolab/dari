<script>
    import "../../app.css";

    import { get } from '#lib/translations.js';
    import Sidebar from '#lib/components/ui/Sidebar.svelte';
    import SidebarItem from '#lib/components/ui/SidebarItem.svelte';

    /** @type {{ data: import('./$types').LayoutData, children: import('svelte').Snippet }} */
    let { children } = $props();

    const i18n = get();
</script>

<Sidebar>
    <ul class="space-y-2">
        <SidebarItem href="/admin/logs" icon="clipboard-list" label={i18n.t('admin.menu.logs')} />
    </ul>
    <hr class="my-2 border-gray-200" />
    <ul class="space-y-2">
        <SidebarItem href="/admin/users" icon="user" label={i18n.t('admin.menu.users')} />
        <SidebarItem href="/admin/groups" icon="users-group" label={i18n.t('common.group_manage')} />
        <SidebarItem href="/admin/servers" icon="server" label={i18n.t('admin.menu.servers')} />
        <SidebarItem href="/admin/nfsshares" icon="folder" label={i18n.t('admin.menu.nfsshares')} />
    </ul>
    <hr class="my-2 border-gray-200" />
    <ul class="space-y-2">
        <SidebarItem href="/admin/settings" icon="adjustments-horizontal" label={i18n.t('admin.menu.settings')} />
        <SidebarItem href="/admin/email" icon="envelope" label={i18n.t('admin.menu.email')} />
    </ul>
    <hr class="my-2 border-gray-200" />
    <ul class="space-y-2">
        <SidebarItem href="/" icon="arrow-left" label={i18n.t('common.back')} />
    </ul>
</Sidebar>

<main class="fixed start-0 md:start-64 top-16 bottom-14 right-0 overflow-y-auto">
    {@render children()}
</main>
