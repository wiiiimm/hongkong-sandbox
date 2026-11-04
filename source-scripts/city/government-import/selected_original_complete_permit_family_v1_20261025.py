"""Snapshot complete current official permit families for a selected primary packet.

Permit association alone grants no source identity, support or publication approval.
"""
import argparse,gzip,sys
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
sys.path.insert(0,str(HERE.parent/'landsd-territory'))
from source import request
URL='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer'


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--primary',required=True);a=p.parse_args();assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.primary]);base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();receipt,pins=authenticate(base/a.primary);refs=[Path(__file__),base/a.primary/'result.json']
 path=base/a.primary/'structures.json';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);selected=read(path)['features'];permits=sorted({r['attributes']['OPNo']for r in selected if r['attributes'].get('OPNo')});assert permits and all(isinstance(s,str)and len(s)<120 and not any(ord(c)<32 for c in s)for s in permits);out.mkdir()
 def query(name,table,where,geometry=False):
  raw,meta=request(URL+'/'+str(table)+'/query',dict(f='json',where=where,outFields='*',returnGeometry='true'if geometry else'false',outSR='2326',resultRecordCount='1000',orderByFields='OBJECTID'),json_expected=False)
  decoded=gzip.decompress(raw)if raw.startswith(b'\x1f\x8b')else raw;dest=out/(name+'.json');dest.write_bytes(decoded);save(out/(name+'-request.json'),dict(**meta,decodedSHA256=digest(decoded),gzipDecoded=decoded!=raw));d=read(dest);assert not d.get('error')and not d.get('exceededTransferLimit');return d['features']
 quote=lambda s:"'"+s.replace("'","''")+"'"
 structures=query('complete-permit-structures',1003,'OPNo IN ('+','.join(map(quote,permits))+')');ids=sorted({int(r['attributes']['BuildingStructureID'])for r in structures});assert ids
 relations=query('complete-permit-relations',1002,'BuildingStructureID IN ('+','.join(map(str,ids))+')');csuids=sorted({r['attributes']['BuildingCSUID']for r in relations});assert csuids
 footprints=query('complete-permit-footprints',0,'BuildingCSUID IN ('+','.join(map(quote,csuids))+')',True)
 assert {r['attributes']['BuildingCSUID']for r in footprints}==set(csuids)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==receipt['currentManifestSHA256'];refs.append(manifest)
 result=dict(uids=receipt['uids'],permits=permits,completePermitStructures=len(structures),completePermitRelations=len(relations),completePermitFootprints=len(footprints),completePermitCSUIDs=csuids,currentManifestSHA256=receipt['currentManifestSHA256'],allRequestedPermitRecordsReturned=True,identityAccepted=False,physicalAcceptance=False,installationApproved=False,publication=False,sourceGeometryChanges=0,qualification='Complete current official structures for every selected nonempty permit, reverse relations and exact footprint records were returned without transfer-limit truncation. Separate permits remain separate; this is source association evidence only, never geometry/support/ownership or publication credit.')
 save(out/'summary.json',result);refs.append(HERE.parent/'landsd-territory/source.py');module('complete_current_permit_family_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-current-selected-official-permit-family-snapshot',refs,result)


if __name__=='__main__':main()
