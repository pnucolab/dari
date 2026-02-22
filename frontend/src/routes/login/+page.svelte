<script>
    import { enhance } from '$app/forms';
    import { Card, Button, Label, Input, Checkbox, Alert } from 'flowbite-svelte';
    import { t } from '$lib/translations';

    export let form;

    let is_agreed = false;
    let submitting = false;

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
        <Card size='none'>
          <form method="POST" action="?/login" use:enhance={handleSubmit}>
            <div class="mb-6">
              <Label for="id" class="mb-2">{$t("login.id")}</Label>
              <Input type="text" id="id" name="id" color="blue" required />
            </div>
            <div class="mb-2">
              <Label for="pw" class="mb-2">{$t("login.pw")}</Label>
              <Input type="password" id="pw" name="pw" color="blue" required />
            </div>
            <div class="text-right mb-6">
              <a href="/forgot-password" class="text-sm text-blue-600 hover:underline dark:text-blue-500">{$t("login.forgot_password")}</a>
            </div>
            <div class="flex items-center gap-2 mb-6">
              <Checkbox color="blue" id="agree" bind:checked={is_agreed} required />
              <Input type="hidden" name="agree" value={is_agreed} />
              <Label for="agree" class="mb-0">
                {@html $t("login.agree")}
              </Label>
            </div>
            {#if form?.error === 'email_not_verified'}
            <Alert color="yellow" class="mb-4" dismissable>{$t("login.email_not_verified")}</Alert>
            {:else if form?.error === 'pending_approval'}
            <Alert color="yellow" class="mb-4" dismissable>{$t("login.pending_approval")}</Alert>
            {:else if form?.error === 'account_deactivated'}
            <Alert color="red" class="mb-4" dismissable>{$t("login.account_deactivated")}</Alert>
            {:else if form?.error}
            <Alert color="red" class="mb-4" dismissable>{$t("login.login.failed")}</Alert>
            {/if}
            {#if submitting}
              <Button class="w-full" color="green" disabled>{$t("login.login")}</Button>
            {:else}
              <Button type="submit" class="w-full" color="green">{$t("login.login")}</Button>
            {/if}

            <div class="flex items-center my-4">
              <hr class="flex-grow border-gray-300" />
              <span class="px-3 text-sm text-gray-500">{$t("login.or")}</span>
              <hr class="flex-grow border-gray-300" />
            </div>

            <Button href="/register" class="w-full" color="blue" outline>{$t("login.register")}</Button>
          </form>
        </Card>
    </div>
</div>
