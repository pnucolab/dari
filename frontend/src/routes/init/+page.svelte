<script>
    import { enhance } from '$app/forms';
    import { get } from '#lib/translations.js';
    import {
        Card,
        Label,
        Input,
        Fileupload,
        Button,
        Alert,
    } from '#lib/components/ui/index.js';

    let { data, form } = $props();

    const i18n = get();

    // svelte-ignore state_referenced_locally
    let currentStep = $state(data.user ? 2 : 1);
    let submitting = $state(false);

    // Store admin info client-side
    let adminUsername = $state('');
    let adminName = $state('');
    let adminEmail = $state('');
    let adminPassword = $state('');
    let adminPasswordConfirm = $state('');
    // a key of the `init` namespace
    let step1Error = $state('');

    function goToStep2() {
        step1Error = '';

        if (!/^[a-z][a-z0-9]{0,30}$/.test(adminUsername)) {
            step1Error = 'init.error_username_format';
            return;
        }
        if (adminUsername.startsWith('guest')) {
            step1Error = 'init.error_username_guest';
            return;
        }
        if (adminPassword.length < 8) {
            step1Error = 'init.error_password_length';
            return;
        }
        if (adminPassword !== adminPasswordConfirm) {
            step1Error = 'init.error_password_mismatch';
            return;
        }

        currentStep = 2;
    }

    function handleDefaultsSubmit() {
        submitting = true;
        return async ({ result, update }) => {
            await update();
            submitting = false;
        };
    }
</script>

