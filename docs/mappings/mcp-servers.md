# Mapping to MCP Servers

This guide describes how **remote (HTTP-connectable) MCP servers**
map to AI Catalog, enabling them to be discovered alongside other AI
artifacts through a unified catalog. The documented, supported path is
to reference each server's **MCP Server Card**
([SEP-2127](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2127))
as the artifact content of a Catalog Entry.

## Overview

An MCP Server Card is a static discovery document for an individual
HTTP-based MCP server, describing its identity and how to connect to it.
A Catalog Entry references the card wherever the server publishes it, as
in the examples below. See
[SEP-2127](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2127)
for the Server Card's schema, fields, and hosting conventions.

In AI Catalog terms, the Server Card is the **artifact content** — the
native metadata that a Catalog Entry references via its `url`, declared
with the known type `application/mcp-server-card+json`. The AI Catalog
does not duplicate or redefine Server Card fields; it provides the
discovery and trust layer that the Server Card does not address.

AI Catalog and MCP Server Cards address different layers of discovery:

MCP Server Card (per-server)
: What does this specific MCP server offer? What transport does it
  use? What tools and resources are available? What authentication
  is required?

AI Catalog (cross-artifact)
: What artifacts does this domain offer? Who published them? Can I
  trust them? What other artifact types are available alongside MCP
  servers?

## Conceptual Mapping

| MCP Server Card | AI Catalog Equivalent |
|:---|:---|
| Server Card document (whole file) | Artifact content via entry `url` (type `application/mcp-server-card+json`) or `data` |
| Server `name` (reverse-DNS identifier) | Entry `identifier` (mapped to the `urn:air:{publisher}:{namespace}:{name}` URN form — e.g. `urn:air:acme-corp.com:mcp:finance-server`) |
| `title` | Stays in the Server Card (which carries its own `title`); entry `displayName` is omitted unless the artifact lacks a name |
| `description` | Stays in the Server Card (which carries its own `description`); entry `description` is omitted to avoid duplicating a value that can drift |
| `version` | Stays in the Server Card (which carries its own `version`); entry `version` is omitted to avoid duplicating a value that can drift (a remote MCP server serves one Server Card, so a catalog never lists multiple versions of it) |
| transport / capabilities / tools / resources / auth | Inside the Server Card — not surfaced in the catalog |
| `repository` | Stays in the Server Card (which carries its own `repository`); omitted from the entry to avoid duplicating a value that can drift — catalog-level source/provenance links surface through the Trust Manifest when needed |
| *(not in the Server Card)* | Entry `publisher` |
| *(not in the Server Card)* | Entry `trustManifest` (identity, attestations, provenance) |
| *(not in the Server Card)* | Entry `tags` for cross-artifact discovery |

## MCP Server as Catalog Entry

A remote MCP server maps to a Catalog Entry whose `url` points to the
server's Server Card and whose `type` is the known type
`application/mcp-server-card+json`:

```json
{
  "identifier": "urn:air:acme-corp.com:mcp:finance-server",
  "type": "application/mcp-server-card+json",
  "url": "https://api.acme-corp.com/mcp/server-card",
  "tags": ["finance", "mcp"],
  "publisher": {
    "identifier": "did:web:acme-corp.com",
    "displayName": "Acme Financial Corp"
  },
  "trustManifest": {
    "identity": "did:web:acme-corp.com",
    "attestations": [
      {
        "type": "publisher-identity",
        "uri": "https://trust.acme-corp.com/certs/publisher.jwt"
      },
      {
        "type": "SOC2-Type2",
        "uri": "https://trust.acme-corp.com/reports/soc2.pdf",
        "digest": "sha256:a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890"
      }
    ]
  }
}
```

