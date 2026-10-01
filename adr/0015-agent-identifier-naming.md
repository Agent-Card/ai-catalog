# ADR 0015: Align Agent Identifier Naming with Domain-Anchored URN Standards

## Status
Accepted

## Date
2026-05-13 (Proposed), 2026-05-28 (Accepted), 2026-06-25 (Updated)

**Participants:** Pamela Dingle (Microsoft), Sam Betts (Cisco), Junjie Bu (Google), Darrel Miller (Microsoft), Alan Blount (Google), Srinivas Krishnan (Google), Krishna Thota (Google), Tadas Antanavicius (Pulse MCP), Ramiz Polic (Cisco), Jeffrey Damick (Amazon)

**Later clarification:** [ADR-0027](0027-did-web-entry-signature-profile.md)
narrows the interoperable v1 signature profile to a root `did:web` issuer and
assigns runtime or workload identity to separate profiles. The logical-name and
cryptographic-issuer separation established here remains unchanged.

## Context
The `ai-catalog` specification originally recommended using URNs or URIs for the `identifier` field in catalog entries, but did not mandate a specific format. This led to inconsistency in examples and potential interoperability issues across different registries and orchestrators.

To ensure global federation and industry-wide interoperability, we need a standardized, secure naming protocol for AI actors. However, we also need to preserve flexibility for organizations running local, private, or closed catalog instances that do not participate in public federation.

## Decision
We will define the `identifier` field as an open text format, while strongly recommending and standardizing the domain-anchored `urn:air` scheme for open or federated ecosystems.

### 1. Open/Flexible Naming (Local Systems)
The `identifier` field remains an open string format (any valid URI or URN is accepted). Local, private, or closed systems can use any custom identifier formats as needed. When a non-standard format is used, client implementations are responsible for parsing and processing it accordingly.

### 2. Standardized Naming Format (Highly Recommended / Federated Systems)
For open, public, or federated systems where global discoverability is required, the identifier **MUST** follow the standard URN format:
`urn:air:{publisher}:{namespace}:{name}`

- `publisher`: The domain name of the publisher organization (e.g., `example.com`).
- `namespace`: Optional segment(s) separated by `:` to categorize the artifact (e.g., `mcp`, `skill`, `agent`, `finance:agent`).
- `name`: The stable, unique logical name of the artifact within that publisher's namespace.

*Examples:*
- `urn:air:example.com:skill:code-review`
- `urn:air:example.com:mcp:weather`

All standard examples and specifications will be updated to follow this URN convention.

## Rationale
- **Interoperability and Federation**: Federated search/discovery systems require a predictable, globally unique, and stable naming scheme to successfully index, cache, and resolve routing.
- **Local Flexibility**: Forcing strict URN formatting on internal or legacy deployments could create unnecessary friction and integration blockages.
- **Nomenclature Stability**: The logical URN acts as a stable contract. Relocating workloads or changing target URLs does not break client routing or caches.
- **Separation of Concerns**: It separates the logical name used for discovery and routing from the cryptographic identity used for trust verification. The `identity` field in the `trustManifest` can utilize various security schemas for cryptographic verification (e.g., SPIFFE, DID, DNS), while this URN-based `identifier` provides a consistent and stable naming mechanism that remains constant even if the underlying security infrastructure changes.

## Consequences
- **Compatibility**: Existing catalogs using non-compliant formats will either continue working as local identifiers or need to migrate if they join a federated system.
- **Ecosystem Consistency**: Public tools, indexes, and reference registries will enjoy a unified naming structure for efficient lookups.
