<script>
    import { page } from '$app/state';
 </script>
  
<div class="flex mx-auto flex-col text-center items-center justify-center fixed left-0 right-0 top-16 bottom-14">
    <h1 class="mb-4 text-5xl font-extrabold text-gray-900">{page.status}</h1>
    <h6 class="text-lg font-bold text-gray-900">{page.error?.message}</h6>
</div>