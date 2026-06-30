# Otto Intelligence Service API Reference
**Version:** 1.0.0

Source: `docs/api/openapi.json` — saved from https://ottoai.shunyalabs.ai/docs


## Root

### `GET` /

**Root**
> Root endpoint

**Response `200`:** Successful Response
- `application/json` → inline


## Ask Otto

### `POST` /api/v1/ask-otto/conversations

**Create Conversation**
> Create a new conversation session.

**Request Body (`application/json`):** `CreateConversationRequest`

**Response `201`:** Successful Response
- `application/json` → `CreateConversationResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `GET` /api/v1/ask-otto/conversations/{conversation_id}

**Get Conversation**
> Get conversation details.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `conversation_id` | path | string | ✅ | Conversation ID (UUID format) |

**Response `200`:** Successful Response
- `application/json` → `GetConversationResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `DELETE` /api/v1/ask-otto/conversations/{conversation_id}

**Delete Conversation**
> Delete a conversation and all its messages.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `conversation_id` | path | string | ✅ | Conversation ID (UUID format) |

**Response `204`:** Successful Response

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `POST` /api/v1/ask-otto/conversations/{conversation_id}/messages

**Send Message**
> Send a message and get AI response.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `conversation_id` | path | string | ✅ | Conversation ID (UUID format) |

**Request Body (`application/json`):** `SendMessageRequest`

**Response `200`:** Successful Response
- `application/json` → `SendMessageResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `GET` /api/v1/ask-otto/conversations/{conversation_id}/messages

**Get Messages**
> Get conversation message history.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `conversation_id` | path | string | ✅ | Conversation ID (UUID format) |
| `limit` | query | integer |  |  |
| `before` | query | string |  |  |

**Response `200`:** Successful Response
- `application/json` → `GetMessagesResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`


## Call Processing

### `GET` /api/v1/call-processing/calls

**List Calls**
> List calls for a company with pagination and filters.

Returns call metadata including status, duration, rep info, and timestamps.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `company_id` | query | string | ✅ | Company ID (required) |
| `call_ids` | query | string |  | Comma-separated list of specific call IDs |
| `rep_id` | query | string |  | Filter by rep ID (from metadata.rep_id) |
| `rep_name` | query | string |  | Filter by rep name (partial match) |
| `status` | query | string |  | Filter by status: queued, processing, completed, failed |
| `phone_number` | query | string |  | Filter by phone number (partial match) |
| `from_date` | query | string |  | Filter calls from this date |
| `to_date` | query | string |  | Filter calls until this date |
| `min_duration` | query | string |  | Minimum call duration in seconds |
| `max_duration` | query | string |  | Maximum call duration in seconds |
| `limit` | query | integer |  | Results per page |
| `offset` | query | integer |  | Pagination offset |
| `sort_by` | query | string |  | Sort field: call_date, created_at, duration |
| `sort_order` | query | string |  | Sort order: asc, desc |

**Response `200`:** Successful Response
- `application/json` → `CallsListResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `GET` /api/v1/call-processing/calls/{call_id}/detail

**Get Call Detail**
> Get full details for a specific call including transcript and segments.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `call_id` | path | string | ✅ |  |
| `include_transcript` | query | boolean |  | Include full transcript |
| `include_segments` | query | boolean |  | Include diarized segments |

**Response `200`:** Successful Response
- `application/json` → `CallDetailResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `GET` /api/v1/call-processing/calls/{call_id}/phases

**Get Call Phases**
> Get conversation phases for a call.

Returns detected phases with timestamps and quality assessments.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `call_id` | path | string | ✅ |  |

**Response `200`:** Successful Response
- `application/json` → `CallPhasesResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `GET` /api/v1/call-processing/chunks/{call_id}

**Get Call Chunks**
> Get chunk summaries for a call.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `call_id` | path | string | ✅ |  |

