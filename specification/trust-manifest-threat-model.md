# Trust Manifest Threat Model

**Status:** Informational

**Date:** 2026-06-20

**Methodology:** STRIDE (Spoofing, Tampering, Repudiation, Information
disclosure, Denial of service, Elevation of privilege).

**Scope:** The optional Trust Manifest extension of the AI Catalog
specification — its data model, signature and verification procedures,
and the conformance levels that depend on it. Catalog mechanisms that
are not trust-bearing (media-type routing, nesting for organization,
version selection) are in scope only where they affect trust decisions.

This document is the security analysis that motivates the normative
hardening in [ai-catalog.md](ai-catalog.md) and the decisions recorded
in [ADR-0019](../adr/0019-trust-manifest-artifact-binding.md) and
[ADR-0009](../adr/0009-trust-manifest-substitution.md), together with the
scope decision in [ADR-0026](../adr/0026-remove-host-trust-manifests.md). It
exists to answer the substitution-attack concern raised in ADR-0009: *"The
substitution attack of changing out the trust manifest is very real,
especially if there's no tamper-proofness built in."*

## 1. System Decomposition

### 1.1 External entities

Publisher
: Produces an artifact and (optionally) signs a Trust Manifest that
  makes verifiable claims about it. Holds a signing key.

Catalog Host
: Serves the AI Catalog document. May or may not be the publisher.
  Controls the bytes of the catalog at rest and in transit.

Consumer / Client
: Fetches the catalog, resolves entries, verifies trust metadata, and
  makes a trust decision (e.g., install, invoke, or surface an
  artifact to a user or agent). The asset being defended is the
  *correctness of this decision*.

Third-party endpoints
: Servers referenced from a Trust Manifest: attestation documents
  (`attestation.uri`), key material (DID documents, JWKS URLs, SPIFFE
  Workload API), provenance statements (`statementUri`,
  `registryUri`).

OCI registry
: Optional content-addressed distribution channel (Layer 3).

Attacker
: See threat agents in section 3.

### 1.2 Data stores

- Catalog document (`application/ai-catalog+json`)
- Trust Manifest (peer element on an entry)
- Artifact bytes (served at `entry.url` or inlined in `entry.data`)
- Attestation documents
- Key material (DID documents, JWK Sets, X.509 SVIDs)
- Provenance statements
- OCI registry content + signatures (Cosign / Notation)

### 1.3 Processes

1. Catalog fetch and parse
2. Entry / nested-catalog resolution
3. Trust Manifest signature verification
4. Signer key resolution (from `identity`)
5. Artifact fetch and digest computation
6. Attestation fetch and validation
7. Provenance evaluation

### 1.4 Data-flow and trust boundaries

```mermaid
flowchart LR
    Pub[Publisher] -->|signs manifest| Cat[(Catalog Document)]
    Host[Catalog Host] -->|serves| Cat
    Cat -->|B1 TLS| Cons[Consumer]
    subgraph Consumer verification
        Cons --> Ver[Verify signature]
        Ver --> KeyRes[Resolve key]
        Cons --> ArtFetch[Fetch + digest artifact]
        Cons --> AttFetch[Fetch + validate attestation]
    end
    KeyRes -->|B4| KeyEP[(Key endpoint: DID/JWKS/SPIFFE)]
    ArtFetch -->|B1/B5| Art[(Artifact)]
    AttFetch -->|B4/B5| AttEP[(Attestation / provenance endpoints)]
    Reg[(OCI registry)] -. B2 alt .-> Cons
```

Trust boundaries:

- **B1 — Transport.** Network path between the consumer and any
  server. Crossed by TLS. A network attacker without a valid
  certificate cannot read or alter traffic, but TLS says nothing about
  the authenticity of the *content* an authorized-but-malicious or
  compromised origin returns.
- **B2 — Catalog-document write.** Who can change the bytes of the
  catalog document at rest (hosting account, CDN, object store, DNS
  control, repository). This is the boundary the substitution attack
  crosses.
- **B3 — Publisher signing key.** The boundary between data an
  attacker can author and data that requires the publisher's private
  key.
- **B4 — Third-party endpoints.** Servers whose URLs appear *inside*
  the (possibly attacker-controlled) Trust Manifest. The consumer is
  induced to contact them.
