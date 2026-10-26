/*
    Joins a component's base classes with the classes passed by its user.
    A base class is dropped when a passed class sets the same thing
    (e.g. `text-center` replaces `text-left`, `border-0` replaces `border`,
    `w-24` replaces `w-full`), so the passed class always wins.
*/
const groups = [
    /^text-(left|center|right|justify|start|end)$/,
    /^border(-[0-8])?$/,
    /^w-/,
    /^h-/,
    /^bg-/,
    /^rounded(-|$)/,
    /^p-/,
    /^px-/,
    /^py-/,
    /^shadow(-|$)/,
    /^text-(xs|sm|base|lg|xl|\dxl)$/,
];

/**
 * @param {string} base
 * @param {string | undefined | null | false} extra
 */
export function cx(base, extra) {
    const added = (extra || '').split(/\s+/).filter(Boolean);
    const taken = groups.filter((re) => added.some((c) => re.test(c)));
    const kept = base.split(/\s+/).filter((c) => c && !taken.some((re) => re.test(c)));
    return [...kept, ...added].join(' ');
}
