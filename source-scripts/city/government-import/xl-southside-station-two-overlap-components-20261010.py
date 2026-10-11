"""Complete authored components at the named mall-station source interface."""
import collections,numpy as np
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from source_closed_components import components
from exact_original_component_contacts_20261009 import exact_component_contacts
DOC=ROOT/'docs/astra-city/government-import/government-xl-southside-station-two-overlap-components-20261010'
PRIOR=DOC.parent/'government-xl-southside-station-original-relationship-20261010'
def main():
 assert not DOC.exists();d=read(PRIOR/'diagnostic.json.gz');paths=[next(ROOT/k for k,v in d['inputHashes'].items() if k.endswith('.glb.gz') and v==n['model']['asset']['sha256']) for n in d['native']];t,p=[decode_original_world_triangles(q.read_bytes()) for q in paths];parts=components(t)['components'];assert len(parts)==157
 contacts=read(PRIOR/'complete-original-contacts.json.gz');records=[]
 for ci in [0,121]:
  c=parts[ci];ids=c['faceIndices'];station=[q for q in contacts['contacts'] if q['sourceFaceA'] in ids];own=exact_component_contacts(t,ids,t,parts[0]['faceIndices'],maximum_pairs=1000000) if ci!=0 else None
  records.append({'originalComponent':ci,'completeOriginalFaceIds':ids,'completeOriginalFaces':t[ids].tolist(),'completeSourceTopology':c,'allOverlapFacesInComponent':[i for i in d['allOverlapOriginalFaceIds'] if i in ids],'allExactStationInterfaces':station,'positiveDimensionalStationInterfaces':sum(q['dimension']>0 for q in station),'allExactMainbodyInterfaces':own,'physicalSupportAccepted':False})
 save(DOC/'diagnostic.json.gz',{'uid':d['uids'][0],'explicitRelatedUID':d['uids'][1],'wholeOriginalWorldSHA256s':d['wholeOriginalWorldSHA256s'],'completeOriginalSourceFaceCounts':[len(t),len(p)],'all157OriginalMallComponentsRetained':True,'all34RawOverlapFacesRetained':d['allOverlapOriginalFaceIds'],'rawCurrentRelatedExcessM2':d['towerExcessIntoNamedPodiumM2'],'rows':records,'inputHashes':d['inputHashes']|{str((PRIOR/'diagnostic.json.gz').relative_to(ROOT)):digest((PRIOR/'diagnostic.json.gz').read_bytes()),str((PRIOR/'complete-original-contacts.json.gz').relative_to(ROOT)):digest((PRIOR/'complete-original-contacts.json.gz').read_bytes())},'primaryRelationshipInterpretation':'Two unchanged named source envelopes at the independently documented direct mall/station connection. This does not claim every source face is L1, legal ownership, common OP, surveyed placement or physical support.','identityAccepted':False,'physicalAccepted':False,'sourceGeometryChanges':0})
 print([{'component':r['originalComponent'],'faces':len(r['completeOriginalFaceIds']),'rawOverlapFaces':len(r['allOverlapFacesInComponent']),'positiveStationContacts':r['positiveDimensionalStationInterfaces'],'positiveMainbodyContacts':None if r['allExactMainbodyInterfaces'] is None else sum(q['dimension']>0 for q in r['allExactMainbodyInterfaces']['contacts'])} for r in records],flush=True)
if __name__=='__main__':main()
