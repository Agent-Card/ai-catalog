# ADR-0028: Independent Trust Manifests and Whole-Object Signatures

**Status:** Proposed

**Date:** 2026-09-12

## Context

An entry currently has one Trust Manifest containing contributor identity,
trust evidence, and a signature. A publisher, an assessor, and a catalog
operator may each have claims to contribute about the same artifact. They
need separate places to publish and update those claims.

The artifact release and a contributor's claims have different lifecycles.
An assessor should be able to update its evidence without requiring the
publisher or another assessor to sign again. At the same time, consumers
need a precise account of what each signature authenticates and which
artifact release the claims describe.

## Decision

### Publish independent contributions

Replace `entry.trustManifest` with an `entry.trustManifests` array. Each
Trust Manifest identifies its `contributor` with an absolute identity URI.
The contributor is required even when the manifest is unsigned. A signed
manifest has one `signature`, whose authenticated `signer` must exactly match
`contributor`, and a `subject` identifying the artifact release.

For example, a publisher can provide source provenance in its manifest,
while an assessor provides audit references in a separate manifest. Either
can update its contribution without invalidating the other's signature.
The array can preserve several contributions from the same identity,
including different signed versions, without changing their contents.

Each manifest has at most one signer. Multiple signatures over the same
manifest and references from one manifest to another are deferred until
concrete consumer requirements justify their additional semantics and
processing. Neither mechanism is necessary to publish independently signed
contributions about the same artifact.

### Bind each signed manifest to its artifact release

A signed Trust Manifest contains a `subject` with the artifact's `identifier`,
`type`, and `digest`, and its `version` when the entry has one. The subject
identifies the release to which the complete contribution applies. A signed
manifest can contain only the contributor, subject, and signature when its
purpose is to endorse the release without additional trust evidence.

Consumers check that the subject matches the containing entry, including
version presence and equality, and verify the artifact against the digest.
The digest describes the artifact bytes, or the JCS encoding of inline
artifact data; it is not a digest of the catalog entry. Add `entry.digest`
for artifact integrity checks independently of any particular contribution.
A signed manifest requires this field and a matching `subject.digest`.

The signed payload can be reconstructed from the manifest itself. Repeating
the release coordinates requires some duplicated data and explicit
subject-to-entry consistency checks. Those costs are accepted in exchange
for a fixed signing scope and a portable signed statement.

The subject does not include `url`. The signature binds the artifact through
its digest while permitting retrieval from mirrors that serve the same
content. Signing entry extensions or an original artifact URL is outside
this proposal and can be considered separately.

### Place fields according to what they describe

Fields are grouped according to what they describe:

- Entry fields describe the shared artifact.
- Trust Manifest fields contain a particular contributor's claims and identify
  the artifact release they concern.
- Signature fields identify the signer, verification profile, and signing time.

The existing fields map to the proposed structure as follows:

| Existing location | Proposed location |
| --- | --- |
| `trustManifest.identity` | `trustManifests[].contributor`; signing identity in `trustManifests[].signature.signer` |
| `trustManifest.identityType` | Removed; the signer profile determines how to interpret the identity URI |
| `trustManifest.privacyPolicyUrl` | `entry.privacyPolicyUrl` |
| `trustManifest.termsOfServiceUrl` | `entry.termsOfServiceUrl` |
| `trustManifest.subject.digest` | Retained; must match the new `entry.digest` |
| `trustManifest.subject.url` | Removed; the entry retains its retrieval URL |
| `trustManifest.signature` | `trustManifests[].signature.jws` |
| `trustManifest.issuedAt` | `trustManifests[].signature.issuedAt` |
| `trustManifest.expiresAt` | `trustManifests[].signature.expiresAt` |
| Catalog root `signature` | Signature object at the same location |

### Sign the complete manifest

A signature object contains `signer`, `profile`, `issuedAt`, optional
`expiresAt`, and a detached `jws`. `issuedAt` records when the contributor
endorsed the claims, including a renewed endorsement of unchanged claims,
independently of when the supporting evidence was created or updated.
For example:

```json
{
  "contributor": "did:web:assessor.example",
  "subject": {
    "identifier": "urn:air:publisher.example:agent:example",
    "type": "application/json",
    "version": "1.0.0",
    "digest": "sha256:56bbd2ff730d81a52951fc2f58809dfb086b4be7a82766dcc18cfe32ff6acbbd"
  },
  "attestations": [
    {
      "type": "SOC2-Type2",
      "uri": "https://assessor.example/report.pdf"
    }
  ],
  "signature": {
    "signer": "did:web:assessor.example",
    "profile": "did-web-v1",
    "issuedAt": "2026-09-13T00:00:00Z",
    "jws": "..."
  }
}
```

The payload is the complete manifest with exactly two exclusions:

