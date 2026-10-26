<script>
    let { class: className = '', children, ...rest } = $props();
</script>

<th {...rest} class="px-6 py-3 {className}">{@render children?.()}</th>
