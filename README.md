# Gitkit

Small git helper

## 💾 Installation

```
$ uv tool install git+https://github.com/bmike7/gitkit.git
```

## 💅 Motivation

As someone who enjoys rising my setup, one crucial element in my
day-to-day is `git`.

`gitkit` has two functionalities I rely on often:

```
usage: gitkit [-h] {clone-with-worktrees,mono-version-bump,add-worktree} ...

Small Git helper.

positional arguments:
  {clone-with-worktrees,mono-version-bump,add-worktree}
                        subcommand help
    clone-with-worktrees
                        Clones git repository with worktrees
    mono-version-bump   Bump a uv package's version
    add-worktree        Add worktree with reference to existing branch

options:
  -h, --help            show this help message and exit

```

- `clone-with-worktrees`
- `mono-version-bump`


### Clone with worktrees

If you haven't heard of `git worktree`s before, they are amazing. They
allow you to switch branches by navigating in your file-system instead
of checking out to another branch within the same repository.

However, it takes some steps to set one up. This command does that
lifting for you:

```
~/topsecret $ gitkit clone-with-worktrees git@github.com:bmike7/assistant_to_the_regional_manager.git

Cloning 'assistant_to_the_regional_manager' with worktrees:
Cloning into bare repository '.bare'...
remote: Enumerating objects: 33, done.
remote: Counting objects: 100% (33/33), done.
remote: Compressing objects: 100% (21/21), done.
remote: Total 33 (delta 14), reused 29 (delta 10), pack-reused 0 (from 0)
Receiving objects: 100% (33/33), 66.50 KiB | 740.00 KiB/s, done.
Resolving deltas: 100% (14/14), done.
From github.com:bmike7/assistant_to_the_regional_manager
 * [new branch]      main       -> origin/main
branch 'main' set up to track 'origin/main'.
Adding worktree 'main'
Preparing worktree (checking out 'main')
HEAD is now at 5d03feb docs: described motivation + installation and usage guide

~/topsecret $ tree assistant_to_the_regional_manager/

assistant_to_the_regional_manager/
└── main
    ├── pyproject.toml
    ├── README.md
    ├── src
    │   ├── cli.py
    │   ├── commands.py
    │   ├── config.py
    │   └── main.py
    └── uv.lock

3 directories, 7 files

```

Then you can start developing features as neighbors to `main`.


### Mono version bump

This one is more useful when you are working with `uv`'s
workspaces. With your monorepo you'll need a way to version your packages,
and you possibly want to deploy them separately. For example when
publishing to PyPI.

> 💡 Note
>
> In combination with CI/CD pipelines this gets really powerful. One way
> to fully take control over your pipelines is by using [Dagger](https://dagger.io)
> which allows creating and testing pipelines from your local machine.
>
> Then a deploy looks as follows:
> 1. `gitkit mono-version-bump {package} patch`
> 2. Your pipeline can do the rest

```
publish-package-from-tag:
  extends: [.dagger]
  stage: deploy
  script:
    - dagger call publish-from-tag --tag "$CI_COMMIT_TAG"
  rules:
    - if: "$CI_COMMIT_TAG"
```
