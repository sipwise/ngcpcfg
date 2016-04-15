import os
import pytest

@pytest.fixture(scope="module", params=['hello', 'world'], ids=['first', 'second'])
def mountsda():
    print("setup")
    assert os.path.exists("/etc")
    pytest.yield_fixture(None)
    print("teardown")
