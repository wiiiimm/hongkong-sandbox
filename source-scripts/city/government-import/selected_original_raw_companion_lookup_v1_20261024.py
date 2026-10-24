"""Inspect complete raw government ZIP directories for a current companion GeoRef.

A bounded source lookup only; absence here is not territory-wide provider absence.
"""
import argparse
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','scope','uid']:p.add_argument('--'+k,required=True)
    p.add_argument('--sheet',action='append',required=True);a=p.parse_args();base=ROOT/'docs/astra-city/government-import';doc=base/a.batch;local=HERE/'local'/a.batch
    assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.scope])and not doc.exists()and not local.exists()
    _,pins=authenticate(base/a.scope);sp=base/a.scope/'summary.json';assert digest(sp.read_bytes())==pins[str(sp.relative_to(ROOT))];scope=read(sp);mp=ROOT/'3d-viewer/city/data/manifest.json';assert digest(mp.read_bytes())==scope['currentManifestSHA256'];refs=[Path(__file__),base/a.scope/'result.json',sp,mp];forms=[]
    for r in scope['rows']:
        f=base/a.scope/(r['uid'].split('/')[1]+'-forms.json.gz');assert digest(f.read_bytes())==pins[str(f.relative_to(ROOT))];refs.append(f);forms += [x for x in read(f)if x['building']['uid']==a.uid]
    assert forms and all(x==forms[0]for x in forms);current=forms[0];tp=ROOT/'3d-viewer'/current['tile'];assert digest(tp.read_bytes())==current['tileSHA256'];assert next(b for b in read(tp)['buildings']if b['uid']==a.uid)==current['building'];refs.append(tp);prefix=current['building']['buildingCSUID'][:10]
    assert len(prefix)==10 and prefix.isdigit()and len(set(a.sheet))==len(a.sheet)
    cached=[]
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        for sheet in a.sheet:
            assert '/'not in sheet and len(sheet)<30
            row=db.execute("SELECT cache_key,index_sha,result-'models' FROM astra_modelling.city_source_directories WHERE sheet=%s ORDER BY created_at DESC LIMIT 1",(sheet,)).fetchone();assert row,(sheet,'No authenticated cached source directory metadata')
            cached.append(dict(sheet=sheet,cacheKey=row[0],indexSHA256=row[1],directoryMetadata=row[2]))
    helper=module('raw_companion_directory_scan',HERE/'xl-next-support-recovery-20261005.py');parser=module('raw_companion_directory_parser',HERE.parent/'landmark-acquisition/acquire.py');rows=[]
    for entry in cached:
        sheet=entry['sheet'];old=entry['directoryMetadata'];folder=local/sheet/'directory'
        directory,_=helper.scan(dict(SHEETNO=sheet,Format_glTF=old['sourceURL'],REVISIONDATE=old['revision']),folder)
        raw=folder/'zip-directory.bin';infos,_=parser.parse_directory(raw.read_bytes());names=[i.filename for i in infos];hits=[n for n in names if prefix in n]
        save(doc/(sheet+'-all-members.json.gz'),names)
        rows.append(dict(**entry,scannedSourceURL=directory['sourceURL'],scannedRevision=directory['revision'],completeRawMembers=len(names),exactGeoRefMatches=hits,rawDirectory=dict(path=str(raw.relative_to(ROOT)),sha256=digest(raw.read_bytes()))));refs.extend(p for p in folder.rglob('*')if p.is_file());print(dict(sheet=sheet,completeRawMembers=len(names),matches=hits),flush=True)
    assert digest(mp.read_bytes())==scope['currentManifestSHA256']
    result=dict(uids=[a.uid],candidateOwners=scope['uids'],currentCompanion=current,exactGeoRef=prefix,rows=rows,sourceGeometryChanges=0,installationApproved=False,permanentRejection=False,qualification='Complete unfiltered raw directory members on explicitly named government sheets. No model-type filter; scoped misses do not establish territory-wide absence or authorise basic suppression, geometry edits or reconstruction. Prepared directory metadata and newly observed source revisions are preserved separately.')
    save(doc/'summary.json',result);refs.extend([HERE/'xl-next-support-recovery-20261005.py',HERE.parent/'landmark-acquisition/acquire.py']);module('raw_companion_lookup_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'bounded-complete-raw-companion-government-lookup',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
