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
    } from 'flowbite-svelte';
    import { ExclamationCircleOutline } from 'flowbite-svelte-icons';
    import { invalidateAll } from '$app/navigation';

    export let data;

    let searchTerm = '';
    let groups = [];
    let maxgid = 0;
    $: groups = data.groups;
    $: maxgid = groups.length?(Math.max(...groups.map(group => parseInt(group.gid))) + 1):1000;
    $: filteredGroups = groups.filter(group => 
        group.name.toLowerCase().includes(searchTerm.toLowerCase())
    );

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
            invalidateAll();
        }
    }

    function cancelGroupmod() {
        editingGroup = null;
    }

    let confirmModal = false;
    let editingGroup = null;
</script>

<Modal title="확인" bind:open={confirmModal} size="xs" autoclose>
    <div class="text-center">
        <ExclamationCircleOutline class="mx-auto mb-4 text-gray-400 w-12 h-12 dark:text-gray-200" />
        <h3 class="mb-5 text-lg font-normal text-gray-500 dark:text-gray-400">정말로 수정할까요?</h3>
        <Button color="red" on:click={confirmGroupmod}>예</Button>
        <Button color="alternative" on:click={cancelGroupmod}>아니오</Button>
    </div>
</Modal>

<div class="grid grid-cols-1 lg:grid-cols-2 gap-4 p-4 w-full">
    <Card size="none" class="lg:col-span-2">
        <TableSearch placeholder="그룹명으로 검색" class="text-center" hoverable={true} bind:inputValue={searchTerm}>
            <TableHead>
                <TableHeadCell width="15%">그룹명</TableHeadCell>
                <TableHeadCell width="15%">GID</TableHeadCell>
                <TableHeadCell>구성원</TableHeadCell>
                <TableHeadCell width="100px">작업</TableHeadCell>
            </TableHead>
            <TableBody tableBodyClass="divide-y">
                {#if filteredGroups.length === 0}
                    <TableBodyRow>
                        <TableBodyCell colspan="4" class="text-center">그룹이 없습니다.</TableBodyCell>
                    </TableBodyRow>
                {/if}
                {#each filteredGroups as group}
                    <TableBodyRow>
                        <TableBodyCell>{group.name}</TableBodyCell>
                        <TableBodyCell>{group.gid}</TableBodyCell>
                        <TableBodyCell><Input type="text" bind:value="{group.members}" /></TableBodyCell>
                        <TableBodyCell>
                            <Button pill outline size="xs" color="blue" on:click={() => {editingGroup = group; confirmModal = true;}}>
                                적용
                            </Button>
                        </TableBodyCell>
                    </TableBodyRow>
                {/each}
            </TableBody>
        </TableSearch>
    </Card>
</div>