"""Complete original vs production-generated private canopy surfaces, no acceptance."""
from pathlib import Path
import subprocess,numpy as np
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_component_contacts_20261009 import exact_component_contacts
B=ROOT/'docs/astra-city/government-import';NAME='government-xl-villa-private-canopy-collision-v1-20261015';DOC=B/NAME;OLD=B/'government-xl-villa-private-canopy-source-boundary-feasibility-v1-20261015'
def main():
 assert not DOC.exists();proposal=OLD/'proposal.json';pins={r['path']:r['sha256'] for r in read(OLD/'result.json')['evidenceRefs']};assert digest(proposal.read_bytes())==pins[str(proposal.relative_to(ROOT))];DOC.mkdir();capture=HERE/'villa_private_canopy_capture_v1_20261015.mjs';output=DOC/'rendered.json'
 subprocess.check_call(['node',str(capture),str(proposal.relative_to(ROOT)),str(output.relative_to(ROOT))],cwd=ROOT);rendered=read(output);paths=[Path(__file__),capture,proposal,OLD/'result.json']+[ROOT/p for p in rendered['inputHashes']]
 meshes={mode:np.concatenate([np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)] for r in rendered['rows'] if r['mode']==mode]) for mode in ['current','privateCandidate']}
 selection=B/'government-xl-villa-five-original-coupled-physical-v3-20261010/selection.json.gz';sources=read(selection)['rows'];paths.append(selection);results=[]
 for row in sources:
  asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];tri=decode_original_world_triangles(asset.read_bytes());paths.append(asset)
  for mode,mesh in meshes.items():
   result=exact_component_contacts(tri,list(range(len(tri))),mesh,list(range(len(mesh))));results.append({'uid':row['uid'],'mode':mode,'sourceSHA256':row['sourceSHA256'],'completeOriginalFaces':len(tri),'completeCanopyFaces':len(mesh),'contacts':result});print(row['uid'],mode,len(result['contacts']),flush=True)
 save(DOC/'collision.json.gz',{'rows':results,'qualification':'Exact surfaces for all complete original model faces versus current/private generated canopy faces. Contacts are not automatically penetration; no containment, model placed-world or full acceptance claim.'})
 summary={'uids':[r['uid'] for r in sources]+[read(proposal)['uid']],'rows':[{'uid':r['uid'],'mode':r['mode'],'completeOriginalFaces':r['completeOriginalFaces'],'completeCanopyFaces':r['completeCanopyFaces'],'surfaceContacts':len(r['contacts']['contacts']),'testedPairs':r['contacts']['trianglePairsTested']} for r in results],'sourceBuildingGeometryChanged':False,'liveGeometryChanged':False,'proposedProceduralGeometryChange':True,'fullAcceptance':False}
 save(DOC/'summary.json',summary)
 module('villa_private_collision_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(NAME,'complete-original-production-private-canopy-surface-collision-v1',paths,{**summary,'nextStep':'Classify retained exact boundary contacts versus positive volume penetration, including production Float32 effects and all generated posts; do not publish until current full acceptance.'})
if __name__=='__main__':main()