- **B5 — Consumer verification egress.** The consumer's own network
  egress while fetching manifest-referenced URLs (SSRF surface).

## 2. Assets

| # | Asset | Why it matters |
|---|-------|----------------|
| AS1 | Integrity + authenticity of the artifact ↔ trust binding | The whole point of the Trust Manifest: that *these* claims describe *this* artifact. |
| AS2 | Publisher signing keys | Compromise lets an attacker forge authentic-looking trust. |
| AS3 | The consumer's trust decision | The ultimate target — install/invoke a malicious artifact under a trusted label. |
| AS4 | Availability of catalog resolution | Consumers depend on resolving catalogs to find tools. |
| AS5 | Consumer privacy / telemetry | Fetches triggered by verification can leak who is evaluating what, and from where. |

## 3. Threat Agents and Assumptions

| ID | Agent | Capability | In scope |
|----|-------|------------|----------|
| A1 | Network attacker | On-path, **cannot** break TLS | Yes (bounded) |
| **A2** | **Catalog-write attacker** | Can modify the catalog document (compromised hosting account, CDN edge, object-store creds, DNS hijack, MITM of a non-TLS origin, or a malicious mirror). **Cannot** obtain the publisher's private key. | **Yes — primary** |
| A3 | Malicious publisher | Authors and signs manifests with a key it legitimately controls | Yes |
| A4 | Compromised third-party endpoint | Controls an attestation/key/provenance URL referenced by a manifest | Yes |
| A5 | Malicious nested/federated author | Authors a sub-catalog that a parent delegates to | Yes |
| A6 | Key-compromise / stale-key attacker | Holds a previously valid (revoked or rotated) publisher key, or replays old signed material | Yes |

Out of scope: breaking TLS or the underlying hash/signature
primitives; compromise of the consumer's own host; supply-chain
compromise of the artifact *before* the publisher signs it (the
manifest can only attest to what the publisher saw).

## 4. STRIDE Analysis

Each threat references the finding IDs (F1–F10) carried in the
companion review and maps to a mitigation in section 6.

### 4.1 Spoofing

| ID | Threat | Boundary | Agent | Finding |
|----|--------|----------|-------|---------|
| S1 | **Self-asserted identity.** Key resolution derives the signer's key *from* the `identity` URI in the manifest. A catalog-write attacker substitutes both `identity` and the key endpoint, signs with their own key, and the signature verifies. Verification proves "signed by whoever owns this identity," not "signed by a publisher I trust." | B2/B3 | A2 | F3 |
| S2 | **Publisher spoofing.** `publisher.identifier`/`displayName` live on the entry, outside any signature; an attacker edits them to impersonate a reputable vendor. | B2 | A2 | F9 |
| S3 | **Host spoofing.** `host.identifier` is attacker-controllable when the catalog is compromised; DID-service-endpoint checks only prove internal consistency of attacker-chosen data. | B2 | A2 | — |

### 4.2 Tampering

| ID | Threat | Boundary | Agent | Finding |
|----|--------|----------|-------|---------|
| **T1** | **Artifact substitution under a valid signature (headline).** The `signature` covers only the Trust Manifest JSON. The artifact is referenced by `entry.url`/`data`/`mediaType`, which sit *outside* the signed bytes. The only binding is `identity == entry.identifier`. An attacker keeps the publisher's validly-signed manifest, leaves `identifier` intact, and repoints `url` to a malicious artifact. Signature still verifies. `provenance.sourceDigest` is OPTIONAL and denotes the *source* (`publishedFrom`), not the served artifact, so it does not close the gap. | B2 | A2 | F1 |
| T2 | **Unsigned manifest tampering.** Level 3 ("Trusted Catalog") requires only that a `trustManifest` be *present*, not signed. An attacker freely rewrites every claim in an unsigned manifest. The "Trusted" label implies cryptographic assurance that is not enforced. | B2 | A2 | F2 |
| T3 | **Catalog-level structural tampering.** Nothing signs the `entries` array or `host`. Even with per-entry signed manifests, an attacker injects new (malicious, unsigned) entries, deletes entries, or reorders/selects versions. Only OCI Layer 3 addresses this today. | B2 | A2/A5 | F6 |

