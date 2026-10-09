"""Authorized terrain-only exact surface candidate, no live mutation."""
from run import ROOT,read,save,digest
from native_parent_child_flat_composition_20261010 import faces
from exact_runtime_coplanar_consolidation_20261010 import consolidate
DOC=ROOT/'docs/astra-city/government-import/government-xl-tung-sing-parent-coplanar-consolidation-20261010'
def main():
    assert not DOC.exists();path=ROOT/'3d-viewer/city/data/government-native-163705-0.json';triangles=faces(read(path));out,proof=consolidate(triangles)
    proof['originalFile']=str(path.relative_to(ROOT));proof['sourceSHA256']=digest(path.read_bytes());proof['originalRuntimeTrianglesSHA256']=digest(triangles.astype('<f8').tobytes());proof['candidateRuntimeTrianglesSHA256']=digest(out.astype('<f8').tobytes());save(DOC/'complete-exact-surface-certificates.json.gz',proof)
    save(DOC/'candidate-original-parent-surface.json.gz',{'position':out.reshape(-1).tolist(),'index':list(range(out.size//3)),'proofFile':str((DOC/'complete-exact-surface-certificates.json.gz').relative_to(ROOT)),'accepted':False})
    print({k:v for k,v in proof.items() if k!='components'},flush=True)
if __name__=='__main__':main()
