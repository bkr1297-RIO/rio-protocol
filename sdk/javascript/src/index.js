"use strict";
/**
 * RIO Protocol SDK — JavaScript
 * ==============================
 * Simple functions for verifying RIO receipts and ledgers and
 * running conformance tests.
 *
 * Quick start:
 *   const rio = require("./js-sdk");
 *
 *   const result = rio.verifyReceipt("receipt.json", "ledger.json",
 *                                    { serviceToken: "your-token" });
 *   console.log(result.overall);  // "PASS" or "FAIL"
 *
 * No external dependencies — Node.js built-ins only.
 */

const { verifyReceipt, verifyLedger } = require("./verifier");
const { runConformanceTests }          = require("./conformance");

module.exports = { verifyReceipt, verifyLedger, runConformanceTests };
