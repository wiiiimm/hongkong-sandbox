"""Export every unchanged original face for actual retained-podium diagnostics."""
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from yoho_eight_current_bound_identity_20261009 import DOC as INPUT,verify_files
BATCH='government-xl-yoho-eight-actual-current-podium-support-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH
def main():
 assert not DOC.exists();row=read(INPUT/'selection.json.gz')['rows'][0];ctx=read(INPUT/'context.json.gz')['rows'][0];proof=verify_files(row,ctx,HERE/'local'/BATCH/'owned-identity-replay');assert proof['passed'];raw=(ROOT/row['candidate']['path']).read_bytes();t=decode_original_world_triangles(raw)
 save(DOC/'complete-original-source-inputs.json.gz',{'rows':[{'uid':row['uid'],'sourceSHA256':row['sourceSHA256'],'position':t.reshape(-1).tolist(),'index':list(range(len(t)*3)),'worldBounds':[t.min(axis=(0,1)).tolist(),t.max(axis=(0,1)).tolist()],'worldTriangleSHA256':digest(t.astype('<f8').tobytes())}],'sourcePath':row['candidate']['path'],'sourceGeometryChanges':0,'inputHashes':{row['candidate']['path']:digest(raw),str((INPUT/'result.json').relative_to(ROOT)):digest((INPUT/'result.json').read_bytes())},'completeCurrentIdentityProof':proof})
 print({'uid':row['uid'],'completeOriginalFaces':len(t),'physicalSupportApproval':False},flush=True)
if __name__=='__main__':main()
