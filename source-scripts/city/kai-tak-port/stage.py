"""Retain original packed mesh bytes and canonicalize only gzip's OS header."""
import gzip,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
c=json.loads((HERE/'candidates/catalogue.json').read_text());m=c['models'][0];raw=(HERE/'candidates'/m['asset']).read_bytes();canonical=raw[:9]+b'\xff'+raw[10:]
expected='7f87b32b2203ad478087cfbec4d19ed274c39a37abb5f1363385f5ecc8ed5a9c'
assert hashlib.sha256(canonical).hexdigest()==expected and gzip.decompress(raw)==gzip.decompress(canonical)
m.update(asset='assets/'+expected+'.glb.gz',sha256=expected,priority='landmark',sourceIdentityReviewed=True,identityReviewApproved=True)
c.update(area='Kai Tak Stadium',models=[m]);out=HERE/'staged';(out/'assets').mkdir(parents=True,exist_ok=True);(out/m['asset']).write_bytes(canonical);(out/'catalogue.json').write_text(json.dumps(c,indent=2)+'\n')
plan={'areas':[{'area':'Kai Tak Stadium','catalogue':'source-scripts/city/kai-tak-port/staged/catalogue.json','destination':'city/data/official-models/kai-tak-stadium/catalogue.json'}]};(HERE/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
