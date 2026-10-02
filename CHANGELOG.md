# Changelog

## Unreleased

Initial import:
- `screen-ir/screen-ir.schema.json`, Screen IR `schemaVersion` 1.0, from `@slaclab/canopy-screen-ir` 0.1.2.
- 32 widget definitions in `screen-ir/widgets/`: 31 carried over from the Beaver widget registry (IR fields only; the `pv-button` and `absolute-canvas` prop schemas from `pydm-converter-tool`'s bundled copy, which has the props the converter emits), plus `unknown-widget`.
- `screen-ir/widget-definition.schema.json` and `conformance/case.schema.json`.
- 17 validation conformance cases, with the semantic rule ids `macro-default-required`, `macro-default-forbidden` and `fox-ref-unresolved`.
- `tools/check.py` reference checker, run in CI.
