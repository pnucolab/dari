<script>
    import { enhance } from '$app/forms';
    import {
        Card,
        Label,
        Input,
        Button,
        Alert,
     } from 'flowbite-svelte';
    import { t } from '$lib/translations';

    export let data;
    let user = null;
    $: user = data.user;

    let old_password = '';
    let new_password = '';
    let new_password_confirm = '';
    let passwordChanging = false;

    function handlePasswordSubmit() {
        passwordChanging = true;
        return async ({ result, update }) => {
            await update();
            passwordChanging = false;
            if (result.type === 'success') {
                old_password = '';
                new_password = '';
                new_password_confirm = '';
            }
        };
    }

    export let form;
</script>

<div class="grid gap-4 p-4 w-full">

{#if form?.error}
<Alert color="red" dismissable>{$t(form.error)}</Alert>
{/if}

<Card size="none">
    <h1>{$t('common.profile')}</h1>
    <div class="grid gap-6 md:grid-cols-3 mb-6">
        <div class="grid gap-2">
            <Label>{$t('user.username')}</Label>
            <Input value={user.username} disabled />
        </div>
        <div class="grid gap-2">
            <Label>{$t('user.name')}</Label>
            <Input value={user.profile.name} disabled />
        </div>
        {#if user.guestinfo}
            <div class="grid gap-2">
                <Label>{$t('user.institute')}</Label>
                <Input value="{user.guestinfo.institute}" disabled />
            </div>
        {/if}
        <div class="grid gap-2">
            <Label>{$t('user.email')}</Label>
            <Input value="{user.email}" disabled />
        </div>
    </div>
</Card>
<Card size="none">
    <h1>{$t('user.vpn_info')}</h1>
    <div>
        {#if user.vpn}
        <span>{$t('user.vpn.qr_set')}</span>
        {:else}
        <span>{$t('user.vpn_not_assigned')}</span>
        {/if}
    </div>
</Card>

{#if user.linux}
<Card size="none">
    <h1>{$t('user.password_change')}</h1>
    <p class="text-gray-600 mb-4">{$t('user.password_change_description')}</p>

    <form method="POST" action="?/password" use:enhance={handlePasswordSubmit}>
        <div class="grid gap-4">
            <div class="grid gap-2">
                <Label for="old_password">{$t('user.old_password')}</Label>
                <Input type="password" id="old_password" name="old_password" bind:value={old_password} required />
            </div>
            <div class="grid gap-2">
                <Label for="new_password">{$t('user.new_password')}</Label>
                <Input type="password" id="new_password" name="new_password" bind:value={new_password} required />
            </div>
            <div class="grid gap-2">
                <Label for="new_password_confirm">{$t('user.new_password_confirm')}</Label>
                <Input type="password" id="new_password_confirm" name="new_password_confirm" bind:value={new_password_confirm} required />
            </div>

            {#if form?.password_error}
            <Alert color="red" dismissable>{form.password_error}</Alert>
            {/if}

            {#if form?.password_success}
            <Alert color="green">{$t('user.password_changed_success')}</Alert>
            {/if}

            <div>
                {#if passwordChanging}
                    <Button color="blue" disabled>{$t('user.changing_password')}</Button>
                {:else}
                    <Button type="submit" color="blue">{$t('user.change_password')}</Button>
                {/if}
            </div>
        </div>
    </form>
</Card>
{/if}

</div>