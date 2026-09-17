from collections.abc import Iterator

import pytest


@pytest.fixture
def sample_names() -> Iterator[list[str]]:
    names = ["Ada", "Grace"]
    yield names
    names.clear()
