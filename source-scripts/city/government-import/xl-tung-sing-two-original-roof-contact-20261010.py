"""Complete original low rims vs every upward original mainbody roof facet."""
import numpy as np
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from source_closed_components import components
DOC=ROOT/'docs/astra-city/government-import/government-xl-tung-sing-two-original-roof-contact-20261010'
PRIOR=DOC.parent/'government-xl-tung-sing-two-detached-original-context-20261010/diagnostic.json.gz'
def main():
 assert not DOC.exists();d=read(PRIOR);source=next(ROOT/k for k in d['inputHashes'] if k.endswith('.glb.gz'));t=decode_original_world_triangles(source.read_bytes());parts=components(t)['components'];main=t[parts[1]['faceIndices']];n=np.cross(main[:,1]-main[:,0],main[:,2]-main[:,0]);length=np.linalg.norm(n,axis=1);ratio=np.divide(n[:,1],length,out=np.zeros(len(main)),where=length>0);roof=main[ratio>.25];rows=[]
 for part in d['rows']:
  a=t[part['allOriginalFaces']];rows.append({'component':part['component'],'originalFaceIds':part['allOriginalFaces'],'position':a.reshape(-1).tolist(),'index':list(range(len(a)*3)),'bottomHKPD':float(a[:,:,1].min()),'worldBounds':[a.min(axis=(0,1)).tolist(),a.max(axis=(0,1)).tolist()]})
 save(DOC/'complete-original-podium-footing-inputs.json.gz',{'terrain':{'position':roof.reshape(-1).tolist(),'index':list(range(len(roof)*3)),'worldTriangleSHA256':digest(roof.astype('<f8').tobytes())},'rows':[{'uid':d['uid'],'sourceSHA256':d['sourceSHA256'],'worldTriangleSHA256':d['wholeSourceWorldSHA256'],'wholeOriginalFaces':len(t),'parts':rows}],'allUpwardMainbodyOriginalRoofFaceIds':[parts[1]['faceIndices'][i] for i in np.flatnonzero(ratio>.25)],'basis':'all-exact-original-mainbody-upward-roof-facets','inputHashes':d['inputHashes']|{str(PRIOR.relative_to(ROOT)):digest(PRIOR.read_bytes())},'physicalAccepted':False})
if __name__=='__main__':main()
