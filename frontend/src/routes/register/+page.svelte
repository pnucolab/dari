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

    let submitting = $state(false);
    let allowedDomains = $derived(data.allowed_email_domains || '');

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
        <Card size="xl" class="p-4 sm:p-6 text-gray-500 dark:text-gray-400">
            <h2 class="text-2xl font-bold mb-4">{i18n.t("register.title")}</h2>
            <Alert color="green" class="mb-4">{i18n.t("register.success")}</Alert>
            <Button href="/login" class="w-full" color="blue">{i18n.t("register.back_to_login")}</Button>
        </Card>
        {:else}
        <Card size="xl" class="p-4 sm:p-6 text-gray-500 dark:text-gray-400">
          <h2 class="text-2xl font-bold mb-4">{i18n.t("register.title")}</h2>
          <p class="text-gray-600 mb-6">{i18n.t("register.description")}</p>

          <form method="POST" action="?/register" use:enhance={handleSubmit}>
            <div class="mb-4">
              <Label for="username" class="mb-2">{i18n.t("register.username")}</Label>
              <Input type="text" id="username" name="username" required
                     placeholder={i18n.t('register.username_placeholder')} />
              <p class="text-sm text-gray-500 mt-1">{i18n.t("register.username_hint")}</p>
            </div>
            <div class="mb-4">
              <Label for="name" class="mb-2">{i18n.t("register.name")}</Label>
              <Input type="text" id="name" name="name" required />
            </div>
            <div class="mb-4">
              <Label for="email" class="mb-2">{i18n.t("register.email")}</Label>
              <Input type="email" id="email" name="email" required
                     placeholder={i18n.t('register.email_placeholder')} />
              {#if allowedDomains}
                <p class="text-sm text-gray-500 mt-1">{i18n.t('register.allowed_domains', { domains: allowedDomains })}</p>
              {/if}
            </div>
            <div class="mb-4">
              <Label for="password" class="mb-2">{i18n.t("register.password")}</Label>
              <Input type="password" id="password" name="password" required />
            </div>
            <div class="mb-6">
              <Label for="password_confirm" class="mb-2">{i18n.t("register.password_confirm")}</Label>
              <Input type="password" id="password_confirm" name="password_confirm" required />
            </div>

            {#if form?.error}
            <Alert color="red" class="mb-4" dismissable>{form.error_i18n ? i18n.t(form.error) : form.error}</Alert>
            {/if}

            {#if submitting}
              <Button class="w-full mb-4" color="blue" disabled>{i18n.t("register.registering")}</Button>
            {:else}
              <Button type="submit" class="w-full mb-4" color="blue">{i18n.t("register.register")}</Button>
            {/if}

            <Button href="/login" class="w-full" color="blue" outline>{i18n.t("register.back_to_login")}</Button>
          </form>
        </Card>
        {/if}
    </div>
</div>
