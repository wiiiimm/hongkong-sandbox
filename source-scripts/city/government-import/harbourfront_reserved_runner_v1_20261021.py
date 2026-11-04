"""Same fail-closed lease supervision with a bounded 60s database observation window."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'shared-modelling'))
import reservation_runner
# Preserve ownership checks, heartbeat cadence, process-group cleanup and TTL.
# 300 + 2*60 + 5 < 3600 leaves ample expiry headroom on this memory-pressured host.
reservation_runner.DB_TIMEOUT_SECONDS=60
result=reservation_runner.run_reserved(sys.argv[1],sys.argv[2:],ttl=3600)
print(json.dumps(result,indent=2),flush=True)
raise SystemExit(0 if result['ok'] else result['exitCode'])
