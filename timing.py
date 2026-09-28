from time import perf_counter
from contextlib import contextmanager

TIMINGS: dict[str, float] = {}

@contextmanager
def timed(stage: str):
    t = perf_counter()
    yield
    TIMINGS[stage] = round((perf_counter() - t) * 1000)