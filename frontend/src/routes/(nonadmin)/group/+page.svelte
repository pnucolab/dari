<script>
    import {
        Card,
        TableSearch,
        TableHead,
        TableHeadCell,
        TableBody,
        TableBodyRow,
        TableBodyCell,
        Input,
        Button,
        Modal,
        Icon,
    } from '#lib/components/ui/index.js';
    import { refreshAll } from '$app/navigation';
    import { get } from '#lib/translations.js';

    let { data } = $props();

    const i18n = get();

    let searchTerm = $state('');
    let groups = $derived(data.groups ?? []);
    let maxgid = $derived(groups.length?(Math.max(...groups.map(group => parseInt(group.gid))) + 1):1000);
    let filteredGroups = $derived(groups.filter(group => 
        group.name.toLowerCase().includes(searchTerm.toLowerCase())
    ));

    async function confirmGroupmod() {
        const formData = new FormData();
        let response;
        formData.append('pk', editingGroup.pk);
        formData.append('members', editingGroup.members);
        response = await fetch('?/groupmod', {
            method: 'POST',
            body: formData,
        });
        if (response.ok) {
            refreshAll();
        }
    }

    function cancelGroupmod() {
        editingGroup = null;
    }

    let confirmModal = $state(false);
    let editingGroup = $state(null);
</script>

<Modal title={i18n.t('common.confirm')} bind:open={confirmModal} size="xs" autoclose>
    <div class="text-center">
        <Icon name="exclamation-circle" class="mx-auto mb-4 text-gray-400 w-12 h-12 dark:text-gray-200" />
        <h3 class="mb-5 text-lg font-normal text-gray-500 dark:text-gray-400">{i18n.t('common.confirm_edit')}</h3>
        <Button color="red" onclick={confirmGroupmod}>{i18n.t('common.yes')}</Button>
        <Button color="alternative" onclick={cancelGroupmod}>{i18n.t('common.no')}</Button>
    </div>
</Modal>

<div class="grid grid-cols-1 lg:grid-cols-2 gap-4 p-4 w-full">
    <Card size="xl" class="p-4 sm:p-6 text-gray-500 dark:text-gray-400 lg:col-span-2">
        <TableSearch placeholder={i18n.t('common.search_group_name')} class="text-center" hoverable={true} bind:inputValue={searchTerm}>
            <TableHead>
                <TableHeadCell width="15%">{i18n.t('common.group_name')}</TableHeadCell>
                <TableHeadCell width="15%">GID</TableHeadCell>
                <TableHeadCell>{i18n.t('common.members')}</TableHeadCell>
                <TableHeadCell width="100px">{i18n.t('common.actions')}</TableHeadCell>
            </TableHead>
            <TableBody class="divide-y">
                {#if filteredGroups.length === 0}
                    <TableBodyRow>
                        <TableBodyCell colspan="4" class="text-center">{i18n.t('common.no_groups')}</TableBodyCell>
                    </TableBodyRow>
                {/if}
                {#each filteredGroups as group}
                    <TableBodyRow>
                        <TableBodyCell>{group.name}</TableBodyCell>
                        <TableBodyCell>{group.gid}</TableBodyCell>
                        <TableBodyCell><Input type="text" bind:value={group.members} /></TableBodyCell>
                        <TableBodyCell>
                            <Button pill outline size="xs" color="blue" onclick={() => {editingGroup = group; confirmModal = true;}}>
                                {i18n.t('common.apply')}
                            </Button>
                        </TableBodyCell>
                    </TableBodyRow>
                {/each}
            </TableBody>
        </TableSearch>
    </Card>
</div>