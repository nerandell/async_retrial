def test_time_delay_for_next_retry(exponential_retry_handler, strategic_retry_handler):
    time_delays = [exponential_retry_handler._get_wait_time(attempt) for attempt in range(5)]
    assert time_delays == [0, 2, 4, 8, 16]
    time_delays = [strategic_retry_handler._get_wait_time(attempt) for attempt in range(5)]
    assert time_delays == [0, 3, 7, 11, 11]
