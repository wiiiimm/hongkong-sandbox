"""Refresh the explicitly stale cached original geometry using the production loader.

No old review or terrain acceptance is promoted. Reuse original DTM grid receipts,
require all source bytes/current tile records, and generate read-only diagnostics.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path
from run import ROOT, read, save, digest
DIR=ROOT/'source-scripts/city/government-import'
BASE=ROOT/'docs/astra-city/government-import'

def ref(path):return {'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes())}

def main():
    p=argparse.ArgumentParser();p.add_argument('--batch',required=True);a=p.parse_args()
    assert a.batch.startswith('government-xl-') and Path(a.batch).name==a.batch
    doc=BASE/(a.batch+'-inputs');local=DIR/'local'/(a.batch+'-inputs');assert not doc.exists()
    previous_path=BASE/'government-xl-remaining-historical-current-tin-preview-20261007/result.json';previous=read(previous_path)
    old_path=BASE/'government-xl-original-dtm-contact-preview-20261007/result.json';old=read(old_path)
    wanted={r['uid'] for r in previous['skipped']};assert len(wanted)==90
    manifest_path=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifest_path)
    installed={m['uid'] for url in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']}
    selections=[];contexts=[];refs=[ref(previous_path),ref(old_path),ref(Path(__file__))];rows=[]
    for prior in old['rows']:
        if prior['uid'] not in wanted or prior['uid'] in installed:continue
        selection_path=BASE/prior['priorBatch']/'selection.json.gz';selection=read(selection_path)
        row=next(r for r in selection['rows'] if r['uid']==prior['uid']);assert row['sourceSHA256']==prior['sourceSHA256']==digest((ROOT/row['candidate']['path']).read_bytes())
        tile_path=ROOT/'3d-viewer'/row['source']['tile'];assert digest(tile_path.read_bytes())==row['source']['tileSHA256']
        assert next(b for b in read(tile_path)['buildings'] if b['uid']==row['uid'])==row['source']['building']
        selections.append(row);contexts.append({'uid':row['uid'],'sourceSHA256':row['sourceSHA256'],'neighbourTileHashes':{row['source']['tile']:row['source']['tileSHA256']}})
        refs.append(ref(selection_path));assert digest((ROOT/prior['grid']['path']).read_bytes())==prior['grid']['sha256']
        rows.append({**prior,'historicalPriorBatch':prior['priorBatch'],'historicalGeometry':prior['geometry'],'priorBatch':doc.name})
    assert len(selections)==len(rows)>0
    frozen={'rows':selections,'manifestSHA256':digest(manifest_path.read_bytes()),'diagnosticOnly':True,'publication':False}
    save(doc/'check-selection.json.gz',frozen);save(doc/'selection.json.gz',frozen);save(doc/'context.json.gz',{'rows':contexts})
    save(doc/'refresh-inputs.json',{'evidenceRefs':refs,'uids':[r['uid'] for r in rows],'modelGeometryChanges':0,'scriptExternalAICalls':0,'publication':False})
    geometry=local/'fresh-world-geometry.json.gz'
    subprocess.run(['node',str(DIR/'xl-original-world-geometry-diagnostic.mjs'),str(doc.relative_to(ROOT)),str(geometry.relative_to(ROOT))],cwd=ROOT,check=True)
    actual=read(geometry);assert actual['diagnosticOnly'] and not actual['publication']
    for path,sha in actual['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
    assert {r['uid'] for r in actual['rows']}=={r['uid'] for r in rows}
    geometry_ref=ref(geometry)
    for row in rows:row['geometry']=geometry_ref
    receipt={'source':old['source'],'rows':rows,'freshProductionGeometry':True,'evidenceRefs':[*refs,geometry_ref],'diagnosticOnly':True,'publication':False,'newlyInstalled':0,'modelGeometryChanges':0,'scriptExternalAICalls':0,'qualification':'Fresh unchanged original assets decoded with current production loader and exact original tile records. No source/identity/terrain acceptance or installation credit.'}
    save(doc/'result.json',receipt)
    subprocess.run([sys.executable,str(DIR/'xl-fresh-current-tin-preview.py'),'--batch',a.batch,'--receipt',str((doc/'result.json').relative_to(ROOT))],cwd=ROOT,check=True)

if __name__=='__main__':main()
