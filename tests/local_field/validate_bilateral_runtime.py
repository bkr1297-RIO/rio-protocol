#!/usr/bin/env python3
"""Schema-check actual bilateral runtime output; shape is never authority."""
import copy
import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

root = Path(__file__).resolve().parents[2]
base = json.loads((root / 'schemas/local-field-v0.1.schema.json').read_text())
trace = json.loads(Path(sys.argv[1]).read_text())
validator = Draft202012Validator(base, format_checker=FormatChecker())
for record in [*trace['definitions'].values(), *trace['controls'],
               {k: trace['candidate'][k] for k in ('body', 'signature')}, trace['chain']['passage']]:
    validator.validate(record)

bilateral = json.loads((root / 'schemas/local-field-bilateral-v0.1.schema.json').read_text())
native_return = json.loads((root / 'schemas/local-field-return-v0.1.schema.json').read_text())
Draft202012Validator.check_schema(base)
Draft202012Validator.check_schema(bilateral)
registry = Registry().with_resources([(s['$id'], Resource.from_contents(s)) for s in (base, bilateral, native_return)])
def validate(kind, value):
    schema = {'$ref': bilateral['$id'] + '#/$defs/' + kind}
    Draft202012Validator(schema, registry=registry, format_checker=FormatChecker()).validate(value)

validate('passage', trace['chain']['passage'])
validate('egress', trace['source_chain']['egress'])
validate('transit', trace['source_chain']['outgoing_transit'])
validate('return_transit', trace['source_chain']['incoming_return'])
validate('return_ingress', trace['source_chain']['return_ingress'])
Draft202012Validator(native_return, format_checker=FormatChecker()).validate(trace['chain']['return'])
for key in ('schema_version', 'replay', 'subject', 'nonce', 'authority_basis', 'return_requirement', 'dependencies'):
    changed = copy.deepcopy(trace['chain']['passage'])
    del changed['body'][key]
    try:
        validate('passage', changed)
    except Exception:
        continue
    raise AssertionError('missing required semantic field accepted: ' + key)
for change in ({'schema_version': 'future'}, {'undeclared_permission': True}):
    changed = copy.deepcopy(trace['chain']['passage'])
    changed['body'].update(change)
    try:
        validate('passage', changed)
    except Exception:
        continue
    raise AssertionError('unknown semantic extension accepted')
print('PASS: actual definitions/controls/candidate/passage, bilateral transit/Return and nine malformed passage rejections')
