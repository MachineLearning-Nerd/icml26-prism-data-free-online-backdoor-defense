import json, pathlib
s=json.load(open(pathlib.Path(__file__).parents[1]/'AUTONOMOUS_STATE.json'))
assert s['openreview_id']=='l3yzuHKpNe' and s['claim_1_outcome']['verdict']=='inconclusive'
assert pathlib.Path(__file__).parents[1].joinpath('contract/live_claims.json').exists()
