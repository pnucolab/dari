<script>
    import { page } from '$app/state';
    import Icon from './Icon.svelte';

    /* Sidebar link; highlighted when `href` is the current path. */
    let { href, label, icon } = $props();

    let active = $derived(page.url.pathname === href);
</script>

<li>
    <a
        {href}
        aria-current={active ? 'page' : undefined}
        class="group flex items-center rounded-sm p-2 text-base font-normal text-gray-900 hover:bg-gray-100 {active ? 'bg-gray-200' : ''}"
    >
        <Icon name={icon} class="w-6 h-6 text-gray-500 transition duration-75 group-hover:text-gray-900" />
        <span class="ms-3">{label}</span>
    </a>
</li>
