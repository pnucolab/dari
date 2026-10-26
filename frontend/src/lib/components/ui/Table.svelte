<script>
    import { setContext } from 'svelte';
    import { cx } from './cx.js';

    /* Table with a horizontally scrolling wrapper; rows read `hoverable` from the context. */
    let { hoverable = false, class: className = '', divClass = 'relative overflow-x-auto', children, ...rest } = $props();

    setContext('table', { get hoverable() { return hoverable; }, search: false });
</script>

<div class={divClass}>
    <table {...rest} class={cx('w-full text-left text-sm text-gray-500', className)}>
        {@render children?.()}
    </table>
</div>
