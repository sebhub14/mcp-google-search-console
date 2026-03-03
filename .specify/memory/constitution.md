# mcp-google-search-console-crunchtools Constitution

> **Version:** 1.0.0
> **Ratified:** 2026-03-03
> **Status:** Active

This constitution establishes the core principles, constraints, and workflows that govern all development on mcp-google-search-console-crunchtools.

---

## I. Core Principles

### 1. Five-Layer Security Model

Every change MUST preserve all five security layers. No exceptions.

**Layer 1 — Token Protection:**
- OAuth credentials stored as `SecretStr` (never logged or exposed)
- Environment-variable-only storage
- Automatic scrubbing from error messages

**Layer 2 — Input Validation:**
- Pydantic models enforce strict data types with `extra="forbid"`
- Allowlists for permitted values (dimensions, search types, operators)
- Site URLs validated against format patterns

**Layer 3 — API Hardening:**
- Auth via Bearer token in Authorization header (never in URL)
- Mandatory TLS certificate validation
- Request timeouts and response size limits
- URL-encoded path parameters

**Layer 4 — Dangerous Operation Prevention:**
- No filesystem access, shell execution, or code evaluation
- No `eval()`/`exec()` functions
- Tools are pure API wrappers with no side effects

**Layer 5 — Supply Chain Security:**
- Weekly automated CVE scanning via GitHub Actions
- Hummingbird container base images (minimal CVE surface)
- Gourmand AI slop detection gating all PRs

### 2. Two-Layer Tool Architecture

Tools follow a strict two-layer pattern:
- `server.py` — `@mcp.tool()` decorated functions that validate args and delegate
- `tools/*.py` — Pure async functions that call `client.py` HTTP methods

Never put business logic in `server.py`. Never put MCP registration in `tools/*.py`.

### 3. OAuth2 Token Management

The server uses OAuth2 refresh tokens for authentication:
- Refresh token exchanged for access token at runtime
- Access tokens cached with expiry tracking (60s buffer)
- Automatic refresh on 401 responses (once)
- Two base URLs: webmasters API and inspection API

### 4. Three Distribution Channels

Every release MUST be available through all three channels simultaneously:

| Channel | Command | Use Case |
|---------|---------|----------|
| uvx | `uvx mcp-google-search-console-crunchtools` | Zero-install, Claude Code |
| pip | `pip install mcp-google-search-console-crunchtools` | Virtual environments |
| Container | `podman run quay.io/crunchtools/mcp-google-search-console` | Isolated, systemd |

### 5. Three Transport Modes

The server MUST support all three MCP transports:
- **stdio** (default) — spawned per-session by Claude Code
- **SSE** — legacy HTTP transport
- **streamable-http** — production HTTP, systemd-managed containers

### 6. Semantic Versioning

Follow [Semantic Versioning 2.0.0](https://semver.org/) strictly.

---

## II. Technology Stack

| Layer | Technology | Version |
|-------|------------|---------|
| Language | Python | 3.10+ |
| MCP Framework | FastMCP | Latest |
| HTTP Client | httpx | Latest |
| Validation | Pydantic | v2 |
| Container Base | Hummingbird | Latest |
| Package Manager | uv | Latest |
| Build System | hatchling | Latest |
| Linter | ruff | Latest |
| Type Checker | mypy (strict) | Latest |
| Tests | pytest + pytest-asyncio | Latest |
| Slop Detector | gourmand | Latest |

---

## III. Testing Standards

### Mocked API Tests (MANDATORY)

Every tool MUST have a corresponding mocked test. Tests use `httpx.AsyncClient` mocking — no live API calls, no credentials required in CI.

### Input Validation Tests

Every Pydantic model in `models.py` MUST have tests in `test_validation.py`.

### Security Tests

- Token sanitization: `SearchConsoleApiError` MUST scrub credentials from messages
- URL truncation: `SiteNotFoundError` MUST truncate long identifiers
- Config safety: `repr()` and `str()` MUST never expose credentials

---

## IV. Code Quality Gates

Every code change must pass through these gates in order:

1. **Lint** — `uv run ruff check src tests`
2. **Type Check** — `uv run mypy src`
3. **Tests** — `uv run pytest -v` (all passing, mocked httpx)
4. **Gourmand** — `gourmand --full .` (zero violations)
5. **Container Build** — `podman build -f Containerfile .`

---

## V. Naming Conventions

| Context | Name |
|---------|------|
| GitHub repo | `crunchtools/mcp-google-search-console` |
| PyPI package | `mcp-google-search-console-crunchtools` |
| CLI command | `mcp-google-search-console-crunchtools` |
| Python module | `mcp_google_search_console_crunchtools` |
| Container image | `quay.io/crunchtools/mcp-google-search-console` |
| systemd service | `mcp-google-search-console.service` |
| HTTP port | 8017 |
| License | AGPL-3.0-or-later |

---

## VI. Governance

### Amendment Process

1. Create a PR with proposed changes to this constitution
2. Document rationale in PR description
3. Require maintainer approval
4. Update version number upon merge

### Ratification History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-03-03 | Initial constitution |
