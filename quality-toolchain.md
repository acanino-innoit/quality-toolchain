# Quality toolchain lab: different tools, different evidence

**Estimated time:** 35–40 minutes  
**Where to work:** inside the downloaded `python-quality-toolchain-lab` repository.  
**Goal:** use Ruff, mypy, and pytest to diagnose different defects in the same prepared Python project.

You do not need to create the project or write tests from scratch. The repository intentionally starts in a failing state.

## 0. Open the project and reproduce its environment

From the folder that contains the repository:

```bash
cd python-quality-toolchain-lab
uv sync --locked
```

Open this folder in your editor. Its important structure is:

```text
python-quality-toolchain-lab/
├── pyproject.toml
├── uv.lock
├── src/
│   └── audience_metrics/
│       ├── __init__.py
│       ├── main.py
│       └── metrics.py
└── tests/
    ├── conftest.py
    └── test_metrics.py
```

### Run the example application

The repository includes an executable example in
`src/audience_metrics/main.py`. It passes a small set of hardcoded values to
the package functions and prints their results. Run the registered project
command with:

```bash
uv run audience-metrics
```

The `[project.scripts]` entry in `pyproject.toml` maps that command to the
`main()` function. The equivalent module command is:

```bash
uv run python -m audience_metrics.main
```

Because the initial implementation defects are intentional, some displayed
results may be incorrect until you complete the exercises below.

Inspect `pyproject.toml` before running anything else. Find these sections:

```text
[project]
[project.scripts]
[dependency-groups]
[tool.ruff]
[tool.ruff.lint]
[tool.mypy]
[tool.pytest.ini_options]
```

Checkpoint:

> Why can one file be read by the package manager, formatter, linter, type checker, and test runner?

## 1. Predict before running

The three tools ask different questions:

| Tool | Main question |
|---|---|
| `ruff format` | Is the source represented in the agreed format? |
| `ruff check` | Does the source contain enabled suspicious patterns? |
| `mypy` | Are values used consistently with their declared or inferred types? |
| `pytest` | Does the executed behavior satisfy the selected expectations? |

Open `src/audience_metrics/metrics.py`. Do not fix it yet.

Predict which tool should detect each problem:

1. inconsistent spacing and layout;
2. an imported module that is never used;
3. calling `.strip()` on a value that may be `None`;
4. subtracting `0.20` from `100` when `0.20` represents a 20% discount;
5. raising `IndexError` when the public behavior promises `ValueError`.

Record your predictions. You will compare them with the actual output.

## 2. Ruff formatter: representation

First run Ruff in observe-only mode:

```bash
uv run ruff format --check .
```

It should return a non-zero status because at least one file would be reformatted. This is an expected diagnostic result, not a broken installation.

Now apply the formatting change:

```bash
uv run ruff format .
uv run ruff format --check .
```

Inspect the edited file.

Checkpoint:

1. What changed?
2. Did the formatter remove the unused import?
3. Did it repair either business rule?

A formatter standardizes representation. Formatted code can still contain lint, type, and behavior defects.

## 3. Ruff linter: enabled source rules

Run the linter:

```bash
uv run ruff check .
```

Read the rule code and message. The configured rules should identify an unused import.

Apply safe automatic fixes and verify again:

```bash
uv run ruff check . --fix
uv run ruff check .
```

Do not assume that `--fix` can or should repair every lint diagnostic. In this project, the targeted unused import has a safe automatic fix.

Checkpoint:

> Ruff is now green. Which predicted problems can still exist, and why?

## 4. Choose what the tools enforce

The policy is customizable. Ruff and mypy do not have exactly the same configuration model:

Treat this section as a policy reference. During the timed lab, inspect the examples and run the single-rule Ruff command; do not try every available rule family.

- **Ruff** has a catalogue of lint rules identified by codes such as `F401` or families such as `F`, `B`, and `I`.
- **mypy** has strictness options and error codes. It checks type-related properties, not formatting or general lint style.

