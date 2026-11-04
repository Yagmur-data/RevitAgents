# Rebuild the settings.json MashProject2.dyn would send to the engine, from the .dyn's saved slider values.
import json, sys
dyn, out = sys.argv[1], sys.argv[2]
d = json.load(open(dyn, encoding="utf-8-sig"))
py = [n for n in d["Nodes"] if "Python" in n["ConcreteType"]][0]
p2n = {}
for n in d["Nodes"]:
    for p in n.get("Outputs", []): p2n[p["Id"]] = n
val = {}
for i, p in enumerate(py["Inputs"]):
    src = [c["Start"] for c in d["Connectors"] if c["End"] == p["Id"]]
    if src: val[i] = p2n[src[0]].get("InputValue")
s = {"h": val[8], "SOL_DIS_KENARI_KAPAT": True, "SOL_C_DERINLIGI": 24.0, "SOL_C_PARCA_SAYISI": int(round(val[9])),
     "KOPRU_YUKSEKLIGI": val[2], "KOPRU_GENISLIGI": val[3], "TEPE_UST": val[4], "TEPE_ALT": val[4],
     "SOL_C_ACIKLIGI": val[5], "SAG_C_ACIKLIGI": val[6], "KOSE_YUVARLATMA_YARICAPI": val[7],
     "GAUSS_X_UST": val[10], "GAUSS_Y_UST": val[11], "SIGMA_X_UST": val[12], "SIGMA_Y_UST": val[13],
     "GAUSS_X_ALT": val[14], "GAUSS_Y_ALT": val[15], "SIGMA_X_ALT": val[16], "SIGMA_Y_ALT": val[17]}
if 19 in val and val[19] is not None: s["GECIS_UZUNLUGU"] = val[19]   # MashProject5: underside transition length
json.dump(s, open(out, "w"), indent=1); print(json.dumps(s))
