"""Fresh exact government primary records for the independently inspected Garden sources."""
from pathlib import Path
import importlib.util,json
from run import ROOT,HERE,read,save,digest
DOC=ROOT/'docs/astra-city/government-import/government-xl-garden-current-primary-identity-context-20261010'
INPUT=DOC.parent/'xl-terrain-recovery-20261010-garden-two-foreign-current-inputs-v1'
REC=DOC.parent/'government-xl-source-neighbour-recovery-leads-20261010/selection.json.gz'
def main():
 assert not DOC.exists();selected=read(INPUT/'check-selection.json.gz')['rows'];selected.append(next(r for r in read(REC)['rows'] if r['uid']=='landsd/213929:0'));manifest=ROOT/'3d-viewer/city/data/manifest.json';msha=digest(manifest.read_bytes());wanted={r['source']['building']['buildingCSUID'] for r in selected}
 for tile in read(manifest)['tiles']:
  p=ROOT/'3d-viewer'/tile['url']
  for b in read(p)['buildings']:
   if b['uid']=='landsd/162285:0':wanted.add(b['buildingCSUID']);podium={'building':b,'tile':tile['url'],'tileSHA256':digest(p.read_bytes())}
 assert len(wanted)==4;spec=importlib.util.spec_from_file_location('garden_primary_queries',HERE/'xl-aqua-marine-fresh-overhead-source-context-v3-20261010.py');q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q);DOC.mkdir(parents=True);q.DOC=DOC;where='BuildingCSUID IN ('+','.join("'"+c+"'" for c in sorted(wanted))+')';primary=q.query(0,where,'exact-current-primary',True);relations=q.query(1002,where,'exact-current-structure-relations');assert len(primary)==4
 save(DOC/'primary-context.json.gz',{'manifestSHA256':msha,'primaryRecords':primary,'exactStructureRelations':relations,'currentGardenPodium':podium,'unchangedOriginalRows':selected,'legalOwnershipClaim':False,'commonPermitClaim':False,'identityAccepted':False,'physicalAccepted':False,'qualification':'Actual exact primary original identifiers and component types. Source-specific visual/roof/terrace interpretations need independent review; no spatial, support, collision, terrain or source edit exemptions.'});assert digest(manifest.read_bytes())==msha
 print(json.dumps({'identities':[(r['attributes']['BuildingCSUID'],r['attributes']['BuildingBlockType'],r['attributes'].get('BuildingID')) for r in primary],'relations':relations}),flush=True)
if __name__=='__main__':main()