> **Note on `type`:** The `type` member is an open-text type identifier
> ([ADR 0014](https://github.com/Agent-Card/ai-catalog/blob/main/adr/0014-media-type-to-type.md));
> any string is accepted, with a recommended set of "known types." The
> known type for an MCP server referenced by its Server Card is
> `application/mcp-server-card+json`.

## MCP Servers as an AI Catalog

A domain that hosts remote MCP servers can publish them as an AI Catalog,
letting clients that understand `application/ai-catalog+json` discover
those servers alongside A2A agents, skills, and other artifacts. Each
entry points to a server's Server Card:

```json
{
  "specVersion": "1.0",
  "host": {
    "displayName": "Acme MCP Servers",
    "identifier": "did:web:acme-corp.com",
    "documentationUrl": "https://acme-corp.com/docs"
  },
  "entries": [
    {
      "identifier": "urn:air:acme-corp.com:mcp:finance-server",
      "type": "application/mcp-server-card+json",
      "url": "https://api.acme-corp.com/finance/server-card",
      "tags": ["finance", "mcp"]
    },
    {
      "identifier": "urn:air:acme-corp.com:mcp:docs-search",
      "type": "application/mcp-server-card+json",
      "url": "https://api.acme-corp.com/docs-search/server-card",
      "tags": ["search", "docs"]
    },
    {
      "identifier": "urn:air:acme-corp.com:mcp:ci-cd",
      "type": "application/mcp-server-card+json",
      "url": "https://api.acme-corp.com/ci-cd/server-card",
      "tags": ["ci", "cd", "devops"]
    }
  ]
}
```

## Decentralized Discovery

AI Catalog enables decentralized discovery: any domain can publish its
MCP servers at `/.well-known/ai-catalog.json` without registering with a
central authority.

A vendor hosting its own MCP servers can publish:

```
https://api.acme-corp.com/.well-known/ai-catalog.json
```

The catalog and the Server Card play two complementary roles: the
catalog is how a client *finds* a server's URL in the first place, and
the Server Card is the connection entry point it points at. They are
useful independently — a client that already knows a server's URL can
point at its Server Card directly, with no catalog traversal, while a
client starting from just a domain uses the catalog to enumerate what
that domain offers.

Because of this, there is no single prescribed discovery ordering.
Clients wire discovery in wherever it fits their architecture — probing
a domain's catalog when it enters a session, watching outbound traffic
at an egress boundary, or connecting to a known Server Card directly. A
typical catalog-first path is: fetch `/.well-known/ai-catalog.json`,
filter entries by `type` (`application/mcp-server-card+json`) to find
MCP servers, follow an entry's `url` to its Server Card for connection
details, and connect — evaluating the Trust Manifest (when present) for
publisher identity and attestations along the way. Whatever the path,
the Server Card is advisory: a client reconciles it against the live
connection and MUST NOT treat it as authoritative for access control —
the connection itself remains the source of truth. See the Server Card
[best-practices guidance](https://github.com/modelcontextprotocol/experimental-ext-server-card)
for the range of client integration strategies.

This separation lets AI Catalog provide the trust and cross-ecosystem
indexing layer while the MCP Server Card provides the protocol-specific
operational details. A domain with multiple MCP servers publishes one AI
Catalog listing all of them, with each entry pointing to its respective
Server Card.

## What AI Catalog Adds

A Server Card describes a single server but has no cross-server discovery
or trust layer. AI Catalog fills this gap:

1. **Publisher identity**: Verifiable publisher with DID or domain
   anchor.
2. **Trust verification**: Attestations (SOC2, HIPAA, publisher
   identity proofs) via the Trust Manifest.
3. **Provenance**: Links to source repositories, registries, and
   build artifacts with cryptographic digests.
4. **Signing**: Detached JWS signature on the Trust Manifest for
   integrity verification.
5. **Cross-ecosystem discovery**: MCP servers become discoverable
   alongside A2A agents, plugins, and datasets through a single
   catalog format.
6. **Composability**: MCP servers can be packaged with related
   artifacts (A2A agents, datasets) in nested catalogs.

