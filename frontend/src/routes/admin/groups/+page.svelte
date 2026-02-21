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
    } from 'flowbite-svelte';
    import { ExclamationCircleOutline, PlusOutline } from 'flowbite-svelte-icons';
    import { invalidateAll } from '$app/navigation';
    import { enhance } from '$app/forms';

    export let data;

    let searchTerm = '';
    let searchAdminTerm = '';
    let groups = [];
    let admins = [];
    let filteredAdmins = [];
    let filteredGroups = [];
    let maxgid = 0;
    $: groups = data.groups;
    $: admins = data.admins;
    $: maxgid = groups.length?(Math.max(...groups.map(group => parseInt(group.gid))) + 1):1000;
    $: filteredGroups = groups.filter(group => 
        group.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
    $: filteredAdmins = admins.filter(admin => 
        admin.linux_username.toLowerCase().includes(searchAdminTerm.toLowerCase())
    );

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
            invalidateAll();
        }
    }

    function checkAdd() {
        return async ({result}) => {
            if (result.type === 'success') {
                invalidateAll();
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
            invalidateAll();
        }
    }

    function checkAddAdmin() {
        return async ({result}) => {
            if (result.type === 'success') {
                invalidateAll();
                addAdminModal = false;
            }
        }
    }

    function cancelAdminmod() {
        editingAdmin = null;
        removingAdmin = null;
    }

    let addModal = false;
    let confirmModal = false;
    let addAdminModal = false;
    let confirmAdminModal = false;
    let editingGroup = null;
    let removingGroup = null;
    let editingAdmin = null;
    let removingAdmin = null;
</script>

<Modal title="확인" bind:open={confirmModal} size="xs" autoclose>
    <div class="text-center">
        <ExclamationCircleOutline class="mx-auto mb-4 text-gray-400 w-12 h-12 dark:text-gray-200" />
        <h3 class="mb-5 text-lg font-normal text-gray-500 dark:text-gray-400">정말로 {editingGroup?"수정":"삭제"}할까요?</h3>
        <Button color="red" on:click={confirmGroupmod}>예</Button>
        <Button color="alternative" on:click={cancelGroupmod}>아니오</Button>
    </div>
</Modal>

<Modal title="그룹 추가" bind:open={addModal} size="xs">
    <form method="POST" action="?/groupadd" use:enhance={checkAdd}>
        <Table>
            <TableHead>
                <TableHeadCell>그룹명</TableHeadCell>
                <TableHeadCell>GID</TableHeadCell>
                <TableHeadCell>구성원</TableHeadCell>
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
            <Button color="blue" type="submit">확인</Button>
            <Button color="alternative" on:click={() => addModal = false}>취소</Button>
        </div>
    </form>
</Modal>
<Modal title="관리자 추가" bind:open={addAdminModal} size="xs">
    <form method="POST" action="?/adminpost" use:enhance={checkAddAdmin}>
        <Table>
            <TableHead>
                <TableHeadCell>관리자 리눅스 아이디</TableHeadCell>
                <TableHeadCell>그룹명 (쉼표로 구분)</TableHeadCell>
            </TableHead>
            <TableBody>
                <TableBodyRow>
                    <TableBodyCell><Input type="text" name="linux_username" /></TableBodyCell>
                    <TableBodyCell><Input type="text" name="group_names" /></TableBodyCell>
                </TableBodyRow>
            </TableBody>
        </Table>
        <div class="flex gap-1">
            <Button color="blue" type="submit">확인</Button>
            <Button color="alternative" on:click={() => addAdminModal = false}>취소</Button>
        </div>
    </form>
</Modal>

<Modal title="확인" bind:open={confirmAdminModal} size="xs" autoclose>
    <div class="text-center">
        <ExclamationCircleOutline class="mx-auto mb-4 text-gray-400 w-12 h-12 dark:text-gray-200" />
        <h3 class="mb-5 text-lg font-normal text-gray-500 dark:text-gray-400">정말로 {editingAdmin?"수정":"삭제"}할까요?</h3>
        <Button color="red" on:click={confirmAdminmod}>예</Button>
        <Button color="alternative" on:click={cancelAdminmod}>아니오</Button>
    </div>
</Modal>
<div class="grid grid-cols-1 lg:grid-cols-2 gap-4 p-4 w-full">
    <Card size="none" class="lg:col-span-2">
        <div class="flex justify-between mb-4">
            <h5 class="mb-5 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">그룹 관리자 관리</h5>
            <Button class="h-10 w-10" size="xs" color="blue" on:click={() => addAdminModal = true}><PlusOutline /></Button>
        </div>
        <TableSearch placeholder="리눅스 아이디로 검색" class="text-center" hoverable={true} bind:inputValue={searchAdminTerm}>
            <TableHead>
                <TableHeadCell width="15%">관리자 리눅스 아이디</TableHeadCell>
                <TableHeadCell>그룹명 (쉼표로 구분)</TableHeadCell>
                <TableHeadCell width="100px">작업</TableHeadCell>
            </TableHead>
            <TableBody tableBodyClass="divide-y">
                {#if filteredAdmins.length === 0}
                    <TableBodyRow>
                        <TableBodyCell colspan="4" class="text-center">관리자가 없습니다.</TableBodyCell>
                    </TableBodyRow>
                {/if}
                {#each filteredAdmins as admin}
                    <TableBodyRow>
                        <TableBodyCell><Input type="text" bind:value="{admin.linux_username}" /></TableBodyCell>
                        <TableBodyCell><Input type="text" bind:value="{admin.group_names}" /></TableBodyCell>
                        <TableBodyCell>
                            <div class="flex gap-1">
                                <Button pill outline size="xs" color="blue" on:click={() => {editingAdmin = admin; removingAdmin = null; confirmAdminModal = true;}}>
                                    적용
                                </Button>
                                <Button pill outline size="xs" color="red" on:click={() => {removingAdmin = admin; editingAdmin = null; confirmAdminModal = true;}}>
                                    삭제
                                </Button>
                            </div>
                        </TableBodyCell>
                    </TableBodyRow>
                {/each}
            </TableBody>
        </TableSearch>
    </Card>
    <Card size="none" class="lg:col-span-2">
        <div class="flex justify-between mb-4">
            <h5 class="mb-5 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">그룹 관리</h5>
            <Button class="h-10 w-10" size="xs" color="blue" on:click={() => addModal = true}><PlusOutline /></Button>
        </div>
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
                        <TableBodyCell><Input type="text" bind:value="{group.name}" /></TableBodyCell>
                        <TableBodyCell><Input type="text" bind:value="{group.gid}" /></TableBodyCell>
                        <TableBodyCell><Input type="text" bind:value="{group.members}" /></TableBodyCell>
                        <TableBodyCell>
                            <div class="flex gap-1">
                                <Button pill outline size="xs" color="blue" on:click={() => {editingGroup = group; removingGroup = null; confirmModal = true;}}>
                                    적용
                                </Button>
                                <Button pill outline size="xs" color="red" on:click={() => {removingGroup = group; editingGroup = null; confirmModal = true;}}>
                                    삭제
                                </Button>
                            </div>
                        </TableBodyCell>
                    </TableBodyRow>
                {/each}
            </TableBody>
        </TableSearch>
    </Card>
</div>