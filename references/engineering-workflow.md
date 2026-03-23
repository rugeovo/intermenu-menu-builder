# Engineering Workflow

Use this workflow whenever turning a natural-language request into an InterMenu bundle.

## Phase 1: Requirement Analysis

Reduce the request into a small functional spec before touching YAML.

Capture:

- user goal
- entry trigger such as command, item binding, or parent menu
- core user flow
- alternate flow
- failure or empty-state flow
- runtime state that must survive clicks or screen changes
- third-party dependencies

Ask a follow-up question only when the answer changes the architecture, menu graph, or dependency set. Otherwise, make an explicit assumption and continue.

## Phase 2: System Design

Treat the bundle like a small feature module.

Define:

- entry menu id
- submenu ids
- navigation edges
- back or exit behavior
- variable contracts
- shared function boundaries
- refresh strategy per state transition

Every `menu open ... with ...` call is an interface:

- source menu is the caller
- destination menu is the callee
- passed variables are the input contract

Do not pass variables the destination never reads. Do not let the destination rely on variables with no clear producer.

## Phase 3: System Implementation

Implementation should follow the design rather than discovering the design halfway through YAML generation.

Rules:

- keep one screen per menu file
- keep filename stem equal to menu id
- move repeated JS into `functions/*.yml`
- initialize first-render state in `events.open`
- use `post_open` only for work that truly depends on the initial refresh

## Phase 4: Static Testing

Before delivery, run both tool-based and reasoning-based checks.

Tool-based:

- run the bundled validator
- resolve missing menu links
- resolve invalid action keys
- resolve suspicious unused or unreachable menus when possible

Reasoning-based:

- simulate first open
- simulate each click path
- simulate back navigation
- simulate empty or zero-data state
- simulate repeated interactions that mutate variables

## Phase 5: Review

Review the bundle as if you were doing a code review.

Check:

- does every menu have a clear purpose
- does every variable have an owner
- does every child menu receive all required inputs
- are dependencies visible to the user
- are there any menus or functions that cannot be reached

Do not hide residual risk. Surface it explicitly in the review output.
