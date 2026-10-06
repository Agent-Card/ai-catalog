# ADR-0029: Define the Policy URLs Extension

**Status:** Proposed

**Date:** 2026-10-05

## Context

Privacy-policy and terms-of-service URLs describe policies governing an
artifact. They have a common display purpose, but they are not themselves
artifact-integrity evidence. Keeping them on the entry provides one place
to find them when an entry contains several contributors' Trust Manifests.

## Decision

Replace the core entry fields `privacyPolicyUrl` and `termsOfServiceUrl`
with one official entry extension:

```json
{
  "extensions": {
    "https://ai-catalog.org/extensions/policy-urls": {
      "privacyPolicyUrl": "https://example.com/privacy",
      "termsOfServiceUrl": "https://example.com/terms"
    }
  }
}
```

Both members are optional strings containing URLs, retaining the existing
fields' URL requirements and meanings. These are the policies governing
the artifact, not the catalog operator's own service policies.

Either a publisher or catalog operator may populate the extension. A Trust
Manifest signature does not authenticate its value. A catalog signature
covers it as part of the complete catalog snapshot; acceptance still
requires applicable signer authorization.

## Rationale

An official extension provides a predictable location for common metadata
without giving policy links a special signing mechanism. Contributor
authentication of entry extensions remains future work.

## Consequences

- Consumers must read the official extension instead of the former core
  entry fields.
- A verified publisher artifact endorsement may coexist with policy links
  that the publisher has not authenticated. Consumers must distinguish
  those assurances.
- A catalog signature authenticates the links as part of its signer's
  snapshot; it does not by itself establish publisher endorsement of those links.
- Signing a URL authenticates the reference, not the contents of a policy
  document that can change at that URL.
