"""Resolve absent inventory CSUID fields against exact current viewer records, read-only."""
from pathlib import Path
from collections import Counter
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-unfinished-current-record-viewer-join-v1-20261028';DOC=BASE/BATCH;PRIOR='government-xl-unfinished-current-record-status-v1-20261028'
def main():
 assert not DOC.exists();_,pins=authenticate(BASE/PRIOR);p=BASE/PRIOR/'summary.json';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];prior=read(p);assert prior['scope']==126 and not prior['errors'];wanted={r['uid']for r in prior['rows']if r['uid']};forms={};refs=[Path(__file__),BASE/PRIOR/'result.json',p];manifest=ROOT/'3d-viewer/city/data/manifest.json';refs.append(manifest)
 for tile in read(manifest)['tiles']:
  path=ROOT/'3d-viewer'/tile['url']
  for b in read(path)['buildings']:
   if b['uid']in wanted:assert b['uid']not in forms;forms[b['uid']]=dict(building=b,tile=tile['url'],tileSHA256=digest(path.read_bytes()));refs.append(path)
 assert set(forms)==wanted;rows=[]
 for r in prior['rows']:
  form=forms.get(r['uid']);current=form['building'].get('buildingCSUID')if form else None;indexed=r['indexedBuildingCSUID'];assert not indexed or indexed==current;exact=[x for x in r['currentRecords']if current and x['BuildingCSUID']==current];status='current-viewer-csuid-matches-government-record'if exact else 'unmatched-viewer-source-without-government-record'if not form and not r['currentRecords']else'current-record-binding-investigation'
  rows.append(dict(uid=r['uid'],sourceKey=r['sourceKey'],indexedSourceSHA256=r['indexedSourceSHA256'],inventoryCSUID=indexed,viewerCSUID=current,inventoryCSUIDAbsent=not indexed,currentViewer=form,matchingCurrentGovernmentRecords=exact,geoRefNo=r['geoRefNo'],status=status,installationApproved=False,permanentRejection=False))
 result=dict(uids=sorted(wanted),scope=126,sourceKeys=prior['sourceKeys'],rows=rows,statusCounts=dict(Counter(r['status']for r in rows)),absentInventoryCSUIDResolved=sum(r['inventoryCSUIDAbsent']and bool(r['matchingCurrentGovernmentRecords'])for r in rows),unmatchedViewerUIDsPreserved=sum(r['uid']is None for r in rows),sourceGeometryChanges=0,installationApproved=False,qualification='The33GeoRef-only results in the prior audit had absent inventoryCSUID fields, not evidence of33changed government records. This read-only exact-current-viewer join distinguishes missing bookkeeping from actual record differences; no source identity/geometry-fit, placement, active-record-to-model accuracy, permanent rejection or installation credit. Original inventory and both null viewer UIDs remain untouched.')
 save(DOC/'summary.json',result);module('unfinished_current_record_viewer_join_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-viewer-join-for-absent-inventory-csuid-status-audit',list(dict.fromkeys(refs)),result);print(dict(statusCounts=result['statusCounts'],absentInventoryCSUIDResolved=result['absentInventoryCSUIDResolved'],unmatchedUIDs=result['unmatchedViewerUIDsPreserved']),flush=True)
if __name__=='__main__':main()
