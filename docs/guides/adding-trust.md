# Adding Trust

An entry can carry optional `trustManifests`, each identifying a contributor and optionally carrying one signature. Each signed manifest binds its claims to an artifact release through a `subject`. Neither a manifest nor a signature is needed for a minimal catalog.

## Choosing what to publish

Add a digest when consumers need to check the artifact's content. Add a Trust Manifest when a contributor has attestations, provenance, or a trust-framework declaration to share. Sign the manifest to authenticate its claims and bind them to that artifact release. A signed manifest can also contain only the contributor, release subject, and signature object, without additional trust claims.

A minimal catalog needs only entries. Discoverable catalogs add Host Info and may use the well-known discovery location. Trusted catalogs additionally satisfy the specification's publisher-signature and evidence requirements; the presence of an arbitrary signature does not establish that conformance level.

## Trust Manifest structure

`entry.trustManifests` is an array. Each manifest identifies its `contributor` by an absolute identity URI and contains that contributor's trust metadata:

```json
{
  "trustManifests": [
    {
      "contributor": "did:web:acme-corp.com",
      "provenance": [
        {
          "relation": "publishedFrom",
          "sourceId": "https://github.com/acme-corp/finance-agent"
        }
      ]
    }
  ]
}
```

This is an excerpt, not a complete entry. The `contributor` value is a claim about authorship, not proof that the contributor supplied the metadata. Authenticate it through the manifest's signature, whose verified `signer` must exactly match `contributor`.

| Manifest field | Description |
|---|---|
| `contributor` | Absolute identity URI of the contributor |
| `subject` | Artifact release identified by `identifier`, `type`, `digest`, and optional `version`; required for signed manifests |
| `signature` | Optional signature object authenticating the manifest and its subject |
| `trustSchema` | Identifies an external trust framework and its version |
| `attestations` | Array of compliance and identity evidence references |
| `provenance` | Array of lineage links |
| `extensions` | Namespaced custom trust metadata |

An unsigned manifest must include a trust schema or a non-empty attestations array, provenance array, or extensions map. A signed manifest may instead endorse only its artifact release.

A `trustSchema` names a trust framework; it does not by itself prove compliance or supply an executable verification policy. Consumers need to understand the referenced framework before using it in a trust decision.

!!! tip "Attestation document format"
    Evidence may be human-readable, such as a PDF audit report, or machine-readable, such as a signed credential. Verification depends on that evidence's format and the consumer's policy.

## Adding compliance attestations

For regulated environments, add compliance evidence:

```json
"attestations": [
  {
    "type": "SOC2-Type2",
    "uri": "https://trust.acme-corp.com/reports/soc2.pdf",
    "digest": "sha256:a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890",
    "description": "SOC 2 Type 2 report, valid through 2026"
  },
  {
    "type": "ISO27701",
    "uri": "https://trust.acme-corp.com/credentials/iso27701.sd-jwt",
    "digest": "sha256:abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
    "description": "ISO/IEC 27701 privacy management certification (IETF SD-JWT VC) issued by did:web:auditor.example"
  },
  {
    "type": "ISO27001",
    "uri": "https://trust.acme-corp.com/certs/iso27001.pdf"
  }
]
```

The `digest` field allows clients to verify the attestation document hasn't been tampered with after being referenced in the catalog.

!!! tip "Attestation freshness"
    Attestations have no built-in expiry. Include a `description` with the validity period, and update the catalog entry's `updatedAt` field when you refresh attestations. Alternatively, you can rely on expiry mechanisms defined by the attestation document format (e.g., Verifiable Credential validity).

## Adding provenance

Provenance links trace where an artifact came from:

```json
"provenance": [
  {
    "relation": "publishedFrom",
    "sourceId": "https://github.com/acme-corp/finance-agent",
    "sourceDigest": "sha256:fedcba0987654321fedcba0987654321fedcba0987654321fedcba0987654321"
  }
]
```

The `relation` field is an open string. Three common values:

