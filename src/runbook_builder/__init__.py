import argparse,hashlib,json
def build(spec):
 required=("service","trigger","owner","steps","verification","rollback");missing=[k for k in required if not spec.get(k)] if isinstance(spec,dict) else list(required)
 if missing:return {"ok":False,"errors":{"missing":missing}}
 if not all(isinstance(spec[k],list) and 0<len(spec[k])<=100 for k in ("steps","verification","rollback")):return {"ok":False,"errors":{"invalid_lists":True}}
 lines=[f"# Runbook: {spec['service']}",f"Owner: {spec['owner']}",f"Trigger: {spec['trigger']}","","## Steps"]+[f"{i}. {x}" for i,x in enumerate(spec["steps"],1)]+["","## Verification"]+[f"- {x}" for x in spec["verification"]]+["","## Rollback"]+[f"- {x}" for x in spec["rollback"]];body="\n".join(lines);return {"ok":True,"markdown":body,"sha256":hashlib.sha256(body.encode()).hexdigest()}
def probe():
 g=build({"service":"demo","trigger":"alarm","owner":"team","steps":["inspect"],"verification":["healthy"],"rollback":["restore"]});b=build({"service":"demo","steps":["act"]});return {"ok":g["ok"] and not b["ok"],"rollback_counter_proof":not b["ok"]}
def main(argv=None):
 p=argparse.ArgumentParser();p.add_argument("command",choices=("build","probe"));p.add_argument("--input");a=p.parse_args(argv);o=probe() if a.command=="probe" else build(json.load(open(a.input)));print(json.dumps(o,sort_keys=True));return 0 if o["ok"] else 2
