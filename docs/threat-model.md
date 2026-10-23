# Threat Model & Security Architecture

BizIntel AI operates in high-trust business analytics environments where proprietary financial ledgers, customer records, and operational documents reside. Security and reliability protections are enforced across every tier.

---

## 1. Threat Vectors & Defense Matrix

| Threat Category | Potential Impact | Implemented Mitigation | Verification Status |
| :--- | :--- | :--- | :--- |
| **Cross-Workspace Data Leakage** | Tenant A accesses Tenant B's financial documents or query results | Strict workspace ownership enforced in database queries, `workspace_id` foreign keys, and route guards. | Verified in `test_cross_workspace_isolation` (0 leaks) |
| **SQL Injection & Schema Mutation** | Attackers execute `DROP TABLE`, `UPDATE`, or exfiltrate credentials | Tokenizing AST parser rejects mutations, semicolons, comments, and unapproved tables; read-only role defense in depth; parameterization. | Verified in `test_sql_validation.py` (0 mutations permitted) |
| **Indirect Prompt Injection** | Ingested PDF/DOCX files contain hidden instructions overriding model governance | `sanitize_retrieved_text` neutralizes system delimiters (`<|im_start|>`, `<<SYS>>`), role spoofing, and override commands (`ignore previous instructions`). | Verified in `test_prompt_injection_sanitization` |
| **Agent Runaway / Infinite Loops** | Agents loop endlessly consuming resources | Bounded shared state with `max_tool_calls = 10` and `max_agent_steps = 12`; explicit step termination. | Verified in `test_supervisor.py` |
| **Secret Exfiltration in Traces** | API keys or passwords logged in OpenTelemetry spans | Sanitized parameter serialization; passwords hashed with scrypt + salt; full database results excluded from traces. | Verified in `TraceViewer` & `test_full_api.py` |
| **Denial of Service (DoS) via File Upload** | Giant uploads crashing the server | Strict 5 MiB file size enforcement, format validation (PDF, DOCX, TXT, MD, CSV, XLSX), memory-safe chunking. | Verified in `test_ingestion_rejects_unsupported_type` |
| **Hallucinated Causation & Advice** | Agents invent business causes without empirical data | Strict separation between verified metrics, qualitative facts, hypotheses, and recommendations; citation validity checks. | Verified in `test_supervisor.py` (Citation validity 100%) |

---

## 2. Authentication & Session Lifecycle

- **Password Storage**: Passwords hashed using `scrypt` with random 16-byte cryptographically secure salts (`N=16384, r=8, p=1`). Plaintext passwords are never persisted.
- **Session Tokens**: Opaque 32-byte URL-safe cryptographic tokens (`secrets.token_urlsafe(32)`). Only the SHA-256 hash of the session token is stored in the database (`auth_sessions`).
- **Workspace Authorization**: All resource queries verify that the authenticated user holds membership in the target workspace via `require_membership`.

---

## 3. Data Minimization & Privacy

- Full database query results are never passed into model generation prompts.
- Aggregated numbers and calculated metrics only are provided to the agent synthesis layer.
- Retained traces record tool names and execution duration, omitting raw customer data.
