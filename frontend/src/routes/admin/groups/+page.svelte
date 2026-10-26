<script>
    import {
        Card,
        Table,
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
    import { enhance } from '$app/forms';
    import { get } from '#lib/translations.js';

    let { data } = $props();

    const i18n = get();

    let searchTerm = $state('');
    let searchAdminTerm = $state('');
    let groups = $derived(data.groups ?? []);
    let admins = $derived(data.admins ?? []);
    let maxgid = $derived(groups.length?(Math.max(...groups.map(group => parseInt(group.gid))) + 1):1000);
    let filteredGroups = $derived(groups.filter(group => 
        group.name.toLowerCase().includes(searchTerm.toLowerCase())
    ));
    let filteredAdmins = $derived(admins.filter(admin => 
        admin.linux_username.toLowerCase().includes(searchAdminTerm.toLowerCase())
    ));

    async function confirmGroupmod() {
        const formData = new FormData();
        let response;
        if (editingGroup) {
            formData.append('pk', editingGroup.pk);
            formData.append('name', editingGroup.name);
            formData.append('gid', editingGroup.gid);
            formData.append('members', editingGroup.members);
            response = await fetch('?/groupmod', {
                method: 'POST',
                body: formData,
            });
        } else if (removingGroup) {
            formData.append('pk', removingGroup.pk);
            response = await fetch('?/groupdel', {
                method: 'POST',
                body: formData,
            });
        }
        if (response.ok) {
            refreshAll();
        }
    }

    function checkAdd() {
        return async ({result}) => {
            if (result.type === 'success') {
                refreshAll();
                addModal = false;
            }
        }
    }

    function cancelGroupmod() {
        editingGroup = null;
        removingGroup = null;
    }

    async function confirmAdminmod() {
        const formData = new FormData();
        let response;
        if (editingAdmin) {
            formData.append('linux_username', editingAdmin.linux_username);
            formData.append('group_names', editingAdmin.group_names);
            response = await fetch('?/adminpost', {
                method: 'POST',
                body: formData,
            });
        } else if (removingAdmin) {
            formData.append('linux_username', removingAdmin.linux_username);
            response = await fetch('?/admindel', {
                method: 'POST',
                body: formData,
            });
        }
        if (response.ok) {
            refreshAll();
        }
    }

    function checkAddAdmin() {
        return async ({result}) => {
            if (result.type === 'success') {
                refreshAll();
                addAdminModal = false;
            }
        }
    }

    function cancelAdminmod() {
        editingAdmin = null;
        removingAdmin = null;
    }

    let addModal = $state(false);
    let confirmModal = $state(false);
    let addAdminModal = $state(false);
    let confirmAdminModal = $state(false);
    let editingGroup = $state(null);
    let removingGroup = $state(null);
    let editingAdmin = $state(null);
    let removingAdmin = $state(null);
</script>

<Modal title={i18n.t('common.confirm')} bind:open={confirmModal} size="xs" autoclose>
    <div class="text-center">
        <Icon name="exclamation-circle" class="mx-auto mb-4 text-gray-400 w-12 h-12 dark:text-gray-200" />
        <h3 class="mb-5 text-lg font-normal text-gray-500 dark:text-gray-400">{editingGroup?i18n.t('common.confirm_edit'):i18n.t('common.confirm_delete')}</h3>
        <Button color="red" onclick={confirmGroupmod}>{i18n.t('common.yes')}</Button>
        <Button color="alternative" onclick={cancelGroupmod}>{i18n.t('common.no')}</Button>
    </div>
</Modal>

<Modal title={i18n.t('admin.groups.add_group')} bind:open={addModal} size="xs">
    <form method="POST" action="?/groupadd" use:enhance={checkAdd}>
        <Table>
            <TableHead>
                <TableHeadCell>{i18n.t('common.group_name')}</TableHeadCell>
                <TableHeadCell>GID</TableHeadCell>
                <TableHeadCell>{i18n.t('common.members')}</TableHeadCell>
            </TableHead>
            <TableBody>
                <TableBodyRow>
                    <TableBodyCell><Input type="text" name="name" /></TableBodyCell>
                    <TableBodyCell><Input type="text" name="gid" value={maxgid} /></TableBodyCell>
                    <TableBodyCell><Input type="text" name="members" /></TableBodyCell>
                </TableBodyRow>
            </TableBody>
        </Table>
        <div class="flex gap-1">
            <Button color="blue" type="submit">{i18n.t('common.confirm')}</Button>
            <Button color="alternative" onclick={() => addModal = false}>{i18n.t('common.cancel')}</Button>
        </div>
    </form>
</Modal>
<Modal title={i18n.t('admin.groups.add_admin')} bind:open={addAdminModal} size="xs">
    <form method="POST" action="?/adminpost" use:enhance={checkAddAdmin}>
        <Table>
            <TableHead>
                <TableHeadCell>{i18n.t('admin.groups.admin_linux_id')}</TableHeadCell>
                <TableHeadCell>{i18n.t('admin.groups.group_names')}</TableHeadCell>
            </TableHead>
            <TableBody>
                <TableBodyRow>
                    <TableBodyCell><Input type="text" name="linux_username" /></TableBodyCell>
                    <TableBodyCell><Input type="text" name="group_names" /></TableBodyCell>
                </TableBodyRow>
            </TableBody>
        </Table>
        <div class="flex gap-1">
            <Button color="blue" type="submit">{i18n.t('common.confirm')}</Button>
            <Button color="alternative" onclick={() => addAdminModal = false}>{i18n.t('common.cancel')}</Button>
        </div>
    </form>
</Modal>

<Modal title={i18n.t('common.confirm')} bind:open={confirmAdminModal} size="xs" autoclose>
    <div class="text-center">
        <Icon name="exclamation-circle" class="mx-auto mb-4 text-gray-400 w-12 h-12 dark:text-gray-200" />
        <h3 class="mb-5 text-lg font-normal text-gray-500 dark:text-gray-400">{editingAdmin?i18n.t('common.confirm_edit'):i18n.t('common.confirm_delete')}</h3>
        <Button color="red" onclick={confirmAdminmod}>{i18n.t('common.yes')}</Button>
        <Button color="alternative" onclick={cancelAdminmod}>{i18n.t('common.no')}</Button>
    </div>
</Modal>
<div class="grid grid-cols-1 lg:grid-cols-2 gap-4 p-4 w-full">
    <Card size="xl" class="p-4 sm:p-6 text-gray-500 dark:text-gray-400 lg:col-span-2">
        <div class="flex justify-between mb-4">
            <h5 class="mb-5 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">{i18n.t('admin.groups.admins_title')}</h5>
            <Button class="h-10 w-10" size="xs" color="blue" onclick={() => addAdminModal = true}><Icon name="plus" /></Button>
        </div>
        <TableSearch placeholder={i18n.t('admin.groups.search_linux_id')} class="text-center" hoverable={true} bind:inputValue={searchAdminTerm}>
            <TableHead>
                <TableHeadCell width="15%">{i18n.t('admin.groups.admin_linux_id')}</TableHeadCell>
                <TableHeadCell>{i18n.t('admin.groups.group_names')}</TableHeadCell>
                <TableHeadCell width="100px">{i18n.t('common.actions')}</TableHeadCell>
            </TableHead>
            <TableBody class="divide-y">
                {#if filteredAdmins.length === 0}
                    <TableBodyRow>
                        <TableBodyCell colspan="4" class="text-center">{i18n.t('admin.groups.no_admins')}</TableBodyCell>
                    </TableBodyRow>
                {/if}
                {#each filteredAdmins as admin}
                    <TableBodyRow>
                        <TableBodyCell><Input type="text" bind:value={admin.linux_username} /></TableBodyCell>
                        <TableBodyCell><Input type="text" bind:value={admin.group_names} /></TableBodyCell>
                        <TableBodyCell>
                            <div class="flex gap-1">
                                <Button pill outline size="xs" color="blue" onclick={() => {editingAdmin = admin; removingAdmin = null; confirmAdminModal = true;}}>
                                    {i18n.t('common.apply')}
                                </Button>
                                <Button pill outline size="xs" color="red" onclick={() => {removingAdmin = admin; editingAdmin = null; confirmAdminModal = true;}}>
                                    {i18n.t('common.delete')}
                                </Button>
                            </div>
                        </TableBodyCell>
                    </TableBodyRow>
                {/each}
            </TableBody>
        </TableSearch>
    </Card>
    <Card size="xl" class="p-4 sm:p-6 text-gray-500 dark:text-gray-400 lg:col-span-2">
        <div class="flex justify-between mb-4">
            <h5 class="mb-5 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">{i18n.t('common.group_manage')}</h5>
            <Button class="h-10 w-10" size="xs" color="blue" onclick={() => addModal = true}><Icon name="plus" /></Button>
        </div>
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
                        <TableBodyCell><Input type="text" bind:value={group.name} /></TableBodyCell>
                        <TableBodyCell><Input type="text" bind:value={group.gid} /></TableBodyCell>
                        <TableBodyCell><Input type="text" bind:value={group.members} /></TableBodyCell>
                        <TableBodyCell>
                            <div class="flex gap-1">
                                <Button pill outline size="xs" color="blue" onclick={() => {editingGroup = group; removingGroup = null; confirmModal = true;}}>
                                    {i18n.t('common.apply')}
                                </Button>
                                <Button pill outline size="xs" color="red" onclick={() => {removingGroup = group; editingGroup = null; confirmModal = true;}}>
                                    {i18n.t('common.delete')}
                                </Button>
                            </div>
                        </TableBodyCell>
                    </TableBodyRow>
                {/each}
            </TableBody>
        </TableSearch>
    </Card>
</div>