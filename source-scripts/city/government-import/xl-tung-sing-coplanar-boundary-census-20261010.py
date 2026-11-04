from run import ROOT,HERE,read,save,digest
from native_parent_child_flat_composition_20261010 import faces
from exact_coplanar_boundary_census_20261010 import census
DOC=ROOT/'docs/astra-city/government-import/government-xl-tung-sing-coplanar-boundary-census-20261010'
def main():
    assert not DOC.exists()
    inputs={'parent':ROOT/'3d-viewer/city/data/government-native-163705-0.json','child':HERE/'local/government-xl-tung-sing-two-nested-original-physical-v3-20261010/government-native-53800-0.json'}
    for name,path in inputs.items():
        result=census(faces(read(path)));result['sourceSHA256']=digest(path.read_bytes());result['sourceFile']=str(path.relative_to(ROOT));save(DOC/(name+'-boundary-census.json.gz'),result)
        print(name,{k:v for k,v in result.items() if k not in ('components','degenerateFaceIds')},flush=True)
if __name__=='__main__':main()
