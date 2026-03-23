# Runtime Semantics

Use these rules when deciding where variables are set and when icons are updated.

## Menu Open Order

The runtime flow is:

1. build inventory from `layout`
2. register icon placeholders
3. run `events.open`
4. run `refresh()` for all icons
5. run `events.post_open`
6. start task
7. open the inventory

Implications:

- Initialize menu variables in `events.open` when they are needed by `{kether:menu-get ...}` or conditional sub-icons during the first render.
- Use `post_open` only for work that must happen after the initial refresh.

## Update vs Refresh

- Kether `menu update <char>` updates rendered item content using cached icon state.
- Kether `menu refresh <char>` recomputes sub-icon conditions and then updates the rendered item.
- In the current runtime, Kether only recognizes a single-letter icon id here. `menu update` or `menu refresh` without a valid single-letter id is a no-op.
- Use `menu-js` with `menu.update()` / `menu.refresh()` when you need to update the whole menu, or when the target layout char is not a single letter.

Choose `update` for numeric or text changes inside an already-selected state. Choose `refresh` for state transitions such as locked/unlocked, claimed/unclaimed, or available/unavailable.

## Shared State Per Layout Char

Multiple slots with the same layout char share the same icon state. A refresh resolves the icon once for that char, then applies it to all matching slots.

Implications:

- Repeated chars are good for borders and duplicated buttons.
- Do not expect repeated chars to hold independent sub-icon state.

## Work-Slot Chars

Some layout chars may intentionally have no `icons` entry and are used as storage or input slots that scripts access with helpers such as:

- `menu.getSlots("@")`
- `menu.getCharItems("@")`
- `menu.setCharItem("@", item)`

Use this pattern for inventory drop zones, recipe inputs, or batch-processing slots. `@` is only a convention; any layout char can be used if the menu logic treats it as a work slot.

## Functions and JS Context

`functions/*.yml` contributes JS helpers under the `utils` object. Inside `menu-js`, the runtime exposes:

- `player`
- `menu`
- `inventory`
- `config`
- `clickEvent` when present in click-related execution
- `closeEvent` when present in close-related execution
- `utils`

The runtime also injects internal context variables such as `__chestMenu__`. Those are implementation details, so generated bundles should normally rely only on the stable helpers listed above.

Configuration data exposed through `config` follows the project's JavaScript wrapper semantics rather than raw Java collection semantics:

- `config.getList(...)`, `config.getMapList(...)`, and similar list-returning helpers produce JS arrays. Use `length` and `[index]`, not `.size()` or `.get(index)`.
- Map-like values returned from config become JS objects. Use property access such as `prize.display`, `display.name`, or bracket access like `prize["weight"]`, not `.get("display")`.
- When in doubt, write `menu-js` as if config values were plain JS arrays and objects.

Use shared functions for repetitive procedural logic such as:

- pagination
- quantity adjustment
- merging similar items
- derived pricing
- bulk inventory scans

## Menu Variables

InterMenu exposes menu instance variables through both Kether and JS.

- Kether: `menu-set`, `menu-get`, `menu-del`, `menu-has`
- JS: `menu.setVar`, `menu.getVar`

Use variables for cross-screen data transfer and per-session menu state.

## Linked Menu Pattern

When one menu opens another with carried state:

```kether
menu open buy with buy {node:icons.@icon@.buy} with material {node:icons.@icon@.material}
```

Design implications:

- The destination menu must be able to render correctly from passed variables alone.
- The source menu should pass only the data the child menu actually needs.
