# Changelog

## Unreleased

Initial import:
- `screen-ir/screen-ir.schema.json`, Screen IR `schemaVersion` 1.0, from `@slaclab/canopy-screen-ir` 0.1.2 (descriptions updated, structure unchanged).
- 32 widget definitions in `screen-ir/widgets/`: 31 carried over from the Beaver widget registry (IR fields only; the `pv-button` and `absolute-canvas` prop schemas from `pydm-converter-tool`'s bundled copy, which has the props the converter emits, so both are version 1.1.0), plus `unknown-widget`. Prop schemas declare the canonical draft-07 `$schema`, `http://json-schema.org/draft-07/schema#`.
- `screen-ir/widget-definition.schema.json` and `conformance/case.schema.json`.
- The `pv-channel` prop format, documented in the README.
- 22 validation conformance cases, with the semantic rule ids `macro-default-required`, `macro-default-forbidden` and `formula-ref-unresolved`.
- `tools/check.py` reference checker, run in CI.
- Formula references use the `formula://` prefix and the `formula-ref-unresolved` rule id, renamed from `fox://` and `fox-ref-unresolved` when Canopy renamed its Fox service to the Formula Engine. There are no aliases: `fox-ref-unresolved` is not a rule id, and `fox://<name>` is not a formula reference. Validators treat a `fox://` value as an ordinary string, like any other unrecognized scheme, so a screen that still uses one passes validation; rewrite it to `formula://`.