### 4.3 Repudiation

| ID | Threat | Boundary | Agent | Finding |
|----|--------|----------|-------|---------|
| R1 | **No issuance time / audit anchor.** A signed manifest carries no `issuedAt`, so a consumer cannot tell *when* a claim was made or which artifact version it covered, weakening dispute resolution and rollback detection. | B3 | A6 | F5 |
| R2 | **Half-specified provenance signatures.** `statementUri` + `signatureRef` exist but have no verification procedure, so provenance statements cannot be relied on as non-repudiable evidence. | B4 | A4 | F8 |

### 4.4 Information disclosure

| ID | Threat | Boundary | Agent | Finding |
|----|--------|----------|-------|---------|
| I1 | **SSRF.** Verification instructs the consumer to fetch attacker-influenced URLs (`attestation.uri`, `statementUri`, `registryUri`, key URLs). A crafted manifest can target internal/loopback/link-local/cloud-metadata addresses from the consumer's network position. | B4/B5 | A2/A4 | F7 |
| I2 | **Verification telemetry / tracking.** Fetches reveal which consumer (IP, identity) is evaluating which artifact, and when. Logo and attestation fetches leak the same. | B1/B5 | A2/A4 | F7 |

### 4.5 Denial of service

| ID | Threat | Boundary | Agent | Finding |
|----|--------|----------|-------|---------|
| D1 | **Oversized / slow verification fetches.** `attestation.size` is OPTIONAL; large attestation documents, large inline `data`, or slow endpoints exhaust consumer memory/connections during verification. | B4/B5 | A2/A4 | F7 |
| D2 | **Nested / circular catalog expansion.** Deep or circular nested catalogs amplify work. (Already addressed by the depth limit and visited-set guidance; retained here for completeness.) | B2 | A2/A5 | — |

### 4.6 Elevation of privilege

| ID | Threat | Boundary | Agent | Finding |
|----|--------|----------|-------|---------|
| E1 | **Signature-algorithm confusion.** The spec mandates detached JWS but constrains no algorithms. Acceptance of `alg: none` or symmetric-vs-asymmetric key confusion (using a public key as an HMAC secret) lets an attacker forge a "valid" signature with no private key. | B3 | A2 | F4 |
| E2 | **Rollback / downgrade.** With no freshness binding and multi-version entries, an attacker replays an older, validly-signed manifest plus its older (e.g., since-patched) artifact, or a manifest signed before a key was revoked. The consumer accepts authentic-but-stale trust. | B2/B3 | A6 | F5 |

## 5. Attack Scenarios

**SC-1 — URL swap under a valid signature (primary).** Acme publishes
`urn:acme:agent:finance` with a manifest signed by
`did:web:acme-corp.com`. An attacker who compromises Acme's CDN leaves
the manifest byte-for-byte intact (so the signature and
`identity == identifier` checks pass) and changes only `entry.url` to a
look-alike host serving a trojaned agent. A Layer-2 consumer "verifies
the signature," sees green, and installs malware. *Closed by F1
mitigation: the signed manifest MUST commit to the artifact digest.*

**SC-2 — False trust at Level 3.** A catalog advertises Level 3 with
unsigned manifests. A consumer treats "Trusted Catalog" as
cryptographic assurance and accepts attacker-rewritten attestations.
*Closed by F2 mitigation: signatures REQUIRED at Level 3.*

**SC-3 — Self-signed substitution.** Attacker replaces `identity` with
`did:web:attacker.example`, repoints the key endpoint to their own
JWKS, and signs the whole (malicious) manifest. Every internal check
passes. *Closed by F3 mitigation: out-of-band trust anchoring —
verified signature ≠ trusted publisher.*