| Relation | Meaning |
|---|---|
| `publishedFrom` | The artifact was built from this source repository |
| `derivedFrom` | The artifact was derived from another artifact |
| `materializedFrom` | The artifact was materialized from an OCI registry |

`sourceId` is a URI identifying the source. `sourceDigest` is a cryptographic hash (`sha256:...`) for integrity verification.

## Signing a Trust Manifest

To endorse an artifact release, add a `subject` and a `signature` object to the contributor's Trust Manifest. Set `signature.signer` to the same absolute identity URI as `contributor`, and `signature.profile` to the identifier of the signer verification procedure. The `did:web` Signer Profile uses `profile: "did-web-v1"`.

For example, Acme can sign a manifest that endorses the artifact release without adding other trust claims:

```json
{
  "contributor": "did:web:acme-corp.com",
  "subject": {
    "identifier": "urn:air:acme-corp.com:a2a:finance",
    "type": "application/a2a-agent-card+json",
    "digest": "sha256:9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
  },
  "signature": {
    "signer": "did:web:acme-corp.com",
    "profile": "did-web-v1",
    "issuedAt": "2026-03-15T10:00:00Z",
    "jws": "eyJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWI6YWNtZS1jb3JwLmNvbSNyZWxlYXNlLXNpZ25pbmcta2V5IiwidHlwIjoiYWktY2F0YWxvZy10cnVzdC1tYW5pZmVzdCtqd3MifQ..detached-jws-signature"
  }
}
```

The JWS here is an illustrative placeholder. Copy the entry's `identifier`, `type`, and `digest` into `subject`. If the entry declares `version`, include that same value in `subject.version`; otherwise omit it from the subject too. Consumers must check that these fields match before accepting the manifest's claims for the entry.

Record the endorsement time in `signature.issuedAt` and, optionally, an expiry time in `signature.expiresAt`. To produce `signature.jws`, take the whole Trust Manifest and omit only its top-level `additionalSignatures` field and `signature.jws`. JCS (RFC 8785) canonicalizes the remaining object before detached JWS signing. All other fields, including `contributor`, `subject`, the signature's metadata, and unfamiliar fields, participate in the signed payload. Follow the full specification for the exact payload and verification algorithm.

The protected JWS header includes `typ: "ai-catalog-trust-manifest+jws"` to identify the signed object as a Trust Manifest. The manifest carries its own release binding, so its signature can be verified independently of the containing entry; accepting it for a particular entry additionally requires the subject and artifact checks.

Adding another contributor's manifest does not invalidate this manifest's signature. Changing any signed content inside this manifest does. Entry metadata outside the manifest, including policy URLs and entry extensions, is not authenticated by this signature. An artifact may be retrieved from a mirror as long as its bytes match the signed digest.

## Verifying a Trust Manifest

First select the procedure named by `profile`, checking that it is supported and permitted by local policy. Other manifests can be evaluated independently.

For the example above, `profile: "did-web-v1"` selects the `did:web` Signer Profile, which verifies Acme's endorsement using `signer: "did:web:acme-corp.com"` and the protected JWS header's `kid: "did:web:acme-corp.com#release-signing-key"`. The DID in `kid` must exactly match `signer`, and the header's `alg` must be `ES256`.

The verifier retrieves Acme's root DID document from `https://acme-corp.com/.well-known/did.json` and checks that it authorizes the selected P-256 key through `assertionMethod`. A key listed only for authentication or key agreement does not satisfy this profile. The verifier uses the authorized key to check the JWS against the canonicalized manifest payload, including its exact `signature.signer` and `signature.profile` values. Changing the profile label therefore invalidates the signature. The identity becomes authenticated only after these checks succeed.

For the manifest to count as Acme's claims, its `contributor` must exactly match the authenticated `signature.signer`. Publisher authority requires an additional check: Acme's root `did:web` domain must match the publisher domain of the entry's standard `urn:air` identifier. An independent contributor can authenticate with its own DID without thereby becoming the artifact's publisher.

Consumers should:

