"""Fetch two missing native terrain pairs with the existing bounded ZIP-range pipeline."""
import importlib.util,json,gzip
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('a',ROOT/'source-scripts/city/landmark-acquisition/acquire.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
original=a.HERE;a.HERE=HERE/'native-terrain-extra';a.HERE.mkdir(exist_ok=True);(a.HERE/'official-selection.json.gz').write_bytes(gzip.compress(json.dumps({'datasetVersion':'Native terrain only','features':[]}).encode(),mtime=0));network=a.Network(a.HERE/'transfer-ledger.json',cap=10_000_000);out=[]
for uid,sheet in [('landsd/22089:0','11-NE-25C'),('landsd/255427:0','11-SW-7C')]:
 source=original/'sources'/sheet;infos,_=a.parse_directory((source/'zip-directory.bin').read_bytes());chosen={e.filename:{'headerOffset':e.header_offset,'crc32':e.CRC,'compressedBytes':e.compress_size,'decodedBytes':e.file_size} for e in infos if e.filename.startswith('TERRAIN') and e.filename.endswith(('.gltf','.bin'))};assert chosen;attrs=a.read(source/'download.json')['indexAttributes'];result=a.acquire_tile(network,sheet,{'attributes':attrs,'uids':[]},{},a.retained_caches(),exact_members=chosen);out.append({'uid':uid,'sheet':sheet,'result':result});print(sheet,result['status'],flush=True)
(ROOT/'docs/astra-city/assembly-support-review/extra-terrain-acquisition.json').write_text(json.dumps({'parts':out,'receivedBytes':network.data['receivedBytes']},indent=2)+'\n')