**Response `200`:** Successful Response
- `application/json` → `ChunksResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `GET` /api/v1/call-processing/phases/analytics

**Get Phase Analytics**
> Get aggregated phase analytics for a company (per Q57).

Returns:
- Average time per phase
- Detection rates
- Commonly missing phases

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `company_id` | query | string | ✅ |  |
| `days` | query | integer |  |  |
| `rep_role` | query | string |  |  |

**Response `200`:** Successful Response
- `application/json` → inline

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `GET` /api/v1/call-processing/phases/search

**Search By Phase**
> Search calls by phase presence/absence.

Find calls that have or are missing specific phases.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `company_id` | query | string | ✅ |  |
| `phase` | query | string |  |  |
| `missing_phase` | query | string |  |  |
| `detected` | query | string |  |  |
| `limit` | query | integer |  |  |
| `offset` | query | integer |  |  |

**Response `200`:** Successful Response
- `application/json` → inline

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `POST` /api/v1/call-processing/process

**Process Call**
> Submit a call for processing.

Returns immediately with a job ID for status tracking.
Background processing happens asynchronously.

Duplicate Processing Prevention:
- By default, if a call_id is alre

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `X-Shunya-API-Key` | header | string |  |  |
| `X-Shunya-API-Key-Id` | header | string |  |  |

**Request Body (`application/json`):** `ProcessCallRequest`

**Response `202`:** Successful Response
- `application/json` → `ProcessCallResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `POST` /api/v1/call-processing/retry/{job_id}

**Retry Failed Job**
> Retry a failed processing job.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `job_id` | path | string | ✅ |  |

**Response `202`:** Successful Response
- `application/json` → `RetryJobResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `GET` /api/v1/call-processing/status/{job_id}

**Get Job Status**
> Get the processing status of a job.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `job_id` | path | string | ✅ |  |

**Response `200`:** Successful Response
- `application/json` → `JobStatusResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `GET` /api/v1/call-processing/summaries

**List Call Summaries**
> List call summaries for a company with pagination and filters.

Returns structured summaries including compliance, qualification, objections, and lead scores.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `company_id` | query | string | ✅ | Company ID (required) |
| `rep_id` | query | string |  | Filter by rep ID (from metadata.rep_id) |
| `status` | query | string |  | Filter by call status |
| `from_date` | query | string |  | Filter calls from this date |
| `to_date` | query | string |  | Filter calls until this date |
| `min_compliance_score` | query | string |  | Minimum compliance score |
| `max_compliance_score` | query | string |  | Maximum compliance score |
| `limit` | query | integer |  | Results per page |
| `offset` | query | integer |  | Pagination offset |
| `sort_by` | query | string |  | Sort field: created_at, compliance_score |
| `sort_order` | query | string |  | Sort order: asc, desc |

**Response `200`:** Successful Response
- `application/json` → `CallSummariesListResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `GET` /api/v1/call-processing/summary/{call_id}

**Get Call Summary**
> Get the summary for a processed call.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `call_id` | path | string | ✅ |  |
| `include_chunks` | query | boolean |  |  |

**Response `200`:** Successful Response
- `application/json` → `CallSummaryResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`


## Coaching

### `GET` /api/v1/coaching/coaches/{coach_id}/effectiveness

**Get Coach Effectiveness**
> Get coach effectiveness metrics (per Q23). Cache is updated by the weekly job and when sessions are completed.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `coach_id` | path | string | ✅ | Coach ID |
| `company_id` | query | string | ✅ | Company ID |
| `timeframe_days` | query | integer |  | Analysis timeframe |
| `use_cached` | query | boolean |  | If true, return from coach_effectiveness cache when available (within 8 days) |

**Response `200`:** Successful Response
- `application/json` → `CoachEffectivenessResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `GET` /api/v1/coaching/reps

**List Reps**
> List all reps (agents) with calls for a company.

