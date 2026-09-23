# GitHub Actions Lab - CI and Continuous Delivery

**Estimated time:** 20-25 minutes  
**Starting point:** completed quality-toolchain repository  
**Demo branch:** feat/githubaction  
**Tools:** GitHub, GitHub Actions, uv, Ruff, mypy, pytest

---

# Goal

GitHub will run the project's quality checks whenever you push to the
demonstration branch feat/githubaction. If they pass, GitHub will build the
Python package and store it as a downloadable artifact.

> [!IMPORTANT]
> This quick demo does not protect main. A workflow triggered by a push runs
> after the push has happened. Protecting main requires CI on Pull Requests and
> a repository rule that makes the CI check required.

# 1. Events control when workflows run

GitHub Actions can react to different repository events:

~~~yaml
# Push to a selected branch
on:
  push:
    branches: [feat/githubaction]
~~~

~~~yaml
# Pull Request whose destination is main
on:
  pull_request:
    branches: [main]
~~~

~~~yaml
# Manual button in the Actions tab
on:
  workflow_dispatch:
~~~

For workflow_dispatch, GitHub requires the workflow file to exist on the
default branch. Therefore it is an event you should know about, but it is not
used by this isolated demo because the workflow stays off main.

Other events include tags, releases, and schedules. A workflow may listen to
several events.

Events answer: **When should automation start?**

They do not answer: **May this change be merged into main?**

The second decision belongs to repository rules and required status checks.

For this demo the sequence is:

~~~text
local commit
  -> push to feat/githubaction
  -> quality checks
  -> build package
  -> store artifact
~~~

This works even without branch-protection controls.

# 2. Prepare the repository

The repository should already contain pyproject.toml, uv.lock, src/, and tests/.

Confirm the remote and branches:

~~~bash
git remote -v
git branch -a
~~~

## 2.1 Enable GitHub Actions

In GitHub, open:

~~~text
Repository -> Settings -> Actions -> General
~~~

Under **Actions permissions**, select an option that permits the actions used
in the lab. The simplest classroom setting is:

~~~text
Allow all actions and reusable workflows
~~~

Under **Workflow permissions**, read access is sufficient:

~~~text
Read repository contents permission
~~~

Save the settings if you changed them.

> [!NOTE]
> There is no separate activation switch for feat/githubaction. GitHub discovers
> YAML files committed under .github/workflows/ and runs them when an event
> matches their configuration.

# 3. Verify the project locally

Recreate the locked environment and run the same checks GitHub will run:

~~~bash
uv sync --locked
uv run ruff format --check .
uv run ruff check .
uv run mypy src
uv run pytest
~~~

All checks must pass. If they fail, complete the previous quality-toolchain
exercise first. The GitHub runner will reproduce the same failures.

# 4. Create the demo branch without changing main

Fetch the latest remote state, then create the demo branch directly from
origin/main. You do not need to check out local main:

~~~bash
git fetch origin
git switch -c feat/githubaction origin/main
~~~

This creates and checks out feat/githubaction while leaving main unchanged.

If the branch already exists locally:

~~~bash
git switch feat/githubaction
~~~

If it already exists both locally and on GitHub, update it with:

~~~bash
git pull --ff-only
~~~

The branch name must exactly match the workflow configuration.

Confirm that you are not on main before creating files or commits:

~~~bash
git branch --show-current
git status
~~~

The first command must print feat/githubaction.

# 5. Create the workflow

Create .github/workflows/ci-cd.yml with this content:

~~~yaml
name: CI and Delivery Demo

on:
  push:
    branches:
      - feat/githubaction

permissions:
  contents: read

jobs:
  ci:
    name: Quality checks
    runs-on: ubuntu-latest

    steps:
      - name: Download repository
        uses: actions/checkout@v7

      - name: Install uv
        uses: astral-sh/setup-uv@v9.0.0
        with:
          enable-cache: true

      - name: Install Python
        run: uv python install 3.12

      - name: Reproduce project environment
        run: uv sync --locked

      - name: Check formatting
        run: uv run ruff format --check .

      - name: Run Ruff
        run: uv run ruff check .

      - name: Run mypy
        run: uv run mypy src

      - name: Run tests
        run: uv run pytest

  delivery:
    name: Build delivery artifact
    runs-on: ubuntu-latest
    needs: ci

    steps:
      - name: Download repository
        uses: actions/checkout@v7

      - name: Install uv
        uses: astral-sh/setup-uv@v9.0.0

      - name: Install Python
        run: uv python install 3.12

      - name: Build package
        run: uv build

      - name: Upload package
        uses: actions/upload-artifact@v4
        with:
          name: audience-metrics-package
          path: dist/
~~~

The workflow is now composed of:

~~~text
push to feat/githubaction
  -> Quality checks job
  -> Build delivery artifact job
~~~

# 6. Understand the workflow

## 6.1 Automatic execution

The push branch filter starts the workflow automatically only for
feat/githubaction. A push to main or another branch does not match it.

