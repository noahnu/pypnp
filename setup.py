from datetime import datetime
from pathlib import Path

from setuptools import setup


setup_requires = ["setuptools_scm"]
install_requires = []
dev_requires = [
    "invoke",
    "pip-tools",
    "semver",
    "twine",
    "wheel",
    "black",
    "isort",
    "py-githooks",
]


def readme() -> str:
    with Path("README.md").open("r") as f:
        return f.read()


if __name__ in ["__main__", "builtins"]:
    setup(
        name="pypnp",
        description="Alternative module resolution system for python",
        author="noahnu",
        author_email="noah@noahnu.com",
        license="MIT",
        url="https://github.com/noahnu/pypnp",
        entry_points={"console_scripts": ["pypnp-run=pypnp.run:main"],},
        long_description=readme(),
        long_description_content_type="text/markdown",
        use_scm_version={
            "local_scheme": lambda _: "",
            "version_scheme": lambda v: v.format_with("{tag}")
            if v.exact
            else datetime.now().strftime("%Y.%m.%d.%H%M%S%f"),
            "write_to": "version.txt",
        },
        zip_safe=False,
        python_requires=">=3.8",
        install_requires=install_requires,
        setup_requires=setup_requires,
        extras_require={"dev": dev_requires},
        classifiers=[
            "Programming Language :: Python :: 3",
            "Intended Audience :: Developers",
            "Operating System :: OS Independent",
        ],
    )
