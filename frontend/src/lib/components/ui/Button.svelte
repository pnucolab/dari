<script>
    /*
        Button (or link styled as a button when `href` is given).
        color: blue | red | green | alternative | light | dark
        size: xs | sm | md | lg | xl
    */
    import { cx } from './cx.js';

    let {
        color = 'blue',
        size = 'md',
        outline = false,
        pill = false,
        href = undefined,
        type = 'button',
        disabled = false,
        class: className = '',
        children,
        ...rest
    } = $props();

    const solid = {
        blue: 'text-white bg-blue-700 hover:bg-blue-800 focus-visible:ring-blue-300',
        red: 'text-white bg-red-700 hover:bg-red-800 focus-visible:ring-red-300',
        green: 'text-white bg-green-700 hover:bg-green-800 focus-visible:ring-green-300',
        dark: 'text-white bg-gray-800 hover:bg-gray-900 focus-visible:ring-gray-300',
        light: 'text-gray-900 bg-white border border-gray-300 hover:bg-gray-100 focus-visible:ring-gray-200',
        alternative: 'text-gray-900 bg-transparent border border-gray-200 hover:bg-gray-100 hover:text-primary-700 focus-visible:ring-gray-200',
    };
    const outlined = {
        blue: 'text-blue-700 border-blue-700 hover:bg-blue-800 focus-visible:ring-blue-300',
        red: 'text-red-700 border-red-700 hover:bg-red-800 focus-visible:ring-red-300',
        green: 'text-green-700 border-green-700 hover:bg-green-800 focus-visible:ring-green-300',
        dark: 'text-gray-900 border-gray-800 hover:bg-gray-900 focus-visible:ring-gray-300',
        light: 'text-gray-700 border-gray-700 hover:bg-gray-800 focus-visible:ring-gray-200',
        alternative: 'text-gray-700 border-gray-700 hover:bg-gray-800 focus-visible:ring-gray-200',
    };
    const sizes = {
        xs: 'px-3 py-2 text-xs',
        sm: 'px-4 py-2 text-sm',
        md: 'px-5 py-2.5 text-sm',
        lg: 'px-5 py-3 text-base',
        xl: 'px-6 py-3.5 text-base',
    };

    let classes = $derived(cx([
        'inline-flex items-center justify-center text-center font-medium focus:outline-none focus-visible:ring-4',
        outline ? `bg-transparent border hover:text-white ${outlined[color]}` : solid[color],
        sizes[size],
        pill ? 'rounded-full' : 'rounded-lg',
        disabled ? 'cursor-not-allowed opacity-50' : '',
    ].join(' '), className));
</script>

{#if href !== undefined}
    <a {href} {...rest} class={classes}>{@render children?.()}</a>
{:else}
    <button {type} {disabled} {...rest} class={classes}>{@render children?.()}</button>
{/if}
