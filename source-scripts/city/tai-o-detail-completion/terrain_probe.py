"""Diagnose the existing live-terrain conflicts against retained adjacent source TINs."""
import json,sys
import numpy as np
from shapely.geometry import Point
from audit import HERE,ROOT,DOC,dump
sys.path.insert(0,str(ROOT/'docs/astra-city/mui-wo-buildings/review'))
from resample_model_terrain import terrain_index

def main():
 catalogue=json.loads((HERE/'compact/catalogue.json').read_text());runtime=json.loads((DOC/'runtime-verification.json').read_text());byuid={r['uid']:r for r in runtime['results']};indexes={};rows=[]
 for e in catalogue['models']:
  tile=e['sourceTile']
  if tile not in indexes:indexes[tile]=terrain_index(HERE/'staged'/tile)
  _,_,_,_,triangles,tree=indexes[tile];ledger=next(r for r in json.loads((DOC/'audit.json').read_text())['rows'] if r['uid']==e['uid']);point=np.array(ledger['centre']);values=[]
  for i in tree.query(Point(point),predicate='covered_by'):
   tri=triangles[i];bary=np.linalg.solve((tri[1:,:][:,[0,2]]-tri[0,[0,2]]).T,point-tri[0,[0,2]]);values.append(float(tri[0,1]+bary[0]*(tri[1,1]-tri[0,1])+bary[1]*(tri[2,1]-tri[0,1])))
  height=max(values) if values else None
  rows.append({'uid':e['uid'],'sourceTile':tile,'samplePoint':point.tolist(),'ownTINHeightHKPD':height,'liveTerrainHeightHKPD':byuid[e['uid']]['terrainAtFootprintCentre'],'modelBaseHKPD':e['worldBounds'][0][1],'modelRoofHKPD':e['worldBounds'][1][1],'roofBelowOwnTIN':height is not None and e['worldBounds'][1][1]<height,'liveRoofOccludedAtCentre':byuid[e['uid']]['roofBelowCentreTerrain']})
 dump(DOC/'source-terrain-probes.json',{'method':'Exact source TIN barycentric height at retained footprint centre, no extrapolation. Maximum if multiple source triangles cover point.','rows':rows,'limits':['Diagnostic only; no live terrain changes or replacement height adjustment.','Centre sample alone does not establish whole-footprint or foundation placement.']});print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
