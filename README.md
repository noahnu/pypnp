# pypnp

## Usage

In the project you want to use pypnp in, first install `pypnp`.

```shell
python -m pip install pypnp
```

A lock file will be generated the first time you run your application, if one does not exist. To run your python application:

```shell
PYTHONPATH=. pypnp-run my.python.module.path
```

### Example

See the README example directory.

## Contributing

This project is still in extremely early stages and not ready for external contributors just yet. Once the idea is flushed out a bit more, I'll open it up.

To setup a virtual environment and install development dependencies:

```shell
. script/bootstrap
```