Returns the ``rep_id`` values that should be used when querying
the ``/reps/{rep_id}/profile`` and ``/reps/{rep_id}/top3`` endpoints.

The ``rep_id`` 

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `company_id` | query | string | ✅ | Company ID |

**Response `200`:** Successful Response
- `application/json` → `RepListResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `GET` /api/v1/coaching/reps/{rep_id}/profile

**Get Rep Coaching Profile**
> Get the full aggregated coaching profile for a rep.

Returns all coaching insights bucketed into canonical categories with
counts, severity distributions, and representative examples. Includes
the top

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `rep_id` | path | string | ✅ | Rep ID |
| `company_id` | query | string | ✅ | Company ID |
| `force_refresh` | query | boolean |  | Force rebuild even if cached |
| `window_days` | query | integer |  | Time window in days |

**Response `200`:** Successful Response
- `application/json` → `RepCoachingProfileResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `GET` /api/v1/coaching/reps/{rep_id}/top3

**Get Rep Top3**
> Get the top-3 most frequent coaching strengths and weaknesses for a rep.

Lightweight endpoint suitable for dashboards and session creation flows.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `rep_id` | path | string | ✅ | Rep ID |
| `company_id` | query | string | ✅ | Company ID |

**Response `200`:** Successful Response
- `application/json` → `RepTop3Response`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `GET` /api/v1/coaching/roi

**Get Coaching Roi**
> Get company-wide coaching ROI metrics (per Q24).

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `company_id` | query | string | ✅ | Company ID |
| `timeframe_days` | query | integer |  | Analysis timeframe |

**Response `200`:** Successful Response
- `application/json` → `CoachingROIResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `POST` /api/v1/coaching/sessions

**Create Coaching Session**
> Log a new coaching session.

Creates a coaching session with:
- Auto-calculated baseline from rep's recent calls
- Manager-defined improvement targets
- Follow-up period tracking (default 2 weeks)

**Request Body (`application/json`):** `CreateCoachingSessionRequest`

**Response `201`:** Successful Response
- `application/json` → `CoachingSessionResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `GET` /api/v1/coaching/sessions

**List Sessions**
> List coaching sessions with filters.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `company_id` | query | string | ✅ | Company ID |
| `rep_id` | query | string |  | Filter by rep |
| `coach_id` | query | string |  | Filter by coach |
| `status` | query | string |  | Filter by status |
| `limit` | query | integer |  |  |
| `offset` | query | integer |  |  |

**Response `200`:** Successful Response
- `application/json` → `SessionsListResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `GET` /api/v1/coaching/sessions/{session_id}

**Get Session**
> Get coaching session details including impact.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `session_id` | path | string | ✅ | Coaching session ID |

**Response `200`:** Successful Response
- `application/json` → `CoachingSessionResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `GET` /api/v1/coaching/sessions/{session_id}/impact

**Get Impact Report**
> Get detailed impact report for a coaching session.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `session_id` | path | string | ✅ | Coaching session ID |

**Response `200`:** Successful Response
- `application/json` → `CoachingImpactResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `PATCH` /api/v1/coaching/sessions/{session_id}/status

**Update Session Status**
> Update coaching session status.

Use this endpoint to:
- Manually complete a session (status='completed')
- Extend the follow-up period (status='extended')
- Mark as insufficient data (status='insuffi

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `session_id` | path | string | ✅ | Coaching session ID |

**Request Body (`application/json`):** `UpdateSessionStatusRequest`

**Response `200`:** Successful Response
- `application/json` → `UpdateSessionStatusResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`


## Insights

### `GET` /api/v1/insights/agents/summary

**Get Agents Summary**
> Get summary of all agents for manager dashboard.

Returns high-level metrics for each agent:
- Total calls
- Average compliance
- Booking rate
- Overall trend
- Any alerts

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `company_id` | query | string | ✅ | Company ID |
| `weeks` | query | integer |  | Analysis period in weeks |

**Response `200`:** Successful Response
- `application/json` → `AgentsSummaryResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `GET` /api/v1/insights/agents/{rep_id}/peer-comparison

