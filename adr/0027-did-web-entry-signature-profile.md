# ADR-0027: Define a `did:web` Signature Profile for Entry Trust Manifests

**Status:** Proposed

**Date:** 2026-09-04

## Context

The Trust Manifest signature procedure defines a detached JWS over canonical
JSON, but its identity and key-selection rules do not provide an interoperable
verification procedure.

The `identity` field has accumulated several meanings. It is described as the
artifact's primary subject, as a workload principal, and as the URI from which
the signer's public key is resolved. The signature instructions separately
refer to the publisher's key. These roles need not identify the same thing.

ADR-0025 assigns artifact identity to the signed `subject`. In particular,
`subject.identifier` names the logical artifact and `subject.version` names the
release when the Catalog Entry declares one. The remaining role needed for
`identity` is the issuer to which the Trust Manifest's claims are attributed.

The existing key-resolution text lists DID, HTTPS, SPIFFE, and DNS mechanisms
as though a short lookup instruction were sufficient for each. These
mechanisms have different authorization models and lifecycles. In particular:

- A DID document can contain several verification methods authorized for
  different purposes. Merely finding a key in `verificationMethod` does not
  authorize it to make assertions.
- A SPIFFE Workload API returns credentials to the local workload calling the
  API. It is not a public resolver for an arbitrary SPIFFE ID carried in a
  catalog document.
- A URL or DNS name does not by itself define whether the TLS key, a JWKS key,
  a DNSSEC record, or some other key is authorized to sign a Trust Manifest.

The existing list therefore creates apparent breadth without giving
independent implementations enough information to select the same key or reach
the same verification result.

AI Catalog also needs to distinguish publisher authentication from publisher
trustworthiness. A signature profile can prove that the controller of a domain
authorized claims about an artifact in that domain's namespace. It cannot
decide whether that publisher is reputable, whether its claims are true, or
whether an artifact is safe for a particular consumer.

## Decision

### Identity Roles

`TrustManifest.identity` identifies the issuer to which the Trust Manifest's
claims are attributed. It does not identify the artifact and does not identify
a running instance of the artifact.

The signed `subject` identifies the artifact release and representation.
Runtime and workload identities belong to the artifact's protocol or a future
runtime-security profile.

### One Interoperable v1 Profile

AI Catalog defines one signature profile for signed Entry Trust Manifests:

