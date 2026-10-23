# Threat model

- Workspace header is a development-only context boundary; production requires authenticated identity and server-side membership checks.
- Document retrieval filters strictly by workspace and treats documents as untrusted text.
- Uploads allow only TXT/CSV in local mode and are limited to 5 MiB.
- Analytics SQL permits a single `SELECT`/`WITH` statement and rejects mutations. Database read-only roles remain mandatory defense in depth.
- Reports label trends as observations and do not infer causation.