**Get Peer Comparison**
> On-demand peer comparison (per Q45-Q46).

Compares rep's score to all peers in same company.
Returns ranking, percentile, and distribution stats.

Note: Per manager decision, this is NOT shown by defa

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `rep_id` | path | string | ✅ | Representative ID |
| `company_id` | query | string | ✅ | Company ID |
| `metric` | query | string |  | Metric to compare |
| `days` | query | integer |  | Analysis period in days |

**Response `200`:** Successful Response
- `application/json` → `PeerComparisonResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `GET` /api/v1/insights/agents/{rep_id}/progression

**Get Agent Progression**
> Get agent behavior progression over time (per Q37-Q48).

Tracks weekly metrics and detects:
- Trends (improving/stable/declining - 5% threshold)
- Anomalies (>20% sudden change)

Returns low-confidenc

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `rep_id` | path | string | ✅ | Representative ID |
| `company_id` | query | string | ✅ | Company ID |
| `metrics` | query | string |  | Comma-separated metrics |
| `weeks` | query | integer |  | Number of weeks to analyze |

**Response `200`:** Successful Response
- `application/json` → `AgentProgressionResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `GET` /api/v1/insights/company/{company_id}/current

**Get Current Company Insight**
> Get the most recent company insight.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `company_id` | path | string | ✅ | Company ID (UUID format) |

**Response `200`:** Successful Response
- `application/json` → `CompanyInsightResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `GET` /api/v1/insights/customers

**Get Customers Insights**
> Get customer insights list.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `company_id` | query | string | ✅ | Company ID (UUID format) |
| `week_start` | query | string |  |  |
| `status` | query | string |  |  |
| `priority` | query | string |  |  |
| `page` | query | integer |  |  |
| `limit` | query | integer |  |  |

**Response `200`:** Successful Response
- `application/json` → `CustomersInsightsResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `POST` /api/v1/insights/generate

**Generate Insights**
> Trigger weekly insights generation.

Designed to be called by external cron jobs.
Background processing happens asynchronously.

**Request Body (`application/json`):** `GenerateInsightsRequest`

**Response `202`:** Successful Response
- `application/json` → `GenerateInsightsResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `GET` /api/v1/insights/leads

**Get Leads**
> Get leads with optional filtering by band and score.

Returns leads from call_summaries where lead_score is present.
Sorted by lead score descending (hottest first).

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `company_id` | query | string | ✅ | Company ID (UUID format) |
| `band` | query | string |  | Filter by lead band: hot, warm, cold |
| `min_score` | query | string |  | Minimum lead score |
| `max_score` | query | string |  | Maximum lead score |
| `timeframe_days` | query | integer |  | Timeframe in days |
| `page` | query | integer |  |  |
| `limit` | query | integer |  |  |

**Response `200`:** Successful Response
- `application/json` → `LeadListResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `GET` /api/v1/insights/leads/distribution

**Get Lead Distribution**
> Get lead score distribution statistics.

Returns counts per band and percentile breakdown.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `company_id` | query | string | ✅ | Company ID (UUID format) |
| `timeframe_days` | query | integer |  | Timeframe in days |

**Response `200`:** Successful Response
- `application/json` → `LeadDistributionResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `GET` /api/v1/insights/leads/{customer_id}/history

**Get Lead Score History**
> Get lead score changes over time for a customer.

Supports dynamic recalculation tracking (per Q31).
Customer can be identified by customer_id or phone number.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `customer_id` | path | string | ✅ | Customer ID or phone number |
| `company_id` | query | string | ✅ | Company ID (UUID format) |
| `limit` | query | integer |  | Max history entries |

**Response `200`:** Successful Response
- `application/json` → `LeadScoreHistoryResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `GET` /api/v1/insights/objections/{company_id}

