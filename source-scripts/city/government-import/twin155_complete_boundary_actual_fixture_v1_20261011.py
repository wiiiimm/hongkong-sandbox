"""Bound immutable actual full-source fixtures for the Twin155 proposal only."""
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
import twin155_named_complete_boundary_visual_assembly_proposal_v1_20261011 as k
BASE=ROOT/'docs/astra-city/government-import'
DOCS={
 'graph':BASE/'xl-terrain-recovery-20261011-twin-regency-tower2-podium-original-contact-census-v2',
 'bands':BASE/'xl-terrain-recovery-20261011-twin-regency293-four-stream-qualified-host-association-v1',
 'finite':BASE/'xl-terrain-recovery-20261011-twin-regency-pair-current-four-stream-finite-grade-v1',
 'attributes':BASE/'xl-terrain-recovery-20261011-twin-regency-two-current-render-attribute-capture-v1',
 'paths':BASE/'xl-terrain-recovery-20261011-twin-regency-bounded-four-stream-current-podium-paths-v1'}
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def actual_fixture():
 docs={};refs=[];receipts={}
 for name,folder in DOCS.items():
  r=read(folder/'result.json');receipts[name]=r;refs.append(ref(folder/'result.json'));p=folder/('actual-render-attributes.json.gz'if name=='attributes'else'diagnostic.json.gz');assert ref(p)in r['evidenceRefs'];docs[name]=read(p);refs.append(ref(p))
 original=[];attrs=docs['attributes']['rows'];uids=['landsd/222465:0','landsd/223206:0'];assert [a['uid']for a in attrs]==uids
 for s,a,count in zip(docs['graph']['completeSourceInputs'],attrs,[13063,456]):
  asset=ROOT/s['asset']['path'];assert ref(asset)==s['asset']and s['asset']['sha256']==a['sourceSHA256']==k.SOURCE_SHA[a['uid']];refs.append(ref(asset));tri=decode_original_world_triangles(asset.read_bytes());assert len(tri)==count;original.append(tri)
 worlds={'providerOriginal':np.concatenate(original)}
 for mode,field in [('capturedLiteral','completeLiteralWorldPosition'),('explicitLeftAssociatedF32ModelMatrix','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32ModelMatrix','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]=np.concatenate([np.asarray(a[field],float).reshape(-1,3)[np.asarray(a['completeOriginalIndex'],np.uint32).reshape(-1,3)]for a in attrs])
 common=set.intersection(*[set(r['qualifiedDiagnosticBodyIDs'])for r in docs['paths']['rows']]);assert len(common)==827
 packages={}
 for part,faces in k.NAMED_SOURCE_PART_FACES.items():
  body=docs['graph']['bodies'][part];assert body['globalOriginalFaces']==faces;uid=body['actorUID'];offset=0 if uid==uids[0]else 13063;contexts={};hosts={}
  for mode in k.MODES:
   row=next(r for r in docs['bands']['rows']if r['mode']==mode);a=next(r for r in row['all293OriginalBodyAssociations']if r['originalBody']==part);f=next(r for r in docs['finite']['rows']if r['mode']==mode and r['uid']==uid);p=next(r for r in docs['paths']['rows']if r['mode']==mode)
   assert k.world_sha(worlds[mode])==row['completeWorldSHA256']==p['completeWorldSHA256'];assert k.world_sha(worlds[mode][:13063]if offset==0 else worlds[mode][13063:])==f['completeWorldSHA256']
   hs=sorted(z for i in common if docs['graph']['bodies'][i]['actorUID']==uid for group in p['completeActualCensusForEveryOriginalBody'][i]['completeActualEdgeCensus']['sharedEdgeConnectedComponents']for z in group);assert hs==a['completeHostSelection']['completeQualifiedSameActorHostFaces']
   finitefaces=[]
   for globalface in faces:
    i=globalface-offset;proof=f['allFaces'][i];ctx=f['completeAllOriginalFacetContexts'][i]
    assert proof['sourceFace']==ctx['sourceFace']==i and ctx['sourceFaceSHA256']==k.world_sha(worlds[mode][globalface])
    finitefaces.append(dict(sourceFace=i,completeActualFacetSHA256=ctx['sourceFaceSHA256'],completeCapturedGroundSHA256=f['completeActualDrawnGroundSHA256'],closedProjectionCovered=ctx['groundProjectionCovered'],existingOrdinaryClearanceBoundProved=proof['completeOriginalBoundProved'],strictlyExposedWholeFacet=ctx['groundProjectionCovered']is True and F(ctx['exactCertifiedLowerClearanceM'])>0,completeFiniteProofSHA256=k.canonical(proof),completeFiniteContextSHA256=k.canonical(ctx)))
   contexts[mode]=dict(completeOwnedWorldSHA256=row['completeWorldSHA256'],association=a,allCompletePartFiniteFaces=finitefaces);hosts[mode]=hs
  packages[part]=dict(part=part,uid=uid,source_sha=k.SOURCE_SHA[uid],worlds=worlds,contexts=contexts,qualified_hosts=hosts,expected_binding=k.binding(part,uid,k.SOURCE_SHA[uid],worlds,contexts,hosts))
 assert len(packages)==155;assert all(ref(ROOT/r['path'])==r for r in refs)
 return docs,packages,refs,receipts
