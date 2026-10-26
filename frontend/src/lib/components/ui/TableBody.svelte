<script>
    let { class: className = '', children, ...rest } = $props();
</script>

<tbody {...rest} class={className}>
    {@render children?.()}
</tbody>