**Get Objection Insights**
> Get objection insights for a company.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `company_id` | path | string | ✅ | Company ID (UUID format) |
| `week_start` | query | string |  |  |
| `category_id` | query | string |  |  |
| `rep_role` | query | string |  | Filter by rep role: 'customer_rep' or 'sales_rep' |

**Response `200`:** Successful Response
- `application/json` → `ObjectionInsightResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `GET` /api/v1/insights/status/{job_id}

**Get Insight Status**
> Get the status of an insight generation job.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `job_id` | path | string | ✅ |  |

**Response `200`:** Successful Response
- `application/json` → `InsightJobStatusResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`


## Queue Admin

### `POST` /api/v1/queue/clear

**Clear Queue**
> Clear waiting call-processing queue records.

This does not stop jobs that have already been picked up by a worker.

**Request Body (`application/json`):** `ClearQueueRequest`

**Response `200`:** Successful Response
- `application/json` → inline

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `GET` /api/v1/queue/status

**Get Queue Status**
> Show Kafka queue lag, Redis job states, and stale processing jobs.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `stale_after_seconds` | query | integer |  |  |
| `limit` | query | integer |  |  |

**Response `200`:** Successful Response
- `application/json` → inline

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`


## Status

### `GET` /api/v1/scheduler/status

**Scheduler Status**
> Get the status of the background scheduler and its jobs.

**Response `200`:** Successful Response
- `application/json` → inline

### `GET` /api/v1/status

**Api Status**
> API status endpoint

**Response `200`:** Successful Response
- `application/json` → inline


## SOP Document Ingestion

### `GET` /api/v1/sop/documents

**List Sop Documents**
> List SOP documents for a company.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `company_id` | query | string | ✅ |  |
| `status` | query | string |  |  |
| `target_role` | query | string |  |  |
| `page` | query | integer |  |  |
| `limit` | query | integer |  |  |

**Response `200`:** Successful Response
- `application/json` → `SOPListResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `GET` /api/v1/sop/documents/status/{job_id}

**Get Sop Processing Status**
> Get SOP processing status.

Poll this endpoint to check progress.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `job_id` | path | string | ✅ |  |

**Response `200`:** Successful Response
- `application/json` → `SOPStatusResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `POST` /api/v1/sop/documents/upload

**Upload Sop Document**
> Upload SOP document for processing.

Supports two methods:
1. Direct file upload: Provide 'file' parameter with actual file (use -F 'file=@/path/to/file.pdf')
2. URL download: Provide 'file_url' param

**Request Body (`multipart/form-data`):** `Body_upload_sop_document_api_v1_sop_documents_upload_post`

**Response `202`:** Successful Response
- `application/json` → `SOPUploadResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `GET` /api/v1/sop/documents/{sop_id}

**Get Sop Document**
> Get SOP document details.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `sop_id` | path | string | ✅ | SOP ID (string or UUID) |

**Response `200`:** Successful Response
- `application/json` → `SOPDocumentResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `DELETE` /api/v1/sop/documents/{sop_id}

**Delete Sop Document**
> Delete SOP document and all associated data.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `sop_id` | path | string | ✅ | SOP ID (string or UUID) |

**Response `204`:** Successful Response

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `POST` /api/v1/sop/documents/{sop_id}/reanalyze

**Trigger Reanalysis**
> Trigger manual re-analysis of calls with current SOP version (per Q5-Q7).

