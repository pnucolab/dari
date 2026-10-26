<script>
    // `color` is accepted for compatibility; the checkbox is always blue.
    let { checked = $bindable(false), color = 'blue', class: className = '', ...rest } = $props();
</script>

<input
    type="checkbox"
    bind:checked
    {...rest}
    class="me-2 h-4 w-4 shrink-0 cursor-pointer rounded-sm border-gray-300 bg-gray-100 accent-blue-700 focus:ring-2 focus:ring-blue-600 {className}"
/>
