"""Job scheduler. One job must exist per request id."""
from .client import Feed


class Scheduler:
    def __init__(self, feed: Feed) -> None:
        self.feed = feed
        self.jobs = {}

    def run_once(self) -> None:
        for event in self.feed.poll():
            self._handle(event)

    def _handle(self, event: dict) -> None:
        # BUG: on reconnect the feed replays events and we enqueue again.
        self.jobs[event["request_id"]] = {"id": event["request_id"], "state": "queued"}
