<script>
    import MultiSelect from './MultiSelect.svelte';

    export let groups = [];
    export let selected = [];

    $: items = groups.map(g => ({ name: g.name, value: g.name }));
</script>

<MultiSelect
    {items}
    bind:selected
    labelKey="name"
    valueKey="value"
    placeholder="그룹 검색..."
    emptyText="그룹이 없습니다."
/>
