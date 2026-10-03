---
icon: material/home
---

# AI Catalog

**A JSON format for making all your AI artifacts discoverable.**

The AI ecosystem is growing fast — MCP servers, A2A agents, Claude Code plugins, datasets, model cards. Each protocol defines its own discovery mechanism, forcing clients to implement bespoke logic for every artifact type.

AI Catalog solves this with a simple, typed JSON format that indexes any kind of AI artifact in one place. Clients read one file. Publishers maintain one list.

---

## What it looks like

```json
{
  "specVersion": "1.0",
  "host": {
    "displayName": "Acme Corp",
    "identifier": "did:web:acme-corp.com"
  },
  "entries": [
    {
      "identifier": "urn:air:acme-corp.com:mcp:weather",
      "type": "application/mcp-server-card+json",
      "url": "https://api.acme-corp.com/mcp/server-card"
    },
    {
      "identifier": "urn:air:acme-corp.com:a2a:research",
      "type": "application/a2a-agent-card+json",
      "url": "https://agents.acme-corp.com/research"
    },
    {
      "identifier": "urn:air:acme-corp.com:catalog:finance",
      "displayName": "Finance Suite",
      "type": "application/ai-catalog+json",
      "url": "https://acme-corp.com/catalogs/finance.json"
    }
  ]
}
```

Serve it at `/.well-known/ai-catalog.json` and any AI client can discover everything you offer.

---

## Key features

<div class="grid cards" markdown>

- **Artifact-agnostic**

    Uses a `type` field to identify artifact kinds — `application/mcp-server-card+json`, `application/a2a-agent-card+json`, and any future type — without defining their schema.

- **Progressive complexity**

    Start with just types and URLs. Add host identity, tags, and versions when you're ready. Layer in trust metadata only when you need it.

- **Composable and nestable**

    Catalog entries can point to other catalogs, enabling hierarchical organization and multi-artifact packaging.

- **Location independent**

    Catalogs work at `/.well-known/`, as API responses, embedded in registries, or as local files. No special infrastructure required.

- **Optional trust layer**

    Optional Trust Manifests group claims by contributor identity. Signatures authenticate selected catalog fields, including claims in Trust Manifests.

- **Federation-ready**

    Sub-catalogs can be authored, hosted, and updated independently by different teams or organizations.

</div>

---

## Who is this for?

**AI tool publishers** — Expose your MCP servers, A2A agents, or plugins through a single discoverable endpoint.

**Platform and enterprise teams** — Organize a large AI artifact inventory into browsable, hierarchical catalogs.

**Registry builders** — Provide a standard discovery interface across multiple artifact types.

**Client developers** — Write one discovery flow that works for all AI artifact types.

---

## Get started

<div class="grid cards" markdown>

- [**Quickstart** — get a catalog live in 5 minutes](getting-started.md)
- [**Creating a Catalog** — detailed authoring guide](guides/creating-a-catalog.md)
- [**Consuming Catalogs** — guide for client developers](guides/consuming-catalogs.md)
- [**Full Specification** — normative reference](specification.md)

</div>
