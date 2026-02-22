<script>
    import MultiSelect from './MultiSelect.svelte';

    export let users = [];
    export let selected = [];

    $: items = users.map(u => ({
        name: u.linux?.username ? `${u.linux.username} (${u.profile?.name || u.username})` : u.username,
        value: u.linux?.username || u.username,
    }));
</script>

<MultiSelect
    {items}
    bind:selected
    labelKey="name"
    valueKey="value"
    placeholder="사용자 검색..."
    emptyText="사용자가 없습니다."
/>
