import argparse as ap
import subprocess
from enum import Enum
from functools import partial
from pathlib import Path

INITIAL_BRANCHES = ["main", "master"]


class Bump(Enum):
    PATCH = "patch"
    MINOR = "minor"
    MAJOR = "major"


def get_arg_parsser() -> ap.ArgumentParser:
    p = ap.ArgumentParser(
        prog="gitkit",
        description="Small Git helper.",
    )
    subs = p.add_subparsers(help="subcommand help")

    cww = subs.add_parser(
        "clone-with-worktrees",
        help="Clones git repository with worktrees",
    )
    cww.add_argument(
        "url",
        help=(
            "Repository url to clone from.\n\n"
            "Based on: `https://nicknisi.com/posts/git-worktrees/`"
        ),
    )
    cww.set_defaults(func=clone_with_worktrees)

    mvb = subs.add_parser("mono-version-bump", help="Bump a uv package's version")
    mvb.add_argument("project", help="The project to bump the version of")
    mvb.add_argument("bump", type=Bump)
    mvb.set_defaults(func=mono_version_bump)

    aw = subs.add_parser(
        "add-worktree", help="Add worktree with reference to existing branch"
    )
    aw.add_argument("branch")
    aw.set_defaults(func=add_worktree)
    return p


def exec(cmd: str, *args, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run([cmd, *args], **kwargs)


precommit = partial(exec, "pre-commit", check=True)
uv = partial(exec, "uv", check=True)
git = partial(exec, "git", check=True)


def add_worktree(args: ap.Namespace) -> None:
    git = partial(exec, "git")
    if cwd := args.cwd:
        git = partial(git, cwd=cwd)
    print(f"Adding worktree '{(branch := args.branch)}'")
    git("worktree", "add", branch)


def clone_with_worktrees(args: ap.Namespace) -> None:
    repo = Path((remote := args.url).split("/")[-1].split(".")[0])
    repo.mkdir()

    print(f"Cloning '{str(repo)}' with worktrees:")
    git = partial(exec, "git", cwd=repo)
    git("clone", "--bare", remote, ".bare")
    (repo / ".git").write_text("gitdir: ./.bare\n")
    git("config", "remote.origin.fetch", "+refs/heads/*:refs/remotes/origin/*")
    git("fetch")
    branches = git(
        "for-each-ref",
        "--format='%(refname:short)'",
        "refs/heads",
        capture_output=True,
        text=True,
    ).stdout.split()
    for branch in branches:
        branch = branch.strip("'")
        git("branch", f"--set-upstream-to=origin/{branch}", branch)
        if branch in INITIAL_BRANCHES:
            add_worktree(ap.Namespace(cwd=repo, branch=branch))


def get_version(project: str) -> str:
    output = uv("version", "--package", project, text=True, capture_output=True).stdout
    return output.strip().removeprefix(project).strip()


def mono_version_bump(args: ap.Namespace) -> None:
    proj = args.project
    precommit("run", "--all-files")
    old_ = get_version(proj)
    uv("version", "--package", proj, "--bump", args.bump.value)
    git("add", ".")
    new_ = get_version(proj)
    assert old_ != new_
    msg = f"chore({proj}): bumping version '{old_}' -> '{new_}'"
    git("commit", "-m", msg)
    git("tag", "-a", f"{proj}/v{new_}", "-m", msg)


def main() -> None:
    args = get_arg_parsser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
