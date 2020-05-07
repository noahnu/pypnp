from setuptools import setup

if __name__ in ["__main__", "builtins"]:
    setup(
        name="pypnp",
        description="Alternative module resolution system for python",
        author="noahnu",
        license="MIT",
        entry_points={
            "console_scripts": [
                "pypnp-run=pypnp.run:main"
            ],
        },
        zip_safe=False,
        python_requires=">=3.8",
        classifiers=[
            "Programming Language :: Python :: 3"
        ]
    )
