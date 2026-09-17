# Adding Trust

AI Catalog separates contributor claims from signatures. An entry can carry optional `trustManifests` keyed by contributor identity, while its `signatures` array records endorsements of selected fields. Neither is needed for a minimal catalog.

## Choosing what to publish

Add a digest when consumers need to check the artifact's content. Add a Trust Manifest when a contributor has attestations, provenance, or a trust-framework declaration to share. Add a signature to authenticate selected entry fields and bind them to that artifact release.

A minimal catalog needs only entries. Discoverable catalogs add Host Info and the well-known discovery location. Trusted catalogs additionally satisfy the specification's publisher-signature and evidence requirements; the presence of an arbitrary signature does not establish that conformance level.

## Trust Manifest structure

`entry.trustManifests` is a map whose keys are identity URIs. Each value contains that contributor's trust metadata:

```json
{
  "trustManifests": {
    "did:web:acme-corp.com": {
      "provenance": [
        {
          "relation": "publishedFrom",
          "sourceId": "https://github.com/acme-corp/finance-agent"
        }
      ]
    }
  }
}
```

This is an excerpt, not a complete entry. An identity key is a claim about the contributor, not proof that the contributor supplied the metadata. Authenticate it through a signature that covers the manifest and whose verified signer matches the key.

| Manifest field | Description |
|---|---|
| `trustSchema` | Identifies an external trust framework and its version |
| `attestations` | Array of compliance and identity evidence references |
| `provenance` | Array of lineage links |
| `extensions` | Namespaced custom trust metadata |

A manifest must include a trust schema or a non-empty attestations array, provenance array, or extensions map.

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

## Signing an entry

To endorse an entry, add an object to `entry.signatures`. Set `signer` to the absolute identity URI of the party issuing the endorsement, `profile` to the identifier of the signer verification procedure, and `paths` to the fields being endorsed. The `did:web` Signer Profile uses `profile: "did-web-v1"`.

For example, Acme can endorse its Trust Manifest together with the entry fields identifying the artifact release:

```json
{
  "signer": "did:web:acme-corp.com",
  "profile": "did-web-v1",
  "paths": [
    ["identifier"],
    ["type"],
    ["digest"],
    ["trustManifests", "did:web:acme-corp.com"]
  ],
  "issuedAt": "2026-03-15T10:00:00Z",
  "jws": "eyJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWI6YWNtZS1jb3JwLmNvbSNyZWxlYXNlLXNpZ25pbmcta2V5In0..detached-jws-signature"
}
```

The JWS here is an illustrative placeholder. If the entry declares `version`, include `["version"]` in that same signature. Include policy links or other fields when they are also part of the endorsement.

Each path lists exact object keys, starting at the entry. For example, `["extensions", "https://example.com/metadata"]` selects one entry extension. A path can select an entire array, such as a contributor's attestations, but cannot select an individual array element.

Record the issuance time in `issuedAt` and, optionally, an expiry time in `expiresAt`. To produce `jws`, resolve each path and sort the resulting path/value pairs using the specification's ordering rule. Construct the payload with those pairs, the signature context, the exact `signer` and `profile` values, and the timestamps. JCS (RFC 8785) canonicalizes that payload before JWS signing. The detached JWS stores no second copy of the values. Follow the full specification for the exact payload and verification algorithm.

Signing one contributor's manifest permits another contributor to add a separate manifest and signature without invalidating the first signature. Changing a value selected by the first signature invalidates it. Selecting an entire map or array also covers its membership and all nested values.

## Authenticating the signer

First select the procedure named by `profile`, checking that it is supported and permitted by local policy. Other signatures can be evaluated independently.

For the example above, `profile: "did-web-v1"` selects the `did:web` Signer Profile, which verifies Acme's endorsement using `signer: "did:web:acme-corp.com"` and the protected JWS header's `kid: "did:web:acme-corp.com#release-signing-key"`. The DID in `kid` must exactly match `signer`, and the header's `alg` must be `ES256`.

The verifier retrieves Acme's root DID document from `https://acme-corp.com/.well-known/did.json` and checks that it authorizes the selected P-256 key through `assertionMethod`. A key listed only for authentication or key agreement does not satisfy this profile. The verifier uses the authorized key to check the JWS against the reconstructed payload, including its exact `signer` and `profile` values. Changing the profile label therefore invalidates the signature. The identity becomes authenticated only after these checks succeed.

For the selected manifest to count as Acme's claims, its identity key must match the authenticated `signer`. Publisher authority requires an additional check: Acme's root `did:web` domain must match the publisher domain of the entry's standard `urn:air` identifier. An independent contributor can authenticate with its own DID without thereby becoming the artifact's publisher.

Consumers should:

1. Select the named, supported, and locally permitted profile (`did-web-v1` here). Check path validity and required field coverage, including `identifier`, `type`, `digest`, and any declared `version` together for artifact binding.
2. Reconstruct and canonicalize the payload, including its context, exact `signer` and `profile` values, and timestamps.
3. Check that the DID in the protected `kid` exactly matches `signer`, resolve the key, check assertion authorization, and verify the ES256 JWS.
4. Check freshness and the authority needed for the intended endorsement; check the contributor identity key when accepting a manifest as that contributor's claims.
5. Verify the artifact bytes against the signed entry digest, and evaluate referenced evidence according to its format and local policy.

If a check fails, do not treat the affected claims as verified. Consumers can retain an unverified entry, retry temporary resolution failures, or reject it according to local policy. A valid signature proves an endorsement, not that the artifact is safe or every claim is true.

## Catalog signatures

The catalog root can also carry `signatures`, with paths relative to the catalog object. To select all Host Info fields, use `["host"]`. To select one field, use a path such as `["host", "documentationUrl"]`.

A catalog signature covering the entire `entries` array includes all nested entry signatures. Adding a nested signature therefore changes that selected value. A root signature over only selected fields does not authenticate an entire catalog snapshot; use the coverage requirements in the specification for that purpose.

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
  "trustManifests": {
    "did:web:acme-corp.com": {
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
      ]
    }
  },
  "signatures": [
    {
      "signer": "did:web:acme-corp.com",
      "profile": "did-web-v1",
      "paths": [
        ["identifier"],
        ["type"],
        ["digest"],
        ["trustManifests", "did:web:acme-corp.com"]
      ],
      "issuedAt": "2026-03-15T10:00:00Z",
      "jws": "eyJhbGciOiJFUzI1NiIsImtpZCI6ImRpZDp3ZWI6YWNtZS1jb3JwLmNvbSNyZWxlYXNlLXNpZ25pbmcta2V5In0..detached-jws-signature"
    }
  ]
}
```

## Next steps

See the [Full Specification](../specification.md) for normative path rules, payload construction, the `did:web` profile, publisher authority, and conformance requirements.
