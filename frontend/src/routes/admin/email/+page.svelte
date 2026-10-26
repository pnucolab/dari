<script>
    import { enhance } from '$app/forms';
    import {
        Alert,
        Button,
        Card,
        Checkbox,
        Input,
        Label,
        Modal,
        Select,
        Textarea,
    } from '#lib/components/ui/index.js';
    import { get } from '#lib/translations.js';

    let { data } = $props();

    const i18n = get();

    // SMTP settings modal
    let smtpModal = $state(false);
    let smtp = $state({
        smtp_host: '',
        smtp_port: '',
        smtp_security: 'starttls',
        smtp_user: '',
        smtp_password: '',
        smtp_password_clear: false,
        smtp_from: '',
        smtp_subject_prefix: '',
        to: '',
    });
    /** @type {null | { action: string, success?: boolean, error?: string, detail?: string, to?: string }} */
    let smtpResult = $state(null);
    let smtpBusy = $state('');
    let passwordSet = $derived(!!data.smtp?.smtp_password_set);

    function openSmtp() {
        const s = data.smtp ?? {};
        smtp = {
            smtp_host: s.smtp_host ?? '',
            smtp_port: s.smtp_port ?? '',
            smtp_security: s.smtp_security || 'starttls',
            smtp_user: s.smtp_user ?? '',
            smtp_password: '',
            smtp_password_clear: false,
            smtp_from: s.smtp_from ?? '',
            smtp_subject_prefix: s.smtp_subject_prefix ?? '',
            to: smtp.to || data.adminEmail || '',
        };
        smtpResult = null;
        smtpBusy = '';
        smtpModal = true;
    }

    /** @type {import('./$types').SubmitFunction} */
    function handleSmtp({ action }) {
        const save = action.search.includes('smtptest') ? false : true;
        smtpBusy = save ? 'save' : 'test';
        smtpResult = null;
        return async ({ result, update }) => {
            smtpBusy = '';
            if (result.type === 'success' || result.type === 'failure') {
                smtpResult = result.data?.smtp ?? { action: save ? 'save' : 'test', error: 'unknown' };
            } else {
                smtpResult = { action: save ? 'save' : 'test', error: 'unknown' };
            }
            if (save && result.type === 'success' && result.data?.smtp?.success) {
                smtp.smtp_password = '';
                smtp.smtp_password_clear = false;
            }
            // keep the modal and its (possibly unsaved) values; reload the settings after a save
            await update({ reset: false, invalidateAll: save && !!smtpResult?.success });
        };
    }

    /** @param {string | undefined} error */
    function smtpError(error) {
        const known = ['invalid_port', 'invalid_security', 'no_recipient', 'send_failed'];
        return i18n.t(`admin.smtp.error_${known.includes(error ?? '') ? error : 'unknown'}`);
    }
</script>

