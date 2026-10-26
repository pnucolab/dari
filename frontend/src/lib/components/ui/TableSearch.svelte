<script>
    import { setContext } from 'svelte';
    import Icon from './Icon.svelte';
    import { cx } from './cx.js';

    /* Table with a search box on top; bind `inputValue` to filter the rows. */
    let { inputValue = $bindable(''), placeholder = '', hoverable = false, class: className = '', children, ...rest } = $props();

    setContext('table', { get hoverable() { return hoverable; }, search: true });

    const id = $props.id();
</script>

<div class="relative overflow-x-auto shadow-md sm:rounded-lg">
    <div class="p-4">
        <label for="{id}-search" class="sr-only">{placeholder}</label>
        <div class="relative mt-1">
            <div class="pointer-events-none absolute inset-y-0 start-0 flex items-center ps-3">
                <Icon name="search" class="w-5 h-5 text-gray-500" />
            </div>
            <input
                id="{id}-search"
                type="text"
                bind:value={inputValue}
                {placeholder}
                class="block w-80 max-w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 ps-10 text-sm text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
        </div>
    </div>
    <table {...rest} class={cx('w-full text-left text-sm text-gray-500', className)}>
        {@render children?.()}
    </table>
</div>
