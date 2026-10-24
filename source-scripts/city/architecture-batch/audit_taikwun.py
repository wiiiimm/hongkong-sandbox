"""Read-only Tai Kwun identity/cache audit. Does not alter inventory or viewer.
Re-run against the current catalogue manifest; source geometry stays native HKPD.
"""
import collections,hashlib,io,json,pathlib,sqlite3,struct,zipfile
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def read(p):return json.loads(p.read_bytes())
# Building numbers verified from the site's official Building History index.
BLOCKS=[('01','Police Headquarters Block',235860),('02','Armoury',267623),('03','Barrack Block',263001),('04',"Married Inspectors' Quarters",242698),('06',"Married Sergeants' Quarters",261799),('07',"Single Inspectors' Quarters",230105),('08','Ablutions Block',16901),('09','Central Magistracy',251755),('10',"Superintendent's House",267516),('11','A Hall',273024),('12','B Hall',231915),('13','C Hall',263599),('14','D Hall',105155),('15','E Hall',114964),('17','F Hall',118450),('19','Bauhinia House',262589),('20','JC Contemporary',244346),('21','JC Cube',330467),('10+13',"Superintendent's House & C Hall",262026)]
def main():
 from shapely.geometry import Polygon
 from shapely import union_all
 c=sqlite3.connect('file:'+str(HERE.parent/'building-batch/local/buildings.sqlite')+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
 manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);live={m['uid']:dict(m,catalogue=p) for p in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/p)['models']}
 rows=[];targets={f'landsd/{n}:0' for _,_,n in BLOCKS}|{'landsd/184076:0'};bs={uid:dict(c.execute('select * from buildings where uid=? and active=1',(uid,)).fetchone()) for uid in targets};refs={b['csuid'][:10]:uid for uid,b in bs.items()};specs=collections.defaultdict(list)
 for p in ROOT.glob('source-scripts/city/*/staged/*/manifest.json'):
  md=read(p)
  for m in md['models']:
   if m.get('geoRefNo') not in refs:continue
   uid=refs[m['geoRefNo']];source_ok=all(hashlib.sha256((p.parent/rel).read_bytes()).hexdigest()==sha for rel,sha in m['sourceHashes'].items());assert source_ok
   specs[uid].append({'modelId':m['id'],'sourceManifest':str(p.relative_to(ROOT)),'sourceEntry':str((p.parent/m['sourceEntry']).relative_to(ROOT)),'sourceTile':md['tile'],'sourceTileRevision':md['tileRevision'],'sourceArchiveSHA256':md['sourceArchiveSha256'],'officialMatches':m['officialMatches'],'exactSingleSourceMatch':m['officialBuildingCSUIDs']==[bs[uid]['csuid']],'sourceFilesSHA256Verified':source_ok,'nativeBounds':m['worldBounds'],'vertices':m['vertices'],'triangles':m['triangles']})
 packed=collections.defaultdict(list)
 paths=list(ROOT.glob('source-scripts/city/*/compact/catalogue*.json'))+list((HERE.parent/'building-batch/local/candidates').glob('catalogue*.json'))
 for p in paths:
  for m in read(p).get('models',[]) if isinstance(read(p).get('models',[]),list) else []:
   if m.get('uid') in targets and m.get('asset') and (p.parent/m['asset']).exists():packed[m['uid']].append({'catalogue':str(p.relative_to(ROOT)),'asset':str((p.parent/m['asset']).relative_to(ROOT)),'modelId':m['modelId'],'bytes':m.get('bytes'),'sha256':m.get('sha256')})
 directory=ROOT/'source-scripts/city/central-completion/sources/11-SW-8D/zip-directory.bin';raw=directory.read_bytes();end=raw.rfind(b'PK\x05\x06');eo=struct.unpack('<4s4H2LH',raw[end:end+22]);buf=bytearray(eo[6]+len(raw));buf[eo[6]:]=raw
 with zipfile.ZipFile(io.BytesIO(buf)) as z:names=z.namelist()
 assert len(names)==eo[4]
 def record(uid,block=None):
  b=bs[uid];entries=[n for n in names if b['csuid'][:10] in n and n.endswith('.gltf')]
  matches=[s for s in specs[uid] if s['exactSingleSourceMatch']];detailed=bool(b['embedded'] or uid in live)
  return {'uid':uid,'objectId':b['object_id'],'buildingCSUID':b['csuid'],'buildingName':b['name'],'nameZH':b['zh'],'block':block,'kind':b['structure_type'],'centre':[b['x'],b['z']],'surveyedBaseTop':[b['source_base'],b['source_top']],'currentlyDetailed':detailed,'liveCatalogue':live.get(uid,{}).get('catalogue'),'status':'already-detailed' if detailed else 'cached-exact-source-candidate' if matches else 'source-not-present-in-checked-sheet-directory','cachedSources':specs[uid],'retainedCompactAssets':packed[uid],'sourceDirectoryEntries':entries,'placementQualification':'Source match is not architecture/placement approval. Keep native1x/HKPD, preserve absolute source geometry and independent surveyed outline heights.'}
 for block,name,oid in BLOCKS:
  uid=f'landsd/{oid}:0';assert bs[uid]['name']==name,(uid,name,bs[uid]['name']);rows.append(record(uid,block))
 def shape(b):
  r=json.loads(b['rings_json']);return Polygon(r[0],r[1:])
 hull=union_all([shape(bs[r['uid']]) for r in rows]).convex_hull;extras=[]
 for n in c.execute('select * from buildings where active=1 and x between -660 and -515 and z between 600 and 780'):
  if n['uid'] in targets:continue
  p=shape(n)
  if hull.covers(p.representative_point()):extras.append({'uid':n['uid'],'objectId':n['object_id'],'buildingCSUID':n['csuid'],'name':n['name'],'kind':n['structure_type'],'centre':[n['x'],n['z']],'qualification':'Inside convex hull of verified principal blocks only. Compound membership/role unverified; not automatically added to upgrade list.'})
 cfa=record('landsd/184076:0');cfa.update({'canonicalName':'Court of Final Appeal','identityReason':'Inventory name has leading The; confirmed current courtaddress8JacksonRoad from official Judiciary and AMO sites. Do not select present LegislativeCouncilComplex atTamar.','sourceLinks':['https://www.hkcfa.hk/en/visiting/attending/how/index.html','https://www.amo.gov.hk/en/heritage-trails/cw-trails/central/section-a/central-a5/index.html']})
 report={'issue':'HKS-208','scope':'Tai Kwun compound principal blocks and source components; Court of Final Appeal identity appendix.','inputManifestSHA256':hashlib.sha256(manifestpath.read_bytes()).hexdigest(),'provenance':[{'url':'https://www.taikwun.hk/en/taikwun/heritage_conservation/buildings','access':'Official page content retrieved via search index; direct open returned403. Official enumeration corroborated by app.taikwun.hk mirror search result.','supports':'16heritage blocks plus2modern additions; official blocknumbers and names.'},{'url':'https://www.taikwun.hk/tactile-audio-interactive-experience/en-US/tai-kwun-tactile-map','access':'Official search index excerpt; direct open returned403.','supports':'The named historic prison, police and courtgroups belong to this compound.'}],'sourceDirectory':{'path':str(directory.relative_to(ROOT)),'entries':len(names),'complete':True,'sha256':hashlib.sha256(raw).hexdigest()},'counts':{'architecturalBlocks':18,'namedSourceParts':len(rows),'currentDetailedParts':sum(r['currentlyDetailed'] for r in rows),'newCachedExactCandidates':sum(r['status']=='cached-exact-source-candidate' for r in rows),'withoutStandaloneSourceModel':sum(r['status']=='source-not-present-in-checked-sheet-directory' for r in rows)},'parts':rows,'unassignedWithinPrincipalBlockHull':extras,'explicitExclusions':[{'uid':'landsd/92514:0','name':'Tai Kwun Mansion','reason':'UnrelatedbuildinginWanChai; nottheTaiKwunheritagecompound.'},{'uid':'landsd/23045:0','name':'Central Police Station','reason':'Modernpolicefacilitywestofcompound; nothistoricPoliceHeadquartersBlock.'},{'uid':'landsd/116558:0','name':'Central Police District Headquarters','reason':'Modernpolicefacilitywestofcompound.'}],'unknowns':['MarriedInspectorsQuarters landsd/242698:0 has retained survey footprint but no exact3396415840model in complete cached11-SW-8Ddirectory. Do not inventreplacement or callcompoundcomplete.','Historic blocks10and13 have threegovernmentrecords including jointconnectingpart262026; keep allstableUIDs distinct.','Ancillary unnamedstructures, walls, pathsandfootbridges needseparatemembershipandgeometryreview; convexhull isonlyascreen.','Allnewcachedmodels require browser/placementacceptance, especially sourcebottom offsets for stacked/slopingblocks.'],'courtOfFinalAppeal':cfa,'aiCallsInScript':0,'networkRequestsInScript':0}
 report['groups']={'tai-kwun':{'uids':[r['uid'] for r in rows]},'court-final-appeal':{'uids':['landsd/184076:0']}}
 (HERE/'taikwun-audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n');print(json.dumps(report['counts']));print('Additionalunassigned',[(r['uid'],r['name'],r['kind']) for r in extras]);print('CFA',cfa['status'])
if __name__=='__main__':main()
