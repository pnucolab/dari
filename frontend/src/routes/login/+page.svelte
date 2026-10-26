<script>
    import { enhance } from '$app/forms';
    import {
        Card,
        Button,
        Label,
        Input,
        Checkbox,
        Alert,
    } from '#lib/components/ui/index.js';
    import { get } from '#lib/translations.js';

    let { form } = $props();

    const i18n = get();

    let is_agreed = $state(false);
    let submitting = $state(false);

    let handleSubmit = () => {
      submitting = true;
      return async ({ result, update }) => {
        submitting = false;
        if (result.type === 'failure') {
          console.log(form);
        }
        await update();
      };
    };
</script>
  
<div class="flex items-center justify-center bg-gray-100 fixed left-0 right-0 top-0 bottom-0">
    <div class="w-full max-w-sm">
        <Card size="xl" class="p-4 sm:p-6 text-gray-500 dark:text-gray-400">
          <form method="POST" action="?/login" use:enhance={handleSubmit}>
            <div class="mb-6">
              <Label for="id" class="mb-2">{i18n.t("login.id")}</Label>
              <Input type="text" id="id" name="id" required />
            </div>
            <div class="mb-2">
              <Label for="pw" class="mb-2">{i18n.t("login.pw")}</Label>
              <Input type="password" id="pw" name="pw" required />
            </div>
            <div class="text-right mb-6">
              <a href="/forgot-password" class="text-sm text-blue-600 hover:underline dark:text-blue-500">{i18n.t("login.forgot_password")}</a>
            </div>
            <div class="flex items-center gap-2 mb-6">
              <Checkbox color="blue" id="agree" bind:checked={is_agreed} required />
              <Input type="hidden" name="agree" value={is_agreed} />
              <Label for="agree" class="mb-0">
                {@html i18n.t("login.agree")}
              </Label>
            </div>
            {#if form?.error === 'email_not_verified'}
            <Alert color="yellow" class="mb-4" dismissable>{i18n.t("login.email_not_verified")}</Alert>
            {:else if form?.error === 'pending_approval'}
            <Alert color="yellow" class="mb-4" dismissable>{i18n.t("login.pending_approval")}</Alert>
            {:else if form?.error === 'account_deactivated'}
            <Alert color="red" class="mb-4" dismissable>{i18n.t("login.account_deactivated")}</Alert>
            {:else if form?.error}
            <Alert color="red" class="mb-4" dismissable>{i18n.t("login.login.failed")}</Alert>
            {/if}
            {#if submitting}
              <Button class="w-full" color="green" disabled>{i18n.t("login.login")}</Button>
            {:else}
              <Button type="submit" class="w-full" color="green">{i18n.t("login.login")}</Button>
            {/if}

            <div class="flex items-center my-4">
              <hr class="flex-grow border-gray-300" />
              <span class="px-3 text-sm text-gray-500">{i18n.t("login.or")}</span>
              <hr class="flex-grow border-gray-300" />
            </div>

            <Button href="/register" class="w-full" color="blue" outline>{i18n.t("login.register")}</Button>
          </form>
        </Card>
    </div>
</div>
