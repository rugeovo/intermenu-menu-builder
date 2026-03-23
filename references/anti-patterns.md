# Anti-Patterns

Check this file before finalizing generated menus.

## Structural Mistakes

- Do not output isolated YAML fragments when the request implies multiple linked menus.
- Do not add custom top-level keys that nothing reads. Extra top-level nodes are fine only when they are consumed by `config`, `{node:...}`, JS helpers, or menu scripts.
- Do not use layout rows that are not exactly 9 characters wide.
- Do not forget `display` on clickable icons.

## Runtime Mistakes

- Do not place first-render variables in `post_open` when icon placeholders need them during the initial refresh.
- Do not use `menu update` when a sub-icon condition must be recomputed.
- Do not use Kether `menu update` or `menu refresh` without a single-letter icon id and expect it to update the whole menu.
- Do not assume repeated chars are independent per-slot buttons.
- Do not treat values returned from `config.getList(...)` or `config.getMapList(...)` as Java `List` or `Map` instances inside `menu-js`; they are exposed as JS arrays and JS objects, so `.size()`, `.get(index)`, and `.get("key")` are invalid.

## Logic Placement Mistakes

- Do not inline long duplicate JS blocks in many icons.
- Do not store runtime state in duplicated config literals when `menu-get` should be used.
- Do not use `itembase` and then rely on `material` as if both will apply equally.

## Compatibility Mistakes

These display keys are supported by the current runtime, but some depend on newer server APIs. Generate them only when the requirement is explicit and the target environment is expected to support them:

- `attributeModifiers`
- `potionEffects`
- `potionColor`
- `food`
- `tool`
- `maxStackSize`
- `rarity`

## Bundle Integrity Mistakes

- Do not reference a menu id that is not generated in the same bundle.
- Do not pass variables through `menu open ... with ...` that the destination menu never uses.
- Do not let a child menu depend on a runtime variable that has no visible producer.
- Do not leave submenu files unreachable unless they are intentionally command-bound entry menus.
- Do not create command bindings that collide across generated entry menus unless the user asked for it.
- Do not hide external dependencies such as Vault, PlaceholderAPI, or item-library plugins.
