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
        Checkbox,
        Button,
        Pagination,
        PaginationItem,
        Modal,
        Label,
        P,
    } from 'flowbite-svelte';
    import {
        PenOutline,
        EditOutline,
        CheckOutline,
        CheckPlusCircleOutline,
        ExclamationCircleOutline,
        BanOutline,
        TrashBinOutline,
        PlusOutline,
    } from 'flowbite-svelte-icons';
    import { enhance } from '$app/forms';
    import { invalidateAll } from '$app/navigation';

    export let data;

    let users = [];
    $: {
        users = data.users.map(user => {
            user.vpn = user.vpn ? true : false;
            return user;
        });
        guests = data.guests.map(user => {
            user.vpn = user.vpn ? true : false;
            return user;
        });
        deactivated = data.deactivated;
    }
    let guests = [];
    let deactivated = [];

    let searchTerm1 = '';
    let searchTerm2 = '';
    let searchTerm3 = '';
    let filteredUsers1 = [];
    let filteredUsers2 = [];
    let filteredUsers3 = [];

    $: {
        filteredUsers1 = users.filter(user => 
            !user.username.startsWith('guest') &&
            (user.username.includes(searchTerm1) || user.profile.name.toLowerCase().includes(searchTerm1.toLowerCase()))
        );
        filteredUsers2 = guests.filter(user => 
            user.username.startsWith('guest') &&
            user.profile.name.toLowerCase().includes(searchTerm2.toLowerCase())
        );
        filteredUsers3 = deactivated.filter(user => 
            !user.is_active &&
            ((user.username && user.username.includes(searchTerm3)) ||
            user.profile.name.toLowerCase().includes(searchTerm3.toLowerCase()))
        );
    }

    let editingUser = null;
    let editingGuest = null;
    let userModal = false;
    let guestModal = false;
    let ldapModal = false;

    $: if (!userModal) editingUser = null;
    $: if (!guestModal) editingGuest = null;
    
    function setEditingUser(user) {
        editingUser = { ...user };
        userModal = true;
    }

    function setEditingGuest(user) {
        editingGuest = { ...user };
        guestModal = true;
    }

    function saveUsermod() {
        userModal = false;
        invalidateAll();
    }

    function saveGuestmod() {
        guestModal = false;
        invalidateAll();
    }

    function ldapFinished() {
        ldapModal = false;
    }
    
    async function deactivateUser(user) {
        let formData = new FormData();
        formData.append('username', user.username);
        let response = await fetch('?/deactivate', {
            method: 'POST',
            body: formData,
        });
        if (response.ok) {
            invalidateAll();
        }
    }

    async function activateUser(user) {
        let formData = new FormData();
        formData.append('username', user.username);
        let response = await fetch('?/activate', {
            method: 'POST',
            body: formData,
        });
        if (response.ok) {
            invalidateAll();
        }
    }

    async function deleteUser(user) {
        let formData = new FormData();
        formData.append('username', user.username);
        let response = await fetch('?/delete', {
            method: 'POST',
            body: formData,
        });
        if (response.ok) {
            invalidateAll();
        }
    }

    let deleteModal = false;
</script>

<form method="POST" action="?/ldap" enhance={ldapFinished}>
    <Modal bind:open={ldapModal} class="w-full">
        <h3 class="mb-4 text-xl font-medium text-gray-900 dark:text-white">LDAP 리빌딩</h3>
        <P>LDAP 데이터베이스를 리빌딩하시겠습니까?</P>
        <svelte:fragment slot="footer">
            <Button color="red" type="submit">리빌딩</Button>
            <Button color="alternative" on:click={() => {ldapModal = false;}}>취소</Button>
        </svelte:fragment>
    </Modal>
</form>

