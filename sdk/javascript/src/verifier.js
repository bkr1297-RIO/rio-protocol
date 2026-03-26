"use strict";
/**
 * RIO Protocol SDK — Verifier (JavaScript)
 * ==========================================
 * Independent verification of RIO receipts and ledgers.
 * Uses only Node.js built-in modules (crypto, fs). No dependencies.
 *
 * Formulas implement the RIO Protocol Specification v1.0, Sections 5 and 6.
 */

const crypto = require("crypto");
const fs = require("fs");

// ── Internal crypto helpers ────────────────────────────────────────────────

function sha256(str) {
  return crypto.createHash("sha256").update(str, "utf8").digest("hex");
}

function hmacSha256(key, msg) {
  return crypto.createHmac("sha256", Buffer.from(key, "utf8"))
    .update(msg, "utf8")
    .digest("hex");
}

// ── File loading ───────────────────────────────────────────────────────────

function loadJson(pathOrObj) {
  if (typeof pathOrObj === "object" && pathOrObj !== null) return pathOrObj;
  return JSON.parse(fs.readFileSync(pathOrObj, "utf8"));
}

function resolveToken(serviceToken, ledger) {
  if (serviceToken) return serviceToken;
  if (process.env.RIO_SERVICE_TOKEN) return process.env.RIO_SERVICE_TOKEN;
  return ledger.demo_service_token || "";
}

// ── Individual checks ──────────────────────────────────────────────────────

function checkReceiptHash(receipt) {
  const vi          = receipt._verification_inputs || {};
  const prevHash    = vi.prev_hash    || "";
  const source      = vi.source       || "";
  const intent      = vi.intent       || "";
  const modelUsed   = vi.model_used   || "";
  const aiResponse  = (vi.ai_response_first_500_chars || receipt.response || "").slice(0, 500);
  const timestamp   = vi.timestamp    || receipt.timestamp || "";
  const stored      = receipt.receipt_hash || "";

  const data     = [prevHash, source, intent, modelUsed, aiResponse, timestamp].join("|");
  const computed = sha256(data);
  const passed   = computed === stored;

  return {
    check_name: "receipt_hash_integrity",
    passed,
    stored,
    computed,
    detail: passed
      ? "Receipt hash matches. Execution record is intact."
      : `MISMATCH — stored: ${stored.slice(0, 16)}…  computed: ${computed.slice(0, 16)}…`,
  };
}

function checkExecutionLedgerChain(rows) {
  if (!rows || rows.length === 0) {
    return { check_name: "execution_ledger_chain_integrity", passed: true,
             chain_intact: true, rows_checked: 0, detail: "No entries." };
  }

  let expectedPrev = "GENESIS";
  const rowResults = [];
  const failures   = [];

  for (const row of rows) {
    const fields = [
      row.action || "", row.agent || "", row.approver || "",
      row.executed_by || "", row.intent_id || "", row.parameters_hash || "",
      row.result || "", row.reason || "", row.receipt_hash || "",
      row.prev_hash || "", row.timestamp || "",
    ];
    const computed    = sha256(fields.join("|"));
    const stored      = row.entry_hash || "";
    const prevOk      = (row.prev_hash || "") === expectedPrev;
    const hashOk      = computed === stored;
    const ok          = prevOk && hashOk;

    rowResults.push({ row_id: row.id, prev_hash_ok: prevOk, entry_hash_ok: hashOk, passed: ok });
    if (!ok) failures.push(`Row id=${row.id}: ${!prevOk ? "prev_hash mismatch" : "entry_hash mismatch"}`);
    expectedPrev = stored;
  }

  const chainIntact = failures.length === 0;
  return {
    check_name: "execution_ledger_chain_integrity",
    passed: chainIntact,
    chain_intact: chainIntact,
    rows_checked: rows.length,
    row_results: rowResults,
    detail: chainIntact
      ? `All ${rows.length} entries verify correctly. Chain is intact.`
      : failures.slice(0, 3).join("; "),
  };
}