- The immediate `signature.jws` member, which holds the signature being computed.
- The immediate `additionalSignatures` member, reserved for a future extension.

These exclusions are not recursive. All other members, including unfamiliar
members and the signature's `signer`, `profile`, and timestamps, remain in
the signed payload. An occurrence of `signature` or `additionalSignatures`
inside a nested extension or other value is retained unchanged. Consumers
ignore the reserved `additionalSignatures` field and assign it no verification
semantics in v1. Reserving its exclusion now permits a later version to
introduce additional signatures without invalidating the original one.

JCS gives the payload a deterministic JSON encoding, and JWS supplies the
cryptographic signature. The detached JWS omits the payload; the verifier
reconstructs it using the same exclusions. The protected JWS `typ` value
`ai-catalog-trust-manifest+jws` distinguishes a Trust Manifest from a catalog
snapshot.

The [specification](../specification/ai-catalog.md#signature-object) defines
signing and verification procedures.

### Authenticate contributors

`signature.signer` identifies whose endorsement is claimed, and
`signature.profile` selects the verification rules. These explicit fields
let consumers inspect identities and select profiles without decoding JWS
headers. Each profile defines how to discover a key and establish that it
is authorized to sign for the claimed identity.

The identity in `signature.signer` may support different verification
profiles. Recording the selected profile in the signature object tells
consumers which verification rules to apply. Including it in the signed
content prevents intermediaries from changing that selection.

The initial [did:web Signer Profile](../specification/ai-catalog.md#the-did-web-signer-profile)
authenticates publishers and independent contributors. The authenticated
`signature.signer` must exactly match the manifest's `contributor` to
authenticate that attribution. An unsigned contributor label alone does not
establish who authored the claims. Additional profiles can support other
identity mechanisms and verification rules.

### Recognize publisher endorsements

The [did:web Publisher Profile](../specification/ai-catalog.md#the-did-web-publisher-profile)
combines the Signer Profile with publisher authorization and artifact
release binding. The authenticated identity must match the publisher domain
in the signed subject's `urn:air` identifier, and the subject must match the
entry and artifact. This lets the same authentication procedure serve
publishers and independent contributors while consumers distinguish their
endorsements. Consumers decide which contributors and claims meet their
trust policies.

### Publish and select updates

A contributor updates its manifest and signs the updated object. Two
registries may retrieve that manifest at different times and consequently
hold different signed versions. When a consumer encounters both for the same
artifact release, it can prefer the contributor's most recent acceptable
signature by comparing `issuedAt` timestamps. Consumers still apply their
own acceptance policy; a later timestamp does not by itself establish that
the evidence is sufficient or current.

### Sign catalog snapshots

The catalog root can carry one `signature` object. Its payload is the complete
catalog with the immediate `signature.jws` and reserved immediate
`additionalSignatures` members excluded, using the same construction as a
Trust Manifest. Its protected JWS `typ` is `ai-catalog+jws`.

The snapshot includes all Host Info and entry values, including nested Trust
Manifests, their signatures, and their reserved `additionalSignatures` fields.
Adding, removing, or changing a contribution therefore requires regenerating
the catalog signature, even when other contributions' signatures remain valid.
Nested signature fields are not removed when constructing the catalog
payload.

Independent Host Info signatures are deferred until a concrete use case is
established, consistent with [ADR-0026](0026-remove-host-trust-manifests.md).

## Consequences

- Contributors can independently publish and update signed trust metadata
  about the same artifact release.
- Each manifest signature authenticates the complete contribution, including
  its contributor identity, release subject, and signature metadata.
- Signed manifests carry their own release binding and can be distributed
  independently, at the cost of duplicated release coordinates and consistency
  checks against the containing entry.
- Existing singular-manifest documents require migration to the array, and
  existing signatures require migration to the structured signature format.
- Moving `privacyPolicyUrl` and `termsOfServiceUrl` onto the entry removes
  their automatic coverage by a signature over the entire Trust Manifest.
  Whole-catalog signatures cover these fields as part of the snapshot.
  Authenticating entry metadata with a contributor's signature is future work.
- Layer 1 uses `entry.digest` for artifact integrity checks. Its previous use
  of `provenance[].sourceDigest` conflicted with the existing verification
  procedure, which distinguishes artifact digests from provenance source
  digests. The meaning of `sourceDigest` is unchanged.
- A catalog signature authenticates the complete snapshot without a separate
  list of covered fields. Changes to entries or their contributions require
  a new snapshot signature.
- Existing native OCI signing and verification policy is unchanged; mapping
  updates adapt the logical fields without requiring preservation of a JWS
  where the mapping already permits native OCI mechanisms.
- Consumers requiring protection against replay of older, still-valid
  endorsements need trusted current information or previously observed state.
