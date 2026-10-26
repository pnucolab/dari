<script>
    let { class: className = '', children, ...rest } = $props();
</script>

<td {...rest} class="whitespace-nowrap px-6 py-4 font-medium {className}">{@render children?.()}</td>
