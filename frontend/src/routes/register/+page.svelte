<script>
    import { enhance } from '$app/forms';
    import { Card, Button, Label, Input, Alert } from 'flowbite-svelte';
    import { t } from '$lib/translations';

    export let data;
    export let form;

    let submitting = false;
    $: allowedDomains = data.allowed_email_domains || '';

    let handleSubmit = () => {
      submitting = true;
      return async ({ result, update }) => {
        submitting = false;
        await update();
      };
    };
</script>

<div class="flex items-center justify-center bg-gray-100 fixed left-0 right-0 top-0 bottom-0">
    <div class="w-full max-w-md">
        {#if form?.success}
        <Card size='none'>
            <h2 class="text-2xl font-bold mb-4">{$t("register.title")}</h2>
            <Alert color="green" class="mb-4">{$t("register.success")}</Alert>
            <Button href="/login" class="w-full" color="blue">{$t("register.back_to_login")}</Button>
        </Card>
        {:else}
        <Card size='none'>
          <h2 class="text-2xl font-bold mb-4">{$t("register.title")}</h2>
          <p class="text-gray-600 mb-6">{$t("register.description")}</p>

          <form method="POST" action="?/register" use:enhance={handleSubmit}>
            <div class="mb-4">
              <Label for="username" class="mb-2">{$t("register.username")}</Label>
              <Input type="text" id="username" name="username" color="blue" required
                     placeholder="{$t('register.username_placeholder')}" />
              <p class="text-sm text-gray-500 mt-1">{$t("register.username_hint")}</p>
            </div>
            <div class="mb-4">
              <Label for="name" class="mb-2">{$t("register.name")}</Label>
              <Input type="text" id="name" name="name" color="blue" required />
            </div>
            <div class="mb-4">
              <Label for="email" class="mb-2">{$t("register.email")}</Label>
              <Input type="email" id="email" name="email" color="blue" required
                     placeholder="{$t('register.email_placeholder')}" />
              {#if allowedDomains}
                <p class="text-sm text-gray-500 mt-1">허용 도메인: {allowedDomains}</p>
              {/if}
            </div>
            <div class="mb-4">
              <Label for="password" class="mb-2">{$t("register.password")}</Label>
              <Input type="password" id="password" name="password" color="blue" required />
            </div>
            <div class="mb-6">
              <Label for="password_confirm" class="mb-2">{$t("register.password_confirm")}</Label>
              <Input type="password" id="password_confirm" name="password_confirm" color="blue" required />
            </div>

            {#if form?.error}
            <Alert color="red" class="mb-4" dismissable>{form.error}</Alert>
            {/if}

            {#if submitting}
              <Button class="w-full mb-4" color="blue" disabled>{$t("register.registering")}</Button>
            {:else}
              <Button type="submit" class="w-full mb-4" color="blue">{$t("register.register")}</Button>
            {/if}

            <Button href="/login" class="w-full" color="blue" outline>{$t("register.back_to_login")}</Button>
          </form>
        </Card>
        {/if}
    </div>
</div>
