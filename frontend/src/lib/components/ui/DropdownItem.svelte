<script>
    let { href = undefined, class: className = '', children, ...rest } = $props();

    const cls = 'block w-full whitespace-nowrap px-4 py-2 text-left font-medium hover:bg-gray-100';
</script>

<li role="none">
    {#if href !== undefined}
        <a role="menuitem" {href} {...rest} class="{cls} {className}">{@render children?.()}</a>
    {:else}
        <button role="menuitem" type="button" {...rest} class="{cls} {className}">{@render children?.()}</button>
    {/if}
</li>
