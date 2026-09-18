"""Stage a standalone regional hydro payload using the shared terrain-cut builder."""
import hashlib,json,pathlib,sys
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];DOC=ROOT/'docs/astra-city/mui-wo-completion'
sys.path.insert(0,str(HERE.parent/'tai-o-completion'));from hydro_terrain import prepare_terrain

def main():
 base=json.loads((ROOT/'3d-viewer/city/data/terrain.json').read_text());manifest=json.loads((ROOT/'3d-viewer/city/data/manifest.json').read_text())
 paths=[HERE/'staged-terrain-mui-wo.json' if p['url'].endswith('terrain-mui-wo.json') else ROOT/'3d-viewer'/p['url'] for p in manifest['terrainPatches']];patches=[json.loads(p.read_text()) for p in paths]
 hydro=json.loads((HERE/'hydro-mui-wo.json').read_text());out=prepare_terrain(hydro,base,patches);target=HERE/'hydro-mui-wo-terrain.json';raw=(json.dumps(out,separators=(',',':'))+'\n').encode();target.write_bytes(raw)
 report={'published':False,'terrainSourceSha256':hashlib.sha256(paths[0].read_bytes()).hexdigest(),'rawTerrainArraysChanged':False,'sourceBuildingsChanged':False,'waterPolygons':len(out['water']),'terrainCuts':[{'resolution':p['georef']['aE'],'removedCells':len(p['cells']),'replacementLandTriangles':sum(len(c['land'])//9 for c in p['cells']),'removedAreaM2':p['removedAreaM2']} for p in out['terrainCuts']],'bedTriangles':len(out['bedTriangles'])//9,'bankTriangles':len(out['bankTriangles'])//9,'outputBytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
 (DOC/'hydro-terrain-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
