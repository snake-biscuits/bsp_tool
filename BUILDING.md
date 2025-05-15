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

`~/.pypirc` can save API keys for the upload
```ini
[pypi]
username = __token__
password = pypi-SuperSecretAndVeryLongBase64PyPiAPIKey

[testpypi]
username = __token__
password = pypi-SuperSecretAndVeryLongBase64TestPyPiAPIKey
```

> API keys can be limited to a single repository
> you can add an entry into `~/.pypirc` for this, but it's more complex
> not gonna explain that here

### TestPyPI

> add rc1 to `version` in `pyproject.toml` first!
> helps us catch errors before the PyPI release

```bash
$ twine upload --repository testpypi dist/*
```

Then, in another folder / virtual environment

```bash
$ python3 -m pip install --index-url https://test.pypi.org/simple/ bsp_tool
```

> might have to wait a second for the latest version to upload


### PyPI

```bash
$ twine upload dist/*
```


[^pf]: Python Packaging User Guide: [Package Formats](https://packaging.python.org/en/latest/discussions/package-formats/)
[^du]: Python `distutils` docs: [Specifying the files to distribute](https://docs.python.org/3.10/distutils/sourcedist.html#specifying-the-files-to-distribute)
