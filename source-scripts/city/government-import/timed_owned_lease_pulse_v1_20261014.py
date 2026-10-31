"""Timed DB ownership/heartbeat pulse; explicit fence boundaries always check."""
import time
class TimedOwnedLeasePulse:
    def __init__(self, owns, heartbeat, *, clock=time.monotonic, interval=20):
        assert interval>0
        self.owns=owns;self.heartbeat=heartbeat;self.clock=clock;self.interval=interval;self.last_heartbeat=clock()
    def __call__(self, *, force=False):
        now=self.clock();due=now-self.last_heartbeat>=self.interval
        if force or due:assert self.owns(),'Canonical lease is not owned'
        if due:
            assert self.heartbeat()['ok'],'Canonical lease heartbeat failed'
            self.last_heartbeat=now
