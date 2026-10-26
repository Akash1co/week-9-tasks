# CIA Career Intelligence API Contract

This document describes the authenticated career-intelligence endpoints. All
paths are relative to the application origin. The route implementations are
placeholders; request validation, persistence, and authorization beyond the
`auth` middleware must be implemented before production use.

## Conventions

- Base path: `/cia/career`
- Content type: `application/json`
- Protected routes require an authenticated application session.
- Send `Accept: application/json` on all requests. Send
  `Content-Type: application/json` when a request has a JSON body.
- IDs are opaque strings. The examples use UUID-like values.
- Error responses have the common shape shown under [Errors](#errors).

### Common headers

| Header | Required | Description |
| --- | --- | --- |
| `Accept` | Yes | `application/json` |
| `Content-Type` | For JSON bodies | `application/json` |
| `Authorization` | Depends on configured auth guard | Send credentials using the application's configured authorization scheme |
| Session cookie and CSRF token | Depends on configured auth guard | Required when using cookie-based authentication for state-changing requests |

## 1. Career dashboard

`GET /cia/career/dashboard`  
Route name: `cia.career.dashboard`

Returns overview metrics for the authenticated user's career-intelligence
workspace.

### Request

No request body or query parameters.

### `200 OK`

```json
{
  "candidate_count": 128,
  "profile_completion_rate": 0.84,
  "average_readiness_score": 76.5,
  "recent_activity": [
    {
      "type": "profile_updated",
      "candidate_id": "cand-1042",
      "occurred_at": "2026-10-26T12:00:00Z"
    }
  ]
}
```

Response schema:

```json
{
  "candidate_count": "integer >= 0",
  "profile_completion_rate": "number between 0 and 1",
  "average_readiness_score": "number between 0 and 100",
  "recent_activity": [
    {
      "type": "string",
      "candidate_id": "string",
      "occurred_at": "ISO-8601 datetime"
    }
  ]
}
```

## 2. Get a candidate profile

`GET /cia/career/profiles/{candidate_id}`  
Route name: `cia.career.profiles.show`

### Path parameters

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `candidate_id` | string | Yes | Candidate identifier |

### Request

No request body.

### `200 OK`

```json
{
  "candidate_id": "cand-1042",
  "name": "Jordan Lee",
  "email": "jordan@example.com",
  "skills": ["Python", "Data Analysis"],
  "scores": {
    "readiness": 82.5,
    "technical": 88
  },
  "history": [
    {
      "event": "assessment_completed",
      "occurred_at": "2026-10-20T09:30:00Z"
    }
  ],
  "created_at": "2026-10-01T10:00:00Z",
  "updated_at": "2026-10-20T09:30:00Z"
}
```

Response schema:

```json
{
  "candidate_id": "string",
  "name": "string",
  "email": "string (email address)",
  "skills": ["string"],
  "scores": {
    "<score_name>": "number"
  },
  "history": [
    {
      "event": "string",
      "occurred_at": "ISO-8601 datetime",
      "details": "object (optional)"
    }
  ],
  "created_at": "ISO-8601 datetime",
  "updated_at": "ISO-8601 datetime"
}
```

## 3. Create a candidate profile

`POST /cia/career/profiles`  
Route name: `cia.career.profiles.store`

### Request headers

Use the common headers and include `Content-Type: application/json`.

### Request body

```json
{
  "name": "Jordan Lee",
  "email": "jordan@example.com",
  "skills": ["Python", "Data Analysis"],
  "scores": {
    "readiness": 82.5
  },
  "history": []
}
```

Request schema:

```json
{
  "name": "string, required, non-empty",
  "email": "string, required, valid email address",
  "skills": ["string"],
  "scores": {
    "<score_name>": "number"
  },
  "history": [
    {
      "event": "string",
      "occurred_at": "ISO-8601 datetime",
      "details": "object (optional)"
    }
  ]
}
```

`skills`, `scores`, and `history` are optional and default to empty values.

### `201 Created`

```json
{
  "candidate_id": "cand-1043",
  "name": "Jordan Lee",
  "email": "jordan@example.com",
  "skills": ["Python", "Data Analysis"],
  "scores": {
    "readiness": 82.5
  },
  "history": [],
  "created_at": "2026-10-26T12:00:00Z",
  "updated_at": "2026-10-26T12:00:00Z"
}
```

## 4. Update candidate skills

`PUT /cia/career/profiles/{candidate_id}/skills`  
Route name: `cia.career.profiles.update_skills`

### Path parameters

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `candidate_id` | string | Yes | Candidate identifier |

### Request headers

Use the common headers and include `Content-Type: application/json`.

### Request body

```json
{
  "skills": ["Python", "Data Analysis", "Machine Learning"]
}
```

Request schema:

```json
{
  "skills": ["string, required"]
}
```

The `skills` array may be empty to clear the candidate's skills.

### `200 OK`

```json
{
  "candidate_id": "cand-1042",
  "skills": ["Python", "Data Analysis", "Machine Learning"],
  "updated_at": "2026-10-26T12:05:00Z"
}
```

## 5. Get candidate recommendations

`GET /cia/career/recommendations/{candidate_id}`  
Route name: `cia.career.recommendations`

### Path parameters

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `candidate_id` | string | Yes | Candidate identifier |

### Request

No request body or query parameters.

### `200 OK`

```json
{
  "candidate_id": "cand-1042",
  "recommendations": [
    {
      "type": "role",
      "title": "Data Analyst",
      "score": 0.91,
      "reason": "Strong alignment with the candidate's data analysis skills."
    }
  ]
}
```

Response schema:

```json
{
  "candidate_id": "string",
  "recommendations": [
    {
      "type": "string",
      "title": "string",
      "score": "number between 0 and 1",
      "reason": "string"
    }
  ]
}
```

## 6. Search profiles by vector similarity

`POST /cia/career/vector-search`  
Route name: `cia.career.vector_search`

### Request headers

Use the common headers and include `Content-Type: application/json`.

### Request body

```json
{
  "query": "Candidates experienced in Python and analytics",
  "limit": 10,
  "filters": {
    "skills": ["Python"]
  }
}
```

Request schema:

```json
{
  "query": "string, required, non-empty",
  "limit": "integer, optional, 1 through 100; default 10",
  "filters": {
    "skills": ["string, optional"]
  }
}
```

### `200 OK`

```json
{
  "query": "Candidates experienced in Python and analytics",
  "results": [
    {
      "candidate_id": "cand-1042",
      "similarity": 0.93,
      "profile": {
        "name": "Jordan Lee",
        "skills": ["Python", "Data Analysis"]
      }
    }
  ]
}
```

Response schema:

```json
{
  "query": "string",
  "results": [
    {
      "candidate_id": "string",
      "similarity": "number between 0 and 1",
      "profile": {
        "name": "string",
        "skills": ["string"]
      }
    }
  ]
}
```

An empty `results` array means no matching profiles were found.

## 7. Career analytics

`GET /cia/career/analytics`  
Route name: `cia.career.analytics`

### Request

No request body or query parameters.

### `200 OK`

```json
{
  "total_candidates": 128,
  "skill_distribution": [
    {
      "skill": "Python",
      "candidate_count": 64
    }
  ],
  "readiness_distribution": {
    "average": 76.5,
    "median": 79,
    "by_band": {
      "high": 42,
      "medium": 61,
      "low": 25
    }
  }
}
```

Response schema:

```json
{
  "total_candidates": "integer >= 0",
  "skill_distribution": [
    {
      "skill": "string",
      "candidate_count": "integer >= 0"
    }
  ],
  "readiness_distribution": {
    "average": "number",
    "median": "number",
    "by_band": {
      "<band_name>": "integer >= 0"
    }
  }
}
```

## Errors

The following error responses apply to all seven routes.

### `400 Bad Request`

Returned when the request body is malformed or fails validation.

```json
{
  "error": {
    "code": "BAD_REQUEST",
    "message": "The request is invalid.",
    "details": {
      "skills": ["The skills field must be an array of strings."]
    }
  }
}
```

`details` may be omitted when there are no field-specific validation errors.

### `401 Unauthorized`

Returned when the request is not authenticated.

```json
{
  "error": {
    "code": "UNAUTHENTICATED",
    "message": "Authentication is required."
  }
}
```

### `404 Not Found`

Returned when a requested candidate does not exist.

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "The requested candidate was not found."
  }
}
```

For a request to a valid endpoint path that does not exist, the application may
also return this status using its standard not-found response.
