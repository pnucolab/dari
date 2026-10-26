<script>
    /* Text-like <input>. `class` is added to the input; pass a w-* class to override the full width. */
    import { cx } from './cx.js';

    let { value = $bindable(), type = 'text', class: className = '', ...rest } = $props();
</script>

{#if type === 'hidden'}
    <input type="hidden" bind:value {...rest} />
{:else}
    <input
        {type}
        bind:value
        {...rest}
        class={cx('block w-full rounded-lg border border-gray-300 bg-gray-50 px-2.5 py-2.5 text-sm text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-50', className)}
    />
{/if}
