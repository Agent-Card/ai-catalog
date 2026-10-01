# ADR-0007: Keep `url` Field Name Over `href`

**Status:** Accepted

**Date:** 2026-04-02

**Participants:** Darrel Miller (Microsoft), Junjie Bu (Google)

## Context

Darrel Miller raised the naming question: "Does anybody have a strong
preference between URL and href?" noting that `url` is "technically less
correct" since the value could be a relative reference (which would make
it a URI reference, not strictly a URL).

## Decision

Use `url` as the field name.

## Rationale

- Junjie Bu expressed preference for `url`: "URL sounds better to me."
- `url` is the more widely recognized term among developers and appears
  in most JSON-based specifications (A2A, MCP, OpenAPI).
- `href` carries HTML/hypermedia connotations that may confuse API-first
  audiences.
- The technical distinction between URL and URI reference is unlikely
  to matter in practice, as catalog entries will overwhelmingly use
  absolute URLs.
- Darrel acknowledged the pragmatic choice: "that's technically less
  correct, but okay."

## Consequences

- The field is named `url` across all objects (catalog entries,
  collection references, attestations).
- Values MAY be relative URI references, despite the field name, though
  absolute URLs are RECOMMENDED.

## Update (2026-07)

The spec has since split naming by intent, and the split is deliberate:

- `url`-suffixed fields (`url`, `documentationUrl`, `logoUrl`,
  `privacyPolicyUrl`, `termsOfServiceUrl`) hold fetchable HTTP(S)
  resources.
- `uri`-suffixed fields (attestation `uri`, `governanceUri`,
  `registryUri`, `statementUri`) allow non-HTTP schemes or values that
  serve as identifiers rather than fetchable locations (e.g. `oci://`
  references).
