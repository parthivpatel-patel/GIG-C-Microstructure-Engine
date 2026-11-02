"""Bounded equal-jitter delays for read-only acquisition, never order retries."""
import math
import random


def retry_delay(attempt, *, minimum=0, ceiling=30, random_source=random.random):
    """Return a finite delay; tests inject samples, not a global random seed.

    The exponential window is [half, full] with an optional Retry-After floor.
    A floor outside the permitted budget rejects rather than ignoring the server.
    """
    if type(attempt) is not int or not 1 <= attempt <= 5:
        raise ValueError('read_only_retry_attempt')
    if (type(minimum) not in (int, float) or type(ceiling) not in (int, float)
            or not math.isfinite(minimum) or not math.isfinite(ceiling)
            or not 0 <= minimum <= ceiling <= 30 or ceiling <= 0):
        raise ValueError('read_only_retry_budget')
    sample = random_source()
    if type(sample) not in (int, float) or not math.isfinite(sample) or not 0 <= sample <= 1:
        raise ValueError('read_only_retry_sample')
    upper = min(ceiling, 2 ** attempt)
    lower = max(minimum, upper / 2)
    upper = max(lower, upper)
    return lower + (upper - lower) * sample
