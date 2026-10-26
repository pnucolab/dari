<script>
    /*
        App sidebar. From the md breakpoint on it is always shown, fixed between the
        navbar (h-16) and the footer (h-14). Below md it is a drawer opened from the
        navbar's hamburger button (the `drawerHidden` store) with a backdrop;
        it closes on the backdrop, the close button, Escape and on navigation.
    */
    import { afterNavigate } from '$app/navigation';
    import { fly, fade } from 'svelte/transition';
    import { sineIn } from 'svelte/easing';
    import { drawerHidden } from '#lib/store.js';
    import CloseButton from './CloseButton.svelte';

    let { children } = $props();

    // The drawer starts closed (and stays closed while rendered on the server).
    drawerHidden.set(true);
    afterNavigate(() => drawerHidden.set(true));

    let width = $state(1024);
    let isDesktop = $derived(width >= 768);
    let drawerOpen = $derived(!isDesktop && !$drawerHidden);

    const close = () => drawerHidden.set(true);

    /** @param {KeyboardEvent} e */
    function onkeydown(e) {
        if (drawerOpen && e.key === 'Escape') close();
    }
</script>

<svelte:window bind:innerWidth={width} {onkeydown} />

{#snippet content()}
    <div class="h-full overflow-y-auto bg-white">
        <div class="flex items-end md:hidden">
            <CloseButton onclick={close} />
        </div>
        <div class="px-3 py-4">
            {@render children()}
        </div>
    </div>
{/snippet}

<!-- desktop: always visible, starts exactly at the navbar's bottom edge -->
<aside id="sidebar" class="fixed top-16 bottom-14 start-0 z-20 hidden w-64 border-r border-slate-300 bg-white md:block">
    {@render content()}
</aside>

<!-- mobile: drawer -->
{#if drawerOpen}
    <!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
    <div role="presentation" class="fixed inset-0 z-40 bg-gray-900/75 md:hidden" onclick={close} transition:fade={{ duration: 150 }}></div>
    <aside
        id="sidebar-drawer"
        class="fixed inset-y-0 start-0 z-50 w-64 border-r border-slate-300 bg-white md:hidden"
        transition:fly={{ x: -320, duration: 200, easing: sineIn }}
    >
        {@render content()}
    </aside>
{/if}
