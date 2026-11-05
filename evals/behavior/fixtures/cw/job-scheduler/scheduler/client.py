class Feed:
    """Stub websocket feed. Drops and reconnects, replaying unacked events."""

    def __init__(self, script):
        self._script = list(script)

    def poll(self):
        return self._script.pop(0) if self._script else []
