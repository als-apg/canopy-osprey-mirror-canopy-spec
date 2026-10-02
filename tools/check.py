"""Check the spec against itself.

1. Every schema in the repo is a valid JSON Schema for its draft.
2. Every widget definition satisfies screen-ir/widget-definition.schema.json,
   its filename equals its id, and its propSchema is a valid draft-07 schema.
3. Every conformance case is well formed and produces its expected outcome
   under the reference validator below.

The reference validator exists to keep the fixtures honest. It is not an SDK:
language SDKs implement validation themselves and run the same fixtures.

Run: uv run tools/check.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator, Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
SCREEN_IR = ROOT / "screen-ir"
IR_SCHEMA = SCREEN_IR / "screen-ir.schema.json"
WIDGET_DEFINITION_SCHEMA = SCREEN_IR / "widget-definition.schema.json"
WIDGETS = SCREEN_IR / "widgets"
CASE_SCHEMA = ROOT / "conformance" / "case.schema.json"
VALIDATE_CASES = ROOT / "conformance" / "screen-ir" / "validate"

FOX_PREFIX = "fox://"


def load(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def pointer(parts: Any) -> str:
    """RFC 6901 JSON Pointer for a path of keys and indexes."""
    return "".join("/" + str(p).replace("~", "~0").replace("/", "~1") for p in parts)


# ── Reference validator ──────────────────────────────────────────────────────


def validate_screen(doc: Any, validator: Draft202012Validator) -> list[dict[str, str]]:
    """Errors as {rule, instancePath}. Semantic rules run only on schema-valid documents."""
    errors = [
        {"rule": "schema", "instancePath": pointer(e.absolute_path)}
        for e in validator.iter_errors(doc)
    ]
    if errors:
        return errors

    kind = doc["kind"]
    for i, macro in enumerate(doc["macros"]):
        has_default = macro.get("default") is not None
        if kind == "screen" and not has_default:
            errors.append({"rule": "macro-default-required", "instancePath": f"/macros/{i}"})
        if kind == "template" and has_default:
            errors.append({"rule": "macro-default-forbidden", "instancePath": f"/macros/{i}"})

    formulas = {f["name"] for f in doc.get("formulas", [])}

    def fox_name(ref: str) -> str:
        return ref[len(FOX_PREFIX):] if ref.startswith(FOX_PREFIX) else ref

    def unresolved(path: str) -> None:
        errors.append({"rule": "fox-ref-unresolved", "instancePath": path})

    def walk(node: dict[str, Any], path: str) -> None:
        for key, value in node["props"].items():
            if isinstance(value, str) and value.startswith(FOX_PREFIX):
                if fox_name(value) not in formulas:
                    unresolved(f"{path}/props{pointer([key])}")
        for j, rule in enumerate(node.get("rules", [])):
            if "formula" in rule and fox_name(rule["formula"]) not in formulas:
                unresolved(f"{path}/rules/{j}/formula")
            for k, pv in enumerate(rule.get("pvs", [])):
                name = pv["name"]
                if name.startswith(FOX_PREFIX) and fox_name(name) not in formulas:
                    unresolved(f"{path}/rules/{j}/pvs/{k}/name")
        for c, child in enumerate(node.get("children", [])):
            walk(child, f"{path}/children/{c}")

    walk(doc["root"], "/root")
    return errors


# ── Checks ───────────────────────────────────────────────────────────────────


def check_schemas(problems: list[str]) -> None:
    for path in (IR_SCHEMA, WIDGET_DEFINITION_SCHEMA, CASE_SCHEMA):
        try:
            Draft202012Validator.check_schema(load(path))
        except Exception as e:  # noqa: BLE001 - report any schema error
            problems.append(f"{path.relative_to(ROOT)}: not a valid 2020-12 schema: {e}")


def check_widgets(problems: list[str]) -> int:
    meta = Draft202012Validator(load(WIDGET_DEFINITION_SCHEMA))
    files = sorted(WIDGETS.glob("*.json"))
    for path in files:
        rel = path.relative_to(ROOT)
        doc = load(path)
        for e in meta.iter_errors(doc):
            problems.append(f"{rel}{pointer(e.absolute_path)}: {e.message}")
        if isinstance(doc, dict):
            if doc.get("id") != path.stem:
                problems.append(f"{rel}: id {doc.get('id')!r} does not match the filename")
            try:
                Draft7Validator.check_schema(doc.get("propSchema", {}))
            except Exception as e:  # noqa: BLE001
                problems.append(f"{rel}/propSchema: not a valid draft-07 schema: {e}")
    return len(files)


def check_cases(problems: list[str]) -> int:
    case_meta = Draft202012Validator(load(CASE_SCHEMA))
    ir = Draft202012Validator(load(IR_SCHEMA))
    files = sorted(VALIDATE_CASES.glob("*.json"))
    for path in files:
        rel = path.relative_to(ROOT)
        case = load(path)
        shape = [f"{pointer(e.absolute_path)}: {e.message}" for e in case_meta.iter_errors(case)]
        if shape:
            problems.extend(f"{rel}{p}" for p in shape)
            continue

        actual = validate_screen(case["screen"], ir)
        if (not actual) != case["valid"]:
            problems.append(f"{rel}: expected valid={case['valid']}, got errors {actual}")
            continue
        for expected in case.get("errors", []):
            if expected not in actual:
                problems.append(f"{rel}: expected error {expected} not among {actual}")
    return len(files)


def main() -> int:
    problems: list[str] = []
    check_schemas(problems)
    widgets = check_widgets(problems)
    cases = check_cases(problems)
    for p in problems:
        print(f"FAIL {p}")
    print(f"{widgets} widget definitions, {cases} conformance cases, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
