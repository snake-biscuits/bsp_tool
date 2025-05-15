# Building `bsp_tool`

## Clean

```bash
$ rm -r *.egg-info/
$ rm -r build/
$ rm -r dist/
```

> NOTE: `build/` dir is normally deleted automatically
> -- but it can stick around if a build is interrupted


## Build

```bash
$ python -m pip install --upgrade pip
$ python -m pip install --upgrade build
$ python -m build
```

`build` will install `build-backend` automatically
running `build` with no arguments will generate both sdist & wheel


## Check

### Source Distribution

```sh
$ tar -tf dist/*.tar.gz
```

Should contain:[^pf][^du]
 * `bsp_tool/`
 * `tests/`
 * `pyproject.toml`
 * `README.md`
 * `CHANGELOG.md`

> `pyproject.toml` lists `pytest` & `pytest-cov` as optional dependencies
> `pytest` can also be configured in `pyproject.toml` under `tool.pytest.ini_options`

### Wheel

```sh
$ unzip -l dist/*.whl
```

`tests/` & `docs/` should be absent


## Upload

```bash
$ python -m pip install --upgrade twine
```

> TODO: using `twine` to upload to TestPyPI
> TODO: using `twine` to upload to PyPI



[^pf]: Python Packaging User Guide: [Package Formats](https://packaging.python.org/en/latest/discussions/package-formats/)
[^du]: Python `distutils` docs: [Specifying the files to distribute](https://docs.python.org/3.10/distutils/sourcedist.html#specifying-the-files-to-distribute)
