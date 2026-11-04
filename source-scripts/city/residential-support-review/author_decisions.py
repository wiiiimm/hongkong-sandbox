"""Bind explicitly written per-part observations to exported evidence; preserve holds."""
import pathlib,json,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/residential-support-review'
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 observations=read(HERE/'visual-observations.json');framing=read(DOC/'bulk-framing/report.json');assert not framing['errors'];support={r['uid']:r for r in read(DOC/'decisions.json')['rows']};coverage={r['uid']:r for r in read(DOC/'coverage.json')['rows']};frames={r['uid']:r for r in framing['rows']};assert set(frames)==set(observations['observations'])
 accepted={u for u,r in frames.items()if support[u]['placementApproved'] and coverage[u]['reviewFlag']=='projection-screen-clear' and len(r['views'])==2 and all(v['active'] and v['nativeGeometryUnchanged'] and v['final']['clear'] and v['final']['fullyFramed']for v in r['views'])}
 initial=set(accepted)
 while True:
  remove={u for u in accepted if any(d['state']=='candidate' and d['uid']not in accepted for d in support[u]['supportDependencies'])}
  if not remove:break
  accepted-=remove
 rows=[]
 for uid,r in frames.items():
  status='approved-native-source-component'if uid in accepted else 'held-native-support-dependency'if uid in initial else 'held-full-scene-inspection'
  rows.append({'uid':uid,'status':status,'observation':observations['observations'][uid],'wholeLandmarkComplete':False,'sourceIdentityApproved':True,'landmarkMembershipApproved':support[uid]['landmarkMembershipApproved'],'supportDependencies':support[uid]['supportDependencies'],'framing':{v['mode']:v['final']for v in r['views']},'images':[{'path':str((DOC/'bulk-framing'/v['file']).relative_to(ROOT)),'sha256':sha(DOC/'bulk-framing'/v['file'])}for v in r['views']]})
 inputs=[DOC/'combined-support.json.gz',DOC/'decisions.json',DOC/'coverage.json',DOC/'bulk-framing/report.json',HERE/'review-candidates/catalogue.json',HERE/'roof-review-54170-0.json',HERE/'visual-observations.json',DOC/'verification.json',DOC/'omitted-support/verification.json']
 review={'issue':'HKS-214','status':'approved-native-source-components','verticalScale':1,'scope':observations['scope'],'approvedCount':len(accepted),'heldCount':len(rows)-len(accepted),'runtimePublicationApproved':False,'inputHashes':{str(p.relative_to(ROOT)):sha(p)for p in inputs},'rows':rows,'nextGate':'Root integrates the approved dependency closure and verifies the installed scene, native support streaming, picking and collision. This review does not complete landmarks or regions.'}
 for p in [HERE/'visual-acceptance.json',DOC/'visual-acceptance.json']:p.write_text(json.dumps(review,indent=2)+'\n')
 print(json.dumps({'approved':len(accepted),'held':len(rows)-len(accepted),'holds':[(r['uid'],r['status'])for r in rows if r['uid']not in accepted]}))
if __name__=='__main__':main()
