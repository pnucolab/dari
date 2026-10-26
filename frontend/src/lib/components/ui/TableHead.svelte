<script>
    let { class: className = '', children, ...rest } = $props();
</script>

<thead {...rest} class="bg-gray-50 text-xs uppercase text-gray-700 {className}">
    <tr>
        {@render children?.()}
    </tr>
</thead>
