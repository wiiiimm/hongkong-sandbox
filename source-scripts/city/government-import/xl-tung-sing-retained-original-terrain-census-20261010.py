"""Read-only exact original TIN redundancy census; never waive a runtime budget."""
import importlib.util,numpy as np,collections
from run import ROOT,HERE,read,save,digest
DOC=ROOT/'docs/astra-city/government-import/government-xl-tung-sing-retained-original-terrain-census-20261010'
OLD=DOC.parent/'government-xl-tung-sing-two-retained-original-physical-v2-20261010'
def main():
 assert not DOC.exists()
 s=importlib.util.spec_from_file_location('tung_sing_terrain_decode',HERE/'xl-second-pass.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 parent=read(ROOT/'3d-viewer/city/data/terrain.json');sel=read(OLD/'selection.json.gz');retained=ROOT/'3d-viewer/city/data/government-native-163705-0.json';old=read(retained)
 rects=[m.resolution.rectangle_for(r['native']['model']['worldBounds'],parent) for r in sel['rows']]+[old['coarseCells']]
 cells=[min(q[0] for q in rects),min(q[1] for q in rects),max(q[2] for q in rects),max(q[3] for q in rects)];bb=m.resolution.extent(cells,parent);fragments=[];refs={str(retained.relative_to(ROOT)):digest(retained.read_bytes())};records=[]
 for row in read(OLD/'source-recovery.json')['sheets']:
  sheet=ROOT/row['cache'];paths=sorted((sheet/'terrain').rglob('*.gltf'));a=np.concatenate([m.terrain_triangles(p) for p in paths]);a=a[(a[:,:,0].max(axis=1)>=bb[0])&(a[:,:,0].min(axis=1)<=bb[2])&(a[:,:,2].max(axis=1)>=bb[1])&(a[:,:,2].min(axis=1)<=bb[3])];fragments.append(a);records.append({'sheet':row['sheet'],'wholeOriginalFacetsInExpandedScope':len(a)})
  for f in row['terrainFiles']:
   p=sheet/'terrain'/f['name'];assert digest(p.read_bytes())==f['sha256'];refs[str(p.relative_to(ROOT))]=f['sha256']
 native=np.concatenate(fragments);canonical=[tuple(sorted(map(tuple,t))) for t in native];count=collections.Counter(canonical);duplicates=sum(n-1 for n in count.values());lo,hi=native.min(axis=(0,1)),native.max(axis=(0,1))
 oldg=old['meta']['georef'];oldbb=[oldg['bE']-834500,816500-oldg['bN'],oldg['bE']-834500+(old['w']-1)*oldg['aE'],816500-oldg['bN']-(old['h']-1)*oldg['aN']]
 save(DOC/'diagnostic.json',{'uids':[r['uid'] for r in sel['rows']],'sourceModelBounds':[r['native']['model']['worldBounds'] for r in sel['rows']],'expandedCells':cells,'expandedBounds':bb,'retainedBounds':oldbb,'retainedFacetCount':len(old['nativeMesh']['index'])//3,'originalTerrainFacetCount':len(native),'exactDuplicateFacetCount':duplicates,'exactUniqueOriginalTerrainFacets':len(count),'originalTerrainBounds':[lo.tolist(),hi.tolist()],'perSheet':records,'inputHashes':refs|{str((OLD/'selection.json.gz').relative_to(ROOT)):digest((OLD/'selection.json.gz').read_bytes()),str((OLD/'source-recovery.json').relative_to(ROOT)):digest((OLD/'source-recovery.json').read_bytes())},'runtimeBudgetRaised':False,'terrainGeometryChanges':0,'modelGeometryChanges':0,'physicalAccepted':False,'qualification':'Exact original triangle redundancy and scope diagnosis only. Vertex order canonicalized solely for equality census; no terrain/model surface modifications or runtime acceptance.'})
 print({'facets':len(native),'duplicates':duplicates,'unique':len(count),'expandedBounds':bb,'retainedBounds':oldbb},flush=True)
if __name__=='__main__':main()
