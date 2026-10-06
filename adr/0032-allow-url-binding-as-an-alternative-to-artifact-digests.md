# ADR-0032: Allow URL Binding as an Alternative to Artifact Digests

**Status:** Proposed

**Date:** 2026-10-05

## Context

[ADR-0019](0019-trust-manifest-artifact-binding.md) required signed Trust
Manifests to bind artifact content through a digest.
[ADR-0025](0025-bind-signed-trust-manifests-to-releases.md) and
[ADR-0028](0028-independent-trust-manifests-and-whole-object-signatures.md)
retained that requirement while binding release coordinates and making
contributor manifests independently signed. A signer may instead intend
to identify an artifact at a particular HTTPS location without claiming to
endorse one fixed representation of that resource.

Both digest binding and URL binding should be defined before v1. If v1
requires every signed Trust Manifest to contain `subject.digest`, consumers
implementing v1 can reject manifests that omit it. A later minor version
could not simply make that field optional when `subject.url` is present:
those existing consumers would still reject the manifest.

Introducing that change after v1 would therefore require a major version or
a separate mechanism that leaves the original digest requirement intact.
Defining both alternatives now gives them one shared Subject structure from
the outset, consistent with the specification's
[compatibility rules](../specification/ai-catalog.md#compatibility-rules).

## Decision

A signed Trust Manifest's `subject` MUST contain at least one of `digest`
or `url`, and MAY contain both:

- `subject.digest` and `entry.digest` MUST either both be absent or both be
  present and exactly equal. When present, artifact integrity verification
  MUST check the artifact against that digest.
- When present, `subject.url` MUST be an absolute HTTPS URL and MUST exactly
  equal `entry.url`. Fetching follows the existing safe-fetching rules,
  including their redirect checks.
- Every present binding MUST succeed. A failed digest check cannot fall
  back to URL binding.

Identifier, type, and symmetric version matching remain required. URL-only
binding is available for every artifact type. An inline entry has no
`entry.url` and therefore requires a digest to carry a signed Trust Manifest.

## Rationale

The signed subject makes the binding explicit: a digest identifies exact
content; a URL identifies the resource at that location.

Symmetric digest presence prevents a manifest from appearing to authenticate
an entry digest that it did not sign.

## Consequences

- This revises the mandatory content binding in ADR-0019, ADR-0025, and ADR-0028.
- A URL-only endorsement does not authenticate the resource's current bytes
  as bytes examined or approved by the signer. Consumers requiring that
  assurance need a verified digest binding.
- A selected URL cannot be replaced with a mirror URL without reissuing the
  manifest. Digest-only binding continues to permit mirrors.
- Signed identifiers and versions remain protected; this does not add
  rollback prevention or change the requirement that `entry.url` retrieve
  the artifact document.
