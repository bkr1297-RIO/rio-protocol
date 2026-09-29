"""Check real runtime export plus forbidden standing casts; no effect simulation."""
import copy
import json
import pathlib
import sys
from jsonschema import Draft202012Validator, FormatChecker

ROOT = pathlib.Path(__file__).resolve().parents[2]
schema_path = ROOT / 'schemas/open-arrow-v0.1.schema.json'
assert schema_path.exists(), 'portable Open Arrow contract must exist'
schema = json.loads(schema_path.read_text())
Draft202012Validator.check_schema(schema)
v = Draft202012Validator(schema, format_checker=FormatChecker())
trace = json.loads(pathlib.Path(sys.argv[1]).read_text())
count = 0
for view in (trace['arrow'], trace['failure'], trace['denial']):
    ids = set()
    for artifact in view['artifacts']:
        v.validate(artifact)
        assert artifact['artifact_id'] not in ids
        ids.add(artifact['artifact_id'])
        for ref in artifact['parent_refs']:
            assert ref in ids, 'history must be ordered and reconstructable'
        if artifact['kind'] == 'OAIR':
            v.validate(artifact['body'])
        count += 1
observation = next(a for a in trace['arrow']['artifacts'] if a['kind'] == 'Observation')
bad = copy.deepcopy(observation)
bad['standing']['Authority'] = 'HUMAN_BOUND'
assert list(v.iter_errors(bad)), 'observation cannot carry operative authority'
bad = copy.deepcopy(observation)
bad['kind'] = 'Evidence'
assert list(v.iter_errors(bad)), 'ordinary kind mutation must not qualify evidence'
for lifecycle in ('INSTALLED_AND_AUTHORIZED', 'HELD'):
    bad = copy.deepcopy(observation)
    bad['standing']['Lifecycle'] = lifecycle
    assert list(v.iter_errors(bad)), 'lifecycle must match the closed artifact kind'
for record in [trace['source_intent'], trace['proposal'], *trace['commands']]:
    v.validate(record)
    count += 1
lf = Draft202012Validator(json.loads((ROOT / 'schemas/local-field-v0.1.schema.json').read_text()), format_checker=FormatChecker())
lf.validate(trace['definition'])
lf.validate(trace['chain']['passage'])
print(f'PASS: {count} actual Open Arrow objects, field/passage compatibility, and forbidden casts')
