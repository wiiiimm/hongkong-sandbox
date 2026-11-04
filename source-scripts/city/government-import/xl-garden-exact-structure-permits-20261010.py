"""Exact government structure/OP lineage, no common-owner interpretation."""
from pathlib import Path
import importlib.util,json
from run import ROOT,HERE,read,save,digest
DOC=ROOT/'docs/astra-city/government-import/government-xl-garden-exact-structure-permits-20261010'
INPUT=DOC.parent/'government-xl-garden-current-primary-identity-context-20261010'
def main():
 assert not DOC.exists();x=read(INPUT/'primary-context.json.gz');ids=sorted({r['attributes']['BuildingStructureID'] for r in x['exactStructureRelations']});assert len(ids)==4;spec=importlib.util.spec_from_file_location('garden_structure_queries',HERE/'xl-aqua-marine-fresh-overhead-source-context-v3-20261010.py');q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q);DOC.mkdir(parents=True);q.DOC=DOC;structures=q.query(1003,'BuildingStructureID IN ('+','.join(map(str,ids))+')','exact-current-structures');relations=q.query(1002,'BuildingStructureID IN ('+','.join(map(str,ids))+')','exact-current-all-related-buildings');save(DOC/'structure-context.json',{'originalPrimaryContextSHA256':digest((INPUT/'primary-context.json.gz').read_bytes()),'structureIds':ids,'exactStructures':structures,'allExactStructureBuildingRelations':relations,'identityAccepted':False,'physicalAccepted':False,'legalOwnershipClaim':False,'qualification':'Exact independently queried structure and related-building records. Shared or separate OP identifiers do not by themselves grant source relationship, support or physical exemptions.'});print(json.dumps({'structures':structures,'allRelations':relations}),flush=True)
if __name__=='__main__':main()
