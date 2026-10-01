# ADR-0020: Require a Substantive Trust Manifest

**Status:** Accepted

**Date:** 2026-06-21

**Participants:** Luca Muscariello (Cisco)

**Later clarification:** [ADR-0027](0027-did-web-entry-signature-profile.md)
supersedes this ADR's description of `identity` as a workload principal. The
manifest-validity rule established here remains unchanged.

## Context

The Trust Manifest is an OPTIONAL companion to a Catalog Entry. Within
it, however, only `identity` was unconditionally REQUIRED. Every other member — `signature`,
`attestations`, `provenance`, `trustSchema`, and the informational fields
— was independently OPTIONAL.

As a result the smallest valid Trust Manifest was `{ "identity": "..." }`,
which carries no trust signal by itself.
Only Level 3 (Trusted Catalog) forced a real payload (`signature` +
`subject` + `issuedAt`). Between "no manifest" and Level 3 the format
permitted a present-but-empty manifest that looks like trust metadata
while asserting nothing — misleading to consumers and noise to tooling.

If every field is optional, the unit of optionality is wrong: the
*manifest* should be the optional element, and when an author chooses to
include one it should be required to be meaningful.

## Decision

Define a validity floor for the Trust Manifest. Beyond the required
`identity`, a Trust Manifest MUST contain at least one *substantive* trust
member:

- a `signature` (with its required `subject` and `issuedAt`),
- a non-empty `attestations` array,
- a non-empty `provenance` array, or
- a `trustSchema`.

`identity` and `identityType` (which identify the workload principal)
and the informational members `privacyPolicyUrl`,
`termsOfServiceUrl`, and `metadata` do not satisfy this requirement.
`subject`, `issuedAt`, and `expiresAt` are not substantive on their own:
an unsigned `subject` digest is attacker-settable and unverifiable, so
they count only as part of a `signature`.

A Trust Manifest that would carry only non-substantive members MUST be
omitted entirely. Consumers SHOULD treat a manifest that violates this
rule as if no Trust Manifest were present.

## Consequences

- A present Trust Manifest now always carries at least one verifiable or
  governance-bearing claim; the degenerate identity-only manifest is no
  longer valid.
- Authors who have nothing substantive to assert simply omit
  `trustManifest`, which is already OPTIONAL — no information is lost.
- The rule is independent of conformance level: even a Level 1 catalog
  that includes a manifest must make it substantive. Level 3 remains
  stricter, requiring a `signature` specifically (see
  [ADR-0019](0019-trust-manifest-artifact-binding.md)).
- Unsigned manifests remain valid when they carry attestations,
  provenance, or a trust schema, preserving low-assurance use cases that
  do not sign.
