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
        Modal,
        Label,
        Icon,
    } from '#lib/components/ui/index.js';
    import { enhance } from '$app/forms';
    import { refreshAll } from '$app/navigation';
    import { get } from '#lib/translations.js';

    let { data } = $props();

    const i18n = get();

    let users = $derived(data.users.map(user => {
        user.vpn = user.vpn ? true : false;
        return user;
    }));
    let guests = $derived(data.guests.map(user => {
        user.vpn = user.vpn ? true : false;
        return user;
    }));
    let deactivated = $derived(data.deactivated);

    let searchTerm1 = $state('');
    let searchTerm2 = $state('');
    let searchTerm3 = $state('');

    let filteredUsers1 = $derived(users.filter(user => 
        !user.username.startsWith('guest') &&
        (user.username.includes(searchTerm1) || user.profile.name.toLowerCase().includes(searchTerm1.toLowerCase()))
    ));
    let filteredUsers2 = $derived(guests.filter(user => 
        user.username.startsWith('guest') &&
        user.profile.name.toLowerCase().includes(searchTerm2.toLowerCase())
    ));
    let filteredUsers3 = $derived(deactivated.filter(user => 
        !user.is_active &&
        ((user.username && user.username.includes(searchTerm3)) ||
        user.profile.name.toLowerCase().includes(searchTerm3.toLowerCase()))
    ));

    let editingUser = $state(null);
    let editingGuest = $state(null);
    let userModal = $state(false);
    let guestModal = $state(false);
    let ldapModal = $state(false);

    $effect.pre(() => {
        if (!userModal) editingUser = null;
    });
    $effect.pre(() => {
        if (!guestModal) editingGuest = null;
    });
    
    function setEditingUser(user) {
        editingUser = { ...user };
        userModal = true;
    }

    function setEditingGuest(user) {
        editingGuest = { ...user };
        guestModal = true;
    }

    async function deactivateUser(user) {
        let formData = new FormData();
        formData.append('username', user.username);
        let response = await fetch('?/deactivate', {
            method: 'POST',
            body: formData,
        });
        if (response.ok) {
            refreshAll();
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
            refreshAll();
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
            refreshAll();
        }
    }

    let deleteModal = $state(false);
</script>

