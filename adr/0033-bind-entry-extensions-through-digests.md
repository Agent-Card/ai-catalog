# ADR-0033: Bind Entry Extensions Through Digests

**Status:** Proposed

**Date:** 2026-10-05

## Context

A Trust Manifest signature covers the manifest and its artifact subject,
but not metadata in `entry.extensions`. Contributors need a way to
authenticate selected entry extensions while allowing unrelated metadata
to be added or changed by catalog operators and federated registries.

## Decision

Add an optional `subject.extensionDigests` object. Each key is the exact
name of an extension in `entry.extensions`; its value is a digest string
using the specification's Digest Format.

For example, this entry excerpt selects one of its two extensions. Unrelated
entry and manifest fields are omitted, and the digest is a placeholder:

```json
{
  "extensions": {
    "com.example.capabilities": {
      "streaming": true
    },
    "com.example.registry": {
      "category": "tools"
    }
  },
  "trustManifests": [
    {
      "contributor": "did:web:publisher.example",
      "subject": {
        "extensionDigests": {
          "com.example.capabilities": "sha256:..."
        }
      }
    }
  ]
}
```

When signed, this manifest binds the complete `com.example.capabilities`
value. Updating `com.example.registry` does not affect that binding.

Compute each digest over the UTF-8 encoding of the JCS-canonicalized
complete extension value. No nested signature fields or other members are
excluded. The manifest signature authenticates both the extension keys and
their digests. An omitted or empty map selects no extensions.

When evaluating extension bindings, consumers MUST evaluate each
independently. Before treating an extension as authenticated, they MUST
verify its selected digest. A missing value, digest mismatch, unsupported
digest algorithm, or canonicalization failure prevents treating that
extension as authenticated; it does not invalidate the artifact binding or
other matching extension bindings.

When evaluating an extension's authentication, consumers distinguish these
outcomes:

| Situation | Meaning |
| --- | --- |
| The manifest selects the extension and its digest matches | The manifest authenticates that value, provided the manifest signature and artifact binding also verify. |
| The manifest selects the extension, but verification fails | The manifest does not authenticate the current value. A missing selected extension also fails verification. |
| The manifest does not select the extension | The manifest makes no authentication claim about that extension. |

An unselected extension is not a failed binding. Consumers need not evaluate
every extension, and a skipped check is not a failed check.

Keys are compared as decoded JSON strings, without URL normalization or
dereferencing.

## Application to Policy URLs

This mechanism also applies to the official policy-URL extension defined
in [ADR-0029](0029-define-the-policy-urls-extension.md). A contributor can
select its complete value through `subject.extensionDigests`, adding
per-contributor authentication to the shared metadata location established
there. Signing this extension is optional; no profile requires it.

## Rationale

A digest map avoids duplicating extension contents and reuses existing
canonicalization and digest rules. Whole-value selection is simpler than
nested paths. Independent verification avoids imposing dependencies between
otherwise unrelated claims and metadata.

## Consequences

- Changing any member of a selected extension changes its binding; changing
  an unselected extension does not.
- Selected values must satisfy JCS. Several manifests can independently
  authenticate the same extension.
- Authentication establishes the manifest signer's endorsement of the
  extension value. It does not establish who authored or added the extension,
  correctness, publisher authority, or support for the extension's semantics.
- A signature remains verified over the unchanged manifest, including any
  extension digests that failed to match the current entry.
- Trust Manifest extensions and catalog-root extensions need no equivalent
  map: they already participate in their containing object's signature.
