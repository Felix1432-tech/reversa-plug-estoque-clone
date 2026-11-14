# DPK stage 1 — isolated implementation

Scope: branch-only changes, no real DPK requests, no credentials, no deployment.

## Security
- Supabase access tokens validated via asymmetric JWKS (RS256/ES256), issuer, audience,
  expiry, issued-at, authenticated role, and UUID subject.
- Required runtime settings: SUPABASE_URL and optional SUPABASE_JWT_AUDIENCE.
- CORS_ALLOWED_ORIGINS is a comma-separated allowlist; default empty.
- Legacy X-User-ID header no longer authenticates a request.
- Keep API private until environment variables, database permissions and JWT tests are verified.

## Extraction
- API pre-creates one running log and passes its ID to the background runner.
- Starlette BackgroundTasks now receives the coroutine function, not an already-scheduled task.
- Missing SKUs are NOT marked unavailable from a potentially incomplete scrape.
- Concurrent extraction race still requires a database-level advisory lock or uniqueness mechanism.
- Full catalog reconciliation requires a separately proven complete snapshot.

## Normalizer
- Pure function in app/normalizers/dpk.py; no network calls.
- Accepts an adapter-owned sanitized dict, NOT an asserted DPK API schema.
- Distinguishes quantity=0 from quantity=null; identifies Campinas by name.
- Synthetic WK58 tests are placeholders; replace/add real sanitized fixtures once authorized.
- Not wired into DPKConnector or the frontend yet.

## Test command
From connector-service: python -m pytest -q tests/test_normalizers/test_dpk.py tests/test_api/test_auth.py

## Remaining work
- Verify Supabase JWKS settings, role/claims and frontend auth integration.
- Test API route and runner with DB mocks; add concurrency protection.
- Confirm real DPK payload contract and permitted integration method.
- Extend persistence and frontend API contract only after fixture validation.
