"""Lease-scoped co-imported source availability failure/retry; no approval."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from candidate_availability_graph_v1_20261026 import validate


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'preview', 'scope', 'native-context', 'uid', 'parent']:
        p.add_argument('--' + key, required=True)
    p.add_argument('--owned', action='store_true')
    a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base = ROOT / 'docs/astra-city/government-import'
    out, local = base / a.batch, HERE / 'local' / a.batch
    refs, pins = [Path(__file__)], {}

    def take(batch, path):
        if batch not in pins:
            pins[batch] = authenticate(base / batch)[1]
            refs.append(base / batch / 'result.json')
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    stage = HERE / 'local' / a.preview
    catalogue = take(a.preview, stage / 'catalogue.json')
    config = take(a.preview, stage / 'browser-config-390.json')
    assert config['terrain']==[] and a.uid!=a.parent
    models={m['uid']:m for m in catalogue['models']}
    assert 2<=len(models)==len(catalogue['models'])<=40
    assert all(m['publicationApproved']is False and m['placementReviewed']is False for m in models.values())
    graph,order=validate(list(models),[u+','+d['uid']for u,m in models.items()for d in m.get('supportDependencies',[])])
    assert a.parent in graph[a.uid]
    for model in models.values():
        for dep in model.get('supportDependencies',[]):
            peer=models[dep['uid']]
            assert dep==dict(uid=peer['uid'],state='installed',buildingCSUID=peer['buildingCSUID'],sha256=peer['sha256'])
        asset=stage/model['asset'];assert digest(asset.read_bytes())==model['sha256'];refs.append(asset)
    entry=next(r for r in catalogue['models']if r['uid']==a.uid)
    assert entry['uid'] == a.uid and entry['publicationApproved'] is False
    scope = take(a.scope, base / a.scope / 'summary.json')
    assert set(models)==set(scope['uids'])
    matching_scope = [r for r in scope['rows'] if r['uid'] == a.uid]
    assert len(matching_scope) == 1
    scope_row = matching_scope[0]
    assert scope_row['sourceSHA256'] == entry['sha256']
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    expected_manifest = digest(manifest.read_bytes())
    assert scope['currentManifestSHA256'] == expected_manifest
    refs.append(manifest)
    all_forms={}
    for scope_item in scope['rows']:
        for form in take(a.scope,base/a.scope/(scope_item['uid'].split('/')[1]+'-forms.json.gz')):
            key=form['building']['uid'];assert key not in all_forms or all_forms[key]==form;all_forms[key]=form
    forms=list(all_forms.values())
    for form in forms:
        tile = ROOT / '3d-viewer' / form['tile']
        assert digest(tile.read_bytes()) == form['tileSHA256']
        assert next(b for b in read(tile)['buildings'] if b['uid'] == form['building']['uid']) == form['building']
        refs.append(tile)
    retained=set(config['additionalRetainedUids'])
    assert retained=={n['uid']for row in scope['rows']for n in row['nearbyNativeActors']}
    archived={r['uid']:r for r in take(a.native_context,base/a.native_context/'native-input.json.gz')['rows']}
    assert retained<=set(archived) and retained<=set(all_forms)
    current={};all_current=set()
    for current_url in read(manifest)['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/current_url
        for native in read(path)['models']:
            assert native['uid']not in all_current;all_current.add(native['uid'])
            if native['uid']in retained:
                asset=(path.parent/native['asset']).resolve()
                assert native==archived[native['uid']]['entry'] and asset==ROOT/archived[native['uid']]['path'] and digest(asset.read_bytes())==native['sha256']
                refs.extend([path,asset]);current[native['uid']]=dict(entry=native,catalogueURL=current_url,assetURL=current_url.rsplit('/',1)[0]+'/'+native['asset'])
    assert set(current)==retained and not set(models)&all_current
    assert all(row['currentNativeActorsChecked']==len(all_current)for row in scope['rows'])
    parent=next(m for m in catalogue['models']if m['uid']==a.parent)
    assert any(dep==dict(uid=a.parent,state='installed',buildingCSUID=parent['buildingCSUID'],sha256=parent['sha256'])for dep in entry['supportDependencies'])
    url=config['catalogueURL']
    parent_catalogue=stage/'catalogue.json'
    source_asset,parent_asset=stage/entry['asset'],stage/parent['asset']
    assert digest(source_asset.read_bytes())==entry['sha256'] and digest(parent_asset.read_bytes())==parent['sha256']
    refs.extend([parent_catalogue,source_asset,parent_asset,HERE/'candidate_availability_graph_v1_20261026.py'])
    lease_path = local / 'reservation.json'
    if not a.owned:
        assert not out.exists() and not local.exists()
        resources = [('building:' if f['building']['uid'].startswith('landsd/') else 'source-form:') + f['building']['uid'] for f in forms]
        claim = reservations.claim(a.batch + '-' + str(uuid.uuid4()), sorted(set(resources)), batch=a.batch, ttl=3600)
        assert claim['ok']
        lease = claim['reservation']
        save(lease_path, json.loads(json.dumps(lease, default=str)))
        try:
            subprocess.run([sys.executable, str(HERE / 'harbourfront_reserved_runner_v1_20261021.py'), str(lease_path), sys.executable, __file__, *sys.argv[1:], '--owned'], cwd=ROOT, check=True)
        finally:
            if reservations.owns(lease):
                assert reservations.release(lease)['ok']
        return
    lease = read(lease_path)
    assert reservations.owns(lease) and not out.exists()
    tool = HERE / 'original_candidate_peer_failure_v1_20261026.mjs'
    refs.extend([tool, ROOT / '3d-viewer/city/app.js', ROOT / '3d-viewer/city/official-models.js', ROOT / '3d-viewer/city/model-support.js'])
    assert all(r.is_file() for r in refs)
    evidence = [dict(path=str(r.relative_to(ROOT)), sha256=digest(r.read_bytes())) for r in dict.fromkeys(refs)]
    input_path = local / 'input.json'
    save(input_path, dict(uid=a.uid, sourceSHA256=entry['sha256'], stage=str(stage.relative_to(ROOT)) + '/',
                          catalogueURL=config['catalogueURL'], viewerURL=config['viewerURL'],
                          form=next(f['building'] for f in forms if f['building']['uid'] == a.uid),
                          expectedDependencies=entry['supportDependencies'],retainedNativeSources=list(current.values()),
                          parent=dict(uid=a.parent, entry=parent, catalogueURL=url, assetURL=url.rsplit('/', 1)[0] + '/' + parent['asset']), evidenceRefs=evidence))
    out.mkdir()
    report_path = out / 'browser.json'
    with (out / 'worker.log').open('w') as log:
        proc = subprocess.run(['node', str(tool), str(input_path.relative_to(ROOT)), str(report_path.relative_to(ROOT))], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, env={**os.environ, 'CHROME_PATH': '/opt/google/chrome/chrome'}, timeout=1200)
    report = read(report_path)
    for item in evidence:
        assert digest((ROOT / item['path']).read_bytes()) == item['sha256']
    assert reservations.owns(lease) and digest(manifest.read_bytes()) == expected_manifest
    summary = dict(uids=list(models),uid=a.uid, parentUid=a.parent, sourceSHA256=entry['sha256'], parentSHA256=parent['sha256'],
                   proposedGraph=graph,dependencyFirstOrder=order,retainedNativeUids=sorted(retained),physicalAcceptance=False,
                   passed=proc.returncode == 0 and report['passed'], browserExitCode=proc.returncode,
                   leasedFormUids=sorted(f['building']['uid'] for f in forms), currentManifestSHA256=expected_manifest,
                   sourceGeometryChanges=0, nativeMetadataChanges=0, installationApproved=False, publication=False,
                   qualification='Supplemental actual native download failure/recovery only. A failed native must retain the dependent own BASIC; retry must activate exact unchanged source and native originals. This is not a substitute for full source/native own-view, collision, visual, identity or publication checks.')
    save(out / 'summary.json', summary)
    refs.append(input_path)
    module('native_dependency_failure_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'actual-co-imported-original-dependency-failure-and-recovery-diagnostic', list(dict.fromkeys(refs)), summary)


if __name__ == '__main__':
    main()
