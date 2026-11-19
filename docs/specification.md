---
icon: material/file-document
---

# Full Specification

The AI Catalog specification is published by the AI Catalog project as the
official **v0.9 specification**, a **Release Candidate for v1.0**. It is ready
for implementation and interoperability feedback, but is **not the final
v1.0 specification**.
Requirements may change in response to feedback before final publication.

Documentation examples continue to use `"specVersion": "1.0"` to illustrate
the planned final version.

Implementations use `"specVersion": "0.9"` and should separately record the
specification revision or commit they implement. Report implementation
experience, ambiguities, and interoperability issues through
[GitHub issues](https://github.com/Agent-Card/ai-catalog/issues).

**[View the full specification :material-arrow-right:](https://agent-card.github.io/ai-catalog/spec/){ .md-button .md-button--primary }**

## What's in the specification

The specification covers:

- **Core schema** — formal definitions for AI Catalog, Catalog Entry, Host Info, Publisher, and all fields
- **Trust Manifests and signatures** — contributor claims, attestations, provenance links, and signing and verification procedures
- **Discovery** — well-known URI, link relation headers, and agent-driven discovery
- **Conformance levels** — normative requirements for Minimal, Discoverable, and Trusted catalogs
- **Version handling** — compatibility rules for producers and consumers
- **Security considerations** — trust layers, catalog poisoning, typosquatting, embedded content safety
- **CDDL schema** — formal machine-readable schema

## Relationship to these docs

The developer documentation you're reading now is a practical guide aimed at getting you productive quickly. It draws from the specification but is not normative.

Informative ecosystem and distribution mappings are maintained separately
in the [Mappings](mappings/index.md) section.

When building a production implementation, refer to the specification for precise requirements — especially for Trust Manifest verification, signature algorithms, and conformance obligations.
