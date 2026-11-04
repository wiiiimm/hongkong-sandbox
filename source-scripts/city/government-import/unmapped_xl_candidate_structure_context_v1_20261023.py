"""Fetch official relationship closure for two unmapped originals' candidate forms.

Candidate overlap never grants ownership, source support, or installation approval.
No public viewer files are read or written while another installer is active.
"""
import gzip
import sys
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
sys.path.insert(0, str(HERE.parent / 'landsd-territory'))
from source import request

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-unmapped-two-candidate-structure-context-v1-20261023'
URL = 'https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer'


def main():
    out = BASE / BATCH
    assert not out.exists()
    prior = BASE / 'government-xl-four-primary-exceptions-native-context-v1-20261023'
    _, pins = authenticate(prior)
    refs = [Path(__file__), prior / 'result.json', HERE.parent / 'landsd-territory/source.py']
    sources = []
    for model in ['B349971856402063C0', 'B352981210001063C0']:
        p = prior / (model + '.json.gz')
        assert digest(p.read_bytes()) == pins[str(p.relative_to(ROOT))]
        refs.append(p)
        r = read(p)
        sources.append(dict(modelId=model, sourceKey=r['sourceKey'], candidateCSUIDs=sorted({f['buildingCSUID'] for f in r['currentAABBCandidates']})))
    out.mkdir()
    requests = []

    def quoted(values):
        assert all(str(v).isalnum() for v in values)
        return ','.join("'" + str(v) + "'" for v in values)

    def query(label, table, where):
        rows, offset = [], 0
        for page in range(20):
            params = dict(f='json', where=where, outFields='*', returnGeometry='false', resultRecordCount='1000', resultOffset=str(offset), orderByFields='OBJECTID')
            raw, receipt = request(URL + '/' + str(table) + '/query', params, json_expected=False)
            decoded = gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw
            p = out / (label + '-' + str(page) + '.json')
            p.write_bytes(decoded)
            save(p.with_name(p.stem + '-request.json'), dict(**receipt, decodedSHA256=digest(decoded), gzipDecoded=raw != decoded))
            if raw != decoded:
                p.with_suffix('.wire.gz').write_bytes(raw)
            data = read(p)
            assert not data.get('error'), data.get('error')
            found = [f['attributes'] for f in data['features']]
            rows.extend(found)
            requests.append(dict(label=label, page=page, table=table, rows=len(found), sha256=digest(decoded)))
            if not data.get('exceededTransferLimit') and len(found) < 1000:
                break
            assert found
            offset += len(found)
        else:
            raise AssertionError('Bounded official relationship pagination exhausted')
        ids = [r['OBJECTID'] for r in rows]
        assert len(ids) == len(set(ids))
        print(label, len(rows), flush=True)
        return rows

    candidates = sorted(set().union(*(set(s['candidateCSUIDs']) for s in sources)))
    primary = query('candidate-primary', 0, 'BuildingCSUID IN (' + quoted(candidates) + ')')
    links = query('candidate-links', 1002, 'BuildingCSUID IN (' + quoted(candidates) + ')')
    ids = sorted({int(r['BuildingStructureID']) for r in links})
    members, structures = [], []
    if ids:
        where = 'BuildingStructureID IN (' + ','.join(map(str, ids)) + ')'
        members = query('complete-members', 1002, where)
        structures = query('structures', 1003, where)
    member_ids = sorted({r['BuildingCSUID'] for r in members} - set(candidates))
    member_primary = query('other-member-primary', 0, 'BuildingCSUID IN (' + quoted(member_ids) + ')') if member_ids else []
    rows = []
    for source in sources:
        linked = {int(r['BuildingStructureID']) for r in links if r['BuildingCSUID'] in source['candidateCSUIDs']}
        complete = [r for r in members if int(r['BuildingStructureID']) in linked]
        csuids = set(source['candidateCSUIDs']) | {r['BuildingCSUID'] for r in complete}
        records = [r for r in primary + member_primary if r['BuildingCSUID'] in csuids]
        georef = source['modelId'][1:11]
        rows.append(dict(**source, structureIds=sorted(linked), completeOfficialMembers=complete, officialPrimaryRecords=records, exactOriginalGeoRefMatches=[r for r in records if str(r.get('GeoRefNo')) == georef], sourceIdentityAccepted=False, installationApproved=False))
    save(out / 'official-context.json.gz', dict(rows=rows, structures=structures))
    save(out / 'request-index.json', requests)
    summary = dict(uids=[], sourceKeys=[s['sourceKey'] for s in sources], sourceModels=2, candidateCSUIDs=len(candidates), officialStructureIds=len(ids), completeMembers=len(members), additionalMemberCSUIDs=len(member_ids), exactOriginalGeoRefMatches=sum(len(r['exactOriginalGeoRefMatches']) for r in rows), sourceIdentityAccepted=False, physicalAccepted=False, installationApproved=False, permanentRejection=False, newlyInstalled=0, sourceGeometryChanges=0, scriptExternalAICalls=0, qualification='Official relationship closure from precisely hash-bound candidate forms for two unmapped originals. Candidate spatial overlap/shared structure is evidence only; no new UID assignment, model replacement, original source/pose edit, support acceptance, optimisation or publication.')
    save(out / 'summary.json', summary)
    module('unmapped_structure_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'unmapped-xl-candidate-official-structure-context', refs, summary)
    print(summary, flush=True)


if __name__ == '__main__':
    main()
