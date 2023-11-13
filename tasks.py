import os
from datetime import datetime

from invoke import exceptions, task


@task
def clean(ctx):
    """
    Remove build files e.g. package, distributable, compiled etc.
    """
    ctx.run("rm -rf *.egg-info dist build __pycache__ .pytest_cache artifacts/*")


@task
def install(ctx, upgrade=False):
    """
    Build test & dev requirements lock file
    """
    if upgrade:
        ctx.run("poetry update")
    else:
        ctx.run("poetry lock", pty=True)
        ctx.run("poetry install", pty=True)


@task
def lint(ctx, fix=False):
    """
    Check and fix syntax
    """
    if not os.environ.get("CI"):
        fix = True

    lint_commands = {
        "isort": f"python -m isort {'' if fix else '--check-only --diff'} .",
        "black": f"python -m black {'' if fix else '--check'} .",
        "flake8": "python -m flake8 pypnp",
    }
    last_error = None
    for section, command in lint_commands.items():
        print(f"\033[1m[{section}]\033[0m")
        try:
            ctx.run(command, pty=True)
        except exceptions.Failure as ex:
            last_error = ex
        print()
    if last_error:
        raise last_error


def version_scheme(v):
    if v.exact:
        return v.format_with("{tag}")
    return datetime.now().strftime("%Y.%m.%d.%H%M%S%f")


@task(pre=[clean])
def build(ctx):
    """
    Generate version from scm and build package distributable
    """
    from setuptools_scm import get_version

    version = get_version(version_scheme=version_scheme, local_scheme=lambda _: "")
    ctx.run(f"poetry version {version}")
    ctx.run("poetry build")


@task
def publish(ctx, dry_run=True):
    """
    Upload built package to pypi
    """
    repo_url = "--repository-url https://test.pypi.org/legacy/" if dry_run else ""
    ctx.run(f"twine upload --skip-existing {repo_url} dist/*")


@task(pre=[build])
def release(ctx, dry_run=True):
    """
    Build and publish package to pypi index based on scm version
    """
    from semver.version import Version

    if not dry_run and not os.environ.get("CI"):
        print("This is a CI only command")
        exit(1)

    if dry_run and not version:
        version = ctx.run("poetry version --short").stdout.strip()

    if not version:
        print("Missing version.")
        exit(1)

    try:
        Version.parse(version)
        should_publish_to_pypi = not dry_run
    except ValueError:
        should_publish_to_pypi = False

    # publish to test to verify builds
    if dry_run:
        publish(ctx, dry_run=True)

    # publish to pypi if test succeeds
    if should_publish_to_pypi:
        publish(ctx, dry_run=False)
