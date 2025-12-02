# tests/test_throttle.py
"""Tests for throttle function."""

import time

from inkpy.ink import throttle


def test_throttle_limits_calls():
    """Throttle should limit function calls to max once per interval."""
    call_count = 0

    def increment():
        nonlocal call_count
        call_count += 1

    # Throttle to 100ms
    throttled = throttle(increment, 100, leading=True, trailing=True)

    # Call rapidly 10 times
    for _ in range(10):
        throttled()
        time.sleep(0.01)  # 10ms between calls

    # Should have at most 2 calls (leading + trailing), not 10
    assert call_count <= 3


def test_throttle_leading_call():
    """Throttle with leading=True should call immediately on first call."""
    call_times = []

    def record_time():
        call_times.append(time.time())

    throttled = throttle(record_time, 100, leading=True, trailing=False)

    start = time.time()
    throttled()

    # First call should happen immediately
    assert len(call_times) == 1
    assert call_times[0] - start < 0.01  # Within 10ms


def test_throttle_trailing_call():
    """Throttle with trailing=True should call after interval ends."""
    call_count = 0

    def increment():
        nonlocal call_count
        call_count += 1

    throttled = throttle(increment, 50, leading=True, trailing=True)

    # Rapid calls
    throttled()  # Leading call (1)
    throttled()
    throttled()

    # Wait for trailing call
    time.sleep(0.1)

    # Should have exactly 2 calls: leading + trailing
    assert call_count == 2
