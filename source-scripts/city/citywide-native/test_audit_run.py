"""Small deterministic HKS-222 audit fixtures; no database or network mutation."""
import gzip
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('native_audit_test',HERE/'audit_run.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)


def model(identifier,state='packed-needs-placement-review',uid='landsd/1:0',asset='a'*64):
    row={'modelId':'B'+identifier+'01063C0','state':state,'sourceEntry':'BUILDING/'+identifier+'.gltf','terrainCheck':{'status':'diagnostic-complete','belowTerrainQuarterMetre':0,'lowRimGapRange':[0,1]}}
    if state=='packed-needs-placement-review':row.update(candidate={'uid':uid},asset={'sha256':asset})
    elif state=='source-match-held':row['matching']={'officialCandidates':[],'officialMatches':[],'viewerMatches':[]}
    else:row['error']='Unrecognised source data'
    return row


class AuditTests(unittest.TestCase):
    def source(self,values):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);p=Path(t.name)/'raw.geojson.gz'
        features=[{'type':'Feature','properties':{'OBJECTID':i+1,'GeoRefNo':value,'BuildingCSUID':'unrelated-'+str(i)},'geometry':None}for i,value in enumerate(values)]
        p.write_bytes(gzip.compress(json.dumps({'type':'FeatureCollection','features':features}).encode()));return p

    def run_audit(self,records,expected,raw,defects=None):
        ledger=io.StringIO();s=a.audit_records(records,expected,raw,ledger,a.sha(raw),defects)
        return s,[json.loads(line)for line in ledger.getvalue().splitlines()]

    def test_partial_counts_collisions_and_missing_ref_classification(self):
        first=[model('1234567890'),model('1111111111','source-match-held'),model('2222222222','source-match-held')]
        second=[model('1234567890'),model('3333333333','source-match-held'),model('4444444444','failed')]
        records=[{'sheet':sheet,'expectedModels':len(ms),'result':{'counts':{'sourceModels':len(ms),'sourceTerrainModels':0},'models':ms,'terrain':[]}}for sheet,ms in [('A',first),('B',second)]]
        s,rows=self.run_audit(records,{'runId':'fixture','expectedSheets':3,'indexedModels':9},self.source(['1111111111',' 2222222222.0 ']))
        self.assertEqual(s['status'],'partial-mechanical-audit');self.assertEqual(s['indexedModelsWithoutAcceptedOutcomes'],3)
        self.assertEqual(s['crossSheetUIDCollisions'],{'uids':1,'members':2,'identicalSourceGroups':1,'distinctSourceGroups':0})
        self.assertEqual(s['absentSelectedFootprintClassifications'],{'mechanical-footprint-selection-or-shape-gap':1,'mechanical-reference-normalisation-review':1,'retained-footprint-identity-absent':1})
        self.assertEqual(s['exceptionCategories']['unclassified-conversion-failure'],1)
        self.assertTrue(s['rawFootprintAudit']['matchesExpectedSourceSHA256'])

    def test_known_source_defect_requires_matching_frozen_source(self):
        bad=model('4444444444','failed');bad['terrainCheck']={'status':'not-checked'};defect={'sheet':'A','modelId':bad['modelId'],'nativeStageSourceSHA256':'frozen','bytes':10}
        record={'sheet':'A','sourceSHA256':'frozen','expectedModels':1,'result':{'counts':{'sourceModels':1,'sourceTerrainModels':1},'models':[bad],'terrain':[{'sourceEntry':'terrain.gltf','state':'failed','error':'Invalid source'}]}}
        expected={'runId':'fixture','expectedSheets':1,'indexedModels':1};source=self.source([])
        s,rows=self.run_audit([record],expected,source,[defect]);self.assertEqual(s['exceptionCategories']['confirmed-source-corrupt'],1);self.assertEqual(s['terrainErrorPatterns'][0]['count'],1);self.assertEqual(s['confirmedSourceCorruptModels'],1);self.assertEqual(s['unknownMechanicalFailures'],1);self.assertNotIn('mechanical-terrain-diagnostic-failure',s['exceptionCategories'])
        record['sourceSHA256']='different';s,rows=self.run_audit([record],expected,source,[defect]);self.assertNotIn('confirmed-source-corrupt',s['exceptionCategories']);self.assertEqual(s['exceptionCategories']['unclassified-conversion-failure'],1)

    def test_count_mismatch_and_terrain_samples_not_approvals(self):
        m=model('1234567890');m['terrainCheck']={'status':'diagnostic-partial-coverage','belowTerrainQuarterMetre':2,'lowRimGapRange':[5,10]}
        record={'sheet':'A','expectedModels':2,'result':{'counts':{'sourceModels':1,'sourceTerrainModels':0},'models':[m],'terrain':[]}}
        s,rows=self.run_audit([record],{'runId':'fixture','expectedSheets':1,'indexedModels':2},self.source([]))
        self.assertEqual(s['countMismatches'],1);self.assertFalse(s['allAcceptedIndexedModelsAccounted']);self.assertEqual(s['sampledTerrainIntersectionModels'],1);self.assertEqual(s['elevatedLowRimModels'],1);self.assertFalse(s['candidatesAltered'])

    def test_verified_same_source_terrain_overlay_preserves_raw_failure(self):
        record={'sheet':'A','cacheKey':'original','sourceSHA256':'source','expectedModels':0,'result':{'counts':{'sourceModels':0,'sourceTerrainModels':1},'models':[],'terrain':[{'sourceEntry':'TERRAIN/a.gltf','state':'failed','error':'Bad normals'}]}}
        repair={'cacheKey':'repair','resultSHA256':'hash','item':{'stage':'native-terrain-repair','sourceSha256':'source','inputs':{'originalCacheKey':'original','sourceEntries':['TERRAIN/a.gltf']}},'result':{'models':[],'counts':{'sourceTerrainModels':1},'terrain':[{'sourceEntry':'TERRAIN/a.gltf','state':'prepared-geometry-only','sourceHashes':{'a.gltf':'source-sha'},'geometryProof':{'verticalScale':1}}]}}
        expected={'runId':'fixture','expectedSheets':1,'indexedModels':0};source=self.source([])
        for state in ['prepared-geometry-only','source-empty']:
            repair['result']['terrain'][0]['state']=state
            overlay=a.repair_overlay([repair],{'runId':'repair-run','expectedSheets':1,'acceptedSheets':1,'pendingSheets':0})
            summary=a.audit_records([record],expected,source,io.StringIO(),a.sha(source),terrain_repair=overlay)
            self.assertEqual(summary['terrainStates'],{'failed':1});self.assertEqual(summary['effectiveTerrainStates'],{state:1});self.assertEqual(summary['unknownMechanicalFailures'],0);self.assertEqual(summary['terrainRepair']['matchedOriginalFailures'],1)
        repair['item']['sourceSha256']='different'
        overlay=a.repair_overlay([repair],{'runId':'repair-run'})
        summary=a.audit_records([record],expected,source,io.StringIO(),a.sha(source),terrain_repair=overlay)
        self.assertEqual(summary['effectiveTerrainStates'],{'failed':1});self.assertGreater(summary['unknownMechanicalFailures'],0)

    def test_terrain_overlay_rejects_missing_proof_and_entry_count_mismatch(self):
        repair={'cacheKey':'repair','item':{'stage':'native-terrain-repair','sourceSha256':'source','inputs':{'originalCacheKey':'original','sourceEntries':['a.gltf']}},'result':{'models':[],'counts':{'sourceTerrainModels':1},'terrain':[{'sourceEntry':'a.gltf','state':'prepared-geometry-only'}]}}
        overlay=a.repair_overlay([repair],{'runId':'repair-run'});self.assertFalse(overlay['entries']);self.assertEqual(len(overlay['validationErrors']),1)
        repair['result']['terrain']=[]
        self.assertTrue(a.repair_overlay([repair],{})['validationErrors'])

    def test_normalisation_does_not_truncate_fractional_references(self):
        self.assertIsNone(a.normal_ref('1234.5'));self.assertIsNone(a.normal_ref(None));self.assertIsNone(a.normal_ref('NaN'));self.assertEqual(a.normal_ref(' 0001234.0 '),'1234')

if __name__=='__main__':unittest.main()
