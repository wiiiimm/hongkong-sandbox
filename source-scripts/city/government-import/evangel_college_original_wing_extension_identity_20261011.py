"""Named original school-wing extension identity proposal; no physical credit.

Complete original surfaces remain in the target/foreign/cell tests. Only the
byte-bound western extension records receive a separately interpreted extent
role. No precise plan fit, architectural function, ownership or root follows.
"""
from datetime import datetime,timezone
import hashlib,json
import numpy as np
import shapely
from king_cheung_complete_ancillary_proposal_20261011 import polygon,spatial_metrics
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
UID='landsd/91306:0';CSUID='4507318353T20070410';MODEL='B450731835301063C0'
SOURCE_SHA='73dfaaf90f9dc8433f757ff796f90a0d8e3d02e2d48eb515f3286fa3eddc964b'
WORLD_SHA='6150374beebfd3c49c267d0c6d0a8ec2f8bf995c030c77bc5a4c5fba423154d2'
ROLE_IDS=[705, 706, 709, 710, 711, 1309, 1310, 1311, 1312, 1313, 1314, 1315, 1316, 1317, 1318, 1319, 1320, 1321, 1322, 1323, 1333, 1334, 1335, 1370, 1371, 1372, 1373, 1374, 1375, 1378, 1379, 1380, 1381, 1382, 1383, 1384, 1385, 1386, 1387, 1388, 1390, 1391, 1393, 1394, 1395, 1398, 1399, 1400, 1401, 1404, 1405, 1417, 1418, 1419, 1420, 1421, 1422, 1423, 1424, 1425, 1426, 1427, 1428, 1429, 1430, 2985, 2986, 2987, 2988, 2989, 2990, 2991, 2992, 2993, 2994, 3233, 3234, 3235, 3236, 3237, 9274, 9275, 9276, 9277, 9278, 9279, 9280, 9281, 9282, 9283, 9284, 9285, 9858, 9859, 9860, 9861, 9862, 9863, 9864, 9865, 9866, 9867, 9868, 9869, 11152, 11153, 11154, 11155, 11156, 11157, 11158, 11159, 11160, 11161, 11162, 11163, 11164, 11165, 11166, 11167, 11168, 11169, 11170, 11171, 11172, 11173, 11174, 11175, 11176, 11177, 11178, 11179, 11180, 11181, 11182, 11183]
RAW_REASONS=['fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent']
CONTEXT_SHA='9a39119f780c4b43a3b9602784c7406454a8af64fbac7fa1862cb081425a3f0e'
def canonical(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def proposal(previous,row,world,forms,provider,source_context):
 tri=np.asarray(world,dtype='<f8');assert tri.shape==(13960,3,3)and np.isfinite(tri).all()
 assert hashlib.sha256(tri.tobytes()).hexdigest()==WORLD_SHA==previous['worldTrianglesSHA256']
 assert row['uid']==previous['uid']==UID and row['modelId']==MODEL and row['triangles']==13960 and row['sourceSHA256']==previous['sourceSHA256']==SOURCE_SHA
 assert not previous['passed']and previous['reasons']==RAW_REASONS
 assert previous['originalOwnership']['sourceGraphVerified']and previous['originalOwnership']['originalRootName']==MODEL
 assert previous['exactWholeCellCoverage']['covered']and previous['exactWholeCellCoverage']['wholeOriginalFacesAccounted']==13960
 assert canonical(source_context)==CONTEXT_SHA
 topology=census(tri,list(range(len(tri))));assert topology==source_context['completeSourceTopology'];groups=topology['sharedEdgeConnectedComponents'];assert len(groups)==226
 assert len(ROLE_IDS)==136 and ROLE_IDS==sorted(set(ROLE_IDS))
 assert set(ROLE_IDS)==set(source_context['nominatedCompleteFaceIDs'])|{1311}
 assert 1311 in topology['exactNonrenderingOriginalFaces'] # Authored collapsed vertical segment, retained without support credit.
 selected=source_context['nominatedSourceDefinedPatches'];assert len(selected)==40
 mainrole=sorted(f for p in selected for f in p['completeOriginalPatchFaces']);assert len(mainrole)==65 and set(mainrole)<=set(groups[13])
 assert set(ROLE_IDS)-{1311}==set(mainrole+groups[20]+groups[142])
 for p in selected:assert np.array_equal(np.asarray(p['completeOriginalTriangles']),tri[p['completeOriginalPatchFaces']])
 mapping={f:i for i,ids in enumerate(groups)for f in ids};contacts=[]
 for saved in source_context['completeDetachedOriginalContexts']:
  component=saved['component'];assert component in [20,142]and saved['completeFaces']==groups[component]and np.array_equal(saved['completeOriginalTriangles'],tri[groups[component]])
  others=sorted(set(range(len(tri)))-set(groups[component]));assert saved['allOtherOriginalFacesExamined']==len(others)
  actual=exact_finite_contacts(tri,groups[component],tri,others,maximum_pairs=float('inf'))
  for c in actual['contacts']:c['otherRealComponent']=mapping.get(c['sourceFaceB'])
  assert actual==saved['completeFiniteContacts']
  positive=[c for c in actual['contacts']if c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2 and c['otherRealComponent']==13]
  assert len(positive)=={20:1,142:78}[component];contacts.append(saved)
 assert [p['component']for p in contacts]==[20,142]
 assert len({f['uid']for f in forms})==len(forms);own=[f for f in forms if f['uid']==UID];assert len(own)==1 and own[0]==row['source']['building']
 assert (own[0]['buildingCSUID'],own[0]['buildingId'],own[0]['structureType'],own[0]['name'])==(CSUID,1101781515,'Tower','EVANGEL COLLEGE')
 assert not provider.get('error')and not provider.get('exceededTransferLimit')and len(provider['features'])==1
 assert provider['spatialReference'].get('latestWkid',provider['spatialReference'].get('wkid'))==2326
 r=provider['features'][0];a=r['attributes'];assert(a['Status'],a['BuildingCSUID'],a['BuildingID'],a['BuildingBlockType'],str(a['GeoRefNo']))==('Active',CSUID,1101781515,'Tower','4507318353')
 assert datetime.fromtimestamp(a['DateCreate']/1000,timezone.utc).strftime('%Y%m%d')=='20070410'
 official=polygon([[(x-834500,816500-y)for x,y in ring]for ring in r['geometry']['rings']]);foreign=shapely.union_all([polygon(f['rings'])for f in forms if f['uid']!=UID])
 checks={name:spatial_metrics(tri,ROLE_IDS,target,foreign)for name,target in [('current',polygon(own[0]['rings'])),('primary',official)]}
 assert all(set(v['allFarVertexWitnessFaceIds'])<=set(ROLE_IDS)for v in checks.values())
 return dict(uids=[UID],originalModelId=MODEL,sourceSHA256=SOURCE_SHA,completeWorldSHA256=WORLD_SHA,completeSourceFaces=13960,namedOriginalWingExtensionFaceIDs=ROLE_IDS,ordinaryExtentFaceCount=13824,fullSourceSpatialChecks=checks,completeOriginalSourceContextSHA256=CONTEXT_SHA,sourceDefinedMainBodyPatchFaces=mainrole,completeDetachedExtensionInterfaces=contacts,zeroArea1311RetainedWithoutRootCredit=True,rawExtentReasonsRetained=previous['reasons'],completeWholeGeoRefCellProofRetained=previous['exactWholeCellCoverage'],allOtherForeignUIDs=sorted(f['uid']for f in forms if f['uid']!=UID),proposedRole='named unchanged original Evangel College low western wing extension; architectural interpretation only',ownerCampusCorroborationIsNotPreciseRegistration=True,architecturalFunctionAccepted=False,propertyOwnershipAccepted=False,structuralRootOrBridgeCredit=False,physicalSupportExemption=False,runtimeExemption=False,currentActorRemoval=False,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,sourceOnly=True,identityAccepted=False,currentAcceptance=False,physicalAccepted=False,installationApproved=False,proposalSpatialGuardsSatisfied=all(v['ordinarySpatialGuardsOnCompleteProjectionAndRemainingFaces']for v in checks.values()))
