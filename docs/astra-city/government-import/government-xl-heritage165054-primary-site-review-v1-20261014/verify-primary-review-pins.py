import hashlib, json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[4]
HERE = pathlib.Path(__file__).resolve().parent
x = json.loads((HERE / "ROOT-REVIEW.json").read_bytes())
for row in x["filePins"]:
    p = ROOT / row["path"]
    assert p.is_file(), row["path"]
    assert hashlib.sha256(p.read_bytes()).hexdigest() == row["sha256"], row["path"]
f = json.loads((HERE / "source-bound-findings.json").read_bytes())
assert f["source"]["uid"] == "landsd/165054:0"
assert f["source"]["rawGzipSHA256"] == "1a978cdc751afa70933802e2faf090b2435250967e63b68f348ed232aeb1837f"
assert f["currentManifest"]["sha256"] == "c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7"
assert not any(f["flags"].values())
print(json.dumps({"allLiteralPinsPass":True,"pins":len(x["filePins"]),"uid":f["source"]["uid"],"primaryReviewOnly":True,"identityAccepted":False,"noDB":True,"noLease":True,"noModelCalculation":True},sort_keys=True))
