> This is a DRAFT specification and is subject to change. It is intended for discussion and feedback.

# RIO Protocol API Endpoints Specification

## 1. Introduction

This document specifies the REST API for a RIO Protocol implementation. The RIO Protocol is a fail-closed execution governance system for AI and automated systems. This specification defines the API endpoints, data structures, and communication protocols required to interact with a RIO-compliant system.

### 1.1. Conventions and Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in RFC 2119.

- **Traceability Chain**: `canonical_request` → `risk_evaluation` → `authorization_record` → `execution_record` → `attestation_record` → `receipt` → `ledger_entry`
- **Governed Execution Loop**: Observe → Verify → Evaluate → Authorize → Execute → Record → Attest → Ledger → Learn → Repeat

## 2. Base URL Convention

All API endpoints described in this specification are relative to a base URL. The base URL for version 1 of the RIO Protocol API SHALL be:

```
/api/v1
```

Implementations MAY prefix this with a domain and namespace (e.g., `https://api.example.com/rio/api/v1`).

## 3. Authentication

All API endpoints MUST be protected and require authentication. Clients MUST authenticate using one of the following methods:

- **mTLS**: Mutual Transport Layer Security, where both the client and server present valid certificates for authentication.
- **Bearer Token**: An `Authorization` header with a bearer token.

```
Authorization: Bearer <your_token>
```

Unauthenticated requests or requests with invalid credentials MUST result in a `401 Unauthorized` error.

## 4. API Endpoints

### 4.1. Request Submission

#### POST /requests

Submits a new canonical request for governed execution.

- **Method**: `POST`
- **Path**: `/requests`

**Request Body Schema**

```json
{
  "requester_id": "string",
  "nonce": "string",
  "operations": [
    {
      "resource": "string",
      "action": "string",
      "params": {}
    }
  ],
  "signature": "string"
}
```

**Response Schema**

```json
{
  "request_id": "string",
  "status": "pending_authorization",
  "timestamp": "string"
}
```

**Error Codes**

- `400 Bad Request`: Invalid request format.
- `409 Conflict`: Duplicate nonce.

**Example Request**

```json
{
  "requester_id": "user-123",
  "nonce": "a7d8f9b0-c1e2-4d5f-8a9b-0c1d2e3f4a5b",
  "operations": [
    {
      "resource": "/accounts/act-456/balance",
      "action": "transfer",
      "params": {
        "destination": "act-789",
        "amount": 100.00
      }
    }
  ],
  "signature": "..."
}
```

**Example Response**

```json
{
  "request_id": "req-abcdef123456",
  "status": "pending_authorization",
  "timestamp": "2026-03-25T12:00:00Z"
}
```

### 4.2. Request Status

#### GET /requests/{request_id}/status

Retrieves the current status of a specific request.

- **Method**: `GET`
- **Path**: `/requests/{request_id}/status`

**Response Schema**

```json
{
  "request_id": "string",
  "status": "string",
  "history": [
    {
      "status": "string",
      "timestamp": "string"
    }
  ]
}
```

**Error Codes**

- `404 Not Found`: `request_id` does not exist.

### 4.3. Authorization

#### POST /authorizations

Submits an authorization decision for a pending request.

- **Method**: `POST`
- **Path**: `/authorizations`

**Request Body Schema**

```json
{
  "request_id": "string",
  "authorizer_id": "string",
  "decision": "approved" | "denied",
  "signature": "string"
}
```

**Response Schema**

```json
{
  "authorization_id": "string",
  "request_id": "string",
  "status": "authorized" | "denied",
  "timestamp": "string"
}
```

#### GET /authorizations/{authorization_id}

Retrieves a specific authorization record.

- **Method**: `GET`
- **Path**: `/authorizations/{authorization_id}`

### 4.4. Execution

#### POST /executions

Triggers the execution of an authorized request.

- **Method**: `POST`
- **Path**: `/executions`

**Request Body Schema**

```json
{
  "request_id": "string"
}
```

**Response Schema**

```json
{
  "execution_id": "string",
  "request_id": "string",
  "status": "completed" | "failed",
  "result": {},
  "timestamp": "string"
}
```

#### GET /executions/{execution_id}

Retrieves a specific execution record.

- **Method**: `GET`
- **Path**: `/executions/{execution_id}`

### 4.5. Receipts

#### GET /receipts/{receipt_id}

Retrieves a specific receipt.

- **Method**: `GET`
- **Path**: `/receipts/{receipt_id}`

#### GET /receipts?request_id={id}

Retrieves the receipt for a given request ID.

- **Method**: `GET`
- **Path**: `/receipts`

### 4.6. Ledger

#### GET /ledger/entries/{entry_id}

Retrieves a specific ledger entry.

- **Method**: `GET`
- **Path**: `/ledger/entries/{entry_id}`

#### GET /ledger/verify/{entry_id}

Verifies the integrity of a single ledger entry.

- **Method**: `GET`
- **Path**: `/ledger/verify/{entry_id}`

#### POST /ledger/verify-chain

Verifies the integrity of the entire ledger hash chain.

- **Method**: `POST`
- **Path**: `/ledger/verify-chain`

### 4.7. Nonce Registry

#### POST /nonces/check

Checks if a nonce has been used.

- **Method**: `POST`
- **Path**: `/nonces/check`

**Request Body Schema**

```json
{
  "nonce": "string"
}
```

**Response Schema**

```json
{
  "used": true | false
}
```

#### POST /nonces/register

Registers a new nonce as used.

- **Method**: `POST`
- **Path**: `/nonces/register`

## 5. Standard Error Response Format

Errors SHALL be returned in a standard format:

```json
{
  "error": {
    "code": "string",
    "message": "string"
  }
}
```

## 6. Rate Limiting and Pagination

### 6.1. Rate Limiting

API clients SHOULD respect the `Retry-After` header in `429 Too Many Requests` responses. Implementations SHOULD include rate limiting to prevent abuse.

### 6.2. Pagination

For endpoints that return a list of items, pagination SHOULD be supported using query parameters:

- `limit`: The number of items to return (e.g., `limit=50`).
- `offset`: The starting position for the next page of results.
