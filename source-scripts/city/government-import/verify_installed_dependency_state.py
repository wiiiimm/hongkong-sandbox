"""Read-only exact current installed dependency evidence; never alter declarations."""
import argparse
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect


def verify(doc):
    doc=Path(doc).resolve();assert doc.is_relative_to(ROOT/'docs/astra-city/government-import')
    hashes={}
    def pinned(path):
        path=Path(path).resolve();assert path.is_relative_to(ROOT)
        raw=path.read_bytes();hashes[str(path.relative_to(ROOT))]=digest(raw)
        return read(path)
    pointer=pinned(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json')
    manifest=pinned(ROOT/'3d-viewer/city/data/manifest.json')
    inventory=pinned(ROOT/pointer['inventory']);assert inventory['snapshotId']==pointer['snapshotId']
    inputs=pinned(doc/'neighbour-inputs.json.gz');standard=pinned(doc/'neighbour-checks.json')
    blocked={r['uid'] for r in standard['rows'] if r['existingNative'] and r['reasons']}
    for patch in inputs['patches']:blocked.update(patch.get('replaces',{}).get('retainedUids',[]))
    entries={}
    for url in manifest['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url;cat=read(path)
        for entry in cat['models']:
            assert entry['uid'] not in entries,'Ambiguous current source UID'
            entries[entry['uid']]=(entry,path)
    wanted={d['uid'] for uid in blocked for d in entries[uid][0].get('supportDependencies',[])}
    proofs={}
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        for uid in sorted(wanted):
            if uid not in entries:continue
            entry,catpath=entries[uid];pinned(catpath)
            asset=(catpath.parent/entry['asset']).resolve();assert asset.is_relative_to(ROOT/'3d-viewer')
            assetsha=digest(asset.read_bytes());hashes[str(asset.relative_to(ROOT))]=assetsha
            row=con.execute('SELECT review_state,source_sha256,result,initial_evidence FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(pointer['snapshotId'],uid)).fetchone()
            if row is None:continue
            state,sha,result,initial=row;installed=False;acceptance=None
            parts=[p for p in inventory['parts'] if p['uid']==uid]
            assert len(parts)==1, 'Installed dependency absent or duplicated in current source inventory'
            part=parts[0]
            assert part.get('candidate',{}).get('sha256')==sha and part['objectId']==entry['objectId']==initial['objectId'], 'Current inventory and Neon source identity disagree'
            # Legacy publicationApproved=false is never silently overridden.
            # Require the exact accepted receipt plus its unchanged catalogue and
            # successful staged/live browser receipts from the verified review.
            if state=='installed-verified' and sha==entry['sha256']==assetsha and not entry.get('publicationApproved'):
                ref=result.get('evidence');expected=result.get('sha256')
                if isinstance(ref,str) and isinstance(expected,str):
                    path=(ROOT/ref).resolve()
                    if path.is_relative_to(ROOT) and path.is_file() and digest(path.read_bytes())==expected:
                        a=pinned(path)
                        if a.get('uid')==uid and a.get('sourceSHA256')==sha and a.get('catalogueSHA256')==digest(catpath.read_bytes()):
                            reports=[]
                            for key,name in [('stagedBrowserSHA256','staged-browser.json'),('liveBrowserSHA256','live-browser.json')]:
                                browser=path.parent/name
                                if browser.exists() and digest(browser.read_bytes())==a.get(key):
                                    report=pinned(browser)
                                    reports.append(report.get('passed') is True and any(v.get('uid')==uid for v in report.get('views',[])))
                            installed=len(reports)==2 and all(reports)
                            if installed:acceptance={'path':ref,'sha256':expected,'catalogueSHA256':a['catalogueSHA256']}
            proofs[uid]={'uid':uid,'csuid':entry.get('buildingCSUID'),'sourceSHA256':sha,'assetSHA256':assetsha,
                'reviewState':state,'snapshotId':pointer['snapshotId'],'snapshotVerified':True,
                'installedAcceptanceVerified':installed,'installedAcceptance':acceptance,
                'reviewResultSHA256':digest(__import__('json').dumps(result,sort_keys=True,separators=(',',':')).encode())}
    for path,sha in hashes.items():assert digest((ROOT/path).read_bytes())==sha,'Installed dependency inputs changed'
    result={'version':1,'snapshotId':pointer['snapshotId'],'proofs':proofs,'inputHashes':hashes,
        'scriptExternalAICalls':0,'modelGeometryChanges':0,'publication':False,
        'qualification':'Read-only exact current installed acceptance by UID/CSUID/source and asset hashes. Historical dependency labels are retained. Full support and all physical/runtime/publication gates remain required.'}
    save(doc/'installed-dependency-state.json',result)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('doc');a=p.parse_args()
    result=verify(ROOT/a.doc)
    print(__import__('json').dumps({'snapshot':result['snapshotId'],'verifiedDependencies':list(result['proofs'])}))
