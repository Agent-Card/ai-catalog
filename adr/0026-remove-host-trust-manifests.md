# ADR-0026: Remove Host Trust Manifests

**Status:** Proposed

**Date:** 2026-09-04

## Context

A Trust Manifest may currently appear on either a Catalog Entry or a Host Info
object. The shared structure is nevertheless defined in terms of an AI
artifact: its identity, publisher, provenance, policies, and, when signed, a
`subject` containing the artifact's media type and content digest.

That model has a concrete security purpose on a Catalog Entry. The publisher
signs claims that are bound through `subject` to the artifact a consumer will
retrieve. A consumer can compare the signed subject with the entry and the
artifact bytes before relying on those claims.

There is no corresponding subject or verification target for a Host Trust
Manifest. Host Info identifies the catalog operator but does not identify an
artifact whose media type and bytes can be hashed. A Host signature over only
the nested manifest would protect its internal claims without approving the
surrounding Host Info object, its placement in the catalog, or the catalog
snapshot. Even after anchoring its signer, a valid Host manifest could
consequently be copied into another catalog without invalidating its signature.

The specification also does not define a Host-specific claim vocabulary or a
consumer decision that depends on independently signed Host claims. Several
shared Trust Manifest members retain artifact-specific semantics, including
publisher identity, provenance, and a privacy policy governing the artifact.
General organizational credentials would require their own issuer, subject,
claim, validity, status, and verification semantics.

Host Info is already included in the bytes protected by the optional top-level
catalog signature. Once the catalog signer is independently authorized, that
is the appropriate scope for establishing the integrity of the operator
metadata and its association with a particular catalog snapshot. Independently
signed audit reports or organizational credentials can retain their native
proof formats; a future profile may define how a catalog carries and evaluates
them when there is a concrete use case.

## Decision

Remove `trustManifest` from Host Info. A Trust Manifest is defined only as an
optional companion to a Catalog Entry and continues to carry claims about an AI
artifact.

This decision does not change Entry Trust Manifest contents or verification.
It also does not define how a top-level catalog signature identifies an
authorized catalog signer; that requires a separate decision.

Operator-specific trust evidence is deferred from the core v1 data model.
Implementations may experiment through the existing top-level
`AICatalog.extensions` mechanism, but consumers cannot assume interoperable
semantics for such extensions.

## Consequences

- Every Trust Manifest has the same artifact-oriented meaning and a Catalog
  Entry that supplies its verification context.
- Host Info remains the place for informational operator identity and
  presentation metadata.
- When present and verified using an authorized signer, catalog-level integrity
  can protect Host Info and its association with the catalog snapshot. A signed,
  verified, and anchored Entry Trust Manifest continues to protect an
  individual publisher's artifact claims.
- The core model does not provide a standard container for operator compliance
  evidence or independently reusable organizational credentials.
- Existing prerelease implementations that expose Host Trust Manifests must
  remove the field, but there is no released v1 representation whose
  compatibility must be preserved.

## Alternatives Considered

### Define separate Host and Entry Trust Manifest types

Deferred. Separate structures would remove the artifact-subject contradiction,
but a useful Host type still needs concrete claims, consumers, and verification
semantics. No such end-to-end requirement has been established for v1.

### Keep an unsigned Host evidence container

Deferred. A catalog signature could protect an unsigned collection of Host
attestation references, but the current fields do not yet provide interoperable
semantics for evaluating organizational evidence. An extension can incubate
that design without making it part of the core model.

### Sign only the Host Trust Manifest's internal claims

Rejected. This authenticates neither the containing catalog nor the
association between those claims and that catalog. It adds a second signature
and lifecycle without a demonstrated independent-consumption requirement.

### Define the catalog or Host Info as the Host manifest's subject

Rejected. Both contain the Host Trust Manifest itself, creating a circular
representation unless special exclusion and canonicalization rules are added.
The existing catalog signature already has the correct document scope.
