"""Apply typed original assembly support with complete face accounting."""
import importlib.util
import json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from original_component_support_20261009 import verify

BATCH='government-xl-hoi-yu-attached-support-proof-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
PAIR=ROOT/'docs/astra-city/government-import/government-xl-hoi-yu-original-pair-v2-20261009'
CENSUS=ROOT/'docs/astra-city/government-import/government-xl-hoi-yu-source-components-20261009/components.json.gz'
INTERFACES=ROOT/'docs/astra-city/government-import/government-xl-hoi-yu-component-interfaces-20261009/diagnostic.json.gz'
CONTACTS=ROOT/'docs/astra-city/government-import/government-xl-hoi-yu-positive-contact-attachment-20261009/diagnostic.json.gz'
PHYSICAL_LOCAL=HERE/'local/government-xl-hoi-fu-yu-complete-original-physical-v2-20261009'

def main():
    assert not DOC.exists()
    lease=read(PHYSICAL_LOCAL/'reservation.json');assert reservations.owns(lease)
    row=next(r for r in read(PAIR/'selection.json.gz')['rows'] if r['uid']=='landsd/177605:0')
    census=read(CENSUS);interfaces=read(INTERFACES);contacts=read(CONTACTS)
    assert row['sourceSHA256']==census['sourceSHA256']==contacts['sourceSHA256']
    for p,sha in interfaces['inputHashes'].items():assert digest((ROOT/p).read_bytes())==sha
    for item in contacts['evidenceRefs']:assert digest((ROOT/item['path']).read_bytes())==item['sha256']
    for uid in ['landsd/177604:0','landsd/177605:0']:
        part=next(r for r in read(PAIR/'selection.json.gz')['rows'] if r['uid']==uid)
        assert digest((ROOT/part['candidate']['path']).read_bytes())==part['sourceSHA256']
    spec=importlib.util.spec_from_file_location('hoi_yu_supported_original_decoder',HERE/'xl-second-pass.py')
    decoder=importlib.util.module_from_spec(spec);spec.loader.exec_module(decoder);decoder.LOCAL=PHYSICAL_LOCAL
    triangles=decoder.glb_triangles({**row,'triangles':8775})
    parts=census['components'];assert len(parts)==len(interfaces['rows'])==32
    for component,measured in zip(parts,interfaces['rows']):
        assert component['triangles']==measured['triangles']
        assert max(abs(a-b) for x,y in zip(component['bounds'],measured['bounds']) for a,b in zip(x,y))<.002
    edges=[{'component':r['component'],'anchorComponent':contacts['mainBodyComponent'],
        'sourceFace':r['witness']['sourceFace'],'anchorFace':r['witness']['mainBodyFace']}
        for r in contacts['rows'] if r['contactWithMainBody']]
    result=verify(triangles,[c['originalSourceFaces'] for c in parts],
        [r['interface'] for r in interfaces['rows']],edges)
    assert result['supportInterfaceAccepted'],result['reasons']
    paths=[CENSUS,INTERFACES,CONTACTS,PAIR/'result.json',Path(__file__),HERE/'original_component_support_20261009.py',HERE/'test_original_component_support_20261009.py',HERE/'exact_original_shell_intersections_20261009.py']
    refs=[{'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())} for p in paths]
    refs += [{'path':p,'sha256':sha} for p,sha in interfaces['inputHashes'].items()]
    refs += contacts['evidenceRefs']
    result.update(uid=row['uid'],supportUid='landsd/177604:0',sourceSHA256=row['sourceSHA256'],
        supportSHA256=next(r['sourceSHA256'] for r in read(PAIR/'selection.json.gz')['rows'] if r['uid']=='landsd/177604:0'),
        evidenceRefs=list({r['path']:r for r in refs}.values()),legacyGlobalRimRetained=True,
        independentlyGroundedPodiumRequired=True,newlyInstalled=0,aiGeometryModelling=False)
    assert reservations.owns(lease)
    save(DOC/'proof.json',result)
    print(json.dumps({k:result[k] for k in ['policy','supportInterfaceAccepted','sourceFaces','componentCount','anchorComponents','fullAcceptance']}),flush=True)

if __name__=='__main__':main()
