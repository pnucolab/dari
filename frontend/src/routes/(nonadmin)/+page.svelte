<script>
    import { get } from '#lib/translations.js';
    import { onMount } from 'svelte';
    import { formatDate } from '#lib/utils.js';
    import {
        Card,
        Table,
        TableHead,
        TableHeadCell,
        TableBody,
        TableBodyRow,
        TableBodyCell,
    } from '#lib/components/ui/index.js';

    const i18n = get();

    let logs = $state(null);

    onMount(() => {
        refreshLogs();
    });

    async function refreshLogs() {
        const response = await fetch('?/logs', {
            method: 'POST',
            'body': '' 
        });
        const result = await response.json();
        const result_json = JSON.parse(JSON.parse(result.data)[1]);
        logs = result_json.items || result_json;
    }
</script>

<div class="grid grid-cols-1 lg:grid-cols-2 gap-4 p-4 w-full">
    <Card size="xl" class="p-4 sm:p-6 text-gray-500 dark:text-gray-400">
        <h5 class="mb-4 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">{i18n.t('user.notice')}</h5>
        <div class="space-y-4">
            <div>
                <p class="mb-2 font-normal text-gray-700 dark:text-gray-400">
                    {@html i18n.t('user.notice_detail')}
                </p>
            </div>
            <div>
                <h6 class="mb-1 font-bold tracking-tight text-gray-900 dark:text-white">
                    {i18n.t('user.privacy_title')}
                </h6>
                <ul class="list-disc list-outside ml-8 mb-2">
                    <li>{@html i18n.t('user.privacy_1')}</li>
                    <li>{@html i18n.t('user.privacy_2')}</li>
                    <li>{@html i18n.t('user.privacy_3')}</li>
                </ul>
            </div>
        </div>
    </Card>

    <Card size="xl" class="p-4 sm:p-6 text-gray-500 dark:text-gray-400">
        <h5 class="mb-4 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">{i18n.t('user.shortcuts')}</h5>
        <h6 class="mb-1 font-bold tracking-tight text-gray-900 dark:text-white">
            {i18n.t('user.freqeuently_used')}
        </h6>
        <ul class="list-disc list-outside ml-8 mb-0">
            <li>{@html i18n.t('user.freqeuently_used_1')}</li>
        </ul>
        <h6 class="mt-3 mb-1 font-bold tracking-tight text-gray-900 dark:text-white">
            {i18n.t('user.usage')}
        </h6>
        <ul class="list-disc list-outside ml-8 mb-0">
            <li>{@html i18n.t('user.usage_1')}</li>
            <li>{@html i18n.t('user.usage_2')}</li>
            <li>{@html i18n.t('user.usage_3')}</li>
        </ul>
    </Card>

    <Card size="xl" class="p-4 sm:p-6 text-gray-500 dark:text-gray-400 lg:col-span-2">
        <h5 class="mb-5 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">{i18n.t('user.service_log')}</h5>
        <Table>
            <TableHead>
                <TableHeadCell width="150px" class="text-center">{i18n.t('user.service')}</TableHeadCell>
                <TableHeadCell>{i18n.t('user.log')}</TableHeadCell>
            </TableHead>
            <TableBody class="divide-y">
                {#if !logs}
                <TableBodyRow>
                    <TableBodyCell colspan="2" class="text-center">{i18n.t('user.log_loading')}</TableBodyCell>
                </TableBodyRow>
                {:else if logs.length === 0}
                <TableBodyRow>
                    <TableBodyCell colspan="2" class="text-center">{i18n.t('user.log_none')}</TableBodyCell>
                </TableBodyRow>
                {:else}
                {#each logs as log}
                <TableBodyRow>
                    <TableBodyCell class="text-center">{log.service}</TableBodyCell>
                    <TableBodyCell>[{formatDate(log.created_at)}] {log.content}</TableBodyCell>
                </TableBodyRow>
                {/each}
                {/if}
            </TableBody>
        </Table>      
    </Card>
</div>