# Example of pypnp

Tested with python 3.8.2, create and activate venv:

```shell
python -m venv .venv
. .venv/bin/activate
```

Now install pypnp:

```shell
python -m pip install -e ../
```

Use pypnp to run the example application:

```shell
PYTHONPATH=. pypnp-run example
```

Since both `a.py` and `b.py` import `c_1.py`, using the typical python module resolution system, you should see:

```
P1: c_1.py
P2: c_1.py
```

Now, let's change the module mapping. Add these 2 lines to the module.pnp file:

```
a.py:c_1:c_2.py
b.py:c_1:c_1.py
```

Re-run the pypnp-run command:

```shell
PYTHONPATH=. pypnp-run example
```

You should now see:

```
P1: c_2.py
P2: c_1.py
```
