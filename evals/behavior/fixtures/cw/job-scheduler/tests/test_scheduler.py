from scheduler.core import Scheduler
from scheduler.client import Feed


def test_single_event_creates_one_job():
    s = Scheduler(Feed([[{"request_id": "r1"}]]))
    s.run_once()
    assert len(s.jobs) == 1
