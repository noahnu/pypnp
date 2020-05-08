import os

from invoke import (
    exceptions,
    task,
)


@task
def clean(ctx):
    """
    Remove build files e.g. package, distributable, compiled etc.
    """
    ctx.run("rm -rf *.egg-info dist build __pycache__ .pytest_cache artifacts/*")


@task
def requirements(ctx, upgrade=False):
    """
    Build test & dev requirements lock file
    """
    args = ["--no-emit-find-links", "--no-index", "--allow-unsafe", "--rebuild"]
    if upgrade:
        args.append("--upgrade")
    ctx.run(
        f"echo '-e .[dev]' | python -m piptools compile "
        f"{' '.join(args)} - -qo- | sed '/^-e / d' > dev_requirements.txt",
        pty=True,
    )


@task
def lint(ctx, fix=False):
    """
    Check and fix syntax
    """
    lint_commands = {
        "isort": f"python -m isort {'' if fix else '--check-only --diff'} -y",
        "black": f"python -m black {'' if fix else '--check'} .",
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


@task(pre=[clean])
def build(ctx):
    """
    Generate version from scm and build package distributable
    """
    ctx.run("python setup.py sdist bdist_wheel")


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
    from semver import parse_version_info

    if not dry_run and not os.environ.get("CI"):
        print("This is a CI only command")
        exit(1)

    # get version created in build
    with open("version.txt", "r") as f:
        version = str(f.read())

    try:
        should_publish_to_pypi = not dry_run and parse_version_info(version)
    except ValueError:
        should_publish_to_pypi = False

    # publish to test to verify builds
    publish(ctx, dry_run=True)

    # publish to pypi if test succeeds
    if should_publish_to_pypi:
        publish(ctx, dry_run=False)
