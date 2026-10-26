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
    let { form, data } = $props();

    const i18n = get();

    let defaults = $derived(data.defaults);

    // Top bar: two colors, the shares always add up to 100%
    let barColor1 = $state('#00b600');
    let barColor2 = $state('#0047b4');
    let barRatio1 = $state(66.3);
    $effect.pre(() => {
        barColor1 = defaults.bar_color1 || '#00b600';
        barColor2 = defaults.bar_color2 || '#0047b4';
        barRatio1 = Number(defaults.bar_ratio ?? 66.3);
    });
    let barRatio2 = $derived(Math.round((100 - barRatio1) * 10) / 10);
    const clamp = (v) => Math.min(100, Math.max(0, Math.round(Number(v) * 10) / 10 || 0));

    let success = $state(false);
    function handleSubmit() {
        success = false;
        return async ({ result, update }) => {
            if (result.type === 'success') {
                success = true;
            }
            await update({ reset: false });
        };
    }
</script>

<div class="p-4 w-full">
    <Card size="xl" class="p-4 sm:p-6 text-gray-500 dark:text-gray-400">
        <h5 class="mb-5 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">{i18n.t('admin.menu.settings')}</h5>
        <form method="POST" enctype="multipart/form-data" action="?/defaults" use:enhance={handleSubmit}>
            <div class="grid gap-2 mb-3">
                <Label>{i18n.t('admin.settings.logo')}</Label>
                <Fileupload name="logo" />
            </div>
            <div class="grid gap-2 mb-3">
                <Label>{i18n.t('admin.settings.sitename')}</Label>
                <Input type="text" name="sitename" value={defaults.sitename} required />
            </div>
            <div class="grid gap-2 mb-3">
                <Label>{i18n.t('admin.settings.sitename_en')}</Label>
                <Input type="text" name="sitename_en" value={defaults.sitename_en ?? ''} />
            </div>
            <div class="grid gap-2 mb-3">
                <Label>{i18n.t('admin.settings.bar_color')}</Label>
                <div class="flex flex-wrap items-center gap-6">
                    <div class="flex items-center gap-2">
                        <input type="color" name="bar_color1" bind:value={barColor1} class="h-9 w-12 cursor-pointer rounded border border-gray-300" />
                        <Input type="number" min="0" max="100" step="0.1" class="w-24" value={barRatio1}
                            oninput={(e) => barRatio1 = clamp(e.currentTarget.value)} />
                        <span>%</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <input type="color" name="bar_color2" bind:value={barColor2} class="h-9 w-12 cursor-pointer rounded border border-gray-300" />
                        <Input type="number" min="0" max="100" step="0.1" class="w-24" value={barRatio2}
                            oninput={(e) => barRatio1 = clamp(100 - Number(e.currentTarget.value))} />
                        <span>%</span>
                    </div>
                </div>
                <input type="hidden" name="bar_ratio" value={barRatio1} />
                <div class="h-2 w-full rounded" style="background: linear-gradient(90deg, {barColor1} 0%, {barColor1} {barRatio1}%, {barColor2} {barRatio1}%, {barColor2} 100%);"></div>
            </div>
            <div class="grid gap-2 mb-3">
                <Label>{i18n.t('admin.settings.gid')}</Label>
                <Input type="text" name="gid" value={defaults.gid} />
            </div>
            <div class="grid gap-2 mb-5">
                <Label>{i18n.t('admin.settings.shell')}</Label>
                <Input type="text" name="shell" value={defaults.shell} />
            </div>
            <div class="grid gap-2 mb-5">
                <Label>{i18n.t('admin.settings.allowed_domains')}</Label>
                <Input type="text" name="allowed_email_domains" value={defaults.allowed_email_domains} />
            </div>
            {#if success}
            <Alert class="mb-4" color="green" dismissable onclose={() => success = false}>{i18n.t('admin.settings.saved')}</Alert>
            {/if}
            {#if form?.error}
            <Alert class="mb-4" color="red" dismissable>{i18n.t(form.error)}</Alert>
            {/if}
            <div class="text-center mb-2">
                <Button type="submit" color="blue" class="w-32">{i18n.t('common.save')}</Button>
            </div>
        </form>
    </Card>
</div>