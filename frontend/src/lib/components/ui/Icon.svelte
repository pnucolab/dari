<script>
    /*
        Inline SVG icons (paths from the MIT-licensed icon set by Themesberg).
        Only the icons the app uses are included; `name` picks one.
    */
    const icons = {
        'chart-pie': { solid: false, paths: [{d: "M10 6.025A7.5 7.5 0 1 0 17.975 14H10V6.025Z", cap: "round", join: "round"}, {d: "M13.5 3c-.169 0-.334.014-.5.025V11h7.975c.011-.166.025-.331.025-.5A7.5 7.5 0 0 0 13.5 3Z", cap: "round", join: "round"}] },
        'globe': { solid: false, paths: [{d: "M4.37 7.657c2.063.528 2.396 2.806 3.202 3.87 1.07 1.413 2.075 1.228 3.192 2.644 1.805 2.289 1.312 5.705 1.312 6.705M20 15h-1a4 4 0 0 0-4 4v1M8.587 3.992c0 .822.112 1.886 1.515 2.58 1.402.693 2.918.351 2.918 2.334 0 .276 0 2.008 1.972 2.008 2.026.031 2.026-1.678 2.026-2.008 0-.65.527-.9 1.177-.9H20M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z", cap: "round"}] },
        'terminal': { solid: false, paths: [{d: "m8 9 3 3-3 3m5 0h3M4 19h16a1 1 0 0 0 1-1V6a1 1 0 0 0-1-1H4a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1Z", cap: "round", join: "round"}] },
        'users-group': { solid: false, paths: [{d: "M4.5 17H4a1 1 0 0 1-1-1 3 3 0 0 1 3-3h1m0-3.05A2.5 2.5 0 1 1 9 5.5M19.5 17h.5a1 1 0 0 0 1-1 3 3 0 0 0-3-3h-1m0-3.05a2.5 2.5 0 1 0-2-4.45m.5 13.5h-7a1 1 0 0 1-1-1 3 3 0 0 1 3-3h3a3 3 0 0 1 3 3 1 1 0 0 1-1 1Zm-1-9.5a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0Z", cap: "round"}] },
        'adjustments-horizontal': { solid: false, paths: [{d: "M20 6H10m0 0a2 2 0 1 0-4 0m4 0a2 2 0 1 1-4 0m0 0H4m16 6h-2m0 0a2 2 0 1 0-4 0m4 0a2 2 0 1 1-4 0m0 0H4m16 6H10m0 0a2 2 0 1 0-4 0m4 0a2 2 0 1 1-4 0m0 0H4", cap: "round"}] },
        'server': { solid: false, paths: [{d: "M5 12a1 1 0 0 0-1 1v4a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-4a1 1 0 0 0-1-1M5 12h14M5 12a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1m-2 3h.01M14 15h.01M17 9h.01M14 9h.01", cap: "round", join: "round"}] },
        'user': { solid: false, paths: [{d: "M7 17v1a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1v-1a3 3 0 0 0-3-3h-4a3 3 0 0 0-3 3Zm8-9a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"}] },
        'envelope': { solid: false, paths: [{d: "m3.5 5.5 7.893 6.036a1 1 0 0 0 1.214 0L20.5 5.5M4 19h16a1 1 0 0 0 1-1V6a1 1 0 0 0-1-1H4a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1Z", cap: "round"}] },
        'arrow-left': { solid: false, paths: [{d: "M5 12h14M5 12l4-4m-4 4 4 4", cap: "round", join: "round"}] },
        'folder': { solid: false, paths: [{d: "M13.5 8H4m0-2v13a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1V9a1 1 0 0 0-1-1h-5.032a1 1 0 0 1-.768-.36l-1.9-2.28a1 1 0 0 0-.768-.36H5a1 1 0 0 0-1 1Z", cap: "round", join: "round"}] },
        'clipboard-list': { solid: false, paths: [{d: "M15 4h3a1 1 0 0 1 1 1v15a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1h3m0 3h6m-3 5h3m-6 0h.01M12 16h3m-6 0h.01M10 3v4h4V3h-4Z", cap: "round", join: "round"}] },
        'language': { solid: false, paths: [{d: "m13 19 3.5-9 3.5 9m-6.125-2h5.25M3 7h7m0 0h2m-2 0c0 1.63-.793 3.926-2.239 5.655M7.5 6.818V5m.261 7.655C6.79 13.82 5.521 14.725 4 15m3.761-2.345L5 10m2.761 2.655L10.2 15", cap: "round", join: "round"}] },
        'plus': { solid: false, paths: [{d: "M5 12h14m-7 7V5", cap: "round", join: "round"}] },
        'trash-bin': { solid: false, paths: [{d: "M5 7h14m-9 3v8m4-8v8M10 3h4a1 1 0 0 1 1 1v3H9V4a1 1 0 0 1 1-1ZM6 7h12v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V7Z", cap: "round", join: "round"}] },
        'edit': { solid: false, paths: [{d: "m14.304 4.844 2.852 2.852M7 7H4a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h11a1 1 0 0 0 1-1v-4.5m2.409-9.91a2.017 2.017 0 0 1 0 2.853l-6.844 6.844L8 14l.713-3.565 6.844-6.844a2.015 2.015 0 0 1 2.852 0Z", cap: "round", join: "round"}] },
        'check-plus-circle': { solid: false, paths: [{d: "M12 21a9 9 0 1 1 0-18c1.052 0 2.062.18 3 .512M7 9.577l3.923 3.923 8.5-8.5M17 14v6m-3-3h6", cap: "round", join: "round"}] },
        'exclamation-circle': { solid: false, paths: [{d: "M12 13V8m0 8h.01M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z", cap: "round", join: "round"}] },
        'ban': { solid: false, paths: [{d: "m6 6 12 12m3-6a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z", cap: "round"}] },
        'chevron-left': { solid: false, paths: [{d: "m14 8-4 4 4 4", cap: "round", join: "round"}] },
        'chevron-right': { solid: false, paths: [{d: "m10 16 4-4-4-4", cap: "round", join: "round"}] },
        'info-circle-solid': { solid: true, paths: [{d: "M2 12C2 6.477 6.477 2 12 2s10 4.477 10 10-4.477 10-10 10S2 17.523 2 12Zm9.408-5.5a1 1 0 1 0 0 2h.01a1 1 0 1 0 0-2h-.01ZM10 10a1 1 0 1 0 0 2h1v3h-1a1 1 0 1 0 0 2h4a1 1 0 1 0 0-2h-1v-4a1 1 0 0 0-1-1h-2Z", evenodd: true}] },
        'exclamation-circle-solid': { solid: true, paths: [{d: "M2 12C2 6.477 6.477 2 12 2s10 4.477 10 10-4.477 10-10 10S2 17.523 2 12Zm11-4a1 1 0 1 0-2 0v5a1 1 0 1 0 2 0V8Zm-1 7a1 1 0 1 0 0 2h.01a1 1 0 1 0 0-2H12Z", evenodd: true}] },
        'close': { solid: true, viewBox: '0 0 20 20', paths: [{d: "M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z", evenodd: true}] },
        'menu': { solid: false, paths: [{d: "M4 6h16M4 12h16M4 18h16", cap: "round", join: "round"}] },
        'search': { solid: true, viewBox: '0 0 20 20', paths: [{d: "M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z", evenodd: true}] },
        'avatar': { solid: true, viewBox: '0 0 16 16', paths: [{d: "M8 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z", evenodd: true}] },
    };

    /** @type {{ name: keyof typeof icons, class?: string, strokeWidth?: number | string, [key: string]: any }} */
    let { name, class: className = 'w-5 h-5', strokeWidth = 2, ...rest } = $props();

    let icon = $derived(icons[name]);
</script>

<svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox={icon.viewBox ?? '0 0 24 24'}
    fill={icon.solid ? 'currentColor' : 'none'}
    aria-hidden="true"
    {...rest}
    class="shrink-0 {className}"
>
    {#each icon.paths as p}
        {#if icon.solid}
            <path d={p.d} fill-rule={p.evenodd ? 'evenodd' : undefined} clip-rule={p.evenodd ? 'evenodd' : undefined} />
        {:else}
            <path d={p.d} stroke="currentColor" stroke-width={strokeWidth} stroke-linecap={p.cap} stroke-linejoin={p.join} />
        {/if}
    {/each}
</svg>
