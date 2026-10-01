# Adding Trust

The Trust Manifest is an optional extension to AI Catalog entries that enables verifiable identity, compliance attestations, and provenance tracking. You don't need it to publish a catalog — but it's valuable for regulated environments, enterprise deployments, and public registries.

## When do you need trust?

| Use case | Level needed |
|---|---|
| Internal tooling, quick prototyping | No trust metadata needed |
| Public tools, developer marketplace | Consider publisher identity |
| Enterprise deployments, compliance-sensitive | Attestations (SOC2, ISO, HIPAA) |
| High-assurance environments | Signed Trust Manifests + provenance |

## Conformance levels

Trust builds on the three conformance levels:

=== "Level 1 — Minimal"

    Just entries with types and URLs. No host, no trust metadata.

    ```json
    {
      "specVersion": "1.0",
      "entries": [...]
    }
    ```

=== "Level 2 — Discoverable"

    Adds a `host` object and is served at `/.well-known/ai-catalog.json`.

    ```json
    {
      "specVersion": "1.0",
      "host": {
        "displayName": "Acme Corp",
        "identifier": "did:web:acme-corp.com"
      },
      "entries": [...]
    }
    ```

=== "Level 3 — Trusted"

    Adds signed, subject-bound Trust Manifests with verifiable identity, attestations, and provenance.

    ```json
    {
      "specVersion": "1.0",
      "host": { ... },
      "entries": [
        {
          "identifier": "urn:air:acme-corp.com:a2a:finance",
          "type": "application/a2a-agent-card+json",
          "url": "...",
          "trustManifest": {
            "identity": "did:web:acme-corp.com:a2a:finance",
            "subject": {
              "identifier": "urn:air:acme-corp.com:a2a:finance",
              "type": "application/a2a-agent-card+json",
              "digest": "sha256:9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
            },
            "issuedAt": "2026-03-15T10:00:00Z",
            "signature": "eyJhbGciOiJFUzI1NiJ9..detached-jws-signature"
          }
        }
      ]
    }
    ```

## Trust Manifest structure

A Trust Manifest is an object on a Catalog Entry. It always requires `identity` and must contain substantive trust evidence. A signed Trust Manifest also requires `subject` and `issuedAt`.

