<script>
    import CloseButton from './CloseButton.svelte';

    /* color: red | green | yellow | blue | gray */
    let { color = 'blue', dismissable = false, onclose = undefined, icon = undefined, class: className = '', children, ...rest } = $props();

    const colors = {
        red: 'bg-red-100 text-red-500',
        green: 'bg-green-100 text-green-500',
        yellow: 'bg-yellow-100 text-yellow-500',
        blue: 'bg-blue-100 text-blue-500',
        gray: 'bg-gray-100 text-gray-500',
    };

    let visible = $state(true);

    function close() {
        visible = false;
        onclose?.();
    }
</script>

{#if visible}
    <div role="alert" {...rest} class="gap-3 rounded-lg p-4 text-sm {colors[color]} {icon || dismissable ? 'flex items-center' : ''} {className}">
        {@render icon?.()}
        {#if icon || dismissable}
            <div>{@render children?.()}</div>
        {:else}
            {@render children?.()}
        {/if}
        {#if dismissable}
            <CloseButton onclick={close} class="ms-auto -my-1.5 -me-1.5 text-current hover:bg-white/50 hover:text-current" />
        {/if}
    </div>
{/if}
