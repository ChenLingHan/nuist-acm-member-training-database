"""Python 3 standard library; download a revision-checked public dataset."""
import gzip, hashlib, json, urllib.request
BASE = "https://raw.githubusercontent.com/ChenLingHan/nuist-acm-member-training-database/main/"
def get(path):
    with urllib.request.urlopen(BASE + path, timeout=30) as response:
        return response.read()
index = json.loads(get("data/index.json"))
path = index["paths"].get("dataset_gzip", index["paths"]["dataset"])
raw = get(path)
if hashlib.sha256(raw).hexdigest() != index["files"][path]["sha256"]:
    raise RuntimeError("Snapshot changed or cache mismatch; retry or pin a commit SHA")
data = json.loads(gzip.decompress(raw) if path.endswith(".gz") else raw)
assert data["revision"] == index["revision"]
print({table: len(data[table]) for table in index["counts"]})
