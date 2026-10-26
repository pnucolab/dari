<script>
    import { Card, Alert, Button } from '#lib/components/ui/index.js';
    import { get } from '#lib/translations.js';

    let { data } = $props();

    const i18n = get();
</script>

<div class="flex items-center justify-center bg-gray-100 fixed left-0 right-0 top-0 bottom-0">
    <div class="w-full max-w-md">
        <Card size="xl" class="p-4 sm:p-6 text-gray-500 dark:text-gray-400">
            {#if data.verified}
            <Alert color="green" class="mb-4">{i18n.t("register.verify_success")}</Alert>
            {:else}
            <Alert color="red" class="mb-4">{i18n.t("register.verify_failed")}</Alert>
            {/if}
            <Button href="/login" class="w-full" color="blue">{i18n.t("register.back_to_login")}</Button>
        </Card>
    </div>
</div>
