"use strict";
/**
 * RIO Protocol SDK — Conformance Test Runner (JavaScript)
 * ========================================================
 * Runs the Appendix C test vectors from the RIO Protocol Specification v1.0.
 * Uses only Node.js built-in modules (crypto, fs). No dependencies.
 */

const crypto = require("crypto");
const fs     = require("fs");
const path   = require("path");

// ── Crypto helpers ─────────────────────────────────────────────────────────

function sha256(str) {
  return crypto.createHash("sha256").update(str, "utf8").digest("hex");
}

function hmacSha256(key, msg) {
  return crypto.createHmac("sha256", Buffer.from(key, "utf8"))
    .update(msg, "utf8")
    .digest("hex");
}

// ── Built-in test vectors (Appendix C) ────────────────────────────────────

const INTENT    = "Summarise the key properties of the secp256k1 elliptic curve in three bullet points.";
const SOURCE    = "manus";
const TIMESTAMP = "2026-03-26T14:00:00.000000Z";
const APPROVER  = "a1b2c3d4e5f6a7b8";
const AGENT     = "claude-sonnet-4-6";
const MODEL     = "claude";
const GATE_TS   = "2026-03-26T14:00:00.512344Z";
const POST_TS   = "2026-03-26T14:00:03.901234Z";
const RESP_TS   = "2026-03-26T14:00:03.847221Z";
const SVC_TOKEN = "demo-service-token-for-testing-only";
const AI_RESP   =
  "The secp256k1 elliptic curve has three key properties:\n\n" +
  "\u2022 Prime field: Defined over a 256-bit prime field, giving approximately 128-bit security.\n" +
  "\u2022 Cofactor h=1: Every non-identity point generates the full group, " +
  "which is important for cryptographic correctness.\n" +
  "\u2022 Efficient endomorphism: Supports a Frobenius endomorphism that enables " +
  "a roughly 30% speedup in scalar multiplication, which is why it was chosen " +
  "for Bitcoin and Ethereum.";

const BUILTIN_VECTORS = [
  {
    id: "TV-C1", name: "intent_hash",
    description: "SHA-256(UTF-8_encode(intent))",
    compute: () => sha256(INTENT),
    expected: "62ddf2d783eb52aa5f0d5aa671485a2239d5c2db01a324902dc282307301ee3a",
  },
  {
    id: "TV-C2", name: "parameters_hash",
    description: "SHA-256(UTF-8_encode(intent + '|' + source + '|' + timestamp))",
    compute: () => sha256(`${INTENT}|${SOURCE}|${TIMESTAMP}`),
    expected: "3becab543471433b50570a1bb0041ed79db2492e1522b4c3fe8c258543a9e356",
  },
  {
    id: "TV-C3", name: "entry_hash (blocked)",
    description: "entry_hash with empty agent and empty receipt_hash (double ||)",
    compute: () => {
      const intentId       = sha256(INTENT);
      const parametersHash = sha256(`${INTENT}|${SOURCE}|${TIMESTAMP}`);
      const fields = [
        "check_gate", "", APPROVER, "manus",
        intentId, parametersHash,
        "blocked", "missing_token", "",
        "GENESIS", "2026-03-26T14:00:01.000000Z",
      ];
      return sha256(fields.join("|"));
    },
    expected: "e44cced653ebcc9376c9ee741906b17b31762b60ba7bb83d6e2fdbf0efca1d29",
  },
  {
    id: "TV-C4", name: "ledger_hash (post-exec)",
    description: "SHA-256 of pipe-delimited post-execution seal fields",
    compute: () => {
      const parametersHash = sha256(`${INTENT}|${SOURCE}|${TIMESTAMP}`);
      const resultHash     = sha256(AI_RESP);
      const seal = [POST_TS, APPROVER, AGENT, "manus",
                    "success", parametersHash, resultHash, "GENESIS"].join("|");
      return sha256(seal);
    },
    expected: "71032422115b7424d6d2b5fd25c12dd66534ac7510f312a88a5c3f89d5afecec",
  },
  {
    id: "TV-C5", name: "HMAC signature",
    description: "HMAC-SHA256(key=service_token, msg=ledger_hash)",
    compute: () => {
      const parametersHash = sha256(`${INTENT}|${SOURCE}|${TIMESTAMP}`);
      const resultHash     = sha256(AI_RESP);
      const seal = [POST_TS, APPROVER, AGENT, "manus",
                    "success", parametersHash, resultHash, "GENESIS"].join("|");
      const ledgerHash = sha256(seal);
      return hmacSha256(SVC_TOKEN, ledgerHash);
    },
    expected: "52fd81e93bb7318814ba7f7092a430ee35b9de3de5b04e715ecf03fb485a8263",
  },
  {
    id: "TV-C6", name: "in-memory receipt_hash (first entry)",
    description: "SHA-256 with GENESIS prev_hash and ai_response[:500]",
    compute: () => {
      const resp500 = AI_RESP.slice(0, 500);
      return sha256(`GENESIS|${SOURCE}|${INTENT}|${MODEL}|${resp500}|${RESP_TS}`);
    },
    expected: "228cd0b0abfdf4d1cfcc6efa83abe8bc8d9b65f518153722a43cc91998498907",
  },
  {
    id: "TV-C7", name: "gate receipt_hash",
    description: "SHA-256(UTF-8_encode('GATE_PASSED|intent_id|source|ts'))",
    compute: () => {
      const intentId = sha256(INTENT);
      return sha256(`GATE_PASSED|${intentId}|${SOURCE}|${GATE_TS}`);
    },
    expected: "272dd6571870b29bb7f8434fe4aca3f8af0a527b9ca5b8b4ccbdaf9a929bff0f",
  },
];

// ── Public API ─────────────────────────────────────────────────────────────

/**
 * Run the RIO Protocol Appendix C conformance test vectors.
 *
 * @param {string} [testDirectory]  Optional path to a directory of custom
 *                                  vector JSON files. If omitted, runs only
 *                                  the built-in Appendix C vectors.
 * @returns {{ overall: string, total: number, passed: number, failed: number, results: Array }}
 */
function runConformanceTests(testDirectory) {
  const vectors = [...BUILTIN_VECTORS];

  // Load custom vectors if provided
  if (testDirectory) {
    const files = fs.readdirSync(testDirectory)
      .filter(f => f.endsWith(".json"))
      .sort();
    for (const file of files) {
      try {
        const tv = JSON.parse(fs.readFileSync(path.join(testDirectory, file), "utf8"));
        const inputStr = tv.input_string || "";
        vectors.push({
          id:          tv.id          || path.basename(file, ".json"),
          name:        tv.name        || file,
          description: tv.description || "",
          compute:     () => sha256(inputStr),
          expected:    tv.expected    || "",
        });
      } catch (e) {
        vectors.push({
          id: file, name: file, description: "custom vector",
          compute: () => { throw e; },
          expected: "",
        });
      }
    }
  }

  const results = vectors.map(tv => {
    let computed = "", passed = false, error = null;
    try {
      computed = tv.compute();
      passed   = computed === tv.expected;
    } catch (e) {
      error = e.message;
    }
    return { id: tv.id, name: tv.name, description: tv.description,
             passed, expected: tv.expected, computed, error };
  });

  const nPass = results.filter(r => r.passed).length;
  const nFail = results.length - nPass;

  return {
    overall: nFail === 0 ? "PASS" : "FAIL",
    total:   results.length,
    passed:  nPass,
    failed:  nFail,
    results,
  };
}

module.exports = { runConformanceTests };
