"""Bind unchanged complete contact roles to current arrays and plot both native interfaces.
Diagnostics only: no geometry, metadata, contact approval or publication changes.
"""
from pathlib import Path
import sys,uuid
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-parkview256319-native-seam-context-v1-20261104'
CURRENT='government-xl-parkview256319-after-tung-cheong-v1-20261104'
CONTACTS='government-xl-parkview256319-installed-support-sequence-v1-20261104-native-rebind'
ROLES='government-xl-cohort19-native-contact-roles-v1-20261101'
UID='landsd/256319:0'

def main():
    out=BASE/BATCH;lp=HERE/'local'/(BATCH+'-control')/'reservation.json'
    resources=sorted(['building:'+u for u in [UID,'landsd/254491:0','landsd/256116:0']]+['immutable-source-proof:'+BATCH])
    if '--owned'not in sys.argv:
        assert not out.exists()and not lp.parent.exists();c=reservations.claim('parkview-seam-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==set(resources)and not out.exists()
    refs=[Path(__file__)];pins={}
    def take(batch,name):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        p=BASE/batch/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    selection=take(CURRENT+'-runtime','selection.json.gz');source=next(r for r in selection['rows']if r['uid']==UID)
    source_attr=next(r for r in take(CURRENT+'-attributes','attributes.json.gz')['rows']if r['uid']==UID)
    context=take(CONTACTS,'summary.json');assert context['completeCurrentSourceArraysIdentical']and context['completeCurrentNativeArraysIdentical']and context['contactCalculationsRepeated']==0
    native_input={r['uid']:r for r in take(CONTACTS,'native-input.json.gz')['rows']};native_attrs={r['uid']:r for r in take(CONTACTS,'native-attributes.json.gz')['rows']}
    role_summary=take(ROLES,'summary.json');manifest=ROOT/'3d-viewer/city/data/manifest.json';mh=digest(manifest.read_bytes());assert mh==selection['manifestSHA256']==context['currentManifestSHA256'];refs.append(manifest)
    fields=dict(literal='completeLiteralWorldPosition',leftF32='completeExplicitLeftAssociatedFloat32WorldPosition',balancedF32='completeExplicitBalancedFloat32WorldPosition')
    out.mkdir();accounts=[];originals={};role_producer=HERE/'selected_original_native_contact_roles_v1_20261025.py';assert digest(role_producer.read_bytes())==pins[ROLES][str(role_producer.relative_to(ROOT))];refs.append(role_producer)
    for pair in context['rows']:
        assert pair['uid']==UID;native_uid=pair['nativeUid'];native=native_input[native_uid];assert native['entry']==pair['rawCurrentNativeEntry']
        source_path=ROOT/source['candidate']['path'];native_path=ROOT/native['path'];assert digest(source_path.read_bytes())==source['sourceSHA256']==pair['sourceSHA256'];assert digest(native_path.read_bytes())==native['entry']['sha256']==pair['nativeSHA256'];refs.extend([source_path,native_path])
        original=[decode_original_world_triangles(q.read_bytes())for q in [source_path,native_path]];originals[native_uid]=original
        for mode in ['original',*fields]:
            assert reservations.owns(lease)
            worlds=original if mode=='original'else[np.asarray(r[fields[mode]],dtype='<f8').reshape(-1,3)[np.asarray(r['completeOriginalIndex']).reshape(-1,3)]for r in [source_attr,native_attrs[native_uid]]]
            row=next(r for r in role_summary['rows']if r['uid']==UID and r['nativeUid']==native_uid and r['mode']==mode)
            assert row['sourceWorldSHA256']==digest(worlds[0].astype('<f8').tobytes())and row['nativeWorldSHA256']==digest(worlds[1].astype('<f8').tobytes())
            stem=UID.split('/')[1]+'--'+native_uid.split('/')[1]+'--'+mode+'.json.gz';raw=take(CONTACTS,stem);roles=take(ROLES,stem)
            assert raw['allPairsExamined']and raw['sourceFacesOmitted']==0
            assert [{k:v for k,v in r.items()if k!='contactRole'}for r in roles]==raw['contacts']
            (out/stem).write_bytes((BASE/ROLES/stem).read_bytes());accounts.append(row)
        roles=read(out/(UID.split('/')[1]+'--'+native_uid.split('/')[1]+'--original.json.gz'))
        points=np.asarray([[float(v)for v in point]for r in roles for point in r['exactPoints']]);lo=points.min(0);hi=points.max(0);pad=np.array([2.,3.,2.]);fig,axes=plt.subplots(1,3,figsize=(18,7))
        for ax,(i,j),label in zip(axes,[(0,1),(0,2),(2,1)],['X / elevation','X / Z','Z / elevation']):
            for triangles,color,name in zip(original,['#2687c7','#888888'],[UID,native_uid]):
                mask=np.all(triangles.max(1)>=lo-pad,axis=1)&np.all(triangles.min(1)<=hi+pad,axis=1);polys=triangles[mask][:,:,[i,j]]
                ax.add_collection(PolyCollection(polys,facecolors='none',edgecolors=color,linewidths=.35,alpha=.5));ax.plot([],[],color=color,label=name)
            for r in roles:
                q=np.asarray([[float(v)for v in point]for point in r['exactPoints']]);ax.plot(q[:,i],q[:,j],'.-',color='#c52a22'if r['dimension']<2 else'#ed8c10',markersize=2,linewidth=.65)
            ax.set_xlim(lo[i]-pad[i],hi[i]+pad[i]);ax.set_ylim(lo[j]-pad[j],hi[j]+pad[j]);ax.set_aspect('equal',adjustable='box');ax.set_title(label);ax.grid(alpha=.15);ax.legend(fontsize=7)
        fig.suptitle(UID+' / '+native_uid+' — original full contact locus, no geometry edits');fig.tight_layout();fig.savefig(out/(native_uid.split('/')[1].replace(':','-')+'-interface.png'),dpi=140);plt.close(fig)
        save(out/(native_uid.split('/')[1].replace(':','-')+'-locus.json'),dict(contactBounds=[lo.tolist(),hi.tolist()],contactSpanM=(hi-lo).tolist(),completeOriginalContactCount=len(roles),qualification='Contact extent and source facets only; no architectural or collision acceptance.'))
    assert digest(manifest.read_bytes())==mh and reservations.owns(lease)
    result=dict(uids=[UID],currentManifestSHA256=mh,rows=accounts,currentCompleteArraysAndEveryRawRoleVerified=True,contactCalculationsRepeated=0,sourceGeometryChanges=0,nativeMetadataChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,qualification=__doc__)
    save(out/'summary.json',result)
    module('parkview_current_native_seam_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-current-native-contact-roles-and-interface-context',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
