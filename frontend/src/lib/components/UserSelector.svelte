<script>
    import MultiSelect from './MultiSelect.svelte';
    import { get } from '#lib/translations.js';

    let { users = [], selected = $bindable([]) } = $props();

    const i18n = get();

    let items = $derived(users.map(u => ({
        name: u.linux?.username ? `${u.linux.username} (${u.profile?.name || u.username})` : u.username,
        value: u.linux?.username || u.username,
    })));
</script>

<MultiSelect
    {items}
    bind:selected
    labelKey="name"
    valueKey="value"
    placeholder={i18n.t('common.search_user')}
    emptyText={i18n.t('common.no_users')}
/>
