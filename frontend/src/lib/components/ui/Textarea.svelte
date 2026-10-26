<script>
    let { value = $bindable(), class: className = '', ...rest } = $props();
</script>

<textarea
    bind:value
    {...rest}
    class="block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-50 {className}"
></textarea>