function checkPostExecLedgerHashes(rows) {
  if (!rows || rows.length === 0) {
    return { check_name: "post_exec_ledger_hash_integrity", passed: true,
             rows_checked: 0, detail: "No entries." };
  }

  let expectedPrev = "GENESIS";
  const rowResults = [];
  const failures   = [];

  for (const row of rows) {
    const seal = [
      row.timestamp || "", row.approver || "", row.agent || "",
      row.executed_by || "", row.policy_result || "",
      row.parameters_hash || "", row.result_hash || "", expectedPrev,
    ].join("|");
    const computed = sha256(seal);
    const stored   = row.ledger_hash || "";
    const ok       = computed === stored;

    rowResults.push({ row_id: row.id, passed: ok });
    if (!ok) failures.push(`Row id=${row.id}: ledger_hash mismatch`);
    expectedPrev = stored;
  }

  const passed = failures.length === 0;
  return {
    check_name: "post_exec_ledger_hash_integrity",
    passed,
    rows_checked: rows.length,
    row_results: rowResults,
    detail: passed
      ? `All ${rows.length} hash values verify correctly.`
      : failures.slice(0, 3).join("; "),
  };
}

function checkPostExecHmac(rows, serviceToken) {
  if (!rows || rows.length === 0) {
    return { check_name: "post_exec_hmac_signatures", passed: true,
             rows_checked: 0, detail: "No entries." };
  }
  if (!serviceToken) {
    return { check_name: "post_exec_hmac_signatures", passed: false,
             rows_checked: 0,
             detail: "No service token. Pass serviceToken= or set RIO_SERVICE_TOKEN." };
  }

  const rowResults = [];
  const failures   = [];

  for (const row of rows) {
    const stored = row.signature || "";
    if (stored === "key_unavailable") {
      rowResults.push({ row_id: row.id, passed: false, detail: "key_unavailable at write time" });
      failures.push(`Row id=${row.id}: signature=key_unavailable`);
      continue;
    }
    const computed = hmacSha256(serviceToken, row.ledger_hash || "");
    const ok       = computed === stored;
    rowResults.push({ row_id: row.id, passed: ok });
    if (!ok) failures.push(`Row id=${row.id}: HMAC mismatch`);
  }

  const passed = failures.length === 0;
  return {
    check_name: "post_exec_hmac_signatures",
    passed,
    rows_checked: rows.length,
    row_results: rowResults,
    detail: passed
      ? `All ${rows.length} HMAC signatures verify correctly.`
      : failures.slice(0, 3).join("; "),
  };
}

// ── Public API ─────────────────────────────────────────────────────────────

/**
 * Verify a RIO receipt against a ledger.
 *
 * @param {string|object} receiptPath  Path to receipt JSON file, or pre-loaded object.
 * @param {string|object} ledgerPath   Path to ledger JSON file, or pre-loaded object.
 * @param {object}        [options]
 * @param {string}        [options.serviceToken]  RIO_SERVICE_TOKEN for HMAC verification.
 * @returns {{ overall: string, checks_passed: number, checks_failed: number, checks: Array }}
 */
function verifyReceipt(receiptPath, ledgerPath, options = {}) {
  const receipt = loadJson(receiptPath);
  const ledger  = loadJson(ledgerPath);
  const token   = resolveToken(options.serviceToken, ledger);

  const execRows     = ledger.execution_ledger      || [];
  const postExecRows = ledger.post_execution_ledger || [];

  const checks = [
    checkReceiptHash(receipt),
    checkExecutionLedgerChain(execRows),
    checkPostExecLedgerHashes(postExecRows),
    checkPostExecHmac(postExecRows, token),
  ];

  const nPass = checks.filter(c => c.passed).length;
  const nFail = checks.length - nPass;

  return { overall: nFail === 0 ? "PASS" : "FAIL",
           checks_passed: nPass, checks_failed: nFail, checks };
}

/**
 * Verify only the ledger (without a receipt file).
 *
 * @param {string|object} ledgerPath   Path to ledger JSON file, or pre-loaded object.
 * @param {object}        [options]
 * @param {string}        [options.serviceToken]  RIO_SERVICE_TOKEN for HMAC verification.
 * @returns {{ overall: string, checks_passed: number, checks_failed: number, checks: Array }}
 */
function verifyLedger(ledgerPath, options = {}) {
  const ledger  = loadJson(ledgerPath);
  const token   = resolveToken(options.serviceToken, ledger);

  const execRows     = ledger.execution_ledger      || [];
  const postExecRows = ledger.post_execution_ledger || [];

  const checks = [
    checkExecutionLedgerChain(execRows),
    checkPostExecLedgerHashes(postExecRows),
    checkPostExecHmac(postExecRows, token),
  ];

  const nPass = checks.filter(c => c.passed).length;
  const nFail = checks.length - nPass;

  return { overall: nFail === 0 ? "PASS" : "FAIL",
           checks_passed: nPass, checks_failed: nFail, checks };
}

module.exports = { verifyReceipt, verifyLedger };
