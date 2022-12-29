import multiprocessing
from multiprocessing import Queue

import pytest


@pytest.fixture(scope="session")
def queue() -> Queue:
    manager = multiprocessing.Manager()
    queue = manager.Queue()
    yield queue
