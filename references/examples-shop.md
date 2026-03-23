# Example Pattern: Default Shop Bundle

Use the default shop bundle as the reference model for non-trivial InterMenu systems.

## File Graph

```text
menus/shop/shop.yml
menus/shop/buy.yml
menus/shop/sell.yml
functions/shop/shop.yml
```

## Why This Example Matters

It demonstrates all of the patterns this skill should reproduce when appropriate:

- entry menu plus linked submenus
- `menu open ... with ...` variable passing
- runtime quantity state via `menu-set` and `menu-get`
- shared JS helpers in `functions/*.yml`
- work-slot chars for inventory processing
- placeholder-driven item reuse with `node`

## Entry Menu Responsibilities

The entry shop menu:

- binds a command such as `shop`
- renders product icons
- stores per-product values under each icon node
- opens `buy` or `sell` submenus with the required variables

This is the right pattern when the first menu is a catalog and the second menu performs the transaction.

## Buy Menu Responsibilities

The buy menu:

- initializes quantity in `events.open`
- uses buttons to mutate a runtime variable
- updates only the central summary icon with `menu update D`
- reads passed variables such as `buy` and `material`

This is the right pattern when the user needs an adjustable quantity and a final confirmation action.

## Sell Menu Responsibilities

The sell menu:

- uses a work-slot char like `@` as the item drop zone
- keeps the work-slot char in `layout`
- accesses those slots from JS helpers
- performs settlement when the confirm icon is clicked

This is the right pattern when the menu needs to scan arbitrary inventory or GUI contents.

## Shared Functions Responsibilities

The shared function file:

- defines quantity mutation helpers
- defines item matching and price aggregation helpers
- keeps the menu YAML focused on business flow

This is the right pattern when multiple menus or multiple icons need the same procedural JS.

## Reusable Lessons

- Split browse and transaction screens.
- Pass only the child-menu variables you actually need.
- Store stable item metadata under icon nodes and reuse it with `node`.
- Put loops and inventory scans into `functions/*.yml`.
