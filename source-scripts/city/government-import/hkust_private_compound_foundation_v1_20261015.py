"""Diagnose both complete original sources and all saved tower rims against private ground/podium."""
from pathlib import Path
import numpy as np,shapely,uuid
from run import ROOT,HERE,read,save,digest,reservations
from primrose_compound_foundation_v2_20261015 import module
B=ROOT/'docs/astra-city/government-import';OLD=B/'government-xl-hkust-private-runtime-capture-v1-20261015';PACKET=B/'government-xl-hkust309822-232155-target-provenance-draft-v1-20261014';DOC=B/'government-xl-hkust-private-compound-foundation-v1-20261015'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not DOC.exists();r=read(OLD/'result.json');pins={x['path']:x['sha256'] for x in r['evidenceRefs']};gp=OLD/'ground.json.gz';assert ref(gp)['sha256']==pins[str(gp.relative_to(ROOT))];g=read(gp)
 for p,h in g['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p
 reportp=PACKET/'two-original-scope-interface-output-v1/result.json';report=read(reportp);triangles={};paths=[Path(__file__),OLD/'result.json',gp,reportp,HERE/'xl-final-script-pass.py'];forms={x['uid']:x for x in report['currentAllSixFormsVerbatim']}
 for a in report['arrayRefs']:
  p=ROOT/a['path'];assert ref(p)==a;arr=read(p);uid=arr['sourceTuple']['uid'];asset=ROOT/arr['sourceTuple']['originalAssetPath'];assert ref(asset)['sha256']==arr['sourceTuple']['sourceSHA256'];triangles[uid]=np.array(arr['completeOrderedOriginalTriangles']);paths.extend([p,asset])
 claim=reservations.claim('hkust-compound-'+str(uuid.uuid4()),['private-compound:'+DOC.name],batch=DOC.name,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();f=module('hkust_compound_existing_contract',HERE/'xl-final-script-pass.py');ground=np.array(g['completeRegionalGroundWorlds']['actualLiteral']).reshape(-1,3,3);tower='landsd/309822:0';podium='landsd/232155:0';compound=np.concatenate([ground,triangles[podium]]);rows=[]
  for uid,support in [(tower,compound),(podium,ground)]:
   foundation=f.foundation_context(triangles[uid],support,f.form_polygon(forms[uid]));rows.append({'uid':uid,'foundation':foundation,'strictFoundationDiagnosticPassed':foundation['completeTerrainTriangles']==foundation['triangles'] and not foundation['fullyBuriedUpwardTriangles'] and foundation['fullyBuriedAreaFraction']==0});assert reservations.heartbeat(lease,ttl=3600)['ok']
  samples=g['originalRimGroundSamples'];points=np.array([x['position'] for x in samples]);polys=shapely.polygons(triangles[podium][:,:,[0,2]]);valid=shapely.area(polys)>1e-10;podiumheights=f.s.context.shared.samples(points[:,[0,2]],triangles[podium][valid],shapely.STRtree(polys[valid]));contacts=[]
  for old,h in zip(samples,podiumheights):
   terrain=old['currentTerrainHeight'];pod=float(h) if np.isfinite(h) else None;highest=max(terrain,pod) if pod is not None else terrain;gap=old['position'][1]-highest;contacts.append({**old,'originalPodiumHeight':pod,'combinedHighestSupportHeight':highest,'combinedGapM':gap,'withinExistingPointOneM':abs(gap)<=.1,'classification':'support-above-rim' if gap<-.1 else 'rim-above-support' if gap>.1 else 'strict-point-contact'})
  counts={k:sum(x['classification']==k for x in contacts) for k in ['support-above-rim','rim-above-support','strict-point-contact']};save(DOC/'compound.json.gz',{'rows':rows,'towerSamples':contacts,'contactCounts':counts,'qualification':'Provider-original sources against actual private literal ground. Not a four-world model placement proof, original strict interface override, or installation acceptance.'});out={'uids':[tower,podium],'foundationRows':rows,'towerContactCounts':counts,'fullAcceptance':False,'privateTerrainGeometryChanged':True,'liveTerrainGeometryChanged':False,'sourceBuildingGeometryChanged':False};save(DOC/'summary.json',out)
  module('hkust_compound_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(DOC.name,'hkust-complete-original-private-compound-foundation-v1',paths,{**out,'nextStep':'Use complete failure accounts to target exact lower facade/source support interpretation. Do not waive strict contact or claim installation; source identity and affected neighbours remain independent.'});print({'foundations':[{k:v for k,v in x.items() if k!='foundation'} for x in rows],'contacts':counts},flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
