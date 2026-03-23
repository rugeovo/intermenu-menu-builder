#!/usr/bin/env python3
"""
Validate a generated InterMenu bundle rooted at a directory that contains:

- menus/
- optional functions/

Example:
    python skills/intermenu-menu-builder/scripts/validate_intermenu_bundle.py src/main/resources/defaults/ch
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

try:
    import yaml
except ImportError as exc:  # pragma: no cover - environment specific
    print("[ERROR] Missing dependency: PyYAML (`pip install pyyaml`).")
    raise SystemExit(2) from exc


VALID_ACTION_KEYS = {
    "all",
    "left",
    "right",
    "shift_left",
    "shift_right",
    "middle",
    "double_click",
    "drop",
    "control_drop",
    "number_key",
    "swap_offhand",
    "window_border_left",
    "window_border_right",
    "creative",
    "unknown",
}

MENU_OPEN_RE = re.compile(r"\bmenu\s+open\s+([A-Za-z0-9_\-]+)\b")
MENU_OPEN_LINE_RE = re.compile(r"\bmenu\s+open\s+([A-Za-z0-9_\-]+)\b")
MENU_OPEN_WITH_RE = re.compile(r"\bwith\s+([A-Za-z_][A-Za-z0-9_]*)\b")
MENU_OP_RE = re.compile(r"\bmenu\s+(update|refresh)(?:\s+([^\s]+))?\b")
UTILS_CALL_RE = re.compile(r"\butils\.([A-Za-z_][A-Za-z0-9_]*)\s*\(")
FUNCTION_DEF_RE = re.compile(r"\bfunction\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")
FUNCTION_START_RE = re.compile(r"(?m)^function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")
KETHER_MENU_GET_RE = re.compile(r"\bmenu-get\s+([A-Za-z_][A-Za-z0-9_]*)\b")
KETHER_MENU_HAS_RE = re.compile(r"\bmenu-has\s+([A-Za-z_][A-Za-z0-9_]*)\b")
KETHER_MENU_SET_RE = re.compile(r"\bmenu-set\s+([A-Za-z_][A-Za-z0-9_]*)\b")
JS_MENU_GET_RE = re.compile(r"""\bmenu\.getVar\(\s*(['"])([A-Za-z_][A-Za-z0-9_]*)\1\s*\)""")
JS_MENU_SET_RE = re.compile(r"""\bmenu\.setVar\(\s*(['"])([A-Za-z_][A-Za-z0-9_]*)\1""")
WORK_CHAR_CONFIG_KEY_RE = re.compile(r"char$", re.IGNORECASE)
WORK_SLOT_LITERAL_RE = re.compile(
    r"""
    \bmenu\.
    (?:
        getSlots|
        getCharItems|
        setCharItem|
        getFirstSlot
    )
    \(\s*(['"])(.)\1
    """,
    re.VERBOSE,
)


@dataclass
class Results:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    @property
    def ok(self) -> bool:
        return not self.errors


@dataclass
class MenuContract:
    path: Path
    incoming_edges: set[str] = field(default_factory=set)
    incoming_vars: set[str] = field(default_factory=set)
    consumed_vars: set[str] = field(default_factory=set)
    produced_vars: set[str] = field(default_factory=set)
    post_open_vars: set[str] = field(default_factory=set)
    command_bindings: list[str] = field(default_factory=list)


def load_yaml(path: Path):
    try:
        with path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle)
    except Exception as exc:
        raise ValueError(f"failed to parse YAML: {exc}") from exc


def iter_menu_files(bundle_root: Path) -> list[Path]:
    menus_dir = bundle_root / "menus"
    return sorted(menus_dir.rglob("*.yml")) if menus_dir.is_dir() else []


def iter_function_files(bundle_root: Path) -> list[Path]:
    functions_dir = bundle_root / "functions"
    return sorted(functions_dir.rglob("*.yml")) if functions_dir.is_dir() else []


def collect_menu_ids(menu_files: Iterable[Path]) -> tuple[dict[str, Path], set[str]]:
    ids: dict[str, Path] = {}
    duplicates: set[str] = set()
    for path in menu_files:
        menu_id = path.stem
        if menu_id in ids:
            duplicates.add(menu_id)
        ids.setdefault(menu_id, path)
    return ids, duplicates


def validate_layout(path: Path, data: dict, results: Results) -> set[str]:
    layout = data.get("layout")
    seen_chars: set[str] = set()
    if not isinstance(layout, list) or not layout:
        results.error(f"{path}: missing or invalid `layout` list")
        return seen_chars
    if len(layout) > 6:
        results.error(f"{path}: layout has {len(layout)} rows; expected 1-6")
    for index, row in enumerate(layout, start=1):
        if not isinstance(row, str):
            results.error(f"{path}: layout row {index} is not a string")
            continue
        if len(row) != 9:
            results.error(f"{path}: layout row {index} length is {len(row)}; expected 9")
        seen_chars.update(ch for ch in row if ch != " ")
    return seen_chars


def validate_bindings(path: Path, data: dict, results: Results) -> list[str]:
    commands: list[str] = []
    bindings = data.get("bindings")
    if bindings is None:
        return commands
    if not isinstance(bindings, dict):
        results.error(f"{path}: `bindings` must be a mapping")
        return commands
    if "commands" in bindings:
        if not isinstance(bindings["commands"], list) or not all(
            isinstance(item, str) for item in bindings["commands"]
        ):
            results.error(f"{path}: `bindings.commands` must be a list of strings")
        else:
            commands = list(bindings["commands"])
    if "items" in bindings:
        items = bindings["items"]
        if not isinstance(items, list):
            results.error(f"{path}: `bindings.items` must be a list")
        else:
            for idx, item in enumerate(items, start=1):
                if not isinstance(item, dict):
                    results.error(f"{path}: bindings.items[{idx}] must be a mapping")
                    continue
                display = item.get("display")
                if not isinstance(display, dict):
                    results.error(f"{path}: bindings.items[{idx}].display must be a mapping")
    return commands


def validate_events(path: Path, data: dict, results: Results) -> list[str]:
    scripts: list[str] = []
    events = data.get("events")
    if events is None:
        return scripts
    if not isinstance(events, dict):
        results.error(f"{path}: `events` must be a mapping")
        return scripts
    for key, value in events.items():
        if not isinstance(value, str):
            results.error(f"{path}: events.{key} must be a string script")
            continue
        scripts.append(value)
    return scripts


def validate_task(path: Path, data: dict, results: Results) -> list[str]:
    scripts: list[str] = []
    task = data.get("task")
    if task is None:
        return scripts
    if not isinstance(task, dict):
        results.error(f"{path}: `task` must be a mapping")
        return scripts
    period = task.get("period")
    if period is not None and not isinstance(period, int):
        results.error(f"{path}: task.period must be an integer when present")
    if isinstance(period, int) and period <= 0:
        results.error(f"{path}: task.period must be > 0")
    script = task.get("script")
    if script is not None:
        if not isinstance(script, str):
            results.error(f"{path}: task.script must be a string")
        else:
            scripts.append(script)
    return scripts


def validate_display(path: Path, icon_id: str, display: dict, results: Results) -> None:
    if "itembase" in display and "material" in display:
        results.warn(
            f"{path}: icons.{icon_id}.display defines both `itembase` and `material`; "
            "runtime will prefer the item-provider path"
        )


def validate_actions(path: Path, icon_id: str, actions: dict, results: Results) -> list[str]:
    scripts: list[str] = []
    if not isinstance(actions, dict):
        results.error(f"{path}: icons.{icon_id}.actions must be a mapping")
        return scripts
    for key, value in actions.items():
        if key not in VALID_ACTION_KEYS:
            results.error(f"{path}: icons.{icon_id}.actions contains invalid action key `{key}`")
        if not isinstance(value, str):
            results.error(f"{path}: icons.{icon_id}.actions.{key} must be a string script")
            continue
        scripts.append(value)
    return scripts


def collect_configured_work_chars(data: dict) -> set[str]:
    chars: set[str] = set()
    for key, value in data.items():
        if not isinstance(key, str):
            continue
        if not WORK_CHAR_CONFIG_KEY_RE.search(key):
            continue
        if isinstance(value, str) and value:
            chars.add(value[0])
    return chars


def collect_script_work_chars(script: str) -> set[str]:
    return {char for _, char in WORK_SLOT_LITERAL_RE.findall(script) if char and char != " "}


def collect_function_work_chars(function_code: str) -> dict[str, set[str]]:
    matches = list(FUNCTION_START_RE.finditer(function_code))
    work_chars_by_function: dict[str, set[str]] = {}
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(function_code)
        body = function_code[start:end]
        work_chars_by_function[match.group(1)] = collect_script_work_chars(body)
    return work_chars_by_function


def collect_function_produced_vars(function_code: str) -> dict[str, set[str]]:
    matches = list(FUNCTION_START_RE.finditer(function_code))
    produced_vars_by_function: dict[str, set[str]] = {}
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(function_code)
        body = function_code[start:end]
        produced_vars_by_function[match.group(1)] = collect_produced_vars(body)
    return produced_vars_by_function


def collect_menu_open_calls(script: str) -> list[tuple[str, set[str]]]:
    calls: list[tuple[str, set[str]]] = []
    for line in script.splitlines():
        match = MENU_OPEN_LINE_RE.search(line)
        if not match:
            continue
        menu_id = match.group(1)
        passed_vars = set(MENU_OPEN_WITH_RE.findall(line[match.end() :]))
        calls.append((menu_id, passed_vars))
    return calls


def collect_consumed_vars(text: str) -> set[str]:
    consumed = set(KETHER_MENU_GET_RE.findall(text))
    consumed.update(KETHER_MENU_HAS_RE.findall(text))
    consumed.update(var_name for _, var_name in JS_MENU_GET_RE.findall(text))
    return consumed


def collect_produced_vars(text: str) -> set[str]:
    produced = set(KETHER_MENU_SET_RE.findall(text))
    produced.update(var_name for _, var_name in JS_MENU_SET_RE.findall(text))
    return produced


def validate_menu_operations(path: Path, script: str, results: Results) -> None:
    for operation, raw_target in MENU_OP_RE.findall(script):
        if not raw_target:
            results.warn(
                f"{path}: `menu {operation}` without a single-letter target is a no-op in Kether; "
                "use menu-js `menu.update()` / `menu.refresh()` for whole-menu updates"
            )
            continue
        if len(raw_target) != 1 or not raw_target.isalpha():
            results.warn(
                f"{path}: `menu {operation} {raw_target}` will not be parsed as a Kether icon target; "
                "use menu-js when targeting non-letter layout chars"
            )


def warn_on_menu_contracts(menu_contracts: dict[str, MenuContract], results: Results) -> None:
    for menu_id in sorted(menu_contracts):
        contract = menu_contracts[menu_id]

        if not contract.incoming_edges and not contract.command_bindings:
            results.warn(
                f"{contract.path}: menu `{menu_id}` has no incoming `menu open` reference and no command binding; "
                "verify that the menu is reachable"
            )

        for var_name in sorted(contract.incoming_vars - contract.consumed_vars):
            results.warn(
                f"{contract.path}: menu `{menu_id}` receives variable `{var_name}` but does not appear to consume it"
            )

        if contract.incoming_vars or not contract.command_bindings:
            unresolved = sorted(contract.consumed_vars - contract.produced_vars - contract.incoming_vars)
            for var_name in unresolved:
                results.warn(
                    f"{contract.path}: menu `{menu_id}` consumes variable `{var_name}` without a visible producer; "
                    "confirm that it is initialized locally or passed by the caller"
                )

        for var_name in sorted(contract.post_open_vars & contract.consumed_vars):
            results.warn(
                f"{contract.path}: variable `{var_name}` is set in `events.post_open` and also consumed in this menu; "
                "confirm that the first render does not depend on it"
            )


def validate_subicons(path: Path, icon_id: str, icon_data: dict, results: Results) -> list[str]:
    scripts: list[str] = []
    sub_icons = icon_data.get("icons")
    if sub_icons is None:
        return scripts
    if not isinstance(sub_icons, dict):
        results.error(f"{path}: icons.{icon_id}.icons must be a mapping")
        return scripts
    for priority, sub_data in sub_icons.items():
        try:
            int(str(priority))
        except ValueError:
            results.error(f"{path}: icons.{icon_id}.icons priority `{priority}` is not numeric")
        if not isinstance(sub_data, dict):
            results.error(f"{path}: icons.{icon_id}.icons.{priority} must be a mapping")
            continue
        condition = sub_data.get("condition")
        if not isinstance(condition, str):
            results.error(f"{path}: icons.{icon_id}.icons.{priority}.condition must be a string")
        else:
            scripts.append(condition)
        display = sub_data.get("display")
        if not isinstance(display, dict):
            results.error(f"{path}: icons.{icon_id}.icons.{priority}.display must be a mapping")
        else:
            validate_display(path, f"{icon_id}.icons.{priority}", display, results)
        actions = sub_data.get("actions")
        if actions is not None:
            scripts.extend(validate_actions(path, f"{icon_id}.icons.{priority}", actions, results))
    return scripts


def validate_icons(path: Path, data: dict, results: Results) -> tuple[list[str], set[str]]:
    scripts: list[str] = []
    icon_ids: set[str] = set()
    icons = data.get("icons")
    if not isinstance(icons, dict) or not icons:
        results.error(f"{path}: missing or invalid `icons` mapping")
        return scripts, icon_ids

    for raw_icon_id, icon_data in icons.items():
        icon_id = str(raw_icon_id)
        icon_ids.add(icon_id[:1])
        if len(icon_id) != 1:
            results.warn(f"{path}: icon key `{icon_id}` is not a single character; runtime uses the first one")
        if not isinstance(icon_data, dict):
            results.error(f"{path}: icons.{icon_id} must be a mapping")
            continue
        display = icon_data.get("display")
        if not isinstance(display, dict):
            results.error(f"{path}: icons.{icon_id}.display must be a mapping")
        else:
            validate_display(path, icon_id, display, results)
        actions = icon_data.get("actions")
        if actions is not None:
            scripts.extend(validate_actions(path, icon_id, actions, results))
        scripts.extend(validate_subicons(path, icon_id, icon_data, results))

    return scripts, icon_ids


def warn_on_unbound_layout_chars(
    path: Path,
    layout_chars: set[str],
    icon_ids: set[str],
    allowed_work_chars: set[str],
    results: Results,
) -> None:
    missing = sorted(char for char in layout_chars if char not in icon_ids and char not in allowed_work_chars)
    for char in missing:
        results.warn(
            f"{path}: layout char `{char}` is used without an icon definition; "
            "treat as intentional only when the slot is filled dynamically"
        )

    dead = sorted(icon_id for icon_id in icon_ids if icon_id not in layout_chars)
    for icon_id in dead:
        results.warn(f"{path}: icon `{icon_id}` is defined but not used in layout")


def validate_functions(
    path: Path, results: Results
) -> tuple[set[str], dict[str, set[str]], dict[str, set[str]]]:
    data = load_yaml(path)
    if not isinstance(data, dict):
        results.error(f"{path}: function file must be a YAML mapping")
        return set(), {}, {}
    functions_block = data.get("functions")
    if not isinstance(functions_block, str):
        results.error(f"{path}: top-level `functions` must be a string block")
        return set(), {}, {}
    function_names = set(FUNCTION_DEF_RE.findall(functions_block))
    return (
        function_names,
        collect_function_work_chars(functions_block),
        collect_function_produced_vars(functions_block),
    )


def validate_menus(
    bundle_root: Path,
    menu_files: list[Path],
    menu_id_map: dict[str, Path],
    allowed_work_chars: set[str],
    util_work_chars: dict[str, set[str]],
    util_produced_vars: dict[str, set[str]],
    results: Results,
) -> tuple[set[str], dict[str, MenuContract]]:
    called_utils: set[str] = set()
    command_owner: dict[str, Path] = {}
    menu_contracts = {
        menu_id: MenuContract(path=menu_path) for menu_id, menu_path in menu_id_map.items()
    }

    for path in menu_files:
        try:
            data = load_yaml(path)
        except ValueError as exc:
            results.error(f"{path}: {exc}")
            continue

        if not isinstance(data, dict):
            results.error(f"{path}: menu file must be a YAML mapping")
            continue
        title = data.get("title")
        if not isinstance(title, str) or not title.strip():
            results.error(f"{path}: missing or invalid `title`")

        menu_id = path.stem
        contract = menu_contracts[menu_id]
        raw_text = path.read_text(encoding="utf-8")
        contract.consumed_vars.update(collect_consumed_vars(raw_text))
        contract.produced_vars.update(collect_produced_vars(raw_text))

        effective_work_chars = set(allowed_work_chars)
        effective_work_chars.update(collect_configured_work_chars(data))
        layout_chars = validate_layout(path, data, results)
        commands = validate_bindings(path, data, results)
        contract.command_bindings.extend(commands)
        scripts = []
        scripts.extend(validate_events(path, data, results))
        scripts.extend(validate_task(path, data, results))
        icon_scripts, icon_ids = validate_icons(path, data, results)
        scripts.extend(icon_scripts)

        events = data.get("events")
        if isinstance(events, dict):
            post_open_script = events.get("post_open")
            if isinstance(post_open_script, str):
                contract.post_open_vars.update(collect_produced_vars(post_open_script))

        for command in commands:
            owner = command_owner.get(command)
            if owner is None:
                command_owner[command] = path
            else:
                results.warn(f"{path}: command binding `{command}` already used by {owner}")

        for script in scripts:
            validate_menu_operations(path, script, results)
            for menu_id in MENU_OPEN_RE.findall(script):
                if menu_id not in menu_id_map:
                    results.error(
                        f"{bundle_root}: script references menu id `{menu_id}` but no matching menu file was found"
                    )
            for target_menu_id, passed_vars in collect_menu_open_calls(script):
                if target_menu_id in menu_contracts:
                    target_contract = menu_contracts[target_menu_id]
                    target_contract.incoming_edges.add(path.stem)
                    target_contract.incoming_vars.update(passed_vars)
            utils_in_script = UTILS_CALL_RE.findall(script)
            called_utils.update(utils_in_script)
            effective_work_chars.update(collect_script_work_chars(script))
            for util_name in utils_in_script:
                effective_work_chars.update(util_work_chars.get(util_name, set()))
                contract.produced_vars.update(util_produced_vars.get(util_name, set()))

        warn_on_unbound_layout_chars(path, layout_chars, icon_ids, effective_work_chars, results)

    warn_on_menu_contracts(menu_contracts, results)
    return called_utils, menu_contracts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate an InterMenu bundle.")
    parser.add_argument("bundle_root", help="Directory containing menus/ and optional functions/")
    parser.add_argument(
        "--allow-layout-char",
        action="append",
        default=[],
        help="Allow a non-space layout char to exist without an icon definition. Repeatable.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    bundle_root = Path(args.bundle_root).resolve()
    allowed_work_chars = {"@"}
    for raw in args.allow_layout_char:
        if raw:
            allowed_work_chars.add(raw[0])

    results = Results()
    if not bundle_root.exists():
        print(f"[ERROR] Bundle root does not exist: {bundle_root}")
        return 2

    menu_files = iter_menu_files(bundle_root)
    function_files = iter_function_files(bundle_root)

    if not menu_files:
        results.error(f"{bundle_root}: no menu files found under menus/")

    menu_id_map, duplicate_menu_ids = collect_menu_ids(menu_files)
    for menu_id in sorted(duplicate_menu_ids):
        results.error(f"{bundle_root}: duplicate menu id by filename stem `{menu_id}`")

    defined_utils: set[str] = set()
    util_work_chars: dict[str, set[str]] = {}
    util_produced_vars: dict[str, set[str]] = {}
    for function_file in function_files:
        try:
            function_names, function_chars, function_var_sets = validate_functions(function_file, results)
            defined_utils.update(function_names)
            for function_name, chars in function_chars.items():
                util_work_chars.setdefault(function_name, set()).update(chars)
            for function_name, produced_vars in function_var_sets.items():
                util_produced_vars.setdefault(function_name, set()).update(produced_vars)
        except ValueError as exc:
            results.error(f"{function_file}: {exc}")

    called_utils, _menu_contracts = validate_menus(
        bundle_root,
        menu_files,
        menu_id_map,
        allowed_work_chars,
        util_work_chars,
        util_produced_vars,
        results,
    )

    for util_name in sorted(called_utils):
        if util_name not in defined_utils:
            results.warn(f"{bundle_root}: `utils.{util_name}()` is referenced but no shared function defines it")

    if results.errors:
        for message in results.errors:
            print(f"[ERROR] {message}")
    for message in results.warnings:
        print(f"[WARN] {message}")

    if not results.errors:
        print(f"[OK] Bundle validation passed: {bundle_root}")
        if results.warnings:
            print(f"[OK] {len(results.warnings)} warning(s) reported")
        return 0

    print(
        f"[FAIL] Bundle validation found {len(results.errors)} error(s)"
        + (f" and {len(results.warnings)} warning(s)" if results.warnings else "")
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