<Modal bind:open={ldapModal} class="w-full">
    <form method="POST" action="?/ldap" id="ldap-form" class="space-y-4">
        <h3 class="mb-4 text-xl font-medium text-gray-900 dark:text-white">{i18n.t('admin.users.ldap_rebuild')}</h3>
        <p class="text-gray-900">{i18n.t('admin.users.ldap_rebuild_confirm')}</p>
    </form>
    {#snippet footer()}
        <Button color="red" type="submit" form="ldap-form">{i18n.t('admin.users.rebuild')}</Button>
        <Button color="alternative" onclick={() => {ldapModal = false;}}>{i18n.t('common.cancel')}</Button>
    {/snippet}
</Modal>

<Modal bind:open={guestModal} size="lg" class="w-full">
    <form method="POST" action="?/{editingGuest?'guest':'guestnew'}" id="guest-form" class="space-y-4">
        <h3 class="mb-4 text-xl font-medium text-gray-900 dark:text-white">{i18n.t('admin.users.basic_info')}</h3>
        <div class="flex gap-3 mb-5">
            <Label class="w-full space-y-2">
                <span>{i18n.t('admin.users.login_password')}</span>
                <Input type="password" name="pw" placeholder={editingGuest?'•••••••••••':''} />
            </Label>
            <Label class="w-full space-y-2">
                <span>{i18n.t('user.name')}</span>
                <Input type="text" name="name" value={editingGuest?editingGuest.profile.name:''} />
            </Label>
            <Label class="w-full space-y-2">
                <span>{i18n.t('user.institute')}</span>
                <Input type="text" name="institute" value={editingGuest?editingGuest.guestinfo.institute:''} />
            </Label>
        </div>
        <div class="flex gap-3 mb-5">
            <Label class="w-full space-y-2">
                <span>{i18n.t('admin.users.date_of_birth')}</span>
                <Input type="date" name="date_of_birth" value={editingGuest?editingGuest.guestinfo.date_of_birth:''} />
            </Label>
            <Label class="w-full space-y-2">
                <span>{i18n.t('admin.users.reference')}</span>
                <Input type="text" name="reference" value={editingGuest?editingGuest.guestinfo.reference:''} />
            </Label>
            <Label class="w-full space-y-2">
                <span>{i18n.t('admin.users.mobile')}</span>
                <Input type="text" name="mobile" value={editingGuest?editingGuest.guestinfo.mobile:''} />
            </Label>
        </div>
        <br>
        <h3 class="mb-4 text-xl font-medium text-gray-900 dark:text-white">{i18n.t('user.linux_info')}</h3>
        <div class="flex gap-3 mb-5">
            {#if editingGuest && editingGuest.linux}
            <Label class="w-full space-y-2">
                <span>{i18n.t('user.username')}</span>
                <Input type="text" name="username" value={editingGuest.linux.username} />
            </Label>
            <Label class="w-full space-y-2">
                <span>UID</span>
                <Input type="text" name="uid" value={editingGuest.linux.uid} />
            </Label>
            <Label class="w-full space-y-2">
                <span>{i18n.t('admin.users.primary_group')}</span>
                <Input type="text" name="group" value={editingGuest.linux.group.name} />
            </Label>
            {:else}
            <p class="text-gray-900">{i18n.t('admin.users.no_linux')}</p>
            {/if}
        </div>
        <h3 class="mb-4 text-xl font-medium text-gray-900 dark:text-white">{i18n.t('admin.users.other_info')}</h3>
        <Table class="text-center mb-5" hoverable={true}>
            <TableHead>
                <TableHeadCell>{i18n.t('user.email')}</TableHeadCell>
                {#if editingGuest}
                <TableHeadCell>OTP</TableHeadCell>
                {/if}
                <TableHeadCell>{i18n.t('admin.users.date_expire')}</TableHeadCell>
            </TableHead>
            <TableBody class="divide-y">
                <TableBodyRow>
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
                </TableBodyRow>
            </TableBody>
        </Table>
        <Input type="hidden" name="username" value={editingGuest?editingGuest.username:""} />
    </form>
    {#snippet footer()}
        <Button color="blue" type="submit" form="guest-form">{i18n.t('common.save')}</Button>
        <Button color="alternative" onclick={() => {guestModal = false;}}>{i18n.t('common.cancel')}</Button>
    {/snippet}
</Modal>

<Modal bind:open={userModal} size="lg" class="w-full">
    {#if editingUser}
    <form method="POST" action="?/user" id="user-form" class="space-y-4">
        <h3 class="mb-4 text-xl font-medium text-gray-900 dark:text-white">{i18n.t('admin.users.basic_info')}</h3>
        <Table class="text-center mb-5" hoverable={true}>
            <TableHead>
                <TableHeadCell>{i18n.t('user.username')}</TableHeadCell>
                <TableHeadCell>{i18n.t('user.name')}</TableHeadCell>
                <TableHeadCell>{i18n.t('admin.users.type')}</TableHeadCell>
            </TableHead>
            <TableBody class="divide-y">
                    <TableBodyRow>
                        <TableBodyCell>{editingUser.username}</TableBodyCell>
                        <TableBodyCell>{editingUser.profile.name}</TableBodyCell>
                        <TableBodyCell>{editingUser.profile.sta}</TableBodyCell>
                    </TableBodyRow>
            </TableBody>
        </Table>
        <h3 class="mb-4 text-xl font-medium text-gray-900 dark:text-white">{i18n.t('user.linux_info')}</h3>
        <div class="flex gap-3 mb-5">
            {#if editingUser.linux}
            <Label class="w-full space-y-2">
                <span>{i18n.t('user.username')}</span>
                <Input type="text" name="linuxid" value={editingUser.linux.username} />
            </Label>
            <Label class="w-full space-y-2">
                <span>UID</span>
                <Input type="text" name="linuxuid" value={editingUser.linux.uid} />
            </Label>
            <Label class="w-full space-y-2">
                <span>{i18n.t('admin.users.primary_group')}</span>
                <Input type="text" name="linuxgroup" value={editingUser.linux.group.name} />
            </Label>
            {:else}
            <p class="text-gray-900">{i18n.t('admin.users.no_linux')}</p>
            {/if}
        </div>
        <h3 class="mb-4 text-xl font-medium text-gray-900 dark:text-white">{i18n.t('admin.users.other_info')}</h3>
        <Table class="text-center mb-5" hoverable={true}>
            <TableHead>
                <TableHeadCell>{i18n.t('user.email')}</TableHeadCell>
                <TableHeadCell>{i18n.t('admin.users.staff')}</TableHeadCell>
                <TableHeadCell>OTP</TableHeadCell>
                <TableHeadCell>{i18n.t('admin.users.date_expire')}</TableHeadCell>
            </TableHead>
            <TableBody class="divide-y">
                <TableBodyRow>
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
                </TableBodyRow>
            </TableBody>
        </Table>
        <Input type="hidden" name="username" value={editingUser.username} />
    </form>
    {/if}
    {#snippet footer()}
        <Button color="blue" type="submit" form="user-form">{i18n.t('common.save')}</Button>
        <Button color="alternative" onclick={() => {userModal = false;}}>{i18n.t('common.cancel')}</Button>
    {/snippet}
</Modal>

<div class="grid grid-cols-1 lg:grid-cols-2 gap-4 p-4 w-full">
    <Card size="xl" class="p-4 sm:p-6 text-gray-500 dark:text-gray-400 lg:col-span-2">
        <form method="POST" action="?/transfer">
            <h5 class="mb-5 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">{i18n.t('admin.users.transfer_title')}</h5>
            <Table class="text-center mb-5" hoverable={true}>
                <TableHead>
                    <TableHeadCell>{i18n.t('admin.users.transfer_from')}</TableHeadCell>
                    <TableHeadCell>{i18n.t('admin.users.transfer_to')}</TableHeadCell>
                    <TableHeadCell width="10%" style="min-width:80px">{i18n.t('common.actions')}</TableHeadCell>
                </TableHead>
                <TableBody class="divide-y">
                    <TableBodyRow>
                        <TableBodyCell><Input type="text" name="username_from" /></TableBodyCell>
                        <TableBodyCell><Input type="text" name="username_to" /></TableBodyCell>
                        <TableBodyCell><Button color="blue" type="submit">{i18n.t('admin.users.transfer')}</Button></TableBodyCell>
                    </TableBodyRow>
                </TableBody>
            </Table>
        </form>
    </Card>
    <Card size="xl" class="p-4 sm:p-6 text-gray-500 dark:text-gray-400 lg:col-span-2">
        <div class="flex justify-between">
            <h5 class="mb-5 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">{i18n.t('admin.menu.users')}</h5>
            <Button class="h-10 whitespace-nowrap" size="xs" color="red" onclick={() => ldapModal = true}>{i18n.t('admin.users.ldap_rebuild')}</Button>
        </div>
        <TableSearch placeholder={i18n.t('admin.users.search_name_id')} class="text-center" hoverable={true} bind:inputValue={searchTerm1}>
            <TableHead>
                <TableHeadCell width="10%" style="min-width:150px">{i18n.t('user.username')}</TableHeadCell>
                <TableHeadCell width="10%" style="min-width:100px">{i18n.t('user.name')}</TableHeadCell>
                <TableHeadCell width="10%" style="min-width:150px">{i18n.t('admin.users.type')}</TableHeadCell>
                <TableHeadCell width="10%" style="min-width:100px">{i18n.t('admin.users.staff')}</TableHeadCell>
                <TableHeadCell width="10%" style="min-width:100px">OTP</TableHeadCell>
                <TableHeadCell width="10%" style="min-width:100px">{i18n.t('user.linux')}</TableHeadCell>
                <TableHeadCell width="10%">{i18n.t('common.actions')}</TableHeadCell>
            </TableHead>
            <TableBody class="divide-y">
                {#if filteredUsers1.length === 0}
                    <TableBodyRow>
                        <TableBodyCell colspan="7" class="text-center">{i18n.t('common.no_users')}</TableBodyCell>
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
                                <Button size="sm" color="alternative" class="border-0" onclick={() => setEditingUser(user)}><Icon name="edit" class="w-4 h-4" /></Button>
                                <Button size="sm" color="alternative" class="border-0" onclick={() => deactivateUser(user)}><Icon name="ban" class="w-4 h-4" /></Button>
                            </div>
                        </TableBodyCell>
                    </TableBodyRow>
                {/each}
            </TableBody>
        </TableSearch>
    </Card>
    <Card size="xl" class="p-4 sm:p-6 text-gray-500 dark:text-gray-400 lg:col-span-2">
        <div class="flex justify-between">
            <h5 class="mb-5 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">{i18n.t('admin.users.guest_title')}</h5>
            <div class="flex gap-2">
                <Button class="h-10 whitespace-nowrap" size="xs" color="red" onclick={() => ldapModal = true}>{i18n.t('admin.users.ldap_rebuild')}</Button>
                <Button class="h-10 w-10" size="xs" color="blue" onclick={() => guestModal = true}><Icon name="plus" /></Button>
            </div>
        </div>
        <TableSearch placeholder={i18n.t('admin.users.search_name')} class="text-center" hoverable={true} bind:inputValue={searchTerm2}>
            <TableHead>
                <TableHeadCell width="10%" style="min-width:150px">{i18n.t('admin.users.guest_id')}</TableHeadCell>
                <TableHeadCell width="10%" style="min-width:80px">{i18n.t('user.name')}</TableHeadCell>
                <TableHeadCell width="10%" style="min-width:100px">{i18n.t('admin.users.date_of_birth')}</TableHeadCell>
                <TableHeadCell>{i18n.t('admin.users.orig_institute')}</TableHeadCell>
                <TableHeadCell width="10%" style="min-width:120px">{i18n.t('admin.users.date_expire')}</TableHeadCell>
                <TableHeadCell width="10%" style="min-width:100px">OTP</TableHeadCell>
                <TableHeadCell width="10%" style="min-width:100px">{i18n.t('user.linux')}</TableHeadCell>
                <TableHeadCell width="10%" style="min-width:80px">{i18n.t('common.actions')}</TableHeadCell>
            </TableHead>
            <TableBody class="divide-y">
                {#if filteredUsers2.length === 0}
                    <TableBodyRow>
                        <TableBodyCell colspan="8" class="text-center">{i18n.t('admin.users.no_guests')}</TableBodyCell>
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
                                <Button size="sm" color="alternative" class="border-0" onclick={() => setEditingGuest(user)}><Icon name="edit" class="w-4 h-4" /></Button>
                                <Button size="sm" color="alternative" class="border-0" onclick={() => deactivateUser(user)}><Icon name="ban" class="w-4 h-4" /></Button>
                            </div>
                        </TableBodyCell>
                    </TableBodyRow>
                {/each}
            </TableBody>
        </TableSearch>
    </Card>
    <Card size="xl" class="p-4 sm:p-6 text-gray-500 dark:text-gray-400 lg:col-span-2">
        <h5 class="mb-5 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">{i18n.t('admin.users.deactivated_title')}</h5>
        <TableSearch placeholder={i18n.t('admin.users.search_name_id')} class="text-center" hoverable={true} bind:inputValue={searchTerm3}>
            <TableHead>
                <TableHeadCell width="200px">{i18n.t('user.username')}</TableHeadCell>
                <TableHeadCell>{i18n.t('user.name')}</TableHeadCell>
                <TableHeadCell>{i18n.t('user.institute')}</TableHeadCell>
                <TableHeadCell>{i18n.t('admin.users.date_expire')}</TableHeadCell>
                <TableHeadCell>{i18n.t('admin.users.date_removal')}</TableHeadCell>
                <TableHeadCell width="10%" style="min-width:80px">{i18n.t('common.actions')}</TableHeadCell>
            </TableHead>
            <TableBody class="divide-y">
                {#if filteredUsers3.length === 0}
                    <TableBodyRow>
                        <TableBodyCell colspan="6" class="text-center">{i18n.t('common.no_users')}</TableBodyCell>
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
                                <Button size="sm" color="alternative" class="border-0" onclick={() => activateUser(user)}><Icon name="check-plus-circle" class="w-4 h-4" /></Button>
                            </div>
                        </TableBodyCell>
                    </TableBodyRow>
                {/each}
            </TableBody>
        </TableSearch>
    </Card>
</div>