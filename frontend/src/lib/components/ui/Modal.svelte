<script>
    /*
        Modal dialog on top of the native <dialog> element (showModal): the rest of
        the page is inert while it is open, so focus stays inside it.
        Closes on Escape, on a click on the backdrop and with the close button.
        - title: optional header text (with the close button in the header)
        - size: xs | sm | md | lg | xl
        - autoclose: close when any button inside it is clicked
        - footer: optional snippet rendered below the body
    */
    import CloseButton from './CloseButton.svelte';

    let {
        open = $bindable(false),
        title = undefined,
        size = 'md',
        autoclose = false,
        dismissable = true,
        class: className = '',
        bodyClass = '',
        children,
        footer = undefined,
        ...rest
    } = $props();

    const sizes = { xs: 'max-w-md', sm: 'max-w-lg', md: 'max-w-2xl', lg: 'max-w-4xl', xl: 'max-w-7xl' };

    const close = () => (open = false);

    /** @param {HTMLDialogElement} dialog */
    function show(dialog) {
        dialog.showModal();
        queueMicrotask(() => {
            const el = dialog.querySelector('[data-autofocus]') ??
                dialog.querySelector('input:not([type=hidden]), textarea, select, button:not([aria-label])');
            if (el instanceof HTMLElement) el.focus();
            else dialog.focus();
        });
        return () => dialog.close();
    }

    /** @param {Event} e */
    function oncancel(e) {
        // Escape key
        e.preventDefault();
        if (dismissable) close();
    }

    /** @param {MouseEvent & { currentTarget: HTMLDialogElement }} e */
    function onclick(e) {
        const dialog = e.currentTarget;
        if (e.target === dialog) {
            // the backdrop belongs to the dialog element itself
            const r = dialog.getBoundingClientRect();
            const inside = e.clientX >= r.left && e.clientX <= r.right && e.clientY >= r.top && e.clientY <= r.bottom;
            if (!inside && dismissable) close();
            return;
        }
        if (autoclose && e.target instanceof Element && e.target.closest('button')) {
            close();
        }
    }
</script>

{#if open}
    <dialog
        {@attach show}
        tabindex="-1"
        {oncancel}
        {onclick}
        {...rest}
        class="m-auto w-full {sizes[size]} max-h-[calc(100%-2rem)] flex-col divide-y divide-gray-300 overflow-hidden rounded-lg bg-white p-0 text-gray-500 shadow-xl backdrop:bg-gray-900/50 open:flex {className}"
    >
        {#if title}
            <div class="flex shrink-0 items-center justify-between rounded-t-lg p-4 text-xl font-semibold text-gray-900 md:p-5">
                <h3>{title}</h3>
                {#if dismissable}
                    <CloseButton onclick={close} />
                {/if}
            </div>
        {:else if dismissable}
            <CloseButton onclick={close} class="absolute end-2.5 top-2.5" />
        {/if}
        <div class="space-y-4 overflow-y-auto overscroll-contain p-4 md:p-5 {bodyClass}">
            {@render children?.()}
        </div>
        {#if footer}
            <div class="flex shrink-0 items-center gap-3 rounded-b-lg p-4 md:p-5">
                {@render footer()}
            </div>
        {/if}
    </dialog>
{/if}
