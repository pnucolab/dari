<script>
    import {
        Card,
        Table,
        TableHead,
        TableHeadCell,
        TableBody,
        TableBodyRow,
        TableBodyCell,
        List,
        Li,
        Modal,
        Label,
        Input,
        Button,
        Alert,
    } from 'flowbite-svelte';
    import { PlusOutline, TrashBinOutline } from 'flowbite-svelte-icons';

    import { onMount, onDestroy } from 'svelte';
    import { enhance } from '$app/forms';
    import { formatDate } from '$lib/utils';

    let servers = null;
    let logs = null;
    let refreshInterval_servers;
    let refreshInterval_logs;

    onMount(() => {
        refreshServerStatus();
        refreshLogs();
        refreshInterval_servers = setInterval(refreshServerStatus, 5000);
        refreshInterval_logs = setInterval(refreshLogs, 5000);
    });

    onDestroy(() => {
        if (refreshInterval_servers) clearInterval(refreshInterval_servers);
        if (refreshInterval_logs) clearInterval(refreshInterval_logs);
    });

    async function refreshServerStatus() {
        const response = await fetch('?/servers', {
            method: 'POST',
            'body': '' 
        });
        const result = await response.json();
        const result_json = JSON.parse(JSON.parse(result.data)[1]);
        servers = result_json;
    }

    async function refreshLogs() {
        const response = await fetch('?/logs', {
            method: 'POST',
            'body': '' 
        });
        const result = await response.json();
        const result_json = JSON.parse(JSON.parse(result.data)[1]);
        logs = result_json;
    }

    async function deleteServer(domainname) {
        let formData = new FormData();
        formData.append('domainname', domainname);
        const response = await fetch('?/serverdelete', {
            method: 'POST',
            'body': formData
        });
        refreshServerStatus();
    }

    let serverModal = false;
    let serverModifying = false;

    export let form;

    function handleSubmit() {
        return async ({ result }) => {
            if (!result.error) {
                serverModal = false;
                refreshServerStatus();
            }
        };
    }
</script>

<form method="POST" action="?/server" use:enhance={handleSubmit}>
    <Modal bind:open={serverModal} size="md" autoclose={false} class="w-full">
        <h3 class="mb-4 text-xl font-medium text-gray-900 dark:text-white">서버 {serverModifying?"변경":"추가"}</h3>
        <div class="flex gap-3 mb-3">
            <Label class="w-full space-y-2">
                <span>도메인네임</span>
                <Input type="text" name="domainname" />
            </Label>
            <Label class="w-full space-y-2">
                <span>IP</span>
                <Input type="text" name="ip" />
            </Label>
            <Label class="space-y-2" style="min-width:100px">
                <span>SSH 포트</span>
                <Input type="number" name="port" placeholder="22" />
            </Label>
        </div>
        <div class="mb-5">
            <Label class="w-full space-y-2">
                <span>허용 그룹 (쉼표 구분, 비워두면 전체 허용)</span>
                <Input type="text" name="allowed_groups" placeholder="group1, group2, ..." />
            </Label>
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

<div class="grid grid-cols-1 lg:grid-cols-2 gap-4 p-4 w-full">
    <Card size='none' class="lg:col-span-2">
        <div class="flex justify-between">
            <h5 class="mb-5 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">서버 상태</h5>
            <Button class="h-10 w-10" size="xs" color="blue" on:click={() => serverModal = true}><PlusOutline /></Button>
        </div>
        <Table class="text-center">
            <TableHead>
                <TableHeadCell>도메인네임</TableHeadCell>
                <TableHeadCell>IP</TableHeadCell>
                <TableHeadCell>SSH 포트</TableHeadCell>
                <TableHeadCell>허용 그룹</TableHeadCell>
                <TableHeadCell>온도</TableHeadCell>
                <TableHeadCell>CPU 점유율</TableHeadCell>
                <TableHeadCell>메모리 사용량</TableHeadCell>
                <TableHeadCell width="100px">작업</TableHeadCell>
            </TableHead>
            <TableBody tableBodyClass="divide-y">
                {#if !servers}
                <TableBodyRow>
                    <TableBodyCell colspan="8" class="text-center">서버 정보를 불러오는 중입니다...</TableBodyCell>
                </TableBodyRow>
                {:else if servers.length === 0}
                <TableBodyRow>
                    <TableBodyCell colspan="8" class="text-center">등록된 서버가 없습니다.</TableBodyCell>
                </TableBodyRow>
                {:else}
                {#each servers as server}
                <TableBodyRow>
                    <TableBodyCell>{server.domainname}</TableBodyCell>
                    <TableBodyCell>{server.ip}</TableBodyCell>
                    <TableBodyCell>{server.port || '-'}</TableBodyCell>
                    <TableBodyCell>{server.allowed_groups && server.allowed_groups.length > 0 ? server.allowed_groups.join(', ') : '전체'}</TableBodyCell>
                    {#if server.stats}
                    <TableBodyCell>{server.stats.t}</TableBodyCell>
                    <TableBodyCell>{server.stats.c}</TableBodyCell>
                    <TableBodyCell>{server.stats.m}</TableBodyCell>
                    {:else}
                    <TableBodyCell colspan="3" class="text-center">정보 없음</TableBodyCell>
                    {/if}
                    <TableBodyCell>
                        <Button outline size="sm" color={null} on:click={() => deleteServer(server.domainname)}><TrashBinOutline class="w-4 h-4" /></Button>
                    </TableBodyCell>
                </TableBodyRow>
                {/each}
                {/if}
            </TableBody>
        </Table>
    </Card>
    <Card size='none' class="lg:col-span-2">
        <h5 class="mb-5 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">서비스 접속 기록 (마지막 20개)</h5>
        <Table>
            <TableHead>
                <TableHeadCell width="200px" class="text-center">아이디<br>(이름)</TableHeadCell>
                <TableHeadCell width="150px" class="text-center">서비스</TableHeadCell>
                <TableHeadCell>접속 기록</TableHeadCell>
            </TableHead>
            <TableBody tableBodyClass="divide-y">
                {#if !logs}
                <TableBodyRow>
                    <TableBodyCell colspan="3" class="text-center">로그를 불러오는 중입니다...</TableBodyCell>
                </TableBodyRow>
                {:else if logs.length === 0}
                <TableBodyRow>
                    <TableBodyCell colspan="3" class="text-center">로그가 없습니다.</TableBodyCell>
                </TableBodyRow>
                {:else}
                {#each logs as log}
                <TableBodyRow>
                    <TableBodyCell class="text-center">{log.username}<br>({log.name})</TableBodyCell>
                    <TableBodyCell class="text-center">{log.service}</TableBodyCell>
                    <TableBodyCell>[{formatDate(log.created_at)}] {log.content}</TableBodyCell>
                </TableBodyRow>
                {/each}
                {/if}
            </TableBody>
        </Table>
    </Card>
</div>
