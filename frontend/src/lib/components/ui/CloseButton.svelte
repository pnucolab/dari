<script>
    import Icon from './Icon.svelte';
    import { get } from '#lib/translations.js';

    const i18n = get();

    let { label = undefined, class: className = '', ...rest } = $props();
</script>

<button
    type="button"
    aria-label={label ?? i18n.t('common.close')}
    {...rest}
    class="m-0.5 rounded-lg p-1.5 text-gray-500 hover:bg-gray-200 hover:text-gray-900 focus:outline-none focus-visible:ring-2 focus-visible:ring-gray-400 {className}"
>
    <Icon name="close" class="w-5 h-5" />
</button>
