# pypnp

![PyPI - License](https://img.shields.io/pypi/l/pypnp) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pypnp) ![PyPI - Downloads](https://img.shields.io/pypi/dm/pypnp) ![PyPI](https://img.shields.io/pypi/v/pypnp)

An opinionated dependency management and resolution system in Python.

## Motivation

`pypnp` is intended to fill the gaps in Python's dependency management system, by rewriting the way Python resolves module imports. It enables multiple versions of a single dependency to be installed by hooking into, and in some cases rewriting Python's module import system.

pypnp should:
- Be intuitive to use and reason about resolution
- Integrate seamlessly into existing python applications
- Support deterministic installations via version locking
- Enable rapid local development

## Context

Dependency management in python is broken.

Fundamentally, a good dependency management solution should provide support for a community of library authors, by making distribution of code safe and easy. For production applications, the dependency manager should also support the ability to _lock_ code such that builds are entirely deterministic.

Python's most popular dependency management solution is `pip`. It allows libraries to be downloaded from private and public registries, supports integrity checks, and a rudimentary versioning system. Although it's possible to print a list of "locked" dependencies to a file and use that as an installation reference, there are a number of tools available to simplify the guarantee of deterministic builds, such as `pip-tools` and `poetry`.

In a typical python application, several direct dependencies will be required. A _direct dependency_ is one which is directly invoked by the application. For example, if your application needs to print formatted lines to stdout, it may `import colored`, a library with offers a suite of formatting tools. To ensure the `colored` module is always available when your application or library is used, you would add it to a `requirements.txt` file or to `install_requires` in a `setup.py`. The consumer of this application would then `pip install -r requirements.txt` or `pip install .` to install the listed direct dependencies. These modules are stored in a common site-packages directory and made available to the module resolution system.

A direct dependency may have its own direct dependency that it invokes. If `colored` requires `attrs` then `attrs` is a direct dependency of `colored` and a _transitive dependency_ of the main application. The relationship of all the dependencies for a given application, forms a _dependency tree_. E.g.:

```
my-application
└── colored
    ├── attrs
    └── xyz
└── requests
    ├── urllib3
        ├── abc
        └── xyz
    └── leftpad
```

Since features may only be available in a specific version range for a given dependency, or may even be removed in some breaking version, we usually specify acceptable version ranges for each dependency in the tree:

```
my-application
└── colored >=3,<4
    ├── attrs ~=19.0
    └── xyz >=4,<6
└── requests
    ├── urllib3 >=10,<11
        ├── abc >2
        └── xyz >=5,<5.2
    └── leftpad ~= 3.5
```

To generate a frozen list of dependencies, we could use a tool such as `pip-tools` which will attempt to find dependency versions which satisfy all version constraints. If you consider the `xyz` dependency, it will settle on `5.1` due to the `urllib3` constraint, even if `5.3` is available with security patches or bug fixes, depsite the `xyz` transitive dependency of `colored` not having the same constraint.

Python's module resolution only allows one version per dependency in the entire tree. This is a fundemental implementation detail of the programming language. This is why `pip-tools` will freeze `xyz` on an "older" version of the library for `colored`, even though `colored` would be okay using a newer version. This means in Python, the larger your dependency tree, and thus the more version constraints enforced, the fewer versions the dependency resolver is able to choose from. It is common to end up in a situation where one transitive dependency blocks the update of a completely unrelated direct dependency, simply because they both share a transitive dependency.

In the Node.js ecosystem, this is solved in a rather simple fashion. Multiple versions of the same library can be installed.

The downside with this approach, is that installed dependencies can become quite bloated, using an obscene amount of disk space. This is not usually a concern with modern computers, although it can definitely lead to challenges de-duplicating dependencies to reduce bundle sizes in code expected to be downloaded over the internet for web-based applications. Since Python is not used for frontend website development, a few extra kilobytes is not usually a concern.

One argument against Node's resolution system, is that it can be hard to reason about which dependency is being used, if there are multiple versions installed. This requires a different way of looking at dependencies. In the above tree, the author of `my-application` _should not be concerned with its transitive dependencies_. If we trust our direct dependencies, that trust should naturally extend to the transitive dependencies. `colored` is maintained by trusted maintainers, such that they will properly vet any dependencies they include in their library. With this in mind, as long as we keep `colored` up to date, we know it will keep its dependencies up to date, so that we always receive the latest bug fixes and security patches. If `requests`, albeit trusted, has a slow release cycle, we know that even if `xyz` is pinned to an unsecure version, the surface area that the unsecure version can affect is isolated to `requests` and call sites of `requests`.

There is one use case where we want to ensure even a transitive dependency is only on one version throughout our tree, and this is in the case where the dependency exposes some singleton where it's fundemental we only have one state. In this case, we require a concept from Node.js (npm) which is not properly supported on the Python ecosystem, and this is the concept of a _peer dependency_. A peer dependency is one in which the expectation is that the consumer will supply the dependency. In the tree, it becomes a sibling node, rather than a child. This pattern allows us to explicitly take it out of the tree, and ensure there is only ever one version installed. Labelling a library as a peer dependency, also makes its intention very clear. The author is telling us that the library only expects one version installed, because of some technical limitation or design detail. You do not need to infer intent on a case by case basis.

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
