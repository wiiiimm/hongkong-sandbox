from pathlib import Path
import json,hashlib,datetime
R=Path(__file__).resolve().parents[8]
P=Path(__file__).resolve().parent
sha=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
v=P/'validation.json'
assert sha(v)=='318c3744fcc0b0f568e087f4b024c1ea8f0132ba5e77e1573c9b0b85a3ef26a3'
a=json.loads(v.read_bytes())
assert a['allPassed'] and a['noDB'] and a['noLease'] and a['noRealUnionOrTerrainEmission']
before=a['beforeLiteralPins'];end=a['beforeEndLiteralPins']
assert len(before)==len(end)==9160
assert [(x['path'],x['sha256'])for x in before]==[(x['path'],x['sha256'])for x in end]
assert all(x['unchanged']is True and x['actualSHA256']==x['sha256']for x in end)
assert len({x['path']for x in before})==9160
for q in before+a['orderedCodePins']:
 assert sha(R/q['path'])==q['sha256'],q['path']
assert len(a['orderedCodePins'])==5
assert sha(R/'3d-viewer/city/data/manifest.json')==a['currentManifestSHA256']=='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7'
assert len(a['commands'])==3 and [q['exitCode']for q in a['commands']]==[0,0,0]
for q in a['commands']:assert sha(R/q['log']['path'])==q['log']['sha256']
out=P/'root-independent-readonly-preparation-audit-v2.json'
assert not out.exists()
result=dict(checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),validationPath=str(v.relative_to(R)),validationSHA256=sha(v),all9160PinsVerified=True,orderedCodePinsVerified=5,currentManifestSHA256=a['currentManifestSHA256'],readonlyPreparationPassed=True,noDB=True,noLease=True,noUnionOrTerrainConstruction=True,commands=a['commands'],auditorSHA256=sha(Path(__file__)),priorRootAttempt=dict(passed=False,failure='Raw before/end list comparison incorrectly compared records with additional actualSHA256/unchanged fields; no processing or database operation ran.',correctedBy='Strict ordered path/SHA equality plus all actualSHA256/unchanged checks; no input tolerance.'))
out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
print(json.dumps(dict(rootAudit=str(out.relative_to(R)),sha256=sha(out),all9160PinsVerified=True,noDB=True,noLease=True)))