- Re-analyzes ALL calls in lookback period (Q7)
- Default lookback: 14 days (Q6)
- Stores both original and new evaluations (

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `sop_id` | path | string | ✅ | SOP ID |
| `lookback_days` | query | integer |  |  |

**Request Body (`application/x-www-form-urlencoded`):** `Body_trigger_reanalysis_api_v1_sop_documents__sop_id__reanalyze_post`

**Response `200`:** Successful Response
- `application/json` → `ReanalysisJobResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `PATCH` /api/v1/sop/documents/{sop_id}/status

**Update Sop Status**
> Update SOP document status (activate/deactivate).

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `sop_id` | path | string | ✅ | SOP ID (string or UUID) |

**Request Body (`application/json`):** `SOPStatusUpdateRequest`

**Response `200`:** Successful Response
- `application/json` → `SOPStatusUpdateResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `POST` /api/v1/sop/documents/{sop_id}/versions

**Upload New Version**
> Upload new version of existing SOP (per Q1-Q4).

- Automatically archives current version (Q2)
- Auto-increments version number (Q1)
- Supports scheduled activation (Q4)

Supports file upload or URL d

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `sop_id` | path | string | ✅ | SOP ID |

**Request Body (`multipart/form-data`):** inline schema

**Response `202`:** Successful Response
- `application/json` → inline

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `GET` /api/v1/sop/documents/{sop_id}/versions

**Get Version History**
> Get all versions of an SOP.

Returns version history sorted by version number descending.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `sop_id` | path | string | ✅ | SOP ID |
| `include_archived` | query | boolean |  |  |

**Response `200`:** Successful Response
- `application/json` → `SOPVersionHistoryResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `GET` /api/v1/sop/documents/{sop_id}/versions/{version}

**Get Specific Version**
> Get specific version details including metrics snapshot.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `sop_id` | path | string | ✅ | SOP ID |
| `version` | path | integer | ✅ | Version number |

**Response `200`:** Successful Response
- `application/json` → inline

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `GET` /api/v1/sop/metrics/{company_id}

**Get Company Sop Metrics**
> Get active SOP metrics for a company.

Returns role-specific and company-wide SOPs.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `company_id` | path | string | ✅ | Company ID (UUID format) |
| `role` | query | string |  |  |
| `sop_id` | query | string |  |  |

**Response `200`:** Successful Response
- `application/json` → `CompanySOPMetricsResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `GET` /api/v1/sop/reanalysis/{job_id}

**Get Reanalysis Results**
> Get re-analysis job status and results.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `job_id` | path | string | ✅ | Reanalysis job ID |

**Response `200`:** Successful Response
- `application/json` → `ReanalysisResultsResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`


## Tenant Configuration

### `POST` /api/v1/tenant-config/

**Create Tenant Config**
> Create a new tenant configuration.

This creates a custom configuration for a company/tenant that controls
how their calls are processed, including qualification rules, service
priorities, and custom 

**Request Body (`application/json`):** `TenantConfigCreateRequest`

**Response `201`:** Successful Response
- `application/json` → `TenantConfigResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `GET` /api/v1/tenant-config/{company_id}

**Get Tenant Config**
> Get tenant configuration.

Returns the configuration for the specified company, or a default
configuration if none exists.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `company_id` | path | string | ✅ | Company ID (UUID format) |

**Response `200`:** Successful Response
- `application/json` → `TenantConfigResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `PUT` /api/v1/tenant-config/{company_id}

**Update Tenant Config**
> Update tenant configuration.

Updates only the provided fields. Previous versions are archived
for rollback capability.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `company_id` | path | string | ✅ | Company ID (UUID format) |

**Request Body (`application/json`):** `TenantConfigUpdateRequest`

**Response `200`:** Successful Response
- `application/json` → `TenantConfigResponse`

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `DELETE` /api/v1/tenant-config/{company_id}

**Delete Tenant Config**
> Delete tenant configuration (soft delete).

Marks the configuration as inactive. The company will use default
configuration after deletion.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `company_id` | path | string | ✅ | Company ID (UUID format) |

**Response `200`:** Successful Response
- `application/json` → inline

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `GET` /api/v1/tenant-config/{company_id}/history

**Get Config History**
> Get configuration version history.

Returns the history of configuration changes for rollback review.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `company_id` | path | string | ✅ | Company ID (UUID format) |
| `limit` | query | integer |  |  |

**Response `200`:** Successful Response
- `application/json` → inline

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `POST` /api/v1/tenant-config/{company_id}/rollback/{version}

**Rollback Config**
> Rollback configuration to a previous version.

Restores the configuration to the specified version number.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `company_id` | path | string | ✅ | Company ID (UUID format) |
| `version` | path | integer | ✅ | Version number to rollback to |

**Response `200`:** Successful Response
- `application/json` → inline

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `POST` /api/v1/tenant-config/{company_id}/rules

**Add Qualification Rule**
> Add a new qualification rule to the tenant configuration.

Rules are evaluated in priority order during call processing.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `company_id` | path | string | ✅ | Company ID (UUID format) |

**Request Body (`application/json`):** `QualificationRuleRequest`

**Response `201`:** Successful Response
- `application/json` → inline

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`

### `POST` /api/v1/tenant-config/{company_id}/services

**Add Service Config**
> Add a new service configuration to the tenant.

Services control prioritization and scoring adjustments.

**Parameters:**
| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `company_id` | path | string | ✅ | Company ID (UUID format) |

**Request Body (`application/json`):** `ServiceConfigRequest`

**Response `201`:** Successful Response
- `application/json` → inline

**Response `422`:** Validation Error
- `application/json` → `HTTPValidationError`


## Health

### `GET` /health

**Health Check**
> Health check endpoint with dependency status

**Response `200`:** Successful Response
- `application/json` → inline


## Key Schemas

### CallSummaryResponse

| Field | Type | Required | Description |
|---|---|---|---|
| `call_id` | string | ✅ |  |
| `company_id` | string | ✅ |  |
| `status` | string | ✅ |  |
| `processed_at` | string | ✅ |  |
| `summary` | `SummaryData` | ✅ |  |
| `compliance` | `ComplianceData` | ✅ |  |
| `objections` | `ObjectionsData` | ✅ |  |
| `qualification` | `QualificationData` | ✅ |  |

### Objection

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | object |  |  |
| `category_id` | integer | ✅ | Objection category ID (1-15 for CSR, 1-14 for sales rep) |
| `category_text` | string | ✅ | Category name |
| `sub_objection` | object |  | Specific objection type when category is 'Other' (category_id=13 for CSR, 14 for sales rep) |
| `objection_text` | string | ✅ | The actual objection |
| `overcome` | boolean |  | Was the objection overcome |
| `speaker_id` | object |  |  |
| `timestamp` | object |  |  |
| `confidence_score` | number | ✅ |  |
| `severity` | object |  |  |
| `response_suggestions` | array |  |  |
| `created_at` | object |  |  |

### SOPCompliance

| Field | Type | Required | Description |
|---|---|---|---|
| `score` | number | ✅ |  |
| `compliance_rate` | number | ✅ |  |
| `stages` | object |  |  |
| `issues` | array |  |  |
| `positive_behaviors` | array |  |  |
| `coaching_issues` | array[`ComplianceIssueDetail`] |  |  |
| `coaching_strengths` | array[`ComplianceStrengthDetail`] |  |  |
| `confidence` | number | ✅ |  |

### BANTScores

| Field | Type | Required | Description |
|---|---|---|---|
| `need` | number | ✅ | Need score |
| `budget` | number | ✅ | Budget score |
| `timeline` | number | ✅ | Timeline score |
| `authority` | number | ✅ | Authority score |

### PendingAction

| Field | Type | Required | Description |
|---|---|---|---|
| `type` | `ActionType` | ✅ |  |
| `action_item` | string |  | Clear, actionable description of what needs to be done |
| `owner` | string | ✅ | Who should complete this action |
| `due_at` | object |  |  |
| `raw_text` | string | ✅ | Original text from transcript mentioning the action |
| `confidence` | number | ✅ |  |
| `contact_method` | object |  |  |
| `category` | object |  | Classification category from INCLUDE framework |
