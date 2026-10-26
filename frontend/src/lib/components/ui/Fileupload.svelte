<script>
    let { files = $bindable(), class: className = '', ...rest } = $props();
</script>

<input
    type="file"
    bind:files
    {...rest}
    class="block w-full cursor-pointer rounded-lg border border-gray-300 bg-gray-50 text-sm text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 file:me-4 file:cursor-pointer file:border-0 file:bg-gray-800 file:px-4 file:py-2.5 file:text-sm file:font-medium file:text-white hover:file:bg-gray-700 {className}"
/>
