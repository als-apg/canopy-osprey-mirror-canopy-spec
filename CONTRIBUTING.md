# Contributing

## Local Setup

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
git clone https://github.com/slaclab/canopy-spec
cd canopy-spec
```

## Running the Check

```bash
uv run --locked tools/check.py
```

This checks the schemas, the widget definitions and the conformance cases. CI
runs the same command on every pull request.

## Submitting Changes

1. Create a branch off `main` using the format `<username>/<description>` or `<username>/#<issue-number>-<description>`
2. Make your changes as described in [Changing the spec](README.md#changing-the-spec) and ensure the check passes
3. Open a pull request

### From a fork

If you don't have write access to this repository, fork it and clone your fork.
Branch off `main` in your fork; the branch name format above is only a
convention for people who push here, so any descriptive name works. Open the
pull request against `slaclab/canopy-spec:main`.

- For anything larger than a small fix, open an issue first so we can agree on
  the approach before you spend time on it.
- A maintainer has to approve the GitHub Actions run on a pull request from a
  fork before it starts.
- Pull requests need an approving review before they can be merged.

## Reporting Security Issues

Don't report vulnerabilities in public issues or pull requests. See
[SECURITY.md](SECURITY.md).

## License

canopy-spec is distributed under the terms in [LICENSE.md](LICENSE.md). By
contributing, you accept that the last paragraph of that file, which licenses
enhancements that you make available, applies to your contribution.
