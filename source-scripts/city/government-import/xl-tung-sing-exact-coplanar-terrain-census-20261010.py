"""Exact authored runtime plane census for an over-budget terrain candidate."""
from run import ROOT,HERE,read,save,digest
from native_parent_child_flat_composition_20261010 import faces
from exact_runtime_coplanar_groups_20261010 import groups
DOC=ROOT/'docs/astra-city/government-import/government-xl-tung-sing-exact-coplanar-terrain-census-20261010'
INPUTS={'parent':ROOT/'3d-viewer/city/data/government-native-163705-0.json',
        'child':HERE/'local/government-xl-tung-sing-two-nested-original-physical-v3-20261010/government-native-53800-0.json'}
def main():
    assert not DOC.exists()
    summaries={}
    for name,path in INPUTS.items():
        triangles=faces(read(path));result=groups(triangles)
        result['sourceFile']=str(path.relative_to(ROOT));result['sourceSHA256']=digest(path.read_bytes())
        result['runtimeWorldTrianglesSHA256']=digest(triangles.astype('<f8').tobytes())
        save(DOC/(name+'-exact-plane-groups.json.gz'),result)
        summaries[name]={k:v for k,v in result.items() if k not in ('rows','degenerateFaceIds')}
        summaries[name]['degenerateFaces']=len(result['degenerateFaceIds'])
        print(name,summaries[name],flush=True)
    save(DOC/'result.json',{'actors':['landsd/53800:0','landsd/126434:0'],
        'retainedActors':['landsd/12851:0','landsd/12852:0','landsd/12854:0','landsd/163705:0'],
        'planeCensus':summaries,'terrainBudget':100000,'geometryChanges':0,'accepted':False})
if __name__=='__main__':main()
