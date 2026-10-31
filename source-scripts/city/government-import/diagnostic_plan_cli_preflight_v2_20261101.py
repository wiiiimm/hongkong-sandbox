"""Check the exact runner allowlist and every phase CLI before model work.

The runner is parsed as source, never imported or executed. No leases, model
commands, acceptance, geometry edits or database work are performed.
"""
import argparse
import ast
import json
from pathlib import Path
from diagnostic_plan_cli_preflight_v1_20261030 import check, ROOT, HERE
from hashlib import sha256

def runner_check(plan_path, runner_name):
    assert Path(runner_name).name==runner_name and runner_name.startswith('original_leased_diagnostic_sequence_') and runner_name.endswith('.py')
    runner=HERE/runner_name;raw=runner.read_bytes();tree=ast.parse(raw,filename=str(runner));assignments=[n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='ALLOWED' for t in n.targets)]
    assert len(assignments)==1
    allowed=ast.literal_eval(assignments[0].value);assert isinstance(allowed,set) and all(isinstance(n,str) for n in allowed)
    path=plan_path.resolve();assert path.is_relative_to(ROOT/'docs/astra-city/government-import');plan=json.loads(path.read_text());blocked=sorted({p['script'] for p in plan['phases']}-allowed)
    assert not blocked, 'Selected runner does not permit phase scripts: '+', '.join(blocked)
    return dict(runner=str(runner.relative_to(ROOT)),runnerSHA256=sha256(raw).hexdigest(),allPhaseScriptsAlreadyAllowed=True,runnerImported=False,runnerExecuted=False)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plan',required=True);p.add_argument('--runner',required=True);a=p.parse_args();path=ROOT/a.plan
    binding=runner_check(path,a.runner);result=check(path);result.update(binding);print(json.dumps({k:v for k,v in result.items() if k!='phases'}))

if __name__=='__main__':main()
