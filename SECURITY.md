# Security Design Document

This document describes the security architecture of mcp-google-search-console-crunchtools.

## 1. Threat Model

### 1.1 Assets to Protect

| Asset | Sensitivity | Impact if Compromised |
|-------|-------------|----------------------|
| OAuth Client Secret | Critical | Can impersonate the application |
| OAuth Refresh Token | Critical | Full account access to Search Console |
| Access Token | High | Temporary API access (1 hour) |
| Search Analytics Data | Medium | Competitive intelligence exposure |
| URL Index Status | Low | Site structure disclosure |

### 1.2 Threat Actors

| Actor | Capability | Motivation |
|-------|------------|------------|
| Malicious AI Agent | Can craft tool inputs | Data exfiltration |
| Local Attacker | Access to filesystem | Token theft |
| Network Attacker | Man-in-the-middle | Token interception (mitigated by TLS) |

### 1.3 Attack Vectors

| Vector | Description | Mitigation |
|--------|-------------|------------|
| Token Leakage | Credentials exposed in logs or errors | SecretStr storage, error scrubbing |
| Input Injection | Malicious site URLs or query params | Pydantic validation, URL encoding |
| SSRF | Redirect API calls | Google API URLs only |
| Denial of Service | Exhaust API quotas | Rate limiting awareness |

## 2. Security Architecture

### 2.1 Defense in Depth Layers

```
Layer 1: Input Validation
- Pydantic models for all tool inputs
- Site URL format validation (regex)
- Reject unexpected fields (extra="forbid")
- Dimension and filter allowlists

Layer 2: Token Handling
- OAuth credentials as environment variables only
- Stored as SecretStr (never logged)
- Automatic scrubbing from error messages
- Bearer token in Authorization header (not URL)

Layer 3: API Client Hardening
- TLS certificate validation (httpx default)
- Request timeout enforcement (30s)
- Response size limits (10MB)
- Automatic token refresh with expiry tracking
- 401 retry with fresh token (once)

Layer 4: Output Sanitization
- Redact credentials from error messages
- Limit response sizes
- Structured errors without internal details

Layer 5: Runtime Protection
- No filesystem access
- No shell execution (subprocess)
- No dynamic code evaluation (eval/exec)
- Type-safe with Pydantic

Layer 6: Supply Chain Security
- Automated CVE scanning via GitHub Actions
- Container built on Hummingbird (minimal CVEs)
- Weekly dependency audits
```

### 2.2 OAuth2 Security

The OAuth2 flow uses refresh tokens for long-lived access:

- Client credentials and refresh token stored as `SecretStr`
- Access tokens cached in memory with expiry tracking
- Automatic refresh 60 seconds before expiry
- On 401, token is invalidated and refreshed once before failing
- Token endpoint uses HTTPS exclusively

### 2.3 Input Validation Rules

- Site URLs: Must match `https?://` or `sc-domain:` pattern
- Dimensions: Allowlist of 6 valid values
- Search types: Allowlist of 6 valid values
- Row limits: 1-25000 range enforced
- Extra fields: Rejected (Pydantic `extra="forbid"`)

## 3. Minimum Permission Scopes

### 3.1 Required OAuth Scope

```
https://www.googleapis.com/auth/webmasters
```

This grants full read/write access to Search Console properties.

### 3.2 Read-Only Alternative

```
https://www.googleapis.com/auth/webmasters.readonly
```

Use this scope if you only need to read data (list sites, query analytics, inspect URLs). Site and sitemap write operations will return permission errors.

## 4. Supply Chain Security

### 4.1 Automated CVE Scanning

1. Weekly scheduled scans (Monday 9 AM UTC)
2. PR checks before merge
3. Automatic issue creation for vulnerabilities
4. Dependabot enabled for security updates

### 4.2 Container Security

Built on Hummingbird Python (Red Hat UBI-based):
- Minimal CVE surface
- Non-root default
- Python optimized with uv

## 5. Reporting Security Issues

Report security vulnerabilities using [GitHub's private security advisory](https://github.com/crunchtools/mcp-google-search-console/security/advisories/new).

Do NOT open public issues for security vulnerabilities.