<Modal bind:open={smtpModal} title={i18n.t('admin.smtp.title')} size="lg">
    <form method="POST" action="?/smtp" id="smtp-form" class="space-y-4" use:enhance={handleSmtp}>
        {#if !data.smtp}
        <Alert color="yellow">{i18n.t('admin.smtp.load_failed')}</Alert>
        {/if}
        <div class="grid gap-4 md:grid-cols-6">
            <div class="flex flex-col gap-2 md:col-span-3">
                <Label for="smtp_host">{i18n.t('admin.smtp.host')}</Label>
                <Input id="smtp_host" name="smtp_host" bind:value={smtp.smtp_host} placeholder="smtp.example.com" autocomplete="off" />
            </div>
            <div class="flex flex-col gap-2 md:col-span-1">
                <Label for="smtp_port">{i18n.t('admin.smtp.port')}</Label>
                <Input id="smtp_port" name="smtp_port" inputmode="numeric" bind:value={smtp.smtp_port} placeholder="587" autocomplete="off" />
            </div>
            <div class="flex flex-col gap-2 md:col-span-2">
                <Label for="smtp_security">{i18n.t('admin.smtp.security')}</Label>
                <Select id="smtp_security" name="smtp_security" bind:value={smtp.smtp_security}>
                    <option value="ssl">{i18n.t('admin.smtp.security_ssl')}</option>
                    <option value="starttls">{i18n.t('admin.smtp.security_starttls')}</option>
                    <option value="none">{i18n.t('admin.smtp.security_none')}</option>
                </Select>
            </div>
            <div class="flex flex-col gap-2 md:col-span-3">
                <Label for="smtp_user">{i18n.t('admin.smtp.user')}</Label>
                <Input id="smtp_user" name="smtp_user" bind:value={smtp.smtp_user} autocomplete="off" />
            </div>
            <div class="flex flex-col gap-2 md:col-span-3">
                <Label for="smtp_password">{i18n.t('admin.smtp.password')}</Label>
                <Input
                    type="password"
                    id="smtp_password"
                    name="smtp_password"
                    bind:value={smtp.smtp_password}
                    disabled={smtp.smtp_password_clear}
                    autocomplete="new-password"
                    placeholder={passwordSet ? i18n.t('admin.smtp.password_saved') : i18n.t('admin.smtp.password_not_set')}
                />
                {#if passwordSet}
                <label class="flex items-center gap-2 text-sm text-gray-700">
                    <Checkbox name="smtp_password_clear" value="1" bind:checked={smtp.smtp_password_clear} />
                    {i18n.t('admin.smtp.password_clear')}
                </label>
                {/if}
            </div>
            <div class="flex flex-col gap-2 md:col-span-3">
                <Label for="smtp_from">{i18n.t('admin.smtp.from')}</Label>
                <Input id="smtp_from" name="smtp_from" bind:value={smtp.smtp_from} placeholder="IT Service Portal <noreply@example.com>" autocomplete="off" />
            </div>
            <div class="flex flex-col gap-2 md:col-span-3">
                <Label for="smtp_subject_prefix">{i18n.t('admin.smtp.subject_prefix')}</Label>
                <Input id="smtp_subject_prefix" name="smtp_subject_prefix" bind:value={smtp.smtp_subject_prefix} placeholder="[IT Service Portal] " autocomplete="off" />
            </div>
        </div>

        <div class="grid gap-2 rounded-lg border border-gray-200 bg-gray-50 p-4">
            <Label for="smtp_to">{i18n.t('admin.smtp.test_title')}</Label>
            <p class="mb-0! text-sm text-gray-500">{i18n.t('admin.smtp.test_hint')}</p>
            <div class="flex flex-col gap-2 sm:flex-row">
                <Input type="email" id="smtp_to" name="to" bind:value={smtp.to} placeholder={i18n.t('admin.smtp.test_to')} />
                <Button type="submit" color="alternative" formaction="?/smtptest" disabled={!!smtpBusy} class="shrink-0">
                    {smtpBusy === 'test' ? i18n.t('admin.smtp.testing') : i18n.t('admin.smtp.test_send')}
                </Button>
            </div>
        </div>

        {#if smtpResult}
            {#if smtpResult.success}
            <Alert color="green" data-smtp-result="success">
                {smtpResult.action === 'test' ? i18n.t('admin.smtp.test_success', { to: smtpResult.to ?? '' }) : i18n.t('admin.smtp.saved')}
            </Alert>
            {:else}
            <Alert color="red" data-smtp-result="error">
                <p class="mb-0! font-medium">{smtpError(smtpResult.error)}</p>
                {#if smtpResult.detail}
                <p class="mb-0! mt-1 break-all font-mono text-xs">{smtpResult.detail}</p>
                {/if}
            </Alert>
            {/if}
        {/if}
    </form>
    {#snippet footer()}
        <Button color="blue" type="submit" form="smtp-form" disabled={!!smtpBusy}>
            {smtpBusy === 'save' ? i18n.t('admin.smtp.saving') : i18n.t('common.save')}
        </Button>
        <Button color="alternative" onclick={() => smtpModal = false}>{i18n.t('user.close')}</Button>
    {/snippet}
</Modal>

<div class="grid gap-4 p-4 w-full">
    <Card size="xl" class="p-4 sm:p-6 text-gray-500">
        <div class="mb-5 flex flex-wrap items-center justify-between gap-3">
            <h5 class="text-2xl font-bold tracking-tight text-gray-900">{i18n.t('admin.email.title')}</h5>
            <Button color="alternative" size="sm" onclick={openSmtp}>{i18n.t('admin.smtp.open')}</Button>
        </div>
        <form method="POST" action="?/email" class="w-full">
            <div class="grid gap-6 mb-6">
                <div class="grid gap-2">
                    <Label for="email_subject">{i18n.t('admin.email.subject')}</Label>
                    <Input type="text" id="email_subject" name="subject" />
                </div>
                <div class="grid gap-2">
                    <Label for="email_body">{i18n.t('admin.email.body')}</Label>
                    <Textarea rows="20" id="email_body" name="body" />
                </div>
            </div>
            <Button type="submit" color="blue" size="xl" class="w-full">{i18n.t('admin.email.send')}</Button>
        </form>
    </Card>
</div>
