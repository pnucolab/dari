<script>
    /* size: sm (max-w-sm, default) | md | lg | xl (no max width) */
    import { cx } from './cx.js';

    let { size = 'sm', class: className = '', children, ...rest } = $props();

    const sizes = { xs: 'max-w-xs', sm: 'max-w-sm', md: 'max-w-lg', lg: 'max-w-2xl', xl: 'max-w-none' };
</script>

<div {...rest} class={cx(`flex w-full flex-col rounded-lg border border-gray-200 bg-white shadow-md ${sizes[size]}`, className)}>
    {@render children?.()}
</div>
