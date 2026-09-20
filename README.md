# Python quality toolchain lab

A media analytics team has received Python code that "works on one machine"
but has not been checked with a shared quality process. This lab uses Ruff,
mypy, and pytest to turn different kinds of failures into useful evidence.

You need Python 3.12 or newer and `uv`.

Start by reproducing the locked environment:

```bash
uv sync --locked
```

Then follow [`quality-toolchain.md`](quality-toolchain.md).

## Run the example application

The project includes a small application entry point with hardcoded example
inputs. Run it through the command registered in `pyproject.toml`:

```bash
uv run audience-metrics
```

Alternatively, run the module directly:

```bash
uv run python -m audience_metrics.main
```

The example inputs and printed output are defined in
`src/audience_metrics/main.py`. This keeps the reusable calculations in
`metrics.py` separate from the executable example.

> [!IMPORTANT]
> The initial formatting, lint, type, and test failures are intentional.
