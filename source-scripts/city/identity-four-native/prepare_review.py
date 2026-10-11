"""Pack exact GeoRefNo Cullinan exceptions and Elements using existing unchanged native GLB packer."""
import json,pathlib,sqlite3,sys,hashlib,gzip,importlib.util
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/identity-four-native';read=lambda p:json.loads(p.read_bytes())
sys.path.insert(0,str(ROOT/'source-scripts/city/shared-modelling'));import reservations
for path in ['/tmp/astra-identity-four-review-lease.json','/tmp/astra-identity-four-elements-lease.json']:assert reservations.owns(read(pathlib.Path(path)))
s=importlib.util.spec_from_file_location('existing_packer',ROOT/'source-scripts/city/central-completion/pack_models.py');pack=importlib.util.module_from_spec(s);s.loader.exec_module(pack)
cat=read(HERE/'candidates/catalogue.json');out=HERE/'review-candidates';out.mkdir(exist_ok=True);rows=read(DOC/'identity-geometry.json')['rows'];models=[]
c=sqlite3.connect('file:'+str(ROOT/'source-scripts/city/building-batch/local/buildings.sqlite')+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
for uid in ['landsd/203728:0','landsd/203724:0','landsd/37369:0','landsd/323059:0','landsd/273061:0']:
 b=dict(c.execute('select * from buildings where uid=? and active=1',(uid,)).fetchone())
 if uid=='landsd/273061:0':mp=HERE/'elements-support/staged/11-NW-24C/manifest.json';m=read(mp);spec=next(s for s in m['models']if s['id'].startswith('B'+b['csuid'][:10]))
 else:row=next(r for r in rows if r['uid']==uid);mp=ROOT/row['sourceManifest'];m=read(mp);spec=next(s for s in m['models']if s['id']==row['modelId'])
 for p,h in spec['sourceHashes'].items():assert hashlib.sha256((mp.parent/p).read_bytes()).hexdigest()==h
 raw,stats=pack.pack(mp.parent/spec['sourceEntry']);compressed=gzip.compress(raw,mtime=0);digest=hashlib.sha256(compressed).hexdigest();(out/(digest+'.glb.gz')).write_bytes(compressed)
 record={'uid':uid,'buildingCSUID':b['csuid'],'objectId':int(uid.split('/')[1].split(':')[0]),'modelId':spec['id'],'sourceTile':m['tile'],'sourceTileRevision':m['tileRevision'],'worldBounds':spec['worldBounds'],'triangles':spec['triangles'],'recordedBaseHeight':b['source_base'],'recordedTopHeight':b['source_top'],'label':b['name'],'priority':'unreviewed','asset':digest+'.glb.gz','encoding':'gzip','bytes':len(compressed),'glbBytes':len(raw),'decodedGeometryBytes':stats['decodedGeometryBytes'],'indexedVertices':stats['vertices'],'sha256':digest,'placementReviewed':False,'identityReviewApproved':False,'publicationApproved':False,'sourceManifest':str(mp.relative_to(ROOT))}
 models.append(record);print(uid,spec['id'],spec['worldBounds'],len(compressed))
cat.update(area='Four alias-resolved towers and exact Elements support; review only',models=models,counts={'packedModels':len(models)});(out/'catalogue.json').write_text(json.dumps(cat,indent=2)+'\n');(out/'catalogue-index.json').write_text(json.dumps({'models':5,'catalogues':['catalogue.json']},indent=2)+'\n')
