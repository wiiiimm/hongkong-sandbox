"""Reconcile a bounded existing-source batch after visual inspection; no publication."""
import json,hashlib,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[3];D=ROOT/'docs/astra-city/landmark-completion-audit';S=pathlib.Path(__file__).parent
read=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def main():
 batch=read(D/'lantau24-batch.json');parts={p['uid']:p for p in batch['parts']};browser=D/'lantau24-browser/report.json';b=read(browser);assert not b['errors'];assert len(b['views'])==96
 for v in b['views']:
  assert sha(browser.parent/v['file'])==v['sha256'];assert not v['cameraCollision'] and not v['uiOverflow'] and v['boxInsideView'];assert v['activeUIDs']==v['uids'];assert all(p['uid']==p['hitUid'] for p in v['picking']);assert all(p['hits'] and any(abs(h-p['sampler'])<.003 for h in p['hits']) for p in v['terrainProbes'])
 for uid in parts:assert {(v['mobile'],v['time']) for v in b['views'] if uid in v['uids']}=={(False,15),(False,22),(True,15),(True,22)}
 support={r['uid']:r for r in read(D/'lantau24-support.json')['rows']};surfaces={r['uid']:r['stats']['patched'] for r in read(D/'lantau24-surfaces.json')['rows']};native={r['uid']:r for r in read(D/'lantau24-native-burial.json')['rows']};proof=read(D/'lantau24-identity-proofs.json');assert set(proof['parts'])==set(parts)
 evidence=[browser,D/'lantau24-support.json',D/'lantau24-surfaces.json',D/'lantau24-native-burial.json',D/'lantau24-identity-proofs.json'];hashes={str(p.relative_to(ROOT)):sha(p) for p in evidence};rows=[]
 for uid,p in parts.items():
  assert p['asset']['sha256']==sha(ROOT/p['asset']['path'])==support[uid]['sha256'];s=surfaces[uid];rim=support[uid]['rimCounts'];assert rim['noContact']==0 and rim['otherTriangleContact']==0
  note=f"Exact existing government native form and source identity retained. All {rim['samples']} low-rim points have current terrain contact or below-grade foundation context; no external support dependency. "
  if s['whollyBuriedTriangles']:
   n=native[uid];assert n['nativeStillWhollyBuriedTriangles']==s['whollyBuriedTriangles'] and not n['nativeUncoveredVertices'] and not s['upwardWhollyBuriedTriangles'];note+=f"One buried side/foundation triangle ({s['hiddenArea']:.5f} square metres, {s['hiddenAreaPercent']:.5f}% of surface) is also buried in original government TIN; preserve native foundation geometry. "
  else:note+='No wholly buried source triangle. '
  if uid=='landsd/58870:0':note+='The one low-rim point 2.149m below terrain does not wholly bury any native face; verify the visible lower facade in its hillside context, without raising source geometry. '
  note+='Actual desktop/mobile day/night scene views, picking, framing and terrain-mesh correspondence checked. Simplified source architecture, not a textured or whole-landmark completion claim.'
  rows.append({'uid':uid,'name':p['name'],'status':'installed-verified','sourceSHA256':p['asset']['sha256'],'modelId':p['asset']['modelId'],'observation':note,'wholeLandmarkComplete':False,'rimCounts':rim,'surface':{k:v for k,v in s.items() if k!='buriedTriangleEvidence'},'evidenceHashes':hashes})
 save(D/'lantau24-decisions.json',{'issue':'HKS-214','reviewSnapshot':batch['reviewSnapshot'],'existingNativeParts':24,'newModelsAdded':0,'installedVerified':24,'verticalScale':1,'sourceGeometryChanged':False,'metadataChanged':False,'rows':rows,'visualInspection':'All96 actual day/night desktop/emulated-mobile captures inspected through contact sheets and individual close-ups. Native source roof outlines and exposed facades remain visible; three small below-grade side faces are retained.','limits':['Source native blocks do not include all architectural ornament or surveyed textures.','No whole Ngong Ping, Po Lin or Lantau completion asserted.','Real-device Safari and sustained mobile performance remain outside this bounded source review.']});print('24 existing source reviews reconciled; zero new assets or source edits')
if __name__=='__main__':main()
