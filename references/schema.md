# InterMenu Bundle Schema

Use this reference when converting a request into files under a bundle root.

## Bundle Layout

Recommended generated structure:

```text
<bundle-root>/
|- menus/
|  |- main.yml
|  \- sub/
|     \- detail.yml
\- functions/
   \- shared.yml
```

`menu open <id>` should target the menu id represented by the filename stem.

## Menu File Shape

Each menu file is a YAML mapping with these runtime-core top-level sections:

- `title`: string
- `layout`: list of 1-6 strings, each length 9
- `bindings`: optional mapping
- `events`: optional mapping
- `task`: optional mapping
- `icons`: mapping

Custom top-level nodes are also valid when they are consumed by menu logic, for example through `config.getString()`, `config.getMap()`, `config.getStringList()`, `{node:...}`, or shared JS helpers. Treat the fixed fields above as the core runtime schema, not as a closed list of all legal top-level keys.

## Layout Rules

- Each row must be exactly 9 characters.
- Spaces represent empty slots.
- Non-space chars usually correspond to `icons.<char>`.
- Work-slot chars are allowed when scripts interact with them directly, such as `@`.
- `@` is only a convention. Any layout char can be used as a work slot when the menu logic reads or writes it intentionally.

## Bindings

`bindings` may contain:

- `commands`: list of strings
- `items`: list of mappings with nested `display`

Use `commands` for entry menus. Use `items` only when the request explicitly needs an item trigger.

## Events

Supported menu lifecycle hooks:

- `open`
- `post_open`
- `close`
- `click`

All event bodies are scripts. They may contain Kether and `menu-js`.

## Task

Use a `task` section only when the request needs periodic refresh behavior.

- `period`: positive integer tick interval
- `script`: Kether script

If `task.period` is lower than `task.min_period` in the plugin `config.yml`, the runtime clamps it up to that minimum instead of using the smaller value.

Avoid adding a task by default.

## Icons

Icon keys should be a single layout character. The runtime only uses the first character of the YAML key, so multi-character keys may parse but are still invalid configuration.

Common shape:

```yaml
icons:
  "A":
    display:
      material: "STONE"
      name: "&fExample"
    actions:
      left: |-
        menu close
```

Optional icon members:

- custom per-icon data, such as `buy`, `sell`, `material`, `targetMenu`
- `display`
- `actions`
- `icons` for sub-icons
- `cooldown`

## Display

Common `display` keys:

- `material`
- `itembase`
- `name`
- `lore`
- `amount`
- `damage`
- `unbreakable`
- `customModelData`
- `itemModel`
- `shiny`
- `color`
- `itemFlags`
- `enchants`
- `hideTooltip`
- `tooltipStyle`
- `texture`

Additional supported keys:

- `attributeModifiers`
- `potionEffects`
- `potionColor`
- `food`
- `tool`
- `maxStackSize`
- `rarity`

Use `itembase` when the item should come from an external item provider rather than a vanilla material.

Some advanced display keys depend on newer Bukkit or Paper APIs. Generate them only when the requirement calls for them and the target runtime is expected to support them.

## Actions

Common action keys:

- `all`
- `left`
- `right`
- `shift_left`
- `shift_right`
- `middle`

The runtime also accepts other Bukkit `ClickType` names converted to lowercase snake case, such as:

- `double_click`
- `drop`
- `control_drop`
- `number_key`
- `swap_offhand`
- `window_border_left`
- `window_border_right`
- `creative`

Keep action scripts close to the user intent. If the same JS appears repeatedly, move it to `functions/*.yml`.

## Sub-Icons

Use sub-icons for stateful variants of the same layout char.

```yaml
icons:
  "V":
    display:
      material: "BARRIER"
    icons:
      100:
        condition: perm server.vip
        display:
          material: "EMERALD"
```

Rules:

- Sub-icon priorities are numeric.
- Higher numeric priority wins.
- If no condition matches, the base `display` and base `actions` are used.

## Text and Value Reuse

Useful value sources:

- `@icon@`
- `{node:path}`
- `{kether:...}`
- `menu-get` / `menu-set`

Prefer these to duplicating literals across similar icons.
