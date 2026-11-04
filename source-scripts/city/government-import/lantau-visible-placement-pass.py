"""Place two unchanged government meshes above the conflicting rendered terrain by node translation only."""
import copy,gzip,hashlib,json,struct,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SOURCE=HERE/'accepted/government-lantau-height-align-20260921';STAGE=HERE/'local/government-lantau-visible-placement-20260921';DOC=ROOT/'docs/astra-city/government-import/government-lantau-visible-placement-20260921'
EXTRA={'landsd/112959:0':1.0,'landsd/182471:0':2.5}
def read(p):
 b=Path(p).read_bytes();return json.loads(gzip.decompress(b) if str(p).endswith('.gz') else b)
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def sha(b):return hashlib.sha256(b).hexdigest()
def pack(g,binary):
 j=json.dumps(g,separators=(',',':')).encode();j+=b' '*(-len(j)%4);binary+=b'\0'*(-len(binary)%4)
 return b'glTF'+struct.pack('<II',2,12+8+len(j)+8+len(binary))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(binary),0x004e4942)+binary
def main():
 source=read(SOURCE/'catalogue.json');models=[];rows=[];proof=[];forms=[]
 selection=read(DOC.parent/'government-lantau-height-align-20260921/selection.json.gz');by_uid={r['uid']:r for r in selection['rows']}
 for uid,extra in EXTRA.items():
  old=next(m for m in source['models'] if m['uid']==uid);entry=copy.deepcopy(old);row=copy.deepcopy(by_uid[uid]);original=(SOURCE/old['asset']).read_bytes();assert sha(original)==old['sha256'];raw=gzip.decompress(original)
  n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);bo=20+n;bn=struct.unpack_from('<I',raw,bo)[0];binary=raw[bo+8:bo+8+bn]
  assert g['nodes'][0]['matrix'][13]==old['sourceWorldBounds'][0][1]
  total=old['verticalPlacementOffsetHKPD']+extra;g['nodes'][0]['matrix'][13]+=total
  packed=gzip.compress(pack(g,binary),mtime=0);digest=sha(packed);asset='assets/'+digest+'.glb.gz';p=STAGE/asset;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(packed)
  shifted=[[point[0],point[1]+extra,point[2]] for point in old['worldBounds']]
  for key in ('sourceWorldBounds','verticalPlacementOffsetHKPD','verticalPlacementBasis'):entry.pop(key,None)
  entry.update(asset=asset,sha256=digest,bytes=len(packed),glbBytes=len(gzip.decompress(packed)),worldBounds=shifted,
   sourceOriginalSHA256=old['sha256'],sourceNodeVerticalShiftHKPD=total,terrainClearanceAdditionalShiftHKPD=extra,
   placementReview=f'Original government vertex, index, normal, colour and material buffers retained byte-for-byte. Source node translated +{total:.4f}m in Y, including +{extra:.1f}m beyond recorded-top alignment, to keep the roof visible above the existing regional terrain. No terrain or neighbouring asset changed.',
   publicationApproved=False,retainsBasicForm=True,proceduralWindows=False)
  row['candidate']['entry']=entry;row['candidate']['path']=str(p);rows.append(row);models.append(entry);forms.append(row['source']['building'])
  proof.append({'uid':uid,'originalSourceSHA256':old['sha256'],'placedSHA256':digest,'meshBinarySHA256':sha(binary),'sourceVertexAndTriangleBuffersUnchanged':True,'nodeTranslationHKPD':total,'additionalRenderedTerrainShiftHKPD':extra,'recordedTopHeightHKPD':entry['recordedTopHeight'],'placedTopHeightHKPD':shifted[1][1],'sourceGeometryGenerated':False,'aiModellingCalls':0})
 catalogue=copy.deepcopy(source);catalogue.update(area='Lantau source meshes visible above conflicting regional terrain',coordinatePolicy='Original source mesh buffers unchanged; source node translations resolve local regional-terrain occlusion, with explicit survey-height discrepancy',counts={'packedModels':2},models=models)
 save(STAGE/'catalogue.json',catalogue);save(STAGE/'catalogue-index.json',{'models':2,'catalogues':['catalogue.json']});save(STAGE/'source-forms.json',forms)
 DOC.mkdir(parents=True,exist_ok=True);(DOC/'selection.json.gz').write_bytes(gzip.compress((json.dumps({'batch':'government-lantau-visible-placement-20260921','rows':rows,'manifestSHA256':sha((ROOT/'3d-viewer/city/data/manifest.json').read_bytes()),'aiCalls':0})+'\n').encode(),mtime=0))
 save(DOC/'source-forms.json',{r['uid']:r['source'] for r in rows});save(DOC/'terrain-candidates.json',[]);save(DOC/'placement-proof.json',{'policy':'source-node-translation-for-visible-terrain-placement-v1','rows':proof,'aiCalls':0,'modelGeometryChanges':0,'terrainChanges':0})
 print(json.dumps({'models':[{'uid':m['uid'],'top':m['worldBounds'][1][1],'additionalShift':m['terrainClearanceAdditionalShiftHKPD']} for m in models]}))
if __name__=='__main__':main()
