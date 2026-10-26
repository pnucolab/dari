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
        Select,
        Icon,
    } from '#lib/components/ui/index.js';
    import GroupSelector from '#lib/components/GroupSelector.svelte';
    import MultiSelect from '#lib/components/MultiSelect.svelte';
    import { get } from '#lib/translations.js';

    import { onMount, onDestroy } from 'svelte';
    import { enhance } from '$app/forms';

    let { form } = $props();

    const i18n = get();

    let shares = $state(null);
    let servers = $state(null);
    let allGroups = $state([]);
    let dariHomeServer = $state(null);
    let refreshInterval;

    let selectedAllowedServers = $state([]);
    let selectedAllowedGroups = $state([]);

    onMount(() => {
        refreshShares();
        refreshServers();
        refreshGroups();
        refreshDariHome();
        refreshInterval = setInterval(refreshShares, 5000);
    });

    onDestroy(() => {
        if (refreshInterval) clearInterval(refreshInterval);
    });

    async function refreshShares() {
        const response = await fetch('?/list', {
            method: 'POST',
            'body': ''
        });
        const result = await response.json();
        const result_json = JSON.parse(JSON.parse(result.data)[1]);
        shares = result_json;
    }

    async function refreshServers() {
        const response = await fetch('?/servers', {
            method: 'POST',
            'body': ''
        });
        const result = await response.json();
        const result_json = JSON.parse(JSON.parse(result.data)[1]);
        servers = result_json;
    }

    async function refreshGroups() {
        const response = await fetch('?/groups', {
            method: 'POST',
            'body': ''
        });
        const result = await response.json();
        const result_json = JSON.parse(JSON.parse(result.data)[1]);
        allGroups = result_json;
    }

    async function refreshDariHome() {
        const response = await fetch('?/darihome', {
            method: 'POST',
            'body': ''
        });
        const result = await response.json();
        const result_json = JSON.parse(JSON.parse(result.data)[1]);
        dariHomeServer = result_json.server_pk;
    }

    async function deleteShare(pk) {
        let formData = new FormData();
        formData.append('pk', pk);
        const response = await fetch('?/delete', {
            method: 'POST',
            'body': formData
        });
        refreshShares();
    }

    async function setDariHome(event) {
        let formData = new FormData();
        formData.append('server_pk', event.target.value);
        const response = await fetch('?/setdarihome', {
            method: 'POST',
            'body': formData
        });
        refreshDariHome();
    }

    let shareModal = $state(false);

    function openShareModal() {
        selectedAllowedServers = [];
        selectedAllowedGroups = [];
        shareModal = true;
    }

    function handleSubmit() {
        return async ({ result }) => {
            if (!result.error) {
                shareModal = false;
                refreshShares();
            }
        };
    }

    let computeServers = $derived(servers ? servers.filter(s => s.server_type === 'compute') : []);
    let storageServers = $derived(servers ? servers.filter(s => s.server_type === 'storage') : []);
    let computeServerItems = $derived(computeServers.map(s => ({ name: `${s.domainname} (${s.ip})`, value: s.domainname })));
</script>