### Select and exclude Ruff rules

The complete searchable catalogue is the [official Ruff rule list](https://docs.astral.sh/ruff/rules/). Each rule page explains what it detects and whether an automatic fix exists.

This project currently uses:

```toml
[tool.ruff.lint]
select = ["E", "F", "I", "B"]
```

The prefixes select rule families:

| Prefix | Example responsibility |
|---|---|
| `E` | pycodestyle errors |
| `F` | Pyflakes checks such as unused imports |
| `I` | import ordering |
| `B` | likely bugs and design problems from flake8-bugbear |

Important difference:

```toml
select = ["B"]
```

replaces the default selection, while:

```toml
extend-select = ["B"]
```

adds `B` rules to the defaults.

Rules can be excluded globally or only for specific files:

```toml
[tool.ruff.lint]
select = ["E", "F", "I", "B"]
ignore = ["E501"]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101"]
```

Use exclusions only when the rule does not fit the project or a specific file category. Avoid hiding a genuine correctness problem merely to obtain a green result.

For a narrow experiment without changing `pyproject.toml`, select a rule on the command line:

```bash
uv run ruff check . --select F401
```

### Detect versus modify with Ruff

| Intention | Command | Modifies files? |
|---|---|---:|
| Detect formatting differences | `uv run ruff format --check .` | No |
| Apply formatting | `uv run ruff format .` | Yes |
| Detect lint violations | `uv run ruff check .` | No |
| Apply available safe lint fixes | `uv run ruff check . --fix` | Yes |

Ruff applies only fixes classified as safe by default. Some rules have no automatic fix. Ruff can expose or apply **unsafe fixes**, but those may change runtime behavior or remove comments and should not be enabled blindly:

```bash
# Show diagnostics and indicate available unsafe fixes without applying them
uv run ruff check . --unsafe-fixes

# Potentially behavior-changing: review before using
uv run ruff check . --fix --unsafe-fixes
```

You can also control which enabled rules Ruff may fix:

```toml
[tool.ruff.lint]
fixable = ["ALL"]
unfixable = ["F401"]
```

This configuration would still report `F401`, but `--fix` would not modify the file for that rule. See the [Ruff linter documentation](https://docs.astral.sh/ruff/linter/) and [complete Ruff settings](https://docs.astral.sh/ruff/settings/) for all selection, exclusion, and fix controls.

### Configure mypy's strictness and error codes

The current project uses:

```toml
[tool.mypy]
python_version = "3.12"
strict = true
files = ["src"]
```

`strict = true` enables a bundle of optional checks. The exact bundle can evolve between mypy versions, so it can also be useful to configure individual options or error codes explicitly:

```toml
[tool.mypy]
strict = true
enable_error_code = ["truthy-bool", "ignore-without-code"]
disable_error_code = ["var-annotated"]
```

Different modules can use different policies when a justified migration or boundary requires it:

```toml
[[tool.mypy.overrides]]
module = "tests.*"
allow_untyped_defs = true
```

For one exceptional line, a targeted suppression includes the exact error code:

```python
result = external_untyped_api()  # type: ignore[no-untyped-call]
```

Prefer a targeted code over a bare `# type: ignore`, and document why the exception is necessary.

Unlike Ruff, mypy reports type problems but does **not** provide a general automatic-fix mode. A developer must decide the correct annotation, narrowing, conversion, or design change. Use the [mypy configuration reference](https://mypy.readthedocs.io/en/stable/config_file.html) and [mypy error-code index](https://mypy.readthedocs.io/en/stable/error_codes.html) to choose the policy.

## 5. mypy: static type compatibility

Run the type checker against the package source:

```bash
uv run mypy src
```

Find the error in `normalize_name`. The annotation says that `name` may be either `str` or `None`:

```python
name: str | None
```

The body calls a string method before proving that the value is a string.

Edit only `normalize_name` so that:

- a string is stripped and returned;
- `None` produces an empty string;
- the declared return type remains `str`.

Then rerun:

```bash
uv run mypy src
```

Do not copy a finished implementation from the tests. Use type narrowing with an `if` statement.

Checkpoint:

1. Did mypy execute the function with example values?
2. Why does the discount formula remain valid from mypy's perspective?

Static type checking analyzes possible types without executing the program. A mathematically wrong expression can still be type-correct.

## 6. pytest: executable expectations

Run the prepared tests:

```bash
uv run pytest
```

Read the test summary before editing anything. Distinguish:

- the test that failed;
- the expected value or exception;
- the observed value or exception;
- the source function responsible.

Repair the two behavior defects in `metrics.py`:

### `discount_price`

The `discount` argument is a rate. Therefore:

```text
price = 100.0
discount = 0.20
expected result = 80.0
```

Do not subtract the rate directly from the price.

### `first_item`

For a non-empty list, return its first item. For an empty list, raise:

```python
ValueError("items must not be empty")
```

Rerun the tests after both fixes:

```bash
uv run pytest
```

The repository also contains a small passing fixture example. You do not need to edit it. Its purpose is to show that a fixture can provide test data and use `yield` to separate setup from cleanup.

Checkpoint:

> Why did pytest expose these defects after Ruff and mypy were already green?

Tests execute selected scenarios and compare observed behavior with explicit expectations. Passing tests are evidence for those scenarios, not proof that no undiscovered bug exists.

## 7. Run the complete verification loop

Run the final sequence exactly as a clean handoff or CI job should run it:

```bash
uv sync --locked
uv run ruff format --check .
uv run ruff check .
uv run mypy src
uv run pytest
```

All commands should finish successfully without editing files.

If a command fails, use the layer that failed:

| Failure | Investigate first |
|---|---|
| `uv sync --locked` | dependency declaration or stale/missing lockfile |
| `ruff format --check` | source representation |
| `ruff check` | enabled lint rule and reported location |
| `mypy` | annotations, inferred types, and narrowing |
| `pytest` | expected behavior, observed behavior, and test setup |

## 8. Connect the configuration to the commands

Return to `pyproject.toml` and match each block to its reader:

```text
[project]                    -> project metadata and runtime requirements
[project.scripts]            -> executable `uv run audience-metrics` command
[dependency-groups].dev      -> Ruff, mypy, and pytest
[tool.ruff]                  -> shared Ruff settings
[tool.ruff.lint]             -> enabled lint policy
[tool.mypy]                  -> static type-checking policy
[tool.pytest.ini_options]    -> test discovery and pytest behavior
```

The configuration is versioned with the source. That means another developer and an automated job can run the same commands under the same declared policy.

## Final reflection

Answer in one sentence each:

1. Which artifact makes the local environment disposable?
2. Why is `ruff format --check` preferable to `ruff format` in a verification job?
3. Give one defect Ruff can detect that mypy is not designed to detect.
4. Give one defect mypy can detect without running the program.
5. Give one defect that required an executable test.
6. Why does a completely green toolchain provide evidence rather than a mathematical proof of correctness?

## Optional extension

If time remains, add this new requirement and test it:

> `discount_price` must reject discounts below `0` or above `1` with `ValueError`.

Decide first which tool can enforce the requirement. Then add a test and implementation, and rerun the complete verification loop.

## Reference

- [Ruff formatter](https://docs.astral.sh/ruff/formatter/)
- [Ruff lint-rule catalogue](https://docs.astral.sh/ruff/rules/)
- [Ruff linter and automatic fixes](https://docs.astral.sh/ruff/linter/)
- [Ruff configuration](https://docs.astral.sh/ruff/configuration/)
- [mypy configuration](https://mypy.readthedocs.io/en/stable/config_file.html)
- [mypy error codes](https://mypy.readthedocs.io/en/stable/error_codes.html)
- [pytest configuration](https://docs.pytest.org/en/stable/reference/customize.html)
