"""Bind overlapping candidate triangles to exactly equal packed original source triangles."""
from pathlib import Path
from collections import defaultdict
import numpy as np
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
B=ROOT/'docs/astra-city/government-import';OLD=B/'government-xl-hkust-private-overlap-inventory-v1-20261015';G=B/'government-xl-hkust-adjoining-native-terrain-v1-20261015';DOC=B/'government-xl-hkust-overlap-exact-source-binding-v1-20261015'
def key(t):return tuple(sorted(tuple(float(x) for x in p) for p in t))
def main():
 assert not DOC.exists();r=read(OLD/'result.json');op=OLD/'overlaps.json.gz';assert digest(op.read_bytes())==next(x['sha256'] for x in r['evidenceRefs'] if x['path']==str(op.relative_to(ROOT)));gr=read(G/'result.json');gp=G/'native-ground.json.gz';assert digest(gp.read_bytes())==next(x['sha256'] for x in gr['evidenceRefs'] if x['path']==str(gp.relative_to(ROOT)));ground=np.array(read(gp)['completeOriginalTerrainTriangles'],dtype=np.float32).astype(float);lookup=defaultdict(list)
 for i,t in enumerate(ground):lookup[key(t)].append(i)
 data=read(op);rows=[]
 for row in data['rows']:
  a=lookup.get(key(row['faceVerticesA']),[]);b=lookup.get(key(row['faceVerticesB']),[]);rows.append({**row,'exactPackedSourceFacesA':a,'exactPackedSourceFacesB':b,'bothFacesExactlyOriginalPacked':bool(a and b)})
 summary={'uids':r['uids'],'pairs':len(rows),'exactOriginalPairCount':sum(x['bothFacesExactlyOriginalPacked'] for x in rows),'otherPairCount':sum(not x['bothFacesExactlyOriginalPacked'] for x in rows),'exactOriginalPairAreaSumM2':sum(x['areaM2'] for x in rows if x['bothFacesExactlyOriginalPacked']),'otherPairAreaSumM2':sum(x['areaM2'] for x in rows if not x['bothFacesExactlyOriginalPacked']),'qualification':'Exact numeric Float32 vertices, vertex order independent. No proximity tolerance. Other pairs may be clipped originals or transition/fill; no approval or geometry edit.'};DOC.mkdir();save(DOC/'bindings.json.gz',{'summary':summary,'rows':rows});save(DOC/'summary.json',summary)
 module('hkust_overlap_binding_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(DOC.name,'hkust-overlap-exact-packed-source-binding-v1',[Path(__file__),OLD/'result.json',op,G/'result.json',gp],{**summary,'nextStep':'Only unbound pairs need ancestor/transition attribution; bound pairs are demonstrated original packed overlaps, but all runtime MAX and neighbour gates remain.'});print(summary,flush=True)
if __name__=='__main__':main()
