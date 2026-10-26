<script>
    import { enhance } from '$app/forms';
    import {
        Card,
        Button,
        Label,
        Input,
        Alert,
    } from '#lib/components/ui/index.js';
    import { get } from '#lib/translations.js';

    let { data, form } = $props();

    const i18n = get();

    let newPassword = $state('');
    let confirmPassword = $state('');
    let submitting = $state(false);
    let mismatch = $state(false);

    let handleSubmit = () => {
      if (newPassword !== confirmPassword) {
        mismatch = true;
        return ({ cancel }) => cancel();
      }
      mismatch = false;
      submitting = true;
      return async ({ result, update }) => {
        submitting = false;
        await update();
      };
    };
</script>

<div class="flex items-center justify-center bg-gray-100 fixed left-0 right-0 top-0 bottom-0">
    <div class="w-full max-w-sm">
        <Card size="xl" class="p-4 sm:p-6 text-gray-500 dark:text-gray-400">
            {#if form?.success}
            <Alert color="green" class="mb-4">{i18n.t("reset-password.success")}</Alert>
            <Button href="/login" class="w-full" color="blue">{i18n.t("reset-password.back_to_login")}</Button>
            {:else if !data.uid || !data.token}
            <Alert color="red" class="mb-4">{i18n.t("reset-password.failed")}</Alert>
            <Button href="/login" class="w-full" color="blue">{i18n.t("reset-password.back_to_login")}</Button>
            {:else}
            <h5 class="mb-4 text-xl font-medium text-gray-900">{i18n.t("reset-password.title")}</h5>
            <form method="POST" use:enhance={handleSubmit}>
                <input type="hidden" name="uid" value={data.uid} />
                <input type="hidden" name="token" value={data.token} />
                <div class="mb-4">
                    <Label for="new_password" class="mb-2">{i18n.t("reset-password.new_password")}</Label>
                    <Input type="password" id="new_password" name="new_password" bind:value={newPassword} required />
                </div>
                <div class="mb-6">
                    <Label for="confirm_password" class="mb-2">{i18n.t("reset-password.confirm_password")}</Label>
                    <Input type="password" id="confirm_password" name="confirm_password" bind:value={confirmPassword} required />
                </div>
                {#if mismatch}
                <Alert color="red" class="mb-4" dismissable>{i18n.t("reset-password.password_mismatch")}</Alert>
                {/if}
                {#if form?.error}
                <Alert color="red" class="mb-4" dismissable>{i18n.t("reset-password.failed")}</Alert>
                {/if}
                {#if submitting}
                <Button class="w-full mb-4" color="blue" disabled>{i18n.t("reset-password.submitting")}</Button>
                {:else}
                <Button type="submit" class="w-full mb-4" color="blue">{i18n.t("reset-password.submit")}</Button>
                {/if}
                <div class="text-center">
                  <a href="/login" class="text-sm text-blue-600 hover:underline dark:text-blue-500">{i18n.t("reset-password.back_to_login")}</a>
                </div>
            </form>
            {/if}
        </Card>
    </div>
</div>
