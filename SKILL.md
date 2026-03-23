---
name: intermenu-menu-builder
description: Design and generate complete InterMenu menu bundles from natural-language requirements. Use when the task is to analyze, architect, implement, test, review, refactor, or expand InterMenu menus, linked submenus, bindings, functions, Kether actions, menu-js logic, placeholder-driven icons, or full YAML file sets for this project. Follow a staged workflow with requirement analysis, system design, implementation, testing, and review. Output complete files under menus/ and functions/, not partial snippets.
---

# InterMenu Menu Builder

Design InterMenu menu packs as small software modules, not as isolated YAML snippets. Never jump directly from the user's request to config output. Stabilize the requirements and the menu-system design first, then implement, test, and review.

## Mandatory Workflow

1. Load the references that define the runtime and the engineering process.
   - Always read `references/schema.md`.
   - Always read `references/runtime-semantics.md`.
   - Always read `references/generation-rules.md`.
   - Always read `references/engineering-workflow.md`.
   - Always read `references/test-review-checklist.md`.
   - Read `references/examples-shop.md` when the request involves linked menus, quantity adjustment, trading, pagination, or shared JS helpers.
   - Read `references/anti-patterns.md` before final review.
2. Perform requirement analysis before writing YAML.
   - Identify the user goal, actor actions, trigger entry points, happy path, failure path, and any background task behavior.
   - Identify all menus the system needs, not just the first visible screen.
   - Identify runtime state, passed variables, derived variables, and external dependencies.
   - Distinguish hard requirements from assumptions.
   - Ask a focused follow-up question only when ambiguity changes the architecture or the dependency model. Otherwise, state an explicit assumption and continue.
3. Produce a system design before implementation.
   - Decide the file graph first.
   - Define one responsibility per menu screen.
   - Define navigation edges and back paths.
   - Define each variable contract: who sets it, who reads it, when it must exist, and how it changes.
   - Decide where logic belongs: icon action, `events.open`, `events.post_open`, `task`, or shared `functions/*.yml`.
   - Decide the refresh strategy: `menu update <char>`, `menu refresh <char>`, or menu-js `menu.update()` / `menu.refresh()`.
4. Implement only after the design is coherent.
   - Generate complete files, not fragments.
   - Output a bundle root containing `menus/` and optional `functions/`.
   - Keep menu ids and filename stems consistent.
   - Prefer one menu file per screen.
   - Use templates from `assets/templates/` when they fit the architecture.
   - Extract shared JS into `functions/*.yml` when logic is reused or large enough to hide menu intent.
5. Test the design statically after implementation.
   - Run `python skills/scripts/validate_intermenu_bundle.py <bundle-root>`.
   - Fix structural errors and warnings that indicate likely logic defects.
   - Walk the menu flow manually with a scenario matrix: first render, each navigation edge, each confirmation path, empty-state behavior, repeated-click behavior, and close/reopen behavior.
6. Review the bundle before delivery.
   - Re-read `references/anti-patterns.md`.
   - Re-check variable lifecycles, menu reachability, dependency visibility, and first-render correctness.
   - If a risk cannot be eliminated, state it explicitly in the review section rather than silently shipping it.
7. Match the project's actual JS data model whenever writing `menu-js`.
   - InterMenu wraps config data through `ConfigurationJS`: config lists become JS arrays, and config maps become JS objects.
   - Use `length`, `[index]`, and property access like `prize.display` or `prize.weight`.
   - Do not use Java-style collection access such as `.size()`, `.get(index)`, or `.get("key")` on values returned from `config.getList(...)`, `config.getMapList(...)`, or similar helpers.

## Output Contract

Before the final files, provide staged engineering output. For non-trivial requests, use these sections in the same language as the user request:

- `需求分析`
- `系统设计`
- `系统实现`
- `测试`
- `审查`

This staging block is not part of the InterMenu YAML schema itself.

Each section must contain concrete content:

- `需求分析`: goal, scope, entry points, user flow, assumptions, dependencies
- `系统设计`: menu graph, file tree, variable contract, function ownership, refresh/update strategy
- `系统实现`: complete files or a statement that the files were written to disk
- `测试`: validator result plus scenario coverage and any untested parts
- `审查`: logic risks found, fixes applied, and remaining constraints

Do not collapse these sections into a vague summary. The point is to force deliberate design and review before the menu bundle is considered finished.

For non-trivial requests, the generated bundle should usually include:

- one entry menu
- zero or more submenu files
- zero or more shared function files

## Design Rules

- Model the result as a menu system, not a single file, unless the request is clearly one-screen only.
- Treat every `menu open ... with ...` call as an interface contract between two modules.
- Define a clear owner for every runtime variable.
- Use `events.open` for initial variable setup.
- Use `events.post_open` only for work that must happen after the initial `refresh`.
- Use Kether `menu update <char>` when only the rendered item content changes and the target is a single-letter icon id.
- Use Kether `menu refresh <char>` when icon conditions or sub-icon selection must be recomputed and the target is a single-letter icon id.
- Use `menu-js` with `menu.update()` / `menu.refresh()` for full-menu updates or when the target layout char is not a single letter such as `#` or `@`.
- Treat repeated layout chars as a shared icon state unless you are deliberately working per-slot.
- Use work-slot chars such as `@` when the layout needs storage or input slots without a clickable icon, but do not assume `@` is the only valid work-slot marker.
- Keep `display` definitions concise and push repeated business logic into placeholders, `menu-get`, `node`, or shared functions.
- Keep menus loosely coupled: pass only the child-menu inputs that the child actually consumes.

## Splitting Heuristics

Create multiple menu files when any of these are true:

- The request has a clear parent/child navigation flow.
- A click on one icon should open a new screen with carried variables.
- The screen needs distinct modes with different layouts.
- The screen mixes browsing with confirmation or transaction execution.

Create `functions/*.yml` when any of these are true:

- The same JS helper is used in multiple files.
- The JS is procedural and stateful enough to hide the menu intent.
- The request mentions pagination, inventory scans, quantity changes, filtering, sorting, or batch operations.

## System Design Expectations

Before implementation, define at least these artifacts mentally or explicitly:

- menu graph
- file tree
- variable contract table
- dependency list
- scenario test list

If any of these is still unclear, the design is not ready for YAML generation.

## Assumption Rules

- If the user does not specify plugin dependencies, make conservative assumptions and state them explicitly.
- If the user asks for a menu that depends on unsupported game data or third-party items, keep the structure valid and leave the dependency visible in the generated config.
- If the request is ambiguous, prefer a working pack with explicit assumptions over asking broad follow-up questions.

## Validation

Use the bundled validator after writing files:

```bash
python skills/scripts/validate_intermenu_bundle.py <bundle-root>
```

Recommended flow when generating menus inside this repository:

```bash
python skills/scripts/validate_intermenu_bundle.py src/main/resources/defaults/ch
```

## Resources

- `references/schema.md`: top-level file schema and field expectations
- `references/runtime-semantics.md`: execution order, icon refresh/update semantics, shared-char behavior
- `references/generation-rules.md`: generation heuristics and file-graph rules
- `references/engineering-workflow.md`: staged analysis/design/implementation workflow
- `references/test-review-checklist.md`: test matrix and review checklist for menu bundles
- `references/examples-shop.md`: breakdown of the default shop bundle pattern
- `references/anti-patterns.md`: invalid or risky patterns to avoid
- `assets/templates/`: starter templates for common menu shapes
- `scripts/validate_intermenu_bundle.py`: structural validator for generated bundles
