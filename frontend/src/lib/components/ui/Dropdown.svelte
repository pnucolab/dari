<script>
    /*
        Menu that opens below its trigger button.
        - trigger: snippet with the button content; `label` is its accessible name
        - children: the menu items (use DropdownItem)
        Closes on a click outside, on Escape and when an item is chosen.
    */
    let {
        open = $bindable(false),
        label = undefined,
        triggerClass = '',
        class: className = '',
        trigger,
        children,
    } = $props();

    let root = $state();

    /** @param {MouseEvent} e */
    function onDocumentClick(e) {
        if (open && root && e.target instanceof Node && !root.contains(e.target)) open = false;
    }

    /** @param {KeyboardEvent} e */
    function onKeydown(e) {
        if (open && e.key === 'Escape') open = false;
    }

    /** @param {MouseEvent} e */
    function onMenuClick(e) {
        if (e.target instanceof Element && e.target.closest('a, button')) open = false;
    }
</script>

<svelte:document onclick={onDocumentClick} onkeydown={onKeydown} />

<div class="relative" bind:this={root}>
    <button
        type="button"
        aria-haspopup="menu"
        aria-expanded={open}
        aria-label={label}
        class="flex items-center focus:outline-none {triggerClass}"
        onclick={() => (open = !open)}
    >
        {@render trigger()}
    </button>
    {#if open}
        <!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_noninteractive_element_interactions -->
        <ul
            role="menu"
            class="absolute end-0 top-full z-50 mt-2 min-w-36 overflow-hidden rounded-lg border border-gray-100 bg-white py-2 text-sm text-gray-700 shadow-md {className}"
            onclick={onMenuClick}
        >
            {@render children?.()}
        </ul>
    {/if}
</div>