- The artifact identifier uses the standard `urn:air` syntax defined in
  [Catalog Entry](../specification/ai-catalog.md#catalog-entry).
- The `{publisher}` component is a lowercase ASCII DNS domain name.
- The Trust Manifest issuer is exactly the root `did:web` DID for that domain.
- The JWS algorithm is ES256.
- The signing key is a P-256 `publicKeyJwk` authorized by the current DID
  document's `assertionMethod` relationship.

For example, a Trust Manifest whose signed subject is
`urn:air:example.com:agent:billing` has the issuer
`did:web:example.com`.

This equality is an authorization rule, not merely a consistency check. The
signed subject identifies the publisher namespace, and the `did:web` method
authenticates control of the corresponding domain through HTTPS. A catalog
attacker can publish a separately named artifact under a domain they control,
but cannot retain the original publisher's `urn:air` identifier without
producing a signature authorized by that publisher's DID document.

Under the `did:web` Publisher Profile, the publisher and Trust Manifest issuer
are the same domain authority. The signing operation can be performed by
publishing automation whose key is authorized by the publisher's DID document,
but the profile does not support a separately identified issuer signing on the
publisher's behalf.

The profile supports only root `did:web` DIDs. Ports, method-specific paths,
subdomain matching, corporate-affiliation heuristics, and delegated issuers are
not inferred. They require an explicit future profile because each changes who
is authorized to speak for the publisher namespace.

### Signature and Verification Semantics

The normative profile specifies the detached JWS construction, protected
headers, key representation, DID resolution, verification-method selection,
and verification result. The important application choices are that `alg` is
`ES256`, `kid` identifies one method under the exact issuer DID, and that method
must be authorized by `assertionMethod`. Merely listing a key under
`verificationMethod`, `authentication`, or `keyAgreement` is insufficient.

No `typ` header is required. The signature appears in a specifically defined
Trust Manifest field, so the containing data model supplies the application
context. A future need for cross-protocol token separation can be addressed by
a separate profile rather than adding a marker without a demonstrated
ambiguity.

A Trust Manifest is verified only after the issuer, signature, signed subject,
Catalog Entry, and artifact all satisfy their respective checks. Failure does
not require rejecting the entire catalog, but the consumer cannot rely on the
manifest's claims or count the entry as Level 3. An expired manifest likewise
cannot supply current verified claims.

The profile uses the DID document returned at verification time. `issuedAt` is
a signed claim rather than a trusted timestamp, so it cannot prove that a
removed key was authorized in the past. Historical verification requires a
separate versioning, logging, or timestamping mechanism.

### Explicit Scope Boundaries

This decision does not define:

- signature profiles for SPIFFE IDs, HTTPS key URLs, DNS records, other DID
  methods, or path-based `did:web` identities;
- publisher delegation, hosted signing, or corporate-affiliation rules;
- historical DID document resolution or transparency-log verification;
- whether an authenticated publisher is trusted for a particular use;
- runtime or workload identity;
- the identity and authorization of a top-level catalog signer;
- signature verification for provenance statement formats; or
- a credential format for `publisher-identity` attestations.

Those mechanisms can be added independently when an end-to-end use case and
authorization model are available.

## Consequences

- Implementations have one mandatory producer-consumer intersection instead of
  an open list from which they can choose incompatible algorithms and keys.
- A standard `urn:air` identifier can be authenticated without a separately
  pinned DID. The verifier relies on its DNS and Web PKI trust roots to resolve
  the corresponding `did:web` document.
- Publisher authentication remains distinct from publisher trustworthiness.
  Registries and consumers can layer allowlists, vetting, attestations, or
  organizational policy on top of the authenticated domain.
- The `identity` field no longer carries artifact or workload semantics.
- Existing signed Trust Manifests that use another identity form or algorithm
  do not satisfy the `did:web` Publisher Profile. They can still be processed
  under a separately defined implementation policy.
- Long-term verification is not guaranteed after a signing key is removed from
  the current DID document.
- The generic key-resolution text for SPIFFE, HTTPS, and DNS is removed rather
  than promising behavior the specification does not define.

## Alternatives Considered

### Require an independently configured expected DID

The verifier could require an exact expected issuer DID supplied out of band.
This is appropriate for private policy and remains available as an additional
constraint. It was not chosen as the only interoperable path because the
standard `urn:air` identifier already contains a publisher domain that can
authorize a matching root `did:web` issuer.

### Retain a generic identity-scheme dispatch table

This would preserve the appearance of supporting more identity mechanisms, but
each mechanism still needs profile-specific rules for signer authorization,
key selection, algorithms, lifecycle, and failure behavior. The table is
removed until those rules exist.

### Support multiple mandatory algorithms

Allowing each producer and consumer to implement any one algorithm from a list
does not ensure that a conforming consumer can verify a conforming producer.
ES256 with P-256 `publicKeyJwk` is selected as the required v1 intersection.
Additional algorithms can be defined in later profiles.

### Infer publisher delegation

Suffix matching, path-based DIDs, and organizational-affiliation rules could
allow subsidiaries or signing services to act for a publisher. Such inference
can also authorize an unintended party. Delegation is deferred until the data
model can express who delegated which namespace to whom.

### Use SPIFFE for the Entry Trust Manifest signer

SPIFFE is designed to authenticate workloads within participating trust
domains. Its Workload API supplies credentials to the local workload rather
than resolving arbitrary public SPIFFE IDs. Runtime authentication can use
SPIFFE without treating it as a public artifact-release signing mechanism.
