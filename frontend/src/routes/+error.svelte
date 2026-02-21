<script>
    import { page } from '$app/stores';
    import { Heading } from 'flowbite-svelte';
 </script>
  
<div class="flex mx-auto flex-col text-center items-center justify-center fixed left-0 right-0 top-16 bottom-14">
    <Heading tag="h1" class="mb-4">{$page.status}</Heading>
    <Heading tag="h6">{$page.error.message}</Heading>
</div>