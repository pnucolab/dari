<script>
    import {
        Card,
        Table,
        TableHead,
        TableHeadCell,
        TableBody,
        TableBodyRow,
        TableBodyCell,
        Button,
    } from 'flowbite-svelte';
    import { ChevronLeftOutline, ChevronRightOutline } from 'flowbite-svelte-icons';

    import { onMount, onDestroy } from 'svelte';
    import { formatDate } from '$lib/utils';

    let logs = null;
    let total = 0;
    let currentPage = 1;
    let perPage = 20;
    let refreshInterval;

    $: totalPages = Math.ceil(total / perPage);

    onMount(() => {
        refreshLogs();
        refreshInterval = setInterval(refreshLogs, 10000);
    });

    onDestroy(() => {
        if (refreshInterval) clearInterval(refreshInterval);
    });

    async function refreshLogs() {
        let formData = new FormData();
        formData.append('page', currentPage);
        formData.append('per_page', perPage);
        const response = await fetch('?/logs', {
            method: 'POST',
            'body': formData
        });
        const result = await response.json();
        const result_json = JSON.parse(JSON.parse(result.data)[1]);
        logs = result_json.items || [];
        total = result_json.total || 0;
    }

    function goToPage(page) {
        if (page < 1 || page > totalPages) return;
        currentPage = page;
        refreshLogs();
    }
</script>

<div class="grid grid-cols-1 gap-4 p-4 w-full">
    <Card size='none'>
        <div class="flex justify-between items-center mb-5">
            <h5 class="text-2xl font-bold tracking-tight text-gray-900 dark:text-white">서비스 접속 기록</h5>
            {#if total > 0}
            <span class="text-sm text-gray-500">총 {total}건</span>
            {/if}
        </div>
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
        {#if totalPages > 1}
        <div class="flex justify-center items-center gap-2 mt-4">
            <Button outline size="sm" color="alternative" disabled={currentPage <= 1} on:click={() => goToPage(currentPage - 1)}>
                <ChevronLeftOutline class="w-4 h-4" />
            </Button>
            {#each Array(totalPages) as _, i}
                {#if totalPages <= 7 || i === 0 || i === totalPages - 1 || (i >= currentPage - 2 && i <= currentPage)}
                <Button size="sm" color={currentPage === i + 1 ? 'blue' : 'alternative'} outline={currentPage !== i + 1} on:click={() => goToPage(i + 1)}>
                    {i + 1}
                </Button>
                {:else if i === currentPage - 3 || i === currentPage + 1}
                <span class="text-gray-400">...</span>
                {/if}
            {/each}
            <Button outline size="sm" color="alternative" disabled={currentPage >= totalPages} on:click={() => goToPage(currentPage + 1)}>
                <ChevronRightOutline class="w-4 h-4" />
            </Button>
        </div>
        {/if}
    </Card>
</div>
