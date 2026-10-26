<script>
    import {
        Card,
        Table,
        TableHead,
        TableHeadCell,
        TableBody,
        TableBodyRow,
        TableBodyCell,
        Modal,
        Label,
        Input,
        Button,
        Alert,
        Icon,
    } from '#lib/components/ui/index.js';
    import GroupSelector from '#lib/components/GroupSelector.svelte';
    import { get } from '#lib/translations.js';

    import { onMount, onDestroy } from 'svelte';
    import { enhance } from '$app/forms';

    let { form } = $props();

    const i18n = get();

    let servers = $state(null);
    let stats = $state({});
    let allGroups = $state([]);
    let refreshInterval;

    let addServerType = $state('compute');
    let serverModal = $state(false);
    let serverModifying = $state(false);

    let editPk = $state('');
    let editDomainname = $state('');
    let editIp = $state('');
    let editPort = $state('');
    let editAllowedGroups = $state([]);

    let apiKeyModal = $state(false);
    let apiKeyValue = $state('');

    function showApiKey(key) {
        apiKeyValue = key || '';
        apiKeyModal = true;
    }

    async function copyApiKey() {
        await navigator.clipboard.writeText(apiKeyValue);
        apiKeyModal = false;
    }

    onMount(() => {
        refreshServers();
        refreshGroups();
        refreshStats();
        refreshInterval = setInterval(refreshStats, 5000);
    });

    onDestroy(() => {
        if (refreshInterval) clearInterval(refreshInterval);
    });

    async function refreshServers() {
        const response = await fetch('?/servers', {
            method: 'POST',
            'body': ''
        });
        const result = await response.json();
        const result_json = JSON.parse(JSON.parse(result.data)[1]);
        servers = result_json;
    }

    async function refreshStats() {
        const response = await fetch('?/stats', {
            method: 'POST',
            'body': ''
        });
        const result = await response.json();
        stats = JSON.parse(JSON.parse(result.data)[1]);
    }

    async function refreshGroups() {
        const response = await fetch('?/groups', {
            method: 'POST',
            'body': ''
        });
        const result = await response.json();
        allGroups = JSON.parse(JSON.parse(result.data)[1]);
    }

    async function deleteServer(pk) {
        let formData = new FormData();
        formData.append('pk', pk);
        const response = await fetch('?/serverdelete', {
            method: 'POST',
            'body': formData
        });
        refreshServers();
    }

    function openAddModal(type) {
        addServerType = type;
        serverModifying = false;
        editPk = '';
        editDomainname = '';
        editIp = '';
        editPort = '';
        editAllowedGroups = [];
        serverModal = true;
    }

    function openEditModal(server) {
        addServerType = server.server_type;
        serverModifying = true;
        editPk = server.pk;
        editDomainname = server.domainname;
        editIp = server.ip;
        editPort = server.port || '';
        editAllowedGroups = server.allowed_groups ? [...server.allowed_groups] : [];
        serverModal = true;
    }

    function handleSubmit() {
        return async ({ result }) => {
            if (!result.error) {
                serverModal = false;
                refreshServers();
            }
        };
    }

    let computeServers = $derived(servers ? servers.filter(s => s.server_type === 'compute') : null);
    let storageServers = $derived(servers ? servers.filter(s => s.server_type === 'storage') : null);
</script>