1. Select the named, supported, and locally permitted profile (`did-web-v1` here). Check that `subject.identifier`, `subject.type`, and `subject.digest` match the entry and that `subject.version` has the same presence and value as `entry.version`.
2. Construct and canonicalize the manifest payload, omitting only its top-level `additionalSignatures` and `signature.jws`.
3. Check the protected `typ`, check that the DID in the protected `kid` exactly matches `signature.signer`, resolve the key, check assertion authorization, and verify the ES256 JWS.
4. Check freshness, exact equality of `contributor` and the authenticated `signature.signer`, and the authority needed for the intended endorsement.
5. Verify the artifact bytes against `subject.digest`, and evaluate referenced evidence according to its format and local policy.

If a check fails, do not treat the affected claims as verified. Consumers can retain an unverified entry, retry temporary resolution failures, or reject it according to local policy. A valid signature proves an endorsement, not that the artifact is safe or every claim is true.

## Catalog signatures

The catalog root can carry one `signature` object authenticating the complete catalog snapshot, including Host Info, entries, and all nested Trust Manifests. Its payload omits only the root's `additionalSignatures` field and the root's `signature.jws`. The catalog signature also covers the signatures and reserved `additionalSignatures` fields inside its Trust Manifests.

The protected JWS header uses `typ: "ai-catalog+jws"`. Adding or changing a nested manifest or signature changes the snapshot and requires a new catalog signature.

## Complete example

An entry with a contributor manifest, artifact digest, policy links, and a signature. The digest and JWS values are illustrative placeholders:

```json
{
  "identifier": "urn:air:acme-corp.com:a2a:finance",
  "type": "application/a2a-agent-card+json",
  "url": "https://agents.acme-corp.com/finance",
  "publisher": {
    "identifier": "did:web:acme-corp.com",
    "displayName": "Acme Financial Corp"
  },
  "digest": "sha256:9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
  "privacyPolicyUrl": "https://acme-corp.com/legal/privacy",
  "termsOfServiceUrl": "https://acme-corp.com/legal/terms",
  "trustManifests": [
    {
      "contributor": "did:web:acme-corp.com",
      "subject": {
        "identifier": "urn:air:acme-corp.com:a2a:finance",
        "type": "application/a2a-agent-card+json",
        "digest": "sha256:9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
      },
      "trustSchema": {
        "identifier": "urn:trust:acme-enterprise-v1",
        "version": "1.0",
        "governanceUri": "https://acme-corp.com/trust/governance.pdf",
        "verificationMethods": ["did:web"]
      },
      "attestations": [
        {
          "type": "SOC2-Type2",
          "uri": "https://trust.acme-corp.com/reports/soc2.pdf",
          "digest": "sha256:a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890",
          "description": "SOC 2 Type 2 report, valid through 2026"
        },
        {
          "type": "ISO27701",
          "uri": "https://trust.acme-corp.com/credentials/iso27701.sd-jwt",
          "digest": "sha256:abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
          "description": "ISO/IEC 27701 privacy management certification (IETF SD-JWT VC) issued by did:web:auditor.example"
        }
      ],
      "provenance": [
        {
          "relation": "publishedFrom",
          "sourceId": "https://github.com/acme-corp/finance-agent",
          "sourceDigest": "sha256:fedcba0987654321fedcba0987654321fedcba0987654321fedcba0987654321"
        }
      ],
      "signature": {
        "signer": "did:web:acme-corp.com",
        "profile": "did-web-v1",
        "issuedAt": "2026-03-15T10:00:00Z",
        "jws": "eyJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWI6YWNtZS1jb3JwLmNvbSNyZWxlYXNlLXNpZ25pbmcta2V5IiwidHlwIjoiYWktY2F0YWxvZy10cnVzdC1tYW5pZmVzdCtqd3MifQ..detached-jws-signature"
      }
    }
  ]
}
```

## Next steps

See the [Full Specification](../specification.md) for subject matching, payload construction, the `did:web` profile, publisher authority, and conformance requirements.
