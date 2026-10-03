---
icon: material/file-document
---

# Full Specification

The AI Catalog specification is published as a W3C-style normative document.

**[View the full specification :material-arrow-right:](https://agent-card.github.io/ai-catalog/spec/){ .md-button .md-button--primary }**

## What's in the specification

The specification covers:

- **Core schema** — formal definitions for AI Catalog, Catalog Entry, Host Info, Publisher, and all fields
- **Trust Manifests and signatures** — contributor claims, attestations, provenance links, selected-field signing, and verification procedures
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
