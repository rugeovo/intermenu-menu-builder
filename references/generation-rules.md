# Generation Rules

Use these rules to decide what files to generate, where state belongs, and how much logic to extract.

## Architecture First

Before writing YAML, decide:

- entry menu id
- submenu ids
- navigation edges
- required variables
- shared functions
- external dependencies

Write this plan down before generating the final files. If the menu graph is still unclear, do not start implementation.

## Menu Splitting Heuristics

Use one menu when:

- the request is a single read-only or lightly interactive screen
- there is no second-step confirmation
- no carried state is needed across screens

Use multiple menus when:

- a click should drill into detail or confirmation
- one screen selects data and another executes the action
- the screen needs separate browse and transaction modes
- there is a natural list/detail or buy/sell separation

## Variable Contract Design

Treat variable flow as an interface design problem.

For each variable, define:

- producer
- consumer
- default value
- mutation points
- whether it must survive a `menu open` transition

Every child menu should be renderable from its local defaults plus the variables explicitly passed to it.

## Function Extraction Heuristics

Create `functions/*.yml` when:

- the same JS logic appears more than once
- the menu contains loops over inventory contents
- you need helper abstractions such as `addToVariable`, `mergeAndCalculatePrice`, pagination, or sorting
- inline `menu-js` would obscure the main business flow

Keep inline JS when:

- it is one short expression or a trivial inventory flag change
- extraction would make the menu harder to read

If the same script or helper concept appears twice, check whether it should become a shared function before duplicating it again.

## Variable Design

Use menu variables for:

- selected item or target id
- page number
- quantity
- selected category
- derived totals that are reused

Do not overuse variables for constants already stored under `icons.<char>` or elsewhere in the config.

## Layout Design

- Use a border char such as `#` for fillers.
- Use a dedicated work-slot char such as `@` for editable or scanned slots, but other chars are also valid when the menu logic references them consistently.
- Keep actionable chars visually sparse enough that the layout remains readable.
- Reuse chars intentionally; repeated chars are a shared icon, not separate buttons.

## Placeholder Strategy

Prefer these mechanisms in this order:

1. `node` when the value already lives in config
2. `menu-get` when the value is runtime state
3. shared `utils` when the value needs JS logic

Avoid hardcoding the same business value in multiple places.

## Event And Refresh Placement

- Use `events.open` for first-render state.
- Use `events.post_open` only for work that is safe after the initial refresh.
- Use `task` only when the screen genuinely needs periodic refresh behavior.
- Pair every state mutation with the smallest valid UI refresh action.

## Assumptions and Dependencies

If the request implies an external dependency, surface it explicitly in the generated bundle summary:

- economy actions imply Vault or a compatible money plugin
- `%placeholder%` access implies PlaceholderAPI
- `itembase` may imply ItemsAdder, Oraxen, MMOItems, MythicMobs, or CraftEngine

Do not hide these dependencies.

## Final Checklist

Before finalizing, verify:

- every target menu id exists
- every submenu is reachable
- every `layout` row has length 9
- action keys are valid
- variable producers and consumers are consistent
- repeated JS is extracted
- unsupported display keys were not added by habit
- the bundle passes the validator
