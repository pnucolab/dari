<script>
    import { enhance } from '$app/forms';
    import { t } from '$lib/translations';
    import {
        Card,
        Label,
        Input,
        Fileupload,
        Button,
        Alert,
    } from 'flowbite-svelte';
    export let form;
    export let data;
    
    let defaults = {};
    $: defaults = data.defaults;

    let success = false;
    function handleSubmit() {
        success = false;
        return async ({ result, update }) => {
            if (result.type === 'success') {
                success = true;
            }
            await update({ reset: false });
        };
    }
</script>

<div class="p-4 w-full">
    <Card size="none">
        <h5 class="mb-5 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">기본 설정</h5>
        <form method="POST" enctype="multipart/form-data" action="?/defaults" use:enhance={handleSubmit}>
            <div class="grid gap-2 mb-3">
                <Label>로고 (Optional)</Label>
                <Fileupload name="logo" />
            </div>
            <div class="grid gap-2 mb-3">
                <Label>조직명</Label>
                <Input type="text" name="sitename" value="{defaults.sitename}" required />
            </div>
            <div class="grid gap-2 mb-3">
                <Label>기본 그룹</Label>
                <Input type="text" name="gid" value="{defaults.gid}" />
            </div>
            <div class="grid gap-2 mb-5">
                <Label>기본 쉘</Label>
                <Input type="text" name="shell" value="{defaults.shell}" />
            </div>
            <div class="grid gap-2 mb-5">
                <Label>허용 이메일 도메인 (쉼표로 구분, 비워두면 모든 도메인 허용)</Label>
                <Input type="text" name="allowed_email_domains" value="{defaults.allowed_email_domains}" />
            </div>
            {#if success}
            <Alert class="mb-4" color="green" dismissable on:close={() => success = false}>저장되었습니다.</Alert>
            {/if}
            {#if form?.error}
            <Alert class="mb-4" color="red" dismissable>{$t(form.error)}</Alert>
            {/if}
            <div class="text-center mb-2">
                <Button type="submit" color="blue" class="w-32">저장</Button>
            </div>
        </form>
    </Card>
</div>