"""Acquire only source terrain geometry for the LOHAS foundation check; no raster or runtime change."""
import importlib.util,pathlib,json,gzip,sys
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('a',ROOT/'source-scripts/city/landmark-acquisition/acquire.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
sys.path.insert(0,str(ROOT/'source-scripts/city/shared-modelling'));import reservations
assert reservations.owns(a.read(pathlib.Path('/tmp/astra-residential-podium-lease.json')))
source=HERE/'sources/12-SW-1D';infos,_=a.parse_directory((source/'zip-directory.bin').read_bytes());chosen={e.filename:{'headerOffset':e.header_offset,'crc32':e.CRC,'compressedBytes':e.compress_size,'decodedBytes':e.file_size} for e in infos if e.filename.startswith('TERRAIN') and e.filename.endswith(('.gltf','.bin'))};assert len(chosen)==2
attrs=a.read(source/'download.json')['indexAttributes'];a.HERE=HERE/'native-terrain';a.HERE.mkdir(exist_ok=True);(a.HERE/'official-selection.json.gz').write_bytes(gzip.compress(json.dumps({'datasetVersion':'Terrain geometry only','features':[]}).encode(),mtime=0))
network=a.Network(a.HERE/'transfer-ledger.json',cap=5_000_000);result=a.acquire_tile(network,'12-SW-1D',{'attributes':attrs,'uids':[]},{},a.retained_caches(),exact_members=chosen)
print(json.dumps({'status':result['status'],'terrain':bool(a.read(ROOT/result['manifest']).get('terrain')),'newBytes':network.data['receivedBytes']}))
