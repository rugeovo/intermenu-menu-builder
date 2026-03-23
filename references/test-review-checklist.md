# Test And Review Checklist

Use this checklist after generating the bundle.

## Scenario Matrix

Test mentally or with concrete examples:

- first render of every menu
- every `menu open` transition
- every confirmation or commit action
- every cancel or back action
- empty inventory or empty data state
- minimum and maximum quantity or page values
- close and reopen behavior
- task-driven refresh behavior when a task exists

## Variable Lifecycle Checklist

For every variable:

- where is it first set
- which menu reads it
- whether it is passed across menus
- whether it needs a default value
- whether it should be deleted or reset

Common failure modes:

- child menu reads a variable never passed in
- source menu passes variables child never uses
- first render depends on a variable only initialized in `post_open`
- state mutation happens but no matching update or refresh is triggered

## Menu Graph Checklist

- every destination menu id exists
- every submenu is reachable
- every child menu has an exit path when the flow requires one
- command bindings do not collide unless intentional

## Logic Placement Checklist

- quick variable initialization belongs in `events.open`
- long repeated JS belongs in `functions/*.yml`
- `menu update <char>` is used only when icon selection does not change
- `menu refresh <char>` is used when sub-icon conditions must be recomputed
- menu-js `menu.update()` / `menu.refresh()` is used for whole-menu or non-letter char updates

## Review Output Checklist

State all of these in the final review block:

- what was validated automatically
- what was only reasoned about manually
- what risks were found and fixed
- what assumptions remain in the bundle
