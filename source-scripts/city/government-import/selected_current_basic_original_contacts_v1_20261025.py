"""Check one explicitly nominated current BASIC podium with the existing harness.

No imported geometry, support approval, source change or publication.
"""
import argparse,subprocess
from copy import deepcopy
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for key in ['batch','runtime','scope','uid','support']:p.add_argument('--'+key,required=True)
 a=p.parse_args();assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.runtime,a.scope])
 base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();refs=[Path(__file__)];pins={}
 def take(name,filename):
  if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
  path=base/name/filename;assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 selection=take(a.runtime,'selection.json.gz');sources=[r for r in selection['rows']if r['uid']==a.uid];assert len(sources)==1
 source=deepcopy(sources[0]);entry=source['candidate']['entry'];assert entry.get('proceduralWindows')in [None,False]
 entry_bindings={}
 if 'proceduralWindows'not in entry:entry['proceduralWindows']=False;entry_bindings['proceduralWindows']=False
 forms=take(a.scope,a.uid.split('/')[1]+'-forms.json.gz');supports=[f for f in forms if f['building']['uid']==a.support];assert len(supports)==1
 support=supports[0];assert support['building']['structureType']=='Podium'and support['building']['parent']==source['source']['building']['parent']and support['building']['parent']
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256']==pins[a.scope][str(manifest.relative_to(ROOT))];refs.append(manifest)
 for url in read(manifest)['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;refs.append(path)
  for m in read(path)['models']:assert m['uid']!=a.support and a.support not in m.get('suppressesBuildingUids',[])
 asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256']==source['candidate']['entry']['sha256'];refs.append(asset)
 for f in [source['source'],support]:
  path=ROOT/'3d-viewer'/f['tile'];assert digest(path.read_bytes())==f['tileSHA256'];assert[f['building']]==[b for b in read(path)['buildings']if b['uid']==f['building']['uid']];refs.append(path)
 rows=[dict(uid=a.uid,supportUid=a.support,source=source,supportForm=support)]
 save(out/'input.json.gz',dict(rows=rows,manifestSHA256=selection['manifestSHA256'],evidenceRefs=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in dict.fromkeys(refs)]))
 tool=HERE/'current_basic_podium_original_contact_v1_20261023.mjs'
 with(out/'worker.log').open('w')as log:subprocess.run(['node',str(tool),str(out.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 report=read(out/'checks.json.gz');assert len(report['rows'])==1
 for path,sha in report['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
 r=report['rows'][0];assert r['uid']==a.uid and r['supportUid']==a.support
 result=dict(diagnosticEntryBindings=entry_bindings,uids=[a.uid],supportUid=a.support,canonicalContactPassed=r['canonicalContactPassed'],usableBasicSupportDiagnostic=r['usableBasicSupportDiagnostic'],basicIsCurrentFinalSupport=r['basicIsCurrentFinalSupport'],samples=r['proof']['samples'],strictContacts=r['proof']['strictContacts'],unresolved=len(r['proof']['unresolved']),sourceGeometryChanges=0,installationApproved=False,physicalSupportAccepted=False,publication=False,newlyInstalled=0,qualification='Explicit exact current source and same-parent BASIC podium with the unchanged canonical support harness. No source geometry or surveyed fields changed. Four-world support, retained contacts, source identity, browser and publication remain separate.')
 save(out/'summary.json',result);refs.append(tool)
 module('selected_current_basic_contacts_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'explicit-current-basic-podium-original-contact-diagnostic',list(dict.fromkeys(refs)),result)
 print({k:result[k]for k in ['canonicalContactPassed','usableBasicSupportDiagnostic','samples','strictContacts','unresolved']},flush=True)
if __name__=='__main__':main()
