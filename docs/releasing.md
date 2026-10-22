# Releasing

The package version is derived from Git tags through setuptools-scm. Automated
PyPI publishing is disabled in this repository. Pushing a version tag records
the source version only and does not publish a package.

## Local release check

Run the checks in CONTRIBUTING.md, then build and inspect both distributions
locally:

~~~bash
uv run --extra dev python -m build
uv run --extra dev twine check dist/*
~~~

## Source version tag

~~~bash
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin main
git push origin vX.Y.Z
~~~