<Modal bind:open={serverModal} size="md" autoclose={false} class="w-full">
    <form method="POST" action="?/server" id="server-form" class="space-y-4" use:enhance={handleSubmit}>
        <input type="hidden" name="server_type" value={addServerType} />
        <input type="hidden" name="allowed_groups" value={editAllowedGroups.join(', ')} />
        {#if serverModifying}<input type="hidden" name="pk" value={editPk} />{/if}
        <h3 class="mb-4 text-xl font-medium text-gray-900 dark:text-white">{i18n.t(`admin.servers.${serverModifying ? 'edit' : 'add'}_${addServerType === 'storage' ? 'storage' : 'compute'}`)}</h3>
        <div class="flex gap-3 mb-3">
            <Label class="w-full space-y-2">
                <span>{i18n.t('admin.servers.domainname')}</span>
                <Input type="text" name="domainname" bind:value={editDomainname} />
            </Label>
            <Label class="w-full space-y-2">
                <span>IP</span>
                <Input type="text" name="ip" bind:value={editIp} />
            </Label>
            {#if addServerType === 'compute'}
            <Label class="space-y-2" style="min-width:100px">
                <span>{i18n.t('admin.servers.ssh_port')}</span>
                <Input type="number" name="port" placeholder="22" bind:value={editPort} />
            </Label>
            {/if}
        </div>
        {#if addServerType === 'compute'}
        <div class="mb-3">
            <Label class="w-full space-y-2">
                <span>{i18n.t('admin.allowed_groups_hint')}</span>
                <GroupSelector groups={allGroups} bind:selected={editAllowedGroups} />
            </Label>
        </div>
        {/if}
        <div class="mb-5">
            {#if form?.error}
            <Alert color="red" dismissable>{i18n.t('admin.servers.error')}</Alert>
            {/if}
        </div>
    </form>
    {#snippet footer()}
        <Button color="blue" type="submit" form="server-form">{serverModifying?i18n.t('admin.servers.submit_edit'):i18n.t('common.add')}</Button>
        <Button color="alternative" onclick={() => serverModal = false}>{i18n.t('common.cancel')}</Button>
    {/snippet}
</Modal>

<div class="grid grid-cols-1 gap-4 p-4 w-full">
    <Card size="xl" class="p-4 sm:p-6 text-gray-500 dark:text-gray-400">
        <div class="flex justify-between">
            <h5 class="mb-5 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">{i18n.t('admin.servers.compute')}</h5>
            <Button class="h-10 w-10" size="xs" color="blue" onclick={() => openAddModal('compute')}><Icon name="plus" /></Button>
        </div>
        <Table class="text-center">
            <TableHead>
                <TableHeadCell>{i18n.t('admin.servers.domainname')}</TableHeadCell>
                <TableHeadCell>IP</TableHeadCell>
                <TableHeadCell>{i18n.t('admin.servers.ssh_port')}</TableHeadCell>
                <TableHeadCell>{i18n.t('admin.allowed_groups')}</TableHeadCell>
                <TableHeadCell>{i18n.t('admin.servers.api_key')}</TableHeadCell>
                <TableHeadCell>{i18n.t('admin.servers.temperature')}</TableHeadCell>
                <TableHeadCell>{i18n.t('admin.servers.cpu')}</TableHeadCell>
                <TableHeadCell>{i18n.t('admin.servers.memory')}</TableHeadCell>
                <TableHeadCell width="100px">{i18n.t('common.actions')}</TableHeadCell>
            </TableHead>
            <TableBody class="divide-y">
                {#if !computeServers}
                <TableBodyRow>
                    <TableBodyCell colspan="9" class="text-center">{i18n.t('admin.servers.loading')}</TableBodyCell>
                </TableBodyRow>
                {:else if computeServers.length === 0}
                <TableBodyRow>
                    <TableBodyCell colspan="9" class="text-center">{i18n.t('admin.servers.no_compute')}</TableBodyCell>
                </TableBodyRow>
                {:else}
                {#each computeServers as server}
                <TableBodyRow>
                    <TableBodyCell>{server.domainname}</TableBodyCell>
                    <TableBodyCell>{server.ip}</TableBodyCell>
                    <TableBodyCell>{server.port || '-'}</TableBodyCell>
                    <TableBodyCell>{server.allowed_groups && server.allowed_groups.length > 0 ? server.allowed_groups.join(', ') : i18n.t('common.all')}</TableBodyCell>
                    <TableBodyCell><button type="button" class="text-xs cursor-pointer hover:underline" onclick={() => showApiKey(server.api_key)}>{server.api_key ? server.api_key.substring(0, 8) + '...' : '-'}</button></TableBodyCell>
                    {#if stats[server.pk]}
                    <TableBodyCell>{stats[server.pk].t}</TableBodyCell>
                    <TableBodyCell>{stats[server.pk].c}</TableBodyCell>
                    <TableBodyCell>{stats[server.pk].m}</TableBodyCell>
                    {:else}
                    <TableBodyCell colspan="3" class="text-center">{i18n.t('admin.servers.no_info')}</TableBodyCell>
                    {/if}
                    <TableBodyCell>
                        <div class="flex gap-1 justify-center">
                            <Button size="sm" color="alternative" class="border-0" onclick={() => openEditModal(server)}><Icon name="edit" class="w-4 h-4" /></Button>
                            <Button size="sm" color="alternative" class="border-0" onclick={() => deleteServer(server.pk)}><Icon name="trash-bin" class="w-4 h-4" /></Button>
                        </div>
                    </TableBodyCell>
                </TableBodyRow>
                {/each}
                {/if}
            </TableBody>
        </Table>
    </Card>
    <Card size="xl" class="p-4 sm:p-6 text-gray-500 dark:text-gray-400">
        <div class="flex justify-between">
            <h5 class="mb-5 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">{i18n.t('admin.servers.storage')}</h5>
            <Button class="h-10 w-10" size="xs" color="blue" onclick={() => openAddModal('storage')}><Icon name="plus" /></Button>
        </div>
        <Table class="text-center">
            <TableHead>
                <TableHeadCell>{i18n.t('admin.servers.domainname')}</TableHeadCell>
                <TableHeadCell>IP</TableHeadCell>
                <TableHeadCell>{i18n.t('admin.servers.api_key')}</TableHeadCell>
                <TableHeadCell>{i18n.t('admin.servers.temperature')}</TableHeadCell>
                <TableHeadCell>{i18n.t('admin.servers.cpu')}</TableHeadCell>
                <TableHeadCell>{i18n.t('admin.servers.memory')}</TableHeadCell>
                <TableHeadCell width="100px">{i18n.t('common.actions')}</TableHeadCell>
            </TableHead>
            <TableBody class="divide-y">
                {#if !storageServers}
                <TableBodyRow>
                    <TableBodyCell colspan="7" class="text-center">{i18n.t('admin.servers.loading')}</TableBodyCell>
                </TableBodyRow>
                {:else if storageServers.length === 0}
                <TableBodyRow>
                    <TableBodyCell colspan="7" class="text-center">{i18n.t('admin.servers.no_storage')}</TableBodyCell>
                </TableBodyRow>
                {:else}
                {#each storageServers as server}
                <TableBodyRow>
                    <TableBodyCell>{server.domainname}</TableBodyCell>
                    <TableBodyCell>{server.ip}</TableBodyCell>
                    <TableBodyCell><button type="button" class="text-xs cursor-pointer hover:underline" onclick={() => showApiKey(server.api_key)}>{server.api_key ? server.api_key.substring(0, 8) + '...' : '-'}</button></TableBodyCell>
                    {#if stats[server.pk]}
                    <TableBodyCell>{stats[server.pk].t}</TableBodyCell>
                    <TableBodyCell>{stats[server.pk].c}</TableBodyCell>
                    <TableBodyCell>{stats[server.pk].m}</TableBodyCell>
                    {:else}
                    <TableBodyCell colspan="3" class="text-center">{i18n.t('admin.servers.no_info')}</TableBodyCell>
                    {/if}
                    <TableBodyCell>
                        <div class="flex gap-1 justify-center">
                            <Button size="sm" color="alternative" class="border-0" onclick={() => openEditModal(server)}><Icon name="edit" class="w-4 h-4" /></Button>
                            <Button size="sm" color="alternative" class="border-0" onclick={() => deleteServer(server.pk)}><Icon name="trash-bin" class="w-4 h-4" /></Button>
                        </div>
                    </TableBodyCell>
                </TableBodyRow>
                {/each}
                {/if}
            </TableBody>
        </Table>
    </Card>
</div>

<Modal bind:open={apiKeyModal} size="sm" autoclose={false}>
    <h3 class="mb-4 text-xl font-medium text-gray-900 dark:text-white">{i18n.t('admin.servers.api_key')}</h3>
    <code class="block w-full p-3 text-sm bg-gray-100 dark:bg-gray-800 rounded-lg break-all select-all">{apiKeyValue}</code>
    {#snippet footer()}
        <Button color="blue" onclick={copyApiKey}>{i18n.t('common.copy')}</Button>
        <Button color="alternative" onclick={() => apiKeyModal = false}>{i18n.t('user.close')}</Button>
    {/snippet}
</Modal>
