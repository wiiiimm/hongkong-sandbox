"""Fail-closed supervision with a bounded 120-second database observation window.

Only the observation timeout changes on this swap-pressured host. Ownership,
300-second heartbeat cadence, one-hour TTL and process-group cleanup stay intact.
300 + 2*120 + 5 < 3600 preserves ample expiry headroom.
"""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'shared-modelling'))
import reservation_runner
reservation_runner.DB_TIMEOUT_SECONDS=120
result=reservation_runner.run_reserved(sys.argv[1],sys.argv[2:],ttl=3600)
print(json.dumps(result,indent=2),flush=True)
raise SystemExit(0 if result['ok'] else result['exitCode'])
