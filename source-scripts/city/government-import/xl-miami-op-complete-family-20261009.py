"""Recover all eight unchanged originals in the explicit Miami OP source family."""
import importlib.util
from run import ROOT,HERE,read,save
DOC=ROOT/'docs/astra-city/government-import/government-xl-miami-op-complete-pair-20261009'
forms=[];basis=[]
for r in read(DOC/'missing-area-separate-upper-form-candidates.json.gz')['rows']:
 csuid=r['buildingCSUID'];relations=read(DOC/('upper-op-relations-'+csuid+'.json'))['features'];structures=read(DOC/('upper-op-structures-'+csuid+'.json'))['features']
 assert relations and structures
 assert {f['attributes']['BuildingStructureID'] for f in relations}=={f['attributes']['BuildingStructureID'] for f in structures}
 assert all(f['attributes']['OPNo'] in ['NT73/91','NT166/91'] and f['attributes']['OPBlockType']=='Tower' for f in structures)
 forms.append(r['originalCurrentForm']);basis.append({'uid':r['uid'],'exactCSUID':csuid,'freshOPRelations':relations,'freshOPStructures':structures})
assert len(forms)==6
s=importlib.util.spec_from_file_location('miami_source_family_recovery',HERE/'xl-miami-op-complete-pair-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
m.BATCH='government-xl-miami-op-complete-family-20261009';m.DOC=ROOT/'docs/astra-city/government-import'/m.BATCH;m.LOCAL=HERE/'local'/m.BATCH;m.UIDS+=sorted(f['uid'] for f in forms)
save(m.DOC/'complete-source-family-primary-basis.json',{'basis':basis,'sourceIdentityAccepted':False,'qualification':'Exact fresh provider tower structures share podium occupation permits NT73/91 and NT166/91; every original/source height retained. No geographic-neighbour inference or footprint suppression.'})
m.main(forms)