<div class="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
    <div class="w-full max-w-3xl">
        <div class="mb-8">
            <div class="flex items-center justify-center">
                <div class="flex items-center space-x-4">
                    <div class="flex items-center">
                        <div class="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold
                            {currentStep >= 1 ? 'bg-blue-600' : 'bg-gray-400'}">
                            {#if currentStep >= 2}
                                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                                </svg>
                            {:else}
                                1
                            {/if}
                        </div>
                        <span class="ml-2 font-medium {currentStep >= 1 ? 'text-blue-600' : 'text-gray-500'}">
                            {i18n.t('init.step_admin')}
                        </span>
                    </div>
                    <div class="w-16 h-0.5 {currentStep >= 2 ? 'bg-blue-600' : 'bg-gray-300'}"></div>
                    <div class="flex items-center">
                        <div class="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold
                            {currentStep >= 2 ? 'bg-blue-600' : 'bg-gray-400'}">
                            2
                        </div>
                        <span class="ml-2 font-medium {currentStep >= 2 ? 'text-blue-600' : 'text-gray-500'}">
                            {i18n.t('init.step_system')}
                        </span>
                    </div>
                </div>
            </div>
        </div>
        <Card size="xl" class="p-4 sm:p-6 text-gray-500 dark:text-gray-400 shadow-xl">
            {#if currentStep === 1}
                <div class="space-y-6">
                    <div class="text-center">
                        <h3 class="text-2xl font-semibold text-gray-800 mb-2">{i18n.t('init.admin_title')}</h3>
                    </div>

                    <div class="space-y-5">
                        <div class="space-y-2">
                            <Label for="username" class="text-gray-700 font-medium">{i18n.t('init.username')}</Label>
                            <Input type="text" id="username" bind:value={adminUsername} required
                                   placeholder={i18n.t('init.username_placeholder')} class="text-base" />
                            <p class="text-sm text-gray-500">{i18n.t('init.username_hint')}</p>
                        </div>
                        <div class="space-y-2">
                            <Label for="name" class="text-gray-700 font-medium">{i18n.t('init.name')}</Label>
                            <Input type="text" id="name" bind:value={adminName} required placeholder={i18n.t('init.name_placeholder')} class="text-base" />
                        </div>
                        <div class="space-y-2">
                            <Label for="email" class="text-gray-700 font-medium">{i18n.t('init.email')}</Label>
                            <Input type="email" id="email" bind:value={adminEmail} required placeholder="admin@example.com" class="text-base" />
                        </div>
                        <div class="space-y-2">
                            <Label for="password" class="text-gray-700 font-medium">{i18n.t('init.password')}</Label>
                            <Input type="password" id="password" bind:value={adminPassword} required class="text-base" />
                            <p class="text-sm text-gray-500">{i18n.t('init.password_hint')}</p>
                        </div>
                        <div class="space-y-2">
                            <Label for="password_confirm" class="text-gray-700 font-medium">{i18n.t('init.password_confirm')}</Label>
                            <Input type="password" id="password_confirm" bind:value={adminPasswordConfirm} required class="text-base" />
                        </div>

                        {#if step1Error}
                        <Alert color="red" class="mt-4">{i18n.t(step1Error)}</Alert>
                        {/if}

                        <div class="pt-4">
                            <Button onclick={goToStep2} color="blue" size="xl" class="w-full">{i18n.t('init.next')}</Button>
                        </div>
                    </div>
                </div>
            {:else}
                <div class="space-y-6">
                    <div class="text-center">
                        <h3 class="text-2xl font-semibold text-gray-800 mb-2">{i18n.t('init.step_system')}</h3>
                    </div>

                    <form method="POST" enctype="multipart/form-data" action="?/setup" use:enhance={handleDefaultsSubmit} class="space-y-5">
                        <input type="hidden" name="admin_username" value={adminUsername} />
                        <input type="hidden" name="admin_name" value={adminName} />
                        <input type="hidden" name="admin_email" value={adminEmail} />
                        <input type="hidden" name="admin_password" value={adminPassword} />

                        <div class="space-y-2">
                            <Label class="text-gray-700 font-medium">{i18n.t('init.logo')}</Label>
                            <Fileupload name="logo" />
                        </div>
                        <div class="space-y-2">
                            <Label class="text-gray-700 font-medium">{i18n.t('init.sitename')}</Label>
                            <Input type="text" name="sitename" required placeholder={i18n.t('init.sitename_placeholder')} class="text-base" />
                        </div>
                        <div class="space-y-2">
                            <Label class="text-gray-700 font-medium">{i18n.t('init.sitename_en')}</Label>
                            <Input type="text" name="sitename_en" placeholder={i18n.t('init.sitename_en_placeholder')} class="text-base" />
                        </div>
                        <div class="space-y-2">
                            <Label class="text-gray-700 font-medium">{i18n.t('init.gid')}</Label>
                            <Input type="text" name="gid" placeholder="users" required class="text-base" />
                            <p class="text-sm text-gray-500">{i18n.t('init.gid_hint')}</p>
                        </div>
                        <div class="space-y-2">
                            <Label class="text-gray-700 font-medium">{i18n.t('init.shell')}</Label>
                            <Input type="text" name="shell" value="/bin/zsh" required class="text-base" />
                        </div>
                        <div class="space-y-2">
                            <Label class="text-gray-700 font-medium">{i18n.t('init.allowed_domains')}</Label>
                            <Input type="text" name="allowed_email_domains" placeholder="example.com,university.ac.kr" class="text-base" />
                            <p class="text-sm text-gray-500">{i18n.t('init.allowed_domains_hint')}</p>
                        </div>

                        {#if form?.error}
                        <Alert color="red" class="mt-4">{form.error_i18n ? i18n.t(form.error) : form.error}</Alert>
                        {/if}

                        {#if form?.success}
                        <Alert color="green" class="mt-4">{i18n.t('init.success')}</Alert>
                        {/if}

                        <div class="pt-4 flex gap-3">
                            <Button onclick={() => currentStep = 1} color="alternative" size="xl" class="flex-1">{i18n.t('init.previous')}</Button>
                            {#if submitting}
                                <Button color="green" size="xl" disabled class="flex-1">{i18n.t('init.submitting')}</Button>
                            {:else}
                                <Button type="submit" color="green" size="xl" class="flex-1">{i18n.t('init.submit')}</Button>
                            {/if}
                        </div>
                    </form>
                </div>
            {/if}
        </Card>
    </div>
</div>
