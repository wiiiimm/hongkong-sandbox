"""Bound a primary-photo roof-branding proposal; no mounting or acceptance.

The owner's photo corroborates roof branding, not source mesh attachment or
unmodelled fixings. Only the six original glyph/logo components are proposed;
the fragment and projecting unit remain unresolved. Historical source/literal
topology is accounted completely, without current physical or F32 credit.
"""
import importlib.util
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census

BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-citic-primary-roof-branding-source-proposal-v1-20261011'
DOC=BASE/BATCH
PHOTO=BASE/'government-xl-citic-primary-signage-context-v1-20261011'
GRAPH=BASE/'xl-terrain-recovery-20261010-citic-current-original-complete-support-v1'
PROBE=BASE/'government-xl-terrain-recovery-citic-complete-original-current-probe-v1-20261010'
UNION=BASE/'government-xl-citic-eight-details-complete-orthogonal-host-union-diagnostic-v1-20261011'
ORDER=[(34,'logo'),(29,'C'),(39,'I'),(36,'T'),(35,'I'),(33,'C')]
ALL=[29,33,34,35,36,39,40,70]

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))

def main():
 assert not DOC.exists()
 g=read(GRAPH/'diagnostic.json.gz');selection=read(PROBE/'selection.json.gz')
 assets=[ROOT/next(r for r in selection['rows']if r['uid']==a['uid'])['candidate']['path']for a in g['actors']]
 for a,p in zip(g['actors'],assets):assert digest(p.read_bytes())==a['sourceSHA256']
 original=np.concatenate([decode_original_world_triangles(p.read_bytes())for p in assets])
 assert original.shape==(14036,3,3) and digest(original.tobytes())==g['binding']['completeOriginalWorldTrianglesSHA256']
 runtimepath=HERE/'local'/PROBE.name/'runtime-geometry.json.gz';runtime=read(runtimepath)
 literal=np.concatenate([np.asarray(next(r for r in runtime['rows']if r['uid']==a['uid'])['position'],float).reshape(-1,3)[np.asarray(next(r for r in runtime['rows']if r['uid']==a['uid'])['index'],np.uint32).reshape(-1,3)]for a in g['actors']])
 assert literal.shape==original.shape and np.isfinite(original).all() and np.isfinite(literal).all()
 for folder in [GRAPH,PROBE,UNION]:
  receipt=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY')
   assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 source=read(PHOTO/'source.json');assert source['sourcePage']=='https://www.citicpacific.com/en/property_projects/citic-tower/'
 assert ref(ROOT/source['photo']['path'])==source['photo']
 proposed=[]
 for k,label in ORDER:
  c=g['components'][k];assert c['actorUID']=='landsd/278303:0'
  t=original[c['globalOriginalFaces']]
  proposed.append(dict(component=k,observedGlyphOrLogo=label,completeFaces=c['globalOriginalFaces'],completeWorldTrianglesSHA256=digest(t.tobytes()),completeBounds=[t.min((0,1)).tolist(),t.max((0,1)).tolist()],role='proposed-provider-authored-roof-branding-render-representation',roleAccepted=False,physicalAttachmentCertified=False,structuralRootCredit=False,structuralBridgeCredit=False))
 assert [p['component']for p in sorted(proposed,key=lambda p:p['completeBounds'][0][0])]==[k for k,_ in ORDER]
 assert sum(len(p['completeFaces'])for p in proposed)==1695
 topology=[]
 for mode,tri in [('untouched-provider-original',original),('historical-production-literal',literal)]:
  for k in ALL:topology.append(dict(mode=mode,component=k,completeCensus=census(tri,g['components'][k]['globalOriginalFaces'])))
 refs=[ref(p)for p in [Path(__file__),*assets,runtimepath,GRAPH/'diagnostic.json.gz',GRAPH/'result.json',PROBE/'selection.json.gz',PROBE/'result.json',UNION/'diagnostic.json.gz',UNION/'result.json',PHOTO/'source.json',ROOT/source['photo']['path'],BASE/'xl-terrain-recovery-20261010-citic-eight-original-detail-visual-v1/original-eight-details-1800x1440.png',HERE/'exact_original_shared_edge_component_census_v2_20261011.py',HERE/'exact_packed_world_geometry_20261009.py']]
 result=dict(proposedSourceRoles=proposed,completeEightSourceAndLiteralTopology=topology,primaryPhoto=source,sourceOnlyHistoricalProposal=True,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,allMeasuredAirGapsAndMountingFailuresPreserved=True,sourceGeometryChanges=0,unresolvedComponents=[40,70],nativeReacceptance=False,visualRoleAccepted=False,installationApproved=False,evidenceRefs=refs,qualification='Root inspected the original owner photo and prior original component render. Roof logo/CITIC word placement/order supports a narrow branding interpretation only. It supplies no physical attachment, unmodelled fixings, current grounding, source/F32/native/runtime acceptance or generic free-floating equipment exception. The one-face fragment and projecting box have no role from this photo. Further current complete physical/source checks and independent bounded role review remain mandatory.')
 save(DOC/'proposal.json.gz',result)
 spec=importlib.util.spec_from_file_location('citic_branding_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 r=m.freeze(BATCH,'primary-source-six-roof-branding-proposal-v1',[ROOT/r['path']for r in refs]+[DOC/'proposal.json.gz'],dict(uids=[a['uid']for a in g['actors']],sourceOnlyHistoricalProposal=True,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,proposedOriginalBrandingComponents=[k for k,_ in ORDER],unresolvedComponents=[40,70],sourceGeometryChanges=0,visualRoleAccepted=False,installationApproved=False,qualification=result['qualification']))
 print(dict(jobId=r['jobId'],sourceOnlyProposal=True,unresolved=[40,70]),flush=True)

if __name__=='__main__':main()
