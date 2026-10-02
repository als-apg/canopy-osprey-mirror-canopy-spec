# canopy-spec

Language-neutral contracts for Canopy. These are the files every Canopy SDK and tool builds on, in any language. This repo holds data and tests only. Each language SDK implements the contracts itself and proves it does so by passing the conformance cases here.

## Layout

```
screen-ir/
  screen-ir.schema.json            the Screen IR document format (*.screen.json), JSON Schema 2020-12
  widget-definition.schema.json    the format of the files in widgets/
  widgets/<type>.json              one file per IR widget type: its id and the props it accepts
conformance/
  case.schema.json                 the format of a conformance case
  screen-ir/validate/*.json        validation cases every implementation must pass
tools/check.py                     checks the spec against itself (run in CI)
```

**Not in this repo:** SDK code, editor metadata (palette icons, inspector layout, display names), converter mappings (`qtMapping`, `qtPropMap`), and widget component names. Those belong to the tools that use them: editor metadata and component names to `@slaclab/canopy-screen-widgets`, converter mappings to `pydm-converter-tool`.

## The Screen IR

The Screen IR (*intermediate representation*) is the `*.screen.json` format. The converter turns PyDM and EDM screens into it, the screen builder edits it, and the runtime renders it.

### Document schema

`screen-ir/screen-ir.schema.json` defines the document. The format version is `schemaVersion: "1.0"`.

The schema is read-tolerant by design:
- `props` is an open bag, so unknown keys are allowed.
- `metadata.source.type` accepts any string.
- A widget `type` can be any string.

### Semantic rules

JSON Schema can't express these rules, so they're defined here. An implementation evaluates them only on documents that already pass the schema. Each rule id is part of the spec: implementations report it, and it won't be renamed.

| Rule id | Fails when | Reported at (`instancePath`) |
|---|---|---|
| `macro-default-required` | `kind` is `screen` and a macro has no `default` | `/macros/{i}` |
| `macro-default-forbidden` | `kind` is `template` and a macro declares a `default` | `/macros/{i}` |
| `fox-ref-unresolved` | A `fox://<name>` reference has no `formulas[]` entry named `<name>`. Checked in: top-level string prop values, a rule's `formula`, and a rule's `pvs[].name` | The prop, `.../rules/{j}/formula`, or `.../rules/{j}/pvs/{k}/name` |

A rule's `formula` may be written with or without the `fox://` prefix. Nested prop values, such as channels inside `waveform-plot` curves, aren't checked in v0.1.

### Widget definitions

Each file in `screen-ir/widgets/` defines one IR widget type:
- **`id`** is the IR `type` value and must equal the filename.
- **`version`** is a semver string. Bump the major version on an incompatible `propSchema` change.
- **`description`** says what the widget is.
- **`supportsPv`**, **`supportsRules`** and **`supportsChildren`** say whether the widget binds PVs, whether rules can target it, and whether its node can have `children`.
- **`propSchema`** is a JSON Schema (draft-07) describing the node's `props`.

**The list of IR widget types is the set of files in this directory.** No separate list is kept, so there's nothing to fall out of sync. `absolute-canvas` is the document root, and `unknown-widget` is the converter's placeholder for source classes it has no definition for. Both are real types and have files here.

**In v0.1 the prop schemas describe props but aren't enforced.** They're carried over from the Beaver registry, and some of their constraints would reject real screens:
- `"type": "number"` rejects macro values like `"$(PREC)"`;
- several `required` lists don't match what the builder writes.

Conformance doesn't test props against them yet; see [Known gaps](#known-gaps-v01).

## Conformance

Each case in `conformance/` is self-contained (format: `conformance/case.schema.json`):

```json
{
  "description": "On a screen every macro needs a default.",
  "valid": false,
  "errors": [{ "rule": "macro-default-required", "instancePath": "/macros/0" }],
  "screen": { "...": "the document under test" }
}
```

An implementation runs its validator on `screen` and compares:
- **Level 1:** whether the screen counts as valid matches `valid`.
- **Level 2:** level 1, and every expected error appears among the reported errors with the same `rule` and `instancePath`. Extra reported errors are allowed.

Each invalid case breaks exactly one rule. Schema-error locations were chosen to be the same in ajv and Python `jsonschema`.

### Current implementations

| Implementation | Result | Notes |
|---|---|---|
| `tools/check.py` (reference) | Level 2, 17/17 | |
| `@slaclab/canopy-screen-ir` `validate()` | Level 1, 17/17 | Schema error paths match. Semantic errors are returned as plain strings without a rule id or path |
| `pydm-converter-tool` `validate_screen_json` | 12/17 | Schema only: it accepts the five semantically invalid cases, so the converter can emit screens that `validate()` rejects |

## Using the spec from an SDK

1. Copy the files you need into the SDK, pinned to a release tag of this repo, and record the tag.
2. In the SDK's CI, check that the copied files are byte-identical to that tag, and run the conformance cases.
3. When this repo releases, open a PR in each SDK that bumps the pin. The SDK's CI shows whether it still conforms.

Don't edit copied files in an SDK. Change the spec here first.

## Versions

- **Release tags** (`vMAJOR.MINOR.PATCH`) version the whole repo. A major bump means some consumer must change.
- **`schemaVersion`** in a document changes only when the document format changes. It isn't tied to the release number.
- **A widget definition's `version`** tracks that type's `propSchema`.

## Changing the spec

1. Open a PR here. Update the schema or definitions, add conformance cases for the change, and run `uv run tools/check.py`.
2. Note the change in `CHANGELOG.md` and tag a release.
3. Bump the pin in each consumer.

## Known gaps (v0.1)

- **`pv-toggle` has no definition.** Both the screen builder and the runtime accept it.
- **Don't validate props against the prop schemas yet, in CI or anywhere else.** In particular, don't enforce their `required` lists. Some don't match real screens: `text-label` requires `text`, but the builder also imports text labels that only have `label`. Enforcing them first needs:
  - a rule that number props also accept macro strings;
  - `required` lists reconciled against what the converter and the builder actually write;
  - consistent key naming. `pv-slider` uses `min`/`max` while `pv-spinbox` uses `minValue`/`maxValue`.
- **Mixed drafts.** The prop schemas are draft-07 and the document schema is 2020-12.
- **No conformance cases for macro expansion or rule evaluation yet.** Today only the runtime implements them.

## Where the initial content came from

- `screen-ir/screen-ir.schema.json`: copied byte-for-byte from `slaclab/canopy-sdk-js` `packages/screen-ir/schema/` at `74fc229` (package version 0.1.2).
- `screen-ir/widgets/*.json`: the IR fields (`id`, `version`, `description`, `propSchema`, `supportsPv`, `supportsRules`, `supportsChildren`) taken from `slaclab/canopy` `widget-registry-data/widgets/*.json` at `bfd8104`. The values are unchanged (checked field by field), except two prop schemas: `pv-button` and `absolute-canvas` come from `pydm-converter-tool`'s bundled registry at `019ee4e`, which adds the props the converter has emitted since 1.0.6 (nine on `pv-button`, `backgroundColor` on `absolute-canvas`). The files are not byte-identical: the other fields were dropped and the JSON was reformatted. `unknown-widget.json` is new; it describes what `pydm-converter-tool` emits.
- `conformance/screen-ir/validate/*.json`: new. They cover the cases in `canopy-sdk-js`'s `validate.test.ts` and the semantic rules in its `validate.ts`.

Background: slaclab/canopy-sdk-js#4 and slaclab/canopy-screen-runtime#6.
