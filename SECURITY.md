# Security policy

## Reporting a vulnerability

Please report suspected vulnerabilities privately. Don't open a public issue,
pull request or discussion for them.

Use GitHub's private vulnerability reporting: open the repository's
[Security tab](https://github.com/slaclab/canopy-spec/security) and choose
**Report a vulnerability**. Only the maintainers can see the report.

A useful report says:

- which release tag or commit you used;
- which schema, widget definition or conformance case is involved;
- the steps to reproduce it and what you expected to happen;
- the impact as you understand it.

The maintainers will acknowledge the report, work with you on a fix and agree a
disclosure date with you. Tell us if you want to be credited.

## Supported versions

canopy-spec is pre-1.0 and under active development. Security fixes are made on
`main` and published in a new release tag; they are not backported to older
tags. Use the latest tag.

## Scope

This repository holds schemas, widget definitions and conformance cases. It runs
no service. Report a vulnerability in an implementation of the spec to that
project. Tell us too if the spec makes the impact worse.
