#!/usr/bin/env node
"use strict";
/**
 * RIO Protocol SDK — JavaScript Verify Example
 * =============================================
 * Demonstrates how to verify a RIO receipt and ledger using the JS SDK.
 *
 * Run from the sdk/ directory:
 *   node examples/js_verify_example.js
 */

const path = require("path");
const fs   = require("fs");

// Load the SDK (no npm install needed — zero external dependencies)
const rio = require(path.join(__dirname, "../javascript/src/index"));

// Paths to example files
const EXAMPLES    = path.join(__dirname, "../../examples");
const RECEIPT_PATH = path.join(EXAMPLES, "example_receipt_v2.json");
const LEDGER_PATH  = path.join(EXAMPLES, "example_ledger.json");

function printBar() { console.log("=".repeat(60)); }

async function main() {
  printBar();
  console.log(" RIO Protocol SDK (JS) — Receipt + Conformance Example");
  printBar();

  // Read the demo service token from the ledger file.
  // In production: pass { serviceToken: process.env.RIO_SERVICE_TOKEN } instead.
  const ledgerData = JSON.parse(fs.readFileSync(LEDGER_PATH, "utf8"));
  const demoToken  = ledgerData.demo_service_token || "";

  // ── Example 1: verifyReceipt ──────────────────────────────────────────────
  console.log("\n[1] Verifying receipt + ledger together...");
  const result = rio.verifyReceipt(RECEIPT_PATH, LEDGER_PATH, { serviceToken: demoToken });

  console.log(`    Overall: ${result.overall}`);
  console.log(`    Passed:  ${result.checks_passed} / ${result.checks.length}`);
  for (const check of result.checks) {
    const icon = check.passed ? "✓" : "✗";
    console.log(`      ${icon} ${check.check_name}: ${check.detail}`);
  }

  // ── Example 2: verifyLedger (without receipt) ─────────────────────────────
  console.log("\n[2] Verifying ledger only...");
  const ledgerResult = rio.verifyLedger(LEDGER_PATH, { serviceToken: demoToken });
  console.log(`    Overall: ${ledgerResult.overall}`);
  console.log(`    Passed:  ${ledgerResult.checks_passed} / ${ledgerResult.checks.length}`);

  // ── Example 3: using pre-loaded objects ───────────────────────────────────
  console.log("\n[3] Using pre-loaded objects instead of file paths...");
  const receiptObj = JSON.parse(fs.readFileSync(RECEIPT_PATH, "utf8"));
  const objResult  = rio.verifyReceipt(receiptObj, ledgerData, { serviceToken: demoToken });
  console.log(`    Overall: ${objResult.overall}`);

  // ── Example 4: runConformanceTests ────────────────────────────────────────
  console.log("\n[4] Running Appendix C conformance test vectors...");
  const confResult = rio.runConformanceTests();
  console.log(`    Overall: ${confResult.overall}`);
  console.log(`    Passed:  ${confResult.passed}/${confResult.total}`);
  for (const r of confResult.results) {
    const icon = r.passed ? "✓" : "✗";
    console.log(`      ${icon} ${r.id.padEnd(6)} ${r.name}`);
  }

  // ── Example 5: what FAIL looks like ──────────────────────────────────────
  console.log("\n[5] Simulating a tampered receipt...");
  const tampered = JSON.parse(fs.readFileSync(RECEIPT_PATH, "utf8"));
  tampered.receipt_hash = "0".repeat(64);
  const failResult = rio.verifyReceipt(tampered, ledgerData, { serviceToken: demoToken });
  console.log(`    Overall: ${failResult.overall}`);
  for (const check of failResult.checks) {
    if (!check.passed) {
      console.log(`      ✗ ${check.check_name}: ${check.detail}`);
    }
  }

  // ── Summary ───────────────────────────────────────────────────────────────
  console.log();
  printBar();
  const allOk = result.overall === "PASS" && confResult.overall === "PASS";
  console.log(` Demo result: ${allOk ? "PASS" : "FAIL"}`);
  printBar();
  console.log();

  process.exit(allOk ? 0 : 1);
}

main().catch(err => { console.error(err); process.exit(1); });
