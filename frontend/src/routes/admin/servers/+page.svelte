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
    } from 'flowbite-svelte';
    import { PlusOutline, TrashBinOutline, EditOutline } from 'flowbite-svelte-icons';
    import GroupSelector from '$lib/components/GroupSelector.svelte';

    import { onMount, onDestroy } from 'svelte';
    import { enhance } from '$app/forms';

    let servers = null;
    let stats = {};
    let allGroups = [];
    let refreshInterval;

    let addServerType = 'compute';
    let serverModal = false;
    let serverModifying = false;

    let editPk = '';
    let editDomainname = '';
    let editIp = '';
    let editPort = '';
    let editAllowedGroups = [];

    let apiKeyModal = false;
    let apiKeyValue = '';

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

    export let form;

    function handleSubmit() {
        return async ({ result }) => {
            if (!result.error) {
                serverModal = false;
                refreshServers();
            }
        };
    }

    $: computeServers = servers ? servers.filter(s => s.server_type === 'compute') : null;
    $: storageServers = servers ? servers.filter(s => s.server_type === 'storage') : null;
</script>

<form method="POST" action="?/server" use:enhance={handleSubmit}>
    <input type="hidden" name="server_type" value={addServerType} />
    <input type="hidden" name="allowed_groups" value={editAllowedGroups.join(', ')} />
    {#if serverModifying}<input type="hidden" name="pk" value={editPk} />{/if}
    <Modal bind:open={serverModal} size="md" autoclose={false} class="w-full">
        <h3 class="mb-4 text-xl font-medium text-gray-900 dark:text-white">{addServerType === 'storage' ? '스토리지' : '컴퓨트'} 서버 {serverModifying?"변경":"추가"}</h3>
        <div class="flex gap-3 mb-3">
            <Label class="w-full space-y-2">
                <span>도메인네임</span>
                <Input type="text" name="domainname" bind:value={editDomainname} />
            </Label>
            <Label class="w-full space-y-2">
                <span>IP</span>
                <Input type="text" name="ip" bind:value={editIp} />
            </Label>
            {#if addServerType === 'compute'}
            <Label class="space-y-2" style="min-width:100px">
                <span>SSH 포트</span>
                <Input type="number" name="port" placeholder="22" bind:value={editPort} />
            </Label>
            {/if}
        </div>
        {#if addServerType === 'compute'}
        <div class="mb-3">
            <Label class="w-full space-y-2">
                <span>허용 그룹 (비워두면 전체 허용)</span>
                <GroupSelector groups={allGroups} bind:selected={editAllowedGroups} />
            </Label>
        </div>
        {/if}
        <div class="mb-5">
            {#if form?.error}
            <Alert color="red" dismissable>서버 정보를 설정하는 데 실패하였습니다.</Alert>
            {/if}
        </div>
        <svelte:fragment slot="footer">
            <Button color="blue" type="submit">{serverModifying?"변경":"추가"}</Button>
            <Button color="alternative" on:click={() => serverModal = false}>취소</Button>
        </svelte:fragment>
    </Modal>
</form>

<div class="grid grid-cols-1 gap-4 p-4 w-full">
    <Card size='none'>
        <div class="flex justify-between">
            <h5 class="mb-5 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">컴퓨트 서버</h5>
            <Button class="h-10 w-10" size="xs" color="blue" on:click={() => openAddModal('compute')}><PlusOutline /></Button>
        </div>
        <Table class="text-center">
            <TableHead>
                <TableHeadCell>도메인네임</TableHeadCell>
                <TableHeadCell>IP</TableHeadCell>
                <TableHeadCell>SSH 포트</TableHeadCell>
                <TableHeadCell>허용 그룹</TableHeadCell>
                <TableHeadCell>API 키</TableHeadCell>
                <TableHeadCell>온도</TableHeadCell>
                <TableHeadCell>CPU 점유율</TableHeadCell>
                <TableHeadCell>메모리 사용량</TableHeadCell>
                <TableHeadCell width="100px">작업</TableHeadCell>
            </TableHead>
            <TableBody tableBodyClass="divide-y">
                {#if !computeServers}
                <TableBodyRow>
                    <TableBodyCell colspan="9" class="text-center">서버 정보를 불러오는 중입니다...</TableBodyCell>
                </TableBodyRow>
                {:else if computeServers.length === 0}
                <TableBodyRow>
                    <TableBodyCell colspan="9" class="text-center">등록된 컴퓨트 서버가 없습니다.</TableBodyCell>
                </TableBodyRow>
                {:else}
                {#each computeServers as server}
                <TableBodyRow>
                    <TableBodyCell>{server.domainname}</TableBodyCell>
                    <TableBodyCell>{server.ip}</TableBodyCell>
                    <TableBodyCell>{server.port || '-'}</TableBodyCell>
                    <TableBodyCell>{server.allowed_groups && server.allowed_groups.length > 0 ? server.allowed_groups.join(', ') : '전체'}</TableBodyCell>
                    <TableBodyCell><button type="button" class="text-xs cursor-pointer hover:underline" on:click={() => showApiKey(server.api_key)}>{server.api_key ? server.api_key.substring(0, 8) + '...' : '-'}</button></TableBodyCell>
                    {#if stats[server.pk]}
                    <TableBodyCell>{stats[server.pk].t}</TableBodyCell>
                    <TableBodyCell>{stats[server.pk].c}</TableBodyCell>
                    <TableBodyCell>{stats[server.pk].m}</TableBodyCell>
                    {:else}
                    <TableBodyCell colspan="3" class="text-center">정보 없음</TableBodyCell>
                    {/if}
                    <TableBodyCell>
                        <div class="flex gap-1 justify-center">
                            <Button outline size="sm" color={null} on:click={() => openEditModal(server)}><EditOutline class="w-4 h-4" /></Button>
                            <Button outline size="sm" color={null} on:click={() => deleteServer(server.pk)}><TrashBinOutline class="w-4 h-4" /></Button>
                        </div>
                    </TableBodyCell>
                </TableBodyRow>
                {/each}
                {/if}
            </TableBody>
        </Table>
    </Card>
    <Card size='none'>
        <div class="flex justify-between">
            <h5 class="mb-5 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">스토리지 서버</h5>
            <Button class="h-10 w-10" size="xs" color="blue" on:click={() => openAddModal('storage')}><PlusOutline /></Button>
        </div>
        <Table class="text-center">
            <TableHead>
                <TableHeadCell>도메인네임</TableHeadCell>
                <TableHeadCell>IP</TableHeadCell>
                <TableHeadCell>API 키</TableHeadCell>
                <TableHeadCell>온도</TableHeadCell>
                <TableHeadCell>CPU 점유율</TableHeadCell>
                <TableHeadCell>메모리 사용량</TableHeadCell>
                <TableHeadCell width="100px">작업</TableHeadCell>
            </TableHead>
            <TableBody tableBodyClass="divide-y">
                {#if !storageServers}
                <TableBodyRow>
                    <TableBodyCell colspan="7" class="text-center">서버 정보를 불러오는 중입니다...</TableBodyCell>
                </TableBodyRow>
                {:else if storageServers.length === 0}
                <TableBodyRow>
                    <TableBodyCell colspan="7" class="text-center">등록된 스토리지 서버가 없습니다.</TableBodyCell>
                </TableBodyRow>
                {:else}
                {#each storageServers as server}
                <TableBodyRow>
                    <TableBodyCell>{server.domainname}</TableBodyCell>
                    <TableBodyCell>{server.ip}</TableBodyCell>
                    <TableBodyCell><button type="button" class="text-xs cursor-pointer hover:underline" on:click={() => showApiKey(server.api_key)}>{server.api_key ? server.api_key.substring(0, 8) + '...' : '-'}</button></TableBodyCell>
                    {#if stats[server.pk]}
                    <TableBodyCell>{stats[server.pk].t}</TableBodyCell>
                    <TableBodyCell>{stats[server.pk].c}</TableBodyCell>
                    <TableBodyCell>{stats[server.pk].m}</TableBodyCell>
                    {:else}
                    <TableBodyCell colspan="3" class="text-center">정보 없음</TableBodyCell>
                    {/if}
                    <TableBodyCell>
                        <div class="flex gap-1 justify-center">
                            <Button outline size="sm" color={null} on:click={() => openEditModal(server)}><EditOutline class="w-4 h-4" /></Button>
                            <Button outline size="sm" color={null} on:click={() => deleteServer(server.pk)}><TrashBinOutline class="w-4 h-4" /></Button>
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
    <h3 class="mb-4 text-xl font-medium text-gray-900 dark:text-white">API 키</h3>
    <code class="block w-full p-3 text-sm bg-gray-100 dark:bg-gray-800 rounded-lg break-all select-all">{apiKeyValue}</code>
    <svelte:fragment slot="footer">
        <Button color="blue" on:click={copyApiKey}>복사</Button>
        <Button color="alternative" on:click={() => apiKeyModal = false}>닫기</Button>
    </svelte:fragment>
</Modal>
