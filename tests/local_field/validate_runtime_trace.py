#!/usr/bin/env python3
"""Validate real runtime records; no generated success fixtures or execution claim."""
import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

root = Path(__file__).resolve().parents[2]
schema = json.loads((root / 'schemas/local-field-v0.1.schema.json').read_text())
Draft202012Validator.check_schema(schema)
validator = Draft202012Validator(schema, format_checker=FormatChecker())
trace = json.loads(Path(sys.argv[1]).read_text())
candidate = {key: trace['candidate'][key] for key in ('body', 'signature')}
records = [trace['definition'], *trace['controls'], candidate, trace['chain']['passage']]
for record in records:
    validator.validate(record)
return_schema = json.loads((root / 'schemas/local-field-return-v0.1.schema.json').read_text())
Draft202012Validator.check_schema(return_schema)
Draft202012Validator(return_schema, format_checker=FormatChecker()).validate(trace['chain']['return'])
missing = json.loads(json.dumps(trace['chain']['passage']))
del missing['body']['authority_basis']
assert not validator.is_valid(missing), 'missing standing reference accepted'
missing = json.loads(json.dumps(trace['chain']['passage']))
del missing['body']['return_requirement']
assert not validator.is_valid(missing), 'missing Return binding accepted'
print(f'PASS: {len(records)} actual signed records, attributed Return, and two malformed-record rejections')
