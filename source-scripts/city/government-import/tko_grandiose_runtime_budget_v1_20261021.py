"""Bind unchanged assembly resource costs to current original-model profiles."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-tko-grandiose-runtime-budget-v1-20261021'
DOC=BASE/BATCH

def main():
    assert not DOC.exists()
    folder=BASE/'government-xl-tko-grandiose-joint-runtime-v2-20261021'
    receipt,pins=authenticate(folder)
    path=folder/'metrics.json'
    assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))]
    metrics=read(path)
    refs=[Path(__file__),folder/'result.json',path]
    # Resource accounting is valid only for the exact measured current loader.
    for name,sha in metrics['inputHashes'].items():
        p=ROOT/name
        assert digest(p.read_bytes())==sha,name
        refs.append(p)
    rows=metrics['rows'];assert len(rows)==11 and all(r['sourcePreserved'] for r in rows)
    costs={key:sum(r['budget'][key] for r in rows) for key in ['geometryBytes','residentBytes','triangles','drawCalls']}
    costs['count']=len(rows)
    checks={profile:{key:dict(used=value,limit=limits[key],passed=value<=limits[key]) for key,value in costs.items()} for profile,limits in metrics['profiles'].items()}
    assert all(check['passed'] for profile in checks.values() for check in profile.values())
    result=dict(uids=[r['uid']for r in rows],sourceSHA256ByUid={r['uid']:r['sourceSHA256']for r in rows},aggregateOriginalModelCosts=costs,profileChecks=checks,originalModelResourceBudgetPassed=True,scope='Exact eleven original model assets only. Terrain and all other scene actors are excluded from model cache budgets. This is not an FPS measurement or a claim that the whole scene fits a mobile frame-time target.',geometryChanges=0,aiGeometryModelling=False,installationApproved=False)
    save(DOC/'budget.json',result)
    module('tko_budget_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'eleven-original-resource-budget-binding',refs,result)
if __name__=='__main__':main()
