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

> [!IMPORTANT]
> The initial formatting, lint, type, and test failures are intentional.
