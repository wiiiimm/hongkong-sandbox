"""Fresh tower/platform current identity for a mandatory three-original diagnostic."""
import importlib.util,shutil,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from tung_sing_current_bound_identity_20261010 import stream_pin
from routed_original_cell_identity import verify_files
DOC=ROOT/'docs/astra-city/government-import/government-xl-tung-sing-three-original-tower-current-identity-inputs-v2-20261010'
OLD=DOC.parent/'government-xl-tung-sing-lei-tung-original-source-relationship-20261010'
INPUT=DOC.parent/'government-xl-tung-sing-two-original-physical-inputs-20261010'
LOCAL=HERE/'local'/DOC.name
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 assert not DOC.exists();DOC.mkdir(parents=True);msha=digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes());selection=read(INPUT/'selection.json.gz');final=module('nested_fresh_forms','xl-final-script-pass.py');contexts=[];rows=selection['rows'];tower=next(r for r in rows if r['uid']=='landsd/53800:0');podium=next(r for r in rows if r['uid']=='landsd/126434:0')
 for row in rows:
  row['triangles']=row['native']['model']['triangles'];a=decode_original_world_triangles((ROOT/row['candidate']['path']).read_bytes());lo,hi=a.min(axis=(0,1)),a.max(axis=(0,1));forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);assert next(b for b,_,_ in forms if b['uid']==row['uid'])==row['source']['building'];context={'uid':row['uid'],'sourceSHA256':row['sourceSHA256'],'identity':final.identity_context(row,a,forms),'neighbourTileHashes':{url:digest((ROOT/'3d-viewer'/url).read_bytes()) for _,_,url in forms}};contexts.append(context)
  raw=verify_files(row,context,LOCAL/'raw-preflight');save(DOC/('raw-'+row['uid'].split('/')[1].replace(':','-')+'.json'),raw)
  if row['uid']==tower['uid']:capture={'manifestSHA256':msha,'forms':[b for b,_,_ in forms],'tileHashes':context['neighbourTileHashes'],'podiumOriginalPath':podium['candidate']['path']}
 query=module('nested_current_primary','xl-tung-sing-lei-tung-source-relationship-20261010.py');query.DOC=DOC;where="BuildingCSUID IN ('3417311416T20050430','3417111358P20060312')";primary=query.query(0,where,'exact-current-primary',True);relations=query.query(1002,where,'exact-current-structure-relations');assert not relations
 source=read(OLD/'original-source-lookup.json.gz');source['primaryRecords']=primary;source['exactRelations']=relations;source['exactStructures']=[]
 for name in ['ha-estate-layout.pdf','ha-tung-sing-floor-plan.pdf']:
  shutil.copyfile(OLD/name,DOC/name);shutil.copyfile(OLD/(name+'.request.json'),DOC/(name+'.request.json'))
 save(DOC/'original-source-lookup.json.gz',source);save(DOC/'current-inputs.json.gz',capture);save(DOC/'complete-original-stream-pins.json.gz',{'tower':stream_pin((ROOT/tower['candidate']['path']).read_bytes(),tower['modelId'],11445),'podium':stream_pin((ROOT/podium['candidate']['path']).read_bytes(),podium['modelId'],432)});save(DOC/'selection.json.gz',{**selection,'manifestSHA256':msha});save(DOC/'context.json.gz',{'rows':contexts})
 parent=read(ROOT/'3d-viewer/city/data/government-native-163705-0.json');second=module('nested_parent_bounds','xl-second-pass.py');rects=[second.resolution.rectangle_for(r['native']['model']['worldBounds'],parent) for r in rows];cells=[min(x[0] for x in rects),min(x[1] for x in rects),max(x[2] for x in rects),max(x[3] for x in rects)];assert 0<cells[0]<cells[2]<parent['w']-1 and 0<cells[1]<cells[3]<parent['h']-1;save(DOC/'nested-parent-scope.json',{'parentURL':'city/data/government-native-163705-0.json','parentSHA256':digest((ROOT/'3d-viewer/city/data/government-native-163705-0.json').read_bytes()),'childCoarseCells':cells,'childBounds':second.resolution.extent(cells,parent),'allOriginalParentActorsRetained':parent['meta']['targetUids'],'terrainBudgetRaised':False,'physicalAccepted':False})
 assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==msha
 (DOC/'README.md').write_text('Fresh complete current actor/manifest bindings and fresh authoritative government primary queries for the previously reviewed exact Tung Sing/Lei Tung original-envelope relationship. Both complete original root/BIN/world streams and source versions remain unchanged. This distinct candidate uses the existing 163705 native terrain as a nested parent; child cells are strictly inside the original parent. All four installed parent actors remain independently checked. No runtime budget increase, geometry edit, physical approval or installation credit. Prior source/roof/retained-budget failures remain immutable.\n')
 refs=[ROOT/r['candidate']['path'] for r in rows]+[ROOT/'3d-viewer/city/data/manifest.json',ROOT/'3d-viewer/city/data/government-native-163705-0.json',Path(__file__),HERE/'tung_sing_adjacent_original_envelope_identity_20261010.py',HERE/'tung_sing_current_bound_identity_20261010.py',HERE/'xl-tung-sing-lei-tung-source-relationship-20261010.py']+[ROOT/'3d-viewer'/u for c in contexts for u in c['neighbourTileHashes']]
 module('nested_capture_fence','xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(DOC.name,'fresh-current-original-primary-nested-inputs-v1',refs,{'uids':[r['uid'] for r in rows],'identityAccepted':False,'physicalAccepted':False,'remainingReason':'fresh-reviewed-identity-replay-and-complete-nested-physical-gates','sourceIdentityReviewUsedAI':True,'previousRuntimeBudgetFailureRetained':True})
 print({'freshManifestSHA256':msha,'nestedCells':cells,'capture':str(DOC.relative_to(ROOT))},flush=True)
if __name__=='__main__':main()
