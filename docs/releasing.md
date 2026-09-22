# Releasing

The package uses setuptools-scm, so the tag is the release version. The initial
release was v0.1.0; the current follow-up release is v0.2.1.

## Local release check

Run the checks in CONTRIBUTING.md, then build and inspect both distributions:

~~~bash
uv run --extra dev python -m build
uv run --extra dev twine check dist/*
~~~

## GitHub and PyPI setup

The publisher is .github/workflows/publish.yml. It runs only for tags matching
v*.*.* and uses PyPI Trusted Publishing through the release environment.

Before the first tag, configure this PyPI Trusted Publisher:

- PyPI owner/account: averyfreeman
- GitHub repository: daisyui-mcp-for-uv-pip
- Workflow filename: .github/workflows/publish.yml
- GitHub environment: release
- Project name: daisyui-mcp

No long-lived PyPI token is required by the workflow. The PyPI project must
exist or be created by the first trusted publisher configuration, and the
release environment must be available in repository settings.

## Tagged release

~~~bash
git tag -a v0.2.1 -m "Release v0.2.1"
git push origin main
git push origin v0.2.1
~~~

The workflow checks out the tag, builds from that tag, validates metadata, and
publishes the tagged wheel and source archive.
