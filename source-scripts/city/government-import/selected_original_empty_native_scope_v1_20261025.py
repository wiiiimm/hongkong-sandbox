"""Bind a zero-current-native nomination to its authenticated complete scope."""
import argparse
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','scope','runtime']:p.add_argument('--'+key,required=True)
    a=p.parse_args();assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.scope,a.runtime])
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=take(a.runtime,base/a.runtime/'selection.json.gz');scope=take(a.scope,base/a.scope/'summary.json')
    sources={r['uid']:r['sourceSHA256']for r in selection['rows']};assert sources
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256']==scope['currentManifestSHA256'];refs.append(manifest)
    selected=[r for r in scope['rows']if r['uid']in sources];assert len(selected)==len(sources)and{r['uid']for r in selected}==set(sources)
    for r in selected:
        assert r['sourceSHA256']==sources[r['uid']]and not r['nearbyNativeActors']and r['currentNativeActorsChecked']>0
    result=dict(uids=sorted(sources),sourceSHA256ByUid=sources,rows=[],completeScopeRows=selected,currentManifestSHA256=selection['manifestSHA256'],physicalAcceptance=False,installationApproved=False,publication=False,sourceGeometryChanges=0,qualification='Every selected source has zero current native candidates in its authenticated complete four-world closed-box scope, including the0.5m nomination margin. Empty finite-contact scope only; BASIC/co-import contacts and all other acceptance checks remain separate. Any nominated current native stops this route.')
    save(out/'summary.json',result);module('empty_native_scope_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-authenticated-empty-current-native-scope',refs,result)


if __name__=='__main__':main()
