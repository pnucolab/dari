<script>
    import { getContext } from 'svelte';

    let { class: className = '', children, ...rest } = $props();

    const table = getContext('table') ?? { hoverable: false, search: false };
</script>

<tr {...rest} class="bg-white {table.search ? '' : 'border-b last:border-b-0'} {table.hoverable ? 'hover:bg-gray-50' : ''} {className}">
    {@render children?.()}
</tr>
