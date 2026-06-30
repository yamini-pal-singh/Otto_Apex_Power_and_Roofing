# QA Guide: Testing Call Processing With Internal API Keys

## Purpose

While testing call-processing APIs, QA can use Shunya/internal test credentials so test usage is not attributed to a client billing key.

This is important when testing client tenant data, SOP behavior, call summaries, coaching, or call quality flows.

## Key Rule

Do not assume that changing only the request header `X-API-Key` prevents client billing attribution.

If QA or a client needs to override the tenant's default Shunya key for a specific call-processing request, pass the optional Shunya override header pair: `X-Shunya-API-Key` and `X-Shunya-API-Key-Id`.

There are two separate key concepts:

| Key / Field | Where It Is Used | Purpose | Billing Impact |
|---|---|---|---|
| `X-API-Key` request header | API request header | Authenticates the request to Otto Intelligence | Does not decide client billing attribution by itself |
| `X-Shunya-API-Key` request header | Optional API request header | Overrides the tenant's default Shunya ASR key for this request | Used with `X-Shunya-API-Key-Id` for this request |
| `X-Shunya-API-Key-Id` request header | Optional API request header | Provides the Shunya billing key ID for the override key | Used for usage/billing attribution |
| `company_id` in request body | Call-processing payload | Selects tenant configuration and company context | Used to load the default downstream Shunya billing/API key mapping |
| Internal `api_key_id` mapping | Server-side key configuration | Used for ASR and usage tracking events | This decides which billing key receives usage |

## Current Behavior

For `POST /api/v1/call-processing/process`:

1. QA sends a request with `X-API-Key`.
2. The API validates `X-API-Key` against the configured Otto API key.
3. The request body `company_id` is used to load tenant configuration.
4. If `X-Shunya-API-Key` and `X-Shunya-API-Key-Id` are provided, the system uses that pair for this request.
5. If no override header is provided, the system loads the Shunya API key and `api_key_id` mapped to the request `company_id`.
6. Usage events are published using the override or mapped `api_key_id`.

So, if QA sends a real client `company_id` without the Shunya override pair, the processing can still be attributed to that client's mapped Shunya billing key, even if the request was sent using an internal Otto `X-API-Key`.

## Required QA Testing Approach

For internal testing, QA should use one of these approved approaches:

| Option | When To Use | What To Do |
|---|---|---|
| Preferred | Functional testing without charging client | Use a dedicated internal/test `company_id` that is mapped to Shunya/internal test billing keys |
| Client-context testing without client billing | Testing a real client's SOP/config behavior | Use the real client `company_id`, but pass both `X-Shunya-API-Key` and `X-Shunya-API-Key-Id` with approved internal/test Shunya credentials |
| Not recommended | Direct testing with real client `company_id` and live client Shunya key | Avoid unless the client has explicitly approved billable testing |

## Request Header

All authenticated API requests must include:

```http
X-API-Key: <internal_otto_api_key>
X-Shunya-API-Key: <optional_shunya_override_key>
X-Shunya-API-Key-Id: <optional_shunya_override_key_id>
Content-Type: application/json
```

The Shunya override headers are optional. If either override header is passed, both must be passed. If only one is provided, the API returns `400` and the call is not queued.

Keys must stay server-side or in QA tools only. Do not put them in frontend/browser code.

For security, the raw `X-Shunya-API-Key` is not placed in the queued Kafka job payload. The API stores it as a short-lived server-side override reference and the worker loads it during processing.

## Call Processing API

Endpoint:

```http
POST https://ottoai.shunyalabs.ai/api/v1/call-processing/process
```

Example QA request:

```bash
curl -X POST "https://ottoai.shunyalabs.ai/api/v1/call-processing/process" \
  -H "X-API-Key: <internal_otto_api_key>" \
  -H "X-Shunya-API-Key: <optional_internal_or_client_shunya_key>" \
  -H "X-Shunya-API-Key-Id: <optional_internal_or_client_shunya_key_id>" \
  -H "Content-Type: application/json" \
  -d '{
    "call_id": "qa-test-20260629-001",
    "company_id": "<internal_or_test_company_id>",
    "audio_url": "https://example.com/test-call-audio.mp3",
    "phone_number": "+10000000000",
    "allow_reprocess": true
  }'
```

Expected response:

```json
{
  "job_id": "<job_id>",
  "call_id": "qa-test-20260629-001",
  "status": "queued",
  "message": "Call processing initiated successfully",
  "status_url": "/api/v1/call-processing/status/<job_id>"
}
```

## Status Check

After submitting a call, QA can check status using:

```bash
curl -X GET "https://ottoai.shunyalabs.ai/api/v1/call-processing/status/<job_id>" \
  -H "X-API-Key: <internal_otto_api_key>"
```

## QA Checklist Before Running Test Calls

| Check | Required Value |
|---|---|
| `X-API-Key` | Internal Otto API key |
| `X-Shunya-API-Key` | Optional internal/test Shunya key when overriding tenant default billing |
| `X-Shunya-API-Key-Id` | Required only when `X-Shunya-API-Key` is passed |
| `company_id` | Internal/test company ID, or real client company ID with approved Shunya override key |
| `call_id` | Unique QA call ID |
| `audio_url` | Test audio URL only |
| `allow_reprocess` | Use `true` only when intentionally rerunning same call ID |
| Billing key ID | Confirmed with the same Shunya key before running client-context tests |

## What Not To Do

| Do Not | Reason |
|---|---|
| Do not use a real client `company_id` without either checking billing key mapping or passing an approved Shunya override pair | Usage may be attributed to the client |
| Do not share actual API keys in email, chat, or screenshots | Keys are sensitive credentials |
| Do not expose `X-API-Key` in browser/frontend code | It should remain server-side or inside QA tooling |
| Do not reuse old `call_id` unless testing reprocessing | Duplicate calls can return conflict responses |

## Summary For QA Team

Use the internal Otto `X-API-Key` for authentication. To override billing/ASR attribution for a specific test request, pass both optional Shunya override headers.

If the goal is to test a client's SOP and tenant behavior without charging the client, use the client's `company_id` plus approved internal/test Shunya override credentials, or confirm the client's default mapping is already pointed to internal/test billing credentials.