<Modal bind:open={shareModal} size="md" autoclose={false} class="w-full">
    <form method="POST" action="?/create" id="share-form" class="space-y-4" use:enhance={handleSubmit}>
        <input type="hidden" name="allowed_groups" value={selectedAllowedGroups.join(', ')} />
        <input type="hidden" name="allowed_servers" value={selectedAllowedServers.join(', ')} />
        <h3 class="mb-4 text-xl font-medium text-gray-900 dark:text-white">{i18n.t('admin.nfs.add_title')}</h3>
        <div class="flex gap-3 mb-3">
            <Label class="w-full space-y-2">
                <span>{i18n.t('user.name')}</span>
                <Input type="text" name="name" placeholder="shared-data" />
            </Label>
            <Label class="w-full space-y-2">
                <span>{i18n.t('admin.nfs.storage_server')}</span>
                <Select name="server_ip">
                    <option value="" disabled selected>{i18n.t('admin.nfs.select_server')}</option>
                    {#each storageServers as srv}
                    <option value={srv.ip}>{srv.domainname} ({srv.ip})</option>
                    {/each}
                </Select>
            </Label>
        </div>
        <div class="flex gap-3 mb-3">
            <Label class="w-full space-y-2">
                <span>{i18n.t('admin.nfs.export_path')}</span>
                <Input type="text" name="export_path" placeholder="/export/data" />
            </Label>
            <Label class="w-full space-y-2">
                <span>{i18n.t('admin.nfs.mount_point')}</span>
                <Input type="text" name="mount_point" placeholder="/mnt/data" />
            </Label>
        </div>
        <div class="mb-3">
            <Label class="w-full space-y-2">
                <span>{i18n.t('admin.allowed_groups_hint')}</span>
                <GroupSelector groups={allGroups} bind:selected={selectedAllowedGroups} />
            </Label>
        </div>
        <div class="mb-5">
            <Label class="space-y-2">
                <span>{i18n.t('admin.nfs.allowed_servers_hint')}</span>
            </Label>
            <div class="mt-2">
                <MultiSelect
                    items={computeServerItems}
                    bind:selected={selectedAllowedServers}
                    labelKey="name"
                    valueKey="value"
                    placeholder={i18n.t('admin.nfs.search_server')}
                    emptyText={i18n.t('admin.servers.no_compute')}
                />
            </div>
            {#if form?.error}
            <Alert color="red" dismissable>{i18n.t('admin.nfs.error')}</Alert>
            {/if}
        </div>
    </form>
    {#snippet footer()}
        <Button color="blue" type="submit" form="share-form">{i18n.t('common.add')}</Button>
        <Button color="alternative" onclick={() => shareModal = false}>{i18n.t('common.cancel')}</Button>
    {/snippet}
</Modal>

<div class="grid grid-cols-1 gap-4 p-4 w-full">
    <Card size="xl" class="p-4 sm:p-6 text-gray-500 dark:text-gray-400">
        <div class="flex justify-between items-center mb-5">
            <h5 class="text-2xl font-bold tracking-tight text-gray-900 dark:text-white">{i18n.t('admin.nfs.home_title')}</h5>
        </div>
        <div class="flex items-center gap-3">
            <Label class="space-y-2 w-full max-w-md">
                <span>{i18n.t('admin.nfs.home_server')}</span>
                <Select onchange={setDariHome} value={dariHomeServer || ''}>
                    <option value="">{i18n.t('admin.nfs.none')}</option>
                    {#each storageServers as srv}
                    <option value={srv.pk}>{srv.domainname} ({srv.ip})</option>
                    {/each}
                </Select>
            </Label>
        </div>
    </Card>
    <Card size="xl" class="p-4 sm:p-6 text-gray-500 dark:text-gray-400">
        <div class="flex justify-between">
            <h5 class="mb-5 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">{i18n.t('admin.nfs.title')}</h5>
            <Button class="h-10 w-10" size="xs" color="blue" onclick={openShareModal}><Icon name="plus" /></Button>
        </div>
        <Table class="text-center">
            <TableHead>
                <TableHeadCell>{i18n.t('user.name')}</TableHeadCell>
                <TableHeadCell>{i18n.t('admin.nfs.server_ip')}</TableHeadCell>
                <TableHeadCell>{i18n.t('admin.nfs.export_path')}</TableHeadCell>
                <TableHeadCell>{i18n.t('admin.nfs.mount_point')}</TableHeadCell>
                <TableHeadCell>{i18n.t('admin.allowed_groups')}</TableHeadCell>
                <TableHeadCell>{i18n.t('admin.nfs.allowed_servers')}</TableHeadCell>
                <TableHeadCell width="100px">{i18n.t('common.actions')}</TableHeadCell>
            </TableHead>
            <TableBody class="divide-y">
                {#if !shares}
                <TableBodyRow>
                    <TableBodyCell colspan="7" class="text-center">{i18n.t('admin.nfs.loading')}</TableBodyCell>
                </TableBodyRow>
                {:else if shares.length === 0}
                <TableBodyRow>
                    <TableBodyCell colspan="7" class="text-center">{i18n.t('admin.nfs.no_shares')}</TableBodyCell>
                </TableBodyRow>
                {:else}
                {#each shares as share}
                <TableBodyRow>
                    <TableBodyCell>{share.name}</TableBodyCell>
                    <TableBodyCell>{share.server_ip}</TableBodyCell>
                    <TableBodyCell><code>{share.export_path}</code></TableBodyCell>
                    <TableBodyCell><code>{share.mount_point}</code></TableBodyCell>
                    <TableBodyCell>{share.allowed_groups && share.allowed_groups.length > 0 ? share.allowed_groups.join(', ') : i18n.t('common.all')}</TableBodyCell>
                    <TableBodyCell>{share.allowed_servers && share.allowed_servers.length > 0 ? share.allowed_servers.join(', ') : i18n.t('common.all')}</TableBodyCell>
                    <TableBodyCell>
                        <Button size="sm" color="alternative" class="border-0" onclick={() => deleteShare(share.pk)}><Icon name="trash-bin" class="w-4 h-4" /></Button>
                    </TableBodyCell>
                </TableBodyRow>
                {/each}
                {/if}
            </TableBody>
        </Table>
    </Card>
</div>
