<script>
    import { get } from '#lib/translations.js';

    let {
        items = [],
        selected = $bindable([]),
        labelKey = 'name',
        valueKey = 'value',
        placeholder,
        emptyText,
    } = $props();

    const i18n = get();

    let search = $state('');
    let open = $state(false);
    let inputEl = $state();
    let containerEl = $state();

    let filtered = $derived(items.filter(item => {
        const label = typeof item === 'string' ? item : item[labelKey];
        const value = typeof item === 'string' ? item : item[valueKey];
        if (selected.includes(value)) return false;
        return label.toLowerCase().includes(search.toLowerCase());
    }));

    function getLabel(value) {
        const item = items.find(i => (typeof i === 'string' ? i : i[valueKey]) === value);
        if (!item) return value;
        return typeof item === 'string' ? item : item[labelKey];
    }

    function select(item) {
        const value = typeof item === 'string' ? item : item[valueKey];
        selected = [...selected, value];
        search = '';
        inputEl?.focus();
    }

    function remove(value) {
        selected = selected.filter(v => v !== value);
        inputEl?.focus();
    }

    function handleKeydown(e) {
        if (e.key === 'Backspace' && search === '' && selected.length > 0) {
            selected = selected.slice(0, -1);
        }
        if (e.key === 'Escape') {
            open = false;
            inputEl?.blur();
        }
    }

    function handleFocus() {
        open = true;
    }

    function handleBlur(e) {
        if (containerEl?.contains(e.relatedTarget)) return;
        setTimeout(() => { open = false; }, 150);
    }
</script>

<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
<div class="relative w-full" bind:this={containerEl} onclick={(e) => { e.stopPropagation(); inputEl?.focus(); }}>
    <div
        class="flex flex-wrap items-center gap-1 min-h-[2.5rem] px-2 py-1 border border-gray-300 rounded-lg bg-gray-50 dark:bg-gray-700 dark:border-gray-600 cursor-text"
    >
        {#each selected as value (value)}
        <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-sm font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300">
            {getLabel(value)}
            <!-- svelte-ignore a11y_consider_explicit_label -->
            <button
                type="button"
                class="inline-flex items-center p-0.5 text-blue-400 hover:bg-blue-200 hover:text-blue-900 dark:hover:bg-blue-800 dark:hover:text-blue-300 rounded-xs"
                onmousedown={(e) => { e.preventDefault(); e.stopPropagation(); remove(value); }}
                onclick={(e) => { e.preventDefault(); e.stopPropagation(); }}
            >
                <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg>
            </button>
        </span>
        {/each}
        <input
            bind:this={inputEl}
            bind:value={search}
            onfocus={handleFocus}
            onblur={handleBlur}
            onkeydown={handleKeydown}
            class="flex-1 min-w-[80px] bg-transparent border-none outline-hidden p-1 text-sm dark:text-white"
            placeholder={placeholder ?? i18n.t('common.search')}
        />
    </div>
    {#if open}
    <div class="absolute z-50 w-full mt-1 max-h-48 overflow-y-auto bg-white border border-gray-200 rounded-lg shadow-lg dark:bg-gray-700 dark:border-gray-600">
        {#if filtered.length === 0}
        <div class="px-3 py-2 text-sm text-gray-500 dark:text-gray-400">{emptyText ?? i18n.t('common.no_items')}</div>
        {:else}
        {#each filtered as item}
        <button
            type="button"
            class="w-full px-3 py-2 text-sm text-left hover:bg-gray-100 dark:hover:bg-gray-600 dark:text-white"
            onmousedown={(e) => { e.preventDefault(); select(item); }}
        >
            {typeof item === 'string' ? item : item[labelKey]}
        </button>
        {/each}
        {/if}
    </div>
    {/if}
</div>