| Field | Requirement | Description |
|---|---|---|
| `attestations` | Optional | Array of compliance and identity attestation objects |
| `expiresAt` | Optional | Time after which a signed Trust Manifest is stale |
| `extensions` | Optional | Named extension map for custom trust data; included in the signed payload when the manifest is signed (see [Extensions](creating-a-catalog.md#extensions)) |
| `identity` | Required | Globally unique artifact URI. Its trust domain must align with the publisher domain in the containing entry's `identifier`. |
| `identityType` | Optional | Type hint for the identity URI: `"did"`, `"spiffe"`, or `"dns"` |
| `issuedAt` | Required when signed | Time at which a signed Trust Manifest was issued |
| `privacyPolicyUrl` | Optional | URL to the privacy policy |
| `provenance` | Optional | Array of provenance links (source code, OCI digests) |
| `signature` | Required at Level 3 | Detached JWS signature over the Trust Manifest content |
| `subject` | Required when signed | Logical artifact release and exact representation covered by a signature |
| `termsOfServiceUrl` | Optional | URL to the terms of service |
| `trustSchema` | Optional | Describes the trust framework applied |

!!! tip "Attestation document format"
    Attestation documents are not restricted to any particular format — they can be human-readable (e.g., a PDF audit report) or machine-readable for automated verification (e.g., JWTs, Verifiable Credentials).

## Adding publisher identity

The simplest trust step is asserting publisher identity. Use an attestation of type `"publisher-identity"`:

```json
"trustManifest": {
  "identity": "urn:air:acme-corp.com:a2a:finance",
  "attestations": [
    {
      "type": "publisher-identity",
      "uri": "https://trust.acme-corp.com/certs/publisher.jwt",
      "description": "Verifies did:web:acme-corp.com as publisher"
    }
  ]
}
```

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

## Signing the Trust Manifest

A signature turns the Trust Manifest from advisory metadata into tamper-evident assertions. Without a signature, an attacker who can modify the catalog can also substitute the Trust Manifest with forged claims.

The `signature` field holds a detached JWS (RFC 7515):

```json
"trustManifest": {
  "identity": "did:web:acme-corp.com:a2a:finance",
  "attestations": [...],
  "subject": {
    "identifier": "urn:air:acme-corp.com:a2a:finance",
    "type": "application/a2a-agent-card+json",
    "digest": "sha256:9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
  },
  "issuedAt": "2026-03-15T10:00:00Z",
  "signature": "eyJhbGciOiJFUzI1NiJ9..detached-jws-signature"
}
```

The signature is computed over the Trust Manifest content using JCS (RFC 8785) canonicalization before signing. The signing key is identified in the JWS header and resolved via the identity's DID document, HTTPS endpoint, SPIFFE bundle, or DNS TXT record.

Clients verifying signatures should:

1. Extract the `signature` field and remove it from the object
2. Canonicalize the remaining Trust Manifest using JCS
3. Resolve the signing key from the identity URI
4. Verify the JWS signature
5. Confirm `subject.identifier` and `subject.type` match the Catalog Entry; confirm the entry and subject versions are both absent or both present and exactly equal; when `subject.url` is present, confirm it matches the entry URL
6. Verify the artifact content against `subject.digest`

## Trust layers

Trust is progressive — use the layer appropriate to your threat model:

| Layer | What it provides | How it works |
|---|---|---|
| **0 — TLS** | Prevents eavesdropping and casual tampering | HTTPS certificate chain |
| **1 — Provenance digests** | Detects artifact tampering in transit | Hash the fetched artifact, compare to `sourceDigest` |
| **2 — Signed Trust Manifest** | Binds signed claims to an artifact release | Verify the JWS and confirm that the signed subject matches the entry and artifact |
| **3 — OCI content-addressing** | Makes modification structurally impossible | All content addressed by digest in an OCI registry |

For most use cases, Layer 0 (HTTPS) + Layer 2 (signed Trust Manifest) provides a strong baseline.

## Complete example

A Trust Manifest with identity, compliance attestation, provenance, and signature:

```json
{
  "identifier": "urn:air:acme-corp.com:a2a:finance",
  "type": "application/a2a-agent-card+json",
  "url": "https://agents.acme-corp.com/finance",
  "publisher": {
    "identifier": "did:web:acme-corp.com",
    "displayName": "Acme Financial Corp"
  },
  "trustManifest": {
    "identity": "did:web:acme-corp.com:a2a:finance",
    "trustSchema": {
      "identifier": "urn:trust:acme-enterprise-v1",
      "version": "1.0",
      "governanceUri": "https://acme-corp.com/trust/governance.pdf",
      "verificationMethods": ["did", "x509"]
    },
    "attestations": [
      {
        "type": "publisher-identity",
        "uri": "https://trust.acme-corp.com/certs/publisher.jwt",
        "description": "Verifies did:web:acme-corp.com as publisher"
      },
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
    "privacyPolicyUrl": "https://acme-corp.com/legal/privacy",
    "termsOfServiceUrl": "https://acme-corp.com/legal/terms",
    "subject": {
      "identifier": "urn:air:acme-corp.com:a2a:finance",
      "url": "https://agents.acme-corp.com/finance",
      "type": "application/a2a-agent-card+json",
      "digest": "sha256:9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
    },
    "issuedAt": "2026-03-15T10:00:00Z",
    "signature": "eyJhbGciOiJFUzI1NiJ9..detached-jws-signature"
  }
}
```

## Next steps

For the full normative requirements on Trust Manifests — key resolution procedures, JCS canonicalization details, verification algorithms — see the [Full Specification](../specification.md).
