# ADR-0028: Identity-Keyed Trust Manifests and Selective Signatures

**Status:** Proposed

**Date:** 2026-09-12

## Context

An entry currently has one Trust Manifest containing contributor identity,
trust evidence, and a signature. A publisher, an assessor, and a catalog
operator may each have claims to contribute about the same artifact. They
need separate places to publish and update those claims.

The existing signature covers the entire Trust Manifest. To authenticate
artifact fields stored outside it, the Trust Manifest repeats them in a
`subject` object. Other entry metadata, such as entry extensions, can also
warrant an endorsement. Letting signatures select entry fields directly gives
these endorsements a common format.

## Decision

### Group claims by contributor

Replace `entry.trustManifest` with `entry.trustManifests`, a map from
contributor identity URIs to Trust Manifest objects. Each entry has at most
one manifest per contributor identity. Each manifest can contain
`trustSchema`, `attestations`, `provenance`, and `extensions`.

For example, the publisher can provide source provenance under
`trustManifests["did:web:publisher.example"]`, while an assessor provides audit
references under `trustManifests["did:web:assessor.example"]`. The assessor can
update its manifest without invalidating a publisher signature that covers
only the publisher's manifest and the shared artifact fields.

### Place fields according to what they describe

Fields are grouped according to what they describe:

- Entry fields describe the shared artifact.
- Trust Manifest fields contain a particular contributor's claims.
- Signature fields describe an endorsement.

The existing fields map to the proposed structure as follows:

| Existing location | Proposed location |
| --- | --- |
| `trustManifest.identity` | Contributor key in `entry.trustManifests`; endorsement identity in `entry.signatures[].signer` |
| `trustManifest.identityType` | Removed; the signer profile determines how to interpret the identity URI |
| `trustManifest.trustSchema` | `entry.trustManifests[identity].trustSchema` |
| `trustManifest.attestations` | `entry.trustManifests[identity].attestations` |
| `trustManifest.provenance` | `entry.trustManifests[identity].provenance` |
| `trustManifest.extensions` | `entry.trustManifests[identity].extensions` |
| `trustManifest.privacyPolicyUrl` | `entry.privacyPolicyUrl` |
| `trustManifest.termsOfServiceUrl` | `entry.termsOfServiceUrl` |
| `trustManifest.subject.digest` | `entry.digest` |
| `trustManifest.subject.identifier`, `.version`, `.type`, `.url` | Already exist in `entry`; sign those fields directly |
| `trustManifest.signature` | `entry.signatures[].jws` |
| `trustManifest.issuedAt` | `entry.signatures[].issuedAt` |
| `trustManifest.expiresAt` | `entry.signatures[].expiresAt` |
| Catalog root `signature` | Objects in the root `signatures` array |

### Sign selected fields

Entries and the catalog root can each carry a `signatures` array. Each
signature names its signer with an absolute identity URI in `signer` and
selects the fields it endorses through `paths`. It also carries `issuedAt`,
optional `expiresAt`, and a detached `jws`. The array supports multiple
endorsements by the same identity, with different selected fields, issuance
times, or keys.

For example, an assessor can endorse its Trust Manifest together with the
entry fields identifying the artifact release:

```json
{
  "signer": "did:web:assessor.example",
  "paths": [
    ["identifier"],
    ["version"],
    ["type"],
    ["digest"],
    ["trustManifests", "did:web:assessor.example"]
  ],
  "issuedAt": "2026-09-13T00:00:00Z",
  "jws": "..."
}
```

Each path is an array of exact object member names, starting at the object
containing the signature array. For example,
`["extensions", "https://example.com/metadata"]` selects one entry extension.
A path can select an entire array, such as a contributor's `attestations`
list, but cannot select an individual array element.

The signer collects each selected path and its value into a pair, sorts those
pairs by path, and adds the signer identity, endorsement timestamps, and a
context identifying the object kind and payload construction. This collected
data is the **payload**: the data over which the signature is computed. JCS
gives it a deterministic JSON encoding, and JWS supplies the cryptographic
signature. The detached JWS stored in `jws` omits the payload; the verifier
constructs that same payload from the selected fields and signature metadata.

For example, the signature object above could have this payload:

