<script>
    import { Card, Alert, Button } from 'flowbite-svelte';
    import { t } from '$lib/translations';

    export let data;
</script>

<div class="flex items-center justify-center bg-gray-100 fixed left-0 right-0 top-0 bottom-0">
    <div class="w-full max-w-md">
        <Card size='none'>
            {#if data.verified}
            <Alert color="green" class="mb-4">{$t("register.verify_success")}</Alert>
            {:else}
            <Alert color="red" class="mb-4">{$t("register.verify_failed")}</Alert>
            {/if}
            <Button href="/login" class="w-full" color="blue">{$t("register.back_to_login")}</Button>
        </Card>
    </div>
</div>