<form method="POST" action="?/{editingGuest?'guest':'guestnew'}" enhance={saveGuestmod}>
    <Modal bind:open={guestModal} size="lg" class="w-full">
        <h3 class="mb-4 text-xl font-medium text-gray-900 dark:text-white">기본 정보</h3>
        <div class="flex gap-3 mb-5">
            <Label class="w-full space-y-2">
                <span>로그인 비밀번호</span>
                <Input type="password" name="pw" placeholder="{editingGuest?'•••••••••••':''}" />
            </Label>
            <Label class="w-full space-y-2">
                <span>이름</span>
                <Input type="text" name="name" value="{editingGuest?editingGuest.profile.name:''}" />
            </Label>
            <Label class="w-full space-y-2">
                <span>소속기관</span>
                <Input type="text" name="institute" value="{editingGuest?editingGuest.guestinfo.institute:''}" />
            </Label>
        </div>
        <div class="flex gap-3 mb-5">
            <Label class="w-full space-y-2">
                <span>생년월일</span>
                <Input type="date" name="date_of_birth" value="{editingGuest?editingGuest.guestinfo.date_of_birth:''}" />
            </Label>
            <Label class="w-full space-y-2">
                <span>보증인</span>
                <Input type="text" name="reference" value="{editingGuest?editingGuest.guestinfo.reference:''}" />
            </Label>
            <Label class="w-full space-y-2">
                <span>휴대전화</span>
                <Input type="text" name="mobile" value="{editingGuest?editingGuest.guestinfo.mobile:''}" />
            </Label>
        </div>
        <br>
        <h3 class="mb-4 text-xl font-medium text-gray-900 dark:text-white">리눅스 계정 정보</h3>
        <div class="flex gap-3 mb-5">
            {#if editingGuest && editingGuest.linux}
            <Label class="w-full space-y-2">
                <span>아이디</span>
                <Input type="text" name="username" value={editingGuest.linux.username} />
            </Label>
            <Label class="w-full space-y-2">
                <span>UID</span>
                <Input type="text" name="uid" value={editingGuest.linux.uid} />
            </Label>
            <Label class="w-full space-y-2">
                <span>기본 그룹</span>
                <Input type="text" name="group" value={editingGuest.linux.group.name} />
            </Label>
            {:else}
            <P>리눅스 계정이 없습니다.</P>
            {/if}
        </div>
        <h3 class="mb-4 text-xl font-medium text-gray-900 dark:text-white">기타 정보</h3>
        <Table class="text-center mb-5" hoverable={true}>
            <TableHead>
                <TableHeadCell>이메일</TableHeadCell>
                {#if editingGuest}
                <TableHeadCell>OTP</TableHeadCell>
                {/if}
                <TableHeadCell>계정 만료일</TableHeadCell>
            </TableHead>
            <TableBody tableBodyClass="divide-y">
                <TableBodyCell>
                    <Input type="email" name="email" value={editingGuest?editingGuest.email:""} />
                </TableBodyCell>
                {#if editingGuest}
                <TableBodyCell>
                    <Checkbox name="otp" class="mx-auto" color="blue" bind:checked={editingGuest.vpn} />
                    <Input type="hidden" name="otp" value={editingGuest.vpn} />
                </TableBodyCell>
                {/if}
                <TableBodyCell>
                    <Input type="date" name="date_expire" value={editingGuest?editingGuest.profile.date_expire:''} />
                </TableBodyCell>
            </TableBody>
        </Table>
        <Input type="hidden" name="username" value={editingGuest?editingGuest.username:""} />
        <svelte:fragment slot="footer">
            <Button color="blue" type="submit">저장</Button>
            <Button color="alternative" on:click={() => {guestModal = false;}}>취소</Button>
        </svelte:fragment>
    </Modal>
</form>

<form method="POST" action="?/user" enhance={saveUsermod}>
    <Modal bind:open={userModal} size="lg" class="w-full">
        <h3 class="mb-4 text-xl font-medium text-gray-900 dark:text-white">기본 정보</h3>
        <Table class="text-center mb-5" hoverable={true}>
            <TableHead>
                <TableHeadCell>아이디</TableHeadCell>
                <TableHeadCell>이름</TableHeadCell>
                <TableHeadCell>구분</TableHeadCell>
            </TableHead>
            <TableBody tableBodyClass="divide-y">
                    <TableBodyRow>
                        <TableBodyCell>{editingUser.username}</TableBodyCell>
                        <TableBodyCell>{editingUser.profile.name}</TableBodyCell>
                        <TableBodyCell>{editingUser.profile.sta}</TableBodyCell>
                    </TableBodyRow>
            </TableBody>
        </Table>
        <h3 class="mb-4 text-xl font-medium text-gray-900 dark:text-white">리눅스 계정 정보</h3>
        <div class="flex gap-3 mb-5">
            {#if editingUser.linux}
            <Label class="w-full space-y-2">
                <span>아이디</span>
                <Input type="text" name="linuxid" value={editingUser.linux.username} />
            </Label>
            <Label class="w-full space-y-2">
                <span>UID</span>
                <Input type="text" name="linuxuid" value={editingUser.linux.uid} />
            </Label>
            <Label class="w-full space-y-2">
                <span>기본 그룹</span>
                <Input type="text" name="linuxgroup" value={editingUser.linux.group.name} />
            </Label>
            {:else}
            <P>리눅스 계정이 없습니다.</P>
            {/if}
        </div>
        <h3 class="mb-4 text-xl font-medium text-gray-900 dark:text-white">기타 정보</h3>
        <Table class="text-center mb-5" hoverable={true}>
            <TableHead>
                <TableHeadCell>이메일</TableHeadCell>
                <TableHeadCell>관리자</TableHeadCell>
                <TableHeadCell>OTP</TableHeadCell>
                <TableHeadCell>계정 만료일</TableHeadCell>
            </TableHead>
            <TableBody tableBodyClass="divide-y">
                <TableBodyCell>
                    <Input type="email" name="email" value={editingUser.email} />
                </TableBodyCell>
                <TableBodyCell>
                    <Checkbox class="mx-auto" color="blue" bind:checked={editingUser.is_staff} />
                    <Input type="hidden" name="staff" value={editingUser.is_staff} />
                </TableBodyCell>
                <TableBodyCell>
                    <Checkbox class="mx-auto" color="blue" bind:checked={editingUser.vpn} />
                    <Input type="hidden" name="otp" value={editingUser.vpn} />
                </TableBodyCell>
                <TableBodyCell>
                    <Input type="date" name="date_expire" value={editingUser.profile.date_expire} />
                </TableBodyCell>
            </TableBody>
        </Table>
        <Input type="hidden" name="username" value={editingUser.username} />
        <svelte:fragment slot="footer">
            <Button color="blue" type="submit">저장</Button>
            <Button color="alternative" on:click={() => {userModal = false;}}>취소</Button>
        </svelte:fragment>
    </Modal>
</form>

<div class="grid grid-cols-1 lg:grid-cols-2 gap-4 p-4 w-full">
    <Card size="none" class="lg:col-span-2">
        <form method="POST" action="?/transfer" enhance={invalidateAll}>
            <h5 class="mb-5 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">사용자 정보 이전</h5>
            <Table class="text-center mb-5" hoverable={true}>
                <TableHead>
                    <TableHeadCell>이전될 사용자의 아이디</TableHeadCell>
                    <TableHeadCell>새로운 사용자의 아이디</TableHeadCell>
                    <TableHeadCell width="10%" style="min-width:80px">작업</TableHeadCell>
                </TableHead>
                <TableBody tableBodyClass="divide-y">
                    <TableBodyRow>
                        <TableBodyCell><Input type="text" name="username_from" /></TableBodyCell>
                        <TableBodyCell><Input type="text" name="username_to" /></TableBodyCell>
                        <TableBodyCell><Button color="blue" type="submit">이전하기</Button></TableBodyCell>
                    </TableBodyRow>
                </TableBody>
            </Table>
        </form>
    </Card>
    <Card size="none" class="lg:col-span-2">
        <div class="flex justify-between">
            <h5 class="mb-5 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">사용자 관리</h5>
            <Button class="h-10 w-24" size="xs" color="red" on:click={() => ldapModal = true}>LDAP 리빌딩</Button>
        </div>
        <TableSearch placeholder="이름 또는 아이디로 검색" class="text-center" hoverable={true} bind:inputValue={searchTerm1}>
            <TableHead>
                <TableHeadCell width="10%" style="min-width:150px">아이디</TableHeadCell>
                <TableHeadCell width="10%" style="min-width:100px">이름</TableHeadCell>
                <TableHeadCell width="10%" style="min-width:150px">구분</TableHeadCell>
                <TableHeadCell width="10%" style="min-width:100px">관리자</TableHeadCell>
                <TableHeadCell width="10%" style="min-width:100px">OTP</TableHeadCell>
                <TableHeadCell width="10%" style="min-width:100px">리눅스</TableHeadCell>
                <TableHeadCell width="10%">작업</TableHeadCell>
            </TableHead>
            <TableBody tableBodyClass="divide-y">
                {#if filteredUsers1.length === 0}
                    <TableBodyRow>
                        <TableBodyCell colspan="7" class="text-center">사용자가 없습니다.</TableBodyCell>
                    </TableBodyRow>
                {/if}
                {#each filteredUsers1 as user (user.username)}
                    <TableBodyRow>
                        <TableBodyCell>{user.username}</TableBodyCell>
                        <TableBodyCell>{user.profile.name}</TableBodyCell>
                        <TableBodyCell>{user.profile.sta}</TableBodyCell>
                        <TableBodyCell>{user.is_staff?"✔":"✖"}</TableBodyCell>
                        <TableBodyCell>{user.vpn?"✔":"✖"}</TableBodyCell>
                        <TableBodyCell>{#if user.linux}✔<br>({user.linux.username}){:else}✖{/if}</TableBodyCell>
                        <TableBodyCell>
                            <div class="flex gap-1 justify-center">
                                <Button outline size="sm" color={null} on:click={() => setEditingUser(user)}><EditOutline class="w-4 h-4" /></Button>
                                <Button outline size="sm" color={null} on:click={() => deactivateUser(user)}><BanOutline class="w-4 h-4" /></Button>
                            </div>
                        </TableBodyCell>
                    </TableBodyRow>
                {/each}
            </TableBody>
        </TableSearch>
    </Card>
    <Card size="none" class="lg:col-span-2">
        <div class="flex justify-between">
            <h5 class="mb-5 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">게스트 관리</h5>
            <div class="flex gap-2">
                <Button class="h-10 w-24" size="xs" color="red" on:click={() => ldapModal = true}>LDAP 리빌딩</Button>
                <Button class="h-10 w-10" size="xs" color="blue" on:click={() => guestModal = true}><PlusOutline /></Button>
            </div>
        </div>
        <TableSearch placeholder="이름으로 검색" class="text-center" hoverable={true} bind:inputValue={searchTerm2}>
            <TableHead>
                <TableHeadCell width="10%" style="min-width:150px">게스트아이디</TableHeadCell>
                <TableHeadCell width="10%" style="min-width:80px">이름</TableHeadCell>
                <TableHeadCell width="10%" style="min-width:100px">생년월일</TableHeadCell>
                <TableHeadCell>원 소속기관</TableHeadCell>
                <TableHeadCell width="10%" style="min-width:120px">계정 만료일</TableHeadCell>
                <TableHeadCell width="10%" style="min-width:100px">OTP</TableHeadCell>
                <TableHeadCell width="10%" style="min-width:100px">리눅스</TableHeadCell>
                <TableHeadCell width="10%" style="min-width:80px">작업</TableHeadCell>
            </TableHead>
            <TableBody tableBodyClass="divide-y">
                {#if filteredUsers2.length === 0}
                    <TableBodyRow>
                        <TableBodyCell colspan="8" class="text-center">게스트가 없습니다.</TableBodyCell>
                    </TableBodyRow>
                {/if}
                {#each filteredUsers2 as user (user.username)}
                    <TableBodyRow>
                        <TableBodyCell>{user.username}</TableBodyCell>
                        <TableBodyCell>{user.profile.name}</TableBodyCell>
                        <TableBodyCell>{user.guestinfo.date_of_birth?user.guestinfo.date_of_birth:'.'}</TableBodyCell>
                        <TableBodyCell>{user.guestinfo.institute}</TableBodyCell>
                        <TableBodyCell>{user.profile.date_expire}</TableBodyCell>
                        <TableBodyCell>{user.vpn?"✔":"✖"}</TableBodyCell>
                        <TableBodyCell>{user.linux?user.linux.username:"✖"}</TableBodyCell>
                        <TableBodyCell>
                            <div class="flex gap-1 justify-center">
                                <Button size="sm" color={null} on:click={() => setEditingGuest(user)}><EditOutline class="w-4 h-4" /></Button>
                                <Button size="sm" color={null} on:click={() => deactivateUser(user)}><BanOutline class="w-4 h-4" /></Button>
                            </div>
                        </TableBodyCell>
                    </TableBodyRow>
                {/each}
            </TableBody>
        </TableSearch>
    </Card>
    <Card size="none" class="lg:col-span-2">
        <h5 class="mb-5 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">비활성화된 사용자 관리 (6개월 후 데이터 자동 삭제)</h5>
        <TableSearch placeholder="이름 또는 아이디로 검색" class="text-center" hoverable={true} bind:inputValue={searchTerm3}>
            <TableHead>
                <TableHeadCell width="200px">아이디</TableHeadCell>
                <TableHeadCell>이름</TableHeadCell>
                <TableHeadCell>소속기관</TableHeadCell>
                <TableHeadCell>계정 만료일</TableHeadCell>
                <TableHeadCell>계정 삭제일</TableHeadCell>
                <TableHeadCell width="10%" style="min-width:80px">작업</TableHeadCell>
            </TableHead>
            <TableBody tableBodyClass="divide-y">
                {#if filteredUsers3.length === 0}
                    <TableBodyRow>
                        <TableBodyCell colspan="6" class="text-center">사용자가 없습니다.</TableBodyCell>
                    </TableBodyRow>
                {/if}
                {#each filteredUsers3 as user (user.username)}
                    <TableBodyRow>
                        <TableBodyCell>{user.username}</TableBodyCell>
                        <TableBodyCell>{user.profile.name}</TableBodyCell>
                        <TableBodyCell>{user.guestinfo?user.guestinfo.institute:""}</TableBodyCell>
                        <TableBodyCell>{user.profile.date_expire?user.profile.date_expire:"."}</TableBodyCell>
                        <TableBodyCell>{user.profile.date_removal?user.profile.date_removal:"."}</TableBodyCell>
                        <TableBodyCell>
                            <div class="flex gap-2 justify-center">
                                <Button size="sm" color={null} on:click={() => activateUser(user)}><CheckPlusCircleOutline class="w-4 h-4" /></Button>
                            </div>
                        </TableBodyCell>
                    </TableBodyRow>
                {/each}
            </TableBody>
        </TableSearch>
    </Card>
</div>