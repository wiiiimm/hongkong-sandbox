"""Run fourteen explicit original-source terrain continuations sequentially.

No publisher or AI calls. Each child owns and releases its own fenced source lease.
A failed child is recorded and never prevents independent sources from running.
"""
import json
import subprocess
import sys
from run import ROOT, HERE, read, save

BATCH = "government-xl-extended-14-20261005"
BASE = "docs/astra-city/government-import/government-xl-extended-14-inputs-20261005"
DOC = ROOT / "docs/astra-city/government-import" / BATCH
LOCAL = HERE / "local" / BATCH


def run():
    assert not (DOC / "commands.json").exists(), "Completed commands are immutable"
    rows = read(ROOT / BASE / "check-selection.json.gz")["rows"]
    assert len(rows) == 14
    LOCAL.mkdir(parents=True, exist_ok=True)
    outcomes = []
    for row in rows:
        uid = row["uid"]
        child = "government-xl-extended-" + uid.split("/")[1].split(":")[0] + "-20261005"
        log = LOCAL / (child + ".log")
        command = [sys.executable, str(HERE / "xl-indexed-terrain-continuation.py"),
                   "--uid", uid, "--batch", child, "--base", BASE]
        print(json.dumps({"starting": uid, "name": row["name"], "child": child}), flush=True)
        with log.open("w") as output:
            proc = subprocess.run(command, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT)
        result_path = ROOT / "docs/astra-city/government-import" / child / "result.json"
        result = read(result_path) if result_path.exists() else None
        outcome = {"uid": uid, "name": row["name"], "batch": child,
                   "returncode": proc.returncode, "command": command,
                   "log": str(log.relative_to(ROOT)), "result": result}
        outcomes.append(outcome)
        save(DOC / "working-commands.json", {"batch": BATCH, "rows": outcomes})
        print(json.dumps({"completed": uid, "returncode": proc.returncode,
                          "checksPassed": result and result["scriptChecksPassed"],
                          "reasons": result and result["reasons"]}), flush=True)
    save(DOC / "commands.json", {"batch": BATCH, "rows": outcomes,
                                "newlyInstalled": 0, "scriptExternalAICalls": 0})


if __name__ == "__main__": run()
