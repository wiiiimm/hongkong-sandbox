"""Exact no-tolerance coverage diagnosis on the unchanged source-TIN pair."""
import numpy as np
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_projection_coverage_20261009 import exact_coverage
from source_closed_components import components
SOURCE=ROOT/'docs/astra-city/government-import/government-xl-tung-sing-original-pair-source-tin-context-20261010'
DOC=ROOT/'docs/astra-city/government-import/government-xl-tung-sing-original-pair-exact-source-terrain-20261010'
INPUT=ROOT/'docs/astra-city/government-import/government-xl-tung-sing-lei-tung-original-source-relationship-20261010'
def main():
 assert not DOC.exists();x=read(SOURCE/'complete-original-source-tin.json.gz');g=np.asarray(x['position'],float).reshape(-1,3)[np.asarray(x['index']).reshape(-1,3)];assert digest(g.astype('<f8').tobytes())==x['worldTriangleSHA256'];capture=read(INPUT/'current-inputs.json.gz');row=read(INPUT/'selection.json.gz')['rows'][0];pair=[decode_original_world_triangles((ROOT/row['candidate']['path']).read_bytes()),decode_original_world_triangles((ROOT/capture['podiumOriginalPath']).read_bytes())];t=np.concatenate(pair);raw=read(SOURCE/'diagnostic.json.gz');cases=[]
 for c in raw['allOriginalPairFaceContexts']:
  if not c['groundProjectionCovered']:cases.append({'sourceFace':c['sourceFace'],'rawPriorFailure':c,'exactOriginalCoverage':exact_coverage(t[c['sourceFace']],g)})
 save(DOC/'exact-original-coverage.json.gz',{'rows':cases,'wholeOriginalPairFaces':len(t),'wholeUnchangedOriginalTerrainFaces':len(g),'allRawMissingFacesExactlyCovered':all(r['exactOriginalCoverage']['exactProjectionCovered'] for r in cases),'sourceGeometryChanges':0,'terrainGeometryChanges':0,'physicalAccepted':False,'inputHashes':{str((SOURCE/'diagnostic.json.gz').relative_to(ROOT)):digest((SOURCE/'diagnostic.json.gz').read_bytes()),str((SOURCE/'complete-original-source-tin.json.gz').relative_to(ROOT)):digest((SOURCE/'complete-original-source-tin.json.gz').read_bytes())}})
 rows=[]
 for uid,tri,sha in zip(['landsd/53800:0','landsd/126434:0'],pair,[row['sourceSHA256'],read(INPUT/'original-source-lookup.json.gz')['rows'][1]['model']['asset']['sha256']]):
  parts=components(tri)['components'];rows.append({'uid':uid,'sourceSHA256':sha,'worldTriangleSHA256':digest(tri.astype('<f8').tobytes()),'wholeOriginalFaces':len(tri),'parts':[{'component':i,'originalFaceIds':p['faceIndices'],'position':tri[p['faceIndices']].reshape(-1).tolist(),'index':list(range(p['triangles']*3)),'bottomHKPD':float(tri[p['faceIndices'],:,1].min()),'worldBounds':[tri[p['faceIndices']].min(axis=(0,1)).tolist(),tri[p['faceIndices']].max(axis=(0,1)).tolist()]} for i,p in enumerate(parts)]})
 save(DOC/'complete-original-podium-footing-inputs.json.gz',{'terrain':x,'rows':rows,'basis':'complete-authenticated-original-source-TIN-only','physicalAccepted':False});print({'rawMissing':len(cases),'exactlyCovered':sum(r['exactOriginalCoverage']['exactProjectionCovered'] for r in cases),'pairParts':[len(r['parts']) for r in rows]},flush=True)
if __name__=='__main__':main()
