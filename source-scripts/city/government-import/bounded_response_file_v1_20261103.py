"""Retain a bounded response, including failed partial bytes, without retry/reset."""
import hashlib
from pathlib import Path


def receive(response, destination, maximum, checkpoint=None):
    destination = Path(destination)
    assert maximum > 0 and not destination.exists()
    destination.parent.mkdir(parents=True, exist_ok=True)
    received = 0
    digest = hashlib.sha256()
    with destination.open('xb') as output:
        while True:
            block = response.read(min(4 * 1024 * 1024, maximum - received + 1))
            if not block:
                break
            output.write(block)
            digest.update(block)
            received += len(block)
            if checkpoint:
                checkpoint(received)
            if received > maximum:
                raise ValueError('Response exceeds byte cap; partial file retained')
    return dict(receivedBytes=received, sha256=digest.hexdigest())
