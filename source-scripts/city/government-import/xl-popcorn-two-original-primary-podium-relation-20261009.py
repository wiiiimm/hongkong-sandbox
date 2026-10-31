"""Independent primary footprint/vertical lineage for two attached original parts.

This captures a specific possible podium relation, not an acceptance exception.
Every failed foreign-area check remains; no support or installation credit.
"""
import importlib.util, json, sys, uuid
from pathlib import Path
import shapely
from run import ROOT, HERE, read, save, digest, reservations
sys.path.insert(0, str(HERE.parent/'landsd-territory'))
from source import BASE, request

BATCH='government-xl-popcorn-two-original-primary-podium-relation-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
PRIMARY=DOC.parent/'government-xl-popcorn-six-held-primary-lineage-20261009'
EXCESS=DOC.parent/'government-xl-popcorn-primary-excess-ownership-v2-20261009'
CONTACT=DOC.parent/'government-xl-popcorn-two-original-podium-contacts-20261009'
PODIUM='landsd/295538:0'
PARTS=['landsd/295421:0','landsd/295425:0']

def polygon(rings):
    shape=shapely.GeometryCollection()
    for ring in rings: shape=shape.symmetric_difference(shapely.Polygon(ring))
    assert shape.is_valid and shape.area>0
    return shape

def primary(provider, form):
    assert not provider.get('error') and not provider.get('exceededTransferLimit')
    assert len(provider['features'])==1
    sr=provider['spatialReference'];assert sr.get('latestWkid',sr.get('wkid'))==2326
    feature=provider['features'][0];a=feature['attributes']
    assert (a['Status'],a['BuildingCSUID'],a['BuildingID'],a['BuildingBlockType'])==('Active',form['buildingCSUID'],form['buildingId'],form['structureType'])
    shape=polygon([[(x-834500,816500-y) for x,y in ring] for ring in feature['geometry']['rings']])
    return a,shape