The manual workflow_dispatch event is not included in this demo because its
workflow file would first need to exist on the default branch.

## 6.2 The GitHub runner

ubuntu-latest creates a temporary Ubuntu machine. It does not contain your
local .venv, uncommitted files, or local configuration. The workflow checks out
the repository, installs uv and Python, and recreates the environment from
pyproject.toml and uv.lock.

## 6.3 Quality and delivery jobs

The CI job runs Ruff formatting, Ruff linting, mypy, and pytest. A failing
command makes the job red.

The delivery job declares needs: ci:

~~~text
CI fails -> delivery does not run
CI passes -> uv build -> upload artifact
~~~

This demonstrates Continuous Delivery: validated code is packaged, but it is
not automatically deployed to production.

# 7. Commit and push

Confirm the branch, inspect the changes, stage them, commit, and push:

~~~bash
git branch --show-current
git status
git diff
git add .github/workflows/ci-cd.yml 05_github_actions_ci_cd_student_lab.md
git diff --staged
git commit -m "ci(actions): add branch-based CI demo"
git push -u origin feat/githubaction
~~~

The first command must print feat/githubaction. The push then matches the event
and starts the workflow. On GitHub, use the branch selector to inspect
feat/githubaction. You do not need to merge it into main for this demo.

> [!IMPORTANT]
> The workflow file must be committed and included in the pushed branch.
> GitHub cannot see uncommitted local files.

# 8. Inspect the run

Open:

~~~text
Repository -> Actions -> CI and Delivery Demo
~~~

The Quality checks job should show:

~~~text
Download repository
Install uv
Install Python
Reproduce project environment
Check formatting
Run Ruff
Run mypy
Run tests
~~~

When all checks pass, GitHub starts Build delivery artifact.

If a check fails, inspect its log, correct the problem locally, and push:

~~~bash
git add <changed-files>
git commit -m "fix: make quality checks pass"
git push
~~~

Every push to feat/githubaction starts a new run.

To demonstrate another push without changing source code, create an empty
commit on the demo branch:

~~~bash
git branch --show-current
git commit --allow-empty -m "ci: retrigger GitHub Actions demo"
git push
~~~

Verify that the first command prints feat/githubaction before committing.

# 9. Download the artifact

On a successful run's summary page, find **Artifacts** and download
audience-metrics-package. It should contain files similar to:

~~~text
audience_metrics-0.1.0-py3-none-any.whl
audience_metrics-0.1.0.tar.gz
~~~

They were built only after CI succeeded.

# 10. What this demo does not control

This lab demonstrates:

~~~text
push to feat/githubaction -> checks -> package artifact
~~~

It does not stop failing code from being pushed or merged into main. A push
workflow runs after the triggering change already exists remotely.

## 10.1 Protecting main in a real repository

When repository controls are available, run CI for Pull Requests:

~~~yaml
on:
  pull_request:
    branches:
      - main
~~~

Then open:

~~~text
Repository -> Settings -> Rules -> Rulesets
~~~

For main, configure:

~~~text
Require a Pull Request before merging
Require status checks to pass before merging
Required check: Quality checks
~~~

The workflow may need to run once before its check name appears in the selector.

~~~text
feature branch
  -> Pull Request to main
  -> Quality checks
  -> pass: merge allowed
  -> fail: merge blocked
~~~

Running CI on a Pull Request without making it required provides feedback, but
does not necessarily block the merge.

## 10.2 Combining events

A production workflow may listen to several events:

~~~yaml
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]
  workflow_dispatch:
~~~

A common division of responsibilities is:

~~~text
Pull Request to main -> validate before merge
Push to main         -> build or deliver after merge
workflow_dispatch    -> authorized manual run
~~~

To run delivery only after a push to main, add this condition to that job:

~~~yaml
if: github.event_name == 'push' && github.ref == 'refs/heads/main'
~~~

That is the safer long-term design, but it needs repository controls that are
outside this quick demo.

# 11. Final checklist

- [ ] Local Ruff, mypy, and pytest checks pass.
- [ ] GitHub Actions is allowed in repository settings.
- [ ] The current branch is feat/githubaction.
- [ ] .github/workflows/ci-cd.yml exists on that branch.
- [ ] The workflow listens for pushes to feat/githubaction.
- [ ] A push creates a workflow run.
- [ ] The runner recreates the locked environment.
- [ ] Ruff, mypy, and pytest run in GitHub Actions.
- [ ] Delivery waits for CI.
- [ ] uv build creates the package.
- [ ] GitHub stores the package as an artifact.
- [ ] You understand that this demo does not protect main.
- [ ] You understand that protecting main needs PR CI plus required checks.

# 12. Key idea

GitHub Actions events decide **when automation runs**:

~~~text
push, Pull Request, manual request, schedule, release, ...
~~~

Repository rules decide **what must pass before merging**:

~~~text
Pull Request + required Quality checks -> control the merge into main
~~~

This lab intentionally uses the simpler demonstration:

~~~text
push to feat/githubaction -> validate -> build -> upload artifact
~~~