**SC-4 — alg:none forgery.** Attacker sets the JWS header `alg` to
`none` (or `HS256` keyed with the publisher's public key) and forges a
manifest with no private key. *Closed by F4 mitigation: algorithm
allowlist.*

**SC-5 — Downgrade.** A patched v2.1 exists, but the attacker re-serves
the still-validly-signed v2.0 manifest + artifact. *Closed by F5
mitigation: `issuedAt`/`expiresAt` + anti-rollback guidance.*

**SC-6 — Verification SSRF.** A manifest sets
`attestation.uri = http://169.254.169.254/latest/meta-data/…`; the
consumer's verifier fetches it and exfiltrates cloud credentials.
*Closed by F7 mitigation: safe-fetching rules.*

**SC-7 — Entry injection.** Attacker appends an unsigned malicious
entry to a catalog full of legitimately signed entries. *Mitigated by
F6: catalog-level signature and/or OCI content-addressing.*

## 6. Controls: Existing vs. Proposed

| Finding | Threats | Existing control | Proposed normative mitigation | Spec section |
|---------|---------|------------------|-------------------------------|--------------|
| F1 | T1 | Detached JWS over manifest; OPTIONAL `sourceDigest` | Signed `subject` `{url?, mediaType, digest}` committing to the served artifact; REQUIRED whenever signed | Trust Manifest → Subject Binding |
| F2 | T2 | Level 3 requires manifest presence | Level 3 MUST carry a signed manifest with subject binding + `issuedAt` | Conformance Level 3 |
| F3 | S1 | Key resolution from `identity` | Trust Anchoring subsection: verified signature ≠ trusted publisher; anchor identity to an out-of-band root | Verification → Trust Anchoring |
| F4 | E1 | "detached JWS" | Algorithm allowlist; reject `alg:none` + symmetric; validate `alg`, pin `kid` | Verification → Signature Algorithms |
| F5 | R1, E2 | none | `issuedAt` (REQUIRED when signed) + `expiresAt`; anti-rollback + revocation guidance | Trust Manifest + Verification |
| F6 | T3 | OCI Layer 3 (informative) | OPTIONAL catalog-level `signature` (RECOMMENDED at L3) + OCI reference | Catalog signature + Security Considerations |
| F7 | I1, I2, D1 | none | Safe-Fetching subsection: size caps, timeouts, no redirects to private ranges, host allowlist | Verification → Safe Fetching |
| F8 | R2 | Fields only | Provenance-statement verification procedure | Verification → Provenance statements |
| F9 | S2 | `identity == identifier` | Bind/flag publisher fields; advisory unless covered by attestation | Verification → Publisher identity |
| F10 | — | JCS | Note JCS numeric round-trip caveat for signed payloads | Verification → Signatures |

## 7. Comparison with the Sigstore Architecture

The Trust Manifest derives its model from Sigstore — sign an artifact,
associate it with an identity, and make the evidence verifiable — but it
reproduces only part of Sigstore's guarantees natively. Sigstore secures
software supply chains with three cooperating roles:

- **Cosign** signs the artifact's *digest* (not just metadata).
- **Fulcio** is a certificate authority that binds an ephemeral signing
  key to an OIDC identity and issues a short-lived certificate, so
  identity is asserted by a *trusted CA* rather than self-declared.
- **Rekor** is an immutable, append-only **transparency log** that
  witnesses each signing event (digest + signature + certificate),
  giving public auditability, non-repudiation, freshness, monitoring,
  and rollback detection (inclusion and consistency proofs).
- A **TUF**-managed root of trust distributes and rotates the Fulcio and
  Rekor public keys.

Verifying a Sigstore artifact means: verify the signature with the
certificate's public key; confirm the certificate identity matches an
*expected* identity; verify the certificate against Sigstore's root of
trust; and verify proof of inclusion in Rekor. The artifact is thereby
proven to come from its expected source and to be untampered.

### 7.1 Mapping

| Sigstore property | Provides | Trust Manifest today | Gap (finding) |
|-------------------|----------|----------------------|---------------|
| Cosign signs the artifact **digest** | Artifact ↔ signature binding | `subject.digest` in the signed payload (this revision) | Closed (F1) |
| **Fulcio** CA binds identity via OIDC; short-lived cert | Identity is CA-attested, not self-asserted | `identity` is self-declared; key resolved *from* it; anchoring pushed to the consumer | Partially open (F3) — anchoring is required but no CA is specified |
| **Rekor** transparency log | Non-repudiation, freshness, monitoring, rollback detection | No transparency-log equivalent; `issuedAt`/`expiresAt` give weak local freshness only | Open (F5, R1, E2) |
| **Keyless / ephemeral keys** | No long-lived key management or revocation problem | Long-lived publisher keys (DID/JWKS); inherits key-management + revocation burden | Open (residual AS2) |
| **TUF** root of trust | Secure distribution + rotation of verification keys | Trust-anchor bootstrapping unspecified | Open (residual) |
| Verify expected identity + cert chain + Rekor inclusion | Full verification chain | Verify signature + `subject` + out-of-band anchor; no inclusion proof | Partially open |

### 7.2 Implications

- **What the Trust Manifest now matches.** With `subject` binding, the
  Trust Manifest reproduces Cosign's core property: a signature commits
  to a specific artifact digest. This is the single most important
  Sigstore guarantee and directly closes the substitution attack (T1).
- **What it delegates.** The Trust Manifest deliberately does not
  operate a CA or a transparency log. It is a *format that can carry*
  Sigstore-style evidence rather than a replacement for Sigstore
  services. Consequently it leans on out-of-band **trust anchoring**
  (section 4.1 / F3) to substitute for Fulcio's CA-attested identity.
- **What is still weaker than Sigstore.** Without a Rekor-equivalent,
  the Trust Manifest cannot offer public auditability, third-party
  witnessing, or strong rollback detection; `issuedAt`/`expiresAt` are a
  local, unwitnessed approximation. Long-lived publisher keys reintroduce
  the key-management and revocation problems Sigstore was designed to
  eliminate.

### 7.3 Recommended convergence

To close the remaining gaps, the specification SHOULD make Sigstore
evidence first-class rather than reinventing it:

1. **Carry Fulcio/Cosign evidence.** Define an attestation `type` (e.g.,
   `sigstore-bundle`) whose document is a Sigstore bundle (certificate +
   signature + Rekor inclusion proof). Verifying it gives CA-attested
   identity and log inclusion "for free," and the `subject.digest`
   already aligns with what Cosign signs.
2. **Anchor via the Sigstore/TUF root.** Permit the trust anchor
   (section 4.1) to be Sigstore's TUF-managed root, so identity is
   verified against Fulcio rather than a hand-maintained allowlist.
3. **Prefer transparency-log inclusion over local freshness.** Where a
   Rekor (or compatible) inclusion proof is available, consumers SHOULD
   prefer it to `issuedAt`/`expiresAt` for freshness, non-repudiation,
   and rollback detection.
4. **Favor keyless/ephemeral signing.** Treat long-lived publisher keys
   as the fallback, not the default, to avoid the revocation burden.

This keeps the Trust Manifest's artifact-agnostic, peer-element design
while letting trust-sensitive deployments inherit Sigstore's full chain
(CA identity + transparency + keyless) instead of a weaker re-implementation.

## 8. Residual Risks

- **Catalog-operator authentication.** HTTPS from an expected domain can
  authenticate the transport endpoint, but a DID service-endpoint check alone
  does not authenticate attacker-selected Host Info. A catalog signature can
  protect the snapshot only after its signer and key are independently
  authorized; the catalog-signature profile does not yet define that
  authorization.
- **Trust-anchor bootstrapping.** Anchoring shifts trust to an
  out-of-band root (pinned allowlist, registry vetting, DID method with
  domain control). The strength of the whole system reduces to how that
  root is established and maintained; the spec can require anchoring but
  cannot supply the root.
- **Publisher-key compromise (AS2).** A subject-bound, signed manifest
  is only as trustworthy as the publisher's key hygiene. Short-lived
  keys, revocation checking, and OCI/Cosign counter-signatures reduce
  but do not eliminate this.
- **Pre-signing supply-chain compromise.** If a malicious artifact is
  signed by a legitimate publisher, the manifest faithfully attests to
  a bad artifact. Out of scope here; addressed by build-provenance
  (SLSA) practices upstream.
- **Catalog availability (AS4).** Even with full integrity, an attacker
  who can delete the catalog or block resolution causes denial of
  service; mitigated operationally (caching, mirrors, OCI), not by the
  trust model.
- **Metadata privacy (AS5).** Verification fetches inherently reveal
  some consumer activity; Data-URI attestations/logos and host
  allowlists reduce, but cannot fully remove, this exposure.