def main():
    assert not DOC.exists(), 'Fresh immutable primary source diagnostic required'
    claim=reservations.claim('popcorn-primary-podium-'+str(uuid.uuid4()),['source-context:'+BATCH],batch=BATCH,ttl=1800)
    assert claim['ok'];lease=claim['reservation'];DOC.mkdir(parents=True)
    paths=[Path(__file__),HERE.parent/'landsd-territory/source.py',EXCESS/'result.json',CONTACT/'result.json']
    rows=[]
    try:
        foreign=[read(EXCESS/(u.split('/')[1].replace(':','-')+'-foreign-actors.json')) for u in PARTS]
        assert all(len(x['foreignActors'])==1 and x['foreignActors'][0]['uid']==PODIUM for x in foreign)
        form=foreign[0]['foreignActors'][0]['currentForm']
        assert form==foreign[1]['foreignActors'][0]['currentForm'] and form['structureType']=='Podium'
        params={'f':'json','where':"BuildingCSUID='"+form['buildingCSUID']+"'",'outFields':'*','returnGeometry':'true','outSR':'2326','resultRecordCount':'1000'}
        raw,receipt=request(BASE+'/0/query',params)
        (DOC/'295538-0-primary.json').write_bytes(raw);save(DOC/'295538-0-primary.request.json',receipt)
        assert receipt['sha256']==digest(raw)
        attrs,parent=primary(json.loads(raw),form);current_parent=polygon(form['rings'])
        assert attrs['BuildingBlockType']=='Podium'
        for uid,old in zip(PARTS,foreign):
            assert reservations.heartbeat(lease)['ok']
            stem=uid.split('/')[1].replace(':','-')
            prior=read(PRIMARY/(stem+'-diagnostic.json'))
            # Use the exact current form from the frozen source context, not a
            # fabricated group polygon or names/OSM parents as spatial credit.
            context=read(PRIMARY/(stem+'-current-context.json.gz'))
            own=context['target'] if 'target' in context else context['identity']['target']
            provider=read(PRIMARY/(stem+'-provider.json'))
            # The source diagnostic's target is a summary; primary stable IDs
            # bind the complete provider footprint and current geometry below.
            a=provider['features'][0]['attributes'];assert a['BuildingCSUID']==own['buildingCSUID'] and a['BuildingBlockType']=='Tower'
            assert a['Status']=='Active' and prior['sourceSHA256']==old['sourceSHA256'] and prior['originalWorldTrianglesSHA256']==old['worldTrianglesSHA256']
            child=polygon([[(x-834500,816500-y) for x,y in ring] for ring in provider['features'][0]['geometry']['rings']])
            exact=read(CONTACT/(stem+'-contacts.json.gz'))
            assert exact['uid']==uid and exact['sourceSHA256']==old['sourceSHA256'] and exact['worldTrianglesSHA256']==old['worldTrianglesSHA256']
            assert exact['podiumUID']==PODIUM and exact['completeOriginalFaces']==old['originalFaces']
            component_faces=[f for c in exact['components'] for f in c['originalFaces']]
            assert sorted(component_faces)==list(range(exact['completeOriginalFaces'])) and len(set(component_faces))==len(component_faces)
            positive=[c for component in exact['components'] for c in component['exactOriginalPodiumContacts']['contacts'] if c['dimension']>0]
            item={'uid':uid,'sourceSHA256':old['sourceSHA256'],'worldTrianglesSHA256':old['worldTrianglesSHA256'],'completeOriginalFaces':old['originalFaces'],'primaryPartAttributes':a,'primaryPodiumAttributes':attrs,'primaryPartAreaM2':child.area,'primaryPartOutsidePrimaryPodiumM2':child.difference(parent).area,'primaryPartOutsideCurrentPodiumM2':child.difference(current_parent).area,'officialPartBaseAboveOfficialPodiumBase':a['BaseHeight']>=attrs['BaseHeight'],'officialPartBaseBelowOfficialPodiumTop':a['BaseHeight']<=attrs['TopHeight'],'exactPositiveDimensionalOriginalContacts':len(positive),'allOriginalComponentsHavePositivePodiumContact':all(c['positiveDimensionalContacts']>0 for c in exact['components']),'rawPrimaryForeignExcessM2':old['completePrimaryExcessM2'],'allForeignActorsRetained':old['foreignActors'],'sharedNameOrParentUsedForCredit':False,'occupationRelationUsedForCredit':False,'identityAccepted':False,'physicalSupportAccepted':False,'installationApproved':False,'sourceGeometryChanges':0}
            save(DOC/(stem+'-diagnostic.json'),item);rows.append(item)
            paths += [PRIMARY/(stem+'-diagnostic.json'),PRIMARY/(stem+'-current-context.json.gz'),PRIMARY/(stem+'-provider.json'),PRIMARY/(stem+'-provider.request.json'),EXCESS/(stem+'-identity.json'),EXCESS/(stem+'-foreign-actors.json'),CONTACT/(stem+'-contacts.json.gz')]
            print(json.dumps({k:item[k] for k in ['uid','primaryPartOutsidePrimaryPodiumM2','primaryPartOutsideCurrentPodiumM2','exactPositiveDimensionalOriginalContacts','allOriginalComponentsHavePositivePodiumContact']}),flush=True)
        save(DOC/'summary.json',{'rows':rows,'publication':False,'identityAccepted':False,'physicalSupportAccepted':False,'installationApproved':False,'qualification':'Specific complete original part/primary Podium relationship evidence only. Raw excess and all physical actors remain; no generic same-parent exemption, ground/support credit, or source geometry changes.'})
    finally:
        assert reservations.release(lease)['ok']
    spec=importlib.util.spec_from_file_location('popcorn_primary_podium_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    m.freeze(BATCH,'two-complete-originals-independent-primary-podium-relation-v1',paths,{'uids':PARTS+[PODIUM],'identityAccepted':False,'physicalAccepted':False,'requiresAIModelGeometry':False,'requiresHumanDecision':False,'remainingReason':'specific-primary-podium-relation-review-and-full-physical-source-support-pending','nextStep':'Review independent primary containment/vertical lineage and every exact source component contact. All current physical, foreign actor, terrain, runtime and browser checks remain required.'})

if __name__=='__main__':main()
