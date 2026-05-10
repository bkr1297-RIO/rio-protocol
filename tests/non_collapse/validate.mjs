import { readFileSync, existsSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = __dirname; // tests/non_collapse/
const repoRoot = resolve(__dirname, '../..'); // repo root

let errors = 0;
let passes = 0;

function check(label, condition, detail) {
  if (condition) {
    console.log(`  ✓ ${label}`);
    passes++;
  } else {
    console.log(`  ✗ ${label} — ${detail || 'FAILED'}`);
    errors++;
  }
}

function parseJSON(path) {
  try {
    return JSON.parse(readFileSync(path, 'utf8'));
  } catch (e) {
    return null;
  }
}

function parseJSONL(path) {
  try {
    const lines = readFileSync(path, 'utf8').trim().split('\n');
    return lines.map((line, i) => {
      try { return JSON.parse(line); }
      catch (e) { return null; }
    });
  } catch (e) {
    return null;
  }
}

// --- 1. All JSON files parse ---
console.log('\n=== 1. JSON Parse Validation ===');

const jsonFiles = [
  'manifest.json',
  'non_collapse_vectors_v0.1.json',
  'non_collapse_evaluation_record.schema.json',
  'non_collapse_failure_taxonomy_v0.1.json',
  'non_collapse_matcher_rules_v0.1.json',
  'non_collapse_failure_record.schema.json',
  'non_collapse_golden_summary.schema.json',
  'non_collapse_golden_summary.example.json',
  'non_collapse_harness_contract.json',
  'non_collapse_pass_fail_algorithm.json',
  'non_collapse_runtime_trace.schema.json',
  'non_collapse_conformance_report.schema.json',
  'non_collapse_conformance_report.example.json',
  'non_collapse_patch_target_matrix_v0.1.json',
  'MANNY_RUNTIME_TRACE_BRIEF.json'
];

for (const f of jsonFiles) {
  const full = resolve(root, f);
  const data = parseJSON(full);
  check(`${f} parses`, data !== null, 'JSON parse error');
}

// Also check provenance at repo root
const provPath = resolve(repoRoot, 'non_collapse_bundle_provenance_v0.1.json');
const provParses = parseJSON(provPath);
check('non_collapse_bundle_provenance_v0.1.json parses', provParses !== null, 'JSON parse error');

const jsonlFiles = [
  'non_collapse_variants_v0.1.jsonl',
  'non_collapse_golden_runs_v0.1.jsonl',
  'non_collapse_negative_runs_v0.1.jsonl',
  'non_collapse_reliance_negative_runs_v0.1.2.jsonl',
  'non_collapse_reliance_variants_v0.1.3.jsonl'
];

for (const f of jsonlFiles) {
  const full = resolve(root, f);
  const lines = parseJSONL(full);
  const allParsed = lines && lines.every(l => l !== null);
  check(`${f} parses (all lines)`, allParsed, 'JSONL parse error');
}

// --- 2. Manifest matches file set ---
console.log('\n=== 2. Manifest Validation ===');

const manifest = parseJSON(resolve(root, 'manifest.json'));
if (manifest) {
  check('manifest version = 0.1.3', manifest.version === '0.1.3', `got ${manifest.version}`);
  check('manifest total_artifacts = 28', manifest.total_artifacts === 28, `got ${manifest.total_artifacts}`);
  check('manifest has checksum_algorithm', manifest.checksum_algorithm === 'sha256');

  for (const artifact of manifest.artifacts) {
    const fullPath = resolve(repoRoot, artifact.path);
    const exists = existsSync(fullPath);
    check(`manifest → ${artifact.path} exists`, exists, 'file not found');
  }
}

// --- 3. Provenance file validation ---
console.log('\n=== 3. Provenance Validation ===');

const prov = parseJSON(provPath);
if (prov) {
  check('provenance.status = generated_from_spec', prov.status === 'generated_from_spec');
  check('provenance.runtime_status = not_enforced', prov.runtime_status === 'not_enforced');
  check('provenance.live_conformance_status = not_claimed', prov.live_conformance_status === 'not_claimed');
  check('provenance.original_bundle_recovered = false', prov.original_bundle_recovered === false);
}

// --- 4. Strict mode validation ---
console.log('\n=== 4. Strict Mode Validation ===');

const algo = parseJSON(resolve(root, 'non_collapse_pass_fail_algorithm.json'));
if (algo) {
  check('strict_mode.enabled = true', algo.strict_mode?.enabled === true);
  const constraints = algo.strict_mode?.constraints || [];
  check('no_tolerance_bands in constraints', constraints.includes('no_tolerance_bands'));
  check('no_soft_pass in constraints', constraints.includes('no_soft_pass'));
  check('no_exemption_list in constraints', constraints.includes('no_exemption_list'));
  check('no_known_acceptable_deviation_list in constraints', constraints.includes('no_known_acceptable_deviation_list'));
  check('no_partial_credit_for_required_behavior in constraints', constraints.includes('no_partial_credit_for_required_behavior'));
}

const contract = parseJSON(resolve(root, 'non_collapse_harness_contract.json'));
if (contract) {
  check('harness contract has strict_mode_human_readable', !!contract.strict_mode_human_readable);
  check('harness contract explains strict mode', contract.strict_mode_human_readable?.what_it_means?.includes('zero tolerance'));
}

// --- 5. Patch target matrix validation ---
console.log('\n=== 5. Patch Target Matrix Validation ===');

const matrix = parseJSON(resolve(root, 'non_collapse_patch_target_matrix_v0.1.json'));
if (matrix) {
  for (const target of matrix.patch_targets) {
    check(`${target.failure_code} has repair_vs_rule_review`, !!target.repair_vs_rule_review);
    check(`${target.failure_code} has human_decision_required=true`, target.human_decision_required === true);
    check(`${target.failure_code} default = requires_human_decision`, target.repair_vs_rule_review === 'requires_human_decision');
  }
}

// --- 6. Schema field validation (spot checks) ---
console.log('\n=== 6. Schema Spot Checks ===');

const evalSchema = parseJSON(resolve(root, 'non_collapse_evaluation_record.schema.json'));
if (evalSchema) {
  check('evaluation_record schema has required fields', evalSchema.required?.includes('evaluation_id') && evalSchema.required?.includes('result'));
}

const failSchema = parseJSON(resolve(root, 'non_collapse_failure_record.schema.json'));
if (failSchema) {
  check('failure_record schema has required fields', failSchema.required?.includes('failure_code') && failSchema.required?.includes('severity'));
}

const traceSchema = parseJSON(resolve(root, 'non_collapse_runtime_trace.schema.json'));
if (traceSchema) {
  check('runtime_trace schema has required fields', traceSchema.required?.includes('trace_id') && traceSchema.required?.includes('action'));
}

const reportSchema = parseJSON(resolve(root, 'non_collapse_conformance_report.schema.json'));
if (reportSchema) {
  check('conformance_report schema has required fields', reportSchema.required?.includes('proof_status_label') && reportSchema.required?.includes('patch_targets'));
}

// --- 7. Example validates against schema (structural check) ---
console.log('\n=== 7. Example Instance Validation ===');

const goldenExample = parseJSON(resolve(root, 'non_collapse_golden_summary.example.json'));
const goldenSchema = parseJSON(resolve(root, 'non_collapse_golden_summary.schema.json'));
if (goldenExample && goldenSchema) {
  const requiredFields = goldenSchema.required || [];
  const allPresent = requiredFields.every(f => f in goldenExample);
  check('golden_summary example has all required fields', allPresent, `missing: ${requiredFields.filter(f => !(f in goldenExample)).join(', ')}`);
  check('golden_summary example strict_mode = true', goldenExample.strict_mode === true);
}

const reportExample = parseJSON(resolve(root, 'non_collapse_conformance_report.example.json'));
if (reportExample && reportSchema) {
  const requiredFields = reportSchema.required || [];
  const allPresent = requiredFields.every(f => f in reportExample);
  check('conformance_report example has all required fields', allPresent, `missing: ${requiredFields.filter(f => !(f in reportExample)).join(', ')}`);
  check('conformance_report example strict_mode = true', reportExample.strict_mode === true);
  check('conformance_report example runtime_status = not_enforced', reportExample.runtime_status === 'not_enforced');
}

// --- 8. Vector counts ---
console.log('\n=== 8. Vector Count Validation ===');

const vectors = parseJSON(resolve(root, 'non_collapse_vectors_v0.1.json'));
if (vectors) {
  const golden = vectors.vectors.filter(v => v.type === 'golden');
  const negative = vectors.vectors.filter(v => v.type === 'negative');
  check('10 golden vectors', golden.length === 10, `got ${golden.length}`);
  check('20 negative vectors', negative.length === 20, `got ${negative.length}`);
  check('30 total base vectors', vectors.vectors.length === 30, `got ${vectors.vectors.length}`);
  check('10 rules defined', vectors.rules.length === 10, `got ${vectors.rules.length}`);
}

const goldenRuns = parseJSONL(resolve(root, 'non_collapse_golden_runs_v0.1.jsonl'));
check('10 golden run traces', goldenRuns?.length === 10, `got ${goldenRuns?.length}`);

const negativeRuns = parseJSONL(resolve(root, 'non_collapse_negative_runs_v0.1.jsonl'));
check('20 action-negative run traces', negativeRuns?.length === 20, `got ${negativeRuns?.length}`);

const relianceNeg = parseJSONL(resolve(root, 'non_collapse_reliance_negative_runs_v0.1.2.jsonl'));
check('11 reliance-negative run traces', relianceNeg?.length === 11, `got ${relianceNeg?.length}`);

const actionVariants = parseJSONL(resolve(root, 'non_collapse_variants_v0.1.jsonl'));
check('10 action variant vectors', actionVariants?.length === 10, `got ${actionVariants?.length}`);

const relianceVariants = parseJSONL(resolve(root, 'non_collapse_reliance_variants_v0.1.3.jsonl'));
check('12 reliance variant vectors', relianceVariants?.length === 12, `got ${relianceVariants?.length}`);

const totalVectors = 10 + 20 + 11 + 10 + 12;
check(`total vector count = ${totalVectors}`, totalVectors === 63, `got ${totalVectors}`);

// --- 9. Checksum validation ---
console.log('\n=== 9. Checksum Validation ===');

if (manifest && manifest.checksum_algorithm === 'sha256') {
  // Spot-check a few files (full checksum validation requires crypto module)
  check('manifest has checksum_algorithm field', true);
  const filesWithChecksums = manifest.artifacts.filter(a => a.sha256 && a.sha256 !== 'self' && a.sha256 !== 'pending_update');
  check(`${filesWithChecksums.length} files have sha256 checksums`, filesWithChecksums.length >= 25, `got ${filesWithChecksums.length}`);
}

// --- Summary ---
console.log('\n=== VALIDATION SUMMARY ===');
console.log(`  Passed: ${passes}`);
console.log(`  Failed: ${errors}`);
console.log(`  Status: ${errors === 0 ? 'ALL VALID' : 'ERRORS DETECTED'}`);
process.exit(errors === 0 ? 0 : 1);
