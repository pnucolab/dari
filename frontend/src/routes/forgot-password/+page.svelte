<script>
    import { enhance } from '$app/forms';
    import { Card, Button, Label, Input, Alert } from 'flowbite-svelte';
    import { t } from '$lib/translations';

    export let form;

    let submitting = false;

    let handleSubmit = () => {
      submitting = true;
      return async ({ result, update }) => {
        submitting = false;
        await update();
      };
    };
</script>

<div class="flex items-center justify-center bg-gray-100 fixed left-0 right-0 top-0 bottom-0">
    <div class="w-full max-w-sm">
        <Card size='none'>
            {#if form?.success}
            <Alert color="green" class="mb-4">{$t("forgot-password.success")}</Alert>
            <Button href="/login" class="w-full" color="blue">{$t("forgot-password.back_to_login")}</Button>
            {:else}
            <h5 class="mb-2 text-xl font-medium text-gray-900">{$t("forgot-password.title")}</h5>
            <p class="mb-4 text-sm text-gray-500">{$t("forgot-password.description")}</p>
            <form method="POST" use:enhance={handleSubmit}>
                <div class="mb-4">
                    <Label for="username" class="mb-2">{$t("forgot-password.username")}</Label>
                    <Input type="text" id="username" name="username" color="blue" required />
                </div>
                <div class="mb-6">
                    <Label for="email" class="mb-2">{$t("forgot-password.email")}</Label>
                    <Input type="email" id="email" name="email" color="blue" required />
                </div>
                {#if submitting}
                <Button class="w-full mb-4" color="blue" disabled>{$t("forgot-password.submitting")}</Button>
                {:else}
                <Button type="submit" class="w-full mb-4" color="blue">{$t("forgot-password.submit")}</Button>
                {/if}
                <div class="text-center">
                  <a href="/login" class="text-sm text-blue-600 hover:underline dark:text-blue-500">{$t("forgot-password.back_to_login")}</a>
                </div>
            </form>
            {/if}
        </Card>
    </div>
</div>
