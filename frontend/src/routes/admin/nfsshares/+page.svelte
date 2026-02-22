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
    } from 'flowbite-svelte';
    import { PlusOutline, TrashBinOutline } from 'flowbite-svelte-icons';
    import GroupSelector from '$lib/components/GroupSelector.svelte';
    import MultiSelect from '$lib/components/MultiSelect.svelte';

    import { onMount, onDestroy } from 'svelte';
    import { enhance } from '$app/forms';

    let shares = null;
    let servers = null;
    let allGroups = [];
    let dariHomeServer = null;
    let refreshInterval;

    let selectedAllowedServers = [];
    let selectedAllowedGroups = [];

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

    let shareModal = false;

    function openShareModal() {
        selectedAllowedServers = [];
        selectedAllowedGroups = [];
        shareModal = true;
    }

    export let form;

    function handleSubmit() {
        return async ({ result }) => {
            if (!result.error) {
                shareModal = false;
                refreshShares();
            }
        };
    }

    $: computeServers = servers ? servers.filter(s => s.server_type === 'compute') : [];
    $: storageServers = servers ? servers.filter(s => s.server_type === 'storage') : [];
    $: computeServerItems = computeServers.map(s => ({ name: `${s.domainname} (${s.ip})`, value: s.domainname }));
</script>

<form method="POST" action="?/create" use:enhance={handleSubmit}>
    <input type="hidden" name="allowed_groups" value={selectedAllowedGroups.join(', ')} />
    <input type="hidden" name="allowed_servers" value={selectedAllowedServers.join(', ')} />
    <Modal bind:open={shareModal} size="md" autoclose={false} class="w-full">
        <h3 class="mb-4 text-xl font-medium text-gray-900 dark:text-white">NFS 공유 추가</h3>
        <div class="flex gap-3 mb-3">
            <Label class="w-full space-y-2">
                <span>이름</span>
                <Input type="text" name="name" placeholder="shared-data" />
            </Label>
            <Label class="w-full space-y-2">
                <span>스토리지 서버</span>
                <Select name="server_ip">
                    <option value="" disabled selected>서버 선택</option>
                    {#each storageServers as srv}
                    <option value={srv.ip}>{srv.domainname} ({srv.ip})</option>
                    {/each}
                </Select>
            </Label>
        </div>
        <div class="flex gap-3 mb-3">
            <Label class="w-full space-y-2">
                <span>내보내기 경로</span>
                <Input type="text" name="export_path" placeholder="/export/data" />
            </Label>
            <Label class="w-full space-y-2">
                <span>마운트 경로</span>
                <Input type="text" name="mount_point" placeholder="/mnt/data" />
            </Label>
        </div>
        <div class="mb-3">
            <Label class="w-full space-y-2">
                <span>허용 그룹 (비워두면 전체 허용)</span>
                <GroupSelector groups={allGroups} bind:selected={selectedAllowedGroups} />
            </Label>
        </div>
        <div class="mb-5">
            <Label class="space-y-2">
                <span>허용 서버 (비워두면 전체 허용)</span>
            </Label>
            <div class="mt-2">
                <MultiSelect
                    items={computeServerItems}
                    bind:selected={selectedAllowedServers}
                    labelKey="name"
                    valueKey="value"
                    placeholder="서버 검색..."
                    emptyText="등록된 컴퓨트 서버가 없습니다."
                />
            </div>
            {#if form?.error}
            <Alert color="red" dismissable>NFS 공유를 설정하는 데 실패하였습니다.</Alert>
            {/if}
        </div>
        <svelte:fragment slot="footer">
            <Button color="blue" type="submit">추가</Button>
            <Button color="alternative" on:click={() => shareModal = false}>취소</Button>
        </svelte:fragment>
    </Modal>
</form>

<div class="grid grid-cols-1 gap-4 p-4 w-full">
    <Card size='none'>
        <div class="flex justify-between items-center mb-5">
            <h5 class="text-2xl font-bold tracking-tight text-gray-900 dark:text-white">홈 디렉토리 설정</h5>
        </div>
        <div class="flex items-center gap-3">
            <Label class="space-y-2 w-full max-w-md">
                <span>홈 디렉토리 서버 (dari-home 내보내기)</span>
                <Select on:change={setDariHome} value={dariHomeServer || ''}>
                    <option value="">선택 안 함</option>
                    {#each storageServers as srv}
                    <option value={srv.pk}>{srv.domainname} ({srv.ip})</option>
                    {/each}
                </Select>
            </Label>
        </div>
    </Card>
    <Card size='none'>
        <div class="flex justify-between">
            <h5 class="mb-5 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">NFS 공유 관리</h5>
            <Button class="h-10 w-10" size="xs" color="blue" on:click={openShareModal}><PlusOutline /></Button>
        </div>
        <Table class="text-center">
            <TableHead>
                <TableHeadCell>이름</TableHeadCell>
                <TableHeadCell>NFS 서버 IP</TableHeadCell>
                <TableHeadCell>내보내기 경로</TableHeadCell>
                <TableHeadCell>마운트 경로</TableHeadCell>
                <TableHeadCell>허용 그룹</TableHeadCell>
                <TableHeadCell>허용 서버</TableHeadCell>
                <TableHeadCell width="100px">작업</TableHeadCell>
            </TableHead>
            <TableBody tableBodyClass="divide-y">
                {#if !shares}
                <TableBodyRow>
                    <TableBodyCell colspan="7" class="text-center">NFS 공유 정보를 불러오는 중입니다...</TableBodyCell>
                </TableBodyRow>
                {:else if shares.length === 0}
                <TableBodyRow>
                    <TableBodyCell colspan="7" class="text-center">등록된 NFS 공유가 없습니다.</TableBodyCell>
                </TableBodyRow>
                {:else}
                {#each shares as share}
                <TableBodyRow>
                    <TableBodyCell>{share.name}</TableBodyCell>
                    <TableBodyCell>{share.server_ip}</TableBodyCell>
                    <TableBodyCell><code>{share.export_path}</code></TableBodyCell>
                    <TableBodyCell><code>{share.mount_point}</code></TableBodyCell>
                    <TableBodyCell>{share.allowed_groups && share.allowed_groups.length > 0 ? share.allowed_groups.join(', ') : '전체'}</TableBodyCell>
                    <TableBodyCell>{share.allowed_servers && share.allowed_servers.length > 0 ? share.allowed_servers.join(', ') : '전체'}</TableBodyCell>
                    <TableBodyCell>
                        <Button outline size="sm" color={null} on:click={() => deleteShare(share.pk)}><TrashBinOutline class="w-4 h-4" /></Button>
                    </TableBodyCell>
                </TableBodyRow>
                {/each}
                {/if}
            </TableBody>
        </Table>
    </Card>
</div>
