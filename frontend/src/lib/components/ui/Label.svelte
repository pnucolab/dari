<script>
    let { class: className = '', children, ...rest } = $props();
</script>

<label {...rest} class="block text-sm font-medium text-gray-700 {className}">{@render children?.()}</label>
