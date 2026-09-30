#!/usr/bin/env python3
"""Check the portable profile against real Projection/Local Field exports.

Schema validity is structural. Signature, current standing, host admission and
effect verification remain the receiving runtime and native proof verifier.
"""
import copy
import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

root = Path(__file__).resolve().parents[2]
schema = json.loads((root / 'schemas/projection-runtime-v0.1.schema.json').read_text())
Draft202012Validator.check_schema(schema)
v = Draft202012Validator(schema, format_checker=FormatChecker())
trace = json.loads(Path(sys.argv[1]).read_text())
count = 0
for view in (trace['projection'], trace['returning'], trace['successor'], trace['host_b'], trace['held']['projection']):
    v.validate(view)
    v.validate(view['projection'])
    prior = None
    for event in view['events']:
        v.validate(event)
        assert event['previous_event_ref'] == prior, 'event order lost'
        prior = event['event_id']
        count += 1
for command in trace['commands']:
    v.validate(command['record'])
    count += 1
lf_schema = json.loads((root / 'schemas/local-field-v0.1.schema.json').read_text())
Draft202012Validator.check_schema(lf_schema)
lf = Draft202012Validator(lf_schema, format_checker=FormatChecker())
for record in [trace['definition'], trace['host_b_definition'], *trace['controls'], *trace['host_b_controls'], trace['candidate'], trace['chain']['passage'], trace['held']['candidate'], trace['held']['chain']['passage']]:
    lf.validate(record)
    count += 1
bad = copy.deepcopy(trace['projection']['projection'])
bad['authority'] = 'SOURCE'
assert not v.is_valid(bad), 'identity cannot carry an ad hoc authority field'
bad = copy.deepcopy(trace['chain']['passage'])
del bad['body']['projection']['binding_ref']
assert not lf.is_valid(bad), 'projection passage needs an independent binding'
bad = copy.deepcopy(trace['host_b']['events'][-1])
bad['payload']['status'] = 'INHERITED'
assert not v.is_valid(bad), 'carriage is not an admission status'
bad = copy.deepcopy(trace['projection'])
bad['visibility_effect'] = 'AUTHORITY'
assert not v.is_valid(bad), 'view cannot claim authority'
assert trace['host_b']['current_binding'] is None
assert trace['host_b_denial']['status'] == 'DENIED'
assert trace['projection']['projection']['projection_id'] == trace['host_b']['projection']['projection_id']
assert trace['successor']['projection']['predecessor_ref'] == trace['projection']['projection']['projection_id']
assert trace['held']['chain']['attempt'] is None
assert trace['held']['chain']['receipt'] is None
assert trace['held']['chain']['return']['receipt_id'] is None
assert trace['held']['projection']['pending_returns'] == []
return_schema = json.loads((root / 'schemas/local-field-return-v0.1.schema.json').read_text())
Draft202012Validator(return_schema, format_checker=FormatChecker()).validate(trace['held']['chain']['return'])
print(f'PASS: {count} actual portable records/events, typed views, lineage and four malformed promotion rejections')
