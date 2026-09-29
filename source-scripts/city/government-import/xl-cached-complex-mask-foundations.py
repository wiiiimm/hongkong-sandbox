"""Diagnose cached multi-model groups with unchanged meshes and parent-ground masks.

Foundation results alone do not approve terrain coverage, runtime, or publication.
"""
import importlib.util
import shapely
from run import ROOT, HERE, read, save, digest


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


final = module('complex_mask_final', 'xl-final-script-pass.py')
patches = module('complex_mask_patch', 'native_patch_resolution.py')
BASE = ROOT / 'docs/astra-city/government-import/government-xl-remaining-20260923'
LOCAL = HERE / 'local/government-xl-complex-mask-foundations-20260929'
OUTPUT = BASE / 'complex-mask-foundations-20260929.json'


def run():
    selected = {r['uid']: r for r in read(BASE/'selection.json.gz')['rows']}
    parent_path = ROOT/'3d-viewer/city/data/terrain.json'
    parent = read(parent_path)
    sampler = final.s.resolution.terrain.fine.DemSampler(parent, rendered=True)
    reports = []
    for site in ('parkview','festival-walk','citywalk'):
        doc = BASE/f'{site}-terrain-diagnostic-20260925'
        result = read(doc/'result.json')
        source_path = ROOT/result['patchPath']
        assert digest(source_path.read_bytes()) == result['patchSHA256']
        candidate = read(source_path)
        inputs = read(doc/'neighbour-inputs.json.gz')
        forms = {r['building']['uid']:r['building'] for r in inputs['rows']}
        blocked = sorted({u for p in read(doc/'neighbour-checks.json')['patches'] for u in p['blockedBy']})
        protected = shapely.union_all([shapely.Polygon(forms[u]['rings'][0], forms[u]['rings'][1:]).buffer(.01,join_style='mitre') for u in blocked])
        bounds = final.s.resolution.extent(result['cells'],parent)
        proof = patches.preserve_parent_under_projection(candidate,bounds,protected,sampler)
        path = LOCAL/site/source_path.name
        save(path,candidate)
        terrain = patches._faces(candidate)
        models=[]
        for uid in result['uids']:
            row=selected[uid]
            triangles=final.s.glb_triangles(row)
            form=row['source']['building']
            footprint=shapely.Polygon(form['rings'][0],form['rings'][1:])
            foundation=final.foundation_context(triangles,terrain,footprint)
            strict=(foundation['completeTerrainTriangles']==foundation['triangles'] and foundation['fullyBuriedUpwardTriangles']==0 and foundation['fullyBuriedAreaFraction']<=.001)
            models.append({'uid':uid,'sourceSHA256':row['sourceSHA256'],'foundation':foundation,'strictFoundationAccepted':strict})
        report={'site':site,'sourcePatchSHA256':result['patchSHA256'],'parentSHA256':digest(parent_path.read_bytes()),
                'candidatePatch':{'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes())},
                'protectedNeighbourUids':blocked,'parentPreservation':proof,'models':models,
                'requiredBeforeAcceptance':['current-source-identity','terrain-seams-and-coverage','runtime','neighbors','browser'],
                'aiCalls':0,'modelGeometryChanges':0,'publication':False}
        reports.append(report)
        save(OUTPUT,{'rows':reports,'aiCalls':0,'modelGeometryChanges':0,'publication':False})
        print({'site':site,'protectedNeighbors':len(blocked),'models':[{'uid':r['uid'],'foundationPassed':r['strictFoundationAccepted'],'buriedUpward':r['foundation']['fullyBuriedUpwardTriangles']} for r in models]},flush=True)


if __name__=='__main__':run()
