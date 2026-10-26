<script>
    import MultiSelect from './MultiSelect.svelte';
    import { get } from '#lib/translations.js';

    let { groups = [], selected = $bindable([]) } = $props();

    const i18n = get();

    let items = $derived(groups.map(g => ({ name: g.name, value: g.name })));
</script>

<MultiSelect
    {items}
    bind:selected
    labelKey="name"
    valueKey="value"
    placeholder={i18n.t('common.search_group')}
    emptyText={i18n.t('common.no_groups')}
/>