```json
{
  "context": "ai-catalog-entry-signature",
  "signer": "did:web:assessor.example",
  "fields": [
    [["digest"], "sha256:56bbd2ff730d81a52951fc2f58809dfb086b4be7a82766dcc18cfe32ff6acbbd"],
    [["identifier"], "urn:air:publisher.example:agent:example"],
    [
      ["trustManifests", "did:web:assessor.example"],
      {
        "attestations": [
          {
            "type": "SOC2-Type2",
            "uri": "https://assessor.example/report.pdf"
          }
        ]
      }
    ],
    [["type"], "application/json"],
    [["version"], "1.0.0"]
  ],
  "issuedAt": "2026-09-13T00:00:00Z"
}
```

Including both paths and values authenticates which fields the signer
endorses. Sorting the pairs lets authors reorder the path list without
changing the signature. The exact `signer` value and timestamps are
authenticated along with the selected fields.

To endorse claims about an artifact release, a signature selects the claims
and the entry's `identifier`, `type`, `digest`, and `version` when present.
The consumer checks both the signature and the artifact content against that
digest. A typical assessor signature selects the assessor's entire manifest
and those entry fields. The signature then establishes which artifact and
version the assessor's claims describe. Selecting `url` additionally endorses
a location; leaving it unselected permits mirrors serving identical bytes.

The [specification](../specification/ai-catalog.md#signature-object) defines
payload construction, verification, and required field coverage.

### Authenticate contributors and establish publisher authority

The `signer` field identifies whose endorsement is claimed; the protected
JWS `kid` identifies the verification key. An explicit identity field gives
consumers a consistent way to inspect signers across verification profiles
without decoding JWS headers. Each profile defines how to discover a key and
establish that it is authorized to sign for the claimed identity.

The initial `did:web` profile authenticates publishers and independent
contributors through their root DIDs. The DID in `kid` must exactly match
`signer`, and that DID's document must authorize the selected key through
`assertionMethod`. These checks and verification of the signature authenticate
`signer`. This profile repeats the identity in `signer` and `kid`, requiring a
consistency check in exchange for a common identity field across profiles.

To attribute selected Trust Manifest claims to their named contributor, the
authenticated `signer` must match the manifest's identity key. A catalog
operator can endorse an assessor's manifest, but the operator's signature
alone does not establish that the assessor made those claims. Publisher
authorization additionally requires the authenticated identity to match the
publisher domain in the entry's signed `urn:air` identifier.

Additional profiles can define other identity mechanisms and their key
discovery and authorization procedures. The consumer decides whether an
authenticated contributor's evidence satisfies its trust policy. Referenced
attestation and provenance documents are verified according to their formats.

### Publish and select updates

A contributor updates its manifest and signs the updated value. Two registries
may retrieve that manifest at different times and consequently hold different
signed versions. When a consumer encounters both for the same artifact
release, it can prefer the manifest covered in full by that contributor's most
recent acceptable signature, comparing `issuedAt` timestamps. A later signature
from another entity does not identify an update by the contributor.

### Sign catalog fields and snapshots

A root signature selects catalog fields: for example, selecting only `host`
endorses the host metadata and leaves `entries` unsigned by that signature.
A consumer accepting a complete catalog snapshot must check that the signature
covers every root member except the root's own `signatures` array.

Selecting the entire `entries` array includes the signatures within each
entry. Adding an entry signature therefore requires regenerating any catalog
signature covering that array, even when the artifact and other metadata are
unchanged. Adding a root co-signature does not change the snapshot.

Independent Host Info signatures are deferred until a concrete use case is
established, consistent with [ADR-0026](0026-remove-host-trust-manifests.md).

## Consequences

- Contributors can independently publish and update their trust metadata.
- Consumers can determine which entry fields each signer endorsed.
- Shared artifact fields have one location and can be covered by several
  signatures from different signers.
- Existing singular-manifest and singular-signature documents require migration
  to the new structure.
- Moving `privacyPolicyUrl` and `termsOfServiceUrl` onto the entry removes
  their automatic coverage by a signature over the entire Trust Manifest.
  Their authentication now depends on the fields selected by each signature.
- Layer 1 uses `entry.digest` for artifact integrity checks. Its previous use
  of `provenance[].sourceDigest` conflicted with the existing verification
  procedure, which distinguishes artifact digests from provenance source
  digests. The meaning of `sourceDigest` is unchanged.
- Signing a complete catalog snapshot requires listing every top-level field
  except `signatures`. Adding a top-level field requires updating that list
  and generating a new snapshot signature.
- Consumers requiring protection against replay of older, still-valid
  endorsements need trusted current information or previously observed state.